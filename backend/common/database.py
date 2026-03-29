"""
Shared MongoDB connection for all route modules.

Client is created LAZILY on first access to avoid crashing at import
time if MongoDB Atlas DNS is slow or unreachable.

MONGO_URL and DB_NAME are REQUIRED.  The process will crash with a clear
error at first DB access if either is missing — no silent localhost fallback.
"""
import os
import sys
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None


def _init_client():
    """Create the Motor client lazily.  Called on first attribute access."""
    global _client, _db
    if _client is not None:
        return

    from motor.motor_asyncio import AsyncIOMotorClient

    mongo_url = os.environ.get("MONGO_URL", "")
    db_name = os.environ.get("DB_NAME", "")

    if not mongo_url:
        logger.critical("FATAL: MONGO_URL environment variable is not set. Exiting.")
        sys.exit(1)
    if not db_name:
        logger.critical("FATAL: DB_NAME environment variable is not set. Exiting.")
        sys.exit(1)

    logger.info("Connecting to MongoDB: %s... / DB: %s", mongo_url[:40], db_name)

    _client = AsyncIOMotorClient(
        mongo_url,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
    )
    _db = _client[db_name]


class _LazyDB:
    """Proxy that initializes the Motor client on first attribute access."""

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
