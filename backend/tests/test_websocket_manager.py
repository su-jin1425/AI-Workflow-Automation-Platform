from unittest.mock import AsyncMock

import pytest

from app.services.websocket_manager import (
    WebSocketManager,
)


@pytest.mark.asyncio
async def test_connect_creates_channel():
    manager = WebSocketManager()

    websocket = AsyncMock()

    await manager.connect(
        "workflow-1",
        websocket,
    )

    assert "workflow-1" in manager.connections
    assert websocket in manager.connections["workflow-1"]


@pytest.mark.asyncio
async def test_multiple_connections_same_channel():
    manager = WebSocketManager()

    ws1 = AsyncMock()
    ws2 = AsyncMock()

    await manager.connect(
        "workflow-1",
        ws1,
    )

    await manager.connect(
        "workflow-1",
        ws2,
    )

    assert len(
        manager.connections["workflow-1"]
    ) == 2


@pytest.mark.asyncio
async def test_multiple_channels():
    manager = WebSocketManager()

    ws1 = AsyncMock()
    ws2 = AsyncMock()

    await manager.connect(
        "channel-a",
        ws1,
    )

    await manager.connect(
        "channel-b",
        ws2,
    )

    assert "channel-a" in manager.connections
    assert "channel-b" in manager.connections

    assert ws1 in manager.connections["channel-a"]
    assert ws2 in manager.connections["channel-b"]


@pytest.mark.asyncio
async def test_disconnect_removes_websocket():
    manager = WebSocketManager()

    websocket = AsyncMock()

    await manager.connect(
        "workflow-1",
        websocket,
    )

    manager.disconnect(
        "workflow-1",
        websocket,
    )

    assert websocket not in manager.connections.get(
        "workflow-1",
        set(),
    )


@pytest.mark.asyncio
async def test_disconnect_unknown_websocket():
    manager = WebSocketManager()

    websocket = AsyncMock()

    manager.disconnect(
        "missing-channel",
        websocket,
    )

    assert True


@pytest.mark.asyncio
async def test_channel_cleanup_after_disconnect():
    manager = WebSocketManager()

    websocket = AsyncMock()

    await manager.connect(
        "workflow-1",
        websocket,
    )

    manager.disconnect(
        "workflow-1",
        websocket,
    )

    channel = manager.connections.get(
        "workflow-1",
        set(),
    )

    assert len(channel) == 0


@pytest.mark.asyncio
async def test_broadcast_single_client():
    manager = WebSocketManager()

    websocket = AsyncMock()

    await manager.connect(
        "workflow-1",
        websocket,
    )

    await manager.broadcast(
        "workflow-1",
        {
            "status": "completed",
        },
    )

    websocket.send_json.assert_awaited_once()


@pytest.mark.asyncio
async def test_broadcast_multiple_clients():
    manager = WebSocketManager()

    ws1 = AsyncMock()
    ws2 = AsyncMock()

    await manager.connect(
        "workflow-1",
        ws1,
    )

    await manager.connect(
        "workflow-1",
        ws2,
    )

    await manager.broadcast(
        "workflow-1",
        {
            "status": "running",
        },
    )

    ws1.send_json.assert_awaited_once()
    ws2.send_json.assert_awaited_once()


@pytest.mark.asyncio
async def test_broadcast_empty_channel():
    manager = WebSocketManager()

    await manager.broadcast(
        "missing-channel",
        {
            "status": "running",
        },
    )

    assert True


@pytest.mark.asyncio
async def test_broadcast_payload_integrity():
    manager = WebSocketManager()

    websocket = AsyncMock()

    payload = {
        "execution_id": "123",
        "status": "completed",
    }

    await manager.connect(
        "workflow-1",
        websocket,
    )

    await manager.broadcast(
        "workflow-1",
        payload,
    )

    websocket.send_json.assert_awaited_once_with(
        payload
    )