# Render + Vercel Deployment Checklist

## ✅ Before Deployment

### Backend Preparation
- [ ] All sensitive keys in `.env` (not in code)
- [ ] `requirements.txt` includes all dependencies:
  - fastapi
  - uvicorn
  - motor
  - mongoengine
  - pydantic
  - pydantic-settings
  - python-jose
  - python-dotenv
  - aiofiles
  - playwright
  - beautifulsoup4
  - requests
  - groq
  - apscheduler

### Frontend Preparation
- [ ] Built frontend: `npm run build`
- [ ] No hardcoded localhost URLs
- [ ] Uses `VITE_API_URL` from environment variable
- [ ] Git changes committed and pushed

---

## 🚀 Step 1: Deploy Backend to Render

### Create Backend Service
- [ ] Go to https://render.com
- [ ] Sign in with GitHub
- [ ] Click "New +" → "Web Service"
- [ ] Select your Job-Finder repository
- [ ] Name it: `job-finder-backend` (or similar)

### Configure Build & Start Commands
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Select Python 3 environment

### Add Environment Variables
In Render dashboard, add:
```
MONGODB_URL=xxx
DB_NAME=job_finder
JWT_SECRET_KEY=xxx (min 32 chars, random)
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
GROQ_API_KEY=xxx (from console.groq.com)
TELEGRAM_BOT_TOKEN=xxx
BACKEND_URL=https://job-finder-backend.onrender.com
FRONTEND_URL=https://job-finder-pearl.vercel.app
CORS_ORIGINS=https://job-finder-pearl.vercel.app,https://*.vercel.app
ENVIRONMENT=production
DAILY_APPLICATION_LIMIT=5
```

- [ ] Click "Create Web Service"
- [ ] Wait for deployment (3-5 minutes)
- [ ] Copy your backend URL from dashboard

---

## 🌐 Step 2: Update Vercel Frontend

### Set Environment Variable
- [ ] Go to https://vercel.com/dashboard
- [ ] Click your Job Finder project
- [ ] Settings → Environment Variables
- [ ] Add variable:
  - **Name**: `VITE_API_URL`
  - **Value**: `https://job-finder-backend.onrender.com` (your Render URL)
- [ ] Click "Save"
- [ ] Vercel auto-redeploys

### Verify Deployment
- [ ] Wait 2-3 minutes for redeploy
- [ ] Visit https://job-finder-pearl.vercel.app
- [ ] Open DevTools (F12)
- [ ] Try to register/login
- [ ] Check Network tab - should be 200 responses, no CORS errors

---

## ✅ Verification Tests

### Test Backend Health
- [ ] Visit: https://job-finder-backend.onrender.com/health
- [ ] Should see: `{"status": "healthy", "version": "1.0.0"}`

### Test API Documentation
- [ ] Visit: https://job-finder-backend.onrender.com/docs
- [ ] Should see Swagger UI with all endpoints

### Test Frontend
- [ ] Visit: https://job-finder-pearl.vercel.app
- [ ] Register new account
- [ ] Login
- [ ] Navigate to Dashboard
- [ ] Check if jobs load (may be empty initially)
- [ ] Try Auto-Apply page
- [ ] No CORS errors in console ✅

### Test API Calls
In browser DevTools console:
```javascript
// Should work without CORS error
fetch('https://job-finder-backend.onrender.com/preferences', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(r => r.json())
.then(data => console.log('Success!', data))
.catch(e => console.error('Error:', e))
```

---

## 📋 Environment Variables Checklist

### Render (Backend) - MUST HAVE
- [ ] MONGODB_URL - MongoDB Atlas connection string
- [ ] JWT_SECRET_KEY - Generate random 32+ char string
- [ ] GROQ_API_KEY - From https://console.groq.com
- [ ] TELEGRAM_BOT_TOKEN - From @BotFather on Telegram (optional but recommended)
- [ ] BACKEND_URL - Your Render URL
- [ ] FRONTEND_URL - https://job-finder-pearl.vercel.app
- [ ] CORS_ORIGINS - Must include your Vercel domain
- [ ] ENVIRONMENT - Set to `production`

### Vercel (Frontend) - MUST HAVE
- [ ] VITE_API_URL - Your Render backend URL (e.g., https://job-finder-backend.onrender.com)

---

## 🔧 Troubleshooting During Deployment

### Backend won't deploy
1. Check Render logs for errors
2. Verify `requirements.txt` has all dependencies
3. Check environment variables are all set
4. Verify MongoDB connection string is correct

### CORS error persists
1. Clear browser cache (Ctrl+Shift+Delete)
2. Verify `VITE_API_URL` is set in Vercel
3. Check Render `CORS_ORIGINS` includes Vercel domain
4. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

### Login fails
1. Check Render backend logs
2. Verify JWT_SECRET_KEY is set
3. Try registering a new account
4. Check MongoDB connection in Render logs

### API endpoints return 404
1. Verify Render deployment completed
2. Check backend URL is correct in Vercel
3. Wait 30 seconds (Render cold start)
4. Try health check endpoint

---

## 📊 Expected URLs After Deployment

```
Frontend:       https://job-finder-pearl.vercel.app
Backend:        https://job-finder-backend.onrender.com
API Health:     https://job-finder-backend.onrender.com/health
API Docs:       https://job-finder-backend.onrender.com/docs
MongoDB Atlas:  https://cloud.mongodb.com
```

---

## 🎯 Success Indicators

- [ ] Frontend loads at Vercel URL
- [ ] Can register new account
- [ ] Can login successfully
- [ ] Dashboard loads without CORS errors
- [ ] Auto-Apply page accessible
- [ ] Network requests show 200 responses
- [ ] No red error messages in DevTools

---

## Final Notes

### Free Tier Behavior (Render)
- ⏰ First request after 15 min inactivity takes ~30 seconds (cold start)
- This is normal! Free tier backends spin down when idle
- Upgrade to Pro ($7/month) for always-on service

### If You Need Always-On Backend
Upgrade Render to Paid plan for ~$7/month:
1. Render dashboard → Settings → Plan
2. Upgrade to Pro
3. No cold start delays

---

**Deployment complete when:**
✅ Frontend and backend both accessible  
✅ Login/register works  
✅ No CORS errors in console  
✅ API requests return 200 status  

Good luck! 🚀
