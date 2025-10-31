#!/usr/bin/env python3
"""
FaceCheck.ID API Client Script
Template for interacting with FaceCheck.ID facial recognition search API
Based on: https://facecheck.id/#Gsf3wAtgu2U
"""

import requests
import json
import time
import base64
from typing import Dict, Any, Optional
import argparse
import sys

class FaceCheckAPIClient:
    def __init__(self):
        self.base_url = "https://facecheck.id"
        self.api_endpoint = f"{self.base_url}/api/search"
        
        # Headers extracted from your curl command
        self.headers = {
            'accept': 'text/plain, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json; charset=UTF-8',
            'dnt': '1',
            'origin': 'https://facecheck.id',
            'priority': 'u=1, i',
            'referer': 'https://facecheck.id/',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        # Cookies from your curl command (you may need to update these)
        self.cookies = {
            'lang': 'en',
            'i': 'HJBzSmeEekN7m3FEe5hyQA%3D%3D',
            'agreedon': 'Fri%20Oct%2017%202025',
            'c': '72',
            'time': '1760758173929'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.cookies.update(self.cookies)

    def search_by_id(self, search_id: str, with_progress: bool = True, 
                    status_only: bool = True, demo: bool = False) -> Dict[str, Any]:
        """
        Search FaceCheck.ID by search ID
        
        Args:
            search_id: The search ID (e.g., 'Gsf3wAtgu2U')
            with_progress: Whether to include progress updates
            status_only: Whether to return status only
            demo: Whether this is a demo search
            
        Returns:
            API response as dictionary
        """
        payload = {
            "id_search": search_id,
            "with_progress": with_progress,
            "status_only": status_only,
            "demo": demo
        }
        
        try:
            response = self.session.post(
                self.api_endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None)
            }
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": response.text
            }

    def upload_image_search(self, image_path: str) -> Dict[str, Any]:
        """
        Upload an image for facial recognition search
        
        Args:
            image_path: Path to the image file
            
        Returns:
            API response as dictionary
        """
        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                
                # Remove content-type header for multipart upload
                headers = self.headers.copy()
                headers.pop('content-type', None)
                
                response = self.session.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    headers=headers,
                    timeout=60
                )
                response.raise_for_status()
                return response.json()
                
        except FileNotFoundError:
            return {"error": f"Image file not found: {image_path}"}
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Upload failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None)
            }

    def get_search_status(self, search_id: str) -> Dict[str, Any]:
        """
        Check the status of a search by ID
        
        Args:
            search_id: The search ID to check
            
        Returns:
            Status information
        """
        return self.search_by_id(search_id, status_only=True)

    def wait_for_completion(self, search_id: str, max_wait: int = 300, 
                          check_interval: int = 5) -> Dict[str, Any]:
        """
        Wait for a search to complete and return results
        
        Args:
            search_id: The search ID to monitor
            max_wait: Maximum time to wait in seconds
            check_interval: Time between status checks in seconds
            
        Returns:
            Final search results
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_search_status(search_id)
            
            if "error" in status:
                return status
                
            # Check if search is complete
            if status.get("status") == "completed":
                return self.search_by_id(search_id, status_only=False)
            
            print(f"Search in progress... Status: {status.get('status', 'unknown')}")
            time.sleep(check_interval)
        
        return {"error": "Search timed out", "search_id": search_id}

def main():
    parser = argparse.ArgumentParser(description='FaceCheck.ID API Client')
    parser.add_argument('--search-id', help='Search ID to query')
    parser.add_argument('--image', help='Path to image file for upload')
    parser.add_argument('--wait', action='store_true', 
                       help='Wait for search completion')
    parser.add_argument('--max-wait', type=int, default=300,
                       help='Maximum wait time in seconds')
    
    args = parser.parse_args()
    
    client = FaceCheckAPIClient()
    
    if args.search_id:
        print(f"Searching for ID: {args.search_id}")
        
        if args.wait:
            result = client.wait_for_completion(args.search_id, args.max_wait)
        else:
            result = client.get_search_status(args.search_id)
        
        print(json.dumps(result, indent=2))
        
    elif args.image:
        print(f"Uploading image: {args.image}")
        result = client.upload_image_search(args.image)
        print(json.dumps(result, indent=2))
        
    else:
        # Example usage with the provided search ID
        print("Example: Searching with provided ID 'Gsf3wAtgu2U'")
        result = client.search_by_id("Gsf3wAtgu2U")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

