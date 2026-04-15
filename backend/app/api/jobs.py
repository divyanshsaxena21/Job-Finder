from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import (
    JobCreate, JobResponse, JobMatchResult, ResumeGenerationRequest, ResumeLetter
)
from app.services.job_service import JobService
from app.services.auth_service import PreferencesService
from app.integrations.groq_service import GroqService
from app.utils.dependencies import get_current_user
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/jobs", tags=["Jobs"])
groq_service = GroqService()


@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new job"""
    try:
        user_id = str(current_user["_id"])
        job = await JobService.create_job(user_id, job_data)
        
        return JobResponse(
            _id=str(job["_id"]),
            user_id=job["user_id"],
            title=job["title"],
            company=job["company"],
            description=job["description"],
            apply_link=job["apply_link"],
            location=job.get("location"),
            salary_min=job.get("salary_min"),
            salary_max=job.get("salary_max"),
            job_type=job.get("job_type"),
            source=job["source"],
            match_score=job.get("match_score"),
            match_reason=job.get("match_reason"),
            missing_skills=job.get("missing_skills"),
            status=job["status"],
            created_at=job["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user's jobs"""
    try:
        user_id = str(current_user["_id"])
        jobs = await JobService.get_user_jobs(user_id, skip, limit)
        
        return [
            JobResponse(
                _id=str(job["_id"]),
                user_id=job["user_id"],
                title=job["title"],
                company=job["company"],
                description=job["description"],
                apply_link=job["apply_link"],
                location=job.get("location"),
                salary_min=job.get("salary_min"),
                salary_max=job.get("salary_max"),
                job_type=job.get("job_type"),
                source=job["source"],
                match_score=job.get("match_score"),
                match_reason=job.get("match_reason"),
                missing_skills=job.get("missing_skills"),
                status=job["status"],
                created_at=job["created_at"]
            )
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get job details"""
    try:
        user_id = str(current_user["_id"])
        job = await JobService.get_job(job_id, user_id)
        
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        return JobResponse(
            _id=str(job["_id"]),
            user_id=job["user_id"],
            title=job["title"],
            company=job["company"],
            description=job["description"],
            apply_link=job["apply_link"],
            location=job.get("location"),
            salary_min=job.get("salary_min"),
            salary_max=job.get("salary_max"),
            job_type=job.get("job_type"),
            source=job["source"],
            match_score=job.get("match_score"),
            match_reason=job.get("match_reason"),
            missing_skills=job.get("missing_skills"),
            status=job["status"],
            created_at=job["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{job_id}/match", response_model=JobMatchResult)
async def match_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Match job with user profile"""
    try:
        user_id = str(current_user["_id"])
        
        # Get job
        job = await JobService.get_job(job_id, user_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # Get match result
        match_result = await groq_service.match_job(user_id, job)
        
        # Update job with match result
        await JobService.update_job_match(job_id, match_result)
        
        return match_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{job_id}/generate-resume", response_model=ResumeLetter)
async def generate_resume(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate tailored resume"""
    try:
        user_id = str(current_user["_id"])
        
        job = await JobService.get_job(job_id, user_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        resume = await groq_service.generate_resume(user_id, job, current_user)
        
        return ResumeLetter(
            resume=resume,
            cover_letter=""
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{job_id}/generate-cover-letter", response_model=ResumeLetter)
async def generate_cover_letter(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate tailored cover letter"""
    try:
        user_id = str(current_user["_id"])
        
        job = await JobService.get_job(job_id, user_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        cover_letter = await groq_service.generate_cover_letter(user_id, job, current_user)
        
        return ResumeLetter(
            resume="",
            cover_letter=cover_letter
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/filter-by-preferences", response_model=List[JobResponse])
async def filter_jobs_by_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get jobs filtered by user preferences"""
    try:
        user_id = str(current_user["_id"])
        jobs = await JobService.filter_jobs_by_preferences(user_id)
        
        return [
            JobResponse(
                _id=str(job["_id"]),
                user_id=job["user_id"],
                title=job["title"],
                company=job["company"],
                description=job["description"],
                apply_link=job["apply_link"],
                location=job.get("location"),
                salary_min=job.get("salary_min"),
                salary_max=job.get("salary_max"),
                job_type=job.get("job_type"),
                source=job["source"],
                match_score=job.get("match_score"),
                match_reason=job.get("match_reason"),
                missing_skills=job.get("missing_skills"),
                status=job["status"],
                created_at=job["created_at"]
            )
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
