import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.execution.nodes import NodeExecutionError, execute_node
from app.models.execution import ExecutionMetric, NodeExecution, WorkflowExecution
from app.models.workflow import Workflow
from app.services.websocket_manager import websocket_manager


class WorkflowEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self, execution_id: UUID) -> None:
        execution = await self._load_execution(execution_id)
        workflow = execution.workflow
        definition = workflow.workflow_definition
        nodes = {node["id"]: node for node in definition["nodes"]}
        edges = definition.get("edges", [])
        outgoing = defaultdict(list)
        incoming = defaultdict(list)
        for edge in edges:
            outgoing[edge["source"]].append(edge)
            incoming[edge["target"]].append(edge)

        context: dict[str, Any] = {"input": execution.input_payload}
        completed: set[str] = set()
        skipped: set[str] = set()
        started_at = perf_counter()

        execution.execution_status = "running"
        execution.started_at = datetime.now(timezone.utc)
        await self._log(execution, "Workflow execution started")
        await self.db.commit()
        await self._broadcast(execution)

        try:
            while len(completed | skipped) < len(nodes):
                ready_nodes = [
                    node_id
                    for node_id in nodes
                    if node_id not in completed
                    and node_id not in skipped
                    and self._dependencies_done(node_id, incoming, completed, skipped, context)
                ]
                if not ready_nodes:
                    raise NodeExecutionError("Workflow cannot progress because no nodes are ready")

                results = await asyncio.gather(
                    *(self._run_node(nodes[node_id], context, execution) for node_id in ready_nodes),
                    return_exceptions=True,
                )
                for node_id, result in zip(ready_nodes, results, strict=True):
                    if isinstance(result, Exception):
                        raise result
                    context[node_id] = result
                    completed.add(node_id)
                    for edge in outgoing[node_id]:
                        if not self._edge_allows(edge, context.get(node_id)):
                            skipped.add(edge["target"])

            execution.execution_status = "completed"
            execution.output_payload = context
            await self._log(execution, "Workflow execution completed")
        except Exception as exc:
            execution.execution_status = "failed"
            execution.output_payload = context
            await self._log(execution, f"Workflow execution failed: {exc}")
        finally:
            execution.completed_at = datetime.now(timezone.utc)
            metric = ExecutionMetric(
                execution_id=execution.id,
                execution_time=perf_counter() - started_at,
                token_usage=self._token_usage(context),
                api_calls=self._api_calls(context),
            )
            self.db.add(metric)
            await self.db.commit()
            await self._broadcast(execution)

    async def _run_node(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
        execution: WorkflowExecution,
    ) -> dict[str, Any]:
        node_execution = NodeExecution(
            execution_id=execution.id,
            node_id=node["id"],
            node_type=node["type"],
            status="running",
            input_payload=context,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(node_execution)
        await self._log(execution, f"Node {node['id']} started")
        await self.db.commit()
        await self._broadcast(execution)

        try:
            output = await execute_node(node, context, self.db)
            node_execution.status = "completed"
            node_execution.output_payload = output
            node_execution.completed_at = datetime.now(timezone.utc)
            await self._log(execution, f"Node {node['id']} completed")
            await self.db.commit()
            await self._broadcast(execution)
            return output
        except Exception as exc:
            node_execution.status = "failed"
            node_execution.error_message = str(exc)
            node_execution.completed_at = datetime.now(timezone.utc)
            await self._log(execution, f"Node {node['id']} failed: {exc}")
            await self.db.commit()
            await self._broadcast(execution)
            raise

    async def _load_execution(self, execution_id: UUID) -> WorkflowExecution:
        result = await self.db.execute(
            select(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
            .join(Workflow)
        )
        execution = result.scalar_one()
        await self.db.refresh(execution, ["workflow"])
        return execution

    def _dependencies_done(
        self,
        node_id: str,
        incoming: dict[str, list[dict[str, Any]]],
        completed: set[str],
        skipped: set[str],
        context: dict[str, Any],
    ) -> bool:
        dependencies = incoming.get(node_id, [])
        if not dependencies:
            return True
        return all(edge["source"] in completed or edge["source"] in skipped for edge in dependencies)

    def _edge_allows(self, edge: dict[str, Any], source_output: dict[str, Any] | None) -> bool:
        condition = edge.get("condition")
        if condition is None:
            return True
        if not isinstance(source_output, dict):
            return False
        return bool(source_output.get("result")) is bool(condition)

    async def _log(self, execution: WorkflowExecution, message: str) -> None:
        logs = list(execution.execution_logs or [])
        logs.append({"time": datetime.now(timezone.utc).isoformat(), "message": message})
        execution.execution_logs = logs

    async def _broadcast(self, execution: WorkflowExecution) -> None:
        await websocket_manager.broadcast(
            str(execution.id),
            {
                "execution_id": str(execution.id),
                "status": execution.execution_status,
                "logs": execution.execution_logs,
                "output": execution.output_payload,
            },
        )

    def _token_usage(self, context: dict[str, Any]) -> int:
        total = 0
        for value in context.values():
            if isinstance(value, dict):
                total += int(value.get("token_usage", 0))
        return total

    def _api_calls(self, context: dict[str, Any]) -> int:
        total = 0
        for value in context.values():
            if isinstance(value, dict) and "status_code" in value:
                total += 1
        return total
