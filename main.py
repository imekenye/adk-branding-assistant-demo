"""
AI Branding Assistant - Main Application Entry Point
"""

import os
import sys
import argparse
from pathlib import Path
import uvicorn
from aiohttp import web, web_request
import aiohttp_cors

# Load environment variables
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

load_dotenv()


async def hello_handler(request: web_request.Request) -> web.Response:
    """Basic hello endpoint"""
    return web.json_response({
        "message": "🎨 ADK Branding Assistant API",
        "status": "running",
        "version": "0.1.0"
    })


async def health_handler(request: web_request.Request) -> web.Response:
    """Health check endpoint"""
    return web.json_response({"status": "healthy"})


def create_app() -> web.Application:
    """Create and configure the web application"""
    app = web.Application()
    
    # Configure CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_get('/', hello_handler)
    app.router.add_get('/health', health_handler)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app


def start_web_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the web server"""
    print("🎨 AI Branding Assistant - Starting Web Server...")
    
    # Verify environment
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
        print("Some features may not work properly without proper API keys")
    
    print("✅ Environment checked")
    print(f"🚀 Starting server on http://{host}:{port}")
    
    app = create_app()
    web.run_app(app, host=host, port=port)


def cli():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="ADK Branding Assistant")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Web server command
    web_parser = subparsers.add_parser("web", help="Start web server")
    web_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    web_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    if args.command == "web":
        start_web_server(args.host, args.port)
    else:
        parser.print_help()


def main():
    """Main application entry point for direct execution"""
    print("🎨 AI Branding Assistant")
    print("Run 'uv run adk web' to start the web server")
    return 0


if __name__ == "__main__":
    exit(main())
