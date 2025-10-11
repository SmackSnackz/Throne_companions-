# Throne Companions - Backend API

Standalone FastAPI backend for the Throne Companions AI application. This backend is optimized for deployment on Render.com.

## Features

- FastAPI-based REST API
- AI-powered conversations using GPT-4o-mini
- Multi-tier subscription system (Novice, Apprentice, Regent, Sovereign)
- Memory system with chat history and summarization
- Mixpanel analytics integration
- Email authentication for admin access
- Comprehensive error logging and monitoring

## Tech Stack

- **Framework**: FastAPI (Python 3.11)
- **Database**: MongoDB
- **AI Integration**: emergentintegrations (GPT-4o-mini)
- **Analytics**: Mixpanel
- **Email**: SendGrid
- **Authentication**: JWT

## Prerequisites

- Python 3.11+
- MongoDB instance (local or cloud)
- Emergent LLM API key
- Mixpanel project token (optional)
- SendGrid API key (optional, for admin email auth)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database
MONGO_URL=mongodb://localhost:27017/throne_companions

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here

# AI Integration
EMERGENT_LLM_KEY=your-emergent-llm-key

# Analytics (Optional)
MIXPANEL_TOKEN=your-mixpanel-token

# Email Service (Optional)
SENDGRID_API_KEY=your-sendgrid-api-key
ADMIN_EMAIL=admin@example.com
```

## Local Development

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd backend_extracted
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the server**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

The API will be available at `http://localhost:8001`

## Deployment on Render.com

### Method 1: Using render.yaml (Recommended)

1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create New Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables**:
   - Add all required environment variables from the Render dashboard
   - Make sure to add:
     - `MONGO_URL`
     - `JWT_SECRET_KEY`
     - `EMERGENT_LLM_KEY`
     - `MIXPANEL_TOKEN` (optional)
     - `SENDGRID_API_KEY` (optional)
     - `ADMIN_EMAIL` (optional)

4. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy your application

### Method 2: Using Dockerfile

1. **Push code to GitHub** (same as above)

2. **Create New Web Service**:
   - Environment: Docker
   - Build Command: (leave empty, uses Dockerfile)
   - Start Command: (leave empty, uses Dockerfile CMD)

3. **Configure Environment Variables** (same as Method 1)

### Important Notes for Render Deployment

- **emergentintegrations Package**: The deployment includes a custom build command that installs `emergentintegrations` from a custom package index. This is crucial and must not be removed.
  
- **Build Command**:
  ```bash
  pip install -r requirements.txt && pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
  ```

- **Port Configuration**: Render automatically sets the `PORT` environment variable. The application is configured to listen on port 8001.

- **MongoDB**: Use MongoDB Atlas or another cloud MongoDB service. Update `MONGO_URL` accordingly.

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Verify JWT token

### Chat
- `POST /api/chat` - Send message and get AI response
- `GET /api/chat/history` - Get user's chat history
- `POST /api/chat/new-session` - Start new chat session

### Admin
- `POST /api/admin/request-access` - Request admin access code
- `POST /api/admin/verify-access` - Verify admin access code
- `GET /api/admin/metrics` - Get system metrics
- `GET /api/admin/errors` - Get error logs

### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `POST /api/user/tier` - Update subscription tier

## Project Structure

```
backend_extracted/
├── config/                      # Configuration files
│   ├── prompt_system.config.json
│   ├── solicitation.config.json
│   ├── tier_prompts.config.json
│   └── tone_anchors.config.json
├── analytics.py                 # Analytics utilities
├── auth_utils.py                # JWT authentication
├── content_packs.py             # Content pack management
├── dashboard.py                 # Admin dashboard logic
├── email_auth_service.py        # Email authentication
├── error_logger.py              # Error logging system
├── focused_expansion_system.py  # "Go Deeper" functionality
├── master_prompt_system.py      # Core AI behavior
├── memory_system.py             # Chat memory management
├── metrics_calculator.py        # Metrics calculation
├── mixpanel_events.py           # Mixpanel event definitions
├── mixpanel_tracker.py          # Mixpanel tracking
├── models.py                    # Pydantic models
├── server.py                    # Main FastAPI application
├── solicitation.py              # Prompt solicitation
├── temp_admin_override.py       # Admin override logic
├── tier_configs.py              # Tier configurations
├── tier_prompt_manager.py       # Tier prompt management
├── tier_system.py               # Tier system logic
├── tone_anchor_system.py        # Tone anchoring
├── unified_prompt_system.py     # Unified prompt system
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── render.yaml                  # Render.com configuration
└── README.md                    # This file
```

## Troubleshooting

### emergentintegrations Import Error

If you encounter `ModuleNotFoundError: No module named 'emergentintegrations'`, ensure you're installing from the custom package index:

```bash
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### MongoDB Connection Issues

- Verify `MONGO_URL` is correctly set
- For MongoDB Atlas, ensure your IP is whitelisted
- Check database user permissions

### Port Already in Use

If port 8001 is already in use, specify a different port:

```bash
uvicorn server:app --host 0.0.0.0 --port 8002
```

## Support

For issues or questions, please contact the development team or open an issue in the repository.

## License

Proprietary - All rights reserved
