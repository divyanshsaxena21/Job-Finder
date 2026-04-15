# Troubleshooting Guide - CORS & Deployment Issues

## Issue: CORS Error on Vercel Frontend

### Error Message
```
Access to XMLHttpRequest at 'http://localhost:8000/preferences' from origin 
'https://job-finder-pearl.vercel.app' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Root Cause
- Your frontend is deployed on Vercel (HTTPS)
- Your backend is running locally (HTTP + localhost)
- Vercel can't access `localhost:8000` from the internet
- Mixed HTTP/HTTPS causes security blocking

---

## Solutions

### ✅ Solution 1: Local Development (Easiest for Testing)

Works perfectly for development:

```bash
# Terminal 1: Start Backend
cd backend
python -m app.main
# Backend runs at: http://localhost:8000

# Terminal 2: Start Frontend  
cd frontend
npm run dev
# Frontend runs at: http://localhost:5173
```

No CORS issues because both run on localhost!

---

### ✅ Solution 2: Deploy Backend to Railway (Best for Production)

**Why Railway?**
- ✅ Free tier available
- ✅ Auto-deploys from GitHub
- ✅ HTTPS support
- ✅ Environment variables easy to manage

**Steps:**

1. **Create Railway Account**
   - Visit https://railway.app
   - Click "Start a new project"
   - Select "Deploy from repo"
   - Connect your GitHub repository

2. **Configure Environment Variables in Railway**
   ```
   MONGODB_URL=your_atlas_connection_string
   DB_NAME=job_finder
   JWT_SECRET_KEY=your_secret_key
   JWT_ALGORITHM=HS256
   JWT_EXPIRY_HOURS=24
   GROQ_API_KEY=your_groq_key
   TELEGRAM_BOT_TOKEN=your_telegram_key
   BACKEND_URL=https://your-app.up.railway.app
   FRONTEND_URL=https://job-finder-pearl.vercel.app
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://job-finder-pearl.vercel.app,https://*.vercel.app
   ENVIRONMENT=production
   DAILY_APPLICATION_LIMIT=5
   ```

3. **Get Your Backend URL**
   - Railway assigns you a domain like: `https://your-app.up.railway.app`
   - Note this URL

4. **Update Vercel Frontend**
   - Go to https://vercel.com/dashboard
   - Click your Job Finder project
   - Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-app.up.railway.app`
   - Click "Save"
   - Vercel auto-redeploys

5. **Test**
   - Go to https://job-finder-pearl.vercel.app
   - CORS error should be gone! ✅

---

### ✅ Solution 3: Use ngrok for Quick Testing

Good for testing production-like setup locally:

```bash
# Install ngrok
# Windows (PowerShell): choco install ngrok
# macOS: brew install ngrok
# Or download from: https://ngrok.com/download

# Terminal 1: Start backend
cd backend
python -m app.main

# Terminal 2: Expose backend with ngrok
ngrok http 8000
# Shows: https://xxxx-xxxx-ngrok.io

# Terminal 3: Start frontend in dev mode
cd frontend
VITE_API_URL=https://xxxx-xxxx-ngrok.io npm run dev
```

---

## Quick Reference

### For Local Development
```
Frontend: http://localhost:5173
Backend: http://localhost:8000
No CORS issues ✅
```

### For Vercel Deployment
```
Frontend: https://job-finder-pearl.vercel.app
Backend: https://your-deployed-backend.com
Requires: VITE_API_URL environment variable to point to backend
```

### For Production Checklist
- [ ] Backend deployed (Railway, Render, Heroku, etc.)
- [ ] Backend domain noted (e.g., https://your-app.up.railway.app)
- [ ] Vercel VITE_API_URL updated to backend URL
- [ ] Environment variables set on deployed platform
- [ ] CORS_ORIGINS includes Vercel domain
- [ ] Test API calls from Vercel frontend

---

## Environment Variable Reference

### Backend (.env)
```bash
# Required
MONGODB_URL=mongodb+srv://...
JWT_SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-key

# Optional (with defaults)
DB_NAME=job_finder
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ENVIRONMENT=development
DAILY_APPLICATION_LIMIT=5
```

### Frontend (.env.local)
```bash
# For local development
VITE_API_URL=http://localhost:8000

# For Vercel deployment (set in Vercel UI)
VITE_API_URL=https://your-backend-domain.com
```

---

## Still Having Issues?

**Check:**
1. Backend is running: Try http://localhost:8000/health
2. Correct API URL in Vercel environment variables
3. Backend CORS includes your Vercel domain
4. No typos in API URL (http vs https, trailing slashes, etc.)
5. Browser cache cleared

**Debug:**
- Open browser DevTools (F12)
- Go to Network tab
- Look for the failed request
- Check the error message and response headers
