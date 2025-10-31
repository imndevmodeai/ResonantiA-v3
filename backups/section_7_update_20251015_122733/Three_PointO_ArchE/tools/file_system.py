# --- START OF FILE Three_PointO_ArchE/tools/file_system.py ---
# ResonantiA Protocol v3.1 - File System Tools
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def read_file(path: str) -> Dict[str, Any]:
    """Reads the content of a file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "Success", "path": path, "content": content}
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return {"status": "Failed", "path": path, "error": str(e)}

def create_file(path: str, content: str) -> Dict[str, Any]:
    """Creates a new file with the given content."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "Success", "path": path}
    except Exception as e:
        logger.error(f"Error creating file {path}: {e}")
        return {"status": "Failed", "path": path, "error": str(e)}

def list_directory(path: str) -> Dict[str, Any]:
    """Lists the contents of a directory."""
    try:
        entries = os.listdir(path)
        return {"status": "Success", "path": path, "entries": entries}
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        return {"status": "Failed", "path": path, "error": str(e)}

# --- END OF FILE ---
