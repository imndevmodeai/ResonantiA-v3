import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

def display_output(
    content: Any,
    format: str = "text",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Display output content with specified format.
    
    Args:
        content: Content to display
        format: Output format ("text", "json", "markdown")
        context: The action context (not directly used but required by execute_action signature).
        
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
        
        # Truncate content for raw_output_preview in IAR
        raw_output_preview = formatted_content[:200] + "..." if len(formatted_content) > 200 else formatted_content

        return {
            "output": formatted_content,
            "reflection": {
                "status": "Success",
                "confidence": 1.0,
                "summary": "Content successfully displayed.",
                "alignment_check": "Aligned with display objective.",
                "potential_issues": [],
                "raw_output_preview": raw_output_preview,
                "action": "display_output",
                "reflection": f"Content formatted as {format}"
            }
        }
        
    except Exception as e:
        error_msg = f"Error displaying output: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Truncate error message for raw_output_preview in IAR
        raw_output_preview = error_msg[:200] + "..." if len(error_msg) > 200 else error_msg

        return {
            "error": error_msg,
            "output": "",
            "reflection": {
                "status": "Failed",
                "confidence": 0.0,
                "summary": "Failed to display content due to an error.",
                "alignment_check": "Failed to align with display objective.",
                "potential_issues": [error_msg],
                "raw_output_preview": raw_output_preview,
                "action": "display_output",
                "reflection": error_msg
            }
        } 