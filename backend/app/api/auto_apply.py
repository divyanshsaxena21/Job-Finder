"""
Auto-Apply Endpoints

Manages automated job applications.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from app.models.database import get_users_collection, get_auto_apply_runs_collection, get_preferences_collection
from app.models.schemas import UserPreferencesResponse
from app.services.auto_apply import AutoApplyOrchestrator
from app.utils.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auto-apply", tags=["auto-apply"])


@router.post("/trigger", status_code=202)
async def trigger_auto_apply(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Manually trigger auto-apply cycle for current user
    
    Returns: Job with submitted count (current auto-apply still running)
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Fetch preferences from preferences collection
        prefs_col = get_preferences_collection()
        prefs = await prefs_col.find_one({"user_id": str(user_id)})
        if not prefs or not prefs.get("auto_apply_enabled"):
            raise HTTPException(
                status_code=400, 
                detail="Auto-apply not enabled. Update preferences first."
            )
        
        # Convert to UserPreferencesResponse
        prefs_obj = UserPreferencesResponse(
            user_id=str(user_id),
            skills=prefs.get("skills", []),
            roles=prefs.get("roles", []),
            experience=prefs.get("experience"),
            location=prefs.get("location", []),
            job_type=prefs.get("job_type", []),
            min_salary=prefs.get("min_salary"),
            max_salary=prefs.get("max_salary"),
            base_resume=prefs.get("base_resume"),
            github_username=prefs.get("github_username"),
            linkedin_url=prefs.get("linkedin_url"),
            auto_apply_enabled=True,
            auto_apply_frequency=prefs.get("auto_apply_frequency", "daily"),
            include_github_projects=prefs.get("include_github_projects", True),
            max_daily_applications=prefs.get("max_daily_applications", 5)
        )
        
        # Run auto-apply (this would be async background task in production)
        logger.info(f"Manually triggered auto-apply for user {user_id}")
        
        result = await AutoApplyOrchestrator.run_auto_apply_cycle(user_id, prefs_obj)
        
        return {
            "status": "completed",
            "jobs_found": result.jobs_found,
            "jobs_applied": result.jobs_applied,
            "jobs_skipped": result.jobs_skipped,
            "jobs_failed": result.jobs_failed,
            "message": f"Applied to {result.jobs_applied} jobs, skipped {result.jobs_skipped}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering auto-apply: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_auto_apply_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 10
) -> dict:
    """
    Get auto-apply run history for current user
    
    Args:
        limit: Number of recent runs to return
    
    Returns: List of recent auto-apply runs
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Get auto-apply runs collection
        auto_apply_col = get_auto_apply_runs_collection()
        
        # Get recent runs for this user
        runs = await auto_apply_col.find(
            {"user_id": ObjectId(user_id)}
        ).sort("started_at", -1).limit(limit).to_list(None)
        
        # Convert ObjectIds to strings for JSON serialization
        for run in runs:
            run["_id"] = str(run["_id"])
            run["user_id"] = str(run["user_id"])
            if "details" in run:
                for detail in run["details"]:
                    if "job_id" in detail:
                        detail["job_id"] = str(detail["job_id"])
        
        return {
            "total_runs": len(runs),
            "runs": runs
        }
    
    except Exception as e:
        logger.error(f"Error fetching auto-apply history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_auto_apply_stats(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get auto-apply statistics for current user
    
    Returns: Stats including total applied, success rate, etc.
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Get auto-apply runs collection
        auto_apply_col = get_auto_apply_runs_collection()
        
        # Get all runs for this user
        runs = await auto_apply_col.find(
            {"user_id": ObjectId(user_id)}
        ).to_list(None)
        
        if not runs:
            return {
                "total_runs": 0,
                "total_applied": 0,
                "total_skipped": 0,
                "total_failed": 0,
                "average_applied_per_run": 0,
                "success_rate": 0.0,
                "last_run": None
            }
        
        # Calculate stats
        total_applied = sum(run.get("jobs_applied", 0) for run in runs)
        total_skipped = sum(run.get("jobs_skipped", 0) for run in runs)
        total_failed = sum(run.get("jobs_failed", 0) for run in runs)
        total_jobs = total_applied + total_skipped + total_failed
        
        success_rate = (total_applied / total_jobs * 100) if total_jobs > 0 else 0
        average_applied = total_applied / len(runs) if runs else 0
        
        # Get last run timestamp
        last_run = runs[0].get("started_at", None) if runs else None
        
        return {
            "total_runs": len(runs),
            "total_applied": total_applied,
            "total_skipped": total_skipped,
            "total_failed": total_failed,
            "average_applied_per_run": round(average_applied, 2),
            "success_rate": round(success_rate, 2),
            "last_run": str(last_run) if last_run else None
        }
    
    except Exception as e:
        logger.error(f"Error calculating auto-apply stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_scheduler_status(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get scheduler status and next run time
    
    Returns: Scheduler info and next scheduled run
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Fetch preferences from preferences collection
        prefs_col = get_preferences_collection()
        prefs = await prefs_col.find_one({"user_id": str(user_id)})
        
        if not prefs:
            return {
                "scheduler_running": False,
                "auto_apply_enabled": False,
                "auto_apply_frequency": "daily",
                "next_scheduled_run": None,
                "scheduled_time": "09:00 UTC (Daily)"
            }
        
        return {
            "scheduler_running": prefs.get("auto_apply_enabled", False),
            "auto_apply_enabled": prefs.get("auto_apply_enabled", False),
            "auto_apply_frequency": prefs.get("auto_apply_frequency", "daily"),
            "next_scheduled_run": None,
            "scheduled_time": "09:00 UTC (Daily)"  # Default schedule
        }
    
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
