
from fastapi import APIRouter, WebSocket
from .ws import chat_handler

router = APIRouter()

@router.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await chat_handler(websocket)
