from app.models.database import get_jobs_collection, get_preferences_collection
from app.models.schemas import JobCreate, JobMatchResult
from bson import ObjectId
from datetime import datetime
from typing import List, Optional


class JobService:
    @staticmethod
    async def create_job(user_id: str, job_data: JobCreate) -> dict:
        """Create a new job"""
        jobs_col = get_jobs_collection()
        
        job_doc = {
            "user_id": user_id,
            "title": job_data.title,
            "company": job_data.company,
            "description": job_data.description,
            "apply_link": job_data.apply_link,
            "location": job_data.location,
            "salary_min": job_data.salary_min,
            "salary_max": job_data.salary_max,
            "job_type": job_data.job_type,
            "source": job_data.source,
            "match_score": None,
            "match_reason": None,
            "missing_skills": None,
            "status": "new",
            "created_at": datetime.utcnow(),
        }
        
        result = await jobs_col.insert_one(job_doc)
        job_doc["_id"] = result.inserted_id
        return job_doc

    @staticmethod
    async def get_user_jobs(user_id: str, skip: int = 0, limit: int = 20) -> List[dict]:
        """Get all jobs for a user"""
        jobs_col = get_jobs_collection()
        
        jobs = await jobs_col.find({"user_id": user_id}) \
            .skip(skip) \
            .limit(limit) \
            .sort("created_at", -1) \
            .to_list(limit)
        return jobs

    @staticmethod
    async def get_job(job_id: str, user_id: str) -> Optional[dict]:
        """Get a specific job"""
        jobs_col = get_jobs_collection()
        
        job = await jobs_col.find_one({
            "_id": ObjectId(job_id),
            "user_id": user_id
        })
        return job

    @staticmethod
    async def update_job_match(job_id: str, match_result: JobMatchResult):
        """Update job with match result"""
        jobs_col = get_jobs_collection()
        
        await jobs_col.find_one_and_update(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "match_score": match_result.match_score,
                    "match_reason": match_result.reason,
                    "missing_skills": match_result.missing_skills,
                    "strengths": match_result.strengths,
                    "status": "matched"
                }
            }
        )

    @staticmethod
    async def filter_jobs_by_preferences(user_id: str) -> List[dict]:
        """Filter jobs based on user preferences"""
        jobs_col = get_jobs_collection()
        prefs_col = get_preferences_collection()
        
        prefs = await prefs_col.find_one({"user_id": user_id})
        if not prefs:
            # Return all jobs if no preferences
            return await jobs_col.find({"user_id": user_id}).to_list(100)
        
        # Build filter query
        filters = {"user_id": user_id}
        
        # Filter by location
        if prefs.get("location"):
            filters["location"] = {"$in": prefs["location"]}
        
        # Filter by job type
        if prefs.get("job_type"):
            filters["job_type"] = {"$in": prefs["job_type"]}
        
        # Filter by salary
        if prefs.get("min_salary") or prefs.get("max_salary"):
            filters["$or"] = [
                {"salary_min": {"$gte": prefs.get("min_salary", 0)}},
                {"salary_max": {"$lte": prefs.get("max_salary", 999999)}}
            ]
        
        jobs = await jobs_col.find(filters).to_list(100)
        return jobs

    @staticmethod
    async def update_job_status(job_id: str, status: str):
        """Update job status"""
        jobs_col = get_jobs_collection()
        
        await jobs_col.find_one_and_update(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": status}}
        )
