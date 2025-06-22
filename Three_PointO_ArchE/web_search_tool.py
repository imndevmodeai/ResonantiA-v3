import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import json
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)

def search_web(
    query: str,
    num_results: int = 10,
    provider: str = "google"
) -> Dict[str, Any]:
    """
    Perform a web search using the search.js browser automation script.
    
    Args:
        query: Search query string
        num_results: Number of results to return (Note: the script may return more)
        provider: The search provider to use ('google' or 'duckduckgo').
        
    Returns:
        Dictionary containing search results and IAR reflection
    """
    result = None # Initialize result to avoid UnboundLocalError
    try:
        # Create a temporary file to store the search results
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as temp_output:
            output_filename = temp_output.name
        
        # Define the path to the search script's directory robustly
        # Hardcoding the root for stability in this specific environment.
        project_root = "/media/dev2025/3626C55326C514B1/Happier"
        script_dir = os.path.join(project_root, 'ResonantiA', 'browser_automation')
        
        # Construct the command to run the Node.js script
        command = [
            "node",
            "search.js",
            "--query",
            query,
            "--engine",
            provider,
            "--output",
            output_filename
        ]
        
        # Execute the script from its own directory
        logger.info(f"Executing browser automation script in '{script_dir}': {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=script_dir
        )

        if result.returncode != 0:
            error_msg = f"Browser automation script failed with exit code {result.returncode}. Stderr: {result.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Read the results from the temporary file, with extra error handling
        search_results = []
        try:
            with open(output_filename, 'r') as f:
                search_results = json.load(f)
        except json.JSONDecodeError:
            # This is the critical error: the script ran but produced an empty or invalid file.
            # We log the stderr from the script to find out why.
            error_msg = f"Browser automation script produced invalid or empty JSON. Stderr: {result.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        # The script returns an array of objects with title, url, snippet
        # We can limit the number of results here if needed
        formatted_results = search_results[:num_results]

        return {
            "results": formatted_results,
            "reflection": {
                "status": "Success",
                "confidence": 0.95, # High confidence as it's from a live browser session
                "insight": f"Found {len(formatted_results)} results for query using {provider} via browser automation.",
                "action": "web_search",
                "reflection": "Search completed successfully using browser automation."
            }
        }
        
    except FileNotFoundError:
        # This will catch if the results file wasn't created
        stderr_output = result.stderr if result else "N/A (subprocess did not run)"
        error_msg = f"Search script did not produce an output file at {output_filename}. Stderr: {stderr_output}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "results": [],
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": "Browser automation script failed to produce output.",
                "action": "web_search",
                "reflection": error_msg
            }
        }
    except Exception as e:
        error_msg = f"Error processing browser automation search: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "results": [],
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": "Web search failed during execution or processing.",
                "action": "web_search",
                "reflection": error_msg
            }
        }
    finally:
        # Clean up the temporary file
        if 'output_filename' in locals() and os.path.exists(output_filename):
            os.remove(output_filename) 