# Throne Companions - Staging Deployment Guide

## Overview
This guide covers deploying the Throne Companions app to a staging environment with email authentication for admin access.

## Prerequisites
1. **Email Service Setup**: Either SendGrid account OR Gmail/SMTP setup
2. **Mixpanel Account**: For analytics tracking
3. **Staging Server**: Cloud instance (AWS, DigitalOcean, etc.)

## Environment Configuration

### 1. Email Service Setup

#### Option A: SendGrid (Recommended)
1. Create account at https://sendgrid.com
2. Verify domain or use single sender verification
3. Generate API key with Mail Send permissions
4. Add to environment: `SENDGRID_API_KEY=your_key_here`

#### Option B: Gmail SMTP
1. Enable 2-factor authentication on Gmail
2. Generate app password: Account → Security → App passwords
3. Configure environment:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

### 2. Mixpanel Setup
1. Create project at https://mixpanel.com
2. Copy project token
3. Add to environment: `REACT_APP_MIXPANEL_TOKEN=your_token`

## Deployment Steps

### 1. Server Setup
```bash
# Clone or upload app files to server
git clone your_repo_url /var/www/throne-companions
cd /var/www/throne-companions

# Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && yarn install
```

### 2. Environment Configuration
```bash
# Copy staging environment file
cp .env.staging backend/.env
cp .env.staging frontend/.env

# Edit with your actual credentials
nano backend/.env
nano frontend/.env
```

### 3. Database Setup
```bash
# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify connection
mongo --eval "db.runCommand({connectionStatus : 1})"
```

### 4. Build and Start Services
```bash
# Build frontend
cd frontend && yarn build

# Start backend
cd ../backend && python server.py

# Serve frontend (use nginx in production)
cd ../frontend && yarn start
```

### 5. Admin Access Testing

#### Test Email Authentication:
1. Navigate to `http://your-staging-domain/admin`
2. Enter admin email (one from ADMIN_EMAILS)
3. Click "Send Access Code"
4. Check email for 6-digit code
5. Enter code to access admin dashboard

#### Test All Tier Behaviors:
1. In admin dashboard, select tier (Novice/Apprentice/Regent/Sovereign)
2. Click "Test [Tier] Behavior"
3. Verify response differences across tiers
4. Check memory access, conversation flow, error logging

## Production Deployment Considerations

### Security
- Use HTTPS/SSL certificates
- Configure proper firewall rules
- Set up domain with DNS
- Use secure JWT secrets
- Enable rate limiting

### Performance
- Use Redis for session storage
- Configure nginx reverse proxy
- Set up MongoDB replica set
- Enable compression and caching

### Monitoring
- Set up error tracking (Sentry)
- Configure uptime monitoring
- Enable application logs
- Set up backup procedures

## Admin Access
Once deployed, admin access is available at:
- **URL**: `https://your-domain/admin`
- **Authorized Emails**: Listed in ADMIN_EMAILS environment variable
- **Access Code**: Delivered via configured email service

## Troubleshooting

### Email Issues
- Check SENDGRID_API_KEY or SMTP credentials
- Verify sender email is authenticated
- Check spam folder for access codes
- Review email service logs

### Tier Testing Issues
- Verify JWT token is valid
- Check admin authorization
- Review backend error logs
- Confirm tier override system is working

### Database Issues
- Verify MongoDB connection
- Check database permissions
- Review connection string format
- Ensure collections are created

## Support
For deployment assistance, review logs in:
- Backend: `/var/log/supervisor/backend.err.log`
- Frontend: Browser console
- MongoDB: `/var/log/mongodb/mongod.log`