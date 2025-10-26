import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
        logging.FileHandler('search_comparison.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SearchComparison:
    def __init__(self, query, num_results=5):
        self.query = query
        self.num_results = num_results
        self.results_dir = "comparison_results"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results directory if it doesn't exist
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            
        # Initialize browser options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # Initialize the driver
        self.driver = None

    def setup_driver(self):
        """Initialize the Chrome WebDriver"""
        try:
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            logging.info("WebDriver initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def search_google(self):
        """Perform Google search using Selenium"""
        try:
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
            
            # Extract results
            results = []
            search_results = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for result in search_results[:self.num_results]:
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, "h3")
                    link_element = result.find_element(By.CSS_SELECTOR, "a")
                    snippet_element = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                    
                    results.append({
                        "title": title_element.text,
                        "link": link_element.get_attribute("href"),
                        "snippet": snippet_element.text
                    })
                except Exception as e:
                    logging.warning(f"Failed to extract result: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logging.error(f"Google search failed: {str(e)}")
            return []

    def search_duckduckgo(self):
        """Perform DuckDuckGo search using Selenium"""
        try:
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
            
            # Extract results
            results = []
            search_results = self.driver.find_elements(By.CSS_SELECTOR, "article.react-results--main")
            
            for result in search_results[:self.num_results]:
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, "h2")
                    link_element = result.find_element(By.CSS_SELECTOR, "a")
                    snippet_element = result.find_element(By.CSS_SELECTOR, "div.react-results--snippet")
                    
                    results.append({
                        "title": title_element.text,
                        "link": link_element.get_attribute("href"),
                        "snippet": snippet_element.text
                    })
                except Exception as e:
                    logging.warning(f"Failed to extract result: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logging.error(f"DuckDuckGo search failed: {str(e)}")
            return []

    def compare_results(self, google_results, duckduckgo_results):
        """Compare and analyze search results"""
        comparison = {
            "timestamp": self.timestamp,
            "query": self.query,
            "google_results_count": len(google_results),
            "duckduckgo_results_count": len(duckduckgo_results),
            "google_results": google_results,
            "duckduckgo_results": duckduckgo_results,
            "analysis": {}
        }
        
        # Basic analysis
        comparison["analysis"]["total_results"] = len(google_results) + len(duckduckgo_results)
        comparison["analysis"]["unique_results"] = len(set(
            [r["link"] for r in google_results] + [r["link"] for r in duckduckgo_results]
        ))
        
        # Compare result overlap
        google_links = set(r["link"] for r in google_results)
        duckduckgo_links = set(r["link"] for r in duckduckgo_results)
        comparison["analysis"]["overlapping_results"] = len(google_links.intersection(duckduckgo_links))
        
        return comparison

    def save_results(self, comparison):
        """Save comparison results to file"""
        filename = f"{self.results_dir}/comparison_{self.timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {filename}")
        return filename

    def run(self):
        """Execute the full comparison workflow"""
        try:
            logging.info(f"Starting search comparison for query: {self.query}")
            
            self.setup_driver()
            
            # Perform searches
            google_results = self.search_google()
            logging.info(f"Google search completed: {len(google_results)} results")
            
            duckduckgo_results = self.search_duckduckgo()
            logging.info(f"DuckDuckGo search completed: {len(duckduckgo_results)} results")
            
            # Compare results
            comparison = self.compare_results(google_results, duckduckgo_results)
            
            # Save results
            results_file = self.save_results(comparison)
            
            # Print summary
            print("\nSearch Comparison Summary:")
            print(f"Query: {self.query}")
            print(f"Google Results: {len(google_results)}")
            print(f"DuckDuckGo Results: {len(duckduckgo_results)}")
            print(f"Total Unique Results: {comparison['analysis']['unique_results']}")
            print(f"Overlapping Results: {comparison['analysis']['overlapping_results']}")
            print(f"\nDetailed results saved to: {results_file}")
            
        except Exception as e:
            logging.error(f"Comparison workflow failed: {str(e)}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("WebDriver closed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_comparison.py <search_query> [num_results]")
        sys.exit(1)
        
    query = sys.argv[1]
    num_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    comparison = SearchComparison(query, num_results)
    comparison.run() 