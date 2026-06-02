from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import websocket_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/executions/{execution_id}")
async def execution_socket(websocket: WebSocket, execution_id: UUID):
    await websocket_manager.connect(str(execution_id), websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(str(execution_id), websocket)
