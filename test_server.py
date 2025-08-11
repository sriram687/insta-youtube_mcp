"""
Test script for the MCP Video Upload Server.
"""

import asyncio
import os
import tempfile
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")


def create_test_video():
    """Create a simple test video file."""
    # Create a minimal MP4 file (this is just for testing file upload)
    # In a real scenario, you'd use a proper video file
    test_content = b"fake video content for testing"
    
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    temp_file.write(test_content)
    temp_file.close()
    
    return temp_file.name


async def test_youtube_upload():
    """Test YouTube upload endpoint."""
    print("\nTesting YouTube upload endpoint...")
    
    # Check if YouTube credentials are configured
    if not all([
        os.getenv("YOUTUBE_CLIENT_ID"),
        os.getenv("YOUTUBE_CLIENT_SECRET"),
        os.getenv("YOUTUBE_ACCESS_TOKEN"),
        os.getenv("YOUTUBE_REFRESH_TOKEN")
    ]):
        print("⚠️  YouTube credentials not configured, skipping test")
        return
    
    test_video_path = create_test_video()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(test_video_path, "rb") as video_file:
                files = {"file": ("test_video.mp4", video_file, "video/mp4")}
                data = {
                    "title": "Test Video Upload",
                    "description": "This is a test video uploaded via the MCP server",
                    "tags": "test,mcp,api"
                }
                
                response = await client.post(
                    f"{BASE_URL}/upload/youtube",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("✅ YouTube upload test passed")
                        print(f"Video ID: {result.get('video_id')}")
                        print(f"Watch URL: {result.get('watch_url')}")
                    else:
                        print(f"❌ YouTube upload failed: {result.get('error')}")
                else:
                    print(f"❌ YouTube upload request failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    
    except Exception as e:
        print(f"❌ YouTube upload test error: {e}")
    finally:
        # Cleanup test file
        if os.path.exists(test_video_path):
            os.unlink(test_video_path)


async def test_instagram_upload():
    """Test Instagram upload endpoint."""
    print("\nTesting Instagram upload endpoint...")
    
    # Check if Instagram credentials are configured
    if not all([
        os.getenv("INSTAGRAM_ACCESS_TOKEN"),
        os.getenv("INSTAGRAM_APP_ID"),
        os.getenv("INSTAGRAM_APP_SECRET")
    ]):
        print("⚠️  Instagram credentials not configured, skipping test")
        return
    
    test_video_path = create_test_video()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(test_video_path, "rb") as video_file:
                files = {"file": ("test_video.mp4", video_file, "video/mp4")}
                data = {
                    "caption": "Test reel uploaded via MCP server! #test #mcp #api"
                }
                
                response = await client.post(
                    f"{BASE_URL}/upload/instagram",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("✅ Instagram upload test passed")
                        print(f"Reel ID: {result.get('reel_id')}")
                        print(f"Permalink: {result.get('permalink')}")
                    else:
                        print(f"❌ Instagram upload failed: {result.get('error')}")
                else:
                    print(f"❌ Instagram upload request failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    
    except Exception as e:
        print(f"❌ Instagram upload test error: {e}")
    finally:
        # Cleanup test file
        if os.path.exists(test_video_path):
            os.unlink(test_video_path)


async def test_file_validation():
    """Test file validation."""
    print("\nTesting file validation...")
    
    # Test with invalid file type
    test_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
    test_file.write(b"This is not a video file")
    test_file.close()
    
    try:
        async with httpx.AsyncClient() as client:
            with open(test_file.name, "rb") as invalid_file:
                files = {"file": ("test.txt", invalid_file, "text/plain")}
                data = {
                    "title": "Test Video",
                    "description": "Test",
                    "tags": "test"
                }
                
                response = await client.post(
                    f"{BASE_URL}/upload/youtube",
                    files=files,
                    data=data
                )
                
                if response.status_code == 400:
                    print("✅ File validation test passed (correctly rejected invalid file)")
                else:
                    print(f"❌ File validation test failed: {response.status_code}")
                    
    except Exception as e:
        print(f"❌ File validation test error: {e}")
    finally:
        if os.path.exists(test_file.name):
            os.unlink(test_file.name)


async def main():
    """Run all tests."""
    print("🚀 Starting MCP Video Upload Server Tests")
    print("=" * 50)
    
    await test_health_check()
    await test_file_validation()
    await test_youtube_upload()
    await test_instagram_upload()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")
    print("\nNote: Upload tests require valid API credentials in .env file")
    print("For full testing, ensure your server is running: python main.py")


if __name__ == "__main__":
    asyncio.run(main())
