from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import UserPreferencesUpdate, UserPreferencesResponse
from app.services.auth_service import PreferencesService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get("/", response_model=UserPreferencesResponse)
async def get_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get user preferences"""
    try:
        user_id = str(current_user["_id"])
        prefs = await PreferencesService.get_preferences(user_id)
        
        if not prefs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")
        
        return UserPreferencesResponse(
            user_id=prefs["user_id"],
            skills=prefs.get("skills", []),
            roles=prefs.get("roles", []),
            experience=prefs.get("experience"),
            location=prefs.get("location", []),
            job_type=prefs.get("job_type", []),
            min_salary=prefs.get("min_salary"),
            max_salary=prefs.get("max_salary"),
            base_resume=prefs.get("base_resume")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/", response_model=UserPreferencesResponse)
async def update_preferences(
    prefs_data: UserPreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        user_id = str(current_user["_id"])
        
        # Convert to dict and filter None values
        update_dict = {k: v for k, v in prefs_data.dict().items() if v is not None}
        
        updated_prefs = await PreferencesService.update_preferences(user_id, update_dict)
        
        if not updated_prefs:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update preferences")
        
        return UserPreferencesResponse(
            user_id=updated_prefs["user_id"],
            skills=updated_prefs.get("skills", []),
            roles=updated_prefs.get("roles", []),
            experience=updated_prefs.get("experience"),
            location=updated_prefs.get("location", []),
            job_type=updated_prefs.get("job_type", []),
            min_salary=updated_prefs.get("min_salary"),
            max_salary=updated_prefs.get("max_salary"),
            base_resume=updated_prefs.get("base_resume")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
