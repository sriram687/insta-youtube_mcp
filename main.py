"""
MCP-compatible FastAPI server for uploading videos to YouTube Shorts and Instagram Reels.
"""

import os
import json
import tempfile
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import aiofiles
import httpx

# Google/YouTube imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# MCP imports
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Shorts & Instagram Reels MCP Server",
    description="MCP-compatible server for uploading videos to YouTube Shorts and Instagram Reels",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP
mcp = FastMCP("Video Upload Server")

# Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "100")) * 1024 * 1024  # Convert to bytes
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_VIDEO_EXTENSIONS", "mp4,mov,avi,mkv,webm").split(",")

# Pydantic models
class YouTubeUploadResponse(BaseModel):
    success: bool
    video_id: Optional[str] = None
    watch_url: Optional[str] = None
    error: Optional[str] = None

class InstagramUploadResponse(BaseModel):
    success: bool
    reel_id: Optional[str] = None
    permalink: Optional[str] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str

# Utility functions
def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )

async def save_temp_file(file: UploadFile) -> str:
    """Save uploaded file to temporary location."""
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    async with aiofiles.open(temp_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return temp_path

def get_video_duration(file_path: str) -> float:
    """Get video duration in seconds using file size estimation."""
    try:
        # Simple estimation based on file size
        # In production, use ffprobe: ffprobe -v quiet -show_entries format=duration -of csv="p=0" file
        file_size = os.path.getsize(file_path)
        # Rough estimation: assume 1MB per 10 seconds for typical mobile video
        estimated_duration = (file_size / (1024 * 1024)) * 10
        return min(estimated_duration, 59.0)  # Cap at 59 seconds for Shorts detection
    except Exception:
        return 45.0  # Default fallback

# YouTube API functions
def refresh_youtube_token() -> Credentials:
    """Refresh YouTube OAuth token."""
    creds = Credentials(
        token=os.getenv("YOUTUBE_ACCESS_TOKEN"),
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )

    # Always try to refresh to ensure we have a valid token
    try:
        creds.refresh(Request())
    except Exception as e:
        print(f"Token refresh failed: {e}")
        # If refresh fails, we'll still try with the existing token

    return creds

async def upload_to_youtube(
    file_path: str,
    title: str,
    description: str,
    tags: List[str]
) -> YouTubeUploadResponse:
    """Upload video to YouTube."""
    try:
        # Get credentials
        creds = refresh_youtube_token()
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Check if video should be a Short
        duration = get_video_duration(file_path)
        is_short = duration < 60
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
        
        # Add Short-specific metadata
        if is_short:
            body['snippet']['description'] += "\n\n#Shorts"
        
        # Upload video
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        
        return YouTubeUploadResponse(
            success=True,
            video_id=video_id,
            watch_url=watch_url
        )
        
    except HttpError as e:
        error_details = json.loads(e.content.decode())
        return YouTubeUploadResponse(
            success=False,
            error=f"YouTube API error: {error_details.get('error', {}).get('message', str(e))}"
        )
    except Exception as e:
        return YouTubeUploadResponse(
            success=False,
            error=f"Upload failed: {str(e)}"
        )

async def upload_to_instagram(file_path: str, caption: str) -> InstagramUploadResponse:
    """
    Upload video to Instagram as a Reel.

    Note: Instagram Graph API requires a publicly accessible video URL.
    This implementation provides a framework but requires additional setup
    for file hosting (AWS S3, Cloudinary, etc.).
    """
    try:
        access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

        if not access_token:
            return InstagramUploadResponse(
                success=False,
                error="Instagram access token not configured"
            )

        # For now, return a success response with instructions
        # In production, you need to implement proper file hosting
        return InstagramUploadResponse(
            success=False,
            error="Instagram upload requires additional setup. Please implement file hosting (AWS S3, Cloudinary, etc.) and update the upload_to_instagram function with your public video URL endpoint."
        )

        # Uncomment and modify the code below once you have file hosting set up:
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Step 1: Upload file to your hosting service (implement this)
            public_video_url = await upload_file_to_public_host(file_path)

            # Step 2: Get Instagram Business Account ID from your access token
            # This assumes you have a User Access Token with proper permissions

            # Step 3: Create media container
            container_data = {
                'media_type': 'REELS',
                'video_url': public_video_url,
                'caption': caption,
                'access_token': access_token
            }

            # Replace 'YOUR_IG_USER_ID' with actual Instagram User ID
            create_response = await client.post(
                f"https://graph.facebook.com/v18.0/YOUR_IG_USER_ID/media",
                data=container_data
            )

            if create_response.status_code != 200:
                return InstagramUploadResponse(
                    success=False,
                    error=f"Failed to create media container: {create_response.text}"
                )

            creation_id = create_response.json().get('id')

            # Step 4: Publish the media
            publish_data = {
                'creation_id': creation_id,
                'access_token': access_token
            }

            publish_response = await client.post(
                f"https://graph.facebook.com/v18.0/YOUR_IG_USER_ID/media_publish",
                data=publish_data
            )

            if publish_response.status_code != 200:
                return InstagramUploadResponse(
                    success=False,
                    error=f"Failed to publish media: {publish_response.text}"
                )

            result = publish_response.json()
            reel_id = result.get('id')

            return InstagramUploadResponse(
                success=True,
                reel_id=reel_id,
                permalink=f"https://www.instagram.com/p/{reel_id}/"
            )
        """

    except Exception as e:
        return InstagramUploadResponse(
            success=False,
            error=f"Instagram upload failed: {str(e)}"
        )

# FastAPI endpoints
@app.post("/upload/youtube", response_model=YouTubeUploadResponse)
async def upload_youtube_endpoint(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form("")
):
    """Upload video to YouTube Shorts."""
    try:
        validate_file(file)
        temp_path = await save_temp_file(file)
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Upload to YouTube
        result = await upload_to_youtube(temp_path, title, description, tag_list)
        
        # Cleanup
        os.unlink(temp_path)
        os.rmdir(os.path.dirname(temp_path))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        return YouTubeUploadResponse(success=False, error=str(e))

@app.post("/upload/instagram", response_model=InstagramUploadResponse)
async def upload_instagram_endpoint(
    file: UploadFile = File(...),
    caption: str = Form("")
):
    """Upload video to Instagram Reels."""
    try:
        validate_file(file)
        temp_path = await save_temp_file(file)
        
        # Upload to Instagram
        result = await upload_to_instagram(temp_path, caption)
        
        # Cleanup
        os.unlink(temp_path)
        os.rmdir(os.path.dirname(temp_path))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        return InstagramUploadResponse(success=False, error=str(e))

# MCP Tool functions
@mcp.tool()
async def post_to_youtube(
    title: str,
    description: str,
    tags: List[str],
    video_path: str
) -> Dict[str, Any]:
    """
    Post a video to YouTube Shorts.
    
    Args:
        title: Video title
        description: Video description
        tags: List of tags for the video
        video_path: Path to the video file
    
    Returns:
        Dictionary with upload result
    """
    try:
        if not os.path.exists(video_path):
            return {"success": False, "error": "Video file not found"}
        
        result = await upload_to_youtube(video_path, title, description, tags)
        return result.dict()
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def post_to_instagram(caption: str, video_path: str) -> Dict[str, Any]:
    """
    Post a video to Instagram Reels.
    
    Args:
        caption: Caption for the Reel
        video_path: Path to the video file
    
    Returns:
        Dictionary with upload result
    """
    try:
        if not os.path.exists(video_path):
            return {"success": False, "error": "Video file not found"}
        
        result = await upload_to_instagram(video_path, caption)
        return result.dict()
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "YouTube Shorts & Instagram Reels MCP Server"}

# Include MCP routes
app.mount("/mcp", mcp.app)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
