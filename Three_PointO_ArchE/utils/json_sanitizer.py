from datetime import datetime

def _sanitize_for_json(data):
    """
    Recursively sanitizes a data structure to ensure it is JSON serializable.
    Converts non-serializable types to their string representation.
    """
    if data is None:
        return None
    if isinstance(data, (str, int, float, bool)):
        return data
    if isinstance(data, dict):
        return {k: _sanitize_for_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_sanitize_for_json(v) for v in data]
    if hasattr(data, 'isoformat'):  # Handle datetime objects
        return data.isoformat()
    # Handle exception objects to prevent serialization errors
    if isinstance(data, BaseException):
        return f"Exception: {type(data).__name__}: {str(data)}"
    # Fallback for other types
    return str(data)



