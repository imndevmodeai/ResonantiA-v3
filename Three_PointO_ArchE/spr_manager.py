import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SPRManager:
    """Manages Synergistic Protocol Resonance (SPR) definitions from a JSON file."""

    def __init__(self, spr_filepath: str):
        """
        Initializes the SPRManager and loads the definitions.

        Args:
            spr_filepath: The path to the JSON file containing SPR definitions.
        """
        if not spr_filepath:
            raise ValueError("SPRManager requires a valid file path.")
        
        self.filepath = spr_filepath
        self.sprs: Dict[str, Dict[str, Any]] = {}
        self.load_sprs()

    def load_sprs(self):
        """Loads or reloads the SPR definitions from the JSON file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                spr_data = json.load(f)
            
            self.sprs = {spr['id']: spr for spr in spr_data if 'id' in spr}
            logger.info(f"Successfully loaded {len(self.sprs)} SPR definitions from {self.filepath}")
        except FileNotFoundError:
            logger.warning(f"SPR file not found at {self.filepath}. Initializing with empty definitions.")
            self.sprs = {}
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from {self.filepath}. Check file for syntax errors.")
            self.sprs = {}
        except (TypeError, KeyError) as e:
            logger.error(f"SPR data format is invalid in {self.filepath}: {e}")
            self.sprs = {}

    def get_spr_by_id(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single SPR definition by its ID.

        Args:
            spr_id: The ID of the SPR to retrieve.

        Returns:
            A dictionary containing the SPR definition, or None if not found.
        """
        return self.sprs.get(spr_id)

    def get_all_sprs(self) -> List[Dict[str, Any]]:
        """
        Retrieves all loaded SPR definitions.

        Returns:
            A list of all SPR definition dictionaries.
        """
        return list(self.sprs.values())

    def search_sprs(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches SPR definitions for a query string in the name or description.

        Args:
            query: The string to search for.

        Returns:
            A list of matching SPR definitions.
        """
        results = []
        query_lower = query.lower()
        for spr in self.sprs.values():
            name = spr.get('name', '').lower()
            description = spr.get('description', '').lower()
            if query_lower in name or query_lower in description:
                results.append(spr)
        return results
