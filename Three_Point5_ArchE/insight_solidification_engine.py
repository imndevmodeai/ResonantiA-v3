import logging
import json
import shutil
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# --- Enums and Dataclasses ---

class InsightType(Enum):
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"

class ValidationStatus(Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"

class SolidificationMethod(Enum):
    NEW_SPR = "new_spr"
    UPDATE_SPR = "update_spr"

@dataclass
class InsightCandidate:
    insight_id: str
    insight_type: InsightType
    core_concept: str
    supporting_details: str
    source_reference: str
    evidence_strength: float
    confidence: float

@dataclass
class ValidationResult:
    validation_status: ValidationStatus
    confidence: float
    notes: str = ""

@dataclass
class SolidificationPlan:
    method: SolidificationMethod
    spr_data: Dict[str, Any]

@dataclass
class SolidificationResult:
    execution_status: str
    spr_changes_made: List[str]
    knowledge_tapestry_updated: bool

# --- Core Components ---

class SPRManager:
    """Manages SPR creation, updating, and integration."""
    def __init__(self, knowledge_tapestry_path: str):
        self.kt_path = Path(knowledge_tapestry_path)
    
    def add_spr(self, spr_data: Dict[str, Any]) -> bool:
        """Adds a new SPR to the knowledge tapestry."""
        try:
            tapestry = json.loads(self.kt_path.read_text()) if self.kt_path.exists() else {"spr_definitions": []}
            tapestry["spr_definitions"].append(spr_data)
            self.kt_path.write_text(json.dumps(tapestry, indent=2))
            return True
        except Exception as e:
            logger.error(f"Failed to add SPR: {e}")
            return False

class InsightValidator:
    """Validates insights against existing knowledge and quality standards."""
    def validate_insight(self, insight: InsightCandidate) -> ValidationResult:
        """Perform comprehensive validation of an insight."""
        # Simplified validation logic
        if insight.confidence > 0.7 and insight.evidence_strength > 0.6:
            return ValidationResult(ValidationStatus.VALIDATED, 0.9, "Insight meets quality thresholds.")
        else:
            return ValidationResult(ValidationStatus.REJECTED, 0.4, "Insight confidence or evidence is too low.")

class InsightSolidificationEngine:
    """Implementation of the InsightsolidificatioN SPR."""
    def __init__(self, knowledge_tapestry_path: str):
        self.spr_manager = SPRManager(knowledge_tapestry_path)
        self.validator = InsightValidator()

    def solidify_insight(self, insight: InsightCandidate) -> Dict[str, Any]:
        """Main workflow for solidifying an insight."""
        start_time = time.time()
        
        try:
            validation_result = self.validator.validate_insight(insight)
            if validation_result.validation_status != ValidationStatus.VALIDATED:
                raise ValueError(f"Insight validation failed: {validation_result.notes}")

            plan = self._create_solidification_plan(insight)
            result = self._execute_solidification(plan)
            
            return {
                "result": result,
                "reflection": {
                    "status": "success",
                    "message": f"Insight '{insight.insight_id}' solidified successfully.",
                    "confidence": validation_result.confidence,
                    "execution_time": time.time() - start_time,
                }
            }

        except Exception as e:
            logger.error(f"Solidification failed for insight {insight.insight_id}: {e}", exc_info=True)
            return {
                "error": str(e),
                "reflection": {
                    "status": "failure",
                    "message": str(e),
                    "confidence": 0.2,
                    "execution_time": time.time() - start_time,
                }
            }

    def _create_solidification_plan(self, insight: InsightCandidate) -> SolidificationPlan:
        """Create detailed plan for insight solidification."""
        spr_data = {
            "spr_id": f"SPR_{insight.insight_id}",
            "core_concept": insight.core_concept,
            "details": insight.supporting_details,
            "source": insight.source_reference
        }
        return SolidificationPlan(method=SolidificationMethod.NEW_SPR, spr_data=spr_data)

    def _execute_solidification(self, plan: SolidificationPlan) -> SolidificationResult:
        """Execute the solidification plan."""
        if plan.method == SolidificationMethod.NEW_SPR:
            success = self.spr_manager.add_spr(plan.spr_data)
            if success:
                return SolidificationResult("completed", [plan.spr_data["spr_id"]], True)
        
        raise RuntimeError("Solidification execution failed.")
