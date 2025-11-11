import requests
import json
from typing import Dict, Any, List, Optional, Tuple
from ..base import DataSourcePlugin
import logging

logger = logging.getLogger(__name__)

class HttpPlugin(DataSourcePlugin):
    """
    A data source plugin for interacting with HTTP APIs.
    This encapsulates the logic of the `call_api` tool.
    """

    def query(self, statement: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Executes an HTTP request. The 'statement' is the URL.

        Args:
            statement (str): The target API endpoint URL.
            **kwargs: Additional parameters for the request, such as:
                method (str): HTTP method (GET, POST, etc.). Defaults to GET.
                headers (dict): Request headers.
                params (dict): URL parameters.
                json_data (dict): JSON payload.

        Returns:
            A list containing a single dictionary with the response, or an error.
        """
        url = statement
        method = kwargs.get("method", "GET").upper()
        headers = kwargs.get("headers", {})
        params = kwargs.get("params")
        json_payload = kwargs.get("json_data")
        timeout = kwargs.get("timeout", 30)

        logger.info(f"Executing HTTP Plugin query: {method} {url}")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_payload,
                timeout=timeout
            )
            response.raise_for_status()

            try:
                response_body = response.json()
            except json.JSONDecodeError:
                response_body = response.text

            return [{
                "status_code": response.status_code,
                "response_body": response_body,
                "headers": dict(response.headers)
            }]

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Plugin query failed: {e}", exc_info=True)
            return [{"error": str(e)}]

    def get_schema(self) -> Dict[str, Any]:
        """
        Returns a schema describing the inputs for this plugin.
        """
        return {
            "type": "http",
            "inputs": {
                "statement": "string (URL)",
                "method": "string (GET, POST, etc.)",
                "headers": "dict",
                "params": "dict",
                "json_data": "dict"
            }
        }
