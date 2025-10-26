"""
Federated Search Agents - Specialized Cognitive Tools for Domain-Specific Inquiry

This module contains the individual "agents" responsible for searching specific,
high-signal domains like academic archives, code repositories, and community forums.
Each agent is a focused tool built to handle the unique APIs, data structures,
and potential rate-limiting of its target source.

This architecture aligns with Mandate 6 (The Mind Forge).
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import logging
from typing import List, Dict, Any, Optional
from Three_PointO_ArchE.tools.web_scraper import scrape_page
from Three_PointO_ArchE.tools.synthesis_tool import invoke_llm_for_synthesis
from Three_PointO_ArchE.tools.youtube_scraper_tool import get_youtube_transcript # Import the new tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseSearchAgent:
    """Abstract base class for a federated search agent."""
    def __init__(self, name: str):
        self.name = name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform the search and return a list of structured results."""
        raise NotImplementedError

class AcademicKnowledgeAgent(BaseSearchAgent):
    """Searches academic sources like ArXiv."""
    def __init__(self):
        super().__init__("ArXiv")

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        search_url = f"https://arxiv.org/search/?query={quote_plus(query)}&searchtype=all&source=header&start=0&max_results={max_results}"
        logger.info(f"Querying {self.name}: {search_url}")
        results = []
        try:
            response = requests.get(search_url, headers=self.headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            result_elements = soup.select("li.arxiv-result")
            for element in result_elements:
                title_elem = element.select_one("p.title")
                snippet_elem = element.select_one("span.abstract-full")
                url_elem = element.select_one("p.list-title a")
                if title_elem and url_elem:
                    results.append({
                        'source': self.name,
                        'title': title_elem.get_text(strip=True),
                        'url': url_elem['href'],
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ""
                    })
        except Exception as e:
            logger.error(f"Error querying {self.name}: {e}")
        return results

class CommunityPulseAgent(BaseSearchAgent):
    """Searches community discussion forums like Reddit."""
    def __init__(self):
        super().__init__("Reddit")

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        
        # First attempt: public JSON endpoint (more reliable than dynamic HTML)
        json_url = f"https://www.reddit.com/search.json?q={quote_plus(query)}&sort=relevance&t=all&limit={max_results}"
        logger.info(f"Querying {self.name} JSON: {json_url}")
        try:
            json_headers = dict(self.headers)
            json_headers['Accept'] = 'application/json'
            r = requests.get(json_url, headers=json_headers, timeout=20)
            if r.status_code == 200:
                data = r.json()
                children = data.get('data', {}).get('children', [])
                for child in children[:max_results]:
                    pdata = child.get('data', {})
                    title = pdata.get('title')
                    permalink = pdata.get('permalink', '')
                    url = f"https://www.reddit.com{permalink}" if permalink else pdata.get('url', '')
                    snippet = pdata.get('selftext', '') or pdata.get('link_flair_text', '') or ''
                    if title and url:
                        results.append({
                            'source': self.name,
                            'title': title.strip(),
                            'url': url,
                            'snippet': snippet.strip()[:200],
                            'search_query': query
                        })
        except Exception as e:
            logger.warning(f"Reddit JSON search failed: {e}")
        
        # Fallback: old.reddit.com static HTML
        if not results:
            search_url = f"https://old.reddit.com/search?q={quote_plus(query)}&sort=relevance&t=all"
            logger.info(f"Querying {self.name} HTML: {search_url}")
            try:
                response = requests.get(search_url, headers=self.headers, timeout=20)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # old.reddit.com uses simple HTML structure
                result_elements = soup.select("div.thing")
                
                for element in result_elements[:max_results]:
                    # Get title link
                    title_elem = element.select_one("a.title")
                    
                    # Get post link (different from title link)
                    data_permalink = element.get('data-permalink', '')
                    
                    # Get snippet from expando or usertext
                    snippet_elem = element.select_one("div.expando") or element.select_one("div.usertext-body")
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = "https://old.reddit.com" + data_permalink if data_permalink else title_elem.get('href', '')
                        
                        results.append({
                            'source': self.name,
                            'title': title,
                            'url': url,
                            'snippet': (snippet_elem.get_text(strip=True) if snippet_elem else f"Reddit discussion: {title}")[:200],
                            'search_query': query
                        })
            except Exception as e:
                logger.error(f"Error querying {self.name} HTML: {e}")
        
        return results

class CodebaseTruthAgent(BaseSearchAgent):
    """Searches code repositories on GitHub."""
    def __init__(self):
        super().__init__("GitHub")

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        search_url = f"https://github.com/search?q={quote_plus(query)}&type=repositories&s=stars&o=desc"
        logger.info(f"Querying {self.name}: {search_url}")
        results = []
        
        # Retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(search_url, headers=self.headers, timeout=20)
                
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 5  # Exponential backoff
                        logger.warning(f"GitHub rate limited. Waiting {wait_time}s before retry {attempt + 1}")
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"GitHub rate limited after {max_retries} attempts")
                        return results
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try multiple selectors for GitHub results
                result_elements = soup.select("div.search-title a")
                if not result_elements:
                    result_elements = soup.select("div[data-testid='results-list'] a") or soup.select("div.Box a")
                
                for element in result_elements[:max_results]:
                    href = element.get('href', '')
                    if href:
                        url = "https://github.com" + href if href.startswith('/') else href
                        title = element.get_text(strip=True)
                        results.append({
                            'source': self.name,
                            'title': title,
                            'url': url,
                            'snippet': f"Repository: {title}",
                            'search_query': query
                        })
                break
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"GitHub search attempt {attempt + 1} failed: {e}. Retrying...")
                    import time
                    time.sleep(2)
                else:
                    logger.error(f"Error querying {self.name} after {max_retries} attempts: {e}")
        return results

