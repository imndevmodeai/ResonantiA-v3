import json
import os
from typing import Dict, Any

class KnowledgeGraphManager:
    """
    Manages the knowledge graph, including loading, saving, and querying.
    """
    def __init__(self, spr_definitions_path: str, knowledge_tapestry_path: str):
        self.spr_definitions_path = spr_definitions_path
        self.knowledge_tapestry_path = knowledge_tapestry_path
        self.spr_definitions = self._load_json(self.spr_definitions_path)
        self.knowledge_tapestry = self._load_json(self.knowledge_tapestry_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        """Loads a JSON file."""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_spr_definition(self, spr_id: str) -> Dict[str, Any]:
        """Retrieves a specific SPR definition."""
        return self.spr_definitions.get(spr_id, {})

    def get_tapestry_node(self, node_id: str) -> Dict[str, Any]:
        """Retrieves a specific node from the knowledge tapestry."""
        return self.knowledge_tapestry.get(node_id, {}) 