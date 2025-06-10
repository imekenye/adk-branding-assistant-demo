"""
AI Branding Assistant - Main Application Entry Point
"""

import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

load_dotenv()


def main():
    """Main application entry point"""
    print("🎨 AI Branding Assistant - Starting...")

    # Verify environment
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please configure your .env file with the required API keys")
        return 1

    print("✅ Environment configured successfully")
    print("🚀 Ready to start ADK web interface...")
    print("\nRun: uv run adk web")
    print("Then open: http://localhost:8000")

    return 0


if __name__ == "__main__":
    exit(main())
