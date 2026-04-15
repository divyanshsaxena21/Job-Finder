"""
Auto-Apply Orchestrator

Coordinates job scraping, matching, resume customization, and application submission.
"""

from typing import List, Optional, Dict
from datetime import datetime
from app.models.schemas import (
    JobCreate, UserPreferencesResponse, AutoApplyJob, AutoApplyRun,
    GitHubProfile
)
from app.services.job_scraper import JobScraperService
from app.services.resume_customizer import ResumeCustomizerService
from app.services.github_service import GitHubService
from app.services.form_submission import FormSubmissionService
from app.services.quality_scorer import JobQualityScorer
from app.models.database import (
    MongoDB, get_jobs_collection, get_applications_collection,
    get_auto_apply_runs_collection
)
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AutoApplyOrchestrator:
    """Orchestrates the auto-apply workflow"""
    
    @staticmethod
    async def run_auto_apply_cycle(user_id: str, preferences: UserPreferencesResponse) -> AutoApplyRun:
        """
        Execute a complete auto-apply cycle:
        1. Scrape jobs
        2. Match with preferences
        3. Customize resume
        4. Auto-apply
        
        Args:
            user_id: User ID
            preferences: User preferences
        
        Returns:
            AutoApplyRun with results
        """
        run = AutoApplyRun(
            user_id=user_id,
            started_at=datetime.now(),
            details=[]
        )
        
        logger.info(f"Starting auto-apply cycle for user {user_id}")
        
        try:
            # Step 1: Scrape jobs
            logger.info("Step 1: Scraping jobs...")
            scraped_jobs = await JobScraperService.scrape_jobs(preferences, max_results=50)
            run.jobs_found = len(scraped_jobs)
            logger.info(f"Found {len(scraped_jobs)} jobs")
            
            if not scraped_jobs:
                logger.warning("No jobs found")
                run.completed_at = datetime.now()
                return run
            
            # Step 2: Fetch GitHub profile if available
            github_profile: Optional[GitHubProfile] = None
            if preferences.github_username and preferences.include_github_projects:
                logger.info(f"Fetching GitHub profile: {preferences.github_username}")
                github_profile = await GitHubService.get_user_repos(
                    preferences.github_username,
                    preferences.github_token
                )
                if github_profile:
                    logger.info(f"Found {len(github_profile.repos)} repositories")
            
            # Step 3: Process each job
            applied_count = 0
            for job in scraped_jobs:
                if applied_count >= preferences.max_daily_applications:
                    logger.info(f"Reached daily application limit ({preferences.max_daily_applications})")
                    break
                
                try:
                    # Check if already applied
                    existing_app = await AutoApplyOrchestrator._check_existing_application(
                        user_id, job.title, job.company
                    )
                    if existing_app:
                        run.details.append(AutoApplyJob(
                            job_id="", status="skipped",
                            error_message=f"Already applied to {job.company}"
                        ))
                        run.jobs_skipped += 1
                        continue
                    
                    # Quality score the job
                    quality_score, quality_reason, quality_details = JobQualityScorer.score_job(
                        job.title, job.company, job.description
                    )
                    
                    should_skip, skip_reason = JobQualityScorer.should_skip_job(quality_score, min_quality=50)
                    if should_skip:
                        run.details.append(AutoApplyJob(
                            job_id="", status="skipped",
                            error_message=f"Low quality: {skip_reason}"
                        ))
                        run.jobs_skipped += 1
                        logger.info(f"Skipping low-quality job: {skip_reason}")
                        continue
                    
                    # Match job with preferences
                    job_keywords = ResumeCustomizerService.extract_keywords(job.description)
                    match_score = ResumeCustomizerService.calculate_match_score(
                        job_keywords, preferences.skills, preferences.experience
                    )
                    
                    if match_score < 40:  # Only apply to jobs with >40% match
                        run.details.append(AutoApplyJob(
                            job_id="", status="skipped",
                            error_message=f"Low match score: {match_score:.0f}%"
                        ))
                        run.jobs_skipped += 1
                        continue
                    
                    # Customize resume
                    customized_resume = ResumeCustomizerService.customize_resume(
                        preferences.base_resume or "",
                        job.description,
                        github_profile,
                        preferences.skills
                    )
                    
                    # Generate cover letter using Groq AI
                    logger.info(f"Generating cover letter for {job.title} at {job.company}")
                    cover_letter = await ResumeCustomizerService.generate_cover_letter_with_groq(
                        job.title, job.company, job.description,
                        user_id, preferences.skills, match_score
                    )
                    
                    # Try to auto-apply
                    success, submit_msg = await AutoApplyOrchestrator._submit_application(
                        user_id, job, customized_resume, cover_letter, preferences
                    )
                    
                    if success:
                        applied_count += 1
                        run.jobs_applied += 1
                        run.details.append(AutoApplyJob(
                            job_id="", status="applied", applied_at=datetime.now()
                        ))
                        logger.info(f"Applied to {job.title} at {job.company}")
                    else:
                        run.jobs_failed += 1
                        run.details.append(AutoApplyJob(
                            job_id="", status="failed",
                            error_message=f"Failed to auto-apply: {submit_msg}"
                        ))
                        logger.warning(f"Failed to apply: {submit_msg}")
                
                except Exception as e:
                    logger.error(f"Error applying to job: {str(e)}")
                    run.jobs_failed += 1
                    run.details.append(AutoApplyJob(
                        job_id="", status="failed",
                        error_message=str(e)
                    ))
            
            run.completed_at = datetime.now()
            logger.info(f"Auto-apply cycle completed. Applied: {run.jobs_applied}, "
                       f"Skipped: {run.jobs_skipped}, Failed: {run.jobs_failed}")
            
            # Save run to database for history tracking
            try:
                auto_apply_col = get_auto_apply_runs_collection()
                run_data = {
                    "user_id": user_id,  # Keep as string, matches schema
                    "started_at": run.started_at,
                    "completed_at": run.completed_at,
                    "jobs_found": run.jobs_found,
                    "jobs_applied": run.jobs_applied,
                    "jobs_skipped": run.jobs_skipped,
                    "jobs_failed": run.jobs_failed,
                    "details": [
                        {
                            "job_id": detail.job_id,
                            "status": detail.status,
                            "applied_at": detail.applied_at,
                            "error_message": detail.error_message
                        }
                        for detail in run.details
                    ]
                }
                await auto_apply_col.insert_one(run_data)
            except Exception as e:
                logger.warning(f"Failed to save auto-apply run to database: {str(e)}")
            
            return run
        
        except Exception as e:
            logger.error(f"Error in auto-apply cycle: {str(e)}")
            run.completed_at = datetime.now()
            return run
    
    @staticmethod
    async def _check_existing_application(user_id: str, job_title: str, company: str) -> bool:
        """Check if user already applied to similar job"""
        # TODO: Implement check in database
        return False
    
    @staticmethod
    async def _submit_application(
        user_id: str,
        job: JobCreate,
        resume: str,
        cover_letter: str,
        preferences: UserPreferencesResponse
    ) -> tuple[bool, str]:
        """
        Submit application to job platform
        
        Args:
            user_id: User ID
            job: Job to apply for
            resume: Customized resume
            cover_letter: Generated cover letter
            preferences: User preferences (for contact info)
        
        Returns:
            Tuple[success, message]
        """
        try:
            # Use FormSubmissionService to actually submit the form
            logger.info(f"Submitting application to {job.source}: {job.apply_link}")
            
            success, submit_msg = await FormSubmissionService.submit_job_application(
                job_url=job.apply_link,
                job_source=job.source,
                resume_text=resume,
                cover_letter=cover_letter,
                user_email=preferences.email or "",
                user_name=preferences.name or "Applicant",
                phone_number=getattr(preferences, 'phone', None),
                github_url=getattr(preferences, 'github_username', None),
                linkedin_url=getattr(preferences, 'linkedin_url', None)
            )
            
            # Save job if doesn't exist
            jobs_col = get_jobs_collection()
            existing = await jobs_col.find_one({"apply_link": job.apply_link, "user_id": user_id})
            if not existing:
                job_data = {
                    "user_id": user_id,
                    "title": job.title,
                    "company": job.company,
                    "description": job.description,
                    "apply_link": job.apply_link,
                    "location": job.location,
                    "source": job.source,
                    "created_at": datetime.now()
                }
                result = await jobs_col.insert_one(job_data)
                job_id = str(result.inserted_id)
            else:
                job_id = str(existing["_id"])
            
            # Save application with submission status
            applications_col = get_applications_collection()
            app_data = {
                "user_id": user_id,
                "job_id": job_id,
                "resume": resume,
                "cover_letter": cover_letter,
                "status": "applied" if success else "failed",
                "submission_status": submit_msg,
                "submitted_at": datetime.now(),
                "created_at": datetime.now()
            }
            await applications_col.insert_one(app_data)
            
            return success, submit_msg
        
        except Exception as e:
            logger.error(f"Error submitting application: {str(e)}")
            return False, f"Error: {str(e)}"
