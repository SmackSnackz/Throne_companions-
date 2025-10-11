# Throne Companions Backend

A FastAPI backend for the Throne Companions AI chat application.

## Features

- **AI Conversations**: GPT-4o-mini powered chat with distinct companion personalities
- **Tier System**: Four subscription tiers (Novice, Apprentice, Regent, Sovereign) with server-side gating
- **Memory System**: Chat history storage and memory summarization with tier-based retention
- **Authentication**: JWT-based auth with admin bypass functionality
- **Analytics**: Mixpanel event tracking integration
- **Advanced Prompting**: Solicitation Layer, Distress Mode Anchoring, and Tone Anchors

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB
- Redis (optional, fallback to in-memory)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd throne-companions-backend
```

2. Install dependencies:
```bash
pip install --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the server:
```bash
python server.py
```

The API will be available at `http://localhost:8001`

## Environment Variables

Create a `.env` file with the following variables:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=throne_companions
CORS_ORIGINS=*
EMERGENT_LLM_KEY=your_emergent_llm_key_here
JWT_SECRET=your_jwt_secret_here
ADMIN_EMAILS=admin@example.com,admin2@example.com
FREE_TIER_MESSAGE_LIMIT=20
REDIS_URL=redis://localhost:6379
```

## API Endpoints

### Authentication
- `POST /api/auth/create-token` - Create JWT token
- `GET /api/auth/verify` - Verify JWT token

### Chat
- `POST /api/chat` - Send message to AI companion
- `POST /api/session/complete` - Complete chat session and generate memory summary

### Companions
- `GET /api/companions` - List all companions
- `GET /api/companions/{id}` - Get companion details
- `GET /api/companions/{id}/messages` - Get companion chat history
- `POST /api/companions/{id}/messages` - Send message to companion

### Tiers
- `GET /api/tiers` - Get subscription tier information

### Analytics (Mixpanel)
- `POST /api/events/companion_selected` - Track companion selection
- `POST /api/events/tier_selected` - Track tier selection
- `POST /api/events/upgrade_clicked` - Track upgrade clicks
- `GET /api/events/mock` - Get mock event data (development)
- `GET /api/events/stats` - Get event statistics (development)

### Admin
- `POST /api/email-auth/send-code` - Send admin authentication code
- `POST /api/email-auth/verify-code` - Verify admin authentication code
- `GET /api/admin/dashboard` - Admin dashboard data
- `GET /api/admin/error-logs` - Get error logs
- `POST /api/admin/temp-override` - Temporary admin tier override

## Architecture

### Core Components

- **server.py** - Main FastAPI application
- **models.py** - Pydantic data models
- **auth_utils.py** - JWT authentication utilities
- **memory_system.py** - Chat memory management
- **mixpanel_tracker.py** - Analytics tracking

### Prompt Systems

- **master_prompt_system.py** - Core AI behavior definitions
- **solicitation.py** - Proactive question system
- **tone_anchor_system.py** - Personality grounding
- **unified_prompt_system.py** - System orchestration

### Configuration

JSON configuration files in `config/` directory:
- `prompt_system.config.json` - System prompts
- `solicitation.config.json` - Solicitation settings
- `tier_prompts.config.json` - Tier-specific prompts
- `tone_anchors.config.json` - Personality anchors

## Development

### Running with Hot Reload

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Testing

```bash
# Test authentication
curl -X POST http://localhost:8001/api/auth/create-token \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","role":"user"}'

# Test chat
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"companion_id":"sophia","message":"Hello!","session_id":"test-session"}'
```

## Deployment

### Render.com

1. Fork this repository
2. Connect to Render.com
3. Use the included `render.yaml` for configuration
4. Set environment variables in Render dashboard

### Docker

```bash
docker build -t throne-companions-backend .
docker run -p 8001:8001 --env-file .env throne-companions-backend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

Private - All rights reserved
