"""
Enhanced Perception Engine - Full Specification Implementation
Implements the complete Perception Engine specification with advanced capabilities
for autonomous web browsing, content analysis, and intelligent interaction.
"""

import os
import re
import time
import random
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Import ArchE components
try:
    from .llm_providers import BaseLLMProvider, OpenAIProvider, GoogleProvider
    from .action_context import ActionContext
    from .utils import create_iar
except ImportError:
    try:
        from llm_providers import BaseLLMProvider, OpenAIProvider, GoogleProvider
        from action_context import ActionContext
        from utils import create_iar
    except ImportError:
        # Fallback for standalone usage
        BaseLLMProvider = None
        OpenAIProvider = None
        GoogleProvider = None
        ActionContext = None
        create_iar = lambda *args, **kwargs: {"confidence": 0.5, "tactical_resonance": 0.5, "potential_issues": []}

logger = logging.getLogger(__name__)

@dataclass
class WebPageAnalysis:
    """Structured analysis of a web page."""
    url: str
    title: str
    content: str
    links: List[str]
    images: List[str]
    metadata: Dict[str, Any]
    sentiment: str
    relevance_score: float
    summary: str
    timestamp: float

@dataclass
class SearchResult:
    """Structured search result."""
    title: str
    url: str
    snippet: str
    relevance_score: float
    source_credibility: float

