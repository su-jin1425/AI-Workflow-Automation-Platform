import pytest
from fastapi import HTTPException

from app.execution.validator import (
    validate_workflow_definition,
)


def test_valid_workflow_passes():
    validate_workflow_definition(
        {
            "nodes": [
                {
                    "id": "start",
                    "type": "logic",
                    "configuration": {},
                },
                {
                    "id": "delay_1",
                    "type": "delay",
                    "configuration": {
                        "seconds": 1,
                    },
                },
            ],
            "edges": [
                {
                    "source": "start",
                    "target": "delay_1",
                }
            ],
        }
    )


def test_empty_workflow_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [],
                "edges": [],
            }
        )


def test_duplicate_node_id_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [
                    {
                        "id": "node1",
                        "type": "logic",
                        "configuration": {},
                    },
                    {
                        "id": "node1",
                        "type": "delay",
                        "configuration": {
                            "seconds": 1,
                        },
                    },
                ],
                "edges": [],
            }
        )


def test_unsupported_node_type_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [
                    {
                        "id": "node1",
                        "type": "unknown_type",
                        "configuration": {},
                    }
                ],
                "edges": [],
            }
        )


def test_invalid_configuration_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [
                    {
                        "id": "node1",
                        "type": "logic",
                        "configuration": "invalid",
                    }
                ],
                "edges": [],
            }
        )


def test_invalid_edge_reference_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [
                    {
                        "id": "node1",
                        "type": "logic",
                        "configuration": {},
                    }
                ],
                "edges": [
                    {
                        "source": "node1",
                        "target": "missing_node",
                    }
                ],
            }
        )


def test_cycle_detection_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [
                    {
                        "id": "a",
                        "type": "logic",
                        "configuration": {},
                    },
                    {
                        "id": "b",
                        "type": "logic",
                        "configuration": {},
                    },
                ],
                "edges": [
                    {
                        "source": "a",
                        "target": "b",
                    },
                    {
                        "source": "b",
                        "target": "a",
                    },
                ],
            }
        )


def test_branching_workflow_passes():
    validate_workflow_definition(
        {
            "nodes": [
                {
                    "id": "start",
                    "type": "logic",
                    "configuration": {},
                },
                {
                    "id": "left",
                    "type": "delay",
                    "configuration": {
                        "seconds": 1,
                    },
                },
                {
                    "id": "right",
                    "type": "delay",
                    "configuration": {
                        "seconds": 1,
                    },
                },
            ],
            "edges": [
                {
                    "source": "start",
                    "target": "left",
                },
                {
                    "source": "start",
                    "target": "right",
                },
            ],
        }
    )