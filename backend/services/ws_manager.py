"""
WebSocket connection manager for real-time notifications.
Broadcasts automation progress, import status, and system events to all connected clients.
"""
import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime, timezone
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per user."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._broadcast_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: str = "anonymous"):
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        self._broadcast_connections.add(websocket)
        logger.info(f"WS connected: user={user_id}, total={len(self._broadcast_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: str = "anonymous"):
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
        self._broadcast_connections.discard(websocket)
        logger.info(f"WS disconnected: user={user_id}, total={len(self._broadcast_connections)}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all connections of a specific user."""
        if user_id in self._connections:
            dead = []
            for ws in self._connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.disconnect(ws, user_id)

    async def broadcast(self, message: dict):
        """Send a message to ALL connected clients."""
        dead = []
        for ws in self._broadcast_connections.copy():
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            # Find and clean up dead connections
            for uid, conns in list(self._connections.items()):
                if ws in conns:
                    self.disconnect(ws, uid)
                    break
            else:
                self._broadcast_connections.discard(ws)

    @property
    def active_count(self) -> int:
        return len(self._broadcast_connections)


# Singleton instance
ws_manager = ConnectionManager()


async def notify_job_started(job_type: str, source: str = None, metadata: dict = None):
    """Broadcast that an automation job has started."""
    await ws_manager.broadcast({
        "type": "job_started",
        "job_type": job_type,
        "source": source,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def notify_job_progress(job_type: str, current: int, total: int, source: str = None, detail: str = None):
    """Broadcast progress update for a running job."""
    await ws_manager.broadcast({
        "type": "job_progress",
        "job_type": job_type,
        "current": current,
        "total": total,
        "source": source,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def notify_job_completed(job_type: str, result: dict = None, source: str = None):
    """Broadcast that a job has completed."""
    await ws_manager.broadcast({
        "type": "job_completed",
        "job_type": job_type,
        "source": source,
        "result": result or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def notify_job_failed(job_type: str, error: str, source: str = None):
    """Broadcast that a job has failed."""
    await ws_manager.broadcast({
        "type": "job_failed",
        "job_type": job_type,
        "source": source,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
