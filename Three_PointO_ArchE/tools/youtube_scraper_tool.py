"""
Local YouTube transcript scraper with caching functionality.
"""

import os
import json
import re
import logging
from typing import Dict, Any, List
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

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

def get_youtube_transcript(video_url: str) -> Dict[str, Any]:
    """
    [IAR Enabled]
    Fetches the transcript for a given YouTube video URL using local caching.
    Falls back to youscrape API if local method fails.

    Args:
        video_url: The full URL of the YouTube video.

    Returns:
        A dictionary containing the transcript data and video info, or an error message.
    """
    logger.info(f"Requesting transcript for YouTube video: {video_url}")
    
    # Extract video ID
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"status": "error", "message": f"Could not extract video ID from URL: {video_url}"}
    
    # Set up cache directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cache_dir = os.path.join(project_root, "transcripts_cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Check cache first
    cached_data = get_cached_transcript(video_id, cache_dir)
    if cached_data:
        return cached_data
    
    # Try local YouTube transcript API
    try:
        logger.info(f"Fetching transcript using YouTube Transcript API for video ID: {video_id}")
        
        # Try to get English transcript first, then any available language
        transcript_data = None
        try:
            # Try English transcript first
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except:
            try:
                # Try any available language
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            except:
                # Try generated transcripts
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], preserve_formatting=True)
        
        # Combine transcript text into a single string for easier processing
        transcript_text = " ".join([segment['text'] for segment in transcript_data])
        
        # Create video info (we don't have title from this API, so we'll use video ID)
        video_info = {
            "title": f"Video {video_id}",
            "video_id": video_id,
            "url": video_url
        }
        
        result = {
            "status": "success",
            "video_info": video_info,
            "full_transcript": transcript_text,
            "transcript_segments": transcript_data
        }
        
        # Cache the result
        cache_transcript(video_id, result, cache_dir)
        
        logger.info(f"Successfully retrieved transcript for video ID: {video_id}")
        return result
        
    except Exception as e:
        logger.warning(f"YouTube Transcript API failed for {video_id}: {e}")
        
        # Use youscrape API server (no fallback - server must be running)
        try:
            import requests
            YOUSCRAPE_API_URL = "http://localhost:3001/api/scrape"
            logger.info(f"Using youscrape API server for video: {video_url}")
            
            response = requests.post(YOUSCRAPE_API_URL, json={"url": video_url}, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            transcript_text = " ".join([segment['text'] for segment in data.get("transcriptData", [])])
            
            result = {
                "status": "success",
                "video_info": data.get("videoInfo", {}),
                "full_transcript": transcript_text,
                "transcript_segments": data.get("transcriptData", [])
            }
            
            # Cache the result
            cache_transcript(video_id, result, cache_dir)
            
            logger.info(f"Successfully retrieved transcript via youscrape server for video: {data.get('videoInfo', {}).get('title', 'N/A')}")
            return result
            
        except Exception as server_error:
            error_message = f"YouTube transcript extraction failed for {video_url}. Local API error: {e}, Server error: {server_error}. Ensure youscrape server is running on localhost:3001"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
