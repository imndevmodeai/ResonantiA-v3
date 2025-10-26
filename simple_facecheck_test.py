#!/usr/bin/env python3
"""
Simple FaceCheck.ID API Usage Example
Quick script to test the API with your specific search ID
"""

import requests
import json

def search_facecheck_by_id(search_id):
    """
    Simple function to search FaceCheck.ID by ID
    """
    url = "https://facecheck.id/api/search"
    
    headers = {
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
    
    cookies = {
        'lang': 'en',
        'i': 'HJBzSmeEekN7m3FEe5hyQA%3D%3D',
        'agreedon': 'Fri%20Oct%2017%202025',
        'c': '72',
        'time': '1760758173929'
    }
    
    payload = {
        "id_search": search_id,
        "with_progress": True,
        "status_only": True,
        "demo": False
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test with your provided search ID
    search_id = "Gsf3wAtgu2U"
    result = search_facecheck_by_id(search_id)
    print(json.dumps(result, indent=2))

