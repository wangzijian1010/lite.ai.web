# Finding Railway PostgreSQL Public URL - Visual Guide

## Step-by-Step Instructions

### 1. Login to Railway
- Go to https://railway.app
- Login with your account

### 2. Find Your Project
- You should see your project dashboard
- Look for your project name (probably something like "lite-ai-web" or similar)

### 3. Click on PostgreSQL Service
- In your project, you'll see service boxes/cards
- One should be labeled "PostgreSQL" or have a PostgreSQL icon
- Click on this PostgreSQL service box

### 4. Navigate to Connect Tab
- Once inside the PostgreSQL service, look at the top tabs
- You should see: Overview, Metrics, **Connect**, Variables, Settings
- Click on **"Connect"**

### 5. Look for Connection Information
In the Connect tab, you might see different sections:

#### Option A: Public Network Section
- Look for a section titled "Public Network" or "External Connection"
- Copy the "Database URL" from this section

#### Option B: Connection Details
- Look for connection details that show:
  - Host: something ending in `.railway.app` or `rlwy.net`
  - Port: (might be 5432 or another number)
  - Database: railway
  - Username: postgres
  - Password: (long string)

#### Option C: Connect Button
- Look for a "Connect" button or "Connection String" button
- This might show you the full connection URL

## What the URL Should Look Like

✅ **CORRECT (Public URL):**
```
postgresql://postgres:password@containers-us-west-123.railway.app:5432/railway
```
OR
```
postgresql://postgres:password@viaduct.proxy.rlwy.net:5432/railway
```

❌ **INCORRECT (Internal URL - won't work locally):**
```
postgresql://postgres:password@postgres.railway.internal:5432/railway
```

## If You Can't Find It

If you're still having trouble, try:
1. Look for any button that says "Connect Externally" or "Public Access"
2. Check if there's a toggle to switch between "Internal" and "External" connections
3. Look in the "Variables" tab for DATABASE_URL or similar
4. Contact Railway support or check their documentation

## Alternative: Use Railway CLI
If you have Railway CLI installed:
```bash
railway login
railway link [your-project-id]
railway variables
```

This should show you all environment variables including the DATABASE_URL.