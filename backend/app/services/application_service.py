from app.models.database import get_applications_collection
from app.models.schemas import ApplicationStatus
from bson import ObjectId
from datetime import datetime
from typing import List, Optional


class ApplicationService:
    @staticmethod
    async def create_application(
        user_id: str,
        job_id: str,
        resume: str,
        cover_letter: str
    ) -> dict:
        """Create a pending application"""
        apps_col = get_applications_collection()
        
        app_doc = {
            "user_id": user_id,
            "job_id": job_id,
            "resume": resume,
            "cover_letter": cover_letter,
            "status": ApplicationStatus.PENDING.value,
            "submitted_at": None,
            "created_at": datetime.utcnow(),
        }
        
        result = await apps_col.insert_one(app_doc)
        app_doc["_id"] = result.inserted_id
        return app_doc

    @staticmethod
    async def get_user_applications(user_id: str, status: Optional[str] = None) -> List[dict]:
        """Get user applications"""
        apps_col = get_applications_collection()
        
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        applications = await apps_col.find(query).sort("created_at", -1).to_list(100)
        return applications

    @staticmethod
    async def get_application(app_id: str, user_id: str) -> Optional[dict]:
        """Get specific application"""
        apps_col = get_applications_collection()
        
        app = await apps_col.find_one({
            "_id": ObjectId(app_id),
            "user_id": user_id
        })
        return app

    @staticmethod
    async def approve_application(app_id: str) -> dict:
        """Approve application (after user approval from Telegram)"""
        apps_col = get_applications_collection()
        
        app = await apps_col.find_one_and_update(
            {"_id": ObjectId(app_id)},
            {
                "$set": {
                    "status": ApplicationStatus.APPROVED.value,
                    "approved_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return app

    @staticmethod
    async def reject_application(app_id: str) -> dict:
        """Reject application"""
        apps_col = get_applications_collection()
        
        app = await apps_col.find_one_and_update(
            {"_id": ObjectId(app_id)},
            {
                "$set": {
                    "status": ApplicationStatus.REJECTED.value,
                    "rejected_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return app

    @staticmethod
    async def mark_submitted(app_id: str) -> dict:
        """Mark application as submitted"""
        apps_col = get_applications_collection()
        
        app = await apps_col.find_one_and_update(
            {"_id": ObjectId(app_id)},
            {
                "$set": {
                    "status": ApplicationStatus.APPLIED.value,
                    "submitted_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return app

    @staticmethod
    async def mark_failed(app_id: str, error_msg: str) -> dict:
        """Mark application as failed"""
        apps_col = get_applications_collection()
        
        app = await apps_col.find_one_and_update(
            {"_id": ObjectId(app_id)},
            {
                "$set": {
                    "status": ApplicationStatus.FAILED.value,
                    "failed_reason": error_msg,
                    "failed_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return app
