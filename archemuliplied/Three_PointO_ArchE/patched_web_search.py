#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResonantiA Protocol v3.5 - Patched Web Search Tool
A self-contained, corrected version of the web search tool to bypass file system issues.
"""
import logging
import requests
import urllib.parse
from bs4 import BeautifulSoup
from typing import Dict, Any

logger = logging.getLogger(__name__)

def search_web(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs a web search using DuckDuckGo and returns the results.
    This patched version ensures all necessary libraries are imported correctly.
    """
    query = inputs.get("query")
    if not query:
        return {"error": "Missing required input: query"}

    num_results = inputs.get("num_results", 5)
    
    logger.info(f"Performing web search for: {query}")

    try:
        # URL encode the query
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        result_nodes = soup.find_all('div', class_='result')

        for i, node in enumerate(result_nodes):
            if i >= num_results:
                break
            
            title_node = node.find('a', class_='result__a')
            link_node = node.find('a', class_='result__a')
            snippet_node = node.find('a', class_='result__snippet')

            if title_node and link_node and snippet_node:
                title = title_node.get_text(strip=True)
                link = link_node['href']
                snippet = snippet_node.get_text(strip=True)
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })

        if not results:
            return {"error": "No results found."}
            
        return {"results": results}

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during web search: {e}")
        return {"error": f"An error occurred during web search: {e}"}
    except Exception as e:
        logger.error(f"An unexpected error occurred during web search: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred during web search: {e}"}
