#!/usr/bin/env python3
"""
Quick start script for the MCP Video Upload Server.
This script helps you get the server running quickly.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path


def print_banner():
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🎬 YouTube Shorts & Instagram Reels MCP Server 🎬        ║
║                                                              ║
║    Quick Start Guide                                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def check_requirements():
    """Check if basic requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return False
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  .env file not found")
        print("📝 Creating .env from .env.example...")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env file created. Please edit it with your credentials.")
        else:
            print("❌ .env.example not found")
            return False
    
    print("✅ Basic requirements check passed")
    return True


def install_dependencies():
    """Install dependencies if needed."""
    print("📦 Installing dependencies...")
    try:
        # Check if fastapi is already installed
        import fastapi
        print("✅ Dependencies already installed")
        return True
    except ImportError:
        print("Installing required packages...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False


def check_credentials():
    """Check if credentials are configured."""
    print("🔐 Checking credentials...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        youtube_configured = all([
            os.getenv("YOUTUBE_CLIENT_ID"),
            os.getenv("YOUTUBE_CLIENT_SECRET"),
            os.getenv("YOUTUBE_ACCESS_TOKEN"),
            os.getenv("YOUTUBE_REFRESH_TOKEN")
        ])
        
        instagram_configured = all([
            os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            os.getenv("INSTAGRAM_APP_ID"),
            os.getenv("INSTAGRAM_APP_SECRET")
        ])
        
        if youtube_configured:
            print("✅ YouTube credentials configured")
        else:
            print("⚠️  YouTube credentials incomplete")
        
        if instagram_configured:
            print("✅ Instagram credentials configured")
        else:
            print("⚠️  Instagram credentials incomplete")
        
        return youtube_configured or instagram_configured
        
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False


def start_server():
    """Start the MCP server."""
    print("🚀 Starting MCP server...")
    
    try:
        # Import and run the server
        import uvicorn
        from main import app
        
        print("✅ Server starting on http://localhost:8000")
        print("📚 API docs available at http://localhost:8000/docs")
        print("🔧 MCP endpoints at http://localhost:8000/mcp")
        print("\n🛑 Press Ctrl+C to stop the server")
        
        # Open browser to docs
        webbrowser.open("http://localhost:8000/docs")
        
        # Start server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True


def show_help():
    """Show help information."""
    print("""
📖 Help & Next Steps:

1. 🔧 Configure Credentials:
   - Edit .env file with your API credentials
   - Get YouTube API credentials from Google Cloud Console
   - Get Instagram API credentials from Facebook Developers

2. 🧪 Test the Server:
   - Run: python test_server.py
   - Or visit: http://localhost:8000/docs

3. 📝 API Usage:
   - POST /upload/youtube - Upload to YouTube Shorts
   - POST /upload/instagram - Upload to Instagram Reels
   - GET /health - Health check

4. 🔗 MCP Integration:
   - Use the MCP tools: post_to_youtube(), post_to_instagram()
   - Access MCP endpoints at /mcp

5. 📚 Documentation:
   - Read README.md for detailed setup instructions
   - Check troubleshooting section for common issues

6. 🆘 Need Help?
   - Check the logs for error messages
   - Verify your API credentials
   - Ensure video files meet platform requirements
    """)


def main():
    """Main quickstart function."""
    print_banner()
    
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        return
    
    if not install_dependencies():
        print("\n❌ Dependency installation failed.")
        return
    
    credentials_ok = check_credentials()
    if not credentials_ok:
        print("\n⚠️  Credentials not fully configured.")
        print("📝 Please edit .env file with your API credentials.")
        print("🔗 See README.md for detailed setup instructions.")
        
        choice = input("\nDo you want to start the server anyway? (y/N): ").lower()
        if choice != 'y':
            show_help()
            return
    
    print("\n" + "="*60)
    start_server()


if __name__ == "__main__":
    main()
