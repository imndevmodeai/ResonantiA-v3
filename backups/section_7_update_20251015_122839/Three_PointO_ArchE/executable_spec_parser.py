import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

def ingest_canonical_specification(file_path: str, section_hint: str = '7') -> Dict[str, Any]:
    """
    Ingests the canonical protocol markdown file and prepares it for blueprint deconstruction.
    This function primarily reads the file content. The core parsing logic resides in
    deconstruct_code_blueprints.

    Args:
        file_path: The path to the canonical specification markdown file.
        section_hint: The top-level section number to look for (as a string, e.g., '7').

    Returns:
        A dictionary containing the file content and initial IAR reflection.
    """
    try:
        spec_path = Path(file_path)
        if not spec_path.is_file():
            raise FileNotFoundError(f"Specification file not found at: {spec_path}")

        content = spec_path.read_text(encoding='utf-8')
        
        reflection = {
            "status": "Success",
            "summary": f"Successfully ingested specification file '{file_path}'.",
            "confidence": 0.95,
            "alignment_check": "Aligned with autopoietic genesis input requirements.",
            "potential_issues": None,
            "raw_output_preview": content[:200] + "..."
        }
        
        return {
            "content": content,
            "file_path": str(spec_path),
            "reflection": reflection
        }

    except Exception as e:
        logger.error(f"Failed to ingest canonical specification from '{file_path}': {e}", exc_info=True)
        reflection = {
            "status": "Failure",
            "summary": f"Failed to ingest specification file: {e}",
            "confidence": 0.0,
            "alignment_check": "Failed to meet input requirements.",
            "potential_issues": [str(e)],
            "raw_output_preview": None
        }
        return {"content": None, "file_path": file_path, "reflection": reflection}


def deconstruct_code_blueprints(spec_content: str, section_hint: str = '7') -> Dict[str, Any]:
    """
    Parses the content of a canonical protocol markdown file to extract executable
    code blueprints from a specified section (typically Section 7).

    Args:
        spec_content: The string content of the markdown specification.
        section_hint: The top-level section number to parse (e.g., '7').

    Returns:
        A dictionary containing the list of extracted blueprints and a summary report.
    """
    blueprints = []
    summary = {
        "blueprints_found": 0,
        "missing_section": True,
        "anomalies": [],
        "processed_files": []
    }
    
    # Regex to find Section 7 (or other hint) and its subsections
    section_pattern = re.compile(
        r"^(#\s*" + re.escape(section_hint) + r"\..*|##\s*" + re.escape(section_hint) + r"\..*|###\s*" + re.escape(section_hint) + r"\..*)",
        re.MULTILINE
    )
    
    # Regex for markdown code fences with language and optional filename
    # ```python(Three_PointO_ArchE/example.py)
    fence_pattern = re.compile(
        r"```(\w+)(?:\(([^)]+)\))?\s*\n(.*?)```", 
        re.DOTALL
    )

    lines = spec_content.split('\n')
    in_target_section = False
    
    for i, line in enumerate(lines):
        # Determine if we are inside the target section
        if line.strip().startswith(f'# {section_hint}') or line.strip().startswith(f'## {section_hint}'):
            in_target_section = True
            summary['missing_section'] = False
            continue
        # Stop if we hit the next major section
        if in_target_section and line.strip().startswith('# '):
            break

        if not in_target_section:
            continue
            
    if summary['missing_section']:
        logger.warning(f"Could not find Section {section_hint} in the provided specification.")
        return {"blueprints": [], "summary": summary}

    # Use finditer to get all matches in the spec_content
    for match in fence_pattern.finditer(spec_content):
        language = match.group(1).lower().strip()
        path_hint = match.group(2)
        code = match.group(3).strip()
        
        file_path = path_hint
        
        if not file_path:
            # If no path hint, try to find a heading just before the code block
            # This is a simple heuristic and might need refinement
            preceding_text = spec_content[:match.start()]
            last_heading = re.findall(r"####?\s*`([^`]+)`", preceding_text)
            if last_heading:
                file_path = last_heading[-1]

        if not file_path:
            summary['anomalies'].append({
                "type": "missing_filepath",
                "location_hint": f"Around line where code block starts: ```{language}",
                "details": "Code block found without a direct path hint `(path/to/file.ext)` or a preceding heading with a filename."
            })
            continue

        # Normalize path
        normalized_path = _normalize_path(file_path)

        blueprint = {
            "file_path": normalized_path,
            "specification": code,
            "language": language
        }
        blueprints.append(blueprint)
        summary['processed_files'].append(normalized_path)

    summary["blueprints_found"] = len(blueprints)
    
    reflection = {
        "status": "Success" if blueprints else "Warning",
        "summary": f"Deconstruction complete. Found {len(blueprints)} blueprints.",
        "confidence": 0.9,
        "alignment_check": "Aligned with autopoietic genesis requirements.",
        "potential_issues": [f"{len(summary['anomalies'])} anomalies found."] if summary['anomalies'] else None,
        "raw_output_preview": json.dumps(summary, indent=2)
    }

    return {
        "blueprints": blueprints,
        "summary": summary,
        "reflection": reflection
    }

def _normalize_path(path_str: str) -> str:
    """
    Normalizes a given path string to ensure it follows consistent conventions.
    - Ensures paths intended for the core system are under 'Three_PointO_ArchE/'.
    - Handles other known top-level directories like 'workflows/' and 'knowledge_graph/'.
    """
    path_str = path_str.strip()
    
    # Known top-level dirs that are NOT in the ArchE package
    known_roots = ["workflows/", "knowledge_graph/", "specifications/"]
    
    for root in known_roots:
        if path_str.startswith(root):
            return path_str
            
    # If it's a python file and not explicitly in another root, assume it belongs in the core package
    if path_str.endswith(".py") and not path_str.startswith("Three_PointO_ArchE/"):
        return f"Three_PointO_ArchE/{path_str}"
        
    return path_str

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # This example assumes you are running from the project root
    # and the protocol file exists.
    protocol_file = 'ResonantiA_Protocol_v3.1-CA.md'
    
    ingest_result = ingest_canonical_specification(protocol_file)
    
    if ingest_result['content']:
        logger.info("Successfully ingested the specification.")
        
        deconstruction_result = deconstruct_code_blueprints(ingest_result['content'])
        
        summary = deconstruction_result['summary']
        blueprints = deconstruction_result['blueprints']
        
        logger.info("\n--- Deconstruction Summary ---")
        logger.info(json.dumps(summary, indent=2))
        
        if blueprints:
            logger.info(f"\n--- Found {len(blueprints)} Blueprints ---")
            for bp in blueprints:
                logger.info(f"  - Path: {bp['file_path']}, Language: {bp['language']}, Spec Length: {len(bp['specification'])}")
        
        # Save blueprints to a file for the workflow to use
        output_path = Path("outputs/blueprints.json")
        output_path.parent.mkdir(exist_ok=True, parents=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(blueprints, f, indent=2)
        logger.info(f"\nBlueprints saved to: {output_path}")

    else:
        logger.error("Failed to ingest the specification. Cannot proceed with deconstruction.")
        logger.error(f"Details: {ingest_result['reflection']['summary']}")
