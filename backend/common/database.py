"""
Shared MongoDB connection for all route modules.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = os.environ['MONGO_URL']
# serverSelectionTimeoutMS: fail fast if Atlas is unreachable (default 30s is too long for K8s probes)
# connectTimeoutMS: individual socket connect timeout
client = AsyncIOMotorClient(
    mongo_url,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=10000,
)
db = client[os.environ['DB_NAME']]
