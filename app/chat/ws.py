
from fastapi import WebSocket, WebSocketDisconnect
from .manager import manager

async def chat_handler(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # format: simple broadcast
            await manager.broadcast(f"💬 {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
