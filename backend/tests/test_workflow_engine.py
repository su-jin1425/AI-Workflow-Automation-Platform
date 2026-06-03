import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.execution.engine import WorkflowEngine
from app.models.workflow import Workflow
from app.models.execution import Execution

@pytest.fixture
def workflow_engine():
    return WorkflowEngine()

@pytest.fixture
def sample_workflow():
    return Workflow(
        id="test-workflow-1",
        name="Test Workflow",
        nodes=[
            {
                "id": "start",
                "type": "start",
                "position": {"x": 0, "y": 0}
            },
            {
                "id": "task-1",
                "type": "task",
                "config": {"action": "process_data"},
                "position": {"x": 200, "y": 0}
            },
            {
                "id": "end",
                "type": "end",
                "position": {"x": 400, "y": 0}
            }
        ],
        connections=[
            {"from": "start", "to": "task-1"},
            {"from": "task-1", "to": "end"}
        ]
    )

@pytest.mark.asyncio
async def test_completed_execution(workflow_engine, sample_workflow):
    """Test workflow execution that completes successfully"""
    # Mock the node execution functions
    with patch('app.execution.engine.execute_task') as mock_execute:
        mock_execute.return_value = {"status": "success"}
        
        # Execute the workflow
        execution = Execution(workflow_id=sample_workflow.id, status="pending")
        result = await workflow_engine.run(sample_workflow, execution)
        
        # Should return success
        assert result.status == "completed"
        assert result.error is None
        # Should have executed all nodes
        assert mock_execute.call_count == 1  # Only 1 task node

@pytest.mark.asyncio
async def test_cancelled_execution(workflow_engine, sample_workflow):
    """Test workflow execution that gets cancelled"""
    # Mock the node execution to simulate cancellation
    with patch('app.execution.engine.execute_task') as mock_execute:
        async def slow_execution(node, context):
            # Simulate a long-running task that checks for cancellation
            import asyncio
            await asyncio.sleep(0.1)  # Short delay
            return {"status": "success"}
        
        mock_execute.side_effect = slow_execution
        
        # Create an execution and mark it as cancelled
        execution = Execution(workflow_id=sample_workflow.id, status="cancelled")
        
        # Execute the workflow
        result = await workflow_engine.run(sample_workflow, execution)
        
        # Should return cancelled
        assert result.status == "cancelled"
        assert result.error is not None

@pytest.mark.asyncio
async def test_cycle_detection(workflow_engine):
    """Test workflow with cycle detection"""
    # Create a workflow with a cycle
    cyclic_workflow = Workflow(
        id="cyclic-workflow-1",
        name="Cyclic Workflow",
        nodes=[
            {
                "id": "start",
                "type": "start",
                "position": {"x": 0, "y": 0}
            },
            {
                "id": "task-1",
                "type": "task",
                "config": {"action": "process_data"},
                "position": {"x": 200, "y": 0}
            },
            {
                "id": "task-2",
                "type": "task",
                "config": {"action": "process_more"},
                "position": {"x": 400, "y": 0}
            }
        ],
        connections=[
            {"from": "start", "to": "task-1"},
            {"from": "task-1", "to": "task-2"},
            {"from": "task-2", "to": "task-1"}  # This creates a cycle
        ]
    )
    
    # Execute the workflow
    execution = Execution(workflow_id=cyclic_workflow.id, status="pending")
    result = await workflow_engine.run(cyclic_workflow, execution)
    
    # Should detect cycle and fail
    assert result.status == "failed"
    assert "cycle" in result.error.lower()

@pytest.mark.asyncio
async def test_token_usage_calculation(workflow_engine, sample_workflow):
    """Test that token usage is calculated correctly"""
    # Mock the node execution functions to return token usage
    with patch('app.execution.engine.execute_task') as mock_execute:
        mock_execute.return_value = {
            "status": "success",
            "token_usage": {"input": 100, "output": 50}
        }
        
        # Execute the workflow
        execution = Execution(workflow_id=sample_workflow.id, status="pending")
        result = await workflow_engine.run(sample_workflow, execution)
        
        # Should calculate token usage
        assert result.status == "completed"
        assert hasattr(result, 'metrics')
        assert "tokens" in result.metrics
        assert result.metrics["tokens"]["input"] == 100
        assert result.metrics["tokens"]["output"] == 50

@pytest.mark.asyncio
async def test_api_call_calculation(workflow_engine, sample_workflow):
    """Test that API call count is calculated correctly"""
    # Mock the node execution functions to return API call count
    with patch('app.execution.engine.execute_task') as mock_execute:
        mock_execute.return_value = {
            "status": "success",
            "api_calls": 3
        }
        
        # Execute the workflow
        execution = Execution(workflow_id=sample_workflow.id, status="pending")
        result = await workflow_engine.run(sample_workflow, execution)
        
        # Should calculate API call count
        assert result.status == "completed"
        assert hasattr(result, 'metrics')
        assert "api_calls" in result.metrics
        assert result.metrics["api_calls"] == 3

@pytest.mark.asyncio
async def test_edge_condition_routing(workflow_engine):
    """Test workflow with conditional routing"""
    # Create a workflow with conditional paths
    conditional_workflow = Workflow(
        id="conditional-workflow-1",
        name="Conditional Workflow",
        nodes=[
            {
                "id": "start",
                "type": "start",
                "position": {"x": 0, "y": 0}
            },
            {
                "id": "condition",
                "type": "condition",
                "config": {
                    "condition": "{{ data.score > 70 }}",
                    "true_path": "pass",
                    "false_path": "fail"
                },
                "position": {"x": 200, "y": 0}
            },
            {
                "id": "pass-task",
                "type": "task",
                "config": {"action": "handle_pass"},
                "position": {"x": 400, "y": -100}
            },
            {
                "id": "fail-task",
                "type": "task",
                "config": {"action": "handle_fail"},
                "position": {"x": 400, "y": 100}
            },
            {
                "id": "end",
                "type": "end",
                "position": {"x": 600, "y": 0}
            }
        ],
        connections=[
            {"from": "start", "to": "condition"},
            {"from": "condition", "to": "pass-task", "condition": "pass"},
            {"from": "condition", "to": "fail-task", "condition": "fail"},
            {"from": "pass-task", "to": "end"},
            {"from": "fail-task", "to": "end"}
        ]
    )
    
    # Mock the condition node execution
    with patch('app.execution.engine.execute_condition') as mock_condition, \
         patch('app.execution.engine.execute_task') as mock_task:
        
        # Condition evaluates to True (pass path)
        mock_condition.return_value = {"status": "success", "next_path": "pass"}
        mock_task.return_value = {"status": "success"}
        
        # Execute the workflow with data that satisfies the condition
        execution = Execution(
            workflow_id=conditional_workflow.id, 
            status="pending",
            input_data={"score": 85}
        )
        result = await workflow_engine.run(conditional_workflow, execution)
        
        # Should complete successfully
        assert result.status == "completed"
        assert result.error is None