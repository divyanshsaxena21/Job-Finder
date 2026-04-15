# Phase 7 Deployment Guide

Complete guide to deploying Job Finder with all Phase 7 features enabled.

## Prerequisites

### System Requirements
- Python 3.9+
- Node.js 16+ (for frontend)
- MongoDB Atlas account
- 2GB+ RAM available

### Required API Keys
1. **Groq API Key** (Free tier)
   - Get from: https://console.groq.com
   - Free tier: 30 requests/minute, unlimited monthly

### Optional Services
- Render (Backend Hosting)
- Vercel (Frontend Hosting)
- Sentry (Error Monitoring)

## Step 1: Install Dependencies

### Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not exists)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all packages
pip install -r requirements.txt

# Verify new packages installed
pip list | grep -E "groq|playwright|beautifulsoup4"

# Download Playwright browsers
playwright install  # This downloads Chromium, Firefox, WebKit (~600MB)
```

### Frontend Dependencies

```bash
# Navigate to frontend directory
cd ../frontend

# Install packages
npm install

# Verify Vite installation
npm list vite
```

## Step 2: Configuration

### Backend Environment Setup

Create or update `.env` file in `backend/` directory:

```bash
# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/job-finder?retryWrites=true&w=majority
MONGO_DB_NAME=job-finder

# Groq AI
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxx

# JWT
JWT_SECRET=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION=7

# App
DEBUG=false
LOG_LEVEL=INFO
APP_NAME=Job Finder
ENVIRONMENT=production

# CORS (for frontend)
FRONTEND_URL=https://yourfrontend.vercel.app
BACKEND_URL=https://yourbackend.onrender.com

# Auto-Apply Scheduler
SCHEDULER_TIMEZONE=UTC
AUTO_APPLY_ENABLED=true
AUTO_APPLY_CHECK_INTERVAL=3600  # Check every hour

# Optional: Proxy/Rate Limiting
USE_PROXY_ROTATION=false
MAX_CONNECTIONS_PER_MINUTE=30  # For Groq API
```

### Frontend Environment Setup

Create or update `.env.production` in `frontend/` directory:

```bash
VITE_API_URL=https://yourbackend.onrender.com
VITE_APP_NAME=Job Finder
VITE_API_TIMEOUT=30000
```

### Database Configuration

MongoDB collections should be automatically created with proper indexes:

```javascript
// Run in MongoDB Atlas console if needed
db.createCollection("auto_apply_runs");
db.auto_apply_runs.createIndex({ "user_id": 1, "started_at": -1 });

db.createCollection("applications");
db.applications.createIndex({ "user_id": 1, "created_at": -1 });

db.createCollection("jobs");
db.jobs.createIndex({ "apply_link": 1 });

db.createCollection("user_preferences");
db.user_preferences.createIndex({ "user_id": 1 }, { "unique": true });
```

## Step 3: Test Installation

### Test Backend Services

```bash
cd backend

# Test Quality Scorer
python -c "from app.services.quality_scorer import JobQualityScorer; print('✓ Quality Scorer loaded')"

# Test Form Submission
python -c "from app.services.form_submission import FormSubmissionService; print('✓ Form Submission loaded')"

# Test Groq Integration
python -c "
import os
os.environ['GROQ_API_KEY'] = 'test'
from app.services.resume_customizer import ResumeCustomizerService
print('✓ Groq Integration loaded')
"

# Test Job Scraper (new sources)
python -c "
from app.services.job_scraper import JobScraperService
import inspect
source = inspect.getsource(JobScraperService.scrape_jobs)
assert 'scrape_stack_overflow' in source
assert 'scrape_dice' in source
print('✓ New job portals integrated')
"

# Test full import
python -c "
from app.services.auto_apply import AutoApplyOrchestrator
print('✓ All services integrated in orchestrator')
"
```

### Run Test Suite

```bash
cd backend

# Run Phase 7 feature tests
python test_phase7_features.py

