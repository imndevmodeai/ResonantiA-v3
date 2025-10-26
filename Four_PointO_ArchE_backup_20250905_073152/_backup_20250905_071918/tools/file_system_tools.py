# Four_PointO_ArchE/tools/file_system_tools.py

import os
from typing import Dict, Any, Tuple, List

def list_directory(path: str = ".") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Lists the contents of a directory."""
    try:
        contents = [os.path.join(path, f) for f in os.listdir(path)]
        result = {"contents": contents, "path": path}
        iar = {
            "confidence": 1.0,
            "tactical_resonance": 1.0,
            "potential_issues": [],
            "metadata": {"item_count": len(contents)}
        }
        return result, iar
    except Exception as e:
        result = {"contents": [], "path": path, "error": str(e)}
        iar = {
            "confidence": 0.0,
            "tactical_resonance": 0.0,
            "potential_issues": [f"An exception occurred: {e}"],
            "metadata": {}
        }
        return result, iar

def read_file(file_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Reads the content of a file."""
    if not file_path:
        result = {"content": "", "error": "No file_path provided."}
        iar = {
            "confidence": 0.0,
            "tactical_resonance": 0.0,
            "potential_issues": ["Input error: file_path was not provided."],
            "metadata": {}
        }
        return result, iar
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        result = {"content": content, "file_path": file_path, "file_size": len(content)}
        iar = {
            "confidence": 1.0,
            "tactical_resonance": 1.0,
            "potential_issues": [],
            "metadata": {"file_path": file_path}
        }
        return result, iar
    except FileNotFoundError:
        result = {"content": "", "error": f"File not found: {file_path}"}
        iar = {
            "confidence": 0.0,
            "tactical_resonance": 0.0,
            "potential_issues": [f"File not found at path: {file_path}"],
            "metadata": {}
        }
        return result, iar
    except Exception as e:
        result = {"content": "", "error": str(e)}
        iar = {
            "confidence": 0.0,
            "tactical_resonance": 0.0,
            "potential_issues": [f"An exception occurred while reading file: {e}"],
            "metadata": {}
        }
        return result, iar

def create_file(file_path: str, content: str = "") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Creates a new file with the specified content."""
    if not file_path:
        result = {"created": False, "error": "No file_path provided."}
        iar = {
            "confidence": 0.0,
            "tactical_resonance": 0.0,
            "potential_issues": ["Input error: file_path was not provided."],
            "metadata": {}
        }
        return result, iar

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = {"file_path": file_path, "content_length": len(content), "created": True}
        iar = {
            "confidence": 1.0,
            "tactical_resonance": 1.0,
            "potential_issues": [],
            "metadata": {"file_path": file_path}
        }
        return result, iar
    except Exception as e:
        result = {"created": False, "error": str(e)}
        iar = {
            "confidence": 0.0,
            "tactical_resonance": 0.0,
            "potential_issues": [f"An exception occurred while creating file: {e}"],
            "metadata": {}
        }
        return result, iar
