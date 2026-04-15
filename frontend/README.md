# Frontend Setup & Deployment Guide

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

App will open at: `http://localhost:5173`

### 3. Build for Production

```bash
npm run build
```

Output will be in `dist/` directory

## Configuration

### Environment Variables

Create `.env` file in frontend root:

```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Job Finder
VITE_APP_VERSION=1.0.0
```

### API URL Configuration

The app automatically routes API calls to the backend:

```javascript
// src/services/api.js
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000'
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/                  # Page components
│   │   ├── Login.jsx          # Auth pages
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx      # Main dashboard
│   │   ├── JobDetail.jsx      # Job detail page
│   │   ├── Applications.jsx   # Application tracking
│   │   └── Preferences.jsx    # User preferences
│   │
│   ├── components/            # Reusable components
│   │   └── ProtectedRoute.jsx # Auth guard
│   │
│   ├── context/              # React Context
│   │   └── AuthContext.jsx   # Auth state management
│   │
│   ├── services/             # API client
│   │   └── api.js           # Axios instance & endpoints
│   │
│   ├── styles/              # CSS files
│   │   ├── index.css       # Global styles
│   │   ├── auth.css        # Auth pages
│   │   ├── dashboard.css   # Dashboard
│   │   ├── job-detail.css  # Job detail
│   │   ├── applications.css
│   │   └── preferences.css
│   │
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
│
├── index.html              # HTML template
├── package.json
├── vite.config.js          # Vite configuration
└── .gitignore
```

## Authentication Flow

### 1. User Registration

```jsx
// User provides: name, email, password, (optional) telegram_chat_id
// API call: POST /auth/register
// Response: { access_token, user }
// Token stored in localStorage
```

### 2. User Login

```jsx
// User provides: email, password
// API call: POST /auth/login
// Response: { access_token, user }
// Token stored in localStorage
// Redirected to dashboard
```

### 3. Protected Routes

```jsx
// Any route wrapped in <ProtectedRoute> requires authentication
// If no token, redirect to /login
// On each page load, verify token via GET /auth/me
```

### 4. Token Management

```javascript
// Stored in localStorage
localStorage.getItem('access_token')
localStorage.setItem('access_token', token)
localStorage.removeItem('access_token')

// Attached to all API requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

## API Integration

### API Service Structure

```javascript
// src/services/api.js

// Authentication APIs
authAPI.register(name, email, password, telegramChatId)
authAPI.login(email, password)
authAPI.getMe()

// Jobs APIs
jobsAPI.create(jobData)
jobsAPI.getAll(skip, limit)
jobsAPI.getById(jobId)
jobsAPI.matchJob(jobId)
jobsAPI.generateResume(jobId)
jobsAPI.generateCoverLetter(jobId)
jobsAPI.filterByPreferences()

// Applications APIs
applicationsAPI.submit(jobId, resume, coverLetter)
applicationsAPI.getAll(statusFilter)
applicationsAPI.getById(appId)
applicationsAPI.approve(appId)
applicationsAPI.reject(appId)

// Preferences APIs
preferencesAPI.get()
preferencesAPI.update(preferences)
```

## Pages & Features

### 1. Login Page (`/login`)
- Email and password input
- Error messages
- Link to register
- Authentication handling

### 2. Register Page (`/register`)
- Name, email, password input
- Optional Telegram Chat ID
- Agreement to terms
- Link to login

### 3. Dashboard (`/dashboard`)
- Job list with cards
- Match score badges
- Filter by status
- Add job manually
- Job detail link
- Logout button

### 4. Job Detail (`/job/:jobId`)
- Full job description
- Match analysis (if available)
- Generate resume button
- Generate cover letter button
- Resume preview textarea
- Cover letter preview textarea
- Submit application button

### 5. Applications (`/applications`)
- Statistics cards
- Filter by status (pending, applied, rejected)
- Application cards with preview
- Resume preview
- Cover letter preview
- Status badges

### 6. Preferences (`/preferences`)
- Add/remove skills
- Add/remove target roles
- Select experience level
- Add/remove locations
- Select job types (checkboxes)
- Salary range (min/max)
- Save button

## Styling

### Design System

**Colors:**
- Primary: #667eea (Purple)
- Secondary: #f0f0f0 (Light gray)
- Success: #4caf50 (Green)
- Warning: #ff9800 (Orange)
- Danger: #f44336 (Red)
- Text: #333 (Dark gray)
- Light Text: #999 (Medium gray)

**Spacing:**
- 8px, 12px, 16px, 20px, 24px, 32px, 40px

**Fonts:**
- System font stack (Apple/Google/Windows native)
- Fallback to sans-serif

**Components:**
- Buttons: 12x20px padding, 6px border radius
- Inputs: 12x12px padding, 1px border
- Cards: 8px border radius, subtle shadow

## Common Tasks

### Add a New Page

```jsx
// 1. Create pages/MyPage.jsx
import React from 'react'
import '../styles/mypage.css'

