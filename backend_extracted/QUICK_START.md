# Quick Start Guide - Throne Companions Backend Deployment

This is the fastest path to get your backend deployed on Render.com.

## Prerequisites

Before starting, have these ready:
- MongoDB connection string (from MongoDB Atlas)
- Emergent LLM API key
- GitHub account
- Render.com account (free)

## 5-Minute Deployment

### Step 1: Push to GitHub (2 minutes)

Open terminal and run these commands:

```bash
# Navigate to backend directory
cd /app/backend_extracted

# Initialize Git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Throne Companions Backend"

# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/throne-companions-backend.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**If authentication fails:**
- Generate a Personal Access Token: GitHub Settings → Developer Settings → Personal Access Tokens
- Use the token as your password when prompted

### Step 2: Deploy on Render (3 minutes)

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Click **Create Web Service**

### Step 3: Add Environment Variables

In Render dashboard, add these variables:

**Required:**
- `MONGO_URL` - Your MongoDB Atlas connection string
- `JWT_SECRET` - Any random string (e.g., `throne_companions_secret_2024`)
- `EMERGENT_LLM_KEY` - Your Emergent LLM API key

**Optional:**
- `MIXPANEL_TOKEN` - For analytics
- `SENDGRID_API_KEY` - For admin emails

### Step 4: Wait for Deployment

Render will:
1. Clone your repository
2. Install dependencies (including emergentintegrations)
3. Start your server
4. Provide you with a URL like: `https://throne-companions-backend.onrender.com`

## Verify Deployment

Test your API:
```bash
curl https://your-service.onrender.com/
```

View API docs:
```
https://your-service.onrender.com/docs
```

## Common Issues

### Issue: emergentintegrations not found
**Fix:** Verify build command in render.yaml includes custom package index

### Issue: MongoDB connection failed
**Fix:** Whitelist all IPs (0.0.0.0/0) in MongoDB Atlas Network Access

### Issue: Push to GitHub failed
**Fix:** Use Personal Access Token instead of password

## Get MongoDB Connection String

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Create database user
4. Click "Connect" → "Connect your application"
5. Copy connection string
6. Replace `<password>` with your database password

## Need More Help?

- **Full Documentation**: See `README.md`
- **GitHub Setup**: See `GITHUB_DEPLOYMENT.md`
- **Deployment Checklist**: See `DEPLOYMENT_CHECKLIST.md`
- **Verification**: Run `python verify_setup.py`

## Your Backend is Ready! 🎉

Once deployed, you can:
- Connect your frontend to the Render URL
- Test API endpoints at `/docs`
- Monitor logs in Render dashboard
- Set up custom domain (optional)

---

**Support:**
- Render Logs: Check for deployment errors
- MongoDB Atlas: Verify connection settings
- GitHub: Ensure all files are pushed

**Deployment Time:** ~5-10 minutes total
