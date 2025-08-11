# YouTube Shorts & Instagram Reels MCP Server

A Model Context Protocol (MCP) compatible FastAPI server that enables automated posting of videos to YouTube Shorts and Instagram Reels.

## Features

- 🎬 **YouTube Shorts Upload**: Automatic detection and upload of short-form videos to YouTube
- 📱 **Instagram Reels Upload**: Direct upload to Instagram Reels with caption support
- 🔐 **OAuth 2.0 Authentication**: Secure authentication for both platforms
- 🛡️ **File Validation**: Comprehensive file type and size validation
- 🔄 **Token Refresh**: Automatic OAuth token refresh for YouTube
- 🎯 **MCP Compatible**: Full MCP tool integration for seamless automation
- ⚡ **Async Operations**: High-performance async file handling

## Prerequisites

### YouTube API Setup

1. **Google Cloud Console Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable YouTube Data API v3 in the API Library
   - Go to "Credentials" and create OAuth 2.0 credentials (Desktop application)
   - Download the credentials JSON file

2. **Get Access and Refresh Tokens**:
   - Go to [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
   - Click the gear icon (⚙️) in the top right
   - Check "Use your own OAuth credentials"
   - Enter your Client ID and Client Secret from step 1
   - In the left panel, find "YouTube Data API v3"
   - Select `https://www.googleapis.com/auth/youtube.upload`
   - Click "Authorize APIs" and complete the OAuth flow
   - Click "Exchange authorization code for tokens"
   - Copy the `access_token` and `refresh_token` for your .env file

3. **Important Notes**:
   - Your current access token has Google Drive scope, not YouTube
   - You MUST get a new token with YouTube Data API v3 scope
   - The refresh token allows automatic token renewal

### Instagram API Setup

1. **Facebook Developer Account**:
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create a developer account if you don't have one
   - Create a new app and select "Business" type

2. **Instagram Graph API Setup**:
   - Add "Instagram Graph API" to your app
   - Configure Instagram Basic Display if needed
   - Add your Instagram Business/Creator account

3. **Get Access Token**:
   - Your current token appears to be valid
   - For production, generate a long-lived access token (60 days)
   - Use the Graph API Explorer to test your token

4. **Important Requirements**:
   - Instagram account must be a Business or Creator account
   - Account must be connected to a Facebook Page
   - For Reels upload, you need additional file hosting setup
   - Videos must be publicly accessible via URL for Instagram API

5. **File Hosting Setup** (Required for Instagram):
   - Instagram Graph API requires publicly accessible video URLs
   - Set up AWS S3, Cloudinary, or similar service
   - Update the `upload_to_instagram` function with your hosting endpoint

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd INSTA&UTUBE_MCP
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

4. **Configure your .env file**:
```env
# YouTube API Credentials
YOUTUBE_CLIENT_ID=your_youtube_client_id_here
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
YOUTUBE_ACCESS_TOKEN=your_youtube_access_token_here
YOUTUBE_REFRESH_TOKEN=your_youtube_refresh_token_here

# Instagram API Credentials
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
INSTAGRAM_APP_ID=your_instagram_app_id_here
INSTAGRAM_APP_SECRET=your_instagram_app_secret_here
```

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:8000` by default.

### API Endpoints

#### Upload to YouTube Shorts
```http
POST /upload/youtube
Content-Type: multipart/form-data

file: <video_file>
title: "My Amazing Short"
description: "Check out this cool video!"
tags: "shorts,viral,amazing"
```

**Response**:
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "watch_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

#### Upload to Instagram Reels
```http
POST /upload/instagram
Content-Type: multipart/form-data

file: <video_file>
caption: "Check out my new reel! #viral #reels"
```

**Response**:
```json
{
  "success": true,
  "reel_id": "17841234567890123",
  "permalink": "https://www.instagram.com/reel/ABC123def456/"
}
```

### MCP Tool Usage

The server exposes two MCP tools:

#### post_to_youtube
```python
await post_to_youtube(
    title="My Video Title",
    description="Video description",
    tags=["tag1", "tag2", "tag3"],
    video_path="/path/to/video.mp4"
)
```

#### post_to_instagram
```python
await post_to_instagram(
    caption="My reel caption #hashtag",
    video_path="/path/to/video.mp4"
)
```

## File Requirements

### Supported Formats
- **Video**: MP4, MOV, AVI, MKV, WebM
- **Max Size**: 100MB (configurable)
- **Duration**: Recommended under 60 seconds for optimal Shorts detection

### YouTube Shorts Criteria
- Videos under 60 seconds are automatically tagged as Shorts
- Vertical or square aspect ratios work best
- Resolution: 1080x1920 (9:16) recommended

### Instagram Reels Criteria
- Duration: 15-90 seconds
- Aspect ratio: 9:16 (vertical) recommended
- Resolution: 1080x1920 recommended

## Configuration

Environment variables can be customized:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# File Upload Configuration
MAX_FILE_SIZE_MB=100
ALLOWED_VIDEO_EXTENSIONS=mp4,mov,avi,mkv,webm

# API Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

## Error Handling

The server provides detailed error responses:

```json
{
  "success": false,
  "error": "File too large. Maximum size is 100MB"
}
```

Common error scenarios:
- Invalid file format
- File too large
- Authentication failures
- API rate limits
- Network timeouts

## Security Considerations

- Store credentials in environment variables, never in code
- Use HTTPS in production
- Implement rate limiting
- Validate all file uploads
- Monitor API usage quotas

## Development

### Running in Development Mode
```bash
DEBUG=True python main.py
```

### Testing the API
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test YouTube upload
curl -X POST "http://localhost:8000/upload/youtube" \
  -F "file=@test_video.mp4" \
  -F "title=Test Video" \
  -F "description=Test Description" \
  -F "tags=test,api"
```

## Troubleshooting

### Common Issues

1. **YouTube Authentication Errors**
   - Verify OAuth credentials are correct
   - Check if access token has expired
   - Ensure YouTube Data API v3 is enabled

2. **Instagram Upload Failures**
   - Verify Instagram Business/Creator account is linked
   - Check access token permissions
   - Ensure video meets Instagram requirements

3. **File Upload Issues**
   - Check file size limits
   - Verify file format is supported
   - Ensure sufficient disk space for temporary files

### Logs and Debugging

Enable debug mode for detailed logging:
```bash
DEBUG=True python main.py
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation
- Open an issue on GitHub
