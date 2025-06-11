# AI Branding Assistant - Google Cloud Multi-Agent Hackathon Entry

🏆 **Google Cloud Multi-Agent Hackathon Submission**

Multi-agent AI system for automated branding and logo generation using Google ADK.

## 🎯 Hackathon Category
**Content Creation and Generation** + **Automation of Complex Processes**

## 🤖 Multi-Agent Architecture

### Agent Workflow
Client Input → Discovery Agent → Research Agent → Visual Direction Agent → Logo Generation Agent → Brand System Agent → Asset Generation Agent → Final Deliverables

### Agent Responsibilities
- **Discovery Agent**: Client intake, requirements gathering, file uploads
- **Research Agent**: Market analysis, competitive intelligence
- **Visual Direction Agent**: Mood boards, color palettes, typography
- **Logo Generation Agent**: Multi-model AI logo creation (GPT-4o, FLUX, Gemini)
- **Brand System Agent**: Brand guidelines, usage rules
- **Asset Generation Agent**: Complete asset packages

## 🛠 Technologies Used

### Core Framework
- **Google ADK (Agent Development Kit)** - Multi-agent orchestration
- **Python 3.11** - Primary development language

### AI Models (Multi-Model Integration)
- **OpenAI GPT-4o** - Professional logo generation with superior text rendering
- **Google Gemini 2.0 Flash** - Native ADK integration, conversational generation
- **FLUX.1.1 Pro (Replicate)** - Creative logo concepts and artistic styles
- **Google Imagen 3** - High-quality alternative generation

### Google Cloud Integration
- **Google Cloud Run** - Serverless deployment
- **Vertex AI** - Enterprise AI model access
- **Google AI Studio** - Gemini model integration

### Supporting Technologies
- **LiteLLM** - Multi-model API integration
- **Pillow + NumPy** - Image processing and analysis
- **HTTPX** - Modern HTTP client for API calls
- **SQLAlchemy** - Data persistence
- **Pydantic** - Data validation

## 🚀 Demo Features

### 1. Multi-Agent Workflow Automation
- Seamless handoffs between specialized agents
- State management across complex branding process
- Error handling and quality gates

### 2. Intelligent Logo Generation
- Multiple AI models working in parallel
- Automatic fallback hierarchy for reliability
- Professional quality validation

### 3. Reference Image Analysis
- Client upload processing
- Style extraction from references
- Color palette generation from brand inspirations

### 4. Complete Brand System
- Logo variations and formats
- Brand guidelines documentation
- Asset package generation

## 🔧 Development Setup

This project uses a hybrid approach:
- **Development**: UV for fast dependency management and development workflow
- **Production**: pip for reliable Docker deployments and CI/CD

### Quick Start (Development)
```bash
# Automatic setup with uv
./scripts/dev-setup.sh

# Or manually:
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras
uv run adk web
```

### Common Development Commands
```bash
uv run adk --help              # Show CLI help
uv run adk web                 # Start web server
uv run black .                 # Format code
uv run isort .                 # Sort imports
uv run mypy agents/ tools/     # Type checking
uv run pytest                  # Run tests
```

### Production Deployment
The project automatically deploys to Google Cloud Run using pip:
- Docker builds use `requirements.txt` (generated from `pyproject.toml`)
- Optimized for cloud deployment reliability
- CI/CD validates both uv (dev) and pip (prod) installations

## 🐳 Docker & Deployment

**Local testing:**
```bash
docker build -t adk-branding-assistant .
docker run -p 8000:8000 adk-branding-assistant
```

**Production:** 
Automatic deployment via GitHub Actions to Google Cloud Run on `hackathon-demo` branch.