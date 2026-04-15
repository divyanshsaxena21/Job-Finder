# API Specification

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except /auth) require JWT token in Authorization header:

```
Authorization: Bearer <token>
```

---

## Authentication Endpoints

### POST /auth/register

Register a new user.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure_password",
  "telegram_chat_id": "123456789"
}
```

**Response:** 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "telegram_chat_id": "123456789",
    "created_at": "2024-04-15T10:30:00Z"
  }
}
```

**Errors:**
- 400: Email already registered
- 500: Server error

---

### POST /auth/login

Login user and get token.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "secure_password"
}
```

**Response:** 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "telegram_chat_id": "123456789",
    "created_at": "2024-04-15T10:30:00Z"
  }
}
```

**Errors:**
- 401: Invalid credentials
- 500: Server error

---

### GET /auth/me

Get current authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** 200 OK
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@example.com",
  "telegram_chat_id": "123456789",
  "created_at": "2024-04-15T10:30:00Z"
}
```

**Errors:**
- 401: Invalid/expired token
- 404: User not found

---

## Jobs Endpoints

### POST /jobs

Create a new job.

**Request:**
```json
{
  "title": "Senior Backend Developer",
  "company": "Tech Corp",
  "description": "Looking for an experienced...",
  "apply_link": "https://example.com/job/123",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "job_type": "full_time",
  "source": "indeed"
}
```

**Response:** 200 OK
```json
{
  "id": "607f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "title": "Senior Backend Developer",
  "company": "Tech Corp",
  "description": "Looking for an experienced...",
  "apply_link": "https://example.com/job/123",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "job_type": "full_time",
  "source": "indeed",
  "match_score": null,
  "match_reason": null,
  "missing_skills": null,
  "status": "new",
  "created_at": "2024-04-15T10:35:00Z"
}
```

---

### GET /jobs

Get user's jobs with pagination.

**Query Parameters:**
- `skip`: Number of jobs to skip (default: 0)
- `limit`: Number of jobs to return (default: 20)

**Request:**
```
GET /jobs?skip=0&limit=20
```

**Response:** 200 OK
```json
[
  {
    "id": "607f1f77bcf86cd799439012",
    "user_id": "507f1f77bcf86cd799439011",
    "title": "Senior Backend Developer",
    "company": "Tech Corp",
    "description": "...",
    "apply_link": "https://example.com/job/123",
    "location": "San Francisco, CA",
    "salary_min": 120000,
    "salary_max": 180000,
    "job_type": "full_time",
    "source": "indeed",
    "match_score": null,
    "match_reason": null,
    "missing_skills": null,
    "status": "new",
    "created_at": "2024-04-15T10:35:00Z"
  }
]
```

---

### GET /jobs/{job_id}

Get specific job details.

**Response:** 200 OK
```json
{
  "id": "607f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "title": "Senior Backend Developer",
  "company": "Tech Corp",
  "description": "...",
  "apply_link": "https://example.com/job/123",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "job_type": "full_time",
  "source": "indeed",
  "match_score": null,
  "match_reason": null,
  "missing_skills": null,
  "status": "new",
  "created_at": "2024-04-15T10:35:00Z"
}
```

**Errors:**
- 404: Job not found

---

### POST /jobs/{job_id}/match

Analyze job match using AI.

**Response:** 200 OK
```json
{
  "match_score": 85.5,
  "reason": "Strong match - You have 4 out of 5 required skills",
  "missing_skills": ["Kubernetes"],
  "strengths": ["Python", "FastAPI", "PostgreSQL", "Docker"]
}
```

**Note:** This calls Groq API and may take 5-10 seconds.

---

### POST /jobs/{job_id}/generate-resume

Generate tailored resume for job.

**Response:** 200 OK
```json
{
  "resume": "JOHN DOE\n\nSoftware Engineer\njohn@example.com\n\nEXPERIENCE\n...",
  "cover_letter": ""
}
```

---

### POST /jobs/{job_id}/generate-cover-letter

Generate tailored cover letter for job.

**Response:** 200 OK
```json
{
  "resume": "",
  "cover_letter": "Dear Hiring Manager,\n\nI am writing to express my interest in the Senior Backend Developer position..."
}
```

---

### GET /jobs/filter-by-preferences

Get jobs filtered by user preferences.

**Response:** 200 OK
```json
[
  {
    "id": "607f1f77bcf86cd799439012",
    "title": "Senior Backend Developer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "match_score": 85.5,
    ...
  }
]
```

---

## Applications Endpoints

### POST /applications/{job_id}/submit

Create pending application (awaiting user approval).

**Request:**
```json
{
  "resume": "JOHN DOE\n\nSoftware Engineer\n...",
  "cover_letter": "Dear Hiring Manager,\n\nI am interested in..."
}
```

**Response:** 200 OK
```json
{
  "id": "707f1f77bcf86cd799439013",
  "user_id": "507f1f77bcf86cd799439011",
  "job_id": "607f1f77bcf86cd799439012",
  "resume": "JOHN DOE\n...",
  "cover_letter": "Dear Hiring Manager,\n...",
  "status": "pending",
  "submitted_at": null,
  "created_at": "2024-04-15T10:40:00Z"
}
```

**Side Effect:** Sends Telegram approval request to user.

---

### GET /applications

Get user's applications.

**Query Parameters:**
- `status_filter`: Filter by status (pending, approved, rejected, applied)

**Request:**
```
GET /applications?status_filter=pending
```

**Response:** 200 OK
```json
[
  {
    "id": "707f1f77bcf86cd799439013",
    "user_id": "507f1f77bcf86cd799439011",
    "job_id": "607f1f77bcf86cd799439012",
    "resume": "...",
    "cover_letter": "...",
    "status": "pending",
    "submitted_at": null,
    "created_at": "2024-04-15T10:40:00Z"
  }
]
```

---

### GET /applications/{app_id}

Get application details.

**Response:** 200 OK
```json
{
  "id": "707f1f77bcf86cd799439013",
  "user_id": "507f1f77bcf86cd799439011",
  "job_id": "607f1f77bcf86cd799439012",
  "resume": "...",
  "cover_letter": "...",
  "status": "pending",
  "submitted_at": null,
  "created_at": "2024-04-15T10:40:00Z"
}
```

---

### POST /applications/{app_id}/approve

Approve application (triggered by Telegram or API).

**Response:** 200 OK
```json
{
  "status": "approved",
  "message": "Application approved. Ready for submission."
}
```

**Side Effect:** 
- Updates application status to "approved"
- Triggers Playwright automation to fill and submit form
- Updates status to "applied" on success

---

### POST /applications/{app_id}/reject

Reject application.

**Response:** 200 OK
```json
{
  "status": "rejected",
  "message": "Application rejected."
}
```

---

## Preferences Endpoints

### GET /preferences

Get user preferences.

**Response:** 200 OK
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "skills": ["Python", "React", "PostgreSQL"],
  "roles": ["Full Stack Developer", "Backend Engineer"],
  "experience": "mid",
  "location": ["Remote", "San Francisco"],
  "job_type": ["full_time", "contract"],
  "min_salary": 100000,
  "max_salary": 180000
}
```

