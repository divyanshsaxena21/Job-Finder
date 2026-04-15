# Job Finder - Deployment Guide

## Frontend Deployment (Vercel) ✅
Your frontend is correctly deployed at: `https://job-finder-pearl.vercel.app`

## Backend Deployment Issue

### The Problem
The frontend on Vercel is trying to access `http://localhost:8000`, but:
- Vercel can't access your local machine
- You can't use HTTP when the frontend uses HTTPS (mixed content)

### Solution 1: Deploy Backend to Railway (Recommended)

**Step 1: Sign up on Railway**
1. Go to https://railway.app
2. Sign up with GitHub
3. Create a new project

**Step 2: Connect Your Repository**
```bash
# Your Git repository should be connected to Railway
# Railway auto-detects Python projects
```

**Step 3: Add Environment Variables in Railway**
Go to Variables section and add:
```
MONGODB_URL=your_mongodb_connection_string
DB_NAME=job_finder
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
GROQ_API_KEY=your_groq_api_key
TELEGRAM_BOT_TOKEN=your_telegram_token
BACKEND_URL=https://your-railway-domain.up.railway.app
FRONTEND_URL=https://job-finder-pearl.vercel.app
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://job-finder-pearl.vercel.app
ENVIRONMENT=production
DAILY_APPLICATION_LIMIT=5
```

**Step 4: Update Vercel Frontend Environment**
1. Go to your Vercel project settings
2. Go to Environment Variables
3. Add: `VITE_API_URL=https://your-railway-domain.up.railway.app`
4. Redeploy

---

### Solution 2: Use ngrok for Local Testing

If you want to test with your local backend:

**Step 1: Install ngrok**
```bash
# macOS
brew install ngrok

# Windows (PowerShell)
choco install ngrok
# Or download from https://ngrok.com/download
```

**Step 2: Expose your backend**
```bash
# Terminal 1: Run your backend
cd backend
python -m app.main

# Terminal 2: Expose it with ngrok
ngrok http 8000
# This gives you a URL like: https://xxxx-xxx-xxx-xxx.ngrok.io
```

**Step 3: Update Vercel Environment**
1. Add to Vercel: `VITE_API_URL=https://xxxx-xxx-xxx-xxx.ngrok.io`
2. Redeploy or test locally

---

### Solution 3: Local Development

For local testing, everything works fine:
```bash
# Terminal 1: Backend
cd backend
python -m app.main

# Terminal 2: Frontend
cd frontend
npm run dev
# Access at http://localhost:5173
```

---

## Backend Deployment Checklist

- [ ] Database: MongoDB Atlas connection string configured
- [ ] Environment variables: All set in deployment platform
- [ ] CORS: Includes your Vercel domain `https://job-finder-pearl.vercel.app`
- [ ] Groq API: Key configured for AI cover letters
- [ ] Port: Backend running on accessible port (auto-assigned by platform)

## Current Status

| Component | Status | URL |
|-----------|--------|-----|
| Frontend | ✅ Deployed | https://job-finder-pearl.vercel.app |
| Backend | ⚠️ Local only | http://localhost:8000 (not accessible from Vercel) |
| Database | ✅ MongoDB Atlas | Connected |

## Next Steps

1. Choose a backend deployment platform (Railway, Render, Heroku, etc.)
2. Deploy backend with environment variables
3. Update `VITE_API_URL` in Vercel
4. Test API connectivity from frontend

## Quick Links

- **Vercel Projects**: https://vercel.com/dashboard
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Heroku**: https://heroku.com
- **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas
- **Groq Console**: https://console.groq.com

---

For local development: Run both backend and frontend on localhost - no deployment needed!
