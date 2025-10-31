"""
Enhanced Perception Engine with Fallback Search Integration
Combines the advanced capabilities of the Enhanced Perception Engine with the 
proven reliability of the Fallback Search Tool's HTTP-based approach.
"""

import os
import re
import time
import random
import json
import logging
import subprocess
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

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
        create_iar = lambda confidence, tactical_resonance, potential_issues=None, metadata=None: {
            "status": "Success",
            "summary": "Web search completed with fallback mechanism",
            "confidence": confidence, 
            "alignment_check": {"objective_alignment": 1.0, "protocol_alignment": 1.0},
            "potential_issues": potential_issues if potential_issues is not None else [],
            "raw_output_preview": f"{{'confidence': {confidence}, 'tactical_resonance': {tactical_resonance}}}"
        }

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

class EnhancedPerceptionEngineWithFallback:
    """
    Enhanced Perception Engine that combines advanced capabilities with reliable fallback search.
    
    Key Features:
    - HTTP-based search using proven wget approach (from fallback search)
    - Advanced content analysis and LLM integration
    - Intelligent result parsing and relevance scoring
    - IAR compliance and error handling
    - Fallback mechanisms for reliability
    """
    
    def __init__(self, 
                 llm_provider: Optional[BaseLLMProvider] = None,
                 max_results: int = 10,
                 timeout: int = 30,
                 use_fallback_search: bool = True):
        """
        Initialize the Enhanced Perception Engine with Fallback.
        
        Args:
            llm_provider: LLM provider for content analysis
            max_results: Maximum results to analyze
            timeout: Timeout for HTTP requests
            use_fallback_search: Use HTTP-based search instead of browser automation
        """
        self.llm_provider = llm_provider or self._get_default_llm_provider()
        self.max_results = max_results
        self.timeout = timeout
        self.use_fallback_search = use_fallback_search
        self.session_data = {
            'searches_performed': 0,
            'start_time': time.time(),
            'errors': [],
            'successful_searches': 0,
            'total_results_found': 0
        }
        self.search_stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "average_response_time": 0.0
        }
    
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
    
    def search_and_analyze(self, query: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform intelligent web search and analyze results using HTTP-based approach.
        
        Args:
            query: Search query
            context: Additional context for analysis
            
        Returns:
            Tuple of (result_dict, iar_dict)
        """
        start_time = time.time()
        self.search_stats["total_searches"] += 1
        self.session_data['searches_performed'] += 1
        
        try:
            logger.info(f"Performing enhanced search: '{query}'")
            
            # Use HTTP-based search (proven approach from fallback search)
            if self.use_fallback_search:
                results = self._search_duckduckgo_http(query)
            else:
                results = self._search_google_http(query)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            if results:
                # Update statistics
                self.search_stats["successful_searches"] += 1
                self.session_data['successful_searches'] += 1
                self.session_data['total_results_found'] += len(results)
                self._update_average_response_time(response_time)
                
                # Enhanced analysis of results
                enhanced_results = self._enhance_search_results(results, query, context)
                
                # Generate intelligent analysis
                analysis = self._analyze_search_results_intelligently(enhanced_results, query, context)
                
                result = {
                    "success": True,
                    "query": query,
                    "engine": "enhanced_perception_with_fallback",
                    "total_results": len(enhanced_results),
                    "response_time": response_time,
                    "results": [r.__dict__ for r in enhanced_results],
                    "analysis": analysis,
                    "timestamp": time.time(),
                    "tool": "enhanced_perception_engine_with_fallback",
                    "version": "1.0.0"
                }
                
                iar = create_iar(
                    confidence=0.85,
                    tactical_resonance=0.8,
                    potential_issues=["Results based on HTTP search, may miss dynamic content"],
                    metadata={"query": query, "results_analyzed": len(enhanced_results), "method": "http_fallback"}
                )
                
                logger.info(f"Enhanced search completed: {len(results)} results in {response_time:.2f}s")
                return result, iar
            else:
                return self._create_error_result(query, "enhanced_perception", "No results found")
                
        except Exception as e:
            logger.error(f"Enhanced search error: {e}")
            self.search_stats["failed_searches"] += 1
            self.session_data['errors'].append(str(e))
            return self._create_error_result(query, "enhanced_perception", f"Search error: {e}")
    
    def _search_duckduckgo_http(self, query: str) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo using HTTP requests (proven approach from fallback search).
        """
        try:
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            # Use wget to fetch the page (proven reliable approach)
            cmd = [
                "wget", 
                "-q", 
                "-O", "-",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--timeout=30",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"wget failed: {result.stderr}")
                return []
            
            # Parse the HTML response
            html = result.stdout
            return self._parse_duckduckgo_html(html)
            
        except subprocess.TimeoutExpired:
            logger.error("wget timeout")
            return []
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def _search_google_http(self, query: str) -> List[Dict[str, str]]:
        """
        Search Google using HTTP requests as alternative.
        """
        try:
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            # Use wget to fetch the page
            cmd = [
                "wget", 
                "-q", 
                "-O", "-",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--timeout=30",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"wget failed: {result.stderr}")
                return []
            
            # Parse the HTML response
            html = result.stdout
            return self._parse_google_html(html)
            
        except subprocess.TimeoutExpired:
            logger.error("wget timeout")
            return []
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
    
    def _parse_duckduckgo_html(self, html: str) -> List[Dict[str, str]]:
        """
        Parse DuckDuckGo HTML to extract search results (enhanced version of fallback search).
        """
        results = []
        
        try:
            # Look for result patterns in the HTML
            # Enhanced patterns for better extraction
            
            # Primary pattern for links and titles
            link_patterns = [
                r'<a[^>]*href="([^"]*)"[^>]*class="[^"]*result__title[^"]*"[^>]*>([^<]*)</a>',
                r'<h2[^>]*class="[^"]*result__title[^"]*"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>',
                r'<a[^>]*href="([^"]*)"[^>]*class="[^"]*result__a[^"]*"[^>]*>([^<]*)</a>'
            ]
            
            for pattern in link_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                
                for match in matches[:self.max_results]:
                    link, title = match
                    
                    # Clean up the title
                    title = re.sub(r'<[^>]*>', '', title).strip()
                    
                    # Skip if empty or invalid
                    if not title or not link or link.startswith('#'):
                        continue
                    
                    # Fix DuckDuckGo redirect URLs
                    link = self._fix_duckduckgo_url(link)
                    
                    # Try to find description near this result
                    description = self._find_description_near_title(html, title)
                    
                    results.append({
                        "title": title,
                        "link": link,
                        "description": description
                    })
                
                if results:  # If we found results with this pattern, use them
                    break
            
            # If still no results, try alternative patterns
            if not results:
                # Alternative pattern for different HTML structure
                alt_pattern = r'<div[^>]*class="[^"]*result[^"]*"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
                alt_matches = re.findall(alt_pattern, html, re.IGNORECASE | re.DOTALL)
                
                for match in alt_matches[:self.max_results]:
                    link, title = match
                    title = re.sub(r'<[^>]*>', '', title).strip()
                    
                    if title and link and not link.startswith('#'):
                        # Fix DuckDuckGo redirect URLs
                        link = self._fix_duckduckgo_url(link)
                        results.append({
                            "title": title,
                            "link": link,
                            "description": ""
                        })
            
        except Exception as e:
            logger.error(f"HTML parsing error: {e}")
        
        return results
    
    def _fix_duckduckgo_url(self, url: str) -> str:
        """
        Fix DuckDuckGo redirect URLs to extract the actual destination URL.
        """
        try:
            # Handle DuckDuckGo redirect URLs
            if 'duckduckgo.com/l/?uddg=' in url:
                # Extract the encoded URL
                import urllib.parse
                # Find the uddg parameter
                parsed = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed.query)
                
                if 'uddg' in query_params:
                    encoded_url = query_params['uddg'][0]
                    # Decode the URL
                    decoded_url = urllib.parse.unquote(encoded_url)
                    return decoded_url
            
            # Handle relative URLs
            if url.startswith('//'):
                return 'https:' + url
            
            # Handle URLs without scheme
            if not url.startswith(('http://', 'https://')):
                return 'https://' + url
            
            return url
            
        except Exception as e:
            logger.warning(f"Error fixing DuckDuckGo URL: {e}")
            return url
    
    def _parse_google_html(self, html: str) -> List[Dict[str, str]]:
        """
        Parse Google HTML to extract search results.
        """
        results = []
        
        try:
            # Google search result patterns
            patterns = [
                r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>',
                r'<div[^>]*class="[^"]*g[^"]*"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                
                for match in matches[:self.max_results]:
                    link, title = match
                    title = re.sub(r'<[^>]*>', '', title).strip()
                    
                    if title and link and not link.startswith('#'):
                        description = self._find_description_near_title(html, title)
                        results.append({
                            "title": title,
                            "link": link,
                            "description": description
                        })
                
                if results:
                    break
            
        except Exception as e:
            logger.error(f"Google HTML parsing error: {e}")
        
        return results
    
    def _find_description_near_title(self, html: str, title: str) -> str:
        """
        Try to find a description snippet near the title (enhanced version).
        """
        try:
            # Look for snippet patterns
            snippet_patterns = [
                r'class="[^"]*result__snippet[^"]*"[^>]*>([^<]*)</span>',
                r'class="[^"]*snippet[^"]*"[^>]*>([^<]*)</span>',
                r'<span[^>]*class="[^"]*st[^"]*"[^>]*>([^<]{50,200})</span>',
                r'<div[^>]*class="[^"]*VwiC3b[^"]*"[^>]*>([^<]*)</div>'
            ]
            
            for pattern in snippet_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    return matches[0].strip()
            
            return ""
            
        except Exception:
            return ""
    
    def _enhance_search_results(self, results: List[Dict], query: str, context: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Enhance search results with relevance scoring and credibility analysis.
        """
        enhanced_results = []
        
        for result in results:
            # Calculate relevance score
            relevance_score = self._calculate_result_relevance(result['title'], result['description'], query, context)
            
            # Calculate source credibility
            credibility_score = self._calculate_source_credibility(result['link'])
            
            enhanced_results.append(SearchResult(
                title=result['title'],
                url=result['link'],
                snippet=result['description'],
                relevance_score=relevance_score,
                source_credibility=credibility_score
            ))
        
        # Sort by relevance score
        enhanced_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return enhanced_results
    
    def _calculate_result_relevance(self, title: str, snippet: str, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate relevance score for a search result (enhanced version).
        """
        try:
            query_terms = query.lower().split()
            title_lower = title.lower()
            snippet_lower = snippet.lower()
            
            # Base relevance from title matches
            title_matches = sum(1 for term in query_terms if term in title_lower)
            title_score = title_matches / len(query_terms) if query_terms else 0
            
            # Snippet relevance
            snippet_matches = sum(1 for term in query_terms if term in snippet_lower)
            snippet_score = snippet_matches / len(query_terms) if query_terms else 0
            
            # Context-based relevance (pinned policy terms)
            context_score = 0.0
            if context:
                pinned_terms = context.get('pinned_policy_terms', [])
                if isinstance(pinned_terms, str):
                    pinned_terms = pinned_terms.split()
                
                pinned_weight = context.get('pinned_policy_weight', 2.0)
                pinned_matches = sum(1 for term in pinned_terms if term.lower() in title_lower or term.lower() in snippet_lower)
                context_score = (pinned_matches * pinned_weight) / max(1, len(pinned_terms)) if pinned_terms else 0
            
            # Combine scores
            total_score = (title_score * 0.6) + (snippet_score * 0.3) + (context_score * 0.1)
            
            return min(1.0, max(0.0, total_score))
            
        except Exception:
            return 0.5
    
    def _calculate_source_credibility(self, url: str) -> float:
        """
        Calculate source credibility score (enhanced version).
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            # High credibility domains
            high_credibility = ['wikipedia.org', '.gov', '.edu', 'reuters.com', 'bbc.com', 'nytimes.com', 'wsj.com']
            medium_credibility = ['medium.com', 'techcrunch.com', 'wired.com', 'arstechnica.com']
            
            if any(cred in domain for cred in high_credibility):
                return 0.9
            elif any(cred in domain for cred in medium_credibility):
                return 0.7
            elif domain.endswith('.org'):
                return 0.6
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def _analyze_search_results_intelligently(self, results: List[SearchResult], query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze search results for patterns and insights using LLM.
        """
        try:
            if not results:
                return {"insights": "No results found"}
            
            # Calculate aggregate metrics
            avg_relevance = sum(r.relevance_score for r in results) / len(results)
            avg_credibility = sum(r.source_credibility for r in results) / len(results)
            
            # Find most relevant result
            most_relevant = max(results, key=lambda r: r.relevance_score)
            
            # Generate insights using LLM
            insights_prompt = f"""
            Analyze these search results for the query "{query}":
            
            Results Summary:
            - Total results: {len(results)}
            - Average relevance: {avg_relevance:.2f}
            - Average credibility: {avg_credibility:.2f}
            - Most relevant: {most_relevant.title}
            
            Top Results:
            {chr(10).join([f"- {r.title}: {r.snippet[:100]}..." for r in results[:3]])}
            
            Context: {context or 'No specific context provided'}
            
            Provide insights about:
            1. Result quality and relevance to the query
            2. Information gaps or missing perspectives
            3. Recommended next steps for deeper research
            4. Overall assessment of search effectiveness
            
            Analysis:
            """
            
            result = self.llm_provider.generate(insights_prompt)
            insights = result.get("generated_text", "Could not analyze results")
            
            return {
                "insights": insights,
                "avg_relevance": avg_relevance,
                "avg_credibility": avg_credibility,
                "most_relevant": most_relevant.title,
                "result_count": len(results),
                "quality_assessment": "high" if avg_relevance > 0.7 else "medium" if avg_relevance > 0.4 else "low"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing search results: {e}")
            return {"insights": f"Analysis error: {e}"}
    
    def browse_and_summarize(self, url: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Navigate to URL and provide intelligent summary using HTTP requests.
        
        Args:
            url: Target URL
            context: Additional context for analysis
            
        Returns:
            Tuple of (result_dict, iar_dict)
        """
        try:
            # Use HTTP request to fetch page content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            
            analysis = WebPageAnalysis(
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
            
            result = {
                "url": url,
                "title": analysis.title,
                "summary": analysis.summary,
                "relevance_score": analysis.relevance_score,
                "links_found": len(analysis.links),
                "content_length": len(analysis.content),
                "metadata": analysis.metadata,
                "sentiment": analysis.sentiment
            }
            
            iar = create_iar(
                confidence=0.8,
                tactical_resonance=0.75,
                potential_issues=["Content extracted via HTTP, may miss dynamic content"],
                metadata={"url": url, "analysis_type": "page_summary", "method": "http_request"}
            )
            
            return result, iar
            
        except Exception as e:
            logger.error(f"Error in browse_and_summarize: {e}")
            result = {"error": f"Page analysis error: {str(e)}"}
            iar = create_iar(0.2, 0.1, [f"Page analysis error: {e}"])
            return result, iar
    
    def _calculate_relevance_score(self, content: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate relevance score using query terms and pinned policy modulation."""
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
    
    def _create_error_result(self, query: str, engine: str, error_message: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Create a standardized error result."""
        self.search_stats["failed_searches"] += 1
        result = {
            "success": False,
            "query": query,
            "engine": engine,
            "error": error_message,
            "results": [],
            "timestamp": time.time(),
            "tool": "enhanced_perception_engine_with_fallback",
            "version": "1.0.0"
        }
        iar = create_iar(0.1, 0.0, [error_message])
        return result, iar
    
    def _update_average_response_time(self, response_time: float) -> None:
        """Update the running average response time."""
        current_avg = self.search_stats["average_response_time"]
        successful_searches = self.search_stats["successful_searches"]
        
        if successful_searches == 1:
            self.search_stats["average_response_time"] = response_time
        else:
            self.search_stats["average_response_time"] = (
                (current_avg * (successful_searches - 1)) + response_time
            ) / successful_searches
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        duration = time.time() - self.session_data['start_time']
        success_rate = 0.0
        if self.session_data['searches_performed'] > 0:
            success_rate = (
                self.session_data['successful_searches'] / 
                self.session_data['searches_performed']
            ) * 100
        
        return {
            "searches_performed": self.session_data['searches_performed'],
            "successful_searches": self.session_data['successful_searches'],
            "total_results_found": self.session_data['total_results_found'],
            "errors": len(self.session_data['errors']),
            "session_duration": duration,
            "success_rate": success_rate,
            "average_response_time": self.search_stats["average_response_time"]
        }

# --- Action Wrapper Functions for Workflow Engine ---

def enhanced_web_search_with_fallback(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Enhanced web search action with fallback reliability.
    
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
    max_results = inputs.get("max_results", 10)
    
    engine = EnhancedPerceptionEngineWithFallback(max_results=max_results)
    result, iar = engine.search_and_analyze(query, context)
    
    # Add session stats
    stats = engine.get_session_stats()
    result["session_stats"] = stats
    
    return result, iar

def enhanced_page_analysis_with_fallback(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Enhanced page analysis action with HTTP reliability.
    
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
    
    engine = EnhancedPerceptionEngineWithFallback()
    result, iar = engine.browse_and_summarize(url, context)
    
    # Add session stats
    stats = engine.get_session_stats()
    result["session_stats"] = stats
    
    return result, iar

# --- Main execution for testing ---
if __name__ == "__main__":
    # Test the Enhanced Perception Engine with Fallback
    print("Testing Enhanced Perception Engine with Fallback...")
    
    engine = EnhancedPerceptionEngineWithFallback()
    
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
        
    except Exception as e:
        print(f"Test error: {e}")
    
    print("Enhanced Perception Engine with Fallback test completed.")
