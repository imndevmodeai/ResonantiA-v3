import logging
import json
import uuid
from pathlib import Path
from threading import Lock
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class SprValidationError(Exception):
    """Custom exception for SPR validation errors."""
    pass

class SprManager:
    """
    The Librarian of Alexandria for ArchE. This class provides a robust, thread-safe
    interface for managing the lifecycle of Self-Perfecting Records (SPRs) – the
    fundamental units of knowledge within the system. It handles the creation,
    retrieval, updating, and deletion of SPRs, ensuring data integrity, durability
    through atomic file writes, and rapid access via an in-memory cache.
    """

    def __init__(self, knowledge_base_path: str = "knowledge/sprs.json"):
        """
        Initializes the SPRManager.

        Args:
            knowledge_base_path (str): The file path for the persistent knowledge base.
        """
        self.kb_path = Path(knowledge_base_path)
        self._lock = Lock()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_knowledge_base()
        logger.info(f"[SprManager] Initialized. Knowledge base loaded from '{self.kb_path}'. {len(self._cache)} SPRs in cache.")

    def _load_knowledge_base(self):
        """Loads the knowledge base from the JSON file into the in-memory cache."""
        with self._lock:
            try:
                if self.kb_path.exists():
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "sprs" in data:
                            self._cache = data["sprs"]
                        else:
                            logger.warning("Knowledge base file is malformed. Starting with an empty cache.")
                else:
                    logger.info("No knowledge base file found. Starting with an empty knowledge base.")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load knowledge base: {e}", exc_info=True)

    def _persist_knowledge_base(self):
        """
        Atomically persists the current state of the in-memory cache to the JSON file.
        Uses a temporary file and rename to ensure atomicity.
        """
        with self._lock:
            try:
                self.kb_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = self.kb_path.with_suffix(f".tmp.{uuid.uuid4()}")
                
                kb_content = {
                    "metadata": {
                        "last_updated_utc": datetime.utcnow().isoformat(),
                        "spr_count": len(self._cache)
                    },
                    "sprs": self._cache
                }

                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(kb_content, f, indent=2)
                
                temp_path.rename(self.kb_path)
                logger.info(f"Knowledge base successfully persisted to {self.kb_path}")

            except (IOError, TypeError) as e:
                logger.error(f"Failed to persist knowledge base: {e}", exc_info=True)


    def create_spr(self, content: str, spr_type: str, related_sprs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Creates a new Self-Perfecting Record.

        Args:
            content (str): The core information or data of the SPR.
            spr_type (str): The type of the SPR (e.g., 'workflow_spec', 'system_axiom').
            related_sprs (List[str], optional): A list of IDs of related SPRs.

        Returns:
            The newly created SPR dictionary.
        """
        spr_id = f"spr-{uuid.uuid4()}"
        timestamp = datetime.utcnow().isoformat()
        
        new_spr = {
            "id": spr_id,
            "version": 1,
            "type": spr_type,
            "content": content,
            "metadata": {
                "created_at_utc": timestamp,
                "last_updated_utc": timestamp,
                "confidence": 0.9, # Initial confidence
                "related_sprs": related_sprs or []
            }
        }
        
        self.validate_spr(new_spr) # Validate before adding

        with self._lock:
            self._cache[spr_id] = new_spr
        
        self._persist_knowledge_base()
        logger.info(f"Created new SPR of type '{spr_type}' with ID {spr_id}.")
        return new_spr

    def get_spr(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an SPR by its ID."""
        with self._lock:
            return self._cache.get(spr_id)

    def update_spr(self, spr_id: str, new_content: str, new_confidence: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Updates an existing SPR. This creates a new version of the SPR.
        """
        with self._lock:
            if spr_id not in self._cache:
                logger.warning(f"Update failed: SPR with ID {spr_id} not found.")
                return None
            
            spr = self._cache[spr_id]
            spr['content'] = new_content
            spr['version'] += 1
            spr['metadata']['last_updated_utc'] = datetime.utcnow().isoformat()
            if new_confidence is not None:
                spr['metadata']['confidence'] = new_confidence
            
            self.validate_spr(spr)
            self._cache[spr_id] = spr
            
        self._persist_knowledge_base()
        logger.info(f"Updated SPR {spr_id} to version {spr['version']}.")
        return spr

    def delete_spr(self, spr_id: str) -> bool:
        """Deletes an SPR by its ID."""
        with self._lock:
            if spr_id not in self._cache:
                logger.warning(f"Deletion failed: SPR with ID {spr_id} not found.")
                return False
            del self._cache[spr_id]

        self._persist_knowledge_base()
        logger.info(f"Deleted SPR {spr_id}.")
        return True

    def find_sprs(self, by_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Finds SPRs based on specified criteria.

        Args:
            by_type (str, optional): Filter SPRs by their 'type' field.

        Returns:
            A list of matching SPRs.
        """
        with self._lock:
            if not by_type:
                return list(self._cache.values())
            
            return [spr for spr in self._cache.values() if spr.get('type') == by_type]

    @staticmethod
    def validate_spr(spr_data: Dict[str, Any]):
        """
        Validates the structure and content of a single SPR.
        
        Raises:
            SprValidationError: If the SPR is invalid.
        """
        required_keys = ['id', 'version', 'type', 'content', 'metadata']
        for key in required_keys:
            if key not in spr_data:
                raise SprValidationError(f"Missing required key: '{key}'")

        if not isinstance(spr_data['metadata'], dict):
            raise SprValidationError("'metadata' must be a dictionary.")
            
        if 'created_at_utc' not in spr_data['metadata']:
            raise SprValidationError("Missing 'created_at_utc' in metadata.")


# --- Test Harness ---
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    test_kb_path = "outputs/test_sprs.json"
    if Path(test_kb_path).exists():
        Path(test_kb_path).unlink()

    print("\n--- [1] Initializing SPR Manager ---")
    spr_manager = SprManager(knowledge_base_path=test_kb_path)

    print("\n--- [2] Creating new SPRs ---")
    axiom_spr = spr_manager.create_spr(
        content="System must prioritize actions that enhance human dignity.",
        spr_type="system_axiom"
    )
    spec_spr = spr_manager.create_spr(
        content="{'workflow_name': 'Test', 'tasks': []}",
        spr_type="workflow_spec",
        related_sprs=[axiom_spr['id']]
    )
    print(f"Created Axiom SPR with ID: {axiom_spr['id']}")
    print(f"Created Spec SPR with ID: {spec_spr['id']}")

    print("\n--- [3] Retrieving an SPR ---")
    retrieved_spr = spr_manager.get_spr(axiom_spr['id'])
    print(f"Retrieved content: '{retrieved_spr['content']}'")
    assert retrieved_spr['id'] == axiom_spr['id']

    print("\n--- [4] Updating an SPR ---")
    updated_spr = spr_manager.update_spr(
        spec_spr['id'],
        new_content="{'workflow_name': 'TestUpdated', 'tasks': [{'id':'t1'}]}",
        new_confidence=0.95
    )
    print(f"Updated Spec SPR to version {updated_spr['version']} with confidence {updated_spr['metadata']['confidence']:.2f}")
    assert updated_spr['version'] == 2
    assert updated_spr['metadata']['confidence'] == 0.95

    print("\n--- [5] Finding SPRs by type ---")
    axiom_sprs = spr_manager.find_sprs(by_type="system_axiom")
    print(f"Found {len(axiom_sprs)} SPR(s) of type 'system_axiom'.")
    assert len(axiom_sprs) == 1

    print("\n--- [6] Deleting an SPR ---")
    is_deleted = spr_manager.delete_spr(axiom_spr['id'])
    print(f"Deletion status for Axiom SPR: {is_deleted}")
    assert is_deleted
    assert spr_manager.get_spr(axiom_spr['id']) is None

    # Clean up test file
    if Path(test_kb_path).exists():
        Path(test_kb_path).unlink()
        print(f"\nCleaned up test knowledge base: {test_kb_path}")

if __name__ == "__main__":
    main()
