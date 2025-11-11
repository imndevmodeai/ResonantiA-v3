#!/usr/bin/env python3
"""
Chaturbate Content Aggregator Flask App
Aggregates live streams and past performances from Chaturbate and cloudbate.com
"""

import os
import re
import json
import logging
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chaturbate_aggregator_secret_key_2024')

# Configuration
CHATURBATE_BASE_URL = "https://chaturbate.com"
CLOUDBATE_BASE_URL = "https://www.cloudbate.com"
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def extract_username_from_url(url_or_username: str) -> Optional[str]:
    """
    Extract Chaturbate username from URL or return username if already extracted.
    Supports multiple formats:
    - https://chaturbate.com/username/
    - https://chaturbate.com/username
    - chaturbate.com/username
    - username
    """
    if not url_or_username:
        return None
    
    url_or_username = url_or_username.strip()
    
    # If it's already just a username (no slashes, no http)
    if not re.search(r'[/:]', url_or_username) and not url_or_username.startswith('http'):
        # Clean username (remove @ if present)
        username = url_or_username.replace('@', '').strip()
        return username if username else None
    
    # Try to extract from URL
    try:
        # Add protocol if missing
        if not url_or_username.startswith('http'):
            url_or_username = 'https://' + url_or_username
        
        parsed = urlparse(url_or_username)
        path = parsed.path.strip('/')
        
        # Extract username from path (first segment)
        if path:
            username = path.split('/')[0].strip()
            # Remove common suffixes
            username = re.sub(r'[/?#].*$', '', username)
            return username if username else None
    except Exception as e:
        logger.error(f"Error extracting username from URL: {e}")
    
    return None


def extract_usernames_from_input(input_text: str) -> List[str]:
    """
    Extract multiple usernames from input text.
    Supports comma-separated, newline-separated, or space-separated lists.
    """
    if not input_text:
        return []
    
    # Split by common delimiters
    potential_usernames = re.split(r'[,\n\r\s]+', input_text.strip())
    
    usernames = []
    for item in potential_usernames:
        item = item.strip()
        if not item:
            continue
        
        username = extract_username_from_url(item)
        if username and username not in usernames:
            usernames.append(username)
    
    return usernames


