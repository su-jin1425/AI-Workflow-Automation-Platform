import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.execution.nodes import (
    execute_delay, 
    execute_condition, 
    execute_logic, 
    execute_file_processing
)

@pytest.mark.asyncio
async def test_delay_node():
    """Test delay node execution"""
    node = {
        "id": "delay-1",
        "type": "delay",
        "config": {"duration": 1}  # 1 second delay
    }
    
    context = {}
    
    # Execute the delay node
    result = await execute_delay(node, context)
    
    # Should return success without errors
    assert result["status"] == "success"
    assert "error" not in result

@pytest.mark.asyncio
async def test_condition_node():
    """Test condition node execution"""
    node = {
        "id": "condition-1",
        "type": "condition",
        "config": {
            "condition": "{{ data.value > 5 }}",
            "true_path": "path-a",
            "false_path": "path-b"
        }
    }
    
    context = {"data": {"value": 10}}  # Value > 5, should take true path
    
    # Execute the condition node
    result = await execute_condition(node, context)
    
    # Should return success and correct path
    assert result["status"] == "success"
    assert result["next_path"] == "path-a"
    assert "error" not in result

@pytest.mark.asyncio
async def test_logic_set():
    """Test logic node with set operation"""
    node = {
        "id": "logic-1",
        "type": "logic",
        "config": {
            "operation": "set",
            "target": "output.result",
            "value": "{{ data.input * 2 }}"
        }
    }
    
    context = {"data": {"input": 5}}
    
    # Execute the logic node
    result = await execute_logic(node, context)
    
    # Should return success and set the value
    assert result["status"] == "success"
    assert context["output"]["result"] == 10
    assert "error" not in result

@pytest.mark.asyncio
async def test_logic_merge():
    """Test logic node with merge operation"""
    node = {
        "id": "logic-2",
        "type": "logic",
        "config": {
            "operation": "merge",
            "target": "output",
            "sources": ["data.obj1", "data.obj2"]
        }
    }
    
    context = {
        "data": {
            "obj1": {"a": 1, "b": 2},
            "obj2": {"c": 3, "d": 4}
        }
    }
    
    # Execute the logic node
    result = await execute_logic(node, context)
    
    # Should return success and merge the objects
    assert result["status"] == "success"
    assert context["output"] == {"a": 1, "b": 2, "c": 3, "d": 4}
    assert "error" not in result

@pytest.mark.asyncio
async def test_logic_pick():
    """Test logic node with pick operation"""
    node = {
        "id": "logic-3",
        "type": "logic",
        "config": {
            "operation": "pick",
            "target": "output.selected",
            "source": "data",
            "keys": ["name", "age"]
        }
    }
    
    context = {
        "data": {
            "name": "John",
            "age": 30,
            "email": "john@example.com"
        }
    }
    
    # Execute the logic node
    result = await execute_logic(node, context)
    
    # Should return success and pick only specified keys
    assert result["status"] == "success"
    assert context["output"]["selected"] == {"name": "John", "age": 30}
    assert "email" not in context["output"]["selected"]
    assert "error" not in result

@pytest.mark.asyncio
async def test_file_processing_text_stats():
    """Test file processing node with text stats operation"""
    node = {
        "id": "file-1",
        "type": "file_processing",
        "config": {
            "operation": "text_stats",
            "target": "output.stats"
        }
    }
    
    context = {
        "file_content": "This is a sample text with multiple words. This text is for testing."
    }
    
    # Execute the file processing node
    result = await execute_file_processing(node, context)
    
    # Should return success and calculate text stats
    assert result["status"] == "success"
    assert "output" in context
    assert "stats" in context["output"]
    assert "error" not in result

@pytest.mark.asyncio
async def test_file_processing_csv_rows():
    """Test file processing node with CSV rows operation"""
    node = {
        "id": "file-2",
        "type": "file_processing",
        "config": {
            "operation": "csv_rows",
            "target": "output.rows"
        }
    }
    
    context = {
        "file_content": "name,age\nJohn,30\nJane,25\nBob,35"
    }
    
    # Execute the file processing node
    result = await execute_file_processing(node, context)
    
    # Should return success and parse CSV rows
    assert result["status"] == "success"
    assert "output" in context
    assert "rows" in context["output"]
    assert len(context["output"]["rows"]) == 3  # Header + 2 data rows
    assert "error" not in result

@pytest.mark.asyncio
async def test_invalid_logic_operation():
    """Test logic node with invalid operation"""
    node = {
        "id": "logic-4",
        "type": "logic",
        "config": {
            "operation": "invalid_op",
            "target": "output.result",
            "value": "test"
        }
    }
    
    context = {}
    
    # Execute the logic node
    result = await execute_logic(node, context)
    
    # Should return error for invalid operation
    assert result["status"] == "error"
    assert "error" in result

@pytest.mark.asyncio
async def test_invalid_delay():
    """Test delay node with invalid duration"""
    node = {
        "id": "delay-2",
        "type": "delay",
        "config": {"duration": -1}  # Invalid negative duration
    }
    
    context = {}
    
    # Execute the delay node
    result = await execute_delay(node, context)
    
    # Should return error for invalid duration
    assert result["status"] == "error"
    assert "error" in result