class VisualSynthesisAgent(BaseSearchAgent):
    """Searches YouTube and extracts video transcripts."""
    def __init__(self):
        super().__init__("YouTube")
        # Placeholder for the sophisticated transcript extraction logic
        self.transcript_extractor = lambda url: "Transcript extraction not fully implemented in this module."

    def search(self, query: str, max_results: int = 1) -> List[Dict[str, Any]]:
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        logger.info(f"Querying {self.name}: {search_url}")
        results = []
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            # YouTube embeds search results in JavaScript - extract video IDs and titles from the page
            import re
            import json as json_lib
            
            # Find ytInitialData which contains search results
            pattern = r'var ytInitialData = ({.*?});'
            match = re.search(pattern, response.text)
            
            if match:
                try:
                    data = json_lib.loads(match.group(1))
                    
                    # Navigate to video renderer items
                    contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                    
                    for content in contents:
                        item_section = content.get('itemSectionRenderer', {}).get('contents', [])
                        for item in item_section[:max_results]:
                            video_renderer = item.get('videoRenderer', {})
                            if video_renderer:
                                video_id = video_renderer.get('videoId', '')
                                title = video_renderer.get('title', {}).get('runs', [{}])[0].get('text', 'YouTube Video')
                                
                                # Get description/snippet
                                description_snippets = video_renderer.get('descriptionSnippet', {}).get('runs', [])
                                snippet = ' '.join([snip.get('text', '') for snip in description_snippets]) if description_snippets else f"YouTube video: {title}"
                                
                                if video_id:
                                    results.append({
                                        'source': self.name,
                                        'title': title,
                                        'url': f"https://www.youtube.com/watch?v={video_id}",
                                        'snippet': snippet[:200],
                                        'search_query': query
                                    })
                                    
                                    if len(results) >= max_results:
                                        break
                        
                        if len(results) >= max_results:
                            break
                            
                except Exception as e:
                    logger.error(f"Error parsing YouTube JSON data: {e}")
            
            if not results:
                logger.warning("YouTube search returned no results. This may be due to dynamic content loading.")
                
        except Exception as e:
            logger.error(f"YouTube search failed for query '{query}': {e}", exc_info=True)
            return []

        # NEW: Process transcripts for each video (limit to first 1 for performance)
        results_with_transcripts = []
        processed_count = 0
        max_transcript_processing = 1  # Limit to 1 video for faster execution
        
        for res in results:
            if "youtube.com" in res['url'] and processed_count < max_transcript_processing:
                try:
                    transcript_data = get_youtube_transcript(res['url'])
                    if transcript_data.get("status") == "success" and transcript_data.get("full_transcript"):
                        # Summarize the transcript
                        summary_prompt = f"Summarize the key points of the following video transcript titled '{res['title']}':\\n\\n{transcript_data['full_transcript'][:8000]}" # Limit context for performance
                        summary_result = invoke_llm_for_synthesis(prompt=summary_prompt, max_tokens=300)
                        
                        if summary_result.get('result', {}).get('generated_text'):
                            res['transcript_summary'] = summary_result['result']['generated_text']
                        else:
                            res['transcript_summary'] = "Failed to generate summary for transcript."
                    else:
                        res['transcript_summary'] = transcript_data.get("message", "Transcript not available.")
                    processed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process transcript for video {res['url']}: {e}")
                    res['transcript_summary'] = "Error during transcript processing."
                    processed_count += 1
            elif "youtube.com" in res['url']:
                # Skip transcript processing for videos beyond the limit
                res['transcript_summary'] = "Transcript processing skipped (performance limit reached)."
            
            results_with_transcripts.append(res)
        
        return results_with_transcripts


