import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

def display_output(
    content: Any,
    format: str = "text"
) -> Dict[str, Any]:
    """
    Display output content with specified format.
    
    Args:
        content: Content to display
        format: Output format ("text", "json", "markdown")
        
    Returns:
        Dictionary containing display result and IAR reflection
    """
    try:
        # Format content based on specified format
        if format == "json":
            if isinstance(content, dict):
                formatted_content = json.dumps(content, indent=2)
            else:
                formatted_content = str(content)
        elif format == "markdown":
            formatted_content = str(content)
        else:  # text
            formatted_content = str(content)
        
        # Log the output
        logger.info(f"Display output ({format}):\n{formatted_content}")
        
        return {
            "output": formatted_content,
            "reflection": {
                "status": "Success",
                "confidence": 1.0,
                "insight": "Output displayed successfully",
                "action": "display_output",
                "reflection": f"Content formatted as {format}"
            }
        }
        
    except Exception as e:
        error_msg = f"Error displaying output: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "output": "",
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "insight": "Output display failed",
                "action": "display_output",
                "reflection": error_msg
            }
        } 