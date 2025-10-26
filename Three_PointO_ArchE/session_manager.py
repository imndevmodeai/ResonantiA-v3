"""Real session management implementation for ArchE v3.0."""
import uuid
import json
from pathlib import Path
from typing import Any, Dict, Optional
from Three_PointO_ArchE.temporal_core import now_iso

__all__ = ["SessionManager"]

class SessionManager:
    """Real session management implementation."""
    
    def __init__(self, session_id: Optional[str] = None, output_dir: str = "."):
        """Initialize session manager with unique session ID."""
        self.session_id = session_id or str(uuid.uuid4())
        self.session_data = {
            "created_at": now_iso(),
            "messages": 0,
            "iar_entries": 0,
            "state": "ACTIVE",
            "last_activity": now_iso(),
            "session_id": self.session_id
        }
        self.output_dir = Path(output_dir)
        self.persist()
    
    def persist(self) -> None:
        """Save session state to JSON file."""
        session_file = self.output_dir / f"session_{self.session_id}.json"
        session_file.write_text(json.dumps(self.session_data, indent=2))
    
    def update(self, **kwargs: Any) -> None:
        """Update session state and persist changes."""
        self.session_data.update(kwargs)
        self.session_data["last_activity"] = now_iso()
        self.persist()
    
    def status(self) -> Dict[str, Any]:
        """Get current session status."""
        return self.session_data.copy()
    
    def increment_messages(self) -> None:
        """Increment message count."""
        self.update(messages=self.session_data["messages"] + 1)
    
    def increment_iar_entries(self) -> None:
        """Increment IAR entry count."""
        self.update(iar_entries=self.session_data["iar_entries"] + 1)
    
    def set_state(self, state: str) -> None:
        """Set session state (ACTIVE, COMPLETED, ERROR, etc.)."""
        self.update(state=state)
    
    def get_session_file_path(self) -> Path:
        """Get path to session file."""
        return self.output_dir / f"session_{self.session_id}.json"
