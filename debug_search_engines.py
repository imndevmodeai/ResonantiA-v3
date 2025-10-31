#!/usr/bin/env python3
"""
Debug script to test search engine selectors
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_engine(engine_name, query="AI safety"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    if engine_name.lower() == "google":
        url = f"https://www.google.com/search?q={quote_plus(query)}"
    elif engine_name.lower() == "bing":
        url = f"https://www.bing.com/search?q={quote_plus(query)}"
    elif engine_name.lower() == "duckduckgo":
        url = f"https://duckduckgo.com/?q={quote_plus(query)}"
    else:
        return
    
    logger.info(f"Testing {engine_name}: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response length: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Save HTML for inspection
        with open(f"/tmp/{engine_name.lower()}_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        logger.info(f"Saved HTML to /tmp/{engine_name.lower()}_debug.html")
        
        # Test different selectors
        if engine_name.lower() == "google":
            selectors_to_test = [
                "div.g",
                "div[data-ved]",
                "div.tF2Cxc",
                "h3",
                "a[href^='http']"
            ]
        elif engine_name.lower() == "bing":
            selectors_to_test = [
                "li.b_algo",
                "div.b_title",
                "div.b_caption",
                "h2 a",
                "h2"
            ]
        elif engine_name.lower() == "duckduckgo":
            selectors_to_test = [
                "div.result",
                "div[data-result]",
                "div.web-result",
                "h2.result__title a",
                "h2 a"
            ]
        
        for selector in selectors_to_test:
            elements = soup.select(selector)
            logger.info(f"Selector '{selector}': {len(elements)} elements found")
            if elements:
                logger.info(f"First element: {elements[0].get_text(strip=True)[:100]}...")
        
    except Exception as e:
        logger.error(f"Error testing {engine_name}: {e}")

if __name__ == "__main__":
    test_search_engine("Google")
    test_search_engine("Bing") 
    test_search_engine("DuckDuckGo")
