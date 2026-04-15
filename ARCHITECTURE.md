# System Architecture

## Overview

Job Finder is a modern, multi-user AI-powered job application assistant built with a microservice-like architecture separating concerns across different layers.

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│               React Frontend (SPA) - Vite                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │ Auth Pages   │ Dashboard    │ Job Detail   │ Applications │  │
│  │ Register     │ Job List     │ Match Score  │ Preferences  │  │
│  │ Login        │ Filters      │ Resume Gen   │              │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                                                                  │
│  ├─ Context API (Auth, User State)                             │
│  ├─ React Router (Navigation)                                  │
│  └─ Axios (API Client)                                         │
└─────────────────────────────────────────────────────────────────┘
                             │ HTTP/REST
                             │ JWT Auth
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│              FastAPI (async, high performance)                  │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │ Auth Routes  │ Job Routes   │ App Routes   │ Preference   │  │
│  │ /auth/*      │ /jobs/*      │ /app/*       │ /pref/*      │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                                                                  │
│  ├─ Request Validation (Pydantic)                              │
│  ├─ JWT Authentication                                         │
│  ├─ Error Handling                                             │
│  └─ CORS Middleware                                            │
└─────────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  BUSINESS     │  │  INTEGRATION     │  │  AUTOMATION      │
│  LOGIC        │  │  SERVICES        │  │  SERVICES        │
├───────────────┤  ├──────────────────┤  ├──────────────────┤
│ Auth Service  │  │ Groq SDK         │  │ Playwright       │
│ Job Service   │  │ Telegram SDK     │  │ Browser Control  │
│ App Service   │  │ API Clients      │  │ Form Filling     │
│ Pref Service  │  │                  │  │ Resume Upload    │
└───────────────┘  └──────────────────┘  └──────────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
        ┌────────────────────┬────────────────────┐
        ▼                    ▼                    ▼
    ┌────────────┐    ┌─────────────┐    ┌──────────────┐
    │ MongoDB    │    │ Groq API    │    │ Playwright   │
    │ Database   │    │ (Cloud)     │    │ (Headless)   │
    │            │    │             │    │              │
    │ • Users    │    │ • Matching  │    │ • Fill Forms │
    │ • Jobs     │    │ • Resume    │    │ • Submit     │
    │ • Apps     │    │ • Letters   │    │ • Screenshot │
    │ • Prefs    │    │             │    │              │
    └────────────┘    └─────────────┘    └──────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │ Telegram Bot │
                      │ (Polling)    │
                      │              │
                      │ • Approval   │
                      │ • Reject     │
                      │ • Notify     │
                      └──────────────┘
```

## Component Architecture

### Frontend Layer

**Purpose:** User interface and interaction

**Components:**
- **Pages**: Login, Register, Dashboard, JobDetail, Applications, Preferences
- **Context**: AuthContext for state management
- **Services**: API client with Axios
- **Styles**: Modular CSS files per page

**Key Features:**
- JWT token management in localStorage
- Protected routes with auth guards
- Responsive design
- Real-time form validation

### API Gateway Layer

**Purpose:** Request routing, validation, authentication

**Middleware:**
- CORS handler
- JWT authentication middleware
- Error handler
- Request/response logging

**Routes:**
- `/auth/*` - User authentication
- `/jobs/*` - Job management
- `/applications/*` - Application tracking
- `/preferences/*` - User preferences

### Business Logic Layer

**Purpose:** Core application logic

**Services:**

1. **AuthService**
   - User registration (email, password, profile)
   - User login & session management
   - Preference initialization
   - Dependencies: Password hashing, JWT

2. **JobService**
   - Job CRUD operations
   - Job filtering by preferences
   - Status management
   - Dependencies: MongoDB

3. **ApplicationService**
   - Application lifecycle (pending → approved → applied)
   - Error tracking
   - Status transitions
   - Dependencies: MongoDB

4. **PreferencesService**
   - Preference retrieval & updates
   - Preference validation
   - Dependencies: MongoDB

### Integration Services Layer

**Purpose:** External service communication

**Services:**

1. **GroqService**
   - Job matching algorithm using AI
   - Resume generation with context
   - Cover letter generation
   - Handles API errors gracefully
   - Dependencies: Groq API SDK

2. **TelegramBotService**
   - User notifications
   - Approval request messages
   - Callback handling
   - Message broadcasting
   - Dependencies: Telegram Bot API

### Automation Services Layer

**Purpose:** Browser automation and form filling

**Module:** PlaywrightAutomation
- Browser instance management
- Form field detection
- Typing simulation (anti-bot)
- Resume upload
- Application submission
- Screenshot capture on error
- Session state saving

## Data Flow

### Authentication Flow

```
User Input
    │
    ▼
Frontend (React)
    │ POST /auth/register
    ▼
FastAPI Route Handler
    │ Validate input
    ▼
AuthService.register()
    │ Hash password (bcrypt)
    │ Create user record
    │ Initialize preferences
    ▼
MongoDB
    │
    ▼
Generate JWT Token
    │
    ▼
Return token + user
    │
    ▼
Frontend stores token
```

### Job Matching Flow

```
User clicks "Analyze Match"
    │
    ▼
Frontend (React)
    │ POST /jobs/{id}/match
    ▼
FastAPI Route Handler
    │ Get user from JWT
    │ Get job from DB
    │ Get user preferences
    ▼
GroqService.match_job()
    │ Build prompt with job + preferences
    │ Call Groq API
    │ Parse response JSON
    ▼
Return match result
    │
    ▼
Update job in MongoDB
    │
    ▼
Return to frontend
    │
    ▼
Display match score + analysis
```

### Application Submission Flow

```
User clicks "Submit Application"
    │
    ▼
Frontend creates application
    │ POST /applications/{id}/submit
    ▼
FastAPI creates pending app record
    │
    ▼
TelegramBot sends approval request
    │
    ▼
User receives Telegram message
    │ with Approve/Reject buttons
    ▼
User clicks Approve
    │
    ▼
API receives /applications/{id}/approve
    │
    ▼
PlaywrightAutomation.automate_job_application()
    │ Launch browser
    │ Open job URL
    │ Detect form fields
    │ Fill form with resume & letter
    │ Submit form
    │
    ▼
Update application status → "applied"
    │
    ▼
Send Telegram confirmation
    │
    ▼
Frontend shows in "Applied" tab
```

## Database Schema

### Collections Structure

```javascript
users {
  _id: ObjectId,
  name: String,
  email: String,
  password_hash: String,
  telegram_chat_id: String,
  created_at: DateTime
}

jobs {
  _id: ObjectId,
  user_id: String,
  title: String,
  company: String,
  description: String,
  apply_link: String,
  location: String,
  salary_min: Integer,
  salary_max: Integer,
  job_type: String,
  source: String,
  match_score: Float,
  match_reason: String,
  missing_skills: [String],
  strengths: [String],
  status: String,
  created_at: DateTime
}

applications {
  _id: ObjectId,
  user_id: String,
  job_id: String,
  resume: String,
  cover_letter: String,
  status: String,
  approved_at: DateTime,
  submitted_at: DateTime,
  failed_reason: String,
  created_at: DateTime
}

user_preferences {
  _id: ObjectId,
  user_id: String,
  skills: [String],
  roles: [String],
  experience: String,
  location: [String],
  job_type: [String],
  min_salary: Integer,
  max_salary: Integer
}
```

### Index Strategy

```
users:
  - email (unique)

jobs:
  - user_id (for user-scoped queries)
  - status (for filtering)
  - created_at (for sorting)

applications:
  - user_id (for user-scoped queries)
  - status (for status filtering)
  - job_id (for job lookups)

user_preferences:
  - user_id (unique, 1:1 relationship)
```

## Security Architecture

### Authentication

```
┌─────────────────────────────────────┐
│ User Login with Email + Password    │
└────────────────┬────────────────────┘
                 │
                 ▼
    Compare with bcrypt password hash
                 │
         ┌───────┴────────┐
         │                │
    Match          No Match
     │                │
     ▼                ▼
  Generate      Return 401
  JWT Token
     │
     ▼
  Return token to client
     │
     ▼
  Client stores in localStorage
     │
     ▼
  Attach to all API requests
     │
     ▼
  Server verifies token
  (expiry, signature)
     │
    Valid? → Continue
     │
    Invalid? → Return 401
```

### API Security

1. **JWT Validation**
   - HS256 algorithm
   - 24-hour expiry (configurable)
   - Signature verification

2. **Password Security**
   - bcrypt hashing
   - Salt rounds: 12

3. **Input Validation**
   - Pydantic schemas
   - Type checking
   - Length validation

4. **Rate Limiting**
   - Per-user limits (future)
   - Per-endpoint limits (future)

## Performance Considerations

### Async Operations

- All database calls are non-blocking (Motor)
- API handlers are async
- Groq API calls don't block request

### Connection Pooling

- MongoDB: Motor handles pooling
- Telegram: Connection reuse
- Groq: HTTP connection pooling

### Caching Opportunities

- Cache job match results (24h)
- Cache user preferences in memory
- Client-side localStorage caching

### Pagination

- Jobs endpoint supports skip/limit
- Default 20 items per page
- Prevents large data transfers

## Scalability Strategy

### Current Limitations

- Single MongoDB instance
- No horizontal scaling
- No caching layer
- Blocking Telegram polling

### Scaling Approach

```
Load Balancer (nginx)
    │
    ├─→ API Server 1
    ├─→ API Server 2
    └─→ API Server 3
         │
         └─→ MongoDB Replica Set
              ├─ Primary
              ├─ Secondary 1
              └─ Secondary 2
         │
         └─→ Redis Cache
         │
         └─→ Background Job Queue
              (Celery/RQ)
```

## Error Handling Strategy

### API Errors

```
Exception
  │
  ├─ Validation Error → 400 Bad Request
  ├─ Auth Error → 401 Unauthorized
  ├─ Not Found → 404 Not Found
  ├─ Conflict → 409 Conflict
  └─ Server Error → 500 Internal Error
       │
       → Log error
       → Return generic message
       → Alert administrators
```

### Service Errors

- Groq API errors: Graceful fallback with message
- Telegram errors: Log and continue
- Playwright errors: Capture screenshot, update status
- MongoDB errors: Retry with backoff

## Deployment Architecture

```
┌─────────────────────────────────────┐
│ Client Browser (SPA)                │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────┐      ┌───────────────┐
│   CDN    │      │  API Server   │
│  (S3)    │      │   (Docker)    │
└──────────┘      └───────┬───────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
     ┌─────────┐  ┌────────────┐  ┌──────────────┐
     │ MongoDB │  │ Groq API   │  │ Telegram API │
     │ Cluster │  │ (Cloud)    │  │ (Cloud)      │
     └─────────┘  └────────────┘  └──────────────┘
```

---

**Architecture Version:** 1.0.0  
**Last Updated:** April 2026  
**Designed for:** Production-ready, scalable job application automation