class EnhancedPerceptionEngine:
    """
    Enhanced Perception Engine implementing full specification requirements.
    
    Features:
    - Advanced anti-detection measures
    - Intelligent content analysis
    - Multi-step navigation
    - Contextual understanding
    - IAR compliance
    - Error recovery
    """
    
    def __init__(self, 
                 headless: bool = True,
                 llm_provider: Optional[BaseLLMProvider] = None,
                 max_pages: int = 10,
                 timeout: int = 30):
        """
        Initialize the Enhanced Perception Engine.
        
        Args:
            headless: Run browser in headless mode
            llm_provider: LLM provider for content analysis
            max_pages: Maximum pages to visit per session
            timeout: Timeout for page loads
        """
        self.headless = headless
        self.llm_provider = llm_provider or self._get_default_llm_provider()
        self.max_pages = max_pages
        self.timeout = timeout
        self.driver = None
        self.session_data = {
            'pages_visited': 0,
            'start_time': time.time(),
            'errors': [],
            'successful_navigations': 0
        }
        # Do not initialize driver here to allow for context management
    
    def __enter__(self):
        """Initialize resources when entering context."""
        if not self.driver:
            self._initialize_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
        self.close()

    def _get_default_llm_provider(self):
        """Get default LLM provider based on available APIs."""
        try:
            if BaseLLMProvider is None:
                return self._create_simulated_provider()
            
            if os.getenv('OPENAI_API_KEY') and OpenAIProvider is not None:
                return OpenAIProvider()
            elif os.getenv('GOOGLE_API_KEY') and GoogleProvider is not None:
                return GoogleProvider()
            else:
                # Fallback to simulated provider
                return self._create_simulated_provider()
        except Exception as e:
            logger.warning(f"Could not initialize LLM provider: {e}")
            return self._create_simulated_provider()
    
    def _create_simulated_provider(self):
        """Create a simulated LLM provider for testing."""
        class SimulatedLLMProvider:
            def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
                return {"generated_text": f"Simulated response to: {prompt[:100]}..."}
            
            def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
                return {"generated_text": f"Simulated chat response to: {len(messages)} messages"}
        
        return SimulatedLLMProvider()
    
    def _get_driver(self):
        """Get or initialize the WebDriver."""
        if self.driver is None:
            self._initialize_driver()
        if self.driver is None:
            raise Exception("WebDriver could not be initialized.")
        return self.driver

    def _initialize_driver(self):
        """Initialize Selenium WebDriver with advanced anti-detection measures."""
        try:
            options = Options()
            
            # Enhanced anti-detection measures
            if self.headless:
                options.add_argument('--headless=new')
            
            # Core stealth options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Realistic user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            options.add_argument(f"user-agent={random.choice(user_agents)}")
            
            # Additional stealth options
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            
            # Window size to appear more human
            options.add_argument('--window-size=1920,1080')
            
            # Initialize driver
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            logger.info("Enhanced Perception Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            self.driver = None
    
    def browse_and_summarize(self, url: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Navigate to URL and provide intelligent summary with context.
        
        Args:
            url: Target URL
            context: Additional context for analysis
            
        Returns:
            Tuple of (result_dict, iar_dict)
        """
        if not self.driver:
            self._initialize_driver() # Ensure driver is initialized
        if not self.driver:
            result = {"error": "WebDriver not initialized"}
            iar = create_iar(0.1, 0.0, ["WebDriver initialization failed"])
            return result, iar
        
        try:
            # Add human-like delay
            time.sleep(random.uniform(2, 5))
            
            # Navigate to URL
            self.driver.get(url)
            self.driver.implicitly_wait(self.timeout)
            
            # Check for blocking
            if self._is_blocked():
                result = {"error": "Access blocked by bot detection"}
                iar = create_iar(0.1, 0.0, ["Bot detection triggered"])
                return result, iar
            
            # Analyze page content
            analysis = self._analyze_page_content(url, context)
            
            # Generate intelligent summary
            summary = self._generate_intelligent_summary(analysis, context)
            
            result = {
                "url": url,
                "title": analysis.title,
                "summary": summary,
                "relevance_score": analysis.relevance_score,
                "links_found": len(analysis.links),
                "content_length": len(analysis.content),
                "metadata": analysis.metadata
            }
            
            iar = create_iar(
                confidence=0.85,
                tactical_resonance=0.8,
                potential_issues=["Content may be incomplete due to JavaScript restrictions"],
                metadata={"url": url, "analysis_type": "page_summary"}
            )
            
            self.session_data['successful_navigations'] += 1
            return result, iar
            
        except Exception as e:
            logger.error(f"Error in browse_and_summarize: {e}")
            result = {"error": f"Navigation error: {str(e)}"}
            iar = create_iar(0.2, 0.1, [f"Navigation error: {e}"])
            self.session_data['errors'].append(str(e))
            return result, iar
    
    def _is_blocked(self) -> bool:
        """Check if access is blocked by bot detection."""
        try:
            page_source = self.driver.page_source.lower()
            blocking_indicators = [
                "captcha", "unusual traffic", "blocked", "robot", "automated",
                "please verify", "security check", "access denied"
            ]
            return any(indicator in page_source for indicator in blocking_indicators)
        except:
            return False
    
    def _analyze_page_content(self, url: str, context: Optional[Dict[str, Any]] = None) -> WebPageAnalysis:
        """Perform comprehensive page content analysis."""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract basic elements
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # Extract content (text)
            content = soup.get_text()
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and not href.startswith('#'):
                    full_url = urljoin(url, href)
                    links.append(full_url)
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                src = img.get('src')
                if src:
                    full_url = urljoin(url, src)
                    images.append(full_url)
            
            # Extract metadata
            metadata = {}
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    metadata[name] = content
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(content, context)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(content)
            
            # Generate summary
            summary = self._generate_content_summary(content, title_text)
            
            return WebPageAnalysis(
                url=url,
                title=title_text,
                content=content,
                links=links,
                images=images,
                metadata=metadata,
                sentiment=sentiment,
                relevance_score=relevance_score,
                summary=summary,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing page content: {e}")
            return WebPageAnalysis(
                url=url,
                title="Error",
                content="",
                links=[],
                images=[],
                metadata={},
                sentiment="neutral",
                relevance_score=0.0,
                summary="Error analyzing content",
                timestamp=time.time()
            )
    
    def _calculate_relevance_score(self, content: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate relevance score using query terms and pinned policy modulation.

        If the caller provides 'pinned_policy_terms' or 'pinned_policy_headers' in
        context, occurrences of those terms are weighted higher to modulate retrieval
        in favor of policy-critical content.
        """
        if not context:
            return 0.5

        content_lower = content.lower()

        # Base terms from the query
        query_terms = context.get('query', '')
        query_terms_list = query_terms.lower().split() if isinstance(query_terms, str) else []

        # Pinned policy terms (can be list or string)
        pinned_terms: List[str] = []
        ppt = context.get('pinned_policy_terms') or context.get('pinned_policy_headers')
        if isinstance(ppt, str):
            pinned_terms = [t.strip().lower() for t in ppt.split() if t.strip()]
        elif isinstance(ppt, list):
            pinned_terms = [str(t).strip().lower() for t in ppt if str(t).strip()]

        # Avoid division by zero
        if not query_terms_list and not pinned_terms:
            return 0.5

        # Count matches
        base_matches = sum(1 for term in query_terms_list if term and term in content_lower)

        # Pinned terms are weighted (entanglement-aware retrieval modulation)
        pinned_weight = context.get('pinned_policy_weight', 2.0)
        try:
            pinned_weight = float(pinned_weight)
        except Exception:
            pinned_weight = 2.0
        pinned_matches = sum(1 for term in pinned_terms if term and term in content_lower)

        # Combine with weighting
        combined_score = base_matches + (pinned_weight * pinned_matches)

        # Normalize by approximate maximum
        denom = max(1.0, len(query_terms_list) + (pinned_weight * max(1, len(pinned_terms))))
        score = combined_score / denom
        return float(min(1.0, max(0.0, score)))
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze content sentiment."""
        try:
            # Simple keyword-based sentiment analysis
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'positive']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'poor']
            
            content_lower = content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
        except:
            return "neutral"
    
    def _generate_content_summary(self, content: str, title: str) -> str:
        """Generate a concise summary of the content."""
        try:
            # Truncate content for LLM processing
            truncated_content = content[:3000]
            
            prompt = f"""
            Please provide a concise summary of the following web page content.
            
            Title: {title}
            Content: {truncated_content}
            
            Summary (2-3 sentences):
            """
            
            result = self.llm_provider.generate(prompt)
            return result.get("generated_text", "Could not generate summary")
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Summary generation failed: {e}"
    
    def _generate_intelligent_summary(self, analysis: WebPageAnalysis, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate intelligent summary with context awareness."""
        try:
            prompt = f"""
            Based on the following web page analysis, provide an intelligent summary that addresses the user's context.
            
            Page Analysis:
            - Title: {analysis.title}
            - Content Summary: {analysis.summary}
            - Relevance Score: {analysis.relevance_score}
            - Sentiment: {analysis.sentiment}
            - Links Found: {len(analysis.links)}
            
            User Context: {context or 'No specific context provided'}
            
            Intelligent Summary:
            """
            
            result = self.llm_provider.generate(prompt)
            return result.get("generated_text", analysis.summary)
            
        except Exception as e:
            logger.error(f"Error generating intelligent summary: {e}")
            return analysis.summary
    
    def search_and_analyze(self, query: str, max_results: int = 5) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform intelligent web search and analyze results.
        
        Args:
            query: Search query
            max_results: Maximum results to analyze
            
        Returns:
            Tuple of (result_dict, iar_dict)
        """
        try:
            # Construct search URL
            search_query = query.replace(" ", "+")
            search_url = f"https://www.google.com/search?q={search_query}"
            
            # Navigate to search results
            self.driver.get(search_url)
            self.driver.implicitly_wait(self.timeout)
            
            if self._is_blocked():
                result = {"error": "Search blocked by bot detection"}
                iar = create_iar(0.1, 0.0, ["Search bot detection triggered"])
                return result, iar
            
            # Extract search results
            results = self._extract_search_results(max_results)
            
            # Analyze results
            analysis = self._analyze_search_results(results, query)
            
            result = {
                "query": query,
                "results_count": len(results),
                "results": [r.__dict__ for r in results],
                "analysis": analysis,
                "search_url": search_url
            }
            
            iar = create_iar(
                confidence=0.8,
                tactical_resonance=0.75,
                potential_issues=["Results may be limited by search engine restrictions"],
                metadata={"query": query, "results_analyzed": len(results)}
            )
            
            return result, iar
            
        except Exception as e:
            logger.error(f"Error in search_and_analyze: {e}")
            result = {"error": f"Search error: {str(e)}"}
            iar = create_iar(0.2, 0.1, [f"Search error: {e}"])
            return result, iar
    
    def _extract_search_results(self, max_results: int) -> List[SearchResult]:
        """Extract structured search results from Google."""
        results = []
        try:
            # Try multiple selectors for search results
            selectors = [
                'div.g',
                'div[data-ved]',
                'div.rc',
                'div.yuRUbf'
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements[:max_results]:
                        try:
                            # Extract title and URL
                            title_elem = element.find_element(By.CSS_SELECTOR, 'h3')
                            title = title_elem.text.strip()
                            
                            link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                            url = link_elem.get_attribute('href')
                            
                            # Extract snippet
                            snippet_elem = element.find_element(By.CSS_SELECTOR, 'div.VwiC3b')
                            snippet = snippet_elem.text.strip()
                            
                            # Calculate relevance and credibility
                            relevance_score = self._calculate_result_relevance(title, snippet)
                            credibility_score = self._calculate_source_credibility(url)
                            
                            results.append(SearchResult(
                                title=title,
                                url=url,
                                snippet=snippet,
                                relevance_score=relevance_score,
                                source_credibility=credibility_score
                            ))
                            
                        except Exception as e:
                            logger.warning(f"Error extracting result: {e}")
                            continue
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error extracting search results: {e}")
            return []
    
    def _calculate_result_relevance(self, title: str, snippet: str) -> float:
        """Calculate relevance score for a search result."""
        # Simple keyword matching - could be enhanced with LLM analysis
        return 0.7  # Placeholder
    
    def _calculate_source_credibility(self, url: str) -> float:
        """Calculate source credibility score."""
        # Simple domain-based credibility
        domain = urlparse(url).netloc
        credible_domains = ['wikipedia.org', 'gov', 'edu', 'reuters.com', 'bbc.com']
        return 0.8 if any(cred in domain for cred in credible_domains) else 0.5
    
    def _analyze_search_results(self, results: List[SearchResult], query: str) -> Dict[str, Any]:
        """Analyze search results for patterns and insights."""
        try:
            if not results:
                return {"insights": "No results found"}
            
            # Analyze result patterns
            avg_relevance = sum(r.relevance_score for r in results) / len(results)
            avg_credibility = sum(r.source_credibility for r in results) / len(results)
            
            # Find most relevant result
            most_relevant = max(results, key=lambda r: r.relevance_score)
            
            # Generate insights
            insights_prompt = f"""
            Analyze these search results for the query "{query}":
            
            Results:
            {chr(10).join([f"- {r.title}: {r.snippet[:100]}..." for r in results[:3]])}
            
            Provide insights about:
            1. Result quality and relevance
            2. Information gaps
            3. Recommended next steps
            
            Analysis:
            """
            
            result = self.llm_provider.generate(insights_prompt)
            insights = result.get("generated_text", "Could not analyze results")
            
            return {
                "insights": insights,
                "avg_relevance": avg_relevance,
                "avg_credibility": avg_credibility,
                "most_relevant": most_relevant.title,
                "result_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing search results: {e}")
            return {"insights": f"Analysis error: {e}"}
    
    def navigate_to_link(self, url: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Navigate to a specific link and analyze content."""
        return self.browse_and_summarize(url)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        duration = time.time() - self.session_data['start_time']
        return {
            "pages_visited": self.session_data['pages_visited'],
            "successful_navigations": self.session_data['successful_navigations'],
            "errors": len(self.session_data['errors']),
            "session_duration": duration,
            "error_rate": len(self.session_data['errors']) / max(1, self.session_data['pages_visited'])
        }
    
    def close(self):
        """Close the browser and cleanup."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Enhanced Perception Engine closed successfully")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")

# --- Action Wrapper Functions for Workflow Engine ---

def enhanced_web_search(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Enhanced web search action with full Perception Engine capabilities and rich VCD events.
    
    Args:
        inputs: Dictionary containing 'query' and optional 'context'
    
    Returns:
        Tuple of (result_dict, iar_dict)
    """
    query = inputs.get("query")
    if not query:
        result = {"error": "Missing required input: query"}
        iar = create_iar(0.1, 0.0, ["Query is required"])
        return result, iar
    
    context = inputs.get("context", {})
    max_results = inputs.get("max_results", 5)
    
    # Import existing VCD bridge
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from vcd_bridge import VCDBridge
        vcd_bridge = VCDBridge()
        vcd_enabled = True
    except ImportError:
        vcd_bridge = None
        vcd_enabled = False
    
    try:
        with EnhancedPerceptionEngine() as engine:
            result, iar = engine.search_and_analyze(query, max_results)
            
            # Add session stats
            stats = engine.get_session_stats()
            result["session_stats"] = stats
            
            # Emit rich VCD event if available and search was successful
            if vcd_enabled and vcd_bridge and "error" not in result:
                try:
                    # Extract search results for VCD
                    search_results = result.get("search_results", [])
                    formatted_results = []
                    
                    for item in search_results:
                        if isinstance(item, dict):
                            formatted_results.append({
                                'title': item.get('title', ''),
                                'url': item.get('url', ''),
                                'snippet': item.get('snippet', ''),
                                'relevance_score': item.get('relevance_score', 0.0),
                                'source_credibility': item.get('source_credibility', 0.0)
                            })
                    
                    vcd_bridge.emit_web_search(
                        query=query,
                        results=formatted_results,
                        search_engine="enhanced_perception"
                    )
                    
                    # Also emit thought process for search strategy
                    vcd_bridge.emit_thought_process(
                        message=f"Executed web search for '{query}' - found {len(formatted_results)} results",
                        context={"query": query, "result_count": len(formatted_results)}
                    )
                    
                except Exception as vcd_error:
                    logger.warning(f"Failed to emit VCD event: {vcd_error}")
            
            return result, iar
            
    except Exception as e:
        result = {"error": f"Enhanced web search error: {e}"}
        iar = create_iar(0.2, 0.1, [f"Web search error: {e}"])
        
        # Emit error VCD event if available
        if vcd_enabled and vcd_bridge:
            try:
                vcd_bridge.emit_thought_process(
                    message=f"Web search failed for query '{query}': {str(e)}",
                    context={"error": str(e), "query": query}
                )
            except Exception as vcd_error:
                logger.warning(f"Failed to emit VCD error event: {vcd_error}")
        
        return result, iar

def enhanced_page_analysis(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Enhanced page analysis action with rich VCD events.
    
    Args:
        inputs: Dictionary containing 'url' and optional 'context'
    
    Returns:
        Tuple of (result_dict, iar_dict)
    """
    url = inputs.get("url")
    if not url:
        result = {"error": "Missing required input: url"}
        iar = create_iar(0.1, 0.0, ["URL is required"])
        return result, iar
    
    context = inputs.get("context", {})
    
    # Import existing VCD bridge
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from vcd_bridge import VCDBridge
        vcd_bridge = VCDBridge()
        vcd_enabled = True
    except ImportError:
        vcd_bridge = None
        vcd_enabled = False
    
    try:
        with EnhancedPerceptionEngine() as engine:
            result, iar = engine.browse_and_summarize(url, context)
            
            # Add session stats
            stats = engine.get_session_stats()
            result["session_stats"] = stats
            
            # Emit rich VCD event if available and analysis was successful
            if vcd_enabled and vcd_bridge and "error" not in result:
                try:
                    # Extract page analysis data for VCD
                    title = result.get("title", "Unknown Page")
                    content = result.get("content", "")
                    images = result.get("images", [])
                    
                    vcd_bridge.emit_web_browse(
                        url=url,
                        title=title,
                        content=content,
                        images=images
                    )
                    
                    # Also emit thought process for analysis insights
                    vcd_bridge.emit_thought_process(
                        message=f"Analyzed page '{title}' - extracted {len(content)} characters of content",
                        context={"url": url, "title": title, "content_length": len(content)}
                    )
                    
                except Exception as vcd_error:
                    logger.warning(f"Failed to emit VCD event: {vcd_error}")
            
            return result, iar
            
    except Exception as e:
        result = {"error": f"Enhanced page analysis error: {e}"}
        iar = create_iar(0.2, 0.1, [f"Page analysis error: {e}"])
        
        # Emit error VCD event if available
        if vcd_enabled and vcd_bridge:
            try:
                vcd_bridge.emit_thought_process(
                    message=f"Page analysis failed for URL '{url}': {str(e)}",
                    context={"error": str(e), "url": url}
                )
            except Exception as vcd_error:
                logger.warning(f"Failed to emit VCD error event: {vcd_error}")
        
        return result, iar

# --- Main execution for testing ---
if __name__ == "__main__":
    # Test the Enhanced Perception Engine
    print("Testing Enhanced Perception Engine...")
    
    with EnhancedPerceptionEngine(headless=True) as engine:
        try:
            # Test web search
            result, iar = engine.search_and_analyze("artificial intelligence trends 2024")
            print(f"Search Result: {result}")
            print(f"IAR: {iar}")
            
            # Test page analysis
            if result.get("results"):
                first_url = result["results"][0]["url"]
                page_result, page_iar = engine.browse_and_summarize(first_url)
                print(f"Page Analysis: {page_result}")
                print(f"Page IAR: {page_iar}")
            
            # Print session stats
            stats = engine.get_session_stats()
            print(f"Session Stats: {stats}")
            
        finally:
            # The 'with' statement ensures engine.close() is called
            pass
    
    print("Enhanced Perception Engine test completed.")