def check_chaturbate_live_status(username: str) -> Dict[str, Any]:
    """
    Check if a Chaturbate user is currently live.
    Returns dict with live status, title, viewers, etc.
    """
    try:
        url = f"{CHATURBATE_BASE_URL}/{username}/"
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': CHATURBATE_BASE_URL
        }
        
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        
        if response.status_code == 404:
            return {
                'is_live': False,
                'exists': False,
                'error': 'User not found'
            }
        
        html = response.text
        
        # Check for live indicators
        is_live = False
        title = None
        viewers = None
        thumbnail = None
        
        # More robust live detection
        html_lower = html.lower()
        
        # Positive indicators of live status
        live_indicators = [
            'room_status": "public"',
            'room_status":"public"',
            '"is_live":true',
            '"is_live": true',
            'is_live":true',
            'currently broadcasting',
            'live now',
            'viewers watching',
            'hls_stream',
            'm3u8',
            'room_status: "public"',
            'room_status:"public"'
        ]
        
        # Negative indicators (definitely offline)
        offline_indicators = [
            'room_status": "offline"',
            'room_status":"offline"',
            '"is_live":false',
            '"is_live": false',
            'currently offline',
            'is currently offline',
            'room_status: "offline"',
            'room_status:"offline"'
        ]
        
        # Check for offline indicators first
        is_offline = any(indicator in html_lower for indicator in offline_indicators)
        
        if is_offline:
            is_live = False
        else:
            # Check for live indicators
            has_live_indicators = any(indicator in html for indicator in live_indicators)
            
            # Also check for stream-related elements
            has_stream_elements = any(term in html_lower for term in [
                'hls', 'm3u8', 'stream_url', 'rtmp', 'videojs', 'jwplayer', 'playlist.m3u8'
            ])
            
            # Check if page has active stream controls
            has_stream_controls = any(term in html_lower for term in [
                'play-button', 'video-player', 'stream-player', 'broadcast-player', 'theater-video'
            ])
            
            # Check for viewer count (if there are viewers, likely live)
            has_viewers = viewers is not None and viewers > 0
            
            # Check for chat elements (live rooms have active chat)
            has_chat = 'chat' in html_lower and ('chat-messages' in html_lower or 'chat-container' in html_lower)
            
            # If we have live indicators or stream elements, consider it live
            if has_live_indicators or (has_stream_elements and has_stream_controls):
                is_live = True
            elif has_viewers and has_chat and 'offline' not in html_lower:
                # If there are viewers and chat, likely live
                is_live = True
            else:
                # Fallback: check if page structure suggests live room
                # Live rooms typically have more interactive elements
                if 'chat' in html_lower and 'tip' in html_lower and 'offline' not in html_lower:
                    # Might be live, but less certain
                    is_live = True
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        
        # Extract thumbnail
        thumbnail_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html, re.IGNORECASE)
        if thumbnail_match:
            thumbnail = thumbnail_match.group(1)
        else:
            # Try alternative thumbnail patterns
            thumbnail_match = re.search(r'thumbnail["\']?\s*[:=]\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
            if thumbnail_match:
                thumbnail = thumbnail_match.group(1)
        
        # Extract viewer count if available
        viewers_match = re.search(r'(\d+)\s*(?:viewers?|watching)', html, re.IGNORECASE)
        if viewers_match:
            viewers = int(viewers_match.group(1))
        
        # Extract HLS stream URL if live
        stream_url = None
        hls_url = None
        
        if is_live:
            # Look for HLS playlist URLs in the HTML
            hls_patterns = [
                r'https://[^"\']+\.m3u8[^"\']*',
                r'["\']([^"\']*playlist\.m3u8[^"\']*)["\']',
                r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'hls["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'stream_url["\']?\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in hls_patterns:
                matches = re.finditer(pattern, html, re.IGNORECASE)
                for match in matches:
                    potential_url = match.group(1) if match.groups() else match.group(0)
                    if '.m3u8' in potential_url and 'edge' in potential_url:
                        hls_url = potential_url
                        break
                if hls_url:
                    break
            
            # Also try to get from API endpoint (this is the most reliable method)
            if not hls_url:
                try:
                    # Get the room code first (needed for API)
                    room_code_match = re.search(r'room["\']?\s*[:=]\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
                    room_code = room_code_match.group(1) if room_code_match else None
                    
                    # Try API endpoint with room code or username
                    api_urls = []
                    if room_code:
                        api_urls.append(f"{CHATURBATE_BASE_URL}/api/public/asp/broadcast/applist/{room_code}/")
                    api_urls.append(f"{CHATURBATE_BASE_URL}/api/public/asp/broadcast/applist/{username}/")
                    
                    for api_url in api_urls:
                        try:
                            api_response = requests.get(api_url, headers=headers, timeout=REQUEST_TIMEOUT)
                            if api_response.status_code == 200:
                                api_data = api_response.json()
                                logger.debug(f"API response: {api_data}")
                                
                                # Look for stream URLs in API response (nested structure)
                                def find_hls_url(obj, depth=0):
                                    if depth > 5:  # Prevent infinite recursion
                                        return None
                                    if isinstance(obj, dict):
                                        for key, value in obj.items():
                                            if isinstance(value, str) and '.m3u8' in value and 'edge' in value:
                                                return value
                                            result = find_hls_url(value, depth + 1)
                                            if result:
                                                return result
                                    elif isinstance(obj, list):
                                        for item in obj:
                                            result = find_hls_url(item, depth + 1)
                                            if result:
                                                return result
                                    return None
                                
                                found_url = find_hls_url(api_data)
                                if found_url:
                                    hls_url = found_url
                                    logger.info(f"Found HLS URL from API: {hls_url[:100]}...")
                                    break
                        except Exception as api_err:
                            logger.debug(f"Error with API URL {api_url}: {api_err}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Could not fetch stream URL from API: {e}")
            
            stream_url = f"{CHATURBATE_BASE_URL}/{username}/"
        
        # Generate mmcdn live thumbnail URL for all users (mmcdn provides thumbnails regardless of live status)
        # mmcdn live thumbnail pattern: https://thumb.live.mmcdn.com/ri/{username}.jpg?{timestamp}
        mmcdn_thumbnail = f"https://thumb.live.mmcdn.com/ri/{username}.jpg"
        
        return {
            'is_live': is_live,
            'exists': True,
            'username': username,
            'title': title or f"{username}'s Room",
            'viewers': viewers,
            'thumbnail': thumbnail,
            'mmcdn_thumbnail': mmcdn_thumbnail,  # mmcdn thumbnail URL (without timestamp, JS will add it)
            'stream_url': stream_url,
            'hls_url': hls_url  # HLS stream URL for embedding
        }
        
    except requests.RequestException as e:
        logger.error(f"Error checking Chaturbate status for {username}: {e}")
        return {
            'is_live': False,
            'exists': None,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error checking Chaturbate status: {e}")
        return {
            'is_live': False,
            'exists': None,
            'error': str(e)
        }


def scrape_cloudbate_performances(username: str) -> List[Dict[str, Any]]:
    """
    Scrape cloudbate.com for past performances/videos of a user.
    Returns list of video data with preview URLs, thumbnails, etc.
    """
    performances = []
    
    try:
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': CLOUDBATE_BASE_URL
        }
        
        # Try multiple URL patterns for cloudbate
        user_urls = [
            f"{CLOUDBATE_BASE_URL}/{username}/",
            f"{CLOUDBATE_BASE_URL}/videos/{username}/",
            f"{CLOUDBATE_BASE_URL}/model/{username}/",
            f"{CLOUDBATE_BASE_URL}/performers/{username}/"
        ]
        
        for url in user_urls:
            try:
                logger.info(f"Trying to scrape: {url}")
                response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
                
                if response.status_code == 200:
                    html = response.text
                    logger.debug(f"Got HTML response, length: {len(html)}")
                    
                    # Dynamic selector discovery - find all elements with video-related attributes
                    # Pattern 1: Any img tag with data-preview (most common pattern)
                    img_patterns = [
                        r'<img[^>]*data-preview="([^"]+)"[^>]*(?:data-webp="([^"]+)"|src="([^"]+)")?[^>]*alt="([^"]*)"',
                        r'<img[^>]*src="([^"]+)"[^>]*data-preview="([^"]+)"[^>]*alt="([^"]*)"',
                        r'<img[^>]*class="[^"]*video[^"]*"[^>]*data-preview="([^"]+)"[^>]*>'
                    ]
                    
                    for pattern in img_patterns:
                        img_matches = re.finditer(pattern, html, re.DOTALL | re.IGNORECASE)
                        for match in img_matches:
                            groups = match.groups()
                            # Find preview URL (could be in different positions)
                            preview_url = None
                            thumbnail_url = None
                            title = None
                            
                            for i, group in enumerate(groups):
                                if group and 'preview' in group.lower() and group.startswith('http'):
                                    preview_url = group
                                elif group and ('.jpg' in group.lower() or '.webp' in group.lower() or '.png' in group.lower()) and group.startswith('http'):
                                    thumbnail_url = group
                                elif group and len(group) > 5 and not group.startswith('http'):
                                    title = group
                            
                            # If we found preview_url in groups, use it
                            if not preview_url:
                                for group in groups:
                                    if group and group.startswith('http') and ('preview' in group.lower() or 'cloudbate' in group.lower()):
                                        preview_url = group
                                        break
                            
                            if preview_url and preview_url.startswith('http'):
                                if preview_url not in [p['preview_url'] for p in performances]:
                                    video_id_match = re.search(r'/(\d+)/', preview_url)
                                    video_id = video_id_match.group(1) if video_id_match else None
                                    
                                    performances.append({
                                        'title': (title or f"{username} Performance").strip(),
                                        'preview_url': preview_url,
                                        'thumbnail_url': thumbnail_url,
                                        'video_id': video_id,
                                        'source': 'cloudbate'
                                    })
                    
                    # Pattern 2: Video tags with preview URLs
                    video_patterns = [
                        r'<video[^>]*src="([^"]+)"[^>]*>',
                        r'<video[^>]*data-preview="([^"]+)"[^>]*>',
                        r'<video[^>]*data-src="([^"]+)"[^>]*>'
                    ]
                    
                    for pattern in video_patterns:
                        video_matches = re.finditer(pattern, html, re.DOTALL | re.IGNORECASE)
                        for match in video_matches:
                            preview_url = match.group(1)
                            if preview_url and preview_url.startswith('http') and ('preview' in preview_url.lower() or 'cloudbate' in preview_url.lower()):
                                if preview_url not in [p['preview_url'] for p in performances]:
                                    performances.append({
                                        'title': f"{username} Performance",
                                        'preview_url': preview_url,
                                        'thumbnail_url': None,
                                        'video_id': None,
                                        'source': 'cloudbate'
                                    })
                    
                    # Pattern 3: Div containers with video data
                    div_patterns = [
                        r'<div[^>]*data-preview="([^"]+)"[^>]*>',
                        r'<div[^>]*class="[^"]*video[^"]*"[^>]*data-preview="([^"]+)"',
                        r'<div[^>]*data-video="([^"]+)"[^>]*>'
                    ]
                    
                    for pattern in div_patterns:
                        div_matches = re.finditer(pattern, html, re.DOTALL | re.IGNORECASE)
                        for match in div_matches:
                            preview_url = match.group(1)
                            if preview_url and preview_url.startswith('http'):
                                if preview_url not in [p['preview_url'] for p in performances]:
                                    performances.append({
                                        'title': f"{username} Performance",
                                        'preview_url': preview_url,
                                        'thumbnail_url': None,
                                        'video_id': None,
                                        'source': 'cloudbate'
                                    })
                    
                    # Pattern 4: Look for any URL containing preview and cloudbate
                    url_pattern = r'https://[^"\'>\s]+cloudbate[^"\'>\s]+preview[^"\'>\s]+\.(?:mp4|webm|m3u8)'
                    url_matches = re.finditer(url_pattern, html, re.IGNORECASE)
                    for match in url_matches:
                        preview_url = match.group(0)
                        if preview_url not in [p['preview_url'] for p in performances]:
                            performances.append({
                                'title': f"{username} Performance",
                                'preview_url': preview_url,
                                'thumbnail_url': None,
                                'video_id': None,
                                'source': 'cloudbate'
                            })
                    
                    # Pattern 5: JSON data embedded in script tags
                    script_pattern = r'<script[^>]*>(.*?)</script>'
                    script_matches = re.finditer(script_pattern, html, re.DOTALL | re.IGNORECASE)
                    for script_match in script_matches:
                        script_content = script_match.group(1)
                        # Look for JSON objects with preview URLs
                        json_preview_pattern = r'["\']preview["\']\s*:\s*["\']([^"\']+)["\']'
                        json_matches = re.finditer(json_preview_pattern, script_content, re.IGNORECASE)
                        for json_match in json_matches:
                            preview_url = json_match.group(1)
                            if preview_url.startswith('http') and preview_url not in [p['preview_url'] for p in performances]:
                                performances.append({
                                    'title': f"{username} Performance",
                                    'preview_url': preview_url,
                                    'thumbnail_url': None,
                                    'video_id': None,
                                    'source': 'cloudbate'
                                })
                    
                    logger.info(f"Found {len(performances)} performances from {url}")
                    
                    # If we found videos, break (don't try other URLs)
                    if performances:
                        break
                else:
                    logger.debug(f"Status code {response.status_code} for {url}")
                        
            except requests.RequestException as e:
                logger.debug(f"Error accessing {url}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error processing {url}: {e}")
                continue
        
        logger.info(f"Total performances found for {username}: {len(performances)}")
        
    except Exception as e:
        logger.error(f"Error scraping cloudbate for {username}: {e}", exc_info=True)
    
    return performances


def get_user_data(username: str) -> Dict[str, Any]:
    """
    Get comprehensive data for a user: live status + past performances.
    """
    logger.info(f"Fetching data for user: {username}")
    
    # Check live status
    live_status = check_chaturbate_live_status(username)
    
    # Scrape past performances
    performances = scrape_cloudbate_performances(username)
    
    return {
        'username': username,
        'live_status': live_status,
        'performances': performances,
        'total_performances': len(performances)
    }


@app.route('/')
def index():
    """Main landing page with input form."""
    return render_template('index.html')


@app.route('/user/<username>')
def user_page(username: str):
    """Landing page for a specific user."""
    user_data = get_user_data(username)
    return render_template('user_landing.html', user_data=user_data)


@app.route('/api/extract', methods=['POST'])
def api_extract():
    """API endpoint to extract usernames from input."""
    try:
        data = request.get_json() or {}
        input_text = data.get('input', '') or request.form.get('input', '')
        
        if not input_text:
            return jsonify({'error': 'No input provided'}), 400
        
        usernames = extract_usernames_from_input(input_text)
        
        return jsonify({
            'success': True,
            'usernames': usernames,
            'count': len(usernames)
        })
    except Exception as e:
        logger.error(f"Error in api_extract: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/<username>', methods=['GET'])
def api_user_data(username: str):
    """API endpoint to get user data."""
    try:
        user_data = get_user_data(username)
        return jsonify(user_data)
    except Exception as e:
        logger.error(f"Error in api_user_data: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/process', methods=['POST'])
def process():
    """Process input and redirect to user page(s)."""
    input_text = request.form.get('usernames', '').strip()
    
    if not input_text:
        return redirect(url_for('index'))
    
    usernames = extract_usernames_from_input(input_text)
    
    if not usernames:
        return redirect(url_for('index'))
    
    # If single username, redirect to user page
    if len(usernames) == 1:
        return redirect(url_for('user_page', username=usernames[0]))
    
    # Multiple usernames - show grid view
    return redirect(url_for('users_grid', usernames=','.join(usernames)))


@app.route('/grid')
def users_grid():
    """Display grid view of multiple users with live streams."""
    usernames_param = request.args.get('usernames', '')
    if not usernames_param:
        return redirect(url_for('index'))
    
    usernames = [u.strip() for u in usernames_param.split(',') if u.strip()]
    if not usernames:
        return redirect(url_for('index'))
    
    # Get live status for all users (in parallel would be better, but sequential for now)
    users_data = []
    for username in usernames[:50]:  # Limit to 50 users
        try:
            live_status = check_chaturbate_live_status(username)
            users_data.append({
                'username': username,
                'live_status': live_status
            })
        except Exception as e:
            logger.error(f"Error checking status for {username}: {e}")
            users_data.append({
                'username': username,
                'live_status': {'is_live': False, 'exists': None, 'error': str(e)}
            })
    
    return render_template('users_grid.html', users_data=users_data)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)

