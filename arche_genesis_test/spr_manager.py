
# -*- coding: utf-8 -*-
"""
spr_manager.py

This module defines the SPRManager, a core component of the ResonantiA Protocol.
It is responsible for managing, identifying, and activating Sparse Priming
Representations (SPRs) within text, forming the bridge between language and
conceptual understanding in the Knowledge Network Oneness (KnO).
"""

import json
import os
import re
from typing import Any, Dict, List, Pattern

# This module is a direct implementation of the 'Sparse priming representationS' SPR.


class SPRManagerError(Exception):
    """Custom exception class for errors specific to the SPRManager."""
    pass


class SPRManager:
    """
    Manages the lifecycle of Sparse Priming Representations (SPRs).

    This class loads a dictionary of SPRs from a JSON file, provides methods
    to scan text for these SPRs, and allows for the dynamic addition of new
    SPRs. It is the primary mechanism for activating conceptual nodes within
    the system's cognitive architecture.

    Attributes:
        spr_filepath (str): The path to the JSON file containing SPR definitions.
        spr_definitions (Dict[str, Dict[str, Any]]): The loaded SPRs.
        spr_pattern (re.Pattern): A compiled regex for efficient scanning.
    """

    def __init__(self, spr_filepath: str):
        """
        Initializes the SPRManager instance.

        Args:
            spr_filepath (str): The path to the SPR definitions JSON file.

        Raises:
            FileNotFoundError: If the specified spr_filepath does not exist.
            SPRManagerError: If the file cannot be loaded or parsed.
        """
        if not os.path.exists(spr_filepath):
            raise FileNotFoundError(
                f"SPR definition file not found at: {spr_filepath}"
            )
        self.spr_filepath = spr_filepath
        self.spr_definitions: Dict[str, Dict[str, Any]] = self._load_spr_definitions()
        # This function is primed by the 'Implementation resonancE' SPR.
        self.spr_pattern: Pattern = self._compile_spr_pattern()

    def _load_spr_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Loads SPR definitions from the JSON file specified at initialization.

        Accepts multiple canonical formats and normalizes them to a single
        in-memory mapping of { spr_key: definition_dict } where spr_key follows
        the Guardian pointS format.

        Supported on-disk formats:
        - List[Dict]: each entry has at least 'spr_id' or 'term'
        - Dict with key 'spr_definitions': List[Dict]
        - Dict mapping { spr_key: definition }

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary of SPR definitions.

        Raises:
            SPRManagerError: If the file is not valid JSON or cannot be read.
        """
        try:
            with open(self.spr_filepath, 'r', encoding='utf-8') as f:
                raw = json.load(f)
        except json.JSONDecodeError as e:
            raise SPRManagerError(
                f"Error decoding JSON from {self.spr_filepath}: {e}"
            ) from e
        except IOError as e:
            raise SPRManagerError(
                f"Could not read SPR file {self.spr_filepath}: {e}"
            ) from e

        # Normalize formats
        if isinstance(raw, dict):
            # Legacy wrapper: { "spr_definitions": [ ... ] }
            if 'spr_definitions' in raw and isinstance(raw['spr_definitions'], list):
                entries = raw['spr_definitions']
            else:
                # Already a mapping { spr_key: def }
                self._build_alias_index_from_mapping(raw)
                return raw
        elif isinstance(raw, list):
            entries = raw
        else:
            raise SPRManagerError(
                f"Unsupported SPR JSON structure in {self.spr_filepath}: {type(raw)}"
            )

        # Convert list-of-entries → mapping, build alias index
        mapping: Dict[str, Dict[str, Any]] = {}
        alias_to_id: Dict[str, str] = {}

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            spr_key = entry.get('spr_id') or entry.get('sprId')
            term = entry.get('term')

            # Fallback: derive key from term if needed
            if not spr_key and term:
                spr_key = term.replace(' ', '')

            if not spr_key:
                # Skip entries without resolvable key
                continue

            # Ensure the term is preserved inside the definition
            definition_dict = {k: v for k, v in entry.items() if k != 'spr_id'}
            # Keep term inside definition for downstream consumers
            if term and 'term' not in definition_dict:
                definition_dict['term'] = term

            mapping[spr_key] = definition_dict

            # Build alias index for robust activation by term
            if term:
                alias_to_id[term.strip().lower()] = spr_key

        self._alias_to_id = alias_to_id
        return mapping

    def _compile_spr_pattern(self) -> Pattern:
        """
        Compiles a single regex pattern to find all known SPRs in a text.

        The pattern is dynamically generated from the keys of the loaded
        `spr_definitions`. It is designed to match whole words/phrases only.

        Returns:
            re.Pattern: A compiled regular expression object.
        """
        if not self.spr_definitions:
            # Return a pattern that will never match if there are no SPRs.
            return re.compile(r'(?!)')

        # Escape keys and known terms to handle special characters and match more robustly.
        keys = set(self.spr_definitions.keys())

        # Include human-readable terms as alternates
        for spr_key, definition in self.spr_definitions.items():
            term = None
            if isinstance(definition, dict):
                term = definition.get('term')
            if isinstance(term, str) and term:
                keys.add(term)

        escaped = [re.escape(k) for k in keys if isinstance(k, str) and k.strip()]
        if not escaped:
            return re.compile(r'(?!)')

        # Use word boundaries where possible; allow internal spaces
        pattern_str = r'\b(' + '|'.join(sorted(escaped, key=len, reverse=True)) + r')\b'
        return re.compile(pattern_str)

    def _build_alias_index_from_mapping(self, mapping: Dict[str, Dict[str, Any]]) -> None:
        """Build a lowercase alias → spr_key index from a mapping structure."""
        alias_to_id: Dict[str, str] = {}
        for spr_key, definition in mapping.items():
            if isinstance(definition, dict):
                term = definition.get('term')
                if isinstance(term, str) and term:
                    alias_to_id[term.strip().lower()] = spr_key
        self._alias_to_id = alias_to_id

    def resolve_spr_key(self, key_or_term: str) -> str | None:
        """
        Resolve an input string that could be a canonical spr_key or a human term
        into a canonical spr_key present in the current definitions.
        """
        if not key_or_term:
            return None
        if key_or_term in self.spr_definitions:
            return key_or_term
        alias = getattr(self, '_alias_to_id', {})
        return alias.get(key_or_term.strip().lower())

    def scan_and_prime(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans input text for known SPRs and returns their full definitions.

        This function is the core of conceptual activation. It finds all
        occurrences of registered SPRs in the given text and returns a list
        of the corresponding concept definitions.

        # This function enables 'Cognitive UnfoldinG' and 'Contextual UnderstandinG'.
        # It is used by the 'Core workflow enginE' and 'RISE'.

        Args:
            text (str): The input text to scan for SPRs.

        Returns:
            List[Dict[str, Any]]: A list of definition dictionaries for each
                                  unique SPR found in the text.
        """
        try:
            found_labels = self.spr_pattern.findall(text)

            activated_concepts: List[Dict[str, Any]] = []
            seen: set[str] = set()

            for label in set(found_labels):
                spr_key = self.resolve_spr_key(label) or label
                if spr_key in seen:
                    continue
                definition = self.spr_definitions.get(spr_key)
                if definition is None and label in self.spr_definitions:
                    definition = self.spr_definitions[label]
                    spr_key = label
                if definition is None:
                    continue

                bundle = self._build_activation_bundle(spr_key, definition)
                activated_concepts.append(bundle)
                seen.add(spr_key)

            return activated_concepts
        except Exception as e:
            # In a production system, this would be logged extensively.
            raise SPRManagerError(
                f"An unexpected error occurred during scan_and_prime: {e}"
            ) from e

    def _build_activation_bundle(self, spr_key: str, definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct a Cognitive Activation Bundle (CAB) for a single SPR.

        The bundle is a minimal, high-signal structure intended to trigger a
        'crescendo of understanding' elsewhere in the system. It consolidates:
        - canonical key and term
        - definition, category, metadata
        - relationships with resolved related spr_keys (where possible)
        - blueprint_details (code/workflow anchors)

        Returns a dictionary safe to inject into workflow context or other engines.
        """
        term = None
        if isinstance(definition, dict):
            term = definition.get('term')

        relationships = definition.get('relationships') if isinstance(definition, dict) else None
        resolved_links: Dict[str, list[str]] = {}
        if isinstance(relationships, dict):
            for rel_key, rel_val in relationships.items():
                if isinstance(rel_val, list):
                    resolved: list[str] = []
                    for label in rel_val:
                        if isinstance(label, str):
                            rk = self.resolve_spr_key(label) or label
                            resolved.append(rk)
                    resolved_links[rel_key] = resolved

        bundle: Dict[str, Any] = {
            'spr_key': spr_key,
            'term': term,
            'definition': definition.get('definition') if isinstance(definition, dict) else None,
            'category': definition.get('category') if isinstance(definition, dict) else None,
            'metadata': definition.get('metadata') if isinstance(definition, dict) else None,
            'relationships': resolved_links if resolved_links else relationships,
            'blueprint_details': definition.get('blueprint_details') if isinstance(definition, dict) else None,
        }

        # Compact None fields
        return {k: v for k, v in bundle.items() if v is not None}

    @staticmethod
    def _is_valid_spr_format(spr_key: str) -> bool:
        """
        Validates if a key conforms to the 'Guardian pointS' format.

        The format requires a non-empty string where the first word starts
        with a capital letter and the last word ends with a capital letter.

        Args:
            spr_key (str): The SPR key to validate.

        Returns:
            bool: True if the key is valid, False otherwise.
        """
        if not isinstance(spr_key, str) or not spr_key.strip():
            return False

        words = spr_key.split()
        if not words:
            return False

        # Check first word's first character
        if not words[0][0].isupper():
            return False

        # Check last word's last character
        if not words[-1][-1].isupper():
            return False

        return True

    def add_spr(self, spr_key: str, definition: Dict[str, Any], overwrite: bool = False) -> None:
        """
        Adds a new SPR to the definitions and persists the change to the file.

        This function acts as the registration step for newly formed concepts,
        making them available for future cognitive activation.

        # This function is a key part of the 'InsightSolidificatioN' process.

        Args:
            spr_key (str): The new SPR key (e.g., "New concepT").
            definition (Dict[str, Any]): The definition dictionary for the SPR.
            overwrite (bool): If True, allows overwriting an existing SPR.
                              Defaults to False.

        Raises:
            ValueError: If the spr_key is in an invalid format or already
                        exists and overwrite is False.
            TypeError: If the provided definition is not a dictionary.
            SPRManagerError: If saving the updated definitions to file fails.
        """
        if not self._is_valid_spr_format(spr_key):
            raise ValueError(
                f"Invalid SPR key format for '{spr_key}'. "
                "Must follow 'Guardian pointS' format."
            )

        if spr_key in self.spr_definitions and not overwrite:
            raise ValueError(
                f"SPR key '{spr_key}' already exists. Set overwrite=True to replace it."
            )

        if not isinstance(definition, dict):
            raise TypeError("SPR definition must be a dictionary.")

        # 1. Update the in-memory dictionary
        self.spr_definitions[spr_key] = definition

        # 2. Save the updated definitions back to the file atomically
        temp_filepath = self.spr_filepath + ".tmp"
        try:
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.spr_definitions, f, indent=4, ensure_ascii=False)
            # Atomic move operation
            os.replace(temp_filepath, self.spr_filepath)
        except (IOError, OSError) as e:
            # If saving fails, revert the in-memory change to maintain consistency.
            # A more robust system might use a transactional approach.
            del self.spr_definitions[spr_key]
            raise SPRManagerError(
                f"Failed to save updated SPR definitions to {self.spr_filepath}: {e}"
            ) from e
        finally:
            # Ensure the temporary file is removed in case of an error during replace
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

        # 3. Re-compile the regex pattern to include the new SPR
        self.spr_pattern = self._compile_spr_pattern()

    def get_spr_definition(self, spr_key: str) -> Dict[str, Any] | None:
        """
        Retrieves the definition for a single SPR key.

        Args:
            spr_key (str): The exact SPR key to look up.

        Returns:
            A dictionary containing the SPR's definition if found, else None.
        """
        # Return a copy to prevent external modification of the internal state.
        return self.spr_definitions.get(spr_key, None)

