#!/bin/bash
# Development environment initialization script

echo "🔧 Initializing AI Branding Assistant development environment..."

# Activate virtual environment
source .venv/bin/activate

# Install all dependencies
uv sync --all-extras

# Create necessary directories
mkdir -p data/{inputs,outputs,shared_state,uploads,cache}

# Set proper permissions
chmod +x scripts/setup/*.sh
chmod +x scripts/deployment/*.sh

echo "✅ Development environment ready!"
echo "🚀 Run 'uv run adk web' to start"