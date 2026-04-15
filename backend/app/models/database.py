from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
from typing import Optional


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_db(cls, url: str, db_name: str):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(url)
        cls.db = cls.client[db_name]
        
        # Create indexes
        await cls._create_indexes()
        print("✓ Connected to MongoDB")

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("✓ Disconnected from MongoDB")

    @classmethod
    async def _create_indexes(cls):
        """Create necessary indexes"""
        # Users indexes
        await cls.db.users.create_index([("email", ASCENDING)], unique=True)
        
        # Jobs indexes
        await cls.db.jobs.create_index([("user_id", ASCENDING)])
        await cls.db.jobs.create_index([("source", ASCENDING)])
        await cls.db.jobs.create_index([("created_at", DESCENDING)])
        
        # Applications indexes
        await cls.db.applications.create_index([("user_id", ASCENDING)])
        await cls.db.applications.create_index([("job_id", ASCENDING)])
        await cls.db.applications.create_index([("status", ASCENDING)])
        
        # User preferences indexes
        await cls.db.user_preferences.create_index([("user_id", ASCENDING)], unique=True)
        
        # Auto-apply runs indexes
        await cls.db.auto_apply_runs.create_index([("user_id", ASCENDING)])
        await cls.db.auto_apply_runs.create_index([("started_at", DESCENDING)])

    @classmethod
    def get_db(cls):
        """Get database instance"""
        return cls.db


# Helper functions to get collections
def get_users_collection():
    return MongoDB.get_db().users


def get_jobs_collection():
    return MongoDB.get_db().jobs


def get_applications_collection():
    return MongoDB.get_db().applications


def get_preferences_collection():
    return MongoDB.get_db().user_preferences


def get_auto_apply_runs_collection():
    return MongoDB.get_db().auto_apply_runs
