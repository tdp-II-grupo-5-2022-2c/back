from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.db import DatabaseManager
from unittest.mock import MagicMock



class MockMongoManager(DatabaseManager):
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = MagicMock()

    async def connect_to_database(self, path: str):
        pass

    async def close_database_connection(self):
        pass