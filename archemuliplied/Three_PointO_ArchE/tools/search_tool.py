import requests
from bs4 import BeautifulSoup
import json
import os
from duckduckgo_search import DDGS
# Make SerpApi optional; avoid hard import errors at module load
try:
    from serpapi import GoogleSearch as _SerpGoogleSearch
except Exception:
    _SerpGoogleSearch = None

class SearchTool:
    """
    A tool to search the web and retrieve content from URLs.
    Adheres to the IAR (Integrated Action Reflection) standard.
    """

    def __init__(self):
        """
        Initializes the SearchTool.
        """
        self.headers = {
            'User-Agent': 'ArchE/3.1 (MasterMind_AI; +https://github.com/your-repo)'
        }
        self.serpapi_key = os.environ.get("SERPAPI_API_KEY")

    def _generate_iar_reflection(self, success, message, data=None):
        """Generates a standardized IAR reflection dictionary."""
        return {
            "tool_name": "SearchTool",
            "success": success,
            "message": message,
            "data": data or {}
        }

    def search(self, query: str, num_results: int = 5, provider: str = "duckduckgo"):
        """
        Performs a web search using the specified provider.
        """
        if provider == "google" and self.serpapi_key:
            return self._google_search(query, num_results)
        return self._duckduckgo_search(query, num_results)

    def _duckduckgo_search(self, query: str, num_results: int):
        """
        Performs a web search using DuckDuckGo.
        """
        message = ""
        results = []
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
            
            message = f"Successfully performed DuckDuckGo search for '{query}'."
            iar_reflection = self._generate_iar_reflection(True, message, {"results": results, "query": query})
            return {"results": results, "reflection": iar_reflection}

        except Exception as e:
            message = f"An error occurred during DuckDuckGo search for '{query}': {e}"
            iar_reflection = self._generate_iar_reflection(False, message, {"query": query})
            return {"results": [], "reflection": iar_reflection}

    def _google_search(self, query: str, num_results: int):
        """
        Performs a web search using Google via SerpApi.
        """
        message = ""
        try:
            if _SerpGoogleSearch is None or not self.serpapi_key:
                # Fallback to DuckDuckGo if SerpApi client/key unavailable
                return self._duckduckgo_search(query, num_results)
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results
            }
            search = _SerpGoogleSearch(params)
            results_dict = search.get_dict()
            results = results_dict.get("organic_results", [])

            # Normalize results to match the DDGS format: [{'title': '', 'href': '', 'body': ''}]
            normalized_results = [
                {"title": r.get("title"), "href": r.get("link"), "body": r.get("snippet")}
                for r in results
            ]
            
            message = f"Successfully performed Google search for '{query}'."
            iar_reflection = self._generate_iar_reflection(True, message, {"results": normalized_results, "query": query})
            return {"results": normalized_results, "reflection": iar_reflection}

        except Exception as e:
            message = f"An error occurred during Google search for '{query}': {e}"
            iar_reflection = self._generate_iar_reflection(False, message, {"query": query})
            return {"results": [], "reflection": iar_reflection}

    def scrape_url(self, url: str):
        """
        Scrapes the text content from a given URL.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            message = f"Successfully scraped content from {url}."
            iar_reflection = self._generate_iar_reflection(True, message, {"url": url, "content_length": len(text)})
            return {"content": text, "reflection": iar_reflection}

        except requests.RequestException as e:
            message = f"Error scraping URL {url}: {e}"
            iar_reflection = self._generate_iar_reflection(False, message, {"url": url})
            return {"content": None, "reflection": iar_reflection}

def get_tool():
    """Factory function to get an instance of the tool."""
    return SearchTool() 