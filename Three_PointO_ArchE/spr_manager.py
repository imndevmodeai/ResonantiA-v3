# --- START OF FILE 3.0ArchE/spr_manager.py ---
# ResonantiA Protocol v3.0 - spr_manager.py
# Manages the loading, saving, querying, and validation of Sparse Priming Representations (SPRs).
# Acts as the interface to the persistent 'Knowledge tapestrY' (spr_definitions_tv.json).

import json
import os
import logging
import re
import time
import copy # For deepcopy operations
from typing import Dict, Any, List, Optional, Tuple, Union # Expanded type hints

# Use relative imports for configuration
try:
    from . import config # Assuming config is in the same package directory
except ImportError:
    # Fallback config if running standalone or package structure differs
    class FallbackConfig:
        KNOWLEDGE_GRAPH_DIR = 'knowledge_graph'
        SPR_JSON_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, 'spr_definitions_tv.json')
        # Add any other config variables that spr_manager might conceptually access
        # For instance, if it were to use metadata for SPR generation:
        # METADATA_DEFAULT_AUTHOR = "SPRManager_Fallback"
    config = FallbackConfig()
    logging.warning("config.py not found via relative import for spr_manager, using fallback.")

logger = logging.getLogger(__name__)

class SPRManager:
    """
    Handles persistence, retrieval, and basic validation of SPR definitions
    stored in a JSON file, representing the Knowledge Tapestry. Provides methods
    for CRUD operations and format checking (Guardian Points). (v3.0)
    """
    def __init__(self, spr_filepath: Optional[str] = None):
        """
        Initializes the SPRManager, loading SPRs from the specified file path.

        Args:
            spr_filepath (str, optional): Path to the SPR JSON definitions file.
                                        Defaults to config.SPR_JSON_FILE.
        """
        # Determine the SPR file path, prioritizing argument over config
        resolved_path = spr_filepath or getattr(config, 'SPR_JSON_FILE', None)
        if not resolved_path or not isinstance(resolved_path, str):
            # Critical error if no valid path can be determined
            raise ValueError("SPR filepath must be provided via argument or defined in config.SPR_JSON_FILE.")
        self.filepath = os.path.abspath(resolved_path) # Store absolute path
        self.sprs: Dict[str, Dict[str, Any]] = {} # Dictionary to hold loaded SPRs {spr_id: spr_definition}
        self.load_sprs() # Load SPRs immediately upon initialization

    def load_sprs(self):
        """
        Loads SPR definitions from the JSON file specified in self.filepath.
        Validates basic structure and SPR format, skipping invalid entries.
        Creates an empty file if it doesn't exist.
        """
        logger.info(f"Attempting to load SPR definitions from: {self.filepath}")
        if not os.path.exists(self.filepath):
            logger.warning(f"SPR definition file not found: {self.filepath}. Initializing empty store and creating file.")
            self.sprs = {}
            try:
                # Ensure directory exists before creating file
                spr_dir = os.path.dirname(self.filepath)
                if spr_dir: os.makedirs(spr_dir, exist_ok=True)
                # Create an empty JSON list in the file
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                logger.info(f"Created empty SPR file at {self.filepath}")
            except IOError as e:
                logger.error(f"Could not create empty SPR file at {self.filepath}: {e}")
            except Exception as e_create:
                logger.error(f"Unexpected error ensuring SPR file exists during load: {e_create}", exc_info=True)
            return # Return with empty self.sprs

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                spr_list = json.load(f)

            # Validate that the loaded data is a list
            if not isinstance(spr_list, list):
                logger.error(f"SPR file {self.filepath} does not contain a valid JSON list. Loading failed.")
                self.sprs = {}
                return

            loaded_count, duplicate_count, invalid_format_count, invalid_entry_count = 0, 0, 0, 0
            temp_sprs: Dict[str, Dict[str, Any]] = {} # Use temp dict to handle duplicates cleanly

            for idx, spr_def in enumerate(spr_list):
                # Validate entry structure
                if not isinstance(spr_def, dict):
                    logger.warning(f"Skipping invalid entry (not a dict) at index {idx} in {self.filepath}")
                    invalid_entry_count += 1; continue
                spr_id = spr_def.get("spr_id")
                if not spr_id or not isinstance(spr_id, str):
                    logger.warning(f"Skipping entry at index {idx} due to missing or invalid 'spr_id'.")
                    invalid_entry_count += 1; continue

                # Validate SPR format (Guardian Points)
                is_valid_format, _ = self.is_spr(spr_id)
                if not is_valid_format:
                    logger.warning(f"Skipping entry '{spr_id}' at index {idx} due to invalid SPR format.")
                    invalid_format_count += 1; continue

                # Check for duplicates based on spr_id
                if spr_id in temp_sprs:
                    logger.warning(f"Duplicate spr_id '{spr_id}' found at index {idx}. Keeping first occurrence.")
                    duplicate_count += 1
                else:
                    # Ensure 'term' field exists, default to spr_id if missing
                    if "term" not in spr_def or not spr_def.get("term"):
                        spr_def["term"] = spr_id
                    temp_sprs[spr_id] = spr_def # Add valid SPR definition to temp dict
                    loaded_count += 1

            self.sprs = temp_sprs # Assign validated SPRs to instance variable
            log_msg = f"Loaded {loaded_count} SPRs from {self.filepath}."
            if duplicate_count > 0: log_msg += f" Skipped {duplicate_count} duplicates."
            if invalid_format_count > 0: log_msg += f" Skipped {invalid_format_count} invalid format entries."
            if invalid_entry_count > 0: log_msg += f" Skipped {invalid_entry_count} invalid structure entries."
            logger.info(log_msg)

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from SPR file {self.filepath}: {e}. Loading failed.")
            self.sprs = {}
        except IOError as e:
            logger.error(f"Error reading SPR file {self.filepath}: {e}. Loading failed.")
            self.sprs = {}
        except Exception as e_load:
            logger.error(f"Unexpected error loading SPRs: {e_load}", exc_info=True)
            self.sprs = {}

    def save_sprs(self):
        """Saves the current in-memory SPR definitions back to the JSON file."""
        try:
            # Convert the dictionary of SPRs back into a list for saving
            spr_list = list(self.sprs.values())
            # Ensure the directory exists before writing
            spr_dir = os.path.dirname(self.filepath)
            if spr_dir: os.makedirs(spr_dir, exist_ok=True)
            # Write the list to the JSON file with indentation
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(spr_list, f, indent=2, default=str) # Use default=str for safety
            logger.info(f"Successfully saved {len(self.sprs)} SPRs to {self.filepath}")
        except IOError as e:
            logger.error(f"Error writing SPR file {self.filepath}: {e}")
        except TypeError as e_type:
            logger.error(f"Error serializing SPR data to JSON: {e_type}. Check for non-serializable objects in SPR definitions.")
        except Exception as e_save:
            logger.error(f"Unexpected error saving SPRs: {e_save}", exc_info=True)

    def add_spr(self, spr_definition: Dict[str, Any], overwrite: bool = False) -> bool:
        """
        Adds or updates an SPR definition in the manager and saves to file.
        Requires 'spr_id' and 'definition'. Validates format.

        Args:
            spr_definition (Dict[str, Any]): The dictionary representing the SPR.
            overwrite (bool): If True, allows overwriting an existing SPR with the same spr_id.

        Returns:
            bool: True if the SPR was successfully added/updated, False otherwise.
        """
        # Validate input structure
        if not isinstance(spr_definition, dict):
            logger.error("SPR definition must be a dictionary.")
            return False
        spr_id = spr_definition.get("spr_id")
        if not spr_id or not isinstance(spr_id, str):
            logger.error("Cannot add SPR definition: Missing or invalid string 'spr_id'.")
            return False

        # Validate SPR format
        is_valid_format, _ = self.is_spr(spr_id)
        if not is_valid_format:
            logger.error(f"Provided spr_id '{spr_id}' does not match the required SPR format (Guardian Points). Add failed.")
            return False

        # Check for existence and overwrite flag
        if spr_id in self.sprs and not overwrite:
            logger.warning(f"SPR with ID '{spr_id}' already exists. Use overwrite=True to replace. Add failed.")
            return False

        # Validate required fields
        if not isinstance(spr_definition.get("definition"), str) or not spr_definition.get("definition"):
            logger.error(f"SPR definition for '{spr_id}' missing required non-empty 'definition' string field. Add failed.")
            return False
        # Ensure 'term' exists, default to spr_id if missing
        if "term" not in spr_definition or not spr_definition.get("term"):
            spr_definition["term"] = spr_id
        # Ensure 'relationships' is a dict if present
        if "relationships" in spr_definition and not isinstance(spr_definition.get("relationships"), dict):
            logger.warning(f"Relationships field for '{spr_id}' is not a dictionary. Setting to empty dict.")
            spr_definition["relationships"] = {}

        # Add or update the SPR in the in-memory dictionary
        action = "Updated" if spr_id in self.sprs and overwrite else "Added"
        self.sprs[spr_id] = spr_definition # Add/overwrite entry
        logger.info(f"{action} SPR: '{spr_id}' (Term: '{spr_definition.get('term')}')")

        # Persist changes to the file
        self.save_sprs()
        return True

    def get_spr(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a deep copy of an SPR definition by its exact spr_id."""
        if not isinstance(spr_id, str):
            logger.warning(f"Invalid spr_id type ({type(spr_id)}) provided to get_spr.")
            return None
        spr_data = self.sprs.get(spr_id)
        if spr_data:
            logger.debug(f"Retrieved SPR definition for ID: {spr_id}")
            try:
                # Return a deep copy to prevent modification of the manager's internal state
                return copy.deepcopy(spr_data)
            except Exception as e_copy:
                logger.error(f"Failed to deepcopy SPR data for '{spr_id}': {e_copy}. Returning potentially shared reference (use with caution).", exc_info=True)
                return spr_data # Fallback to shallow reference
        else:
            logger.debug(f"SPR definition not found for ID: {spr_id}")
            return None

    def find_spr_by_term(self, term: str, case_sensitive: bool = False) -> Optional[Dict[str, Any]]:
        """
        Finds the first SPR definition matching a given term (in 'term' field or 'spr_id').
        Returns a deep copy.
        """
        if not isinstance(term, str) or not term:
            logger.warning("Invalid or empty term provided to find_spr_by_term.")
            return None

        found_spr: Optional[Dict[str, Any]] = None
        if case_sensitive:
            # Check 'term' field first (case-sensitive)
            for spr_data in self.sprs.values():
                if spr_data.get("term") == term:
                        found_spr = spr_data; break
            # If not found in 'term', check 'spr_id' (case-sensitive)
            if not found_spr and term in self.sprs:
                found_spr = self.sprs[term]
        else:
            term_lower = term.lower()
            # Check 'term' field first (case-insensitive)
            for spr_data in self.sprs.values():
                if spr_data.get("term", "").lower() == term_lower:
                        found_spr = spr_data; break
            # If not found in 'term', check 'spr_id' (case-insensitive)
            if not found_spr:
                for spr_id, spr_data in self.sprs.items():
                        if spr_id.lower() == term_lower:
                            found_spr = spr_data; break

        if found_spr:
            spr_id_found = found_spr.get("spr_id", "Unknown")
            logger.debug(f"Found SPR by term '{term}' (Case Sensitive: {case_sensitive}). SPR ID: {spr_id_found}")
            try:
                # Return a deep copy
                return copy.deepcopy(found_spr)
            except Exception as e_copy:
                logger.error(f"Failed to deepcopy found SPR data for term '{term}' (ID: {spr_id_found}): {e_copy}. Returning potentially shared reference.", exc_info=True)
                return found_spr
        else:
            logger.debug(f"SPR definition not found for term: '{term}' (Case Sensitive: {case_sensitive})")
            return None

    def get_all_sprs(self) -> List[Dict[str, Any]]:
        """Returns a deep copy of the list of all loaded SPR definitions."""
        try:
            # Return a deep copy to prevent external modification of the internal state
            return copy.deepcopy(list(self.sprs.values()))
        except Exception as e_copy:
            logger.error(f"Failed to deepcopy all SPRs: {e_copy}. Returning potentially shared references.", exc_info=True)
            return list(self.sprs.values()) # Fallback

    def is_spr(self, text: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Checks if a given text string strictly matches the SPR format (Guardian Points)
        based on user-defined rules:
        - Min length 3.
        - First char: Alphanumeric; if letter, must be UPPERCASE.
        - Last char: Alphanumeric; if letter, must be UPPERCASE.
        - Middle chars (if any): ONLY lowercase letters or spaces. No uppercase.
        - No leading/trailing spaces globally.
        - Word-based interpretation: Not strictly enforced here, but the pattern should
          allow for forms like "ExamplE" or "Word WordY".
          The core check is on character types at positions.
        """
        if not text or not isinstance(text, str):
            return False, "SPR text must be a non-empty string."

        # Rule: Min length 3
        if len(text) < 3:
            return False, f"SPR '{text}' is too short (min 3 chars required)."

        # Rule: No leading/trailing spaces globally (already implicitly handled by char checks if they fail on space)
        # but good to be explicit if we change logic later.
        if text.strip() != text:
            return False, f"SPR '{text}' must not have leading or trailing spaces."

        first_char = text[0]
        last_char = text[-1]
        middle_chars = text[1:-1] # This will be empty if len(text) == 2, handled by min length 3

        # Rule: First character
        if not first_char.isalnum():
            return False, f"SPR '{text}': First character '{first_char}' must be alphanumeric."
        if first_char.isalpha() and not first_char.isupper():
            return False, f"SPR '{text}': First alphabetic character '{first_char}' must be uppercase."

        # Rule: Last character
        if not last_char.isalnum():
            return False, f"SPR '{text}': Last character '{last_char}' must be alphanumeric."
        if last_char.isalpha() and not last_char.isupper():
            return False, f"SPR '{text}': Last alphabetic character '{last_char}' must be uppercase."

        # Rule: Middle characters (if any)
        if middle_chars: # Only check if middle_chars is not an empty string
            for char_idx, char_val in enumerate(middle_chars):
                if not (char_val.islower() or char_val.isspace()):
                    return False, f"SPR '{text}': Middle character '{char_val}' (at index {char_idx + 1}) must be lowercase or a space."
                if char_val.isupper(): # This is a stronger condition than the previous one, kept for clarity
                    return False, f"SPR '{text}': Middle character '{char_val}' (at index {char_idx + 1}) must not be uppercase."
        # If we made it here, all rules passed.
        return True, None

    # --- Conceptual SPR Writer/Decompressor Interface Methods ---
    # These methods provide a conceptual interface aligning with Section 3 roles.
    # Actual SPR creation is typically driven by InsightSolidification workflow using add_spr.
    # Actual decompression/activation happens implicitly via pattern recognition.

    def conceptual_write_spr(self, core_concept_term: str, definition: str, relationships: dict, blueprint: str, category: str = "General", metadata: Optional[Dict[str,Any]] = None) -> Optional[str]:
        """
        Conceptual function simulating the creation of an SPR term and adding its definition.
        Generates SPR ID from term, validates, and calls add_spr. Used for illustration.
        Now includes passed metadata, with default for ExampleUsage.
        """
        if not core_concept_term or not isinstance(core_concept_term, str) or not core_concept_term.strip():
            logger.error("SPR Write Error: Core concept term must be a non-empty string.")
            return None
        if not definition or not isinstance(definition, str):
            logger.error("SPR Write Error: Definition must be a non-empty string.")
            return None
        
        current_metadata = metadata if isinstance(metadata, dict) else {}

        term = core_concept_term.strip()
        # Attempt to generate SPR ID from term
        cleaned_term = re.sub(r'[^a-zA-Z0-9\s]', '', term).strip()
        if len(cleaned_term) < 2:
            logger.error(f"SPR Write Error: Cleaned core concept term '{cleaned_term}' is too short to generate SPR ID.")
            return None

        # Generate potential SPR ID using Guardian Points logic
        first_char = cleaned_term[0]
        last_char = cleaned_term[-1]
        middle_part = cleaned_term[1:-1].lower()
        generated_spr_id = first_char.upper() + middle_part + last_char.upper()

        # Validate the generated ID format
        is_valid_format, _ = self.is_spr(generated_spr_id)
        if not is_valid_format:
            logger.error(f"SPR Write Error: Generated SPR term '{generated_spr_id}' from '{core_concept_term}' has invalid format. Attempting fallback.")
            # Fallback attempt (e.g., first word initial + last word final char) - might fail
            words = cleaned_term.split()
            if len(words) >= 2:
                fallback_spr_id = words[0][0].upper() + words[0][1:].lower() + words[-1][-1].upper()
                is_valid_fallback, _ = self.is_spr(fallback_spr_id)
                if is_valid_fallback:
                        generated_spr_id = fallback_spr_id
                        logger.warning(f"Used fallback SPR term generation: '{generated_spr_id}'")
                else:
                        logger.error("Fallback SPR term generation also failed. Cannot create SPR.")
                        return None
            else:
                logger.error("Cannot generate valid SPR term from single word.")
                return None

        # Prepare the full SPR definition dictionary
        spr_def = {
            "spr_id": generated_spr_id,
            "term": core_concept_term,
            "definition": definition,
            "category": category if isinstance(category, str) else "General",
            "relationships": relationships if isinstance(relationships, dict) else {},
            "blueprint_details": blueprint if isinstance(blueprint, str) else "",
            "example_usage": current_metadata.get("ExampleUsage", ""), # Added field from template
            "metadata": { # Add some basic metadata from input or defaults
                "created_by": current_metadata.get("created_by", "ConceptualSPRWriter"),
                "timestamp": current_metadata.get("timestamp", time.time()),
                **{k: v for k, v in current_metadata.items() if k not in ["created_by", "timestamp", "ExampleUsage"]} # Include other metadata
            }
        }

        # Attempt to add the SPR using the standard method (will handle saving)
        if self.add_spr(spr_def, overwrite=False): # Default to not overwrite
            return generated_spr_id # Return the ID if successful
        else:
            logger.warning(f"Conceptual SPR Write: Failed to add SPR '{generated_spr_id}'. It might already exist (use overwrite=True) or validation failed.")
            return None # Return None on failure

    def conceptual_decompress_spr(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """
        Conceptual function simulating SPR decompression. Simply retrieves the SPR definition.
        Actual decompression is internal cognitive activation.
        """
        logger.debug(f"Conceptual Decompress: Retrieving definition for SPR ID '{spr_id}'")
        return self.get_spr(spr_id) # Uses the standard retrieval method

# --- END OF FILE 3.0ArchE/spr_manager.py --- 