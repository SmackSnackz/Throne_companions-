# Deployment Guide

This document provides comprehensive deployment instructions for the Throne Companions Backend.

## Quick Deployment Options

### 1. Render.com (Recommended)

#### Prerequisites
- GitHub account
- Render.com account
- Emergent LLM API key

#### Steps

1. **Fork/Upload this repository to GitHub**

2. **Create a Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" > "Web Service"
   - Connect your GitHub repository

3. **Configure the service:**
   - **Environment**: Python 3
   - **Build Command**: 
     ```bash
     pip install --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     python server.py
     ```

4. **Set Environment Variables:**
   ```
   MONGO_URL=mongodb://localhost:27017/throne_companions
   DB_NAME=throne_companions
   CORS_ORIGINS=*
   EMERGENT_LLM_KEY=your_actual_key_here
   JWT_SECRET=your_jwt_secret_here
   ADMIN_EMAILS=admin@example.com,admin2@example.com
   FREE_TIER_MESSAGE_LIMIT=20
   PORT=8001
   ```

5. **Deploy**: Click "Create Web Service"

#### Using render.yaml (Automated)

1. Ensure `render.yaml` is in your repository root
2. Update the environment variables in `render.yaml`
3. Deploy: Render will automatically detect and use the configuration

### 2. Docker Deployment

#### Local Docker

```bash
# Build the image
docker build -t throne-companions-backend .

# Run with environment variables
docker run -p 8001:8001 \
  -e MONGO_URL=mongodb://host.docker.internal:27017/throne_companions \
  -e EMERGENT_LLM_KEY=your_key_here \
  -e JWT_SECRET=your_secret_here \
  throne-companions-backend
```

#### Docker Compose (with MongoDB)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### 3. VPS/Server Deployment

#### Prerequisites
- Ubuntu 20.04+ (or similar Linux distribution)
- Python 3.11+
- MongoDB
- Nginx (optional, for reverse proxy)

#### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd throne-companions-backend
   ```

2. **Install Python dependencies:**
   ```bash
   ./install.sh
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your configuration
   ```

4. **Start the service:**
   ```bash
   ./start.sh
   ```

#### Systemd Service (Production)

Create `/etc/systemd/system/throne-companions.service`:

```ini
[Unit]
Description=Throne Companions Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/throne-companions-backend
Environment=PATH=/path/to/throne-companions-backend/venv/bin
ExecStart=/path/to/throne-companions-backend/venv/bin/python server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable throne-companions
sudo systemctl start throne-companions
```

## Database Setup

### MongoDB Configuration

#### Local MongoDB
```bash
# Install MongoDB (Ubuntu)
sudo apt-get install -y mongodb

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Create database
mongo
> use throne_companions
> exit
```

#### MongoDB Atlas (Cloud)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster
3. Get connection string
4. Update `MONGO_URL` in your environment variables

### Required Collections
The application will automatically create these collections:
- `chat_messages` - Chat conversation history
- `chat_history` - Detailed chat logs for memory system
- `memory_summary` - AI-generated conversation summaries
- `mixpanel_events` - Analytics events (mock mode)
- `content_events` - Content pack usage tracking
- `error_logs` - Application error logs

## Environment Variables Reference

### Required Variables
- `MONGO_URL` - MongoDB connection string
- `EMERGENT_LLM_KEY` - API key for AI functionality
- `JWT_SECRET` - Secret for JWT token generation

### Optional Variables
- `DB_NAME` - Database name (default: throne_companions)
- `CORS_ORIGINS` - Allowed CORS origins (default: *)
- `ADMIN_EMAILS` - Comma-separated admin emails
- `FREE_TIER_MESSAGE_LIMIT` - Free tier message limit (default: 20)
- `REDIS_URL` - Redis connection string (optional, uses in-memory fallback)
- `PORT` - Server port (default: 8001)

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'emergentintegrations'
**Solution:**
```bash
pip install --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ emergentintegrations
```

#### 2. MongoDB Connection Failed
- Verify MongoDB is running: `sudo systemctl status mongodb`
- Check connection string format: `mongodb://host:port/database`
- For MongoDB Atlas, ensure IP whitelist includes your server

#### 3. Port Already in Use
- Change the PORT environment variable
- Kill existing processes: `sudo lsof -t -i:8001 | xargs sudo kill -9`

#### 4. Redis Connection Failed (Non-critical)
- The app will fallback to in-memory storage
- Install Redis: `sudo apt-get install redis-server`
- Or remove REDIS_URL from environment variables

#### 5. AI Responses Not Working
- Verify `EMERGENT_LLM_KEY` is correctly set
- Check API key permissions and quotas
- Review server logs for API errors

### Logs and Monitoring

#### View Logs
```bash
# Direct run
tail -f server.log

# Systemd service
sudo journalctl -u throne-companions -f

# Docker
docker logs -f container_name
```

#### Health Check Endpoint
```bash
curl http://localhost:8001/api/companions
```

#### API Documentation
Access interactive API docs at: `http://your-domain:8001/docs`

## Performance Optimization

### Production Settings
- Use a production WSGI server (included in Docker setup)
- Configure MongoDB with appropriate indexes
- Set up Redis for better caching
- Use a reverse proxy (Nginx) for SSL termination
- Enable MongoDB replica set for high availability

### Scaling
- The application is stateless and can be horizontally scaled
- Use a load balancer to distribute traffic
- Consider MongoDB sharding for large datasets
- Implement Redis Cluster for distributed caching

## Security Considerations

### Production Checklist
- [ ] Use strong, unique JWT_SECRET
- [ ] Configure specific CORS origins (not *)
- [ ] Enable MongoDB authentication
- [ ] Use SSL/TLS certificates
- [ ] Regularly rotate API keys
- [ ] Monitor for unusual API usage patterns
- [ ] Keep dependencies updated

### Firewall Rules
```bash
# Allow only necessary ports
sudo ufw allow 22   # SSH
sudo ufw allow 80   # HTTP
sudo ufw allow 443  # HTTPS
sudo ufw deny 8001  # Block direct backend access
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
mongodump --db throne_companions --out /backup/$(date +%Y%m%d)

# Restore backup
mongorestore --db throne_companions /backup/20240101/throne_companions
```

### Configuration Backup
- Backup `.env` file
- Document custom configuration changes
- Version control all deployment scripts

---

For additional support or questions, please refer to the main README.md or contact the development team.