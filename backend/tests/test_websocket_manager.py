import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.websocket_manager import WebSocketManager

@pytest.fixture
def websocket_manager():
    return WebSocketManager()

@pytest.fixture
def mock_websocket():
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.close = AsyncMock()
    return websocket

@pytest.mark.asyncio
async def test_connect(websocket_manager, mock_websocket):
    """Test that websocket connections are properly added"""
    client_id = "test-client-123"
    
    # Connect the websocket
    await websocket_manager.connect(mock_websocket, client_id)
    
    # Verify the websocket was added to connections
    assert client_id in websocket_manager.active_connections
    assert websocket_manager.active_connections[client_id] == mock_websocket
    mock_websocket.accept.assert_called_once()

@pytest.mark.asyncio
async def test_disconnect(websocket_manager, mock_websocket):
    """Test that websocket connections are properly removed"""
    client_id = "test-client-123"
    
    # First connect the websocket
    await websocket_manager.connect(mock_websocket, client_id)
    assert client_id in websocket_manager.active_connections
    
    # Then disconnect
    await websocket_manager.disconnect(client_id)
    
    # Verify the websocket was removed from connections
    assert client_id not in websocket_manager.active_connections
    mock_websocket.close.assert_called_once()

@pytest.mark.asyncio
async def test_broadcast(websocket_manager, mock_websocket):
    """Test that broadcast sends payload to all connections"""
    client_id_1 = "test-client-1"
    client_id_2 = "test-client-2"
    message = {"event": "test", "data": "Hello, World!"}
    
    # Connect two websockets
    websocket_1 = AsyncMock()
    websocket_1.send_text = AsyncMock()
    websocket_2 = AsyncMock()
    websocket_2.send_text = AsyncMock()
    
    await websocket_manager.connect(websocket_1, client_id_1)
    await websocket_manager.connect(websocket_2, client_id_2)
    
    # Broadcast message
    await websocket_manager.broadcast(message)
    
    # Verify both websockets received the message
    websocket_1.send_text.assert_called_once_with('{"event": "test", "data": "Hello, World!"}')
    websocket_2.send_text.assert_called_once_with('{"event": "test", "data": "Hello, World!"}')