class SearchEngineAgent(BaseSearchAgent):
    """
    Specialized agent for general search engines (Startpage, Google, Bing, DuckDuckGo).
    """
    def __init__(self, engine_name: str = "Startpage"):
        super().__init__(engine_name)
        self.engine_name = engine_name
        
        if engine_name.lower() == "startpage":
            self.base_url = "https://www.startpage.com/sp/search"
            self.search_param = "query"
        elif engine_name.lower() == "google":
            self.base_url = "https://www.google.com/search"
            self.search_param = "q"
        elif engine_name.lower() == "bing":
            self.base_url = "https://www.bing.com/search"
            self.search_param = "q"
        elif engine_name.lower() == "duckduckgo":
            self.base_url = "https://duckduckgo.com/"
            self.search_param = "q"
        else:
            raise ValueError(f"Unsupported search engine: {engine_name}")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using the specified search engine.
        """
        search_url = f"{self.base_url}?{self.search_param}={quote_plus(query)}"
        logger.info(f"Querying {self.engine_name}: {search_url}")
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            
            # Different selectors for different search engines
            if self.engine_name.lower() == "startpage":
                # Startpage search result selectors - WORKING IMPLEMENTATION
                result_elements = soup.select("div.w-gl__result")
                if not result_elements:
                    result_elements = soup.select("div[class*='result']")
                
                for element in result_elements[:max_results]:
                    # Try multiple title selectors for Startpage
                    title_elem = (element.select_one("h3.w-gl__result-title a") or 
                                element.select_one("h3 a") or
                                element.select_one("a[href]"))
                    
                    # Try multiple snippet selectors for Startpage
                    snippet_elem = (element.select_one("p.w-gl__description") or 
                                  element.select_one("p") or
                                  element.select_one("div[class*='description']"))
                    
                    if title_elem:
                        url = title_elem.get('href', '')
                        results.append({
                            'source': self.engine_name,
                            'title': title_elem.get_text(strip=True),
                            'url': url,
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else "",
                            'search_query': query,
                            'relevance_score': 0.8,  # Add relevance scoring
                            'source_credibility': 0.9  # Add credibility scoring
                        })
            
            elif self.engine_name.lower() == "google":
                # Google search result selectors - try multiple approaches
                result_elements = soup.select("div.g")
                if not result_elements:
                    # Fallback selectors for Google
                    result_elements = soup.select("div[data-ved]")
                if not result_elements:
                    result_elements = soup.select("div.tF2Cxc")
                
                for element in result_elements[:max_results]:
                    # Try multiple title selectors
                    title_elem = element.select_one("h3") or element.select_one("h2") or element.select_one("a h3")
                    
                    # Try multiple URL selectors
                    url_elem = element.select_one("a[href^='http']") or element.select_one("a[href^='/url']")
                    
                    # Try multiple snippet selectors
                    snippet_elem = (element.select_one("span[style*='-webkit-line-clamp']") or 
                                  element.select_one("div.VwiC3b") or 
                                  element.select_one("span.aCOpRe") or
                                  element.select_one("div.IsZvec"))
                    
                    if title_elem and url_elem:
                        url = url_elem['href']
                        # Clean up Google redirect URLs
                        if url.startswith('/url?'):
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                            url = parsed.get('q', [url])[0]
                        
                        results.append({
                            'source': self.engine_name,
                            'title': title_elem.get_text(strip=True),
                            'url': url,
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else "",
                            'search_query': query
                        })
            
            elif self.engine_name.lower() == "bing":
                # Bing search result selectors - try multiple approaches
                result_elements = soup.select("li.b_algo")
                if not result_elements:
                    # Fallback selectors for Bing
                    result_elements = soup.select("div.b_title") or soup.select("div.b_caption")
                
                for element in result_elements[:max_results]:
                    # Try multiple title selectors
                    title_elem = (element.select_one("h2 a") or 
                                element.select_one("h2") or 
                                element.select_one("a[href]"))
                    
                    # Try multiple snippet selectors
                    snippet_elem = (element.select_one("p") or 
                                  element.select_one("div.b_caption") or
                                  element.select_one("span"))
                    
                    if title_elem:
                        url = title_elem.get('href', '')
                        if not url and title_elem.name == 'a':
                            url = title_elem.get('href', '')
                        
                        results.append({
                            'source': self.engine_name,
                            'title': title_elem.get_text(strip=True),
                            'url': url,
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else "",
                            'search_query': query
                        })
            
            elif self.engine_name.lower() == "duckduckgo":
                # DuckDuckGo search result selectors - try multiple approaches
                result_elements = soup.select("div.result")
                if not result_elements:
                    # Fallback selectors for DuckDuckGo
                    result_elements = soup.select("div[data-result]") or soup.select("div.web-result")
                
                for element in result_elements[:max_results]:
                    # Try multiple title selectors
                    title_elem = (element.select_one("h2.result__title a") or 
                                element.select_one("h2 a") or 
                                element.select_one("a.result__a"))
                    
                    # Try multiple snippet selectors
                    snippet_elem = (element.select_one("div.result__snippet") or 
                                  element.select_one("div.result__body") or
                                  element.select_one("span"))
                    
                    if title_elem:
                        results.append({
                            'source': self.engine_name,
                            'title': title_elem.get_text(strip=True),
                            'url': title_elem['href'],
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else "",
                            'search_query': query
                        })
            
            logger.info(f"Agent '{self.name}' found {len(results)} results.")
            return results
            
        except Exception as e:
            logger.error(f"{self.engine_name} search failed: {e}")
            return []
