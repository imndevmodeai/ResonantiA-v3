import os
from typing import Dict, Any, Optional
import logging
import json
import base64 # Added for Base64 encoding/decoding

logger = logging.getLogger(__name__)

async def custom_write_file_action(inputs: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    ArchE-specific action to create or overwrite a file with provided content.
    Returns an IAR-compliant reflection.
    """
    file_path = inputs.get("file_path")
    content = inputs.get("content", "")

    if not file_path:
        summary = "File path not provided."
        logger.error(f"Task '{context.task_key}': {summary}")
        return {
            "reflection": {
                "status": "Failed",
                "summary": summary,
                "confidence": 0.0,
                "alignment_check": "Misaligned",
                "potential_issues": ["Missing file_path input"],
                "raw_output_preview": ""
            }
        }

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        summary = f"Successfully created/overwritten file: {file_path}"
        logger.info(f"Task '{context.task_key}': {summary}")
        return {
            "reflection": {
                "status": "Success",
                "summary": summary,
                "confidence": 1.0,
                "alignment_check": "Aligned",
                "potential_issues": [],
                "raw_output_preview": f"Content written to {file_path}"
            },
            "file_path": file_path,
            "content_length": len(content)
        }
    except Exception as e:
        summary = f"Failed to write file {file_path}: {e}"
        logger.error(f"Task '{context.task_key}': {summary}", exc_info=True)
        return {
            "reflection": {
                "status": "Failed",
                "summary": summary,
                "confidence": 0.0,
                "alignment_check": "Misaligned",
                "potential_issues": [str(e)],
                "raw_output_preview": ""
            }
        }

async def read_file_custom(
    target_file: str,
    start_line_one_indexed: Optional[int] = None,
    end_line_one_indexed_inclusive: Optional[int] = None,
    should_read_entire_file: bool = False,
    context: Optional[Dict[str, Any]] = None # Required by execute_action signature
) -> Dict[str, Any]:
    """
    Custom tool to read the contents of a file or a specific range of lines.
    Returns content Base64-encoded and an IAR reflection.
    """
    iar = {
        "status": "fail",
        "confidence": 0.0,
        "potential_issues": [],
        "alignment_check": "not_aligned",
        "tactical_resonance": "low",
        "crystallization_potential": "low"
    }
    encoded_content = ""
    try:
        if not os.path.exists(target_file):
            iar["potential_issues"].append(f"File not found: {target_file}")
            iar["confidence"] = 0.1
            return {"content": encoded_content, "reflection": iar}

        with open(target_file, 'rb') as f: # Open in binary read mode
            if should_read_entire_file:
                raw_content = f.read()
            else:
                if start_line_one_indexed is None or end_line_one_indexed_inclusive is None:
                    iar["potential_issues"].append("Must specify line range or read entire file.")
                    iar["confidence"] = 0.2
                    return {"content": encoded_content, "reflection": iar}

                # For line-based reading, we still need to read lines and then encode
                lines = f.readlines()
                start_idx = max(0, start_line_one_indexed - 1)
                end_idx = min(len(lines), end_line_one_indexed_inclusive)
                raw_content = b"".join(lines[start_idx:end_idx]) # Join bytes

            encoded_content = base64.b64encode(raw_content).decode('utf-8')

        iar["status"] = "success"
        iar["confidence"] = 0.9
        iar["alignment_check"] = "aligned"
        iar["tactical_resonance"] = "high"
        iar["crystallization_potential"] = "medium"
        logger.info(f"Successfully read and Base64-encoded file: {target_file}")

    except Exception as e:
        iar["potential_issues"].append(f"Error reading file {target_file}: {str(e)}")
        iar["confidence"] = 0.0
        logger.error(f"Error in read_file_custom for {target_file}: {e}", exc_info=True)

    return {"content": encoded_content, "reflection": iar}

async def edit_file_custom(
    target_file: str,
    code_edit_base64: str, # Expect Base64 encoded content
    instructions: str, # For logging/context, not directly used for edit application here
    context: Optional[Dict[str, Any]] = None # Required by execute_action signature
) -> Dict[str, Any]:
    """
    Custom tool to edit the contents of a file, expecting Base64-encoded content.
    This basic version overwrites the file.
    Returns success status and an IAR reflection.
    """
    iar = {
        "status": "fail",
        "confidence": 0.0,
        "potential_issues": [],
        "alignment_check": "not_aligned",
        "tactical_resonance": "low",
        "crystallization_potential": "low"
    }
    try:
        decoded_content = base64.b64decode(code_edit_base64.encode('utf-8'))

        with open(target_file, 'wb') as f: # Open in binary write mode
            f.write(decoded_content)

        iar["status"] = "success"
        iar["confidence"] = 0.95
        iar["alignment_check"] = "aligned"
        iar["tactical_resonance"] = "high"
        iar["crystallization_potential"] = "medium"
        logger.info(f"Successfully edited (overwrote) file: {target_file} with Base64 content. Instructions: {instructions}")

    except Exception as e:
        iar["potential_issues"].append(f"Error editing file {target_file}: {str(e)}")
        iar["confidence"] = 0.0
        logger.error(f"Error in edit_file_custom for {target_file}: {e}", exc_info=True)

    return {"status": "complete", "reflection": iar} 