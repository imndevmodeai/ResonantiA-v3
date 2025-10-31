# ResonantiA Protocol v3.1 - spr_manager.py
# This file is the result of a Resonance Audit and Harmonization.
# It refactors the original data loader into a dynamic, active "Master Musician"
# as envisioned by its Living Specification (specifications/spr_manager.md),
# capable of scanning for and priming SPRs to activate the KnO.

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)

class SPRManager:
    """
    The Master Musician of the Bell Chamber (the KnO).
    It scans for cognitive keys (SPRs), activates conceptual resonance by
    retrieving their definitions, and manages the master ledger of all SPRs.
    """

    def __init__(self, spr_filepath: str):
        """
        Initializes the SPRManager, loads the master ledger of bells, and
        prepares to read the sheet music by compiling a recognition pattern.

        Args:
            spr_filepath: The path to the JSON file containing the master ledger of SPRs.
        """
        if not spr_filepath:
            raise ValueError("SPRManager requires a valid file path.")
        
        self.filepath = Path(spr_filepath).resolve()
        self.sprs: Dict[str, Dict[str, Any]] = {}
        self.spr_pattern: Optional[re.Pattern] = None
        self.load_sprs()

    def load_sprs(self):
        """
        Loads or reloads the master ledger of all bells (SPR definitions).
        After loading, it immediately recompiles the pattern for recognizing them.
        """
        try:
            if not self.filepath.exists() or self.filepath.stat().st_size == 0:
                logger.warning(f"SPR file is missing or empty at {self.filepath}. Initializing with an empty ledger.")
                self.sprs = {}
                # Attempt to create an empty file if it doesn't exist
                if not self.filepath.exists():
                    self.filepath.parent.mkdir(parents=True, exist_ok=True)
                    self.filepath.touch()
                self._compile_spr_pattern()
                return

            with open(self.filepath, 'r', encoding='utf-8') as f:
                spr_data = json.load(f)

            if isinstance(spr_data, list):
                spr_list = spr_data
            elif isinstance(spr_data, dict) and 'spr_definitions' in spr_data:
                spr_list = spr_data['spr_definitions']
            else:
                raise ValueError("SPR file must contain a list or a dict with 'spr_definitions' key.")

            temp_sprs = {}
            for spr_def in spr_list:
                spr_id = spr_def.get('spr_id') or spr_def.get('id')
                if spr_id and isinstance(spr_id, str):
                    if spr_id in temp_sprs:
                        logger.warning(f"Duplicate SPR ID '{spr_id}' found in ledger. The first occurrence will be used.")
                    else:
                        temp_sprs[spr_id] = spr_def
            self.sprs = temp_sprs

            if not self.sprs:
                logger.warning(f"No valid SPR definitions were loaded from {self.filepath}.")
            else:
                logger.info(f"Successfully loaded {len(self.sprs)} bells (SPR definitions) from the master ledger.")
            
            self._compile_spr_pattern()

        except Exception as e:
            logger.error(f"CRITICAL ERROR: Could not load the master ledger of SPRs from {self.filepath}. The Bell Chamber is silent. Error: {e}", exc_info=True)
            self.sprs = {}
            self._compile_spr_pattern() # Compile with empty set to avoid errors

    def _compile_spr_pattern(self):
        """
        The musician studies the entire collection of bells to create a single,
        powerful mental filter (regex) to instantly recognize any of them in a
        piece of music, respecting the Guardian Points format.
        """
        if not self.sprs:
            self.spr_pattern = None
            logger.warning("No SPRs loaded, the musician has no music to recognize.")
            return

        spr_keys = [re.escape(key) for key in self.sprs.keys()]
        # The pattern looks for whole words (\b) that exactly match one of the SPR keys.
        pattern_str = r'\b(' + '|'.join(spr_keys) + r')\b'
        try:
            self.spr_pattern = re.compile(pattern_str)
            logger.info(f"The musician is now attuned to recognize {len(spr_keys)} unique SPRs.")
        except re.error as e:
            logger.error(f"Failed to compile SPR recognition pattern. The musician is deaf to the music. Error: {e}")
            self.spr_pattern = None

    def scan_and_prime(self, text: str) -> List[Dict[str, Any]]:
        """
        The musician reads the sheet music (text) and strikes the resonant bells (SPRs).
        This activates the concepts, returning the full definitions of all unique SPRs found.

        Args:
            text: The input text (the sheet music) to be scanned.

        Returns:
            A list of the full dictionary definitions for each unique SPR found.
        """
        if not self.spr_pattern or not isinstance(text, str):
            return []

        found_sprs: Set[str] = set(self.spr_pattern.findall(text))
        
        activated_concepts = []
        if found_sprs:
            logger.debug(f"The musician recognized the following SPRs: {sorted(list(found_sprs))}")
            for spr_key in sorted(list(found_sprs)): # Sort for deterministic order
                if spr_key in self.sprs:
                    # Retrieve the full definition to activate the concept
                    activated_concepts.append(self.sprs[spr_key])
            logger.info(f"Primed {len(activated_concepts)} concepts from the provided text.")
        
        return activated_concepts

    def add_spr(self, spr_definition: Dict[str, Any], save_to_file: bool = True) -> bool:
        """
        The bell-founder (InsightSolidificatioN) gives a new, perfectly-tuned bell
        to the musician, who adds it to the chamber and updates the master ledger.

        Args:
            spr_definition: A dictionary for the new SPR. Must contain 'spr_id'.
            save_to_file: If True, saves the entire ledger back to the file system.

        Returns:
            True if the SPR was successfully added, False otherwise.
        """
        spr_id = spr_definition.get('spr_id')
        if not spr_id or not isinstance(spr_id, str):
            logger.error("The new bell has no name (missing 'spr_id'). It cannot be added to the chamber.")
            return False
        
        if spr_id in self.sprs:
            logger.warning(f"A bell named '{spr_id}' already exists. The old bell will be replaced with the new one.")

        self.sprs[spr_id] = spr_definition
        logger.info(f"New bell '{spr_id}' has been added to the chamber.")
        
        # The musician updates their mental filter to include the new bell.
        self._compile_spr_pattern()

        if save_to_file:
            self._save_ledger()
            
        return True

    def _save_ledger(self):
        """Saves the current state of the master ledger to the JSON file."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            spr_list = list(self.sprs.values())
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(spr_list, f, indent=4)
            logger.info(f"The master ledger at {self.filepath} has been updated.")
        except Exception as e:
            logger.error(f"The musician failed to update the master ledger. Error: {e}", exc_info=True)

    def get_spr_by_id(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single SPR definition by its ID."""
        return self.sprs.get(spr_id)

    def get_all_sprs(self) -> List[Dict[str, Any]]:
        """Retrieves all loaded SPR definitions."""
        return list(self.sprs.values())
