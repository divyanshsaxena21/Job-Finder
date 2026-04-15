from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import ApplicationResponse, ApplicationStatus
from app.services.application_service import ApplicationService
from app.integrations.telegram_bot import telegram_bot
from app.utils.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/{job_id}/submit", response_model=ApplicationResponse)
async def submit_application(
    job_id: str,
    resume: str,
    cover_letter: str,
    current_user: dict = Depends(get_current_user)
):
    """Create a pending application (awaiting user approval via Telegram)"""
    try:
        user_id = str(current_user["_id"])
        
        # Create application in pending status
        app = await ApplicationService.create_application(
            user_id,
            job_id,
            resume,
            cover_letter
        )
        
        # Send Telegram notification
        if current_user.get("telegram_chat_id"):
            # Get job info for notification (would need job_service call)
            await telegram_bot.send_approval_request(
                chat_id=current_user["telegram_chat_id"],
                job_title="Job Title",  # Would get from job service
                company="Company Name",
                match_score=0,
                app_id=str(app["_id"])
            )
        
        return ApplicationResponse(
            _id=str(app["_id"]),
            user_id=app["user_id"],
            job_id=app["job_id"],
            resume=app["resume"],
            cover_letter=app["cover_letter"],
            status=ApplicationStatus(app["status"]),
            submitted_at=app.get("submitted_at"),
            created_at=app["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    status_filter: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's applications"""
    try:
        user_id = str(current_user["_id"])
        applications = await ApplicationService.get_user_applications(user_id, status_filter)
        
        return [
            ApplicationResponse(
                _id=str(app["_id"]),
                user_id=app["user_id"],
                job_id=app["job_id"],
                resume=app["resume"],
                cover_letter=app["cover_letter"],
                status=ApplicationStatus(app["status"]),
                submitted_at=app.get("submitted_at"),
                created_at=app["created_at"]
            )
            for app in applications
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific application"""
    try:
        user_id = str(current_user["_id"])
        app = await ApplicationService.get_application(app_id, user_id)
        
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
        return ApplicationResponse(
            _id=str(app["_id"]),
            user_id=app["user_id"],
            job_id=app["job_id"],
            resume=app["resume"],
            cover_letter=app["cover_letter"],
            status=ApplicationStatus(app["status"]),
            submitted_at=app.get("submitted_at"),
            created_at=app["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{app_id}/approve")
async def approve_application(
    app_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Approve application (called by Telegram callback or API)"""
    try:
        user_id = str(current_user["_id"])
        
        # Verify ownership
        app = await ApplicationService.get_application(app_id, user_id)
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
        updated_app = await ApplicationService.approve_application(app_id)
        
        return {
            "status": "approved",
            "message": "Application approved. Ready for submission."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{app_id}/reject")
async def reject_application(
    app_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Reject application"""
    try:
        user_id = str(current_user["_id"])
        
        # Verify ownership
        app = await ApplicationService.get_application(app_id, user_id)
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
        await ApplicationService.reject_application(app_id)
        
        return {
            "status": "rejected",
            "message": "Application rejected."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
