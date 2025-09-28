#!/bin/bash
# One-click deployment script for Throne Companions

echo "🚀 Throne Companions - Staging Deployment"
echo "=========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial deployment commit"
fi

echo "📋 Deployment Options:"
echo "1. Render.com (Recommended)"
echo "2. Railway.app"
echo "3. DigitalOcean App Platform"
echo "4. Manual VPS Setup"

read -p "Choose deployment option (1-4): " choice

case $choice in
    1)
        echo "🎯 Deploying to Render.com..."
        echo "1. Push code to GitHub first:"
        echo "   git remote add origin https://github.com/YOUR-USERNAME/throne-companions.git"
        echo "   git push -u origin main"
        echo ""
        echo "2. Then go to https://render.com and deploy from GitHub"
        echo "3. Your admin URL will be: https://throne-companions-staging.onrender.com/admin"
        ;;
    2)
        echo "🚂 Deploying to Railway..."
        echo "1. Go to https://railway.app"
        echo "2. Deploy from GitHub repo"
        echo "3. Add MongoDB service"
        echo "4. Your admin URL will be: https://throne-companions-staging.up.railway.app/admin"
        ;;
    3)
        echo "🌊 Deploying to DigitalOcean..."
        echo "1. Go to https://cloud.digitalocean.com/apps"
        echo "2. Create new app from GitHub"
        echo "3. Add managed MongoDB database"
        echo "4. Your admin URL will be: https://throne-companions-staging.ondigitalocean.app/admin"
        ;;
    4)
        echo "🖥️  Manual VPS deployment..."
        echo "1. Set up Ubuntu server"
        echo "2. Install Node.js, Python, MongoDB"
        echo "3. Clone repo and run setup scripts"
        ;;
esac

echo ""
echo "✅ Admin Email Whitelisted: Rjohnson801915@gmail.com"
echo "🔐 Access: Email → Get Code → Verify → Admin Dashboard"
echo "🎯 Features: Tier Testing, Error Logs, Stats Dashboard"