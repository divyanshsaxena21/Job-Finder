from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"


# ===== USER SCHEMAS =====
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    telegram_chat_id: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    telegram_chat_id: Optional[str]
    created_at: datetime

    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ===== PREFERENCES SCHEMAS =====
class UserPreferencesUpdate(BaseModel):
    skills: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    experience: Optional[str] = None
    location: Optional[List[str]] = None
    job_type: Optional[List[JobType]] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    base_resume: Optional[str] = None
    # Social profiles
    github_username: Optional[str] = None
    github_token: Optional[str] = None
    linkedin_url: Optional[str] = None
    linkedin_email: Optional[str] = None
    # Auto-apply settings
    auto_apply_enabled: Optional[bool] = False
    auto_apply_frequency: Optional[str] = "daily"  # daily, weekly, bi-weekly
    include_github_projects: Optional[bool] = True
    max_daily_applications: Optional[int] = 5


class UserPreferencesResponse(BaseModel):
    user_id: str
    skills: List[str] = []
    roles: List[str] = []
    experience: Optional[str] = None
    location: List[str] = []
    job_type: List[JobType] = []
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    base_resume: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    auto_apply_enabled: bool = False
    auto_apply_frequency: str = "daily"
    include_github_projects: bool = True
    max_daily_applications: int = 5


# ===== JOB SCHEMAS =====
class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    apply_link: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    source: str = "manual"  # indeed, naukri, wellfound, manual


class JobResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    title: str
    company: str
    description: str
    apply_link: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    source: str
    match_score: Optional[float] = None
    match_reason: Optional[str] = None
    missing_skills: Optional[List[str]] = None
    status: str = "new"
    created_at: datetime

    class Config:
        populate_by_name = True


# ===== MATCH SCHEMAS =====
class JobMatchResult(BaseModel):
    match_score: float  # 0-100
    reason: str
    missing_skills: List[str]
    strengths: List[str]


# ===== GITHUB INTEGRATION =====
class GitHubRepo(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    topics: List[str] = []


class GitHubProfile(BaseModel):
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    repos: List[GitHubRepo] = []
    public_repos: int = 0


# ===== AUTO-APPLY SCHEMAS =====
class AutoApplyJob(BaseModel):
    job_id: str
    status: str  # "pending", "applied", "failed", "skipped"
    applied_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AutoApplyRun(BaseModel):
    user_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    jobs_found: int = 0
    jobs_applied: int = 0
    jobs_skipped: int = 0
    jobs_failed: int = 0
    details: List[AutoApplyJob] = []


# ===== RESUME & COVER LETTER SCHEMAS =====
class ResumeGenerationRequest(BaseModel):
    job_id: str


class ResumeLetter(BaseModel):
    resume: str
    cover_letter: str


# ===== APPLICATION SCHEMAS =====
class ApplicationCreate(BaseModel):
    job_id: str
    resume: str
    cover_letter: str


class ApplicationResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    job_id: str
    resume: str
    cover_letter: str
    status: ApplicationStatus
    submitted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True


# ===== TELEGRAM APPROVAL SCHEMAS =====
class TelegramApproval(BaseModel):
    user_id: str
    job_id: str
    action: str  # approve or reject
