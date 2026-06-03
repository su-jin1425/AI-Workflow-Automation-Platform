from app.execution.validator import (
    validate_workflow_definition,
)


def test_linear_workflow_valid():
    workflow = {
        "nodes": [
            {
                "id": "logic_1",
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
                "source": "logic_1",
                "target": "delay_1",
            }
        ],
    }

    validate_workflow_definition(workflow)


def test_multi_node_workflow_valid():
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
        ],
    }

    validate_workflow_definition(workflow)


def test_parallel_branch_workflow():
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


def test_diamond_workflow():
    workflow = {
        "nodes": [
            {
                "id": "start",
                "type": "logic",
                "configuration": {},
            },
            {
                "id": "branch_a",
                "type": "delay",
                "configuration": {
                    "seconds": 1,
                },
            },
            {
                "id": "branch_b",
                "type": "delay",
                "configuration": {
                    "seconds": 2,
                },
            },
            {
                "id": "merge",
                "type": "logic",
                "configuration": {},
            },
        ],
        "edges": [
            {
                "source": "start",
                "target": "branch_a",
            },
            {
                "source": "start",
                "target": "branch_b",
            },
            {
                "source": "branch_a",
                "target": "merge",
            },
            {
                "source": "branch_b",
                "target": "merge",
            },
        ],
    }

    validate_workflow_definition(workflow)


def test_long_chain_workflow():
    nodes = []
    edges = []

    for i in range(15):
        nodes.append(
            {
                "id": f"node_{i}",
                "type": "logic",
                "configuration": {},
            }
        )

    for i in range(14):
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


def test_multiple_conditions():
    workflow = {
        "nodes": [
            {
                "id": "start",
                "type": "logic",
                "configuration": {},
            },
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
            {
                "id": "end",
                "type": "logic",
                "configuration": {},
            },
        ],
        "edges": [
            {
                "source": "start",
                "target": "condition_1",
            },
            {
                "source": "condition_1",
                "target": "condition_2",
            },
            {
                "source": "condition_2",
                "target": "end",
            },
        ],
    }

    validate_workflow_definition(workflow)


def test_multiple_delays():
    workflow = {
        "nodes": [
            {
                "id": "delay_1",
                "type": "delay",
                "configuration": {
                    "seconds": 1,
                },
            },
            {
                "id": "delay_2",
                "type": "delay",
                "configuration": {
                    "seconds": 2,
                },
            },
            {
                "id": "delay_3",
                "type": "delay",
                "configuration": {
                    "seconds": 3,
                },
            },
        ],
        "edges": [
            {
                "source": "delay_1",
                "target": "delay_2",
            },
            {
                "source": "delay_2",
                "target": "delay_3",
            },
        ],
    }

    validate_workflow_definition(workflow)


def test_large_valid_workflow():
    nodes = []
    edges = []

    for i in range(50):
        nodes.append(
            {
                "id": f"node_{i}",
                "type": "logic",
                "configuration": {},
            }
        )

    for i in range(49):
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