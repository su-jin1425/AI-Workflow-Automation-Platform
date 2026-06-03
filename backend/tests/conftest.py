import pytest


@pytest.fixture
def valid_workflow():
    return {
        "nodes": [
            {
                "id": "logic_1",
                "type": "logic",
                "configuration": {},
            }
        ],
        "edges": [],
    }


@pytest.fixture
def branching_workflow():
    return {
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


@pytest.fixture
def cyclic_workflow():
    return {
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


@pytest.fixture
def duplicate_node_workflow():
    return {
        "nodes": [
            {
                "id": "duplicate",
                "type": "logic",
                "configuration": {},
            },
            {
                "id": "duplicate",
                "type": "delay",
                "configuration": {
                    "seconds": 1,
                },
            },
        ],
        "edges": [],
    }


@pytest.fixture
def invalid_edge_workflow():
    return {
        "nodes": [
            {
                "id": "logic_1",
                "type": "logic",
                "configuration": {},
            }
        ],
        "edges": [
            {
                "source": "logic_1",
                "target": "missing_node",
            }
        ],
    }


@pytest.fixture
def delay_workflow():
    return {
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


@pytest.fixture
def condition_workflow():
    return {
        "nodes": [
            {
                "id": "condition_1",
                "type": "condition",
                "configuration": {},
            }
        ],
        "edges": [],
    }


@pytest.fixture
def large_workflow():
    nodes = []

    for i in range(50):
        nodes.append(
            {
                "id": f"node_{i}",
                "type": "logic",
                "configuration": {},
            }
        )

    edges = []

    for i in range(49):
        edges.append(
            {
                "source": f"node_{i}",
                "target": f"node_{i+1}",
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
    }


@pytest.fixture
def sample_execution_payload():
    return {
        "customer_id": "123",
        "order_id": "456",
        "amount": 99.99,
    }


@pytest.fixture
def sample_monitoring_response():
    return {
        "active": 1,
        "reserved": 0,
        "scheduled": 0,
    }


@pytest.fixture
def sample_analytics_response():
    return {
        "total_workflows": 10,
        "total_executions": 50,
        "successful_executions": 45,
        "failed_executions": 5,
    }