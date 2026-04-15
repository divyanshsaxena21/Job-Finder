# Render + Vercel Deployment Guide

## Overview
- **Frontend**: Vercel (https://job-finder-pearl.vercel.app)
- **Backend**: Render (https://your-backend.onrender.com)
- **Database**: MongoDB Atlas
- **AI/APIs**: Groq, Telegram

---

## Step 1: Deploy Backend to Render

### Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Deploy Your Backend

1. **Click "New +" → "Web Service"**
   ![Render Dashboard](https://render.com/images/home/hero.png)

2. **Select Your Repository**
   - Find `Job-Finder` repository
   - Click "Connect"

3. **Configure Service**
   - **Name**: `job-finder-backend` (or any name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

4. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable"
   
   Add these (get values from your local .env):
   ```
   MONGODB_URL=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=job_finder
   JWT_SECRET_KEY=your_secure_random_string_min_32_chars
   JWT_ALGORITHM=HS256
   JWT_EXPIRY_HOURS=24
   GROQ_API_KEY=your_groq_api_key_from_console.groq.com
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   BACKEND_URL=https://job-finder-backend.onrender.com
   FRONTEND_URL=https://job-finder-pearl.vercel.app
   CORS_ORIGINS=https://job-finder-pearl.vercel.app,https://*.vercel.app
   ENVIRONMENT=production
   DAILY_APPLICATION_LIMIT=5
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)
   - Get your backend URL: `https://job-finder-backend.onrender.com`

---

## Step 2: Get Backend URL from Render

After deployment:
1. Go to your Render service dashboard
2. Copy the URL from the top (example: `https://job-finder-backend.onrender.com`)
3. **Save this URL** - you'll need it for Vercel

**Verify Backend is Running:**
```
https://job-finder-backend.onrender.com/health
```
Should return:
```json
{"status": "healthy", "version": "1.0.0"}
```

---

## Step 3: Update Frontend on Vercel

### Set Environment Variable

1. Go to https://vercel.com/dashboard
2. Click your `Job Finder` project
3. Go to **Settings** → **Environment Variables**
4. Add new variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://job-finder-backend.onrender.com` (your Render URL)
   - Click "Save"

5. **Important**: After adding env var, Vercel automatically redeploys

### Verify Deployment
Wait 2-3 minutes, then:
1. Go to https://job-finder-pearl.vercel.app
2. Open DevTools (F12) → Network tab
3. Try to login
4. Check if API calls succeed (should see 200 responses)

---

## Step 4: Verify CORS is Working

**Test API Connection:**
```bash
# From your browser console or curl:
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://job-finder-backend.onrender.com/preferences

# Should return 200 OK, not CORS error
```

---

## All URLs

| Component | URL | Status |
|-----------|-----|--------|
| Frontend | https://job-finder-pearl.vercel.app | ✅ Deployed |
| Backend API | https://job-finder-backend.onrender.com | ✅ Deployed |
| API Health | https://job-finder-backend.onrender.com/health | ✅ Check here |
| API Docs | https://job-finder-backend.onrender.com/docs | ✅ Swagger UI |
| MongoDB Atlas | https://cloud.mongodb.com | ✅ Active |

---

## Environment Variables Summary

### Backend (Render) - Set in Render Dashboard
```
MONGODB_URL=your_mongodb_connection_string
DB_NAME=job_finder
JWT_SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_key
TELEGRAM_BOT_TOKEN=your_telegram_key
BACKEND_URL=https://job-finder-backend.onrender.com
FRONTEND_URL=https://job-finder-pearl.vercel.app
CORS_ORIGINS=https://job-finder-pearl.vercel.app,https://*.vercel.app
ENVIRONMENT=production
```

### Frontend (Vercel) - Set in Vercel Dashboard
```
VITE_API_URL=https://job-finder-backend.onrender.com
```

---

## Troubleshooting

### "CORS error" on Vercel
✅ **Solution**: 
- Verify `VITE_API_URL` is set correctly in Vercel
- Check backend CORS_ORIGINS includes Vercel domain
- Redeploy Vercel after changing env var

### "API not responding" 
✅ **Solution**:
- Test backend health: https://job-finder-backend.onrender.com/health
- Check Render logs for errors
- Verify MongoDB connection string
- Verify all env vars are set

### "Login fails"
✅ **Solution**:
- Check backend logs on Render
- Verify JWT_SECRET_KEY is set
- Try registering new account instead

### "Cold start delay" (first request takes 30 seconds)
✅ **This is normal on free Render tier** - backend sleeps when idle, wakes on request

---

## Free Tier Limitations

### Render (Free)
- ✅ Auto-deploys from GitHub
- ✅ HTTPS/SSL included
- ⚠️ Spins down after 15 min inactivity
- ⚠️ Limited bandwidth
- 💰 Upgrade to Pro for always-on ($7/month)

### Vercel (Free)
- ✅ Fast static hosting
- ✅ ServerLess functions
- ✅ Better than Netlify for scaling
- ⚠️ Limited API calls
- 💰 Pro for advanced features

---

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Copy Render URL
3. ✅ Set Vercel env var with Render URL
4. ✅ Test API calls from frontend
5. ✅ Monitor logs on Render dashboard

---

## Support

**Render Docs**: https://render.com/docs  
**Vercel Docs**: https://vercel.com/docs  
**MongoDB Atlas**: https://docs.atlas.mongodb.com

Good luck! 🚀
