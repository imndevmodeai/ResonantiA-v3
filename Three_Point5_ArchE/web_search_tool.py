import logging
import time
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Attempt to import the primary, unified search tool
try:
    # This assumes a unified_search_tool exists elsewhere in the project
    from .unified_search_tool import perform_web_search as unified_search
    UNIFIED_SEARCH_AVAILABLE = True
    logger.info("Unified search tool is available.")
except ImportError:
    UNIFIED_SEARCH_AVAILABLE = False
    unified_search = None
    logger.warning("Unified search tool not found. Falling back to legacy DuckDuckGo search.")

def _create_reflection(status: str, message: str, **kwargs) -> Dict[str, Any]:
    """Creates a standardized IAR reflection dictionary."""
    reflection = {
        "status": status,
        "message": message,
        "confidence": 0.0,
        "execution_time": 0.0,
    }
    reflection.update(kwargs)
    return reflection

def _legacy_duckduckgo_search(query: str, num_results: int) -> List[Dict[str, str]]:
    """Performs a direct search on DuckDuckGo and scrapes the results."""
    results = []
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for result in soup.find_all('div', class_='result'):
        title_tag = result.find('a', class_='result__a')
        snippet_tag = result.find('a', class_='result__snippet')
        url_tag = result.find('a', class_='result__url')

        if title_tag and snippet_tag and url_tag:
            results.append({
                "title": title_tag.text,
                "snippet": snippet_tag.text.strip(),
                "url": url_tag['href']
            })
        if len(results) >= num_results:
            break
            
    return results

def search_web(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs a web search using the best available method, with IAR compliance.
    """
    start_time = time.time()
    query = inputs.get("query")
    num_results = inputs.get("num_results", 10)

    if not query:
        return {
            "error": "Input 'query' is required.",
            "reflection": _create_reflection(
                status="failure",
                message="Input validation failed: 'query' is required.",
                inputs=inputs,
                execution_time=time.time() - start_time
            )
        }
    
    results = []
    search_method_used = "none"

    if UNIFIED_SEARCH_AVAILABLE:
        try:
            unified_result = unified_search(query, num_results)
            # Assuming unified_search returns a list of dicts with title, link, description
            results = [
                {"title": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("description", "")}
                for r in unified_result.get("results", [])
            ]
            search_method_used = "unified_search"
            logger.info(f"Unified search succeeded for query: '{query}'")
        except Exception as e:
            logger.warning(f"Unified search failed: {e}. Falling back to legacy search.")
            search_method_used = "unified_search_failed"

    if not results and search_method_used != "unified_search":
        try:
            results = _legacy_duckduckgo_search(query, num_results)
            search_method_used = "legacy_duckduckgo"
            logger.info(f"Legacy DuckDuckGo search succeeded for query: '{query}'")
        except Exception as e:
            logger.error(f"Legacy DuckDuckGo search failed: {e}", exc_info=True)
            return {
                "error": f"Web search failed: {str(e)}",
                "reflection": _create_reflection(
                    status="failure",
                    message=f"All search methods failed. Last error: {str(e)}",
                    inputs=inputs,
                    potential_issues=[type(e).__name__],
                    execution_time=time.time() - start_time
                )
            }

    return {
        "results": results,
        "reflection": _create_reflection(
            status="success",
            message=f"Found {len(results)} results using '{search_method_used}'.",
            inputs=inputs,
            outputs={"results_count": len(results), "search_method": search_method_used},
            confidence=0.85 if results else 0.5,
            execution_time=time.time() - start_time
        )
    }
