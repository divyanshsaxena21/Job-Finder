# Production Deployment - Quick Start

## TL;DR - Just Deploy!

### Backend to Render
1. Push to GitHub
2. Create account at https://render.com
3. Connect repo → New Web Service
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Add env vars (MongoDB, JWT, Groq, etc.)
7. Deploy ✅
8. Copy your Render URL

### Frontend on Vercel
1. Already deployed at https://job-finder-pearl.vercel.app ✅
2. Go to Vercel Dashboard
3. Settings → Environment Variables
4. Add: `VITE_API_URL=https://your-render-url.onrender.com`
5. Save (auto-redeploys) ✅

**Done!** Your app works! 🚀

---

## Environment Variables You Need

### Backend (Render)
```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/job_finder
JWT_SECRET_KEY=generate_random_32_char_string_here
GROQ_API_KEY=get_from_console.groq.com
BACKEND_URL=https://your-backend.onrender.com
FRONTEND_URL=https://job-finder-pearl.vercel.app
CORS_ORIGINS=https://job-finder-pearl.vercel.app,https://*.vercel.app
ENVIRONMENT=production
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-backend.onrender.com
```

---

## Test It Works

1. Visit: https://job-finder-pearl.vercel.app
2. Register or login
3. Open DevTools (F12)
4. Network tab should show ✅ 200 responses
5. No red CORS errors = Success! ✅

---

## Still Have Issues?

- **CORS error?** Check `VITE_API_URL` in Vercel env vars
- **API not responding?** Check backend URL is correct
- **Login fails?** Verify JWT_SECRET_KEY is set
- **Cold start delayed?** This is normal on free Render (30 sec wait)

See `RENDER_VERCEL_DEPLOYMENT.md` for detailed steps.
See `DEPLOYMENT_CHECKLIST.md` for complete checklist.
