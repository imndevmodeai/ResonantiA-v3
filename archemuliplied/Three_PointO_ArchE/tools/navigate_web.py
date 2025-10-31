import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List


def _iar(status: str, summary: str, confidence: float, issues: Optional[List[str]] = None, preview: Optional[str] = None) -> Dict[str, Any]:
    return {
        "status": status,
        "summary": summary,
        "confidence": max(0.0, min(1.0, float(confidence))),
        "alignment_check": "Aligned with navigation/ingestion goal",
        "potential_issues": issues or None,
        "raw_output_preview": (preview[:150] + "...") if isinstance(preview, str) and len(preview) > 150 else preview,
    }


def navigate_web(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lightweight HTTP navigation and ingestion tool (no JS).

    Inputs:
      - url (str): target URL
      - timeout (int, default 20)
      - headers (dict): optional request headers
      - selector (str): optional CSS selector to extract specific content
      - allow_redirects (bool, default True)

    Returns:
      { "content": str, "status_code": int, "title": str?, "selection": str?, "reflection": IAR }
    """
    url = inputs.get("url")
    if not url or not isinstance(url, str):
        return {"error": "Input 'url' is required.", "reflection": _iar("Failure", "Missing url input", 0.0, ["InputValidation"]) }

    timeout = int(inputs.get("timeout", 20))
    headers = inputs.get("headers") or {"User-Agent": "ArchE/3.5 (+resonantia)"}
    allow_redirects = bool(inputs.get("allow_redirects", True))
    selector = inputs.get("selector")

    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
        status_code = resp.status_code
        text = resp.text
        soup = BeautifulSoup(text, "lxml")
        title = (soup.title.string.strip() if soup.title and soup.title.string else None)
        selection = None
        if selector:
            node = soup.select_one(selector)
            if node:
                selection = node.get_text(strip=True)
        return {
            "content": text,
            "status_code": status_code,
            "title": title,
            "selection": selection,
            "reflection": _iar(
                "Success" if status_code == 200 else "Partial",
                f"Fetched {url} ({status_code})",
                0.9 if status_code == 200 else 0.6,
                None if status_code == 200 else [f"HTTP {status_code}"],
                selection or (text[:150] if text else None)
            )
        }
    except requests.Timeout:
        return {"error": f"Timeout fetching {url}", "reflection": _iar("Failure", f"Timeout fetching {url}", 0.0, ["Timeout"]) }
    except requests.RequestException as e:
        return {"error": f"Request error: {e}", "reflection": _iar("Failure", f"Request error for {url}", 0.0, ["RequestException"]) }



