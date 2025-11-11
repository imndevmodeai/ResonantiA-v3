from flask import Flask, render_template, request, jsonify
import base64
import json
import re
from datetime import datetime
import os
import requests
from typing import Dict, Any

# --- Integrated FaceCheckAPIClient ---
class FaceCheckAPIClient:
    def __init__(self):
        self.base_url = "https://facecheck.id"
        self.api_endpoint = f"{self.base_url}/api/search"
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

    def search_by_id(self, search_id: str) -> Dict[str, Any]:
        payload = {
            "id_search": search_id,
            "with_progress": True,
            "status_only": False,  # We want the full data
            "demo": False
        }
        try:
            response = self.session.post(self.api_endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"API request failed: {str(e)}")
        except json.JSONDecodeError:
            raise ValueError("Failed to parse API response.")

app = Flask(__name__)

# --- Existing functions ---
def find_items_in_data(data):
    """
    Robust function to find the 'items' array in various JSON structures.
    Returns the items list or None if not found.
    """
    # Direct items at root level
    if isinstance(data, dict) and 'items' in data and isinstance(data['items'], list):
        return data['items']
    
    # Direct results at root level
    if isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
        return data['results']
    
    # Items inside 'output' key
    if isinstance(data, dict) and 'output' in data:
        output = data['output']
        if isinstance(output, dict) and 'items' in output and isinstance(output['items'], list):
            return output['items']
        # Also check for 'results' inside output
        if isinstance(output, dict) and 'results' in output and isinstance(output['results'], list):
            return output['results']
    
    # Items inside nested 'output.output' structure
    if isinstance(data, dict) and 'output' in data:
        output = data['output']
        if isinstance(output, dict) and 'output' in output:
            nested_output = output['output']
            if isinstance(nested_output, dict) and 'items' in nested_output and isinstance(nested_output['items'], list):
                return nested_output['items']
    
    # If data itself is a list, return it
    if isinstance(data, list):
        return data
    
    # If data is a single item object (has base64 field), wrap it in a list
    if isinstance(data, dict) and 'base64' in data:
        return [data]
    
    # Search recursively in all dictionary values
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'items' and isinstance(value, list):
                return value
            elif isinstance(value, (dict, list)):
                result = find_items_in_data(value)
                if result:
                    return result
    
    return None

def process_and_render(data):
    """
    Main processing logic for the Flask app.
    Takes a JSON data structure, finds items, processes base64, and renders results.
    """
    items = find_items_in_data(data)
    if not items:
        raise ValueError('Could not find "items" array in the data.')

    # Extract original image from the 'input' field if available
    original_image_base64 = None
    if isinstance(data, dict) and 'input' in data and isinstance(data['input'], list):
        if data['input'] and 'base64' in data['input'][0]:
            original_image_base64 = data['input'][0]['base64']

    processed_items = []
    for item in items:
        if not item.get('base64') or not item['base64'].startswith('data:image/'):
            continue

        extracted_url = None
        try:
            match = re.search(r'data:image/\w+;base64,(.*)', item['base64'])
            if match:
                encoded_data = match.group(1)
                missing_padding = len(encoded_data) % 4
                if missing_padding:
                    encoded_data += '=' * (4 - missing_padding)
                
                binary_data = base64.b64decode(encoded_data)
                text_data = binary_data.decode('latin-1', errors='ignore')
                base64_pattern = re.compile(r'[A-Za-z0-9+/]+=*')
                matches = base64_pattern.findall(text_data)
                
                for b64_match in matches:
                    if len(b64_match) > 20:
                        try:
                            missing_padding = len(b64_match) % 4
                            if missing_padding:
                                b64_match += '=' * (4 - missing_padding)
                            
                            decoded = base64.b64decode(b64_match).decode('utf-8', errors='ignore')
                            if decoded.startswith('{') and 'url' in decoded:
                                json_data = json.loads(decoded)
                                if 'url' in json_data:
                                    extracted_url = json_data['url']
                                    break
                        except:
                            continue
                
                if not extracted_url:
                    url_pattern = re.compile(r'https?://[^\s"]+')
                    url_match = url_pattern.search(text_data)
                    if url_match:
                        extracted_url = url_match.group(0)
        except Exception as e:
            app.logger.error(f"Error processing base64 for GUID {item.get('guid')}: {e}")

        final_url = extracted_url if extracted_url else item.get('url', 'No URL found')
        
        processed_items.append({
            'guid': item.get('guid'),
            'score': item.get('score'),
            'base64': item['base64'],
            'url': final_url,
            'index': item.get('index'),
            'indexDB': item.get('indexDB'),
            'seen': item.get('seen', 'N/A')
        })

    if not processed_items:
        raise ValueError('No valid items with base64 images were found.')

    html_output = render_template('results.html', items=processed_items, original_image=original_image_base64)
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"results_{timestamp}.html"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_output)
        app.logger.info(f"Successfully saved results to {filepath}")
    except Exception as e:
        app.logger.error(f"Failed to save results HTML file: {e}")
    return html_output

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_json():
    try:
        raw_data = request.get_data(as_text=True)
        if not raw_data:
            raise ValueError('No data received')
        data = json.loads(raw_data)
        return process_and_render(data)
    except (ValueError, json.JSONDecodeError) as e:
        app.logger.error(f"Error processing JSON: {e}")
        return render_template('error.html', message=str(e)), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return render_template('error.html', message='An unexpected error occurred.'), 500

@app.route('/from-url', methods=['GET'])
def process_from_url():
    try:
        facecheck_url = request.args.get('url')
        if not facecheck_url or 'facecheck.id' not in facecheck_url:
            raise ValueError("A valid FaceCheck.ID URL is required.")
        
        # Extract search ID from the URL hash
        search_id_match = re.search(r'#([a-zA-Z0-9_-]+)', facecheck_url)
        if not search_id_match:
            raise ValueError("Could not extract search ID from the URL.")
        
        search_id = search_id_match.group(1)
        
        client = FaceCheckAPIClient()
        data = client.search_by_id(search_id)
        
        return process_and_render(data)
    except ValueError as e:
        app.logger.error(f"Error processing from URL: {e}")
        return render_template('error.html', message=str(e)), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return render_template('error.html', message='An unexpected error occurred.'), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3033))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host=host, port=port)

