# Comprehensive Setup Guide

## Complete Installation from Scratch

This guide walks you through setting up and running the Job Finder application end-to-end.

---

## 🔒 Environment Variables Overview

**All sensitive data (API keys, database URLs, secrets) are stored in `.env` files.**

- **Backend:** `backend/.env` (not committed to git)
- **Frontend:** `frontend/.env` (not committed to git)
- **Examples:** `.env.example` files provided for reference

For detailed information on each environment variable:
👉 **See [.env.GUIDE.md](.env.GUIDE.md)** for complete documentation on:
- Where to get each API key
- How to generate secrets
- Production vs. development configuration
- Security best practices

Quick reference:
- `backend/.env.example` - Backend environment template
- `frontend/.env.example` - Frontend environment template
- `.env.local.example` - Local development config
- `.env.production.example` - Production deployment examples

---

## Prerequisites

Before starting, ensure you have:

1. **Python 3.9+**
   ```bash
   python --version
   ```

2. **Node.js 16+**
   ```bash
   node --version
   npm --version
   ```

3. **MongoDB**
   - Cloud: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (free tier available)
   - Or local: [MongoDB Community Edition](https://www.mongodb.com/try/download/community)

4. **Groq API Key**
   - Sign up at [console.groq.com](https://console.groq.com)
   - Create API key

5. **Telegram Bot Token**
   - Chat with [@BotFather](https://t.me/botfather) on Telegram
   - Create bot and copy token

---

## Step 1: Backend Setup

### 1.1 Navigate to Backend Directory

```bash
cd backend
```

### 1.2 Create Virtual Environment

```bash
# macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# Windows PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows Command Prompt:
python -m venv venv
venv\Scripts\activate.bat
```

You should see `(venv)` prefix in terminal.

### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

This takes 2-3 minutes. If you see errors:
- Ensure Python version is 3.9+
- Try: `pip install --upgrade pip`
- Try: `pip install -r requirements.txt --user`

### 1.4 Setup Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit the .env file
```

**For MongoDB:**

**Option A: Use MongoDB Atlas (Cloud)**
```
1. Go to mongodb.com/cloud/atlas
2. Create free account
3. Create cluster (M0 free tier)
4. Click "Connect" → "Drivers"
5. Copy connection string
6. Replace <username>, <password>, <cluster>
7. Paste into MONGODB_URL
```

**Option B: Use Local MongoDB**
```
MONGODB_URL=mongodb://localhost:27017
```

**For Groq API:**
```
1. Go to console.groq.com
2. Sign in / Create account
3. Copy API key from dashboard
4. Paste into GROQ_API_KEY
```

**For Telegram Bot:**
```
1. Open Telegram, search for @BotFather
2. Send /start, then /newbot
3. Follow prompts (give bot a name)
4. Copy token and paste into TELEGRAM_BOT_TOKEN
5. To get YOUR chat ID:
   - Search @userinfobot on Telegram
   - Start chat, it shows your ID
   - You'll use this later
```

**Other Variables:**
```env
JWT_SECRET_KEY=super_secret_key_change_this_in_production
# Generate one: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 1.5 Test Backend

```bash
# Start the server
python -m app.main

# Or with auto-reload:
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✓ Connected to MongoDB
```

**Test connection:**
```bash
# In another terminal
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","version":"1.0.0"}
```

✅ **Backend is running!**

---

## Step 2: Frontend Setup

### 2.1 Navigate to Frontend Directory

```bash
# From project root
cd frontend
```

### 2.2 Install Dependencies

```bash
npm install
```

This takes 1-2 minutes and downloads ~300MB.

### 2.3 Configure Environment (Optional)

Most config is automatic, but you can create `.env` if needed:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Job Finder
```

### 2.4 Start Development Server

```bash
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

✅ **Frontend is running!**

---

## Step 3: Testing the Full Application

### 3.1 Open Application

1. Open browser to: **http://localhost:5173**
2. You should see the **Login** page

### 3.2 Create Account

1. Click **"Don't have an account? Register"**
2. Fill in:
   - **Name**: Your Full Name
   - **Email**: your@email.com
   - **Password**: Strong password
   - **Telegram Chat ID** (optional): Leave blank for now
3. Click **Register**
4. You're logged in and redirected to **Dashboard**

### 3.3 Update Preferences

1. Click **Preferences** in top menu
2. Add your:
   - **Skills**: React, Python, JavaScript
   - **Target Roles**: Software Engineer, Full Stack Developer
   - **Experience**: Mid-level
   - **Locations**: Remote, New York
   - **Job Types**: Full Time
3. Click **Save Preferences**

### 3.4 Add a Sample Job

1. Click **Dashboard**
2. Click **Add Job Manually**
3. Fill in:
   ```
   Title: Python Backend Developer
   Company: Tech Startup
   Description: We're looking for an experienced Python developer...
   Apply Link: https://example.com/job/python-dev
   Location: Remote
   ```
4. Click **Create Job**

### 3.5 Test Job Matching

1. From Dashboard, click **View Details** on the job
2. Click **Analyze Match**
3. Wait for AI analysis (uses Groq API)
4. See match score and analysis

### 3.6 Generate Resume & Cover Letter

1. Still on Job Detail page
2. Click **Generate Resume**
3. Wait for generation
4. Click **Generate Cover Letter**
5. Wait for generation
6. Review generated content
7. (Optional) Edit content in textareas

### 3.7 Test Application Submission

1. Click **Submit Application**
2. Application is created as "Pending"
3. Go to **Applications** page
4. You should see it listed as "Pending Approval"

---

## Step 4: Add Telegram Integration (Optional)

### 4.1 Get Your Telegram Chat ID

1. Open Telegram
2. Search for **@userinfobot**
3. Start conversation
4. Bot shows your **Chat ID** (large number)

### 4.2 Update Your Profile

1. Click the **user menu** (top right of Dashboard)
2. Click **Settings** (or go to Preferences)
3. Find **Telegram Chat ID** field
4. Paste your Chat ID from step 4.1
5. Save

### 4.3 Test Telegram Notifications

1. Create another application
2. In the bot's Python code, add your chat ID:
   ```python
   await telegram_bot.send_approval_request(
       chat_id="YOUR_CHAT_ID",
       job_title="Test Job",
       company="Test Company",
       match_score=85,
       app_id="test_app_id"
   )
   ```
3. Run this code
4. Check Telegram - you should receive a message with Approve/Reject buttons

---

## Common Issues & Solutions

### Backend Issues

**❌ "ModuleNotFoundError: No module named 'fastapi'"**
```bash
# Solution: Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**❌ "MongoDB connection refused"**
```bash
# Solution: Start MongoDB or check connection string
# Local: brew services start mongodb-community
# Cloud: Check MongoDB Atlas IP whitelist
# Update MONGODB_URL in .env
```

**❌ "Groq API Error: Invalid API Key"**
```bash
# Solution: Check API key is correct
# Get from console.groq.com
# Ensure no extra spaces in .env
```

**❌ "Port 8000 already in use"**
```bash
# Solution: Use different port
uvicorn app.main:app --port 8001
```

### Frontend Issues

**❌ "npm: command not found"**
```bash
# Solution: Install Node.js from nodejs.org
# Verify: node --version && npm --version
```

**❌ "Port 5173 already in use"**
```bash
# Solution: Use different port
npm run dev -- --port 5174
```

**❌ "Cannot find module 'axios'"**
```bash
# Solution: Install dependencies
npm install
```

**❌ "API request fails / CORS error"**
```bash
# Solution 1: Ensure backend is running
# Solution 2: Check VITE_API_URL in .env
# Solution 3: Check backend CORS configuration
```

---

## Verification Checklist

Before considering setup complete:

- [ ] Backend runs without errors
- [ ] Frontend loads without errors
- [ ] Can register new account
- [ ] Can login successfully
- [ ] Can add preferences
- [ ] Can add job manually
- [ ] Can analyze job match (may take ~10 seconds)
- [ ] Can generate resume
- [ ] Can generate cover letter
- [ ] Can submit application
- [ ] Can view applications list

---

## Next Steps

### 1. **Integrate Real Job Sources**
Add scrapers for Indeed, LinkedIn, etc.

### 2. **Setup Playwright Automation**
Install Playwright browsers:
```bash
playwright install
```

### 3. **Deploy to Production**
- Backend: Render, Heroku, AWS, DigitalOcean
- Frontend: Vercel, Netlify, AWS S3 + CloudFront

### 4. **Enable Advanced Features**
- API rate limiting
- Email notifications
- Job scheduling
- Application analytics

---

## Getting Help

1. **Check Error Logs**
   - Backend: Terminal output
   - Frontend: Browser console (F12)
   - Network tab: See API responses

2. **Verify Configuration**
   - Backend: Check .env file
   - Frontend: Check .env and API URL
   - MongoDB: Test connection string

3. **Read Documentation**
   - Backend: `backend/README.md`
   - Frontend: `frontend/README.md`
   - Main: `README.md`

4. **Common Commands**
   ```bash
   # View logs
   tail -f ~/.local/share/MongoDB/data/server.log
   
   # Get MongoDB URI
   cat backend/.env | grep MONGODB_URL
   
   # Test API
   curl http://localhost:8000/health
   ```

---

## File Structure Reference

```
Job-Finder/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # Start here
│   │   ├── config.py
│   │   ├── api/
│   │   └── services/
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Copy → .env
│   └── README.md
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── main.jsx           # Start here
│   │   ├── App.jsx
│   │   └── pages/
│   ├── package.json           # Node dependencies
│   ├── vite.config.js
│   └── README.md
│
└── README.md                  # Main documentation
```

---

**🎉 You're all set! Start building your job application automation!**
