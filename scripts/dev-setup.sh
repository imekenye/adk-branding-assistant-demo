#!/bin/bash

# Development Setup Script
# Uses uv for fast development environment setup

set -e

echo "🚀 Setting up ADK Branding Assistant for development..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "✅ uv is already installed ($(uv --version))"
fi

# Sync dependencies
echo "📥 Installing dependencies with uv..."
uv sync --all-extras

echo "🎯 Development environment ready!"
echo ""
echo "💡 Quick commands:"
echo "  uv run adk --help              # Show CLI help"
echo "  uv run adk web                 # Start web server"
echo "  uv run black .                 # Format code"
echo "  uv run isort .                 # Sort imports"
echo "  uv run mypy agents/ tools/     # Type checking"
echo "  uv run pytest                  # Run tests"
echo ""
echo "🔧 For production deployment:"
echo "  The project uses pip and requirements.txt"
echo "  requirements.txt is generated dynamically from uv.lock during CI/CD"
echo "  Docker builds use: pip install -r requirements.txt"
echo ""
echo "📝 To manually generate requirements.txt:"
echo "  uv export --format requirements-txt --locked --no-dev > requirements.txt" 