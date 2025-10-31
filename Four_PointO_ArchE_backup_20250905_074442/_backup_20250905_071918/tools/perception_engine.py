from typing import Dict, Any, Tuple
import os
import re
from .utils import create_iar
from .llm_tool import generate_text
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class PerceptionEngine:
    """
    An autonomous browsing agent that combines a headless browser
    with an LLM for intelligent page analysis and interaction.
    """
    def __init__(self, headless: bool = True):
        self.driver = self._initialize_driver(headless)

    def _initialize_driver(self, headless: bool = True):
        """Initializes the Selenium WebDriver with enhanced anti-detection measures."""
        options = webdriver.ChromeOptions()
        
        # Enhanced anti-detection measures
        if headless:
            options.add_argument('--headless=new')  # Use new headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # More realistic user agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Additional stealth options
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Faster loading
        options.add_argument('--disable-javascript')  # Avoid dynamic content issues
        
        try:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            print(f"FATAL: Could not initialize WebDriver: {e}")
            return None

    def browse_and_summarize(self, url: str) -> str:
        """Navigates to a URL and provides a high-level summary of its content."""
        if not self.driver:
            return "WebDriver not initialized."
        
        try:
            # Add random delay to appear more human-like
            import time
            import random
            time.sleep(random.uniform(1, 3))
            
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            
            # Check if we hit a CAPTCHA or blocking page
            page_source = self.driver.page_source.lower()
            if "captcha" in page_source or "unusual traffic" in page_source or "blocked" in page_source:
                return f'{{"summary": "Access blocked by {url} due to bot detection. The page requires CAPTCHA verification or is blocking automated requests. This is a common issue with search engines and other sites that detect automated browsing."}}'
            
            # Try to extract search results if it's a Google search
            if "google.com/search" in url:
                return self._extract_google_search_results()
            
            # For other pages, use the original summarization
            page_content = BeautifulSoup(self.driver.page_source, 'lxml').get_text()
            
            # Use the LLM to summarize the raw text content
            summary_prompt = f"Please provide a concise summary of the following web page content:\n\n{page_content[:4000]}" # Limit context size
            
            llm_inputs = {"prompt": summary_prompt, "model": "gemini-1.5-flash"} # Use a fast model for summarization
            summary_result, _ = generate_text(llm_inputs)
            
            return summary_result.get("generated_text", "Could not summarize content.")
            
        except Exception as e:
            return f'{{"summary": "Error accessing {url}: {str(e)}"}}'
    
    def _extract_google_search_results(self) -> str:
        """Extract search results from Google search page."""
        try:
            # Look for search result elements
            results = []
            
            # Try different selectors for search results
            selectors = [
                'div.g',  # Standard Google results
                'div[data-ved]',  # Alternative selector
                'div.rc',  # Another common selector
                'h3'  # Result titles
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements("css selector", selector)
                if elements:
                    for element in elements[:5]:  # Limit to first 5 results
                        try:
                            text = element.text.strip()
                            if text and len(text) > 10:  # Filter out empty or very short results
                                results.append(text)
                        except:
                            continue
                    break
            
            if results:
                summary = f"Found {len(results)} search results: " + " | ".join(results[:3])
                return f'{{"summary": "{summary}"}}'
            else:
                return '{"summary": "No search results found on the page. The page may be blocked or the search query did not return results."}'
                
        except Exception as e:
            return f'{{"summary": "Error extracting search results: {str(e)}"}}'

    def navigate(self, url: str):
        """Navigate to a URL."""
        if self.driver:
            self.driver.get(url)
            self.driver.implicitly_wait(5)

    def wait_for(self, selector: str):
        """Wait for an element to be present."""
        if self.driver:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            except Exception as e:
                print(f"Warning: Element {selector} not found: {e}")

    def extract_text(self, selector: str) -> str:
        """Extract text from elements matching the selector."""
        if not self.driver:
            return ""
        try:
            from selenium.webdriver.common.by import By
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return " ".join([elem.text for elem in elements if elem.text])
        except Exception as e:
            print(f"Warning: Could not extract text from {selector}: {e}")
            return ""

    def click(self, selector: str):
        """Click an element matching the selector."""
        if self.driver:
            try:
                from selenium.webdriver.common.by import By
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.click()
            except Exception as e:
                print(f"Warning: Could not click {selector}: {e}")

    def type_into(self, selector: str, text: str):
        """Type text into an element matching the selector."""
        if self.driver:
            try:
                from selenium.webdriver.common.by import By
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.clear()
                element.send_keys(text)
            except Exception as e:
                print(f"Warning: Could not type into {selector}: {e}")

    def close(self):
        """Closes the browser."""
        if self.driver:
            self.driver.quit()

# --- Action Wrapper for the Workflow Engine ---

def answer_question_from_web(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    An action that uses the PerceptionEngine to answer a question by browsing the web.
    This is the first step towards a fully autonomous browsing agent.
    """
    question = inputs.get("question")
    if not question:
        result = {"error": "Missing required input: question."}
        iar = create_iar(0.1, 0.0, ["Question is required."])
        return result, iar
        
    engine = None
    try:
        engine = PerceptionEngine()
        
        # For this initial implementation, we'll do a simple search and summarize the first result.
        search_query = question.replace(" ", "+")
        search_url = f"https://www.google.com/search?q={search_query}"
        
        summary = engine.browse_and_summarize(search_url)

        # The real power will come from analyzing the search results page and deciding which link to click.
        # For now, summarizing the results page is a good first step.
        final_answer_prompt = f"Based on the following summary of a Google search results page, please provide a direct answer to the user's question.\n\nUser Question: '{question}'\n\nSearch Summary:\n{summary}"
        
        llm_inputs = {"prompt": final_answer_prompt, "model": "gemini-1.5-pro-latest"}
        final_result, _ = generate_text(llm_inputs)

        answer = final_result.get("generated_text", "Could not derive an answer from the search results.")
        
        result = {"answer": answer}
        iar = create_iar(
            confidence=0.8,
            tactical_resonance=0.85,
            potential_issues=["Answer is based on a summary of the first search results page, not a deep dive into links."],
            metadata={"question": question}
        )
        return result, iar

    except Exception as e:
        result = {"error": f"An unexpected error occurred in the Perception Engine: {e}"}
        iar = create_iar(0.1, 0.1, [f"Perception Engine Error: {e}"])
        return result, iar
    finally:
        if engine:
            engine.close()
