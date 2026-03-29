"""
Shared MongoDB connection for all route modules.
Client is created LAZILY on first access to avoid crashing
at import time if MongoDB Atlas DNS is slow/unreachable.
"""
import os
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None


def _get_mongo_url():
    url = os.environ.get('MONGO_URL', '')
    if not url:
        logger.critical("MONGO_URL is NOT SET")
    return url


def _get_db_name():
    name = os.environ.get('DB_NAME', '')
    if not name:
        logger.critical("DB_NAME is NOT SET")
    return name


def _init_client():
    """Create the Motor client lazily. Called on first attribute access."""
    global _client, _db
    if _client is not None:
        return

    from motor.motor_asyncio import AsyncIOMotorClient

    mongo_url = _get_mongo_url()
    db_name = _get_db_name()

    logger.info(f"Connecting to MongoDB: {mongo_url[:40]}... / DB: {db_name}")

    _client = AsyncIOMotorClient(
        mongo_url,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
    )
    _db = _client[db_name]


class _LazyDB:
    """Proxy that initializes the Motor client on first attribute access.
    Allows `from common.database import db` to work at import time
    without actually connecting to MongoDB."""

    def __getattr__(self, name):
        _init_client()
        return getattr(_db, name)

    def __getitem__(self, name):
        _init_client()
        return _db[name]

    def __repr__(self):
        return f"<LazyDB connected={_client is not None}>"


class _LazyClient:
    """Proxy for the Motor client."""

    def __getattr__(self, name):
        _init_client()
        return getattr(_client, name)

    def close(self):
        if _client is not None:
            _client.close()


db = _LazyDB()
client = _LazyClient()
