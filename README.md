# SINCE-AI-SANDVIK-CHALLENGE

An intelligent Microsoft Teams bot that monitors channel messages, classifies spare parts inquiries using a hybrid AI pipeline, and provides proactive notifications with RAG-based spare parts matching.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Detailed Setup Instructions](#detailed-setup-instructions)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Team Members](#team-members)

## 🎯 Overview

This project consists of three main services working together:

1. **Teams Agent** - A FastAPI-based bot that listens to Microsoft Teams channel messages, classifies them using the classifier server, and sends intelligent notifications with spare parts matching
2. **Classifier Server** - A hybrid AI classification service that uses a fine-tuned XLM-RoBERTa model with LLM fallback for identifying spare parts inquiries
3. **Teams Demo** - A SvelteKit frontend application for visualizing and interacting with the Teams bot

### Key Features

- **Intelligent Message Classification**: Hybrid AI pipeline combining local transformer models with LLM reasoning
- **Spare Parts Matching**: RAG-based search through spare parts catalog using semantic similarity
- **Proactive Notifications**: Sends adaptive cards to configured users when spare parts inquiries are detected
- **Deep Links**: Cards include direct links to original channel messages
- **Keyword Filtering**: Optional keyword-based filtering for notifications
- **Cost-Efficient**: ~75% reduction in LLM API costs compared to pure LLM solutions

## 🏗️ Architecture

```
┌─────────────────┐
│  Microsoft Teams│
│     Channels    │
└────────┬────────┘
         │
         │ Webhook POST /api/messages
         ▼
┌─────────────────┐
│  Teams Agent    │◄─────┐
│  (FastAPI)      │      │
│  Port: 3978     │      │
└────────┬────────┘      │
         │               │
         │ Classify      │ Spare Parts
         │ Request       │ Catalog Search
         ▼               │
┌─────────────────┐      │
│ Classifier      │      │
│ Server          │      │
│ (FastAPI)       │      │
│ Port: 8069      │      │
└─────────────────┘      │
         │               │
         │ Uses          │
         ▼               │
┌─────────────────┐      │
│ Featherless.ai  │      │
│ (LLM API)       │      │
└─────────────────┘      │
         │               │
         │               │
         └───────────────┘
         │
         │ Notification Card
         ▼
┌─────────────────┐
│  Teams Demo     │
│  (SvelteKit)    │
│  Port: 3000     │
└─────────────────┘
```

### Classification Pipeline

1. **Stage 1: Local Model (XLM-RoBERTa-base)**
   - Fast, zero-cost classification
   - Handles ~75-80% of requests
   - Confidence threshold: 0.61

2. **Stage 2: LLM Fallback (Meta-Llama-3.1-8B-Instruct)**
   - Activated when confidence < 0.61
   - Handles ambiguous cases
   - Handles ~20-25% of requests

## 📦 Prerequisites

- **Docker** and **Docker Compose** (recommended for full stack)
- **Python 3.9+** (if running services individually)
- **Node.js 18+** and **npm** (for teams-demo frontend)
- **Featherless.ai API Key** (for LLM fallback)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SINCE-AI-SANDVIK-CHALLENGE
   ```

2. **Create a `.env` file in the root directory:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values (see Environment Variables section)
   ```
   
   **Note:** The `.env.example` file contains a minimal template. You'll need to add additional variables as documented in the [Environment Variables](#environment-variables) section below.
   For a quick start the FEATHERLESS_API_KEY is enough, other variables were used only for development etc.
3. **Start all services:**
   ```bash
   docker compose up --build
   ```

4. **Verify services are running:**
   - Teams Agent: http://localhost:3978/health
   - Classifier Server: http://localhost:8069/health
   - Teams Demo: http://localhost:3000

### Option 2: Individual Services

See [Detailed Setup Instructions](#detailed-setup-instructions) below.

## 🔐 Environment Variables

### Root `.env` File (for Docker Compose)

Create a `.env` file in the project root with the following variables:

```bash
# ============================================
# Featherless.ai API Configuration
# ============================================
# Required for LLM fallback in classifier-server and RAG in teams-agent
FEATHERLESS_API_KEY=your-featherless-api-key-here

# ============================================
# Microsoft Teams Bot Configuration
# ============================================
# Azure AD App Registration credentials
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=your-client-id
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=your-client-secret
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=your-tenant-id

# ============================================
# Teams Agent Configuration
# ============================================
# Azure AD Object ID of the user who should receive notifications
TARGET_USER_ID=user-object-id-here

# Optional: Target user tenant ID (usually same as tenant-id above)
TARGET_USER_TENANT_ID=tenant-id

# Optional: Bot ID (usually auto-detected)
BOT_ID=bot-id

# Optional: Notification keywords (comma-separated)
# Only messages containing these keywords will trigger notifications
# Leave empty to send notifications for all messages
# Example: NOTIFICATION_KEYWORDS=urgent,important,help
NOTIFICATION_KEYWORDS=

# ============================================
# Service Endpoints (for Docker Compose)
# ============================================
# Classifier server port (default: 8069)
CLASSIFIER_PORT=8069

# Classifier endpoint URL (default: http://classifier-server:8069/classify)
# For Docker Compose, use internal service name
CLASSIFIER_ENDPOINT=http://classifier-server:8069/classify
```

### Teams Agent Environment Variables

If running teams-agent individually, create `apps/teams-agent/.env` based on `apps/teams-agent/env.TEMPLATE`:

```bash
# Microsoft Teams Bot Configuration
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=client-id
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=client-secret
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=tenant-id

# Target user configuration
TARGET_USER_ID=user-object-id-here
TARGET_USER_TENANT_ID=tenant-id
BOT_ID=bot-id

# Notification keywords (optional)
NOTIFICATION_KEYWORDS=

# Service endpoints
WEBHOOK_URL=http://localhost:3000/api/webhook
CLASSIFIER_ENDPOINT=http://localhost:8069/classify

# Featherless.ai API (for RAG search)
FEATHERLESS_API_KEY=your-featherless-api-key-here
FEATHERLESS_MODEL=Qwen/Qwen2.5-7B-Instruct

# Spare parts catalog path (optional, defaults to tests/data/sku_register_full.csv)
SPARE_PARTS_CSV_PATH=tests/data/sku_register_full.csv

# Server configuration (optional)
HOST=0.0.0.0
PORT=3978
LOG_LEVEL=DEBUG
LOG_FILE=agent.log
```

### Classifier Server Environment Variables

If running classifier-server individually, create `apps/classifier-server/.env`:

```bash
# Featherless.ai API Key (required for LLM fallback)
FEATHERLESS_API_KEY=your-featherless-api-key-here

# Server port (optional, default: 8069)
CLASSIFIER_PORT=8069
```

### Teams Demo Environment Variables

If running teams-demo individually, create `apps/teams-demo/.env`:

```bash
# Teams Agent URL
TEAMS_AGENT_URL=http://localhost:3978/api/messages

# Node environment
NODE_ENV=production
```

## 📖 Detailed Setup Instructions

### 1. Teams Agent Setup

**Location:** `apps/teams-agent/`

**Steps:**

1. **Install dependencies:**
   ```bash
   cd apps/teams-agent
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp env.TEMPLATE .env
   # Edit .env with your configuration
   ```

3. **Run the service:**
   ```bash
   # Option A: Using app.py
   python app.py
   
   # Option B: Using uvicorn directly
   uvicorn src.main:app --host 0.0.0.0 --port 3978
   ```

4. **Verify it's running:**
   ```bash
   curl http://localhost:3978/health
   ```

**Docker (individual):**
```bash
cd apps/teams-agent
docker build -t teams-agent -f DOCKERFILE .
docker run -p 3978:3978 --env-file .env teams-agent
```

### 2. Classifier Server Setup

**Location:** `apps/classifier-server/`

**Steps:**

1. **Download the trained model:**
   ```bash
   cd apps/classifier-server
   python download_model.py
   ```
   This downloads the fine-tuned XLM-RoBERTa model to `./spare_parts_model/`

2. **Install dependencies:**
   ```bash
   pip install -r requirements-server.txt
   ```

3. **Configure environment:**
   ```bash
   # Create .env file
   echo "FEATHERLESS_API_KEY=your-key-here" > .env
   echo "CLASSIFIER_PORT=8069" >> .env
   ```

4. **Run the service:**
   ```bash
   python server.py
   # Or using uvicorn:
   uvicorn server:app --host 0.0.0.0 --port 8069
   ```

5. **Verify it's running:**
   ```bash
   curl http://localhost:8069/health
   ```

**Docker (individual):**
```bash
cd apps/classifier-server
docker build -t classifier-server -f Dockerfile .
docker run -p 8069:8069 --env-file .env classifier-server
```

### 3. Teams Demo Setup

**Location:** `apps/teams-demo/`

**Steps:**

1. **Install dependencies:**
   ```bash
   cd apps/teams-demo
   npm install
   ```

2. **Configure environment:**
   ```bash
   # Create .env file
   echo "TEAMS_AGENT_URL=http://localhost:3978/api/messages" > .env
   ```

3. **Run in development mode:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   npm run preview
   ```

**Docker (individual):**
```bash
cd apps/teams-demo
docker build -t teams-demo -f DOCKERFILE .
docker run -p 3000:3000 --env-file .env teams-demo
```

### 4. Microsoft Teams Bot Registration

1. **Create Azure AD App Registration:**
   - Go to Azure Portal → Azure Active Directory → App registrations
   - Create a new registration
   - Note the **Application (client) ID** and **Directory (tenant) ID**

2. **Create Client Secret:**
   - Go to Certificates & secrets
   - Create a new client secret
   - Copy the secret value (you won't see it again)

3. **Configure Bot Framework:**
   - Go to [Azure Bot Service](https://portal.azure.com/#blade/Microsoft_Azure_BotService/BotServicesBlade)
   - Create a new bot or use existing
   - Configure messaging endpoint: `https://your-domain.com/api/messages` (or use ngrok for local development)

4. **Get Target User Object ID:**
   - Go to Azure Portal → Azure Active Directory → Users
   - Find the target user
   - Copy the **Object ID**

5. **Set Environment Variables:**
   - Use the values from steps above in your `.env` file

### 5. Using ngrok for Local Development

For local development, you'll need to expose your Teams Agent to the internet:

```bash
# Install ngrok
# macOS: brew install ngrok
# Or download from https://ngrok.com/

# Expose Teams Agent
ngrok http 3978

# Use the HTTPS URL in your Bot Framework messaging endpoint
# Example: https://abc123.ngrok.io/api/messages
```

## 🔌 API Endpoints

### Teams Agent (`http://localhost:3978`)

- **POST `/api/messages`** - Main webhook endpoint for Teams messages
  - Accepts: Teams MessageActionsPayload or Activity object
  - Returns: Activity response object

- **GET `/api/messages`** - Health check
  - Returns: `{"status": "ok"}`

- **GET `/health`** - Health check
  - Returns: `{"status": "healthy"}`

- **GET `/`** - Root endpoint
  - Returns: `{"status": "ok", "service": "Teams Agent"}`

### Classifier Server (`http://localhost:8069`)

- **POST `/classify`** - Classify a message
  - Request:
    ```json
    {
      "message": "Need a replacement gasket for model TX900"
    }
    ```
  - Response:
    ```json
    {
      "is_parts_inquiry": true,
      "confidence": 0.85,
      "method": "model"
    }
    ```

- **GET `/health`** - Health check
  - Returns: Model status and API key configuration

- **GET `/debug-env`** - Debug environment variables
  - Returns: Environment variable status (for troubleshooting)

### Teams Demo (`http://localhost:3000`)

- **GET `/`** - Main demo interface
- **POST `/api/webhook`** - Receives notification cards from Teams Agent
- **POST `/api/bot`** - Forwards messages to Teams Agent

## 📁 Project Structure

```
SINCE-AI-SANDVIK-CHALLENGE/
├── compose.yaml                 # Docker Compose configuration
├── .env.example                 # Root environment template
├── README.md                    # This file
│
├── apps/
│   ├── teams-agent/            # Teams bot service
│   │   ├── src/
│   │   │   ├── agent.py        # Main agent logic
│   │   │   ├── card_messages.py # Card creation
│   │   │   ├── models.py       # Pydantic models
│   │   │   ├── start_server.py # FastAPI setup
│   │   │   └── main.py         # Entry point
│   │   ├── tests/              # Integration tests
│   │   ├── env.TEMPLATE        # Environment template
│   │   ├── requirements.txt    # Python dependencies
│   │   └── DOCKERFILE          # Docker configuration
│   │
│   ├── classifier-server/      # Classification service
│   │   ├── server.py           # FastAPI server
│   │   ├── train.py            # Model training script
│   │   ├── download_model.py   # Model download script
│   │   ├── requirements-server.txt
│   │   ├── requirements-train.txt
│   │   ├── Dockerfile
│   │   └── README.md           # Technical overview
│   │
│   └── teams-demo/             # Frontend demo
│       ├── src/
│       │   ├── routes/         # SvelteKit routes
│       │   └── components/     # UI components
│       ├── package.json
│       ├── DOCKERFILE
│       └── README.md
│
└── data/                        # Training/test data
    ├── synthetic_dataset.csv
    └── test.csv
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "FEATHERLESS_API_KEY not found"

**Problem:** Classifier server can't find the API key.

**Solution:**
- Ensure `.env` file exists in the root directory (for Docker Compose) or in the service directory
- Check that `FEATHERLESS_API_KEY` is set correctly
- For Docker Compose, ensure the variable is in the root `.env` file
- Verify with: `curl http://localhost:8069/debug-env`

#### 2. "No conversation reference found"

**Problem:** Teams Agent can't send proactive messages.

**Solution:**
- The target user must send at least one direct message to the bot first
- This establishes a conversation reference for proactive messaging
- Check that `TARGET_USER_ID` is set correctly

#### 3. "TARGET_USER_ID not configured"

**Problem:** Teams Agent doesn't know who to send notifications to.

**Solution:**
- Set `TARGET_USER_ID` in your `.env` file
- Use the Azure AD Object ID (not email or display name)
- Find it in Azure Portal → Users → Select user → Object ID

#### 4. Classifier Server returns 503 errors

**Problem:** LLM fallback is failing.

**Solution:**
- Verify `FEATHERLESS_API_KEY` is valid
- Check API key has sufficient credits
- Review server logs for detailed error messages
- Test with: `curl -X POST http://localhost:8069/classify -H "Content-Type: application/json" -d '{"message":"test"}'`

#### 5. Teams messages not being received

**Problem:** Bot isn't receiving webhook calls from Teams.

**Solution:**
- Verify messaging endpoint is correctly configured in Azure Bot Service
- For local development, use ngrok to expose the service
- Check that the bot is added to the Teams channel
- Verify network connectivity and firewall rules
- Check Teams Agent logs: `docker logs teams-agent`

#### 6. Docker Compose services can't communicate

**Problem:** Services can't reach each other.

**Solution:**
- Ensure all services are on the same network (`teams-network`)
- Use service names for internal communication (e.g., `http://classifier-server:8069`)
- Check service dependencies in `compose.yaml`
- Verify with: `docker network inspect since-ai-sandvik-challenge_teams-network`

#### 7. Model not found error

**Problem:** Classifier server can't find the trained model.

**Solution:**
- Run `python download_model.py` in `apps/classifier-server/`
- Ensure model is in `./spare_parts_model/` directory
- Check Dockerfile includes model download step
- Verify model files are included in Docker image

#### 8. Port already in use

**Problem:** Port conflicts when starting services.

**Solution:**
- Check what's using the port: `lsof -i :3978` (macOS/Linux)
- Change port in `.env` or `compose.yaml`
- Stop conflicting services

### Debugging Tips

1. **Check service logs:**
   ```bash
   # Docker Compose
   docker compose logs teams-agent
   docker compose logs classifier-server
   docker compose logs teams-demo
   
   # Individual containers
   docker logs teams-agent
   docker logs classifier-server
   ```

2. **Test endpoints individually:**
   ```bash
   # Teams Agent health
   curl http://localhost:3978/health
   
   # Classifier Server health
   curl http://localhost:8069/health
   
   # Test classification
   curl -X POST http://localhost:8069/classify \
     -H "Content-Type: application/json" \
     -d '{"message":"Need spare parts"}'
   ```

3. **Verify environment variables:**
   ```bash
   # In Docker container
   docker exec teams-agent env | grep TARGET_USER_ID
   docker exec classifier-server env | grep FEATHERLESS_API_KEY
   ```

4. **Check network connectivity:**
   ```bash
   # From teams-agent container
   docker exec teams-agent curl http://classifier-server:8069/health
   ```

## 👥 Team Members

- **Juhana Kaarlehto** - [LinkedIn](https://www.linkedin.com/in/juhana-kaarlehto-2a6771392/)
- **Vargha Csongor Csaba** - [LinkedIn](https://www.linkedin.com/in/varghacsongorcsaba/)
- **Kirill Nikolaev** - [LinkedIn](https://www.linkedin.com/in/koodarikirka/)
- **Erdős Péter Zsombor** - [LinkedIn](https://www.linkedin.com/in/erdospeterzs/)

## 📄 License

Copyright © 2025 Juhana Kaarlehto, Vargha Csongor Csaba, Kirill Nikolaev, Erdős Péter Zsombor. All rights reserved.

**Warning:** The unauthorized reproduction or distribution of this copyrighted work is illegal.

## 📚 Additional Documentation

- [Classifier Server Technical Overview](apps/classifier-server/README.md) - Detailed explanation of the hybrid AI pipeline
- [Teams Agent Documentation](apps/teams-agent/README.MD) - Complete Teams Agent architecture and API reference
- [Integration Tests](apps/teams-agent/tests/README.md) - Testing guide and examples
