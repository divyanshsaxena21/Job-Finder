# Quick Start Reference

## 🚀 5-Minute Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt

cp .env.example .env
# Edit .env: Add MONGODB_URL, GROQ_API_KEY, TELEGRAM_BOT_TOKEN

python -m app.main
# Server at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# App at http://localhost:5173
```

---

## 🔑 Essential Environment Variables

```env
# Backend/.env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/db
GROQ_API_KEY=gsk_xxxxx
TELEGRAM_BOT_TOKEN=123456:ABCxyz
JWT_SECRET_KEY=any_secret_key_here
```

---

## 📋 Default Test Credentials

After setup, register:
- **Email**: test@example.com
- **Password**: test123
- **Name**: Test User

---

## 🔗 Important URLs

| Service | URL | Notes |
|---------|-----|-------|
| Frontend | http://localhost:5173 | React app |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| MongoDB | localhost:27017 | Local only |

---

## 📦 What's Included

✅ **Complete Backend**
- JWT authentication
- MongoDB integration
- Groq AI matching
- Resume/cover letter generation
- Telegram bot
- Playwright automation

✅ **Complete Frontend**
- Login/Register pages
- Dashboard with jobs
- Job detail & matching
- Applications tracking
- Preferences management
- Responsive design

✅ **Full Documentation**
- Setup guide
- API reference
- Architecture docs
- Deployment guides
- Troubleshooting

---

## 🎯 Key Features to Test

1. **Register & Login**
   - Create account
   - Verify token in localStorage

2. **Preferences**
   - Add skills, roles, locations
   - Save and verify in API

3. **Job Management**
   - Add job manually
   - Analyze match (uses Groq)
   - View match score

4. **Document Generation**
   - Generate resume (AI-powered)
   - Generate cover letter
   - Edit before submission

5. **Applications**
   - Submit application
   - Track status
   - View applications list

---

## 🐛 Common Issues

### Backend Won't Start
```bash
# Check virtual environment
source venv/bin/activate
python -m app.main
```

### MongoDB Connection Error
```bash
# Check .env
cat .env | grep MONGODB_URL

# Test connection
python -c "from app.models.database import MongoDB; import asyncio; asyncio.run(MongoDB.connect_db('...', 'job_finder'))"
```

### Frontend Shows Blank Page
```bash
# Check console for errors
# F12 → Console tab

# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### API Connection Fails
```bash
# Ensure backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"1.0.0"}

# Check CORS in backend
# Should allow localhost:5173
```

---

## 📚 Documentation Structure

```
Job-Finder/
├── README.md              ← Main overview
├── SETUP.md              ← Complete setup guide
├── backend/README.md     ← Backend docs & deployment
├── frontend/README.md    ← Frontend docs & deployment
└── This file             ← Quick reference
```

---

## 🔐 Security Checklist

✅ Change JWT_SECRET_KEY in production
✅ Use strong MongoDB password
✅ Enable HTTPS in production
✅ Restrict CORS origins
✅ Use environment secrets manager
✅ Never commit .env file
✅ Rotate API keys regularly

---

## 🚀 Deployment Quick Links

**Backend:**
- [Render](https://render.com) - Easy Flask/FastAPI hosting
- [Railway](https://railway.app) - Good for full stack
- [AWS EC2](https://aws.amazon.com/ec2/) - Most flexible

**Frontend:**
- [Vercel](https://vercel.com) - Optimized for Vite
- [Netlify](https://netlify.com) - Great DX
- [GitHub Pages](https://pages.github.com) - Free

---

## 📞 Support Resources

1. **Error in Backend?**
   - Check logs in terminal
   - Verify .env variables
   - Test API with curl

2. **Frontend Not Loading?**
   - Check browser console (F12)
   - Verify backend is running
   - Clear browser cache

3. **API Request Errors?**
   - Check Network tab in DevTools
   - Verify token is valid
   - Check CORS settings

4. **Database Issues?**
   - Verify connection string
   - Check IP whitelist (MongoDB Atlas)
   - Test with MongoDB Compass

---

## 🎓 Next Steps

1. **Customize UI**
   - Edit color scheme in CSS
   - Add company logo
   - Modify job board layout

2. **Add Real Job Source**
   - Create Indeed scraper
   - Add LinkedIn integration
   - Connect Wellfound API

3. **Enhance Automation**
   - Improve form detection
   - Add screenshot on error
   - Save session state

4. **Add Features**
   - Email notifications
   - Job alerts
   - Interview scheduling
   - Salary tracking

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────┐
│      React Frontend (Vite)          │
│  Login | Dashboard | Applications   │
│      Context + Axios API Client     │
└──────────────────┬──────────────────┘
                   │ HTTP/JWT
┌──────────────────▼──────────────────┐
│   FastAPI Backend (Python)          │
│  Auth | Jobs | Applications | AI    │
│   MongoDB Motor Async Drivers       │
└──────────────────┬──────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
   MongoDB      Groq API   Playwright
  (Database)   (AI Match)  (Automation)
```

---

**Last Updated:** April 2026  
**Version:** 1.0.0 Production Ready

For detailed instructions, see **SETUP.md** and **README.md**