# Expected output:
# ✅ TEST SUITE COMPLETED
# ✓ Quality Scorer: Working
# ✓ Groq Integration: Configured
# ✓ Form Submission: Ready
# ✓ Additional Portals: Implemented
# ✓ Orchestrator: Integrated
```

## Step 4: Start Backend

```bash
cd backend

# Development mode (with logs)
python -m app.main

# You should see:
# INFO:app.main:🚀 Starting Job Finder API...
# ✓ Connected to MongoDB
# INFO:app.scheduler:Scheduler initialized with auto-apply job (daily at 9 AM)
# INFO:apscheduler.scheduler:Scheduler started
# INFO:app.main:✓ Scheduler initialized successfully
# INFO:     Application startup complete.
# INFO:uvicorn.server:Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Start Frontend

```bash
cd frontend

# Development mode
npm run dev

# Expected output:
# VITE v4.x.x
# ➜  Local:   http://localhost:5173/
# ➜  press h to show help
```

## Step 6: Test Complete Workflow

### Test Account Setup

1. Navigate to http://localhost:5173
2. Sign up with test account
3. Go to Settings and fill in:
   - Name: "Test User"
   - Email: "test@example.com"
   - Phone: "123-456-7890"
   - Skills: "Python, JavaScript, FastAPI"
   - Location: "New York"
   - Job Types: "Full-time, Contract"
   - Roles: "Software Engineer, Backend Developer"

### Test Auto-Apply Trigger

```bash
# Trigger via API (requires auth token)
curl -X POST http://localhost:8000/auto-apply/trigger \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Or use frontend dashboard:
# Dashboard → Auto-Apply Settings → Manual Trigger button
```

### Verify Results

Check dashboard for:
- **Jobs Found**: Should show 50-120 unique jobs
- **Jobs Applied**: Depends on match score and quality
- **Quality Scores**: Each job should have score 0-100
- **Errors**: Any CAPTCHA blocks or form submission errors
- **History**: Run should appear in history timeline

## Step 7: Production Deployment

### Deploy Backend to Render

```bash
# 1. Create new Render.com Web Service
# 2. Connect GitHub repository
# 3. Set environment variables (from .env):
#    - MONGO_URI
#    - GROQ_API_KEY
#    - JWT_SECRET
#    - FRONTEND_URL (pointing to Vercel)
# 4. Set build command: pip install -r requirements.txt && playwright install
# 5. Set start command: gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
# 6. Deploy (auto-redeploy on push)
```

### Deploy Frontend to Vercel

```bash
# 1. Create new Vercel project from GitHub
# 2. Set framework: Vite
# 3. Build command: npm run build
# 4. Install command: npm install
# 5. Environment variables:
#    - VITE_API_URL=https://yourbackend.onrender.com
# 6. Deploy (auto-redeploy on push)
```

### Production Checklist

- [ ] All dependencies installed
- [ ] GROQ_API_KEY configured
- [ ] Playwright browsers cached/available
- [ ] MongoDB credentials secure
- [ ] CORS configured properly
- [ ] Rate limiting in place
- [ ] Error monitoring (Sentry) configured
- [ ] HTTPS enabled
- [ ] Database backups scheduled
- [ ] Logs monitored
- [ ] Uptime monitoring configured

## Step 8: Monitoring & Maintenance

### Monitor Auto-Apply Runs

```python
# Check backend logs
# Render: View logs in Render dashboard

# View database
# MongoDB: Check collections in Atlas
# - auto_apply_runs collection for run history
# - applications collection for submitted applications
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| GROQ_API_KEY not working | Verify key at https://console.groq.com |
| Playwright timeout | Increase timeout in env, check network |
| MongoDB connection fails | Verify IP whitelist in MongoDB Atlas |
| Form submission fails | Check if site HTML changed, update selectors |
| CAPTCHA blocks submission | Normal - waits for manual solve (5 min timeout) |
| Rate limiting (429 error) | Reduce submission speed or add proxy rotation |

### Update Procedures

When updating to new version:

```bash
# Backend
cd backend
git pull
pip install -r requirements.txt  # In case dependencies changed
playwright install --with-deps    # Update Playwright if needed
python -m app.main               # Start

