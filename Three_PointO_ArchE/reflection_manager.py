from typing import Dict, Any

class ReflectionManager:
    """
    Manages the IAR (Integrated Action Reflection) reflections generated by tools.
    """
    def __init__(self):
        self.reflections = []

    def add_reflection(self, reflection: Dict[str, Any]):
        """Adds a new reflection to the manager."""
        self.reflections.append(reflection)

    def get_reflections(self) -> list:
        """Returns all reflections."""
        return self.reflections 