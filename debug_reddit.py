#!/usr/bin/env python3
"""
Debug Reddit search to understand why it's returning 0 results
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_reddit_search(query="AI safety"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Try different Reddit search URLs
    urls_to_test = [
        f"https://www.reddit.com/search/?q={quote_plus(query)}&type=link&sort=relevance&t=all",
        f"https://www.reddit.com/search/?q={quote_plus(query)}&sort=relevance",
        f"https://www.reddit.com/search/?q={quote_plus(query)}",
        f"https://old.reddit.com/search/?q={quote_plus(query)}&sort=relevance&t=all"
    ]
    
    for i, url in enumerate(urls_to_test):
        logger.info(f"Testing Reddit URL {i+1}: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=20)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response length: {len(response.text)}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save HTML for inspection
            with open(f"/tmp/reddit_debug_{i+1}.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info(f"Saved HTML to /tmp/reddit_debug_{i+1}.html")
            
            # Test different selectors
            selectors_to_test = [
                "div[data-testid='post-container']",
                "div[class*='post']",
                "article",
                "div[class*='thing']",
                "div.Post",
                "div[data-click-id='body']",
                "div[class*='scrollerItem']"
            ]
            
            for selector in selectors_to_test:
                elements = soup.select(selector)
                logger.info(f"Selector '{selector}': {len(elements)} elements found")
                if elements:
                    logger.info(f"First element text: {elements[0].get_text(strip=True)[:100]}...")
            
            # Look for any links that might be posts
            links = soup.select("a[href*='/r/']")
            logger.info(f"Found {len(links)} links with '/r/' pattern")
            if links:
                logger.info(f"First link: {links[0].get('href', '')}")
            
        except Exception as e:
            logger.error(f"Error testing Reddit URL {i+1}: {e}")

if __name__ == "__main__":
    debug_reddit_search()
