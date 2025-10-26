from typing import Dict, Any, List

class PatternManager:
    """
    Manages patterns identified by the system, such as recurring
    sequences of actions or common data structures.
    """
    def __init__(self):
        self.patterns = []

    def add_pattern(self, pattern: Dict[str, Any]):
        """Adds a new pattern to the manager."""
        self.patterns.append(pattern)

    def get_patterns(self) -> List[Dict[str, Any]]:
        """Returns all identified patterns."""
        return self.patterns 