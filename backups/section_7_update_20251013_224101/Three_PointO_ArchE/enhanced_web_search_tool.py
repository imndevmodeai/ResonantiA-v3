#!/usr/bin/env python3
"""
Enhanced Web Search Tool with CAPTCHA and Login Handling
Incorporates sophisticated techniques from adult-content-seeker-pro for robust web automation.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedWebSearchTool:
    """
    Enhanced web search tool with CAPTCHA and login handling capabilities.
    Incorporates techniques from adult-content-seeker-pro for robust automation.
    """
    
    def __init__(self):
        self.driver = None
        self.profile_dir = Path(".selenium-profiles")
        self.profile_dir.mkdir(exist_ok=True)
        
        # Cookie consent selectors (from adult-content-seeker-pro)
        self.cookie_consent_selectors = [
            '#onetrust-accept-btn-handler',
            'button#accept-cookies',
            'button[aria-label*="Accept" i]',
            'button:has-text("Accept all")',
            '.fc-cta-consent',
            'button[mode="primary"][aria-label*="Accept" i]',
            '#onetrust-accept-btn-handler',
            '.cookie-accept',
            '#cookie-accept',
            'button[data-testid*="accept"]'
        ]
        
        # Age gate selectors
        self.age_gate_selectors = [
            '#disclaimer_background_accept',
            'button#disclaimer_background_accept',
            '#enterButton',
            'button:has-text("I Agree")',
            'button:has-text("Enter")',
            'button.age-verification-button',
            '#age-verification',
            '.age-gate-accept',
            'button[data-testid*="age"]'
        ]
        
        # CAPTCHA detection selectors
        self.captcha_selectors = [
            '.captcha',
            '#captcha',
            '.recaptcha',
            '#recaptcha',
            '.hcaptcha',
            '#hcaptcha',
            'iframe[src*="recaptcha"]',
            'iframe[src*="hcaptcha"]',
            '.captcha-container'
        ]
    
    def _setup_driver(self, site_key: str = "default") -> webdriver.Chrome:
        """Setup Chrome driver with stealth capabilities and persistent profile."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium not available. Install with: pip install selenium webdriver-manager")
        
        # Create site-specific profile directory
        profile_path = self.profile_dir / f"{site_key}-profile"
        profile_path.mkdir(exist_ok=True)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        
        # Stealth options (from adult-content-seeker-pro techniques)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent spoofing
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute stealth script
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _handle_cookie_consent(self, driver: webdriver.Chrome) -> bool:
        """Handle cookie consent banners using techniques from adult-content-seeker-pro."""
        try:
            for selector in self.cookie_consent_selectors:
                try:
                    # Try different selector strategies
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if not elements:
                        # Try XPath for text-based selectors
                        if "has-text" in selector:
                            text = selector.split('"')[1]
                            elements = driver.find_elements(By.XPATH, f"//button[contains(text(), '{text}')]")
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(0.5)  # Wait for banner to disappear
                            logger.info(f"Clicked cookie consent: {selector}")
                            return True
                except Exception as e:
                    logger.debug(f"Cookie consent selector {selector} failed: {e}")
                    continue
            return False
        except Exception as e:
            logger.warning(f"Cookie consent handling failed: {e}")
            return False
    
    def _handle_age_gate(self, driver: webdriver.Chrome, site_key: str = "") -> bool:
        """Handle age verification gates using site-specific techniques."""
        try:
            # Get domain-specific selectors
            current_url = driver.current_url
            domain = ""
            try:
                from urllib.parse import urlparse
                domain = urlparse(current_url).hostname.lower()
            except:
                pass
            
            selectors = self.age_gate_selectors.copy()
            
            # Add site-specific selectors (from adult-content-seeker-pro)
            if 'redtube' in domain:
                selectors.extend(['#warning', '#age-verification'])
            elif 'xvideos' in domain:
                selectors.extend(['#disclaimer_background_accept'])
            elif 'xnxx' in domain:
                selectors.extend(['#disclaimer_background_accept'])
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if not elements:
                        # Try XPath for text-based selectors
                        if "has-text" in selector:
                            text = selector.split('"')[1]
                            elements = driver.find_elements(By.XPATH, f"//button[contains(text(), '{text}')]")
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(1.0)  # Wait for page transition
                            logger.info(f"Clicked age gate: {selector}")
                            return True
                except Exception as e:
                    logger.debug(f"Age gate selector {selector} failed: {e}")
                    continue
            return False
        except Exception as e:
            logger.warning(f"Age gate handling failed: {e}")
            return False
    
    def _detect_captcha(self, driver: webdriver.Chrome) -> bool:
        """Detect if page contains CAPTCHA challenges."""
        try:
            for selector in self.captcha_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.warning(f"CAPTCHA detected: {selector}")
                    return True
            return False
        except Exception as e:
            logger.debug(f"CAPTCHA detection failed: {e}")
            return False
    
    def _wait_for_page_load(self, driver: webdriver.Chrome, timeout: int = 10) -> bool:
        """Wait for page to fully load and handle common obstacles."""
        try:
            # Wait for DOM to be ready
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Handle cookie consent
            self._handle_cookie_consent(driver)
            time.sleep(0.5)
            
            # Handle age gates
            self._handle_age_gate(driver)
            time.sleep(0.5)
            
            # Check for CAPTCHA
            if self._detect_captcha(driver):
                logger.warning("CAPTCHA detected - manual intervention may be required")
                return False
            
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False
        except Exception as e:
            logger.warning(f"Page load handling failed: {e}")
            return False
    
    def search_with_selenium(self, query: str, num_results: int = 10, site_key: str = "search") -> Dict[str, Any]:
        """Perform web search using Selenium with enhanced obstacle handling."""
        start_time = time.time()
        
        try:
            driver = self._setup_driver(site_key)
            
            # Navigate to search engine
            search_url = f"https://www.google.com/search?q={query}"
            driver.get(search_url)
            
            # Wait for page load and handle obstacles
            if not self._wait_for_page_load(driver):
                return {
                    "error": "Page load failed or CAPTCHA detected",
                    "search_results": [],
                    "reflection": {
                        "status": "failure",
                        "message": "Page load failed or CAPTCHA detected",
                        "confidence": 0.1,
                        "potential_issues": ["CAPTCHA", "Page load timeout"]
                    }
                }
            
            # Extract search results
            results = []
            try:
                # Wait for search results to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
                )
                
                # Extract result elements
                result_elements = driver.find_elements(By.CSS_SELECTOR, "div.g")
                
                for element in result_elements[:num_results]:
                    try:
                        # Extract title
                        title_element = element.find_element(By.CSS_SELECTOR, "h3")
                        title = title_element.text
                        
                        # Extract URL
                        link_element = element.find_element(By.CSS_SELECTOR, "a")
                        url = link_element.get_attribute("href")
                        
                        # Extract snippet
                        snippet_element = element.find_element(By.CSS_SELECTOR, ".VwiC3b")
                        snippet = snippet_element.text
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                    except Exception as e:
                        logger.debug(f"Failed to extract result: {e}")
                        continue
                        
            except TimeoutException:
                logger.warning("Search results not found")
            
            driver.quit()
            
            execution_time = time.time() - start_time
            
            return {
                "search_results": results,
                "reflection": {
                    "status": "success",
                    "message": f"Found {len(results)} results using enhanced Selenium search",
                    "confidence": 0.9 if len(results) > 0 else 0.3,
                    "execution_time": execution_time,
                    "potential_issues": [] if len(results) > 0 else ["No results found"]
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced Selenium search failed: {e}")
            return {
                "error": str(e),
                "search_results": [],
                "reflection": {
                    "status": "failure",
                    "message": f"Enhanced Selenium search failed: {str(e)}",
                    "confidence": 0.1,
                    "potential_issues": [type(e).__name__]
                }
            }
    
    def search_with_requests(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Fallback search using requests and BeautifulSoup."""
        if not REQUESTS_AVAILABLE:
            return {
                "error": "Requests library not available",
                "search_results": [],
                "reflection": {
                    "status": "failure",
                    "message": "Requests library not available",
                    "confidence": 0.0,
                    "potential_issues": ["Missing dependency"]
                }
            }
        
        start_time = time.time()
        
        try:
            # Use DuckDuckGo for fallback (no CAPTCHA issues)
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract DuckDuckGo results
            result_elements = soup.find_all('div', class_='result')
            
            for element in result_elements[:num_results]:
                try:
                    title_element = element.find('a', class_='result__a')
                    snippet_element = element.find('a', class_='result__snippet')
                    
                    if title_element:
                        title = title_element.text.strip()
                        url = title_element.get('href', '')
                        snippet = snippet_element.text.strip() if snippet_element else ''
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                except Exception as e:
                    logger.debug(f"Failed to extract DuckDuckGo result: {e}")
                    continue
            
            execution_time = time.time() - start_time
            
            return {
                "search_results": results,
                "reflection": {
                    "status": "success",
                    "message": f"Found {len(results)} results using DuckDuckGo fallback",
                    "confidence": 0.8 if len(results) > 0 else 0.2,
                    "execution_time": execution_time,
                    "potential_issues": [] if len(results) > 0 else ["No results found"]
                }
            }
            
        except Exception as e:
            logger.error(f"DuckDuckGo fallback search failed: {e}")
            return {
                "error": str(e),
                "search_results": [],
                "reflection": {
                    "status": "failure",
                    "message": f"DuckDuckGo fallback search failed: {str(e)}",
                    "confidence": 0.1,
                    "potential_issues": [type(e).__name__]
                }
            }

def enhanced_search_web(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced web search with CAPTCHA and login handling capabilities.
    Incorporates sophisticated techniques from adult-content-seeker-pro.
    
    Args:
        inputs (Dict): A dictionary containing:
            - query (str): Search query string.
            - num_results (int): Number of results to return.
            - provider (str): The search provider ('enhanced' for Selenium, 'duckduckgo' for fallback).
            - site_key (str): Site-specific profile key for persistent sessions.
        
    Returns:
        Dictionary containing search results and a compliant IAR reflection.
    """
    start_time = time.time()
    
    # Input validation
    query = inputs.get('query', '').strip()
    if not query:
        return {
            "error": "Input 'query' is required.",
            "search_results": [],
            "reflection": {
                "status": "failure",
                "message": "Input validation failed: 'query' is required.",
                "confidence": 0.0,
                "potential_issues": ["Missing required input"]
            }
        }
    
    num_results = inputs.get('num_results', 10)
    provider = inputs.get('provider', 'enhanced')
    site_key = inputs.get('site_key', 'default')
    
    # Initialize enhanced search tool
    search_tool = EnhancedWebSearchTool()
    
    try:
        if provider == 'enhanced' and SELENIUM_AVAILABLE:
            # Use enhanced Selenium search with obstacle handling
            result = search_tool.search_with_selenium(query, num_results, site_key)
        else:
            # Use fallback DuckDuckGo search
            result = search_tool.search_with_requests(query, num_results)
        
        # Add execution metadata
        result['reflection']['execution_time'] = time.time() - start_time
        result['reflection']['search_method'] = provider
        
        return result
        
    except Exception as e:
        logger.error(f"Enhanced web search failed: {e}")
        return {
            "error": str(e),
            "search_results": [],
            "reflection": {
                "status": "failure",
                "message": f"Enhanced web search failed: {str(e)}",
                "confidence": 0.1,
                "execution_time": time.time() - start_time,
                "potential_issues": [type(e).__name__]
            }
        }

if __name__ == "__main__":
    # Test the enhanced search tool
    test_inputs = {
        "query": "artificial intelligence trends 2024",
        "num_results": 5,
        "provider": "enhanced",
        "site_key": "test"
    }
    
    result = enhanced_search_web(test_inputs)
    print(json.dumps(result, indent=2))


