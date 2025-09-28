# Quick Render.com Deployment Guide

## Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Connect your GitHub repository

## Step 2: Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial staging deployment"
git remote add origin https://github.com/YOUR-USERNAME/throne-companions.git
git push -u origin main
```

## Step 3: Deploy on Render
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: throne-companions-staging
   - **Root Directory**: /
   - **Build Command**: 
     ```
     cd frontend && yarn install && yarn build && cd ../backend && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```
     cd backend && python server.py
     ```

## Step 4: Environment Variables
Add these in Render dashboard:
- `NODE_ENV` = `production`
- `REACT_APP_BACKEND_URL` = `https://throne-companions-staging.onrender.com`
- `MONGO_URL` = `mongodb://mongo:27017/throne_companions`
- `DB_NAME` = `throne_companions`
- `EMERGENT_LLM_KEY` = `your_emergent_key`
- `JWT_SECRET` = `your_jwt_secret`
- `ADMIN_EMAILS` = `admin@thronecompanions.com,Rjohnson801915@gmail.com`

## Step 5: Deploy MongoDB
1. Create new "Private Service"
2. Use Docker image: `mongo:5.0`
3. Add persistent disk for `/data/db`

## Step 6: Access Admin Panel
**URL**: `https://throne-companions-staging.onrender.com/admin`
**Email**: `Rjohnson801915@gmail.com`

## Alternative: Railway Deployment
1. Go to https://railway.app
2. Deploy from GitHub
3. Add MongoDB service
4. Same environment variables