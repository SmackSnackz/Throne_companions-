# Deployment Checklist for Throne Companions Backend

Use this checklist to ensure a smooth deployment to Render.com.

## Pre-Deployment Checklist

### 1. Code Verification
- [x] All Python files extracted from original backend
- [x] Configuration files in `/config` directory
- [x] `requirements.txt` includes all dependencies
- [x] `emergentintegrations` is listed in requirements.txt
- [x] `.env.example` provides template for environment variables
- [x] `.gitignore` excludes sensitive files

### 2. Deployment Files
- [x] `Dockerfile` created with proper emergentintegrations installation
- [x] `render.yaml` configured for Render.com deployment
- [x] `README.md` with comprehensive documentation
- [x] `GITHUB_DEPLOYMENT.md` with step-by-step GitHub/Render guide

### 3. Environment Variables (Required for Render)
- [ ] `MONGO_URL` - MongoDB connection string
- [ ] `JWT_SECRET` - Secret key for JWT tokens
- [ ] `EMERGENT_LLM_KEY` - Emergent LLM API key
- [ ] `FREE_TIER_MESSAGE_LIMIT` - Set to "20" (optional)
- [ ] `CORS_ORIGINS` - Set to "*" or specific origins (optional)

### 4. Optional Environment Variables
- [ ] `MIXPANEL_TOKEN` - For analytics tracking
- [ ] `SENDGRID_API_KEY` - For admin email authentication
- [ ] `ADMIN_EMAIL` - Admin email address
- [ ] `REDIS_URL` - For message counting (if needed)

### 5. External Services Setup
- [ ] **MongoDB**: Set up MongoDB Atlas account and create cluster
  - URL: https://www.mongodb.com/cloud/atlas
  - Get connection string
  - Whitelist all IPs (0.0.0.0/0) in Network Access
- [ ] **Emergent LLM Key**: Verify key is active and has credits
- [ ] **Mixpanel** (optional): Create project and get token
- [ ] **SendGrid** (optional): Get API key for email service

## GitHub Setup Checklist

### 6. Git Repository
- [ ] Navigate to `/app/backend_extracted`
- [ ] Run `git init`
- [ ] Run `git add .`
- [ ] Run `git commit -m "Initial commit: Backend for Render deployment"`

### 7. GitHub Repository Creation
- [ ] Create new repository on GitHub
- [ ] Name: `throne-companions-backend` (or your choice)
- [ ] Visibility: Private (recommended)
- [ ] Do NOT initialize with README, .gitignore, or license

### 8. Push to GitHub
Choose one method:

#### Option A: HTTPS with Personal Access Token
- [ ] Generate Personal Access Token on GitHub
  - Settings → Developer settings → Personal access tokens
  - Select `repo` scope
- [ ] Run: `git remote add origin https://github.com/YOUR_USERNAME/throne-companions-backend.git`
- [ ] Run: `git branch -M main`
- [ ] Run: `git push -u origin main`
- [ ] Enter username and token as password

#### Option B: SSH
- [ ] Generate SSH key: `ssh-keygen -t ed25519 -C "your.email@example.com"`
- [ ] Add SSH key to GitHub (Settings → SSH and GPG keys)
- [ ] Run: `git remote add origin git@github.com:YOUR_USERNAME/throne-companions-backend.git`
- [ ] Run: `git branch -M main`
- [ ] Run: `git push -u origin main`

## Render.com Deployment Checklist

### 9. Create Web Service
- [ ] Go to https://dashboard.render.com/
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub account (if not already connected)
- [ ] Select `throne-companions-backend` repository
- [ ] Render should auto-detect `render.yaml`

### 10. Manual Configuration (if auto-detect fails)
- [ ] Name: `throne-companions-backend`
- [ ] Environment: `Python`
- [ ] Build Command: 
  ```
  pip install -r requirements.txt && pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
  ```
- [ ] Start Command: 
  ```
  uvicorn server:app --host 0.0.0.0 --port $PORT
  ```
- [ ] Plan: Free (or your preferred plan)

### 11. Add Environment Variables in Render
Go to Environment tab and add:
- [ ] `MONGO_URL` = `<your-mongodb-atlas-connection-string>`
- [ ] `JWT_SECRET` = `<generate-random-secret-key>`
- [ ] `EMERGENT_LLM_KEY` = `<your-emergent-llm-key>`
- [ ] `FREE_TIER_MESSAGE_LIMIT` = `20`
- [ ] `CORS_ORIGINS` = `*` (or specific origin)
- [ ] Optional: `MIXPANEL_TOKEN`, `SENDGRID_API_KEY`, `ADMIN_EMAIL`

### 12. Deploy
- [ ] Click "Create Web Service"
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Check logs for any errors

## Post-Deployment Verification

### 13. Test Deployment
- [ ] Access your Render service URL
- [ ] Test health endpoint: `GET https://your-service.onrender.com/`
- [ ] Test API documentation: `GET https://your-service.onrender.com/docs`
- [ ] Test authentication endpoint: `POST /api/auth/register`
- [ ] Test chat endpoint: `POST /api/chat`

### 14. Monitor
- [ ] Check Render logs for any errors
- [ ] Monitor MongoDB connections
- [ ] Verify LLM API calls are working
- [ ] Test message limit for free tier users

## Common Issues and Solutions

### Issue: emergentintegrations not found
**Solution**: Verify build command includes custom package index:
```bash
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### Issue: MongoDB connection timeout
**Solution**: 
1. Whitelist all IPs (0.0.0.0/0) in MongoDB Atlas
2. Verify connection string is correct
3. Check database user permissions

### Issue: Port binding error
**Solution**: Ensure start command uses `$PORT` variable, not hardcoded port

### Issue: CORS errors
**Solution**: Set `CORS_ORIGINS` environment variable to your frontend URL or `*`

## Security Review

- [ ] No sensitive data in code
- [ ] `.env` file is gitignored (not pushed to GitHub)
- [ ] All secrets are in Render environment variables
- [ ] MongoDB uses strong password
- [ ] JWT secret is random and secure
- [ ] Repository is private (if contains proprietary code)

## Success Criteria

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ Service starts and stays healthy
- ✅ API documentation loads at `/docs`
- ✅ User registration works
- ✅ Chat endpoint returns AI responses
- ✅ MongoDB connections are stable
- ✅ No critical errors in logs

---

## Quick Reference Commands

### Git Commands
```bash
cd /app/backend_extracted
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/throne-companions-backend.git
git branch -M main
git push -u origin main
```

### Update Deployment
```bash
git add .
git commit -m "Update description"
git push origin main
```

### Check Python Dependencies
```bash
pip list | grep emergentintegrations
```

### Test Local Server
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

---

**Need Help?**
- Check `README.md` for detailed documentation
- Check `GITHUB_DEPLOYMENT.md` for GitHub setup
- Review Render logs in dashboard
- Verify all environment variables are set correctly
