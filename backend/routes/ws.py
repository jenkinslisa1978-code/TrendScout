"""
WebSocket endpoint for real-time notifications.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
import jwt
import os

from services.ws_manager import ws_manager

logger = logging.getLogger(__name__)

ws_router = APIRouter()

JWT_SECRET = os.environ.get("JWT_SECRET", "")


def _extract_user_id(token: str) -> str:
    """Extract user_id from JWT token. Returns 'anonymous' if invalid."""
    if not token or not JWT_SECRET:
        return "anonymous"
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("user_id", "anonymous")
    except Exception:
        return "anonymous"


@ws_router.websocket("/api/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time notifications.
    Connect with: ws://host/api/ws/notifications?token=JWT_TOKEN
    """
    user_id = _extract_user_id(token)
    await ws_manager.connect(websocket, user_id)

    try:
        while True:
            # Keep connection alive; client can send pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception:
        ws_manager.disconnect(websocket, user_id)


routers = [ws_router]
