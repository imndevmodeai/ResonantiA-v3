"""
Session Auto-Capture System
============================

Automatically captures and exports conversation sessions to markdown files,
integrating with the existing session_manager.py and ThoughtTrail system.

This closes the gap between manual cursor_*.md file creation and automated
session persistence.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now_iso

logger = logging.getLogger(__name__)

class SessionAutoCapture:
    """
    Automatically captures conversation sessions and exports them to markdown.
    
    Integrates with:
    - session_manager.py for session tracking
    - thought_trail.py for IAR entries
    - Autopoietic learning loop for pattern detection
    """
    
    def __init__(self, 
                 output_dir: str = ".",
                 session_manager=None,
                 thought_trail=None):
        """
        Initialize the auto-capture system.
        
        Args:
            output_dir: Directory to save captured sessions
            session_manager: Existing SessionManager instance
            thought_trail: Existing ThoughtTrail instance
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_manager = session_manager
        self.thought_trail = thought_trail
        self.current_session_data = {
            "messages": [],
            "iar_entries": [],
            "sprs_primed": [],
            "insights_detected": []
        }
        
        logger.info(f"SessionAutoCapture initialized, output to: {self.output_dir}")
    
    def capture_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Capture a single message in the conversation.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (timestamp, confidence, etc.)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": now_iso(),
            "metadata": metadata or {}
        }
        
        self.current_session_data["messages"].append(message)
        logger.debug(f"Captured {role} message ({len(content)} chars)")
    
    def capture_iar_entry(self, iar_entry: Dict[str, Any]):
        """
        Capture an IAR entry from ThoughtTrail.
        
        Args:
            iar_entry: IAR entry dictionary
        """
        self.current_session_data["iar_entries"].append(iar_entry)
        logger.debug(f"Captured IAR entry: {iar_entry.get('task_id', 'unknown')}")
    
    def capture_spr_priming(self, sprs: List[Dict[str, Any]]):
        """
        Capture SPRs that were primed during the session.
        
        Args:
            sprs: List of primed SPR dictionaries
        """
        self.current_session_data["sprs_primed"].extend(sprs)
        logger.debug(f"Captured {len(sprs)} primed SPRs")
    
    def capture_insight(self, insight: Dict[str, Any]):
        """
        Capture an insight detected by the learning loop.
        
        Args:
            insight: Insight dictionary
        """
        self.current_session_data["insights_detected"].append(insight)
        logger.debug(f"Captured insight: {insight.get('core_concept', 'unknown')}")
    
    def export_session(self, session_id: str = None, topic: str = None) -> Path:
        """
        Export the current session to a markdown file.
        
        Args:
            session_id: Optional session identifier
            topic: Optional topic/title for the session
            
        Returns:
            Path to the exported markdown file
        """
        timestamp = datetime.now().strftime("%m.%d.%y")
        
        # Generate filename following existing pattern
        if topic:
            safe_topic = topic.lower().replace(" ", "_")[:50]
            filename = f"cursor_{safe_topic}.{timestamp}.md"
        else:
            filename = f"cursor_session_{session_id or 'unknown'}.{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        # Generate markdown content
        content = self._generate_markdown()
        
        # Write to file
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Session exported to: {filepath}")
        
        return filepath
    
    def _generate_markdown(self) -> str:
        """
        Generate markdown content from captured session data.
        
        Returns:
            Markdown formatted string
        """
        lines = []
        
        # Header
        lines.append(f"# ArchE Session Capture")
        lines.append(f"_Auto-exported on {now_iso()} from ArchE SessionAutoCapture_")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Session Summary
        lines.append("## Session Summary")
        lines.append("")
        lines.append(f"- **Messages**: {len(self.current_session_data['messages'])}")
        lines.append(f"- **IAR Entries**: {len(self.current_session_data['iar_entries'])}")
        lines.append(f"- **SPRs Primed**: {len(self.current_session_data['sprs_primed'])}")
        lines.append(f"- **Insights Detected**: {len(self.current_session_data['insights_detected'])}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Conversation
        lines.append("## Conversation")
        lines.append("")
        
        for msg in self.current_session_data["messages"]:
            role = msg["role"].title()
            content = msg["content"]
            
            lines.append(f"**{role}**")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # SPRs Primed
        if self.current_session_data["sprs_primed"]:
            lines.append("## SPRs Activated During Session")
            lines.append("")
            
            unique_sprs = {}
            for spr in self.current_session_data["sprs_primed"]:
                spr_id = spr.get("spr_id", "unknown")
                if spr_id not in unique_sprs:
                    unique_sprs[spr_id] = spr
            
            for spr_id, spr_data in unique_sprs.items():
                lines.append(f"### `{spr_id}`")
                definition = spr_data.get("definition", "No definition available")
                lines.append(f"{definition}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # IAR Entries
        if self.current_session_data["iar_entries"]:
            lines.append("## IAR Reflection Log")
            lines.append("")
            
            for iar in self.current_session_data["iar_entries"]:
                task_id = iar.get("task_id", "unknown")
                action = iar.get("action_type", "unknown")
                confidence = iar.get("confidence", 0.0)
                
                lines.append(f"### Action: `{action}` (ID: {task_id})")
                lines.append(f"**Confidence**: {confidence:.2f}")
                lines.append("")
                
                iar_dict = iar.get("iar", {})
                if iar_dict:
                    lines.append(f"**Intention**: {iar_dict.get('intention', 'N/A')}")
                    lines.append(f"**Action**: {iar_dict.get('action', 'N/A')}")
                    lines.append(f"**Reflection**: {iar_dict.get('reflection', 'N/A')}")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Insights
        if self.current_session_data["insights_detected"]:
            lines.append("## Insights Detected by Autopoietic Learning Loop")
            lines.append("")
            
            for insight in self.current_session_data["insights_detected"]:
                concept = insight.get("core_concept", "Unknown Concept")
                confidence = insight.get("confidence", 0.0)
                
                lines.append(f"### Insight: {concept}")
                lines.append(f"**Confidence**: {confidence:.2f}")
                lines.append("")
                lines.append(insight.get("supporting_details", "No details available"))
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Footer
        lines.append("## Session Metadata")
        lines.append("")
        lines.append("```json")
        metadata = {
            "exported_at": now_iso(),
            "message_count": len(self.current_session_data["messages"]),
            "iar_count": len(self.current_session_data["iar_entries"]),
            "spr_count": len(set(s.get("spr_id") for s in self.current_session_data["sprs_primed"])),
            "insight_count": len(self.current_session_data["insights_detected"])
        }
        lines.append(json.dumps(metadata, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*This session was automatically captured and exported by ArchE SessionAutoCapture system.*")
        
        return "\n".join(lines)
    
    def reset_session(self):
        """Reset session data for a new session."""
        self.current_session_data = {
            "messages": [],
            "iar_entries": [],
            "sprs_primed": [],
            "insights_detected": []
        }
        logger.info("Session data reset for new session")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session data.
        
        Returns:
            Dictionary with session statistics
        """
        return {
            "message_count": len(self.current_session_data["messages"]),
            "iar_count": len(self.current_session_data["iar_entries"]),
            "unique_sprs": len(set(s.get("spr_id") for s in self.current_session_data["sprs_primed"])),
            "insight_count": len(self.current_session_data["insights_detected"]),
            "last_activity": now_iso()
        }

