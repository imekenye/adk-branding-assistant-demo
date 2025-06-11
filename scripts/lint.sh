#!/bin/bash
# Linting and formatting script for ADK Branding Assistant

echo "🧹 Running code formatting and linting..."

echo "📦 Running isort..."
uv run isort .

echo "🖤 Running black..."
uv run black .

echo "🔍 Running mypy..."
uv run mypy main.py

echo "✅ Linting complete!"

# Check if all passed
echo "🧪 Verifying formatting..."
if uv run black --check . && uv run isort --check-only .; then
    echo "✨ All formatting checks passed!"
    exit 0
else
    echo "❌ Formatting checks failed!"
    exit 1
fi 