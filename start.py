#!/usr/bin/env python3
"""
Startup script for Cloud Run deployment
Ensures proper port binding and error handling
"""
import os
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main startup function"""
    print("🚀 ADK Branding Assistant - Cloud Run Startup")
    
    # Get port from environment
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'
    
    print(f"📡 Binding to {host}:{port}")
    
    # Verify required environment variables
    required_vars = ['GOOGLE_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
    else:
        print("✅ Environment variables verified")
    
    # Import and start the server
    try:
        from main import start_web_server
        print("📦 Module imports successful")
        
        print(f"🌐 Starting web server on {host}:{port}")
        start_web_server(host=host, port=port)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 