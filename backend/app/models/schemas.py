from pydantic import BaseModel, EmailStr, Field
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
