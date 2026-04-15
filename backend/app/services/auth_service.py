from app.models.database import get_users_collection, get_preferences_collection
from app.models.schemas import UserRegister, UserResponse, UserPreferencesResponse
from app.utils.auth import hash_password, verify_password, create_access_token
from bson import ObjectId
from datetime import datetime


class AuthService:
    @staticmethod
    async def register(user_data: UserRegister) -> dict:
        """Register a new user"""
        users_col = get_users_collection()
        
        # Check if user already exists
        existing_user = await users_col.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create user
        user_doc = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "telegram_chat_id": user_data.telegram_chat_id,
            "created_at": datetime.utcnow(),
        }
        
        result = await users_col.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        # Create empty preferences
        prefs_col = get_preferences_collection()
        await prefs_col.insert_one({
            "user_id": str(result.inserted_id),
            "skills": [],
            "roles": [],
            "experience": None,
            "location": [],
            "job_type": [],
            "min_salary": None,
            "max_salary": None,
        })
        
        return user_doc

    @staticmethod
    async def login(email: str, password: str) -> dict:
        """Login user"""
        users_col = get_users_collection()
        
        user = await users_col.find_one({"email": email})
        if not user:
            raise ValueError("Invalid credentials")
        
        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")
        
        return user

    @staticmethod
    async def get_user_by_id(user_id: str) -> dict:
        """Get user by ID"""
        users_col = get_users_collection()
        user = await users_col.find_one({"_id": ObjectId(user_id)})
        return user


class PreferencesService:
    @staticmethod
    async def get_preferences(user_id: str) -> dict:
        """Get user preferences"""
        prefs_col = get_preferences_collection()
        prefs = await prefs_col.find_one({"user_id": user_id})
        return prefs

    @staticmethod
    async def update_preferences(user_id: str, prefs_data: dict) -> dict:
        """Update user preferences"""
        prefs_col = get_preferences_collection()
        
        update_data = {}
        for key, value in prefs_data.items():
            if value is not None:
                update_data[key] = value
        
        result = await prefs_col.find_one_and_update(
            {"user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
        return result
