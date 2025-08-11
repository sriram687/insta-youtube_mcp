"""
Setup script for the MCP Video Upload Server.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("📝 Please copy .env.example to .env and fill in your credentials")
        return False
    
    print("✅ .env file found")
    
    # Check for required variables
    required_vars = [
        "YOUTUBE_CLIENT_ID",
        "YOUTUBE_CLIENT_SECRET", 
        "YOUTUBE_ACCESS_TOKEN",
        "YOUTUBE_REFRESH_TOKEN",
        "INSTAGRAM_ACCESS_TOKEN",
        "INSTAGRAM_APP_ID",
        "INSTAGRAM_APP_SECRET"
    ]
    
    missing_vars = []
    with open(env_path) as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your_" in content or f"{var}=" in content.split(f"{var}=")[1].split('\n')[0] == "":
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or incomplete environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True


def create_temp_directories():
    """Create necessary temporary directories."""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    print("✅ Temporary directories created")


def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    try:
        import fastapi
        import uvicorn
        import google.auth
        import googleapiclient
        import httpx
        import fastmcp
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def display_next_steps():
    """Display next steps for the user."""
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("="*50)
    print("\n📋 Next steps:")
    print("1. Verify your .env file has correct credentials")
    print("2. For YouTube: Ensure your access token has YouTube Data API v3 scope")
    print("3. For Instagram: Set up file hosting (AWS S3, Cloudinary, etc.) for Reels upload")
    print("4. Start the server: python main.py")
    print("5. Test the endpoints: python test_server.py")
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔧 MCP endpoints: http://localhost:8000/mcp")


def main():
    """Main setup function."""
    print("🚀 Setting up MCP Video Upload Server")
    print("="*40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Test imports
    if success and not test_imports():
        success = False
    
    # Check environment file
    if success and not check_env_file():
        success = False
    
    # Create directories
    if success:
        create_temp_directories()
    
    if success:
        display_next_steps()
    else:
        print("\n❌ Setup failed. Please fix the issues above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
