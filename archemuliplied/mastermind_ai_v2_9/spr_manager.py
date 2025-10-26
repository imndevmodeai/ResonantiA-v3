# ResonantiA Protocol v2.9.5 - spr_manager.py
# Manages the loading, saving, and querying of Sparse Priming Representations (SPRs).
# Emphasizes KG as management tool for internal cognitive triggers.

import json
import os
import logging
import re # For more robust SPR format checking
import time # For timestamping
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)
# Ensure logging is configured by the main application or set a default handler
if not logger.hasHandlers():
     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SPRManager:
    """
    Handles the persistence and retrieval of SPR definitions from a JSON file.
    Acts as the interface to the conceptual 'Knowledge tapestrY'.
    Provides methods for checking SPR format and conceptual management.
    """
    def __init__(self, spr_filepath: str):
        """
        Initializes the SPRManager.
        Args:
            spr_filepath (str): The path to the JSON file storing SPR definitions.
        """
        if not spr_filepath or not isinstance(spr_filepath, str):
             raise ValueError("SPR filepath must be a non-empty string.")
        self.filepath = spr_filepath
        # Stores SPRs keyed by spr_id (the SPR term itself, e.g., "KnowledgE")
        self.sprs: Dict[str, Dict[str, Any]] = {}
        self.load_sprs()

    def load_sprs(self):
        """Loads SPR definitions from the JSON file."""
        if not os.path.exists(self.filepath):
            logger.warning(f"SPR definition file not found: {self.filepath}. Initializing empty store.")
            self.sprs = {}
            # Create an empty file with an empty list structure
            try:
                # Ensure parent directory exists first
                spr_dir = os.path.dirname(self.filepath)
                if spr_dir: os.makedirs(spr_dir, exist_ok=True)
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                logger.info(f"Created empty SPR file at {self.filepath}")
            except IOError as e:
                logger.error(f"Could not create empty SPR file at {self.filepath}: {e}")
            except Exception as e:
                 logger.error(f"Unexpected error ensuring SPR file exists during load: {e}", exc_info=True)
            return

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                spr_list = json.load(f)
                if not isinstance(spr_list, list):
                     logger.error(f"SPR file {self.filepath} does not contain a JSON list. Loading failed.")
                     self.sprs = {}
                     return

                # Use the SPR term (e.g., "KnowledgE") as the primary key for faster lookup
                loaded_count = 0
                duplicate_count = 0
                invalid_count = 0
                temp_sprs = {}
                for idx, spr_def in enumerate(spr_list):
                    if not isinstance(spr_def, dict):
                         logger.warning(f"Item at index {idx} in SPR file is not a dictionary. Skipping.")
                         invalid_count += 1
                         continue

                    spr_term = spr_def.get("spr_id") # Assuming spr_id holds the term like "KnowledgE"
                    is_valid_format, _ = self.is_spr(spr_term) # Validate format using internal method

                    if not spr_term or not is_valid_format:
                         logger.warning(f"Invalid or missing spr_id/term format in definition at index {idx}: {spr_def}. Skipping.")
                         invalid_count += 1
                         continue

                    if spr_term in temp_sprs:
                         logger.warning(f"Duplicate SPR term/ID found: '{spr_term}' at index {idx}. Keeping first occurrence.")
                         duplicate_count += 1
                    else:
                         temp_sprs[spr_term] = spr_def
                         loaded_count += 1

                self.sprs = temp_sprs
                log_msg = f"Loaded {loaded_count} SPRs from {self.filepath}."
                if duplicate_count > 0: log_msg += f" Skipped {duplicate_count} duplicates."
                if invalid_count > 0: log_msg += f" Skipped {invalid_count} invalid entries."
                logger.info(log_msg)

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from SPR file {self.filepath}: {e}")
            self.sprs = {}
        except IOError as e:
            logger.error(f"Error reading SPR file {self.filepath}: {e}")
            self.sprs = {}
        except Exception as e:
            logger.error(f"Unexpected error loading SPRs: {e}", exc_info=True)
            self.sprs = {}


    def save_sprs(self):
        """Saves the current SPR definitions back to the JSON file."""
        try:
            spr_list = list(self.sprs.values())
            # Ensure directory exists before writing
            spr_dir = os.path.dirname(self.filepath)
            if spr_dir: os.makedirs(spr_dir, exist_ok=True)

            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(spr_list, f, indent=2, default=str) # Use default=str for safety
            logger.info(f"Saved {len(self.sprs)} SPRs to {self.filepath}")
        except IOError as e:
            logger.error(f"Error writing SPR file {self.filepath}: {e}")
        except TypeError as e:
             logger.error(f"Error serializing SPR data to JSON: {e}. Check for non-serializable objects.")
        except Exception as e:
            logger.error(f"Unexpected error saving SPRs: {e}", exc_info=True)

    def add_spr(self, spr_definition: Dict[str, Any], overwrite: bool = False) -> bool:
        """
        Adds or updates an SPR definition using the 'spr_id' key (which should be the SPR term itself).

        Args:
            spr_definition: A dictionary containing the SPR details (must include 'spr_id' matching format).
            overwrite: If True, overwrite existing SPR with the same ID/term.

        Returns:
            True if added/overwritten successfully, False otherwise.
        """
        if not isinstance(spr_definition, dict):
             logger.error("SPR definition must be a dictionary.")
             return False

        spr_id = spr_definition.get("spr_id") # The SPR term, e.g., "KnowledgE"
        if not spr_id or not isinstance(spr_id, str):
            logger.error("Cannot add SPR definition without a valid string 'spr_id' (the SPR term).")
            return False
        is_valid_format, _ = self.is_spr(spr_id)
        if not is_valid_format:
             logger.error(f"Provided spr_id '{spr_id}' does not match the required SPR format.")
             return False

        if spr_id in self.sprs and not overwrite:
            logger.warning(f"SPR with ID/Term '{spr_id}' already exists. Use overwrite=True to replace.")
            return False

        # Basic validation of required fields
        if not isinstance(spr_definition.get("definition"), str) or not spr_definition.get("definition"):
             logger.error(f"SPR definition for '{spr_id}' missing required non-empty 'definition' string field.")
             return False
        # Add term field if missing, based on spr_id
        if "term" not in spr_definition or not spr_definition.get("term"):
             spr_definition["term"] = spr_id # Use the ID as the display term if not provided

        # Ensure relationships is a dict if present
        if "relationships" in spr_definition and not isinstance(spr_definition["relationships"], dict):
             logger.warning(f"Relationships for SPR '{spr_id}' is not a dict. Resetting to empty dict.")
             spr_definition["relationships"] = {}


        action = "Updated" if spr_id in self.sprs and overwrite else "Added"
        self.sprs[spr_id] = spr_definition # Add or overwrite
        logger.info(f"{action} SPR: {spr_id}")
        self.save_sprs() # Save after modification
        return True

    def get_spr(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an SPR definition by its ID/term (e.g., "KnowledgE")."""
        if not isinstance(spr_id, str): return None # ID must be string
        spr_data = self.sprs.get(spr_id)
        if spr_data:
             logger.debug(f"Retrieved SPR: {spr_id}")
        else:
             logger.debug(f"SPR not found: {spr_id}")
        return spr_data # Returns dict or None

    def find_spr_by_term(self, term: str, case_sensitive: bool = False) -> Optional[Dict[str, Any]]:
         """
         Finds the first SPR definition matching a given term.
         Searches the 'term' field first, then 'spr_id' field.
         """
         if not isinstance(term, str): return None

         if case_sensitive:
              # Check term field first
              for spr_id, spr_data in self.sprs.items():
                   if spr_data.get("term") == term:
                        logger.debug(f"Found SPR by case-sensitive term '{term}': {spr_id}")
                        return spr_data
              # Check spr_id field as fallback
              if term in self.sprs:
                   logger.debug(f"Found SPR by case-sensitive spr_id '{term}'.")
                   return self.sprs[term]
         else:
              term_lower = term.lower()
              # Check term field first (case-insensitive)
              for spr_id, spr_data in self.sprs.items():
                   if spr_data.get("term", "").lower() == term_lower:
                        logger.debug(f"Found SPR by case-insensitive term '{term}': {spr_id}")
                        return spr_data
              # Check spr_id field as fallback (case-insensitive)
              for spr_id, spr_data in self.sprs.items():
                    if spr_id.lower() == term_lower:
                         logger.debug(f"Found SPR by case-insensitive spr_id '{term}'.")
                         return spr_data

         logger.debug(f"SPR not found for term: {term} (Case Sensitive: {case_sensitive})")
         return None

    def get_all_sprs(self) -> List[Dict[str, Any]]:
        """Returns a list of all loaded SPR definitions."""
        return list(self.sprs.values())

    def is_spr(self, text: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Checks if a given text string matches the SPR format (Guardian Points).
        Format: Starts with Uppercase/Digit, Ends with Uppercase/Digit, Middle is all Lowercase/Space (or empty).
        Excludes all-caps strings longer than a threshold (e.g., 3 chars).

        Args:
            text: The string to check.

        Returns:
            A tuple: (bool indicating if it matches the format, the text itself if matched else None).
        """
        if not text or not isinstance(text, str) or len(text) < 1:
            return False, None

        # Handle single character case - Assume NOT an SPR
        if len(text) == 1:
             return False, None

        # Length 2 or more
        first_char = text[0]
        last_char = text[-1]
        middle_part = text[1:-1]

        is_first_guardian = first_char.isupper() or first_char.isdigit()
        is_last_guardian = last_char.isupper() or last_char.isdigit()

        # Middle part must be all lowercase OR spaces OR empty
        # Allow spaces based on examples like 'As Above So BeloW'
        is_middle_valid = all(c.islower() or c.isspace() for c in middle_part) or not middle_part

        # Exclude all caps (e.g., "NASA", "API") which might fit pattern otherwise
        # Allow short all caps like 'AI' potentially? Let's exclude all caps > 3 chars.
        is_all_caps = text.isupper()
        exclude_all_caps = is_all_caps and len(text) > 3 # Heuristic threshold

        is_match = is_first_guardian and is_last_guardian and is_middle_valid and not exclude_all_caps

        return is_match, text if is_match else None

    # --- Conceptual SPR Writer/Decompressor Interface ---

    def conceptual_write_spr(self, core_concept_term: str, definition: str, relationships: dict, blueprint: str, category: str = "General") -> Optional[str]:
         """
         Conceptual function for creating an SPR term and adding its definition.
         Generates SPR term from core_concept_term based on rules.
         """
         if not core_concept_term or not isinstance(core_concept_term, str) or not core_concept_term.strip():
              logger.error("Core concept term must be a non-empty string for SPR creation.")
              return None
         if not definition or not isinstance(definition, str):
              logger.error("Definition must be a non-empty string for SPR creation.")
              return None


         # Generate SPR ID/Term from the core concept term
         term = core_concept_term.strip()
         # Clean term: Remove problematic chars for format rule, keep spaces
         # Allow letters, numbers, spaces for middle part generation
         cleaned_term = re.sub(r'[^a-zA-Z0-9\s]', '', term)
         cleaned_term = cleaned_term.strip() # Remove leading/trailing spaces after cleaning

         if len(cleaned_term) < 2:
              logger.error(f"Cleaned core concept term '{cleaned_term}' too short to generate SPR term.")
              return None

         # Construct SPR ID using first/last of cleaned term
         spr_id = cleaned_term[0].upper() + cleaned_term[1:-1].lower() + cleaned_term[-1].upper()

         # Validate the generated SPR format (should pass if logic is correct)
         is_valid_format, _ = self.is_spr(spr_id)
         if not is_valid_format:
              logger.error(f"Generated SPR term '{spr_id}' from '{core_concept_term}' has invalid format after cleaning. Check input or generation logic.")
              # Try a simpler fallback? e.g., FirstWordLastWorD?
              words = cleaned_term.split()
              if len(words) >= 2:
                   spr_id = words[0][0].upper() + words[0][1:].lower() + words[-1][-1].upper() # Example fallback
                   if not self.is_spr(spr_id)[0]: spr_id = "GeneratedErroR" # Final fallback
              else: spr_id = "GeneratedErroR"

              if spr_id == "GeneratedErroR":
                   logger.error("Could not generate valid SPR term.")
                   return None
              else:
                   logger.warning(f"Used fallback SPR term generation: '{spr_id}'")


         # Create definition dict
         spr_def = {
              "spr_id": spr_id, # The SPR term itself
              "term": core_concept_term, # The original human-readable term
              "definition": definition,
              "category": category if isinstance(category, str) else "General",
              "relationships": relationships if isinstance(relationships, dict) else {},
              "blueprint_details": blueprint if isinstance(blueprint, str) else "",
              "metadata": {"created_by": "ConceptualSPRWriter", "timestamp": time.time()} # Example metadata
         }
         # Add SPR using the main method (default no overwrite)
         if self.add_spr(spr_def, overwrite=False):
              return spr_id
         else:
              # Add failed (e.g., already exists and overwrite=False)
              logger.warning(f"Failed to add SPR '{spr_id}'. It might already exist.")
              return None # Indicate failure


    def conceptual_decompress_spr(self, spr_id: str) -> Optional[Dict[str, Any]]:
         """Conceptual function for retrieving SPR details using its ID/term."""
         # This is essentially just getting the definition from the managed store
         return self.get_spr(spr_id)


if __name__ == "__main__":
    # Ensure logging is configured for standalone testing
    if not logging.getLogger().hasHandlers():
         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Need config for file paths
    try:
         from mastermind_ai_v2_9 import config
    except ImportError:
         class FallbackConfig:
              KNOWLEDGE_GRAPH_DIR = 'knowledge_graph'
              SPR_JSON_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, 'test_spr_definitions.json')
         config = FallbackConfig()
         print("Using fallback config for SPR Manager test.")


    print("SPR Manager loaded (ResonantiA v2.9.5)")
    # Example usage:
    # Ensure the directory exists
    if config.KNOWLEDGE_GRAPH_DIR and not os.path.exists(config.KNOWLEDGE_GRAPH_DIR):
        try:
            os.makedirs(config.KNOWLEDGE_GRAPH_DIR)
        except OSError as e:
             print(f"ERROR: Could not create knowledge graph directory: {e}")
             exit()

    test_spr_file = config.SPR_JSON_FILE
    # Create a dummy SPR file for testing if it doesn't exist
    if not os.path.exists(test_spr_file):
         try:
              with open(test_spr_file, 'w', encoding='utf-8') as f:
                   json.dump([], f)
         except IOError as e:
              print(f"ERROR: Could not create test SPR file: {e}")
              exit()

    manager = SPRManager(test_spr_file)
    print(f"Initial SPR count: {len(manager.sprs)}")

    # Example add using conceptual writer
    print("\n--- Testing Conceptual Write ---")
    new_spr_id = manager.conceptual_write_spr(
         core_concept_term="Cognitive Reflection Cycle",
         definition="The meta-cognitive process of examining the ThoughtTraiL.",
         relationships={"type": "MetaCognitiveProcess", "part_of": ["Metacognitive shifT"]},
         blueprint="Points to Section 5.3",
         category="MetaCognition"
    )
    if new_spr_id:
         print(f"Conceptually wrote SPR: {new_spr_id}")
         print(f"SPR count after add: {len(manager.sprs)}")
         retrieved = manager.conceptual_decompress_spr(new_spr_id)
         print(f"Retrieved conceptually written SPR: {json.dumps(retrieved, indent=2)}")
    else:
         print("Failed to conceptually write SPR (check logs for reason).")
    print("------------------------------")


    # Example format check
    print("\n--- Format Checks ---")
    tests = ["KnowledgE", "KNO", "normal", "A1", "MidnighT", "API", "A", "As Above So BeloW", "Test-SP R", "Guardian pointS", "WorkflowEnginE"]
    for t in tests:
         is_valid, term = manager.is_spr(t)
         print(f"Is '{t}' an SPR format? {is_valid}")
    print("---------------------\n")

    # Clean up test file (optional)
    # try:
    #      os.remove(test_spr_file)
    #      print(f"Removed test file: {test_spr_file}")
    # except OSError as e:
    #      print(f"Could not remove test file {test_spr_file}: {e}")
