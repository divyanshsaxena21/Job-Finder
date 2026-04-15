# Deploy Now - Final Checklist

## ✅ Code Fixes Applied

Your code has been fixed:
- ✅ `AutoApplySettings.jsx` - Fixed environment variable name
- ✅ `api.js` - Removed localhost fallback  
- ✅ Error handling - Added if env var is missing

Now push to GitHub:
```bash
git add .
git commit -m "Fix: Use VITE_API_URL env var for production, remove localhost fallback"
git push origin main
```

---

## 🎯 Deploy Backend (Render)

### Create Render Service
1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Select your GitHub `Job-Finder` repository
4. Configure:
   - **Name**: `job-finder-backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Add Environment Variables
Click **"Advanced"** and add these variables:

```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=job_finder
JWT_SECRET_KEY=your_secure_secret_key_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
GROQ_API_KEY=your_groq_api_key_from_console.groq.com
TELEGRAM_BOT_TOKEN=your_telegram_token
BACKEND_URL=https://job-finder-backend.onrender.com
FRONTEND_URL=https://job-finder-pearl.vercel.app
CORS_ORIGINS=https://job-finder-pearl.vercel.app,https://*.vercel.app
ENVIRONMENT=production
DAILY_APPLICATION_LIMIT=5
```

### Deploy
- Click **"Create Web Service"**
- Wait 3-5 minutes for deployment
- **COPY YOUR RENDER URL** (e.g., `https://job-finder-backend.onrender.com`)
- Verify: Visit `https://job-finder-backend.onrender.com/health`

---

## 🎯 Deploy Frontend (Vercel)

### Set Environment Variable
1. Go to https://vercel.com/dashboard
2. Select **Job Finder** project
3. Click **Settings** → **Environment Variables**
4. **Add New Variable:**
   - **Name**: `VITE_API_URL`
   - **Value**: `https://job-finder-backend.onrender.com` (your Render URL)
   - **Auto-Redeploy**: Vercel does this automatically
5. Click **Save**

### Verify Deployment
- Wait 2-3 minutes for Vercel to redeploy
- Check: https://vercel.com/dashboard → Deployments tab
- When done, visit: https://job-finder-pearl.vercel.app

---

## 🧪 Test Everything Works

### Test 1: Backend Health
```
Visit: https://job-finder-backend.onrender.com/health
Expected: {"status": "healthy", "version": "1.0.0"}
```

### Test 2: Frontend Loads
```
Visit: https://job-finder-pearl.vercel.app
Should load without errors ✅
```

### Test 3: Login Works
1. Go to https://job-finder-pearl.vercel.app
2. Open DevTools (F12) → Network tab
3. Click Login or Register
4. Check Network requests:
   - ✅ Should see POST to `https://job-finder-backend.onrender.com/auth/...`
   - ✅ Status should be 200, NOT CORS errors
5. If login succeeds → **Everything works!** 🎉

### Test 4: Auto-Apply Page
1. Login successfully
2. Click "🤖 Auto-Apply" in navbar
3. Should load without CORS errors
4. See your preferences and stats

---

## 🚀 Full Deployment Summary

| Step | Status | Where |
|------|--------|-------|
| 1. Push code changes | TODO | `git push origin main` |
| 2. Deploy backend to Render | TODO | https://render.com |
| 3. Set Vercel env var | TODO | https://vercel.com/dashboard |
| 4. Test frontend | TODO | https://job-finder-pearl.vercel.app |

---

## ⏱️ Timeline

- **5 min**: Push code to GitHub
- **5 min**: Create Render service + add env vars
- **5 min**: Render deploys (3-5 min wait)
- **2 min**: Set Vercel env var
- **3 min**: Vercel redeploys
- **5 min**: Test everything

**Total: ~25 minutes to full production!**

---

## After Deployment

### Monitor
- Render logs: https://render.com → Services → job-finder-backend → Logs
- Vercel logs: https://vercel.com/dashboard → Job Finder → Deployments

### If Issues Appear
1. Check environment variables are set correctly
2. Verify MongoDB connection string
3. Test backend health endpoint
4. Hard refresh frontend (Ctrl+Shift+R)
5. Check browser DevTools → Network tab

---

## Notes

- **Cold Start**: First request to Render backend takes ~30 seconds (normal for free tier)
- **Auto-Redeploy**: Vercel redeploys automatically when env var changes
- **HTTPS Only**: All production URLs must use HTTPS
- **CORS**: Backend CORS includes Vercel domain automatically

---

**You're ready! 🚀 Follow the steps above and you'll be live!**
