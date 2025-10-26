"""
A simple, robust web scraper tool for ArchE.
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def scrape_page(url: str, **kwargs) -> Dict[str, Any]:
    """
    [IAR Enabled]
    Scrapes the text content of a given URL.
    """
    logger.info(f"Scraping URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = "\\n".join(chunk for chunk in chunks if chunk)

        return {
            "status": "success",
            "url": url,
            "content": content[:15000] # Limit content size
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to scrape URL {url}: {e}")
        return {"status": "error", "url": url, "error": str(e)}

