# GitHub Setup and Deployment Guide

This guide will help you push the Throne Companions backend to GitHub and deploy it on Render.com.

## Step 1: Initialize Git Repository

Navigate to the backend_extracted directory and initialize Git:

```bash
cd /app/backend_extracted
git init
```

## Step 2: Configure Git (If Not Already Done)

Set your Git username and email:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Step 3: Add Files to Git

Add all files to the repository:

```bash
git add .
```

## Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: Throne Companions Backend for Render deployment"
```

## Step 5: Create GitHub Repository

1. Go to [GitHub](https://github.com) and log in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name it: `throne-companions-backend`
5. Keep it **Private** (recommended for production code)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 6: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

### For a new repository:

```bash
git remote add origin https://github.com/YOUR_USERNAME/throne-companions-backend.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### If you encounter authentication issues:

GitHub no longer supports password authentication. You have two options:

#### Option A: Using Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Throne Companions Deployment"
4. Select scopes: `repo` (all repo permissions)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

When pushing, use:
```bash
git push https://YOUR_TOKEN@github.com/YOUR_USERNAME/throne-companions-backend.git main
```

Or set up credential helper:
```bash
git config --global credential.helper store
git push -u origin main
# Enter username and paste token as password
```

#### Option B: Using SSH

1. Generate SSH key:
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```

2. Add SSH key to GitHub:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copy the output and add it to GitHub (Settings → SSH and GPG keys → New SSH key)

3. Change remote URL to SSH:
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/throne-companions-backend.git
   git push -u origin main
   ```

## Step 7: Verify Push

Check your GitHub repository in the browser to ensure all files are uploaded.

## Step 8: Deploy on Render.com

### Method 1: Automatic Deployment (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Click "Connect GitHub" (authorize if needed)
4. Select your `throne-companions-backend` repository
5. Render will detect `render.yaml` automatically

### Method 2: Manual Configuration

If automatic detection doesn't work:

1. **Name**: throne-companions-backend
2. **Environment**: Python
3. **Build Command**:
   ```bash
   pip install -r requirements.txt && pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
   ```
4. **Start Command**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port $PORT
   ```
5. **Plan**: Free (or your preferred plan)

### Step 9: Configure Environment Variables on Render

Add these environment variables in Render Dashboard:

| Key | Value | Required |
|-----|-------|----------|
| `MONGO_URL` | Your MongoDB connection string | ✅ Yes |
| `JWT_SECRET` | Your JWT secret key | ✅ Yes |
| `EMERGENT_LLM_KEY` | Your Emergent LLM API key | ✅ Yes |
| `MIXPANEL_TOKEN` | Your Mixpanel token | ⚠️ Optional |
| `SENDGRID_API_KEY` | Your SendGrid API key | ⚠️ Optional |
| `ADMIN_EMAIL` | Admin email address | ⚠️ Optional |
| `FREE_TIER_MESSAGE_LIMIT` | 20 | ⚠️ Optional |
| `CORS_ORIGINS` | * | ⚠️ Optional |

**Important**: 
- For MongoDB, use MongoDB Atlas (free tier available)
- Never commit `.env` file to GitHub (already in .gitignore)

## Step 10: Deploy

Click "Create Web Service" and wait for deployment to complete.

## Updating Your Deployment

After making changes to your code:

```bash
cd /app/backend_extracted
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically detect the push and redeploy your application.

## Troubleshooting

### Issue: "emergentintegrations not found"

**Solution**: Verify your build command includes:
```bash
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### Issue: "MongoDB connection failed"

**Solutions**:
1. Verify `MONGO_URL` is correct in Render environment variables
2. If using MongoDB Atlas:
   - Whitelist all IPs (0.0.0.0/0) in Network Access
   - Verify database user has correct permissions

### Issue: "Port binding error"

**Solution**: Ensure start command uses `$PORT` variable:
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Issue: "Push rejected - authentication failed"

**Solution**: Use Personal Access Token instead of password (see Step 6).

## Maintenance

### View Logs
Go to Render Dashboard → Your Service → Logs

### Manual Deploy
Go to Render Dashboard → Your Service → Manual Deploy → Deploy latest commit

### Environment Variables
Go to Render Dashboard → Your Service → Environment → Add/Edit variables

## Security Checklist

- ✅ `.env` file is in `.gitignore`
- ✅ No API keys hardcoded in code
- ✅ Repository is private (recommended)
- ✅ Environment variables set in Render dashboard
- ✅ MongoDB IP whitelist configured
- ✅ CORS origins properly configured

## Support

For deployment issues:
- Check Render logs for error messages
- Verify all environment variables are set
- Ensure MongoDB is accessible
- Verify emergentintegrations installation

For application issues:
- Check server logs in Render dashboard
- Test endpoints using provided API documentation
- Verify LLM key is valid and has credits

---

**Next Steps After Deployment:**
1. Test your API endpoints
2. Connect your frontend to the deployed backend URL
3. Monitor logs for any issues
4. Set up custom domain (optional)
