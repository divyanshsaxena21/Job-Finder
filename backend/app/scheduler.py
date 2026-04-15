"""
Scheduler Setup

Manages scheduled tasks like auto-apply cycles.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.config import settings
from app.models.database import get_users_collection, get_preferences_collection
from app.services.auto_apply import AutoApplyOrchestrator
from app.models.schemas import UserPreferencesResponse
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def auto_apply_job():
    """
    Scheduled job to run auto-apply for all enabled users
    
    Runs daily at 9 AM by default
    """
    logger.info("Starting scheduled auto-apply job...")
    
    try:
        # Get all users with auto_apply enabled
        prefs_col = get_preferences_collection()
        enabled_users = await prefs_col.find({"auto_apply_enabled": True}).to_list(None)
        
        if not enabled_users:
            logger.info("No users with auto-apply enabled")
            return
        
        logger.info(f"Running auto-apply for {len(enabled_users)} users")
        
        for user_pref in enabled_users:
            try:
                user_id = user_pref["user_id"]
                
                # Convert to UserPreferencesResponse
                prefs = UserPreferencesResponse(
                    user_id=user_id,
                    skills=user_pref.get("skills", []),
                    roles=user_pref.get("roles", []),
                    experience=user_pref.get("experience"),
                    location=user_pref.get("location", []),
                    job_type=user_pref.get("job_type", []),
                    min_salary=user_pref.get("min_salary"),
                    max_salary=user_pref.get("max_salary"),
                    base_resume=user_pref.get("base_resume"),
                    github_username=user_pref.get("github_username"),
                    auto_apply_enabled=True,
                    include_github_projects=user_pref.get("include_github_projects", True),
                    max_daily_applications=user_pref.get("max_daily_applications", 5)
                )
                
                # Run auto-apply cycle
                result = await AutoApplyOrchestrator.run_auto_apply_cycle(user_id, prefs)
                logger.info(f"User {user_id}: Applied {result.jobs_applied}, "
                           f"Skipped {result.jobs_skipped}, Failed {result.jobs_failed}")
            
            except Exception as e:
                logger.error(f"Error in auto-apply for user {user_pref.get('user_id')}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in scheduled auto-apply job: {str(e)}")


def init_scheduler():
    """Initialize the scheduler"""
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return
    
    # Add auto-apply job - daily at 9 AM
    scheduler.add_job(
        auto_apply_job,
        CronTrigger(hour=9, minute=0),
        id="auto_apply_daily",
        name="Daily Auto-Apply Job",
        replace_existing=True
    )
    
    logger.info("Scheduler initialized with auto-apply job (daily at 9 AM)")
    scheduler.start()


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def get_scheduler():
    """Get the scheduler instance"""
    return scheduler
