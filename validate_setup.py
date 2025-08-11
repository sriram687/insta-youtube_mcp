"""
Validation script to check if the MCP Video Upload Server is properly configured.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_file_structure():
    """Check if all required files are present."""
    print("📁 Checking file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        ".env",
        "README.md",
        "config.py",
        "upload_utils.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True


def check_dependencies():
    """Check if all dependencies are installed."""
    print("📦 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "python-multipart",
        "python-dotenv",
        "google-auth",
        "google-api-python-client",
        "requests",
        "fastmcp",
        "pydantic",
        "aiofiles",
        "httpx"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True


def validate_youtube_credentials():
    """Validate YouTube API credentials."""
    print("🎬 Validating YouTube credentials...")
    
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    access_token = os.getenv("YOUTUBE_ACCESS_TOKEN")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, access_token, refresh_token]):
        print("❌ YouTube credentials incomplete")
        return False
    
    # Check if credentials look valid
    if not client_id.endswith(".apps.googleusercontent.com"):
        print("⚠️  YouTube Client ID format looks incorrect")
        return False
    
    if not client_secret.startswith("GOCSPX-"):
        print("⚠️  YouTube Client Secret format looks incorrect")
        return False
    
    # Check if access token has correct scope (this is a basic check)
    if "ya29." not in access_token:
        print("⚠️  YouTube Access Token format looks incorrect")
        return False
    
    print("✅ YouTube credentials format looks correct")
    print("⚠️  Note: Verify your access token has YouTube Data API v3 scope")
    return True


def validate_instagram_credentials():
    """Validate Instagram API credentials."""
    print("📱 Validating Instagram credentials...")
    
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    app_id = os.getenv("INSTAGRAM_APP_ID")
    app_secret = os.getenv("INSTAGRAM_APP_SECRET")
    
    if not all([access_token, app_id, app_secret]):
        print("❌ Instagram credentials incomplete")
        return False
    
    # Basic format checks
    if not access_token.startswith("IGAA"):
        print("⚠️  Instagram Access Token format looks incorrect")
        return False
    
    if not app_id.isdigit():
        print("⚠️  Instagram App ID should be numeric")
        return False
    
    if len(app_secret) != 32:
        print("⚠️  Instagram App Secret should be 32 characters")
        return False
    
    print("✅ Instagram credentials format looks correct")
    return True


async def test_server_import():
    """Test if the main server can be imported."""
    print("🔧 Testing server import...")
    
    try:
        from main import app
        print("✅ Server imports successfully")
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False


def check_environment_config():
    """Check environment configuration."""
    print("⚙️  Checking environment configuration...")
    
    # Check basic config
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8000")
    debug = os.getenv("DEBUG", "False")
    
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            print(f"❌ Invalid port number: {port}")
            return False
    except ValueError:
        print(f"❌ Port must be a number: {port}")
        return False
    
    print(f"✅ Server config: {host}:{port} (debug={debug})")
    return True


def generate_report():
    """Generate a validation report."""
    print("\n" + "="*60)
    print("📋 VALIDATION REPORT")
    print("="*60)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Dependencies", check_dependencies),
        ("Environment Config", check_environment_config),
        ("YouTube Credentials", validate_youtube_credentials),
        ("Instagram Credentials", validate_instagram_credentials),
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n{name}:")
        results[name] = check_func()
    
    # Test server import
    print(f"\nServer Import:")
    results["Server Import"] = asyncio.run(test_server_import())
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your server is ready to run.")
        print("🚀 Start with: python main.py")
        print("🧪 Test with: python test_server.py")
    else:
        print(f"\n⚠️  {total - passed} issues found. Please fix them before running the server.")
        print("📖 Check README.md for setup instructions.")
    
    return passed == total


def main():
    """Main validation function."""
    print("🔍 MCP Video Upload Server - Setup Validation")
    print("="*50)
    
    success = generate_report()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
