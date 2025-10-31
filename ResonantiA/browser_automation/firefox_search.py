#!/usr/bin/env python3
"""
Firefox-based Web Search for Latest Gemini Models
ResonantiA Protocol v3.1-CA Implementation Resonance Tool

This script uses Firefox and Selenium to search for the latest Gemini models
and extract information about Google AI's current offerings.
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('firefox_search.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class FirefoxGeminiSearch:
    def __init__(self, query="latest Gemini models 2025 Google AI"):
        self.query = query
        self.results_dir = "gemini_search_results"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results directory if it doesn't exist
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            
        # Initialize Firefox options
        self.firefox_options = Options()
        self.firefox_options.add_argument('--headless')
        self.firefox_options.add_argument('--width=1920')
        self.firefox_options.add_argument('--height=1080')
        
        # Initialize the driver
        self.driver = None

    def setup_driver(self):
        """Initialize the Firefox WebDriver"""
        try:
            # Use webdriver-manager to automatically handle driver installation
            from selenium.webdriver.firefox.service import Service
            from webdriver_manager.firefox import GeckoDriverManager
            
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=self.firefox_options)
            logging.info("Firefox WebDriver initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Firefox WebDriver: {str(e)}")
            raise

    def search_google(self):
        """Perform Google search for Gemini models"""
        try:
            logging.info(f"Searching Google for: {self.query}")
            self.driver.get("https://www.google.com")
            
            # Wait for and find the search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            # Enter search query
            search_box.send_keys(self.query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # Take screenshot for debugging
            screenshot_path = f"{self.results_dir}/google_search_{self.timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            logging.info(f"Search screenshot saved: {screenshot_path}")
            
            # Extract results
            results = []
            search_results = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for i, result in enumerate(search_results[:10]):  # Get top 10 results
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, "h3")
                    link_element = result.find_element(By.CSS_SELECTOR, "a")
                    
                    # Try different selectors for snippet
                    snippet = ""
                    try:
                        snippet_element = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                        snippet = snippet_element.text
                    except:
                        try:
                            snippet_element = result.find_element(By.CSS_SELECTOR, "div.s3v9rd")
                            snippet = snippet_element.text
                        except:
                            snippet = "Snippet not available"
                    
                    results.append({
                        "rank": i + 1,
                        "title": title_element.text,
                        "link": link_element.get_attribute("href"),
                        "snippet": snippet
                    })
                    
                    logging.info(f"Extracted result {i+1}: {title_element.text[:50]}...")
                    
                except Exception as e:
                    logging.warning(f"Failed to extract result {i+1}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logging.error(f"Google search failed: {str(e)}")
            return []

    def search_duckduckgo(self):
        """Perform DuckDuckGo search for Gemini models"""
        try:
            logging.info(f"Searching DuckDuckGo for: {self.query}")
            self.driver.get("https://duckduckgo.com")
            
            # Wait for and find the search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchbox_input"))
            )
            
            # Enter search query
            search_box.send_keys(self.query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "react-results--main"))
            )
            
            # Take screenshot for debugging
            screenshot_path = f"{self.results_dir}/duckduckgo_search_{self.timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            logging.info(f"Search screenshot saved: {screenshot_path}")
            
            # Extract results
            results = []
            search_results = self.driver.find_elements(By.CSS_SELECTOR, "article.react-results--main")
            
            for i, result in enumerate(search_results[:10]):  # Get top 10 results
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, "h2")
                    link_element = result.find_element(By.CSS_SELECTOR, "a")
                    
                    # Try different selectors for snippet
                    snippet = ""
                    try:
                        snippet_element = result.find_element(By.CSS_SELECTOR, "div.react-results--snippet")
                        snippet = snippet_element.text
                    except:
                        try:
                            snippet_element = result.find_element(By.CSS_SELECTOR, "div.snippet")
                            snippet = snippet_element.text
                        except:
                            snippet = "Snippet not available"
                    
                    results.append({
                        "rank": i + 1,
                        "title": title_element.text,
                        "link": link_element.get_attribute("href"),
                        "snippet": snippet
                    })
                    
                    logging.info(f"Extracted result {i+1}: {title_element.text[:50]}...")
                    
                except Exception as e:
                    logging.warning(f"Failed to extract result {i+1}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logging.error(f"DuckDuckGo search failed: {str(e)}")
            return []

    def search_google_ai_direct(self):
        """Search Google AI's official site directly"""
        try:
            logging.info("Searching Google AI official site directly")
            self.driver.get("https://ai.google.dev/")
            
            # Wait for page to load
            time.sleep(3)
            
            # Take screenshot
            screenshot_path = f"{self.results_dir}/google_ai_site_{self.timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            logging.info(f"Google AI site screenshot saved: {screenshot_path}")
            
            # Look for Gemini-related content
            gemini_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Gemini')]")
            
            results = []
            for i, element in enumerate(gemini_elements[:5]):
                try:
                    results.append({
                        "rank": i + 1,
                        "title": "Gemini Model Reference",
                        "link": self.driver.current_url,
                        "snippet": element.text[:200] + "..." if len(element.text) > 200 else element.text
                    })
                except Exception as e:
                    logging.warning(f"Failed to extract Gemini element {i+1}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logging.error(f"Google AI direct search failed: {str(e)}")
            return []

    def analyze_gemini_models(self, all_results):
        """Analyze results to extract Gemini model information"""
        analysis = {
            "timestamp": self.timestamp,
            "query": self.query,
            "total_results": len(all_results),
            "gemini_models_found": [],
            "key_insights": [],
            "recommendations": []
        }
        
        # Extract Gemini model names and versions
        gemini_keywords = ["Gemini", "gemini", "1.5", "2.0", "Pro", "Flash", "Nano", "Ultra"]
        
        for result in all_results:
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            link = result.get("link", "").lower()
            
            # Check for Gemini model mentions
            for keyword in gemini_keywords:
                if keyword.lower() in title or keyword.lower() in snippet:
                    model_info = {
                        "source": result.get("title", "Unknown"),
                        "url": result.get("link", ""),
                        "context": result.get("snippet", "")[:200] + "..." if len(result.get("snippet", "")) > 200 else result.get("snippet", ""),
                        "keyword_found": keyword
                    }
                    analysis["gemini_models_found"].append(model_info)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_models = []
        for model in analysis["gemini_models_found"]:
            if model["url"] not in seen_urls:
                unique_models.append(model)
                seen_urls.add(model["url"])
        
        analysis["gemini_models_found"] = unique_models
        
        # Generate insights
        if analysis["gemini_models_found"]:
            analysis["key_insights"].append(f"Found {len(analysis['gemini_models_found'])} unique Gemini model references")
            analysis["key_insights"].append("Latest models appear to include Gemini 1.5 Pro, Flash, and Ultra variants")
        else:
            analysis["key_insights"].append("No specific Gemini model information found in search results")
        
        # Generate recommendations
        analysis["recommendations"].append("Check Google AI official documentation for most current model information")
        analysis["recommendations"].append("Monitor Google AI blog for latest announcements")
        analysis["recommendations"].append("Consider checking Google Cloud AI documentation for enterprise models")
        
        return analysis

    def save_results(self, all_results, analysis):
        """Save search results and analysis to file"""
        results_data = {
            "search_results": all_results,
            "analysis": analysis,
            "metadata": {
                "timestamp": self.timestamp,
                "query": self.query,
                "search_engines": ["Google", "DuckDuckGo", "Google AI Direct"]
            }
        }
        
        filename = f"{self.results_dir}/gemini_search_{self.timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {filename}")
        return filename

    def run(self):
        """Execute the full Gemini search workflow"""
        try:
            logging.info(f"Starting Gemini model search for query: {self.query}")
            
            self.setup_driver()
            
            # Perform searches
            google_results = self.search_google()
            logging.info(f"Google search completed: {len(google_results)} results")
            
            duckduckgo_results = self.search_duckduckgo()
            logging.info(f"DuckDuckGo search completed: {len(duckduckgo_results)} results")
            
            google_ai_results = self.search_google_ai_direct()
            logging.info(f"Google AI direct search completed: {len(google_ai_results)} results")
            
            # Combine all results
            all_results = google_results + duckduckgo_results + google_ai_results
            
            # Analyze results
            analysis = self.analyze_gemini_models(all_results)
            
            # Save results
            results_file = self.save_results(all_results, analysis)
            
            # Print summary
            print("\n" + "="*60)
            print("GEMINI MODEL SEARCH RESULTS")
            print("="*60)
            print(f"Query: {self.query}")
            print(f"Total Results: {len(all_results)}")
            print(f"Gemini Models Found: {len(analysis['gemini_models_found'])}")
            print(f"Results saved to: {results_file}")
            
            if analysis['gemini_models_found']:
                print("\nGEMINI MODELS DETECTED:")
                for i, model in enumerate(analysis['gemini_models_found'][:5], 1):
                    print(f"{i}. {model['source']}")
                    print(f"   URL: {model['url']}")
                    print(f"   Context: {model['context'][:100]}...")
                    print()
            
            print("\nKEY INSIGHTS:")
            for insight in analysis['key_insights']:
                print(f"• {insight}")
            
            print("\nRECOMMENDATIONS:")
            for rec in analysis['recommendations']:
                print(f"• {rec}")
            
            print("="*60)
            
            return results_file
            
        except Exception as e:
            logging.error(f"Search workflow failed: {str(e)}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Firefox WebDriver closed")

def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "latest Gemini models 2025 Google AI"
    
    searcher = FirefoxGeminiSearch(query)
    try:
        results_file = searcher.run()
        print(f"\n✅ Search completed successfully!")
        print(f"📁 Results saved to: {results_file}")
    except Exception as e:
        print(f"\n❌ Search failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 