import pytest

from app.execution.validator import (
    validate_workflow_definition,
)


def test_delay_node_valid():
    workflow = {
        "nodes": [
            {
                "id": "delay_1",
                "type": "delay",
                "configuration": {
                    "seconds": 5,
                },
            }
        ],
        "edges": [],
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


def test_delay_negative_seconds_rejected():
    workflow = {
        "nodes": [
            {
                "id": "delay_1",
                "type": "delay",
                "configuration": {
                    "seconds": -1,
                },
            }
        ],
        "edges": [],
    }

    with pytest.raises(ValueError):
        validate_workflow_definition(workflow)


def test_delay_missing_seconds_rejected():
    workflow = {
        "nodes": [
            {
                "id": "delay_1",
                "type": "delay",
                "configuration": {},
            }
        ],
        "edges": [],
    }

    with pytest.raises(ValueError):
        validate_workflow_definition(workflow)


def test_condition_node_valid():
    workflow = {
        "nodes": [
            {
                "id": "condition_1",
                "type": "condition",
                "configuration": {},
            }
        ],
        "edges": [],
    }

    validate_workflow_definition(workflow)


def test_multiple_condition_nodes():
    workflow = {
        "nodes": [
            {
                "id": "condition_1",
                "type": "condition",
                "configuration": {},
            },
            {
                "id": "condition_2",
                "type": "condition",
                "configuration": {},
            },
        ],
        "edges": [
            {
                "source": "condition_1",
                "target": "condition_2",
            }
        ],
    }

    validate_workflow_definition(workflow)


def test_logic_node_valid():
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


def test_multiple_logic_nodes():
    workflow = {
        "nodes": [
            {
                "id": "logic_1",
                "type": "logic",
                "configuration": {},
            },
            {
                "id": "logic_2",
                "type": "logic",
                "configuration": {},
            },
        ],
        "edges": [
            {
                "source": "logic_1",
                "target": "logic_2",
            }
        ],
    }

    validate_workflow_definition(workflow)


def test_mixed_node_types():
    workflow = {
        "nodes": [
            {
                "id": "logic_1",
                "type": "logic",
                "configuration": {},
            },
            {
                "id": "condition_1",
                "type": "condition",
                "configuration": {},
            },
            {
                "id": "delay_1",
                "type": "delay",
                "configuration": {
                    "seconds": 3,
                },
            },
        ],
        "edges": [
            {
                "source": "logic_1",
                "target": "condition_1",
            },
            {
                "source": "condition_1",
                "target": "delay_1",
            },
        ],
    }

    validate_workflow_definition(workflow)


def test_large_mixed_workflow():
    workflow = {
        "nodes": [
            {
                "id": "logic_1",
                "type": "logic",
                "configuration": {},
            },
            {
                "id": "condition_1",
                "type": "condition",
                "configuration": {},
            },
            {
                "id": "delay_1",
                "type": "delay",
                "configuration": {
                    "seconds": 1,
                },
            },
            {
                "id": "logic_2",
                "type": "logic",
                "configuration": {},
            },
            {
                "id": "delay_2",
                "type": "delay",
                "configuration": {
                    "seconds": 2,
                },
            },
        ],
        "edges": [
            {
                "source": "logic_1",
                "target": "condition_1",
            },
            {
                "source": "condition_1",
                "target": "delay_1",
            },
            {
                "source": "delay_1",
                "target": "logic_2",
            },
            {
                "source": "logic_2",
                "target": "delay_2",
            },
        ],
    }

    validate_workflow_definition(workflow)