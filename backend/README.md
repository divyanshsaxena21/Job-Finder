# Backend Setup & Deployment Guide

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your editor
```

Required environment variables:
```env
MONGODB_URL=<your_mongodb_connection_string>
GROQ_API_KEY=<your_groq_api_key>
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
JWT_SECRET_KEY=<your_secret_key>
```

### 3. Start Server

```bash
# Development
python -m app.main

# Or with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

## Architecture

### Project Structure

```
app/
├── main.py              # FastAPI app & lifecycle
├── config.py            # Settings from env
├── api/                 # Route handlers
│   ├── auth.py
│   ├── jobs.py
│   ├── applications.py
│   └── preferences.py
├── models/              # Data models
│   ├── schemas.py       # Pydantic schemas
│   └── database.py      # MongoDB setup
├── services/            # Business logic
│   ├── auth_service.py
│   ├── job_service.py
│   └── application_service.py
├── integrations/        # External services
│   ├── groq_service.py
│   └── telegram_bot.py
├── automation/          # Playwright scripts
│   └── playwright_automation.py
└── utils/              # Helpers
    ├── auth.py         # JWT, password hashing
    └── dependencies.py # Auth middleware
```

### Core Services

#### AuthService
- User registration & login
- Password hashing with bcrypt
- Preference initialization

#### JobService
- CRUD operations for jobs
- Job filtering by preferences
- Job status management

#### GroqService
- Job matching with AI
- Resume generation
- Cover letter generation

#### ApplicationService
- Application lifecycle management
- Status transitions (pending → approved → applied)
- Error tracking

#### TelegramBot
- Send approval requests
- Handle user responses
- Send notifications

#### PlaywrightAutomation
- Open job application pages
- Detect form fields
- Fill forms with typing simulation
- Upload resume
- Submit applications

## Database Setup

### MongoDB Atlas (Cloud)

1. Create account at [mongodb.com](https://www.mongodb.com)
2. Create a cluster
3. Create a database user
4. Get connection string
5. Add IP to whitelist
6. Set `MONGODB_URL` in `.env`

### Local MongoDB

```bash
# Install MongoDB
# macOS:
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Connection string:
MONGODB_URL=mongodb://localhost:27017
```

### Verify Connection

```python
from app.models.database import MongoDB
from app.config import settings

# Test in Python shell
import asyncio
asyncio.run(MongoDB.connect_db(settings.mongodb_url, settings.db_name))
# Should print: ✓ Connected to MongoDB
```

## API Integration

### Groq API Setup

1. Get API key from [console.groq.com](https://console.groq.com)
2. Set `GROQ_API_KEY` in `.env`
3. Available models:
   - `mixtral-8x7b-32768` (fast, accurate)
   - `llama2-70b-4096` (larger)

### Telegram Bot Setup

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get token and update `.env`
3. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
4. Start bot for polling:

```python
from app.integrations.telegram_bot import telegram_bot

# In async context
await telegram_bot.send_approval_request(
    chat_id="your_chat_id",
    job_title="Software Engineer",
    company="Tech Co",
    match_score=85.5,
    app_id="app_uuid"
)
```

## Testing

### Manual Testing with curl

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"pass123"}'

# Get current user (with token)
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Add job
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Backend Developer",
    "company":"Tech Co",
    "description":"Job description...",
    "apply_link":"https://job.example.com",
    "location":"Remote"
  }'
```

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Login and copy token
4. Paste in auth field
5. Test all endpoints

## Performance Optimization

### Database Indexes
Automatically created on startup:
- `users.email` (unique)
- `jobs.user_id`
- `jobs.created_at`
- `applications.user_id`
- `applications.status`
- `user_preferences.user_id` (unique)

### Async Operations
- All database operations are non-blocking
- Jobs fetched with pagination (default 20)
- API responders stream large responses

### Caching Opportunities
- Cache job matches for 24 hours
- Cache generated documents
- Cache user preferences

## Deployment

### Production Checklist

```bash
# 1. Update environment
ENVIRONMENT=production
JWT_SECRET_KEY=<generate_strong_key>

# 2. Use production database
MONGODB_URL=<production_cluster_url>

# 3. Update CORS origins
# In main.py, restrict to your frontend domain

# 4. Use production ASGI server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# 5. Set up reverse proxy (nginx)
# 6. Enable HTTPS/SSL
# 7. Set up monitoring
# 8. Configure logging
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t job-finder-api .
docker run -p 8000:8000 --env-file .env job-finder-api
```

## Monitoring & Logging

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Key Events to Monitor
- User registration/login failures
- Job matching errors
- Groq API errors
- Telegram delivery failures
- Playwright automation failures
- Database connection issues

## Common Issues

### 1. MongoDB Connection Timeout
```bash
# Check MongoDB is running
# Verify connection string
# Check firewall rules
```

### 2. Groq API Rate Limit
```bash
# Implement backoff strategy
# Cache responses
# Use smaller prompts
```

### 3. Playwright Headless Browser Fails
```bash
# Install browsers:
playwright install

# Check disk space
# Increase timeouts
```

### 4. JWT Token Expired
```python
# Token expires after JWT_EXPIRY_HOURS
# Client must capture refresh token mechanism
# Implement token refresh endpoint
```

## Scaling Tips

1. **Database**: Add read replicas for scaling reads
2. **Caching**: Use Redis for job match cache
3. **Queue**: Add Celery/RQ for async tasks
4. **Load Balancer**: Use behind load balancer
5. **CDN**: Serve static assets from CDN
6. **API Rate Limiting**: Implement rate limiter

## Security Hardening

1. Change default JWT secret
2. Use strong MongoDB password
3. Restrict CORS origins
4. Enable HTTPS in production
5. Use environment secrets manager
6. Rotate API keys regularly
7. Enable database encryption
8. Add request logging
9. Implement rate limiting
10. Add input validation

---

For detailed API documentation, visit: `/docs` after starting the server
