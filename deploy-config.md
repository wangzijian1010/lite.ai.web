# Deployment Configuration Guide

## Problem
The current `.env.production` file points to a development IDE URL that won't be accessible in production, preventing proper frontend-backend testing during deployment.

## Solution

### 1. Environment Files Setup
- `.env` - Default development environment
- `.env.production` - Production environment (needs actual backend URL)
- `.env.local.example` - Template for local development

### 2. Deployment Steps

#### For CloudStudio Deployment:
1. Update `frontend/.env.production` with your actual backend URL:
   ```
   VITE_API_BASE_URL=https://your-deployed-backend-url.com
   ```

2. If backend and frontend are deployed on the same domain, use relative URL:
   ```
   VITE_API_BASE_URL=/api
   ```

#### For Vercel/Netlify Deployment:
1. Set environment variables in your deployment platform:
   - Variable name: `VITE_API_BASE_URL`
   - Value: Your backend URL (e.g., `https://your-backend.herokuapp.com`)

### 3. Backend CORS Configuration
Make sure your backend allows your frontend domain in CORS settings.

Current backend CORS config in `backend/app/main.py`:
```python
allow_origins=[
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "https://lite-ai-web.vercel.app",
    "https://*.vercel.app"
]
```

Add your production frontend URL to this list.

### 4. Testing Before Deployment
1. Update `.env.production` with your backend URL
2. Build the frontend: `npm run build`
3. Preview the build: `npm run preview`
4. Test API calls to ensure connectivity

### 5. Common Deployment Scenarios

#### Same Domain Deployment:
```
VITE_API_BASE_URL=/api
```

#### Different Domain Deployment:
```
VITE_API_BASE_URL=https://api.yourdomain.com
```

#### CloudStudio Deployment:
```
VITE_API_BASE_URL=https://your-cloudstudio-backend-url.com
```

### 6. Environment Variable Priority
1. `.env.local` (highest priority, git-ignored)
2. `.env.production` (for production builds)
3. `.env` (default)