import os
import glob

# --- Configuration ---
OUTPUT_FILENAME = "Generated_Protocol_Section_7.md"
PROTOCOL_VERSION = "v3.5-GP"
PYTHON_SOURCE_DIR = "Three_PointO_ArchE"
WORKFLOW_SOURCE_DIR = "workflows"
KNOWLEDGE_SOURCE_FILE = os.path.join(PYTHON_SOURCE_DIR, "knowledge_graph", "spr_definitions_tv.json")

# Define the precise order and section numbering for Python files
PYTHON_FILE_ORDER = [
    (7.1, "config.py"),
    (7.2, "main.py"),
    (7.3, "workflow_engine.py"),
    (7.4, "action_registry.py"),
    (7.5, "spr_manager.py"),
    (7.6, "cfp_framework.py"),
    (7.7, "quantum_utils.py"),
    (7.8, "tools.py"),
    (7.9, "enhanced_tools.py"),
    (7.10, "code_executor.py"),
    (7.11, "logging_config.py"),
    (7.12, "error_handler.py"),
    (7.13, "causal_inference_tool.py"),
    (7.14, "agent_based_modeling_tool.py"),
    (7.19, "predictive_modeling_tool.py"), # Note the section number jump
    (7.22, "action_handlers.py"),
    # (7.23, "error_handler.py"), # Duplicate found in survey, assuming 7.12 is canonical
    # (7.24, "logging_config.py"), # Duplicate found in survey, assuming 7.11 is canonical
    (7.28, "system_representation.py"),
    (7.29, "cfp_implementation_example.py"),
]

def format_file_content(section_number, title, file_path, language="python"):
    """Reads a file and formats its content for the protocol document."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine the language for markdown code block
        if file_path.endswith(".json"):
            language = "json"
        elif file_path.endswith(".py"):
            language = "python"
        
        # Construct the formatted block
        header = f"**(7.{section_number} `{title}`)**\n"
        start_marker = f"# --- START OF FILE {os.path.join(PYTHON_SOURCE_DIR, title) if language == 'python' else file_path} ---\n"
        end_marker = f"# --- END OF FILE {os.path.join(PYTHON_SOURCE_DIR, title) if language == 'python' else file_path} ---\n"

        # Special handling for JSON to be wrapped in a code block for clarity
        if language == "json":
             formatted_content = f"{header}```{language}\n{start_marker}{content}\n{end_marker}```\n\n"
        else: # Python files are already formatted with comments
             formatted_content = f"{header}```python\n{start_marker}{content}\n{end_marker}```\n\n"

        return formatted_content

    except FileNotFoundError:
        print(f"Warning: File not found and will be skipped: {file_path}")
        return f"**(7.{section_number} `{title}`)**\n\n-- FILE NOT FOUND AT: {file_path} --\n\n"
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return f"**(7.{section_number} `{title}`)**\n\n-- ERROR PROCESSING FILE: {file_path} | {e} --\n\n"


def main():
    """Main function to generate the Section 7 document."""
    print(f"Starting generation of Section 7 for ResonantiA Protocol {PROTOCOL_VERSION}...")
    
    all_content = []
    
    # --- 1. Process Core Python Files in specified order ---
    print("Processing core Python files...")
    for section_num, filename in PYTHON_FILE_ORDER:
        file_path = os.path.join(PYTHON_SOURCE_DIR, filename)
        # We pass the floating point number as is, and format it inside the function
        # This is a bit unusual but works for this specific case.
        # A more robust way might be to handle section numbers as strings.
        section_int = int(str(section_num).split('.')[1])
        all_content.append(format_file_content(section_int, filename, file_path, language="python"))

    # --- 2. Process the Knowledge Graph (SPR Definitions) ---
    print("Processing Knowledge Graph file...")
    # Manually assign section number for the SPR file
    all_content.append(format_file_content(15, os.path.basename(KNOWLEDGE_SOURCE_FILE), KNOWLEDGE_SOURCE_FILE, language="json"))

    # --- 3. Process Workflow Files ---
    print(f"Processing workflow files from {WORKFLOW_SOURCE_DIR}...")
    workflow_files = sorted(glob.glob(os.path.join(WORKFLOW_SOURCE_DIR, "*.json")))
    
    # Assign section numbers starting from 16, skipping known numbers
    known_sections = {int(str(s).split('.')[1]) for s, f in PYTHON_FILE_ORDER}
    known_sections.add(15) # Add the SPR section
    
    current_workflow_section = 16
    for wf_path in workflow_files:
        while current_workflow_section in known_sections:
            current_workflow_section += 1
        
        filename = os.path.basename(wf_path)
        all_content.append(format_file_content(current_workflow_section, filename, wf_path, language="json"))
        known_sections.add(current_workflow_section) # Add to used sections
        current_workflow_section += 1

    # --- 4. Write the final output file ---
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(f"# Section 7: Complete Source Code & Placeholders ({PROTOCOL_VERSION})\n\n")
            f.write("*(This section is auto-generated from the project's source files.)*\n\n")
            f.writelines(all_content)
        print(f"\nSuccessfully generated protocol document: {OUTPUT_FILENAME}")
        print(f"Total files documented: {len(all_content)}")
    except IOError as e:
        print(f"Fatal Error: Could not write output file {OUTPUT_FILENAME}: {e}")

if __name__ == "__main__":
    main()
