from motor.motor_asyncio import AsyncIOMotorClient
import os

class MongoManager:
    _client: AsyncIOMotorClient = None

    @classmethod
    async def connect(cls):
        cls._client = AsyncIOMotorClient(os.getenv("MONGO_URI"))

    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()

    @property
    def db(self):
        if not self._client:
            raise RuntimeError("MongoDB client not initialized.")
        return self._client.get_database("val-vod")

mongo = MongoManager()