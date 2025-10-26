from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Literal
import uuid
import time
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
import json

# --- Type Definitions for Schema ---

# General Types
SenderType = Literal["user", "arche"]
StatusType = Literal["ok", "warn", "error"]
SeverityType = Literal["info", "success", "warn", "error"]

# Message Types
MessageType = Literal[
    "chat", "iar", "spr", "temporal", "meta", "complex", "implementation",
    "protocol_init", "error"
]

# VCD Event Types
VcdEventType = Literal[
    "WorkflowStart", "TaskEvaluation", "TaskExecution", "TaskSuccess", "TaskFailure",
    "WorkflowSuccess", "WorkflowFailure", "ThoughtTrail", "IAR", "SPR", "Temporal",
    "Meta", "Complex", "Implementation"
]

# --- Dataclass Schemas ---

@dataclass
class IARSchema:
    status: StatusType
    confidence: float

@dataclass
class SPRActivationSchema:
    spr_id: str
    confidence: float

@dataclass
class TemporalContextSchema:
    timeframe: str
    forecasts: Dict[str, Any]

@dataclass
class MetaCognitiveStateSchema:
    sirc_active: bool
    shift_active: bool

@dataclass
class ComplexSystemVisioningSchema:
    abm_summary: str
    indicators: Dict[str, Any]

@dataclass
class ImplementationResonanceSchema:
    crdsp_pass: bool
    docs_updated: bool

@dataclass
class ProtocolInitSchema:
    session_id: str
    version: str

@dataclass
class ProtocolErrorSchema:
    message: str
    error: str
    fallback_mode: bool

@dataclass
class EnhancedMessage:
    """
    Defines the canonical JSON envelope for messages within the ArchE system,
    providing a rich, structured context for observability and debugging.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    timestamp: str = field(default_factory=lambda: now_iso() + "Z")
    sender: SenderType = "arche"
    message_type: MessageType = "chat"
    protocol_compliance: bool = True
    protocol_version: str = "ResonantiA v3.1-CA"
    
    # Optional contextual data blocks
    iar: Optional[IARSchema] = None
    spr_activations: Optional[List[SPRActivationSchema]] = None
    temporal_context: Optional[TemporalContextSchema] = None
    meta_cognitive_state: Optional[MetaCognitiveStateSchema] = None
    complex_system_visioning: Optional[ComplexSystemVisioningSchema] = None
    implementation_resonance: Optional[ImplementationResonanceSchema] = None
    thought_trail: Optional[List[str]] = None
    protocol_init: Optional[ProtocolInitSchema] = None
    protocol_error: Optional[ProtocolErrorSchema] = None

    def to_json(self) -> str:
        """Serializes the dataclass to a JSON string, excluding None values."""
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        return json.dumps(data, indent=2, default=lambda o: o.__dict__)

@dataclass
class VcdEvent:
    """
    Defines the atomic event structure for the Visual Cognitive Debugger (VCD) timeline.
    Each event represents a discrete step or observation in a workflow.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    t: int = field(default_factory=lambda: int(time.time()))
    type: VcdEventType = "ThoughtTrail"
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    severity: SeverityType = "info"

    def to_json(self) -> str:
        """Serializes the VCD event to a single-line JSON string."""
        return json.dumps(self.__dict__, default=str)

# --- Emission Contract ---

def emit_vcd_event(
    event_type: VcdEventType,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
    severity: Optional[SeverityType] = "info"
) -> str:
    """
    Creates and serializes a VcdEvent. This function embodies the emission contract.

    Args:
        event_type: The type of the VCD event.
        message: A descriptive message for the event.
        metadata: Optional dictionary for additional context (e.g., task_id).
        severity: The severity level of the event.

    Returns:
        A single-line JSON string representing the VcdEvent.
    """
    event = VcdEvent(
        type=event_type,
        message=message,
        metadata=metadata or {},
        severity=severity
    )
    # In a real implementation, this would likely log to a file or send to a websocket
    print(event.to_json()) # For demonstration, print to stdout
    return event.to_json()


if __name__ == '__main__':
    print("--- Protocol & VCD Event Schema Demonstration ---")

    # Example 1: A simple chat message from the user
    user_chat = EnhancedMessage(
        sender="user",
        message_type="chat",
        content="Tell me about Cognitive Resonance."
    )
    print("\n1. User Chat Message:")
    print(user_chat.to_json())

    # Example 2: ArchE response with IAR and SPR activation
    arche_response = EnhancedMessage(
        sender="arche",
        message_type="iar",
        content="Cognitive Resonance is a state of profound alignment...",
        iar=IARSchema(status="ok", confidence=0.92),
        spr_activations=[SPRActivationSchema(spr_id="Cognitive resonancE", confidence=0.88)]
    )
    print("\n2. ArchE Response with IAR:")
    print(arche_response.to_json())

    # Example 3: VCD Events for a workflow task
    print("\n3. VCD Event Sequence for a Task:")
    task_meta = {"task_id": "deconstruct_code_blueprints", "attempt": 1}
    emit_vcd_event("TaskEvaluation", "Starting evaluation of task.", task_meta, "info")
    emit_vcd_event("TaskExecution", "Executing blueprint deconstruction.", task_meta, "info")
    emit_vcd_event(
        "IAR",
        "Deconstruction complete. Found 15 blueprints.",
        {"task_id": "deconstruct_code_blueprints", "confidence": 0.9, "issues": None},
        "success"
    )
    emit_vcd_event("TaskSuccess", "Task completed successfully.", task_meta, "success")

    # Example 4: A protocol error message
    error_message = EnhancedMessage(
        sender="arche",
        message_type="error",
        content="Failed to connect to external API.",
        protocol_compliance=False,
        protocol_error=ProtocolErrorSchema(
            message="API Connection Timeout",
            error="Connection timed out after 30 seconds.",
            fallback_mode=True
        )
    )
    print("\n4. Protocol Error Message:")
    print(error_message.to_json())
