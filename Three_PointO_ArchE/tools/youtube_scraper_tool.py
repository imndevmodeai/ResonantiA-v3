"""
Local YouTube transcript scraper with caching functionality.
"""

import os
import json
import re
import logging
import requests # Import the requests library
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Fallback: try to parse as URL
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            if parsed.path.startswith('/watch'):
                query_params = parse_qs(parsed.query)
                return query_params.get('v', [None])[0]
            elif parsed.path.startswith('/'):
                return parsed.path[1:]
    except:
        pass
    
    return None

def get_cached_transcript(video_id: str, cache_dir: str) -> Dict[str, Any]:
    """Check if transcript is already cached locally."""
    cache_file = os.path.join(cache_dir, f"{video_id}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                logger.info(f"Using cached transcript for video ID: {video_id}")
                return cached_data
        except Exception as e:
            logger.warning(f"Failed to read cached transcript for {video_id}: {e}")
    return None

def cache_transcript(video_id: str, transcript_data: Dict[str, Any], cache_dir: str):
    """Cache transcript data locally."""
    cache_file = os.path.join(cache_dir, f"{video_id}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Cached transcript for video ID: {video_id}")
    except Exception as e:
        logger.warning(f"Failed to cache transcript for {video_id}: {e}")

# --- NEW: Refactored to use the internal youscrape service ---
def check_youscrape_server() -> bool:
    """Check if youscrape server is running and healthy."""
    youscrape_endpoint = "http://localhost:3001/api/scrape"
    try:
        # Simple health check - try a HEAD request or check if port is open
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 3001))
        sock.close()
        return result == 0
    except Exception:
        return False

def start_youscrape_server() -> bool:
    """Attempt to start the youscrape server if not running."""
    import subprocess
    import os
    import time
    
    try:
        # Check if server is already running
        if check_youscrape_server():
            logger.info("youscrape server is already running")
            return True
        
        # Find the server file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
        server_path = os.path.join(project_root, 'youscrape', 'backend', 'server.mjs')
        
        if not os.path.exists(server_path):
            logger.warning(f"youscrape server file not found at {server_path}")
            return False
        
        # Start the server in background
        logger.info(f"Starting youscrape server from {server_path}")
        process = subprocess.Popen(
            ['node', server_path],
            cwd=os.path.dirname(server_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server started successfully
        if check_youscrape_server():
            logger.info("youscrape server started successfully")
            return True
        else:
            logger.warning("youscrape server may not have started properly")
            return False
            
    except Exception as e:
        logger.error(f"Failed to start youscrape server: {e}")
        return False

def get_youtube_transcript(video_id_or_url: str) -> Dict[str, Any]:
    """
    Fetches the transcript for a YouTube video using the internal youscrape service.
    Automatically checks and starts the server if needed.

    Args:
        video_id_or_url: The ID or full URL of the YouTube video.

    Returns:
        A dictionary containing the transcript and video information.
        
    Raises:
        Exception: If the scraping service fails or returns an error.
    """
    logger.info(f"Requesting transcript for '{video_id_or_url}' from local youscrape service.")

    # 1. Construct the full YouTube URL if only an ID is provided
    if "youtube.com" in video_id_or_url or "youtu.be" in video_id_or_url:
        video_url = video_id_or_url
    else:
        video_url = f"https://www.youtube.com/watch?v={video_id_or_url}"

    # 2. Check if server is running, start if not
    if not check_youscrape_server():
        logger.info("youscrape server not running, attempting to start...")
        if not start_youscrape_server():
            logger.warning("Could not start youscrape server, transcript extraction may fail")
            return {
                "status": "error",
                "message": "youscrape server is not running and could not be started",
                "transcript_data": None,
                "video_info": None
            }

    # 3. Define the local service endpoint and payload
    youscrape_endpoint = "http://localhost:3001/api/scrape"
    payload = {"url": video_url}
    headers = {"Content-Type": "application/json"}

    try:
        # 4. Make the POST request to the youscrape service
        response = requests.post(youscrape_endpoint, json=payload, headers=headers, timeout=180) # Increased timeout for long scrapes
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Process the response
        data = response.json()

        if data.get("success"):
            logger.info(f"Successfully retrieved transcript for video: {data.get('videoInfo', {}).get('title')}")
            
            # Extract transcript text properly
            transcript_data = data.get("transcriptData", {})
            transcript_text = ""
            
            # Handle different transcript data formats
            if isinstance(transcript_data, str):
                transcript_text = transcript_data
            elif isinstance(transcript_data, dict):
                # Try common keys
                transcript_text = (transcript_data.get("text") or 
                                 transcript_data.get("transcript") or 
                                 transcript_data.get("full_transcript") or
                                 str(transcript_data))
            elif isinstance(transcript_data, list):
                # Join list items
                transcript_text = " ".join([str(item) for item in transcript_data])
            
            # The service returns the data in the desired format
            return {
                "status": "success",
                "transcript_data": transcript_data,
                "full_transcript": transcript_text,
                "video_info": data.get("videoInfo", {}),
                "video_id": extract_video_id(video_url)
            }
        else:
            logger.error(f"youscrape service returned failure for URL: {video_url}")
            return {
                "status": "error",
                "message": "youscrape service returned failure",
                "transcript_data": None,
                "video_info": None
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to youscrape service at {youscrape_endpoint}. Error: {e}")
        return {
            "status": "error",
            "message": f"Could not connect to youscrape service: {str(e)}",
            "transcript_data": None,
            "video_info": None
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching transcript: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "transcript_data": None,
            "video_info": None
        }

