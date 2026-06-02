from collections import defaultdict, deque
from typing import Any

from fastapi import HTTPException

from app.core.config import settings

SUPPORTED_NODE_TYPES = {
    "ai_prompt",
    "api_request",
    "condition",
    "delay",
    "database",
    "webhook",
    "email",
    "scheduler",
    "logic",
    "file_processing",
}


def validate_workflow_definition(definition: dict[str, Any]) -> None:
    nodes = definition.get("nodes")
    edges = definition.get("edges", [])

    if not isinstance(nodes, list) or not nodes:
        raise HTTPException(status_code=422, detail="Workflow must include at least one node")
    if len(nodes) > settings.max_workflow_nodes:
        raise HTTPException(status_code=422, detail="Workflow has too many nodes")
    if not isinstance(edges, list):
        raise HTTPException(status_code=422, detail="Workflow edges must be a list")

    node_ids: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            raise HTTPException(status_code=422, detail="Each node must be an object")
        node_id = node.get("id")
        node_type = node.get("type")
        if not isinstance(node_id, str) or not node_id:
            raise HTTPException(status_code=422, detail="Each node needs a string id")
        if node_id in node_ids:
            raise HTTPException(status_code=422, detail=f"Duplicate node id: {node_id}")
        if node_type not in SUPPORTED_NODE_TYPES:
            raise HTTPException(status_code=422, detail=f"Unsupported node type: {node_type}")
        if not isinstance(node.get("configuration", {}), dict):
            raise HTTPException(status_code=422, detail=f"Node {node_id} configuration must be an object")
        node_ids.add(node_id)

    adjacency: dict[str, list[str]] = defaultdict(list)
    incoming_count = {node_id: 0 for node_id in node_ids}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_ids or target not in node_ids:
            raise HTTPException(status_code=422, detail="Every edge must reference existing nodes")
        adjacency[source].append(target)
        incoming_count[target] += 1

    ready = deque([node_id for node_id, count in incoming_count.items() if count == 0])
    visited = 0
    while ready:
        current = ready.popleft()
        visited += 1
        for target in adjacency[current]:
            incoming_count[target] -= 1
            if incoming_count[target] == 0:
                ready.append(target)

    if visited != len(node_ids):
        raise HTTPException(status_code=422, detail="Workflow graph must not contain cycles")
