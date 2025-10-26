from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# The canonical definition of a QuantumProbability state
@dataclass
class QuantumProbability:
    probability: float
    evidence: list[str] = field(default_factory=list)

    def to_dict(self):
        return {"probability": self.probability, "evidence": self.evidence}

# The one true, canonical definition of a CognitiveResponse
@dataclass
class CognitiveResponse:
    content: str
    confidence: QuantumProbability
    processing_path: str
    controller_used: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: Optional[float] = None
    fallback_reason: Optional[str] = None
    initial_superposition: Optional[Dict[str, float]] = None

    def to_dict(self):
        return {
            "content": self.content,
            "confidence": self.confidence.to_dict(),
            "processing_path": self.processing_path,
            "controller_used": self.controller_used,
            "metadata": self.metadata,
            "processing_time_ms": self.processing_time_ms,
            "fallback_reason": self.fallback_reason,
            "initial_superposition": self.initial_superposition,
        }

# The canonical definition of CognitiveMetrics
@dataclass
class CognitiveMetrics:
    """Performance metrics for the cognitive system."""
    total_queries: int = 0
    crcs_direct_count: int = 0
    crcs_fallback_count: int = 0
    rise_primary_count: int = 0
    rise_escalation_count: int = 0
    avg_crcs_time_ms: float = 0.0
    avg_rise_time_ms: float = 0.0
    avg_confidence: float = 0.0
    learning_events: int = 0
    
    def update_avg(self, field_name: str, new_value: float, count: int):
        """Update a running average."""
        current_avg = getattr(self, field_name)
        new_avg = (current_avg * (count - 1) + new_value) / count if count > 0 else new_value
        setattr(self, field_name, new_avg)

