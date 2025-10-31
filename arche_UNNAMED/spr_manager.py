"""
SPR Manager - ResonantiA Protocol v3.5-GP
Manages Sparse Priming Representations (SPRs) for internal cognitive activation.
SPRs use Guardian pointS format: First/last uppercase alphanumeric, middle lowercase/space.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import copy

logger = logging.getLogger(__name__)


class SPRManager:
    """
    Manages the Knowledge Tapestry - the SPR definitions that trigger
    internal cognitive activation within ArchE's KnO (Knowledge Network Oneness).
    
    SPRs are NOT simple lookups; they trigger internal cognitive unfolding.
    This manager handles persistence and querying of SPR definitions.
    """
    
    def __init__(self, spr_file_path: Optional[str] = None):
        """
        Initialize SPRManager.
        
        Args:
            spr_file_path: Path to spr_definitions_tv.json. 
                          Defaults to knowledge_graph/spr_definitions_tv.json
                          relative to project root or current working directory.
        """
        if spr_file_path is None:
            # Try common locations
            possible_paths = [
                Path("knowledge_graph/spr_definitions_tv.json"),
                Path("../knowledge_graph/spr_definitions_tv.json"),
                Path("../../knowledge_graph/spr_definitions_tv.json"),
            ]
            for p in possible_paths:
                if p.exists():
                    spr_file_path = str(p.resolve())
                    break
            if spr_file_path is None:
                # Default fallback
                spr_file_path = "knowledge_graph/spr_definitions_tv.json"
        
        self.spr_file_path = Path(spr_file_path)
        self.sprs: Dict[str, Dict[str, Any]] = {}  # spr_id -> SPR definition dict
        self._load_sprs()
    
    def _load_sprs(self):
        """Load SPR definitions from JSON file."""
        if not self.spr_file_path.exists():
            logger.warning(f"SPR file not found: {self.spr_file_path}. Initializing empty store.")
            self.sprs = {}
            return
        
        try:
            with open(self.spr_file_path, 'r', encoding='utf-8') as f:
                spr_list = json.load(f)
            
            if not isinstance(spr_list, list):
                logger.error(f"SPR file {self.spr_file_path} does not contain a JSON array. Loading failed.")
                self.sprs = {}
                return
            
            loaded_count = 0
            invalid_count = 0
            duplicate_count = 0
            
            for idx, spr_def in enumerate(spr_list):
                if not isinstance(spr_def, dict):
                    logger.warning(f"Item at index {idx} in SPR file is not a dictionary. Skipping.")
                    invalid_count += 1
                    continue
                
                spr_id = spr_def.get("spr_id")
                if not spr_id or not isinstance(spr_id, str):
                    logger.warning(f"Missing or invalid spr_id at index {idx}. Skipping.")
                    invalid_count += 1
                    continue
                
                # Validate SPR format (Guardian pointS)
                is_valid, _ = self.is_spr_format(spr_id)
                if not is_valid:
                    logger.warning(f"SPR ID '{spr_id}' at index {idx} does not match Guardian pointS format. Skipping.")
                    invalid_count += 1
                    continue
                
                if spr_id in self.sprs:
                    logger.warning(f"Duplicate SPR ID '{spr_id}' at index {idx}. Keeping first occurrence.")
                    duplicate_count += 1
                else:
                    self.sprs[spr_id] = spr_def
                    loaded_count += 1
            
            log_msg = f"Loaded {loaded_count} SPRs from {self.spr_file_path}"
            if duplicate_count > 0:
                log_msg += f". Skipped {duplicate_count} duplicates."
            if invalid_count > 0:
                log_msg += f". Skipped {invalid_count} invalid entries."
            logger.info(log_msg)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from SPR file {self.spr_file_path}: {e}")
            self.sprs = {}
        except IOError as e:
            logger.error(f"Error reading SPR file {self.spr_file_path}: {e}")
            self.sprs = {}
        except Exception as e:
            logger.error(f"Unexpected error loading SPRs: {e}", exc_info=True)
            self.sprs = {}
    
    def save_sprs(self):
        """Save current SPR definitions back to JSON file."""
        try:
            spr_list = list(self.sprs.values())
            
            # Ensure directory exists
            self.spr_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.spr_file_path, 'w', encoding='utf-8') as f:
                json.dump(spr_list, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Saved {len(self.sprs)} SPRs to {self.spr_file_path}")
            
        except IOError as e:
            logger.error(f"Error writing SPR file {self.spr_file_path}: {e}")
            raise
        except TypeError as e:
            logger.error(f"Error serializing SPR data to JSON: {e}. Check for non-serializable objects.")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving SPRs: {e}", exc_info=True)
            raise
    
    def get_spr(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an SPR definition by its ID.
        
        Args:
            spr_id: The SPR identifier in Guardian pointS format.
        
        Returns:
            SPR definition dictionary, or None if not found.
        """
        if not isinstance(spr_id, str):
            return None
        
        spr_data = self.sprs.get(spr_id)
        if spr_data:
            logger.debug(f"Retrieved SPR: {spr_id}")
        else:
            logger.debug(f"SPR not found: {spr_id}")
        
        return spr_data
    
    def find_sprs_by_term(self, term: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Find SPRs matching a given term.
        
        Args:
            term: Search term (matches 'term' field or 'spr_id').
            case_sensitive: Whether to perform case-sensitive matching.
        
        Returns:
            List of matching SPR definitions.
        """
        if not isinstance(term, str):
            return []
        
        matches = []
        search_term = term if case_sensitive else term.lower()
        
        for spr_id, spr_data in self.sprs.items():
            # Check 'term' field
            spr_term = spr_data.get("term", "")
            if case_sensitive:
                if term in spr_term or term == spr_id:
                    matches.append(spr_data)
            else:
                if search_term in spr_term.lower() or search_term == spr_id.lower():
                    matches.append(spr_data)
        
        logger.debug(f"Found {len(matches)} SPRs matching term '{term}'")
        return matches
    
    def find_sprs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Find all SPRs in a given category."""
        matches = [spr for spr in self.sprs.values() if spr.get("category") == category]
        logger.debug(f"Found {len(matches)} SPRs in category '{category}'")
        return matches
    
    def get_related_sprs(self, spr_id: str, relation_type: Optional[str] = None) -> List[str]:
        """
        Get related SPR IDs based on relationships.
        
        Args:
            spr_id: The source SPR ID.
            relation_type: Optional filter for relationship type (e.g., 'enables', 'part_of').
        
        Returns:
            List of related SPR IDs.
        """
        spr_def = self.get_spr(spr_id)
        if not spr_def:
            return []
        
        relationships = spr_def.get("relationships", {})
        if not isinstance(relationships, dict):
            return []
        
        related_ids = []
        for key, value in relationships.items():
            if relation_type is None or key == relation_type:
                if isinstance(value, list):
                    related_ids.extend([v for v in value if isinstance(v, str)])
                elif isinstance(value, str):
                    related_ids.append(value)
        
        # Deduplicate while preserving order
        seen = set()
        unique_related = []
        for rid in related_ids:
            if rid not in seen and rid in self.sprs:
                seen.add(rid)
                unique_related.append(rid)
        
        logger.debug(f"Found {len(unique_related)} related SPRs for '{spr_id}' (relation_type={relation_type})")
        return unique_related
    
    def add_spr(self, spr_definition: Dict[str, Any], overwrite: bool = False) -> bool:
        """
        Add or update an SPR definition.
        
        Args:
            spr_definition: Dictionary containing SPR definition with 'spr_id' key.
            overwrite: If True, overwrite existing SPR with same ID.
        
        Returns:
            True if added/updated successfully, False otherwise.
        """
        if not isinstance(spr_definition, dict):
            logger.error("SPR definition must be a dictionary.")
            return False
        
        spr_id = spr_definition.get("spr_id")
        if not spr_id or not isinstance(spr_id, str):
            logger.error("Cannot add SPR definition without a valid string 'spr_id'.")
            return False
        
        # Validate format
        is_valid, _ = self.is_spr_format(spr_id)
        if not is_valid:
            logger.error(f"Provided spr_id '{spr_id}' does not match required Guardian pointS format.")
            return False
        
        # Check for existing SPR
        if spr_id in self.sprs and not overwrite:
            logger.warning(f"SPR with ID '{spr_id}' already exists. Use overwrite=True to replace.")
            return False
        
        # Validate required fields
        if not spr_definition.get("definition"):
            logger.error(f"SPR definition for '{spr_id}' missing required 'definition' field.")
            return False
        
        # Ensure 'term' field exists (default to spr_id if missing)
        if "term" not in spr_definition:
            spr_definition["term"] = spr_id
        
        # Ensure relationships is a dict
        if "relationships" in spr_definition and not isinstance(spr_definition["relationships"], dict):
            logger.warning(f"Relationships for SPR '{spr_id}' is not a dict. Resetting to empty dict.")
            spr_definition["relationships"] = {}
        
        action = "Updated" if spr_id in self.sprs and overwrite else "Added"
        self.sprs[spr_id] = copy.deepcopy(spr_definition)
        logger.info(f"{action} SPR: {spr_id}")
        
        self.save_sprs()
        return True
    
    def is_spr_format(self, text: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Check if a string matches the Guardian pointS SPR format.
        
        Format Rules:
        - Starts with uppercase letter or digit
        - Ends with uppercase letter or digit
        - Middle characters are lowercase letters, digits, or spaces
        - Length >= 2
        - NOT all-caps strings > 3 characters (excludes acronyms like "NASA")
        
        Args:
            text: String to validate.
        
        Returns:
            Tuple of (is_valid: bool, normalized_spr: Optional[str])
        """
        if not text or not isinstance(text, str):
            return False, None
        
        if len(text) < 2:
            return False, None
        
        # Check first and last characters
        first_char = text[0]
        last_char = text[-1]
        
        is_first_guardian = first_char.isupper() or first_char.isdigit()
        is_last_guardian = last_char.isupper() or last_char.isdigit()
        
        # Check middle part (all lowercase or space)
        middle_part = text[1:-1]
        is_middle_valid = all(c.islower() or c.isdigit() or c.isspace() for c in middle_part) or not middle_part
        
        # Exclude all-caps acronyms (unless very short)
        is_all_caps = text.isupper()
        exclude_all_caps = is_all_caps and len(text) > 3
        
        is_match = is_first_guardian and is_last_guardian and is_middle_valid and not exclude_all_caps
        
        return is_match, text if is_match else None
    
    def extract_sprs_from_text(self, text: str) -> List[str]:
        """
        Extract potential SPR identifiers from text using pattern matching.
        
        Args:
            text: Text to scan for SPR patterns.
        
        Returns:
            List of potential SPR IDs found in text.
        """
        if not isinstance(text, str):
            return []
        
        # Pattern: Word boundaries, followed by uppercase/digit, then lowercase/spaces, then uppercase/digit
        # Matches patterns like "KnowledgE", "WorkflowEnginE", "CognitivE resonancE"
        pattern = r'\b([A-Z0-9][a-z0-9\s]*[A-Z0-9])\b'
        
        matches = re.findall(pattern, text)
        found_sprs = []
        
        for match in matches:
            # Clean up match (remove extra whitespace)
            cleaned = re.sub(r'\s+', ' ', match.strip())
            is_valid, normalized = self.is_spr_format(cleaned)
            if is_valid and normalized and normalized in self.sprs:
                found_sprs.append(normalized)
        
        # Deduplicate
        return list(dict.fromkeys(found_sprs))
    
    def get_all_sprs(self) -> List[Dict[str, Any]]:
        """Return all SPR definitions as a list."""
        return list(self.sprs.values())
    
    def get_spr_count(self) -> int:
        """Return the total number of loaded SPRs."""
        return len(self.sprs)
    
    def search_sprs(self, query: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search SPRs by text query across multiple fields.
        
        Args:
            query: Search query string.
            search_fields: Fields to search (default: ['spr_id', 'term', 'definition', 'category']).
        
        Returns:
            List of matching SPR definitions.
        """
        if not query or not isinstance(query, str):
            return []
        
        if search_fields is None:
            search_fields = ['spr_id', 'term', 'definition', 'category']
        
        query_lower = query.lower()
        matches = []
        
        for spr_id, spr_data in self.sprs.items():
            for field in search_fields:
                field_value = spr_data.get(field, "")
                if isinstance(field_value, str) and query_lower in field_value.lower():
                    matches.append(spr_data)
                    break  # Only add once per SPR
        
        logger.debug(f"Search query '{query}' found {len(matches)} matching SPRs")
        return matches
