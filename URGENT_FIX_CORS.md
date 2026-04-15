# URGENT FIX - CORS Error on Vercel

## Your Issue
```
Error at https://job-finder-pearl.vercel.app/auto-apply
"Access to XMLHttpRequest at 'http://localhost:8000' blocked by CORS"
```

## Root Cause
Your frontend on Vercel was trying to call `http://localhost:8000` instead of your Render backend.

**Why?** Two bugs in the code:
1. ❌ `AutoApplySettings.jsx` was looking for wrong env var (`VITE_API_BASE_URL` instead of `VITE_API_URL`)
2. ❌ When env var not found, it fell back to hardcoded `http://localhost:8000`

## Fixed! ✅

**Changes made:**
- ✅ `AutoApplySettings.jsx` - Now uses correct `VITE_API_URL` environment variable
- ✅ `api.js` - Removed localhost fallback, requires `VITE_API_URL` to be set
- ✅ Added error messages if env var is missing

---

## What You Must Do NOW (3 minutes)

### Step 1: Set Environment Variable in Vercel
1. Go to https://vercel.com/dashboard
2. Click your **Job Finder** project
3. Go to **Settings** → **Environment Variables**
4. Add new variable:
   ```
   Name: VITE_API_URL
   Value: https://your-backend.onrender.com
   ```
   (Replace with your actual Render URL if different)
5. Click **Save**

### Step 2: Vercel Auto-Redeploys
- Vercel automatically redeploys after env var change
- Wait 2-3 minutes for deployment to complete
- Check: https://vercel.com/dashboard → Job Finder → Deployments tab

### Step 3: Test It Works
1. Go to https://job-finder-pearl.vercel.app
2. Open DevTools (F12)
3. Go to Network tab
4. Try to login
5. Check API calls:
   - Should see ✅ **200 responses** (not CORS errors)
   - URLs should point to **https://your-backend.onrender.com**

---

## Deployment Steps

### Backend (Render)
```
1. https://render.com → New Web Service
2. Select your GitHub repo
3. Build: pip install -r requirements.txt
4. Start: uvicorn app.main:app --host 0.0.0.0 --port 8000
5. Add environment variables
6. Deploy
7. Copy Render URL (example: https://job-finder-backend.onrender.com)
```

### Frontend (Vercel) - WHAT YOU NEED TO DO NOW
```
1. https://vercel.com → Job Finder project
2. Settings → Environment Variables
3. Add: VITE_API_URL = https://your-render-url.onrender.com
4. Save (auto-redeploy)
5. Test at https://job-finder-pearl.vercel.app
```

---

## Verify Setup

Run this to verify everything is configured correctly:
```bash
node verify-setup.js
```

This checks:
- ✅ Environment variables configured
- ✅ No hardcoded localhost URLs
- ✅ Correct variable names used
- ✅ CORS settings correct

---

## If CORS Error Still Appears

1. **Hard refresh** browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. **Clear cache**: Settings → Clear browsing data
3. **Check Render backend URL** is set correctly in Vercel
4. **Verify Render backend is running**:
   ```
   Visit: https://your-backend.onrender.com/health
   Should see: {"status": "healthy", "version": "1.0.0"}
   ```

---

## Summary

| Issue | Fixed |
|-------|-------|
| AutoApplySettings env var | ✅ Changed to VITE_API_URL |
| Hardcoded localhost | ✅ Removed |
| api.js error handling | ✅ Added |

**Now you must:** Set `VITE_API_URL` in Vercel dashboard (3 minutes)

Then test: https://job-finder-pearl.vercel.app

✅ CORS error gone!
