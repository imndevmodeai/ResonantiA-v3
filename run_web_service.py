import sys
import os
import waitress

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from arche_registry.api import app

if __name__ == '__main__':
    waitress.serve(app, host='127.0.0.1', port=5001) 