# Frontend
cd frontend
git pull
npm install
npm run build
```

## Performance Tuning

### Optimize Job Scraping

Default behavior:
- Scrape 6 sources in parallel
- Max 10 jobs per source (60 total)
- Takes ~20 seconds

To make faster:
```python
# In scrape_jobs():
# Reduce max_results
scrape_jobs(max_results=30)  # Instead of 60
# Takes ~10 seconds instead
```

### Optimize Form Submission

Default behavior:
- Sequential submission (one at a time)
- 12 seconds per application
- 10 applications = 120 seconds total

To make faster:
```python
# Could parallelize but NOT RECOMMENDED
# It would increase blocking/CAPTCHA risk
# Better: Submit fewer applications per run
preferences.max_daily_applications = 5  # Instead of 10
```

### Optimize Cover Letter Generation

Default behavior:
- Groq API: 2-5 seconds per letter
- Generate only for >40% match

To skip cover letters:
```python
# Option 1: Disable in preferences
# Option 2: Use template letter (modify auto_apply.py)
```

## Troubleshooting Guide

### Application Form Not Found

```python
# Update selectors in form_submission.py
# 1. Check site's current HTML with Chrome DevTools
# 2. Find correct button/form selectors
# 3. Update in _submit_indeed(), _submit_naukri(), etc.
# 4. Test with debug screenshots
```

### Low Application Success Rate

```python
# Check dashboard statistics:
# - High quality_skips = increase min_quality threshold
# - High skill_mismatch = add more skills to profile
# - High CAPTCHA blocks = use proxy rotation
# - High form_errors = update form selectors
```

### MongoDB Connection Issues

```python
# 1. Get connection string from MongoDB Atlas
# 2. Verify IP whitelist includes your server
# 3. Check credentials are correct
# 4. Test connection:
import pymongo
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
client.admin.command('ping')  # Should succeed
```

### Groq API Rate Limited

```python
# If getting 429 (rate limit) errors:
# Free tier: 30 requests/minute
# Solution 1: Reduce applications per run
# Solution 2: Upgrade Groq plan (paid)
# Solution 3: Add request queueing/backoff
```

## Support & Documentation

### Key Documentation Files

1. **FORM_SUBMISSION_SERVICE.md** - Form automation details
2. **GROQ_COVER_LETTERS.md** - Cover letter setup
3. **ADVANCED_FEATURES.md** - Quality scoring, portals
4. **PHASE_7_SUMMARY.md** - Complete feature summary
5. **test_phase7_features.py** - Test suite

### Getting Help

1. Check documentation files
2. Review inline code comments
3. Enable debug logging: `LOG_LEVEL=DEBUG`
4. Check application logs
5. Review test cases for examples

## Rollback Plan

If something breaks in production:

```bash
# 1. Rollback to previous version on Render
# 2. Check error logs
# 3. Fix locally
# 4. Test thoroughly
# 5. Re-deploy when ready

# Or disable specific features:
# In auto_apply.py:
# - Comment out form submission to fall back to database save
# - Disable Groq to use template letters
# - Disable quality scoring to allow all jobs
```

## Version Info

- **Release**: Phase 7 Complete
- **Date**: 2024
- **Components**:
  - Form Submission Service (300 lines)
  - Groq AI Integration (60 lines)
  - Quality Scorer (300 lines)
  - Additional Job Portals (Stack Overflow, Dice)
  - CAPTCHA Detection
- **Status**: ✅ Production Ready

---

**Deployment Status**: Ready for production

**Next Steps**:
1. Follow steps 1-6 for local testing
2. Verify all tests pass
3. Deploy to staging first
4. Run 24-hour stability test
5. Monitor for errors
6. Deploy to production
7. Set up monitoring/alerts

**Expected Timeline**: 2-3 hours from start to production
