import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus

from .utils.reflection_utils import create_reflection, ExecutionStatus

logger = logging.getLogger(__name__)

def search_web(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a web search using direct HTTP requests and return results with IAR reflection.
    
    Args:
        inputs (Dict): A dictionary containing:
            - query (str): Search query string.
            - num_results (int): Number of results to return.
            - provider (str): The search provider ('duckduckgo' is the reliable default).
        
    Returns:
        Dictionary containing search results and a compliant IAR reflection.
    """
    start_time = time.time()
    action_name = "web_search"
    
    query = inputs.get("query")
    num_results = inputs.get("num_results", 10)
    provider = inputs.get("provider", "duckduckgo")

    if not query:
        return {
            "error": "Input 'query' is required.",
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.FAILURE,
                message="Input validation failed: 'query' is required.",
                inputs=inputs,
                execution_time=time.time() - start_time
            )
        }

    if provider != "duckduckgo":
        # For now, only support DuckDuckGo to avoid dealing with Google's bot detection
        return {
            "error": "Unsupported provider. Only 'duckduckgo' is currently supported for direct requests.",
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.FAILURE,
                message=f"Provider '{provider}' is not supported.",
                inputs=inputs,
                potential_issues=["ConfigurationError"],
                execution_time=time.time() - start_time
            )
        }
        
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        # Find all result divs
        result_divs = soup.find_all('div', class_='result')
        
        for div in result_divs[:num_results]:
            title_tag = div.find('a', class_='result__a')
            snippet_tag = div.find('a', class_='result__snippet')
            url_tag = div.find('a', class_='result__url')

            if title_tag and snippet_tag and url_tag:
                title = title_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(strip=True)
                # Clean up the URL from DDG's tracking link
                url = url_tag['href']
                cleaned_url = url.split('uddg=')[-1]
                if cleaned_url.startswith('https'):
                    results.append({
                        "title": title,
                        "url": requests.utils.unquote(cleaned_url),
                        "snippet": snippet
                    })

        if not results:
            return {
                "result": {"results": []},
                "reflection": create_reflection(
                    action_name=action_name,
                    status=ExecutionStatus.WARNING,
                    message="Search completed but found no results.",
                    inputs=inputs,
                    outputs={"results_count": 0},
                    confidence=0.7,
                    potential_issues=["No results found for query."],
                    execution_time=time.time() - start_time
                )
            }

        outputs = {"results": results}
        return {
            "result": outputs,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.SUCCESS,
                message=f"Found {len(results)} results for query using {provider}.",
                inputs=inputs,
                outputs={"results_count": len(results)},
                confidence=0.9,
                execution_time=time.time() - start_time
            )
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error during web search: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=[type(e).__name__],
                execution_time=time.time() - start_time
            )
        }
    except Exception as e:
        error_msg = f"An unexpected error occurred during web search: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.CRITICAL_FAILURE,
                message=error_msg,
                inputs=inputs,
                potential_issues=[type(e).__name__],
                execution_time=time.time() - start_time
            )
        } 