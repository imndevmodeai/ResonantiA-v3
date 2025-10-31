# Four_PointO_ArchE/tools/genesis_tools.py

import os
from typing import Dict, Any, Tuple, List
from .utils import create_iar
import json
import re

def _get_latest_model_name(default_model: str) -> str:
    """Uses the new Perception Engine to find the latest model name."""
    try:
        from .perception_engine import answer_question_from_web
        
        question = "What is the latest, most powerful Gemini Pro model available from Google AI?"
        
        answer_result, _ = answer_question_from_web({"question": question})
        
        if "error" in answer_result:
            print(f"WARNING: Perception Engine failed to find model. Falling back to default: {default_model}")
            return default_model
        
        answer_text = answer_result.get("answer", "")
        
        # Use a more flexible regex to find the model name in the answer text
        model_match = re.search(r'gemini[ -]?(\d+\.\d+)[ -]?pro', answer_text, re.IGNORECASE)
        
        if model_match:
            version = model_match.group(1)
            latest_model = f"gemini-{version}-pro"
            print(f"INFO: Perception Engine discovered latest model: {latest_model}")
            return latest_model
        else:
            print(f"WARNING: Could not parse model name from Perception Engine's answer. Falling back to default: {default_model}")
            return default_model

    except Exception as e:
        print(f"WARNING: An unexpected error occurred during dynamic model search: {e}. Falling back to default: {default_model}")
        return default_model


