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
def get_youtube_transcript(video_id_or_url: str) -> Dict[str, Any]:
    """
    Fetches the transcript for a YouTube video using the internal youscrape service.

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

    # 2. Define the local service endpoint and payload
    youscrape_endpoint = "http://localhost:3001/api/scrape"
    payload = {"url": video_url}
    headers = {"Content-Type": "application/json"}

    try:
        # 3. Make the POST request to the youscrape service
        response = requests.post(youscrape_endpoint, json=payload, headers=headers, timeout=180) # Increased timeout for long scrapes
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Process the response
        data = response.json()

        if data.get("success"):
            logger.info(f"Successfully retrieved transcript for video: {data.get('videoInfo', {}).get('title')}")
            # The service returns the data in the desired format
            return {
                "status": "success",
                "transcript_data": data.get("transcriptData"),
                "video_info": data.get("videoInfo")
            }
        else:
            logger.error(f"youscrape service returned failure for URL: {video_url}")
            raise Exception("Failed to retrieve transcript. The youscrape service indicated failure.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to youscrape service at {youscrape_endpoint}. Is it running? Error: {e}")
        raise Exception(f"Could not connect to the internal youscrape service. Please ensure it is running on port 3001. Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching transcript: {e}")
        raise
