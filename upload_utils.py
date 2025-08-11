"""
Utility functions for handling video uploads to social media platforms.
"""

import os
import tempfile
import shutil
from typing import Optional
import httpx
from fastapi import UploadFile, HTTPException


class VideoUploadHandler:
    """Handle video file uploads and temporary storage."""
    
    def __init__(self, max_file_size: int = 100 * 1024 * 1024):
        self.max_file_size = max_file_size
        self.temp_dir = tempfile.mkdtemp()
    
    async def save_upload_file(self, upload_file: UploadFile) -> str:
        """Save uploaded file to temporary location."""
        if upload_file.size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"
            )
        
        # Create unique filename
        file_extension = upload_file.filename.split(".")[-1].lower()
        temp_filename = f"upload_{os.urandom(8).hex()}.{file_extension}"
        temp_path = os.path.join(self.temp_dir, temp_filename)
        
        # Save file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return temp_path
    
    def cleanup_file(self, file_path: str):
        """Remove temporary file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup file {file_path}: {e}")
    
    def cleanup_all(self):
        """Remove all temporary files."""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp directory: {e}")


async def upload_file_to_temporary_host(file_path: str) -> Optional[str]:
    """
    Upload file to a temporary hosting service.
    This is a placeholder - in production, you'd upload to your own CDN/server.
    
    For Instagram, you need a publicly accessible URL.
    Options:
    1. Upload to your own server/CDN
    2. Use a service like Cloudinary, AWS S3, etc.
    3. Use a temporary file hosting service
    
    Returns the public URL of the uploaded file.
    """
    # This is a placeholder implementation
    # In a real scenario, you would:
    # 1. Upload to AWS S3, Cloudinary, or your own server
    # 2. Return the public URL
    
    # For demo purposes, we'll return a placeholder URL
    # You MUST implement actual file hosting for Instagram to work
    return f"https://your-server.com/temp/{os.path.basename(file_path)}"


def get_video_info(file_path: str) -> dict:
    """
    Get video information like duration, resolution, etc.
    This is a simplified version - in production, use ffprobe.
    """
    try:
        file_size = os.path.getsize(file_path)
        
        # Estimate duration based on file size (very rough)
        # In production, use: ffprobe -v quiet -show_entries format=duration -of csv="p=0" file_path
        estimated_duration = min((file_size / (1024 * 1024)) * 8, 60)  # Cap at 60 seconds
        
        return {
            "duration": estimated_duration,
            "file_size": file_size,
            "is_short": estimated_duration < 60
        }
    except Exception as e:
        return {
            "duration": 30,  # Default
            "file_size": 0,
            "is_short": True,
            "error": str(e)
        }


def validate_video_file(upload_file: UploadFile, allowed_extensions: list) -> None:
    """Validate uploaded video file."""
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = upload_file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed extensions: {', '.join(allowed_extensions)}"
        )
    
    # Additional validation can be added here
    # e.g., check file headers, MIME type, etc.
