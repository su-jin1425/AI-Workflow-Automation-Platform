import pytest
from fastapi import HTTPException

from backend.app.execution.validator import validate_workflow_definition


def test_valid_workflow_definition_passes():
    validate_workflow_definition(
        {
            "nodes": [
                {"id": "start", "type": "logic", "configuration": {"operation": "set", "value": 1}},
                {"id": "delay", "type": "delay", "configuration": {"seconds": 0}},
            ],
            "edges": [{"source": "start", "target": "delay"}],
        }
    )


def test_cycle_is_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [
                    {"id": "a", "type": "logic", "configuration": {}},
                    {"id": "b", "type": "logic", "configuration": {}},
                ],
                "edges": [{"source": "a", "target": "b"}, {"source": "b", "target": "a"}],
            }
        )
