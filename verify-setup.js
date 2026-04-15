#!/usr/bin/env node

/**
 * Verify Render + Vercel Production Setup
 * 
 * Run this before deploying to check all configuration
 */

const fs = require('fs');
const path = require('path');

console.log('\n╔════════════════════════════════════════════════════════════╗');
console.log('║     Job Finder - Render + Vercel Setup Verification        ║');
console.log('╚════════════════════════════════════════════════════════════╝\n');

let allGood = true;

// Check 1: Environment Variables in .env files
console.log('📋 Checking Configuration Files...\n');

// Backend .env
const backendEnvPath = path.join(__dirname, '../backend/.env');
if (fs.existsSync(backendEnvPath)) {
  const backendEnv = fs.readFileSync(backendEnvPath, 'utf8');
  
  if (backendEnv.includes('MONGODB_URL=')) {
    console.log('✅ Backend: .env has MONGODB_URL');
  } else {
    console.log('❌ Backend: .env missing MONGODB_URL');
    allGood = false;
  }
  
  if (backendEnv.includes('BACKEND_URL=https://')) {
    console.log('✅ Backend: BACKEND_URL points to HTTPS');
  } else {
    console.log('⚠️  Backend: BACKEND_URL should use HTTPS (https://your-backend.onrender.com)');
  }
  
  if (backendEnv.includes('CORS_ORIGINS=')) {
    if (backendEnv.includes('job-finder-pearl.vercel.app') || backendEnv.includes('*.vercel.app')) {
      console.log('✅ Backend: CORS_ORIGINS includes Vercel domain');
    } else {
      console.log('❌ Backend: CORS_ORIGINS missing Vercel domain (job-finder-pearl.vercel.app)');
      allGood = false;
    }
  }
  
  if (backendEnv.includes('ENVIRONMENT=production')) {
    console.log('✅ Backend: ENVIRONMENT is set to production');
  } else {
    console.log('⚠️  Backend: ENVIRONMENT should be "production"');
  }
} else {
  console.log('⚠️  Backend: No .env file found (will use Render env vars)');
}

// Frontend .env.local
const frontendEnvPath = path.join(__dirname, '../frontend/.env.local');
if (fs.existsSync(frontendEnvPath)) {
  const frontendEnv = fs.readFileSync(frontendEnvPath, 'utf8');
  
  if (frontendEnv.includes('VITE_API_URL=')) {
    console.log('✅ Frontend: .env.local has VITE_API_URL');
    
    if (frontendEnv.includes('http://localhost')) {
      console.log('⚠️  Frontend: VITE_API_URL points to localhost (development mode)');
    } else if (frontendEnv.includes('onrender.com')) {
      console.log('✅ Frontend: VITE_API_URL points to Render backend');
    }
  } else {
    console.log('⚠️  Frontend: .env.local missing VITE_API_URL');
  }
} else {
  console.log('ℹ️  Frontend: No .env.local (will use Vercel env vars)');
}

// Check 2: Code - No hardcoded localhost
console.log('\n🔍 Checking Source Code...\n');

const apiJsPath = path.join(__dirname, '../frontend/src/services/api.js');
const apiJsContent = fs.readFileSync(apiJsPath, 'utf8');

if (apiJsContent.includes("'http://localhost") || apiJsContent.includes('"http://localhost')) {
  console.log('❌ api.js: Contains hardcoded localhost URL');
  allGood = false;
} else {
  console.log('✅ api.js: No hardcoded localhost URLs');
}

if (apiJsContent.includes('VITE_API_URL')) {
  console.log('✅ api.js: Uses VITE_API_URL environment variable');
} else {
  console.log('❌ api.js: Not using VITE_API_URL environment variable');
  allGood = false;
}

const autoApplyPath = path.join(__dirname, '../frontend/src/pages/AutoApplySettings.jsx');
const autoApplyContent = fs.readFileSync(autoApplyPath, 'utf8');

if (autoApplyContent.includes('VITE_API_BASE_URL')) {
  console.log('❌ AutoApplySettings.jsx: Using wrong env var (VITE_API_BASE_URL instead of VITE_API_URL)');
  allGood = false;
} else if (autoApplyContent.includes('VITE_API_URL')) {
  console.log('✅ AutoApplySettings.jsx: Using VITE_API_URL environment variable');
} else {
  console.log('⚠️  AutoApplySettings.jsx: Not using environment variable');
}

// Check 3: Vercel Deployment
console.log('\n🚀 Vercel Deployment Checklist...\n');

console.log('Required steps before deploying to Vercel:');
console.log('  1. ✓ Frontend code is pushed to GitHub');
console.log('  2. ✓ Go to https://vercel.com/dashboard');
console.log('  3. ✓ Select Job Finder project');
console.log('  4. ✓ Settings → Environment Variables');
console.log('  5. ✓ Add: VITE_API_URL = https://your-backend.onrender.com');
console.log('  6. ✓ Click Save');
console.log('  7. ✓ Wait for auto-redeploy (2-3 min)\n');

// Check 4: Render Deployment
console.log('🚀 Render Deployment Checklist...\n');

console.log('Required steps before deploying to Render:');
console.log('  1. ✓ Backend code is pushed to GitHub');
console.log('  2. ✓ Go to https://render.com');
console.log('  3. ✓ New Web Service → Select your repo');
console.log('  4. ✓ Build: pip install -r requirements.txt');
console.log('  5. ✓ Start: uvicorn app.main:app --host 0.0.0.0 --port 8000');
console.log('  6. ✓ Add all environment variables (see below)');
console.log('  7. ✓ Deploy and copy the Render URL\n');

console.log('Environment variables needed on Render:');
console.log('  • MONGODB_URL');
console.log('  • JWT_SECRET_KEY');
console.log('  • GROQ_API_KEY');
console.log('  • BACKEND_URL=https://your-backend.onrender.com');
console.log('  • FRONTEND_URL=https://job-finder-pearl.vercel.app');
console.log('  • CORS_ORIGINS=https://job-finder-pearl.vercel.app,https://*.vercel.app');
console.log('  • ENVIRONMENT=production\n');

// Final check
console.log('═════════════════════════════════════════════════════════════\n');

if (allGood) {
  console.log('✅ All checks passed! You\'re ready to deploy.\n');
  console.log('Next step: Deploy backend to Render, then frontend to Vercel.\n');
  process.exit(0);
} else {
  console.log('❌ Some issues found. Please fix them before deploying.\n');
  process.exit(1);
}