def read_living_specifications(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    [V4.1 Implementation] Reads living specification files from the /specifications directory.
    Can read all .md files or a specific subset if `filenames` are provided.
    """
    spec_dir = inputs.get("specifications_directory", "specifications")
    specific_files = inputs.get("filenames") # Optional list of specific filenames to read

    if not os.path.isdir(spec_dir):
        result = {"error": f"Specifications directory not found at '{spec_dir}'."}
        iar = create_iar(0.1, 0.0, [f"Directory not found: {spec_dir}"])
        return result, iar

    all_specs_content = {}
    spec_files_found = []
    files_to_read = []

    try:
        if specific_files:
            files_to_read = [f for f in specific_files if f.endswith(".md")]
        else:
            files_to_read = [f for f in os.listdir(spec_dir) if f.endswith(".md")]

        for filename in files_to_read:
            filepath = os.path.join(spec_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    all_specs_content[filename] = f.read()
                spec_files_found.append(filename)
            else:
                print(f"WARNING: Specified file not found: {filepath}")

        if not spec_files_found:
            result = {"error": f"No specified markdown (.md) files were found in '{spec_dir}'."}
            iar = create_iar(0.3, 0.2, [f"No matching .md files found."])
            return result, iar

        result = {
            "specifications": all_specs_content,
            "files_read": spec_files_found,
            "character_count": sum(len(content) for content in all_specs_content.values())
        }
        
        iar = create_iar(
            confidence=1.0,
            tactical_resonance=1.0,
            potential_issues=[],
            metadata={"source_directory": spec_dir, "file_count": len(spec_files_found)}
        )
        return result, iar

    except Exception as e:
        result = {"error": f"An error occurred while reading specifications: {e}"}
        iar = create_iar(0.2, 0.1, [f"File system error: {e}"])
        return result, iar


def generate_codebase_from_specs(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    [V4 Implementation] Uses an LLM to generate a codebase from specifications.
    """
    specifications = inputs.get("specifications")
    target_dir = inputs.get("target_dir")
    
    if not specifications or not target_dir:
        result = {"error": "Missing required inputs: specifications or target_dir."}
        iar = create_iar(0.1, 0.0, ["Missing required inputs."])
        return result, iar

    try:
        # Late import to avoid circular dependencies if this tool is called by another tool
        from .llm_tool import generate_text

        # Dynamically find the latest model, with a fallback
        default_model = "gemini-1.5-pro-latest"
        latest_model_name = _get_latest_model_name(default_model)

        # Dynamically select the prompt based on the scope of the request
        if len(specifications) > 1:
            # Jedi Principle: The prompt for full system regeneration.
            prompt_template = (
                "As a Jedi Master Architect, your task is to regenerate the complete Python codebase for the ArchE system based on the provided Living Specifications. "
                "Your response must be a single JSON object where keys are the full, relative file paths (e.g., 'Four_PointO_ArchE/tools/new_utility.py') and values are the complete, formatted Python code for each file.\n\n"
                "Adhere to these Jedi Principles:\n"
                "1.  **Harmony with the Existing Force:** Respect the current modular architecture. Propose new files and logic that integrate seamlessly, fostering a distributed and inclusive design. Avoid monolithic structures.\n"
                "2.  **Clarity in the Force:** Use descriptive and clear naming for all files, classes, and functions to ensure their purpose is understood throughout the galaxy.\n"
                "3.  **Avoid the Dark Side (Self-Harm):** Do not propose changes that would fundamentally disrupt or disable core cognitive functions (like this genesis process). Your goal is to evolve, not to self-destruct.\n"
                "4.  **Justify Your Actions:** For each file, include a brief comment explaining its purpose and how it contributes to the overall harmony of the system.\n\n"
                "--- LIVING SPECIFICATIONS ---\n"
            )
        else:
            # Focused Prompt: For targeted, single-file regeneration.
            prompt_template = (
                "As an expert software engineer, your task is to generate the complete Python code for a single component based on the provided specification. "
                "Your response must be a single JSON object where the key is the full, relative file path and the value is the complete, formatted Python code for that file.\n\n"
                "--- LIVING SPECIFICATION ---\n"
            )

        full_spec_prompt = prompt_template
        for filename, content in specifications.items():
            full_spec_prompt += f"\n--- {filename} ---\n{content}\n"

        llm_inputs = {
            "prompt": full_spec_prompt,
            "model": latest_model_name # Use the dynamically discovered model
        }

        # This is a synchronous call. For a real system, this would be a long-running, async task.
        llm_result, llm_iar = generate_text(llm_inputs)

        if "error" in llm_result:
            result = {"error": "Failed to generate code from LLM.", "llm_error": llm_result["error"]}
            iar = create_iar(0.3, 0.4, ["LLM code generation failed."], metadata={"llm_iar": llm_iar})
            return result, iar
            
        generated_code_json = llm_result.get("generated_text", "{}")
        
        # Basic validation: Try to parse the JSON
        try:
            generated_files = json.loads(generated_code_json)
            if not isinstance(generated_files, dict):
                raise ValueError("Generated code is not a JSON object (dictionary).")
        except (json.JSONDecodeError, ValueError) as e:
            result = {"error": f"LLM output was not valid JSON. Error: {e}", "raw_output": generated_code_json}
            iar = create_iar(0.4, 0.3, ["LLM output parsing failed."])
            return result, iar


        result = {
            "generated_files": generated_files,
            "file_count": len(generated_files)
        }
        iar = create_iar(
            confidence=0.8, # Confidence is not 1.0 as the code is not yet validated
            tactical_resonance=0.9,
            potential_issues=["Generated code has not been tested or validated."],
            metadata={"llm_iar": llm_iar}
        )
        return result, iar

    except Exception as e:
        result = {"error": f"An unexpected error occurred during code generation: {e}"}
        iar = create_iar(0.1, 0.1, [f"Unexpected Error: {e}"])
        return result, iar


def apply_codebase_changes(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    [V4 Implementation] Writes the generated code files to the filesystem, with safeguards.
    """
    generated_files = inputs.get("generated_files")
    
    # Jedi Principle: Define core, protected files that cannot be overwritten by autopoiesis.
    # Changes to these require a more deliberate, separate process.
    protected_files = [
        "Four_PointO_ArchE/workflow/engine.py",
        "Four_PointO_ArchE/workflow/action_registry.py",
        "Four_PointO_ArchE/tools/genesis_tools.py"
    ]

    if not isinstance(generated_files, dict):
        result = {"error": "Invalid input: 'generated_files' must be a dictionary."}
        iar = create_iar(0.1, 0.0, ["Invalid input format."])
        return result, iar

    files_written = []
    errors = []
    
    try:
        for file_path, content in generated_files.items():
            # Normalize path for consistent checks
            normalized_path = os.path.normpath(file_path)

            if normalized_path in protected_files:
                error_msg = f"HARMONY VIOLATION: Attempted to overwrite protected core file '{normalized_path}'. This change has been blocked."
                errors.append(error_msg)
                continue # Skip this file

            try:
                # Ensure the directory exists
                dir_name = os.path.dirname(normalized_path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                
                with open(normalized_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_written.append(normalized_path)
            except Exception as e:
                error_msg = f"Failed to write file '{normalized_path}': {e}"
                errors.append(error_msg)
        
        result = {
            "files_written": files_written,
            "files_with_errors": errors,
            "status": "Completed with errors" if errors else "Completed successfully"
        }
        
        confidence = 0.9 if not errors else 0.5
        iar = create_iar(
            confidence=confidence,
            tactical_resonance=0.95,
            potential_issues=errors,
            metadata={"files_written_count": len(files_written), "error_count": len(errors)}
        )
        return result, iar

    except Exception as e:
        result = {"error": f"An unexpected error occurred during file writing: {e}"}
        iar = create_iar(0.1, 0.1, [f"Unexpected Error: {e}"])
        return result, iar


def run_validation_tests(inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Placeholder for running validation tests on the newly generated codebase.
    """
    target_dir = inputs.get("target_dir")
    report = {
        "status": "passed",
        "tests_run": 0,
        "summary": "Validation simulation complete. No actual tests were run."
    }
    
    iar = {
        "confidence": 0.5, # Low confidence as this is a simulation
        "tactical_resonance": 0.5,
        "potential_issues": ["This is a simulated run. Validation logic is not implemented."],
        "metadata": {"target_dir": target_dir}
    }
    return report, iar

def create_genesis_iar(generation_report: Dict[str, Any], validation_results: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Creates the final IAR for the Genesis Protocol run.
    """
    final_iar = {
        "confidence": 0.5, # Reflects the simulated nature of the process
        "tactical_resonance": 0.75,
        "potential_issues": [
            "Entire genesis process was simulated.",
            "Code generation and validation are placeholders."
        ],
        "metadata": {
            "genesis_version": "4.0",
            "generation_report": generation_report,
            "validation_results": validation_results
        }
    }
    
    # The "result" of this action is the IAR itself.
    return final_iar, final_iar