---

### PUT /preferences

Update user preferences.

**Request:**
```json
{
  "skills": ["Python", "React", "PostgreSQL", "Docker"],
  "roles": ["Full Stack Developer"],
  "experience": "senior",
  "location": ["Remote"],
  "job_type": ["full_time"],
  "min_salary": 120000,
  "max_salary": 200000
}
```

**Response:** 200 OK
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "skills": ["Python", "React", "PostgreSQL", "Docker"],
  "roles": ["Full Stack Developer"],
  "experience": "senior",
  "location": ["Remote"],
  "job_type": ["full_time"],
  "min_salary": 120000,
  "max_salary": 200000
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Email already registered |
| 500 | Server Error - Unexpected error |

---

## Rate Limiting

Currently no rate limiting. In production, implement:
- 100 requests/minute per user
- 1000 requests/hour per user
- 10 job matches per day per user

---

## WebSocket (Future)

For real-time notifications:
```
ws://localhost:8000/ws/{user_id}
```

Events:
- `application_created`
- `application_approved`
- `application_submitted`
- `match_score_updated`

---

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

Example:
```json
{
  "detail": "Email already registered"
}
```

---

## Examples

### Complete Workflow

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
# Response: { "access_token": "...", "user": {...} }

# 2. Save token
TOKEN="eyJhbGciOiJIUzI1NiIs..."

# 3. Add job
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Backend Developer",
    "company": "Tech Corp",
    "description": "Job description...",
    "apply_link": "https://example.com/job"
  }'

# 4. Analyze match
curl -X POST http://localhost:8000/jobs/607f1f77bcf86cd799439012/match \
  -H "Authorization: Bearer $TOKEN"

# 5. Generate resume
curl -X POST http://localhost:8000/jobs/607f1f77bcf86cd799439012/generate-resume \
  -H "Authorization: Bearer $TOKEN"

# 6. Generate cover letter
curl -X POST http://localhost:8000/jobs/607f1f77bcf86cd799439012/generate-cover-letter \
  -H "Authorization: Bearer $TOKEN"

# 7. Submit application
curl -X POST http://localhost:8000/applications/607f1f77bcf86cd799439012/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resume": "... resume content ...",
    "cover_letter": "... cover letter content ..."
  }'

# 8. View applications
curl -X GET http://localhost:8000/applications \
  -H "Authorization: Bearer $TOKEN"

# 9. Approve application (via Telegram or API)
curl -X POST http://localhost:8000/applications/707f1f77bcf86cd799439013/approve \
  -H "Authorization: Bearer $TOKEN"
```

---

Version: 1.0.0  
Last Updated: April 2026