export const MyPage = () => {
  return <div>My Page</div>
}

// 2. Add route in App.jsx
<Route path="/mypage" element={<ProtectedRoute><MyPage /></ProtectedRoute>} />

// 3. Add to navigation in Dashboard.jsx
<li><a href="/mypage">My Page</a></li>

// 4. Create styles/mypage.css
```

### Add a New API Call

```javascript
// In src/services/api.js
export const myAPI = {
  getData: () => api.get('/myendpoint'),
  postData: (data) => api.post('/myendpoint', data)
}

// In your component
import { myAPI } from '../services/api'

const response = await myAPI.getData()
```

### Handle Loading States

```jsx
const [loading, setLoading] = useState(true)
const [error, setError] = useState('')

useEffect(() => {
  const fetch = async () => {
    try {
      const response = await jobsAPI.getAll()
      setJobs(response.data)
    } catch (err) {
      setError('Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }
  fetch()
}, [])

if (loading) return <div>Loading...</div>
if (error) return <div className="error">{error}</div>
```

## Deployment

### Vercel (Recommended)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy
vercel

# 4. Set environment variables in Vercel dashboard
VITE_API_URL=https://api.yourdomain.com
```

### Netlify

```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Build
npm run build

# 3. Deploy
netlify deploy --prod --dir=dist

# Or connect GitHub for auto-deployment
```

### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
docker build -t job-finder-frontend .
docker run -p 80:80 job-finder-frontend
```

### Traditional Hosting

```bash
# 1. Build
npm run build

# 2. Upload dist/ folder to your hosting
# 3. Configure server to serve index.html for all routes

# Example nginx config:
# location / {
#   try_files $uri $uri/ /index.html;
# }
```

## Performance Optimization

### Current Optimizations
- Code splitting via Vite
- CSS tree-shaking
- Minification in production
- Fast refresh in development

### Potential Improvements
- Image lazy loading
- Component code splitting with React.lazy
- Service Worker for offline support
- Local caching strategy
- API response caching
- Bundle analysis

### Check Bundle Size
```bash
npm run build

# The output will show bundle size
# Keep main.js under 200KB
```

## Troubleshooting

### API Connection Issues

```javascript
// Check API URL configuration
console.log(process.env.VITE_API_URL)

// Test API endpoint
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

### CORS Errors

```javascript
// Backend might not have CORS enabled
// Check main.py for CORSMiddleware configuration
// Ensure frontend URL is in allow_origins
```

### Token Not Persisting

```javascript
// Check localStorage
console.log(localStorage.getItem('access_token'))

// Verify token is valid
// Check expiry time
```

### Blank Page on Load

```javascript
// Check browser console for errors
// Verify React is rendering
// Check if #root div exists in index.html
```

## Development Tips

### Hot Reload
Changes to React components automatically reload (Vite).

### Debug Mode
```javascript
// In browser console
localStorage.setItem('DEBUG', 'true')

// In your component
if (localStorage.getItem('DEBUG')) {
  console.log('Debug info')
}
```

### API Response Logging
```javascript
// In src/services/api.js
api.interceptors.response.use(response => {
  console.log('API Response:', response.config.url, response.data)
  return response
})
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile: iOS Safari 12+, Chrome Android

---

For detailed React documentation: https://react.dev
For detailed Vite documentation: https://vitejs.dev
