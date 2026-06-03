import pytest
from fastapi import HTTPException

from app.execution.validator import (
    validate_workflow_definition,
)


def test_valid_workflow_passes():
    workflow = {
        "nodes": [
            {
                "id": "logic_1",
                "type": "logic",
                "configuration": {},
            }
        ],
        "edges": [],
    }

    validate_workflow_definition(workflow)


def test_empty_workflow_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [],
                "edges": [],
            }
        )


def test_duplicate_node_id_rejected():
    workflow = {
        "nodes": [
            {
                "id": "node_1",
                "type": "logic",
                "configuration": {},
            },
            {
                "id": "node_1",
                "type": "delay",
                "configuration": {
                    "seconds": 1,
                },
            },
        ],
        "edges": [],
    }

    with pytest.raises(HTTPException):
        validate_workflow_definition(workflow)


def test_unsupported_node_type_rejected():
    workflow = {
        "nodes": [
            {
                "id": "node_1",
                "type": "invalid_type",
                "configuration": {},
            }
        ],
        "edges": [],
    }

    with pytest.raises(HTTPException):
        validate_workflow_definition(workflow)


def test_invalid_configuration_rejected():
    workflow = {
        "nodes": [
            {
                "id": "delay_1",
                "type": "delay",
                "configuration": {
                    "seconds": -5,
                },
            }
        ],
        "edges": [],
    }

    with pytest.raises(HTTPException):
        validate_workflow_definition(workflow)


def test_invalid_edge_reference_rejected():
    workflow = {
        "nodes": [
            {
                "id": "node_1",
                "type": "logic",
                "configuration": {},
            }
        ],
        "edges": [
            {
                "source": "node_1",
                "target": "missing_node",
            }
        ],
    }

    with pytest.raises(HTTPException):
        validate_workflow_definition(workflow)


def test_cycle_detection_rejected():
    workflow = {
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

    with pytest.raises(HTTPException):
        validate_workflow_definition(workflow)


def test_branching_workflow_passes():
    workflow = {
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
                    "seconds": 2,
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

    validate_workflow_definition(workflow)


def test_self_loop_rejected():
    workflow = {
        "nodes": [
            {
                "id": "node_1",
                "type": "logic",
                "configuration": {},
            }
        ],
        "edges": [
            {
                "source": "node_1",
                "target": "node_1",
            }
        ],
    }

    with pytest.raises(HTTPException):
        validate_workflow_definition(workflow)


def test_missing_nodes_key_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "edges": [],
            }
        )


def test_missing_edges_key_rejected():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [],
            }
        )


def test_nodes_must_be_list():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": {},
                "edges": [],
            }
        )


def test_edges_must_be_list():
    with pytest.raises(HTTPException):
        validate_workflow_definition(
            {
                "nodes": [],
                "edges": {},
            }
        )


def test_large_valid_workflow():
    nodes = []

    for i in range(25):
        nodes.append(
            {
                "id": f"node_{i}",
                "type": "logic",
                "configuration": {},
            }
        )

    edges = []

    for i in range(24):
        edges.append(
            {
                "source": f"node_{i}",
                "target": f"node_{i+1}",
            }
        )

    workflow = {
        "nodes": nodes,
        "edges": edges,
    }

    validate_workflow_definition(workflow)


def test_delay_zero_seconds_valid():
    workflow = {
        "nodes": [
            {
                "id": "delay_1",
                "type": "delay",
                "configuration": {
                    "seconds": 0,
                },
            }
        ],
        "edges": [],
    }

    validate_workflow_definition(workflow)
