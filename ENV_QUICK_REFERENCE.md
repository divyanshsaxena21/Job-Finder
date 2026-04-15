# Environment Variables Quick Reference

## 🚀 Quick Setup

```bash
# Copy templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit files with your credentials
# See .env.GUIDE.md for detailed instructions
```

---

## 📋 Backend Variables (backend/.env)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `MONGODB_URL` | ✅ Yes | - | Database connection string |
| `DB_NAME` | ❌ No | job_finder | Database name |
| `JWT_SECRET_KEY` | ✅ Yes | - | Token signing key (generate new!) |
| `JWT_ALGORITHM` | ❌ No | HS256 | JWT algorithm |
| `JWT_EXPIRY_HOURS` | ❌ No | 24 | Token expiration hours |
| `GROQ_API_KEY` | ✅ Yes | - | Groq AI API key |
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | - | Telegram bot token |
| `BACKEND_URL` | ❌ No | http://localhost:8000 | Backend API URL |
| `FRONTEND_URL` | ❌ No | http://localhost:5173 | Frontend app URL |
| `CORS_ORIGINS` | ❌ No | http://localhost:5173,... | Allowed CORS origins |
| `ENVIRONMENT` | ❌ No | development | dev or production |

---

## 📋 Frontend Variables (frontend/.env)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `VITE_API_URL` | ❌ No | http://localhost:8000 | Backend API endpoint |
| `VITE_DEBUG` | ❌ No | false | Enable debug logging |

---

## 🔑 Where to Get Each Key

### MongoDB URL
**Local:**
```
mongodb://localhost:27017
```

**Cloud (MongoDB Atlas):**
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up (free)
3. Create cluster
4. Click "Connect" → "Drivers"
5. Copy connection string
6. Format: `mongodb+srv://username:password@cluster.mongodb.net/dbname`

### JWT_SECRET_KEY
**Generate secure random**
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### GROQ_API_KEY
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Navigate to API Keys
4. Create new key
5. Copy: `gsk_...`

### TELEGRAM_BOT_TOKEN
1. Open Telegram
2. Search for @BotFather
3. Send `/newbot`
4. Follow prompts
5. Copy token: `123456:ABC-DEF...`

### CORS_ORIGINS
**Development:**
```
http://localhost:5173,http://localhost:3000
```

**Production:**
```
https://yourdomain.com,https://www.yourdomain.com
```

---

## ✅ Development Checklist

```
[ ] MongoDB installed/accessible
[ ] backend/.env created
[ ] frontend/.env created
[ ] GROQ_API_KEY set
[ ] TELEGRAM_BOT_TOKEN set
[ ] JWT_SECRET_KEY generated
[ ] VITE_API_URL matches BACKEND_URL
[ ] Backend starts: python -m app.main
[ ] Frontend starts: npm run dev
[ ] Can register test account
[ ] No CORS errors in console
[ ] API endpoints responding (localhost:8000/docs)
```

---

## ⚠️ Production Checklist

```
[ ] New JWT_SECRET_KEY generated
[ ] ENVIRONMENT=production
[ ] MONGODB_URL uses production database
[ ] CORS_ORIGINS restricted to your domain(s)
[ ] API keys are production keys
[ ] .env file NOT committed to git
[ ] Environment variables set in hosting platform
[ ] Database backups enabled
[ ] HTTPS/SSL configured
[ ] Verified with test credentials
[ ] Monitoring/logging configured
```

---

## 🐛 Troubleshooting

### "Error: GROQ_API_KEY field required"
→ Set `GROQ_API_KEY` in `backend/.env`

### "CORS error from frontend"
→ Check `CORS_ORIGINS` includes your frontend URL

### "Cannot connect to MongoDB"
→ Verify `MONGODB_URL` format and credentials

### "Telegram not sending messages"
→ Check `TELEGRAM_BOT_TOKEN` is valid

### "Frontend can't reach API"
→ Ensure `VITE_API_URL` matches `BACKEND_URL`

---

## 📚 Documentation

- **Detailed Guide:** See [.env.GUIDE.md](.env.GUIDE.md)
- **Local Development:** See [.env.local.example](.env.local.example)
- **Production Setup:** See [.env.production.example](.env.production.example)
- **Complete Setup:** See [SETUP.md](SETUP.md)
- **Quick Start:** See [QUICK_START.md](QUICK_START.md)

---

## 🔒 Security Reminders

⚠️ **NEVER:**
- Commit `.env` files to git
- Hardcode API keys in source code
- Share production credentials in chat/email
- Use development credentials in production

✅ **ALWAYS:**
- Use `.env.example` for reference
- Generate new JWT_SECRET_KEY for production
- Store secrets in hosting platform (Vercel, Render, etc.)
- Rotate secrets periodically
- Restrict CORS_ORIGINS in production

---

## 🤔 Common Questions

**Q: Do I need all variables?**  
A: Only those marked as ✅ Yes. Defaults are provided for others.

**Q: Can I use the same .env for dev and production?**  
A: No! Use different credentials. See `.env.production.example` for production setup.

**Q: What if I lose my .env file?**  
A: Copy from `.env.example` and regenerate API keys. Save in secure location.

**Q: How often should I rotate secrets?**  
A: JWT_SECRET_KEY every 3-6 months, API keys when team changes.

**Q: Can frontend see backend .env variables?**  
A: No. Backend `.env` is server-only. Frontend can only use VITE_* variables.

---

**Last Updated:** April 15, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

