import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import json
import subprocess
import os

logger = logging.getLogger(__name__)

def search_web(
    query: str,
    num_results: int = 10,
    search_type: str = "academic_and_technical_repositories",
    provider: str = "mock_provider"
) -> Dict[str, Any]:
    """
    Perform a web search and return results with IAR reflection.
    
    Args:
        query: Search query string
        num_results: Number of results to return
        search_type: Type of search to perform
        provider: The search provider to use (e.g., 'puppeteer_nodejs', 'google_search_api', 'mock_provider').
        
    Returns:
        Dictionary containing search results and IAR reflection
    """
    results = []
    summary = ""
    alignment_check = ""
    potential_issues = []
    status = "Failed"
    confidence = 0.0
    captured_screenshots = []
    
    try:
        if provider == "mock_provider":
            logger.info(f"Using mock search provider for query: {query}")
            results = [
                {
                    "title": f"Mock Result {i} for {query}",
                    "url": f"https://mock.example.com/result{i}",
                    "snippet": f"This is a SAMPLE result from the mock provider for query: {query}"
                }
                for i in range(num_results)
            ]
            summary = f"Successfully performed mock search for '{query}' and found {len(results)} results."
            alignment_check = "Aligned with mock search objective."
            potential_issues = ["Using mock provider; no real-time data."]
            status = "Success"
            confidence = 0.8

        elif provider == "puppeteer_nodejs":
            logger.info(f"Using puppeteer_nodejs search provider (browser_automation/search.js) for query: {query}")
            # Correct path to the new browser_automation script
            browser_automation_script_path = os.path.join(
                os.path.dirname(__file__), "..", "ResonantiA", "browser_automation", "search.js"
            )
            
            command_args = [
                "node",
                browser_automation_script_path,
                query,
                str(num_results),
                "duckduckgo", # Assuming duckduckgo for now, can be made dynamic later if needed
                os.path.join(os.path.dirname(__file__), "..", "outputs"), # Output directory for results.json
                "--debug", # Include debug to get more logs
                "--include-text-content", # Request full text content scraping
                "--capture-all", # Request all captures (screenshots, html, pdf)
                "--capture-dir", os.path.join(os.path.dirname(__file__), "..", "outputs", "captures") # Specific capture directory
            ]

            try:
                # Run the Node.js script as a subprocess
                # Capture stdout for JSON results and stderr for screenshot paths/debug info
                process = subprocess.run(
                    command_args,
                    capture_output=True, text=True, check=False, timeout=90 # Set check=False to handle non-zero exit codes manually
                )
                
                raw_output = process.stdout.strip()
                raw_stderr = process.stderr.strip()
                
                # Prioritize stderr for error detection
                script_error_detected = False
                error_message_from_script = ""

                if "Puppeteer search failed:" in raw_stderr or "Error waiting for DuckDuckGo results:" in raw_stderr:
                    script_error_detected = True
                    error_message_from_script = raw_stderr # Capture the full stderr for detailed error
                elif process.returncode != 0:
                    script_error_detected = True
                    error_message_from_script = f"Puppeteer script exited with non-zero code {process.returncode}. Stderr: {raw_stderr}"

                if script_error_detected:
                    summary = f"Puppeteer search failed: {error_message_from_script[:200]}"
                    alignment_check = "Failed to perform web search."
                    potential_issues = [error_message_from_script]
                    status = "Failed"
                    confidence = 0.0
                elif raw_output:
                    parsed_output = json.loads(raw_output)
                    if isinstance(parsed_output, list):
                        results = parsed_output
                        summary = f"Successfully performed web search and data capture for '{query}' using Puppeteer. Found {len(results)} results."
                        alignment_check = "Aligned with web search and data collection objectives."
                        potential_issues = []
                        status = "Success"
                        confidence = 0.95
                    elif isinstance(parsed_output, dict) and "error" in parsed_output:
                        error_msg = parsed_output["error"]
                        summary = f"Puppeteer search script reported an error: {error_msg}"
                        alignment_check = "Failed to perform web search."
                        potential_issues = [error_msg]
                        status = "Failed"
                        confidence = 0.0
                    else:
                        summary = f"Puppeteer search script returned unexpected output format. Raw stdout: {raw_output[:100]}... Raw stderr: {raw_stderr[:200]}"
                        alignment_check = "Failed to parse Puppeteer script output."
                        potential_issues = ["Unexpected script output format.", raw_output[:200], raw_stderr[:200]]
                        status = "Failed"
                        confidence = 0.1
                else:
                    summary = f"Puppeteer search script returned no JSON output for query: {query}. Stderr: {raw_stderr[:200]}"
                    alignment_check = "Failed to get search results."
                    potential_issues = ["Puppeteer script returned empty JSON output.", raw_stderr[:200]]
                    status = "Failed"
                    confidence = 0.0

                # Extract screenshot paths from stderr (even if error, for debugging)
                for line in raw_stderr.splitlines():
                    if line.startswith("SCREENSHOT_PATH:"):
                        captured_screenshots.append(line.replace("SCREENSHOT_PATH:", "").strip())

            except subprocess.TimeoutExpired as e:
                error_msg = f"Puppeteer script timed out after {e.timeout} seconds. Stderr: {e.stderr[:200] if e.stderr else 'N/A'}"
                summary = f"Puppeteer search timed out: {error_msg}"
                alignment_check = "Web search timed out."
                potential_issues = [error_msg]
                status = "Failed"
                confidence = 0.0
            except json.JSONDecodeError as e:
                # Ensure raw_output and raw_stderr are defined before accessing them
                raw_output_for_log = ""
                raw_stderr_for_log = ""
                if 'raw_output' in locals():
                    raw_output_for_log = raw_output[:200]
                if 'raw_stderr' in locals():
                    raw_stderr_for_log = raw_stderr[:200]

                error_msg = f"Failed to parse JSON output from Puppeteer script: {e}. Raw stdout: {raw_output_for_log}. Raw stderr: {raw_stderr_for_log}"
                summary = f"Puppeteer script returned invalid JSON: {error_msg}"
                alignment_check = "Failed to parse web search results."
                potential_issues = [error_msg]
                status = "Failed"
                confidence = 0.0
            except Exception as e:
                error_msg = f"An unexpected error occurred during Puppeteer search integration: {str(e)}"
                summary = f"Unexpected error in Puppeteer search: {error_msg}"
                alignment_check = "Unexpected integration error."
                potential_issues = [error_msg]
                status = "Failed"
                confidence = 0.0

        else:
            logger.warning(f"Unsupported search provider: {provider}. Proceeding with mock results.")
            results = [
                {
                    "title": f"Mock (Unsupported Provider: {provider}) Result {i} for {query}",
                    "url": f"https://mock.example.com/unsupported{i}",
                    "snippet": f"This is a mock result because provider {provider} is not supported yet for query: {query}"
                }
                for i in range(num_results)
            ]
            summary = f"Unsupported search provider '{provider}'. Returned mock results for '{query}'."
            alignment_check = "Partially aligned (mock results only)."
            potential_issues = [f"Unsupported search provider: {provider}. Using mock results."]
            status = "Partial"
            confidence = 0.1
        
        raw_output_preview = json.dumps(results[:1], indent=2)[:200] + "..." if results else "No results to preview."

        # Include captured screenshots in potential_issues for IAR
        if captured_screenshots:
            potential_issues.append(f"Captured screenshots: {captured_screenshots}")

        return {
            "results": results,
            "reflection": {
                "status": status,
                "confidence": confidence,
                "summary": summary,
                "alignment_check": alignment_check,
                "potential_issues": potential_issues,
                "raw_output_preview": raw_output_preview,
                "action": "web_search",
                "reflection": summary # Re-use summary for general reflection
            }
        }
        
    except Exception as e:
        error_msg = f"Error performing web search: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        raw_output_preview = error_msg[:200] + "..." if len(error_msg) > 200 else error_msg

        return {
            "error": error_msg,
            "results": [],
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "summary": "Web search failed due to an unexpected error.",
                "alignment_check": "Failed to perform web search.",
                "potential_issues": [error_msg],
                "raw_output_preview": raw_output_preview,
                "action": "web_search",
                "reflection": error_msg
            }
        } 