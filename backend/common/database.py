"""
Shared MongoDB connection for all route modules.
Uses os.environ.get with clear error logging for production safety.
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')

if not mongo_url:
    logger.critical("MONGO_URL environment variable is NOT SET. Database operations will fail.")
    mongo_url = 'mongodb://localhost:27017'

if not db_name:
    logger.critical("DB_NAME environment variable is NOT SET. Database operations will fail.")
    db_name = 'trendscout'

logger.info(f"Connecting to MongoDB: {mongo_url[:30]}... / DB: {db_name}")

client = AsyncIOMotorClient(
    mongo_url,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=10000,
)
db = client[db_name]
