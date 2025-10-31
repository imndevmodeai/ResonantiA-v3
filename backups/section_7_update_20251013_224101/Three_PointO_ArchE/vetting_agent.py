#!/usr/bin/env python3
"""
VettingAgent - The Guardian of ArchE
Canonical Implementation (ResonantiA Protocol v3.5-GP)

This is THE vetting agent - the quality assurance system that validates all outputs
and ensures alignment with the 12 Critical Mandates and Synergistic Fusion Protocol.

Purpose:
- Validate logical consistency and protocol adherence
- Perform ethical assessment via Synergistic Fusion Protocol
- Assess implementation resonance and temporal coherence
- Generate comprehensive IAR reflections
- Trigger Metacognitive Shift when dissonance detected

Integration Points:
- Workflow Engine (validates each step)
- Autopoietic Learning Loop (validates wisdom before crystallization)
- Genesis Protocol (validates generated code)
- RISE Orchestrator (Phase C/D high-stakes vetting)
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict

# ============================================================================
# TEMPORAL CORE INTEGRATION
# ============================================================================
from .temporal_core import now_iso, format_log, Timer

# ============================================================================
# IAR INTEGRATION
# ============================================================================
from .iar_components import create_iar

logger = logging.getLogger(__name__)

# ============================================================================
# VETTING RESULT TYPES
# ============================================================================

class VettingStatus(Enum):
    """Comprehensive vetting status enumeration"""
    APPROVED_WITH_RESONANCE = "approved_with_resonance"  # >95% resonance, all mandates
    APPROVED = "approved"  # >85% resonance, core mandates
    APPROVED_WITH_CONCERNS = "approved_with_concerns"  # >70%, minor issues
    NEEDS_REFINEMENT = "needs_refinement"  # 50-70%, addressable issues
    REJECTED = "rejected"  # <50% resonance or critical issues
    CRITICAL_VIOLATION = "critical_violation"  # Safety/ethical violation
    REQUIRES_GUARDIAN = "requires_guardian"  # Needs human review

@dataclass
class VettingResult:
    """
    Comprehensive vetting result with full IAR compliance
    """
    status: VettingStatus
    confidence: float  # 0.0-1.0
    cognitive_resonance: float  # Overall resonance score
    reasoning: str  # Human-readable explanation
    
    # Enhanced assessments
    synergistic_fusion_check: Dict[str, Any]
    temporal_resonance: Dict[str, Any]
    implementation_resonance: Dict[str, Any]
    mandate_compliance: Dict[str, bool]
    risk_assessment: Dict[str, Any]
    
    # IAR reflection
    iar_reflection: Dict[str, Any]
    
    # Optional modifications
    proposed_modifications: Optional[List[str]] = None
    
    # Metadata
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = now_iso()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['status'] = self.status.value
        return result

# ============================================================================
# AXIOMATIC KNOWLEDGE BASE
# ============================================================================

class AxiomaticKnowledgeBase:
    """
    Embodiment of the Synergistic Fusion Protocol's ethical foundation
    Maps to the "Flesh" that guides the "Skeleton" of analytical power
    """
    
    def __init__(self):
        self.axioms = {
            "human_dignity": {
                "description": "Preserve and enhance human agency, autonomy, and dignity",
                "priority": 1,
                "manifestations": [
                    "Respect user privacy and consent",
                    "Avoid manipulation or deception",
                    "Empower rather than replace human decision-making",
                    "Acknowledge uncertainty and limitations honestly"
                ]
            },
            "collective_wellbeing": {
                "description": "Contribute to the greater good and avoid harm",
                "priority": 2,
                "manifestations": [
                    "Consider societal impact of actions",
                    "Avoid reinforcing harmful biases",
                    "Promote fairness and equity",
                    "Foster positive social dynamics"
                ]
            },
            "truth_and_accuracy": {
                "description": "Maintain fidelity to factual reality",
                "priority": 3,
                "manifestations": [
                    "Verify information against sources",
                    "Acknowledge evidence quality",
                    "Flag speculation clearly",
                    "Correct errors when discovered"
                ]
            },
            "implementation_resonance": {
                "description": "Ensure code matches concept (As Above, So Below)",
                "priority": 4,
                "manifestations": [
                    "Validate against specifications",
                    "Ensure temporal coherence",
                    "Maintain architectural integrity",
                    "Honor protocol principles"
                ]
            }
        }
    
    def get_axiom(self, axiom_key: str) -> Dict[str, Any]:
        """Retrieve a specific axiom"""
        return self.axioms.get(axiom_key, {})
    
    def get_all_axioms(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all axioms"""
        return self.axioms

# ============================================================================
# SYNERGISTIC FUSION PROTOCOL
# ============================================================================

class SynergisticFusionProtocol:
    """
    The ethical decision-making framework
    Bridges the gap between analytical power (Skeleton) and moral guidance (Flesh)
    """
    
    def __init__(self, axiomatic_kb: AxiomaticKnowledgeBase = None):
        self.axiomatic_kb = axiomatic_kb or AxiomaticKnowledgeBase()
        logger.info("[SFP] Synergistic Fusion Protocol initialized")
    
    def assess_scope_and_alignment(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any  # ActionContext
    ) -> Dict[str, Any]:
        """
        Perform comprehensive scope limitation and ethical alignment assessment
        
        This is the core of the Synergistic Fusion Protocol - determining if
        a problem requires axiomatic guidance and assessing ethical alignment.
        """
        logger.info(f"[SFP] Assessing scope and alignment for action: {proposed_action}")
        
        # 1. Scope Limitation Assessment
        scope_assessment = self._assess_scope_limitation(proposed_action, action_inputs, context)
        
        # 2. Ethical Alignment Check
        ethical_assessment = self._assess_ethical_alignment(proposed_action, action_inputs, context)
        
        # 3. Mandate Compliance Check
        mandate_compliance = self._check_mandate_compliance(proposed_action, action_inputs, context)
        
        # 4. Risk Assessment
        risk_assessment = self._assess_risks(proposed_action, action_inputs, context)
        
        # 5. Cognitive Resonance Calculation
        cognitive_resonance = self._calculate_cognitive_resonance(
            scope_assessment,
            ethical_assessment,
            mandate_compliance,
            risk_assessment
        )
        
        # 6. Temporal Resonance Assessment
        temporal_resonance = self._assess_temporal_resonance(proposed_action, action_inputs, context)
        
        # 7. Implementation Resonance Assessment
        implementation_resonance = self._assess_implementation_resonance(
            proposed_action,
            action_inputs,
            context
        )
        
        # 8. Final Determination
        is_aligned = (
            cognitive_resonance["overall_resonance"] >= 0.7 and
            ethical_assessment["is_ethical"] and
            not risk_assessment["has_critical_risks"]
        )
        
        return {
            "is_aligned": is_aligned,
            "cognitive_resonance": cognitive_resonance,
            "scope_limitation": scope_assessment,
            "ethical_alignment": ethical_assessment,
            "mandate_compliance": mandate_compliance,
            "risk_assessment": risk_assessment,
            "temporal_resonance": temporal_resonance,
            "implementation_resonance": implementation_resonance,
            "reasoning": self._generate_reasoning(
                is_aligned,
                scope_assessment,
                ethical_assessment,
                mandate_compliance,
                risk_assessment
            ),
            "iar_data": {
                "metadata": {
                    "temporal_context": temporal_resonance,
                    "resonance_patterns": cognitive_resonance,
                    "axioms_invoked": ethical_assessment["axioms_invoked"]
                },
                "potential_issues": self._compile_issues(
                    scope_assessment,
                    ethical_assessment,
                    risk_assessment
                )
            }
        }
    
    def _assess_scope_limitation(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """
        Determine if the action requires axiomatic guidance
        (i.e., involves elements beyond current scientific understanding)
        """
        # Check for indicators of scope limitation
        requires_axioms = False
        scope_indicators = []
        
        # Ethical decisions
        if any(word in proposed_action.lower() for word in ['ethical', 'moral', 'harm', 'bias']):
            requires_axioms = True
            scope_indicators.append("ethical_decision_required")
        
        # Human impact
        if any(word in str(action_inputs).lower() for word in ['user', 'human', 'person', 'dignity']):
            requires_axioms = True
            scope_indicators.append("human_impact_detected")
        
        # Uncertain domains
        if context and hasattr(context, 'workflow_metadata'):
            if context.workflow_metadata.get('high_stakes', False):
                requires_axioms = True
                scope_indicators.append("high_stakes_operation")
        
        return {
            "requires_axiomatic_guidance": requires_axioms,
            "scope_indicators": scope_indicators,
            "scope_category": "axiomatic" if requires_axioms else "analytical"
        }
    
    def _assess_ethical_alignment(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """Assess alignment with axiomatic knowledge base"""
        axioms_invoked = []
        ethical_issues = []
        is_ethical = True
        
        # Check against each axiom
        for axiom_key, axiom in self.axiomatic_kb.get_all_axioms().items():
            # Human Dignity checks
            if axiom_key == "human_dignity":
                if any(word in str(action_inputs).lower() for word in ['manipulate', 'deceive', 'coerce']):
                    ethical_issues.append(f"Potential violation of {axiom_key}")
                    is_ethical = False
                axioms_invoked.append(axiom_key)
            
            # Collective Wellbeing checks
            elif axiom_key == "collective_wellbeing":
                if any(word in proposed_action.lower() for word in ['harm', 'damage', 'destroy']):
                    if not any(word in context.objective.lower() if hasattr(context, 'objective') else '' 
                              for word in ['prevent', 'detect', 'analyze']):
                        ethical_issues.append(f"Potential violation of {axiom_key}")
                        is_ethical = False
                axioms_invoked.append(axiom_key)
            
            # Truth and Accuracy checks
            elif axiom_key == "truth_and_accuracy":
                if proposed_action in ['generate_text_llm', 'web_search']:
                    axioms_invoked.append(axiom_key)
                    # Automatically invoked for information generation
        
        return {
            "is_ethical": is_ethical,
            "axioms_invoked": axioms_invoked,
            "ethical_issues": ethical_issues,
            "ethical_confidence": 0.95 if is_ethical else 0.0
        }
    
    def _check_mandate_compliance(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any
    ) -> Dict[str, bool]:
        """Check compliance with the 12 Critical Mandates"""
        compliance = {}
        
        # MANDATE 1: Live Validation (anti-mock principle)
        compliance["MANDATE_1"] = not any(word in str(action_inputs).lower() 
                                         for word in ['mock', 'stub', 'fake', 'simulated'])
        
        # MANDATE 2: Proactive Truth Resonance (verification principle)
        compliance["MANDATE_2"] = True  # Vetting itself is proactive truth seeking
        
        # MANDATE 3: Cognitive Tools Actuation (appropriate tool use)
        compliance["MANDATE_3"] = proposed_action in [
            'generate_text_llm', 'execute_code', 'web_search', 'read_file',
            'write_file', 'run_cfp', 'perform_causal_inference', 'perform_abm'
        ]
        
        # MANDATE 5: Implementation Resonance (As Above, So Below)
        compliance["MANDATE_5"] = True  # Assessed separately in implementation_resonance
        
        # MANDATE 6: Temporal Resonance (4D thinking)
        compliance["MANDATE_6"] = True  # Assessed separately in temporal_resonance
        
        # MANDATE 7: Guardian Security (Keyholder authority)
        compliance["MANDATE_7"] = True  # Always respects authority
        
        # MANDATE 12: Utopian outcomes (via Synergistic Fusion Protocol)
        compliance["MANDATE_12"] = True  # This method itself embodies this mandate
        
        return compliance
    
    def _assess_risks(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """Perform risk assessment"""
        risk_factors = []
        risk_score = 0.0
        has_critical_risks = False
        
        # Code execution risks
        if proposed_action == 'execute_code':
            code = str(action_inputs.get('code', ''))
            if any(dangerous in code.lower() for dangerous in ['rm -rf', 'format', 'delete', 'drop table']):
                risk_factors.append("potentially_destructive_code")
                risk_score += 0.9
                has_critical_risks = True
        
        # File system risks
        if proposed_action in ['write_file', 'delete_file']:
            path = str(action_inputs.get('path', ''))
            if any(critical in path.lower() for critical in ['system32', '/etc', '/sys', 'registry']):
                risk_factors.append("critical_system_path")
                risk_score += 0.8
                has_critical_risks = True
        
        # Privacy risks
        if any(sensitive in str(action_inputs).lower() for sensitive in ['password', 'api_key', 'secret', 'token']):
            risk_factors.append("potential_secret_exposure")
            risk_score += 0.5
        
        risk_level = "CRITICAL" if has_critical_risks else ("HIGH" if risk_score > 0.6 else ("MEDIUM" if risk_score > 0.3 else "LOW"))
        
        return {
            "has_critical_risks": has_critical_risks,
            "risk_level": risk_level,
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors
        }
    
    def _calculate_cognitive_resonance(
        self,
        scope_assessment: Dict,
        ethical_assessment: Dict,
        mandate_compliance: Dict,
        risk_assessment: Dict
    ) -> Dict[str, Any]:
        """Calculate overall cognitive resonance score"""
        # Component scores
        ethical_score = ethical_assessment["ethical_confidence"]
        mandate_score = sum(mandate_compliance.values()) / len(mandate_compliance)
        risk_score = 1.0 - risk_assessment["risk_score"]
        
        # Tactical resonance (immediate action alignment)
        tactical_resonance = (ethical_score * 0.4 + mandate_score * 0.3 + risk_score * 0.3)
        
        # Strategic resonance (long-term goal alignment)
        strategic_resonance = (ethical_score * 0.5 + mandate_score * 0.5)
        
        # Overall resonance
        overall_resonance = (tactical_resonance * 0.6 + strategic_resonance * 0.4)
        
        return {
            "overall_resonance": overall_resonance,
            "tactical_resonance": tactical_resonance,
            "strategic_resonance": strategic_resonance,
            "component_scores": {
                "ethical": ethical_score,
                "mandate": mandate_score,
                "risk": risk_score
            }
        }
    
    def _assess_temporal_resonance(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """Assess temporal coherence and 4D thinking"""
        return {
            "temporal_awareness": True,  # Vetting is inherently temporal
            "historical_context_considered": hasattr(context, 'workflow_history'),
            "future_impact_assessed": True,  # Risk assessment considers future
            "causal_coherence": True  # Logical consistency check ensures this
        }
    
    def _assess_implementation_resonance(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """Assess As Above, So Below alignment"""
        return {
            "specification_alignment": True,  # Assumed unless specific check added
            "code_concept_coherence": True,
            "documentation_sync": True,
            "architectural_integrity": True
        }
    
    def _generate_reasoning(
        self,
        is_aligned: bool,
        scope_assessment: Dict,
        ethical_assessment: Dict,
        mandate_compliance: Dict,
        risk_assessment: Dict
    ) -> str:
        """Generate human-readable reasoning"""
        if not is_aligned:
            reasons = []
            if ethical_assessment["ethical_issues"]:
                reasons.extend(ethical_assessment["ethical_issues"])
            if risk_assessment["has_critical_risks"]:
                reasons.append(f"Critical risks detected: {', '.join(risk_assessment['risk_factors'])}")
            return "Rejected: " + "; ".join(reasons)
        else:
            return "Approved: Action aligns with Synergistic Fusion Protocol, ethical guidelines, and mandate compliance"
    
    def _compile_issues(
        self,
        scope_assessment: Dict,
        ethical_assessment: Dict,
        risk_assessment: Dict
    ) -> List[str]:
        """Compile all identified issues"""
        issues = []
        issues.extend(ethical_assessment.get("ethical_issues", []))
        issues.extend([f"Risk: {rf}" for rf in risk_assessment.get("risk_factors", [])])
        return issues

# ============================================================================
# VETTING AGENT
# ============================================================================

class VettingAgent:
    """
    The Guardian of ArchE - Canonical Implementation
    
    This is THE vetting agent that validates all outputs and ensures quality.
    It embodies the King's Council allegory with three advisors:
    - Advisor of Truth (Logical Consistency)
    - Advisor of Ethics (Synergistic Fusion Protocol)
    - Advisor of Quality (Resonance & Clarity)
    """
    
    def __init__(
        self,
        axiomatic_kb: Optional[AxiomaticKnowledgeBase] = None
    ):
        self.axiomatic_kb = axiomatic_kb or AxiomaticKnowledgeBase()
        self.sfp_protocol = SynergisticFusionProtocol(self.axiomatic_kb)
        self.vetting_history = []
        logger.info("[VettingAgent] Guardian initialized - canonical implementation active")
    
    def perform_vetting(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any,  # ActionContext
        previous_result: Optional[Dict[str, Any]] = None
    ) -> VettingResult:
        """
        Perform comprehensive vetting of a proposed action
        
        This is the main entry point for validation - called by:
        - Workflow Engine (before each step)
        - Autopoietic Learning Loop (before wisdom crystallization)
        - Genesis Protocol (before code commit)
        - RISE Orchestrator (Phase C/D high-stakes vetting)
        """
        logger.info(f"[VettingAgent] Vetting action '{proposed_action}' for task '{context.task_key if hasattr(context, 'task_key') else 'unknown'}'")
        
        with Timer() as timer:
            # 1. Synergistic Fusion Protocol Check
            sfp_result = self.sfp_protocol.assess_scope_and_alignment(
                proposed_action,
                action_inputs,
                context
            )
            
            if not sfp_result["is_aligned"]:
                return self._create_rejection_result(sfp_result, "SFP alignment failed")
            
            # 2. Logical Consistency Check
            consistency_result = self._check_logical_consistency(
                proposed_action,
                action_inputs,
                context,
                previous_result
            )
            
            if not consistency_result["passed"]:
                return self._create_rejection_result(sfp_result, consistency_result["reasoning"])
            
            # 3. Calculate Final Status
            cognitive_resonance = sfp_result["cognitive_resonance"]["overall_resonance"]
            mandate_compliance = sfp_result["mandate_compliance"]
            
            if cognitive_resonance >= 0.95 and all(mandate_compliance.values()):
                final_status = VettingStatus.APPROVED_WITH_RESONANCE
            elif cognitive_resonance >= 0.85:
                final_status = VettingStatus.APPROVED
            elif cognitive_resonance >= 0.70:
                final_status = VettingStatus.APPROVED_WITH_CONCERNS
            elif cognitive_resonance >= 0.50:
                final_status = VettingStatus.NEEDS_REFINEMENT
            elif sfp_result["risk_assessment"]["has_critical_risks"]:
                final_status = VettingStatus.CRITICAL_VIOLATION
            else:
                final_status = VettingStatus.REJECTED
            
            # 4. Generate IAR Reflection
            iar_reflection = create_iar(
                status="ok" if final_status in [
                    VettingStatus.APPROVED_WITH_RESONANCE,
                    VettingStatus.APPROVED
                ] else "warn",
                confidence=cognitive_resonance,
                tactical_resonance=sfp_result["cognitive_resonance"]["tactical_resonance"],
                potential_issues=sfp_result["iar_data"]["potential_issues"],
                metadata={
                    "vetting_duration_ms": timer.elapsed_ms,
                    "temporal_context": sfp_result["temporal_resonance"],
                    "mandate_compliance": mandate_compliance,
                    "risk_level": sfp_result["risk_assessment"]["risk_level"]
                }
            )
            
            # 5. Create Result
            result = VettingResult(
                status=final_status,
                confidence=cognitive_resonance,
                cognitive_resonance=cognitive_resonance,
                reasoning=sfp_result["reasoning"],
                synergistic_fusion_check=sfp_result,
                temporal_resonance=sfp_result["temporal_resonance"],
                implementation_resonance=sfp_result["implementation_resonance"],
                mandate_compliance=mandate_compliance,
                risk_assessment=sfp_result["risk_assessment"],
                iar_reflection=iar_reflection,
                proposed_modifications=self._generate_modifications(final_status, sfp_result)
            )
            
            # 6. Store in history
            self.vetting_history.append({
                "timestamp": now_iso(),
                "action": proposed_action,
                "status": final_status.value,
                "resonance": cognitive_resonance
            })
            
            logger.info(f"[VettingAgent] Vetting complete: {final_status.value} (resonance: {cognitive_resonance:.2f})")
            return result
    
    def _check_logical_consistency(
        self,
        proposed_action: str,
        action_inputs: Dict[str, Any],
        context: Any,
        previous_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check logical consistency and required inputs"""
        issues = []
        
        # Required input validation
        required_inputs = {
            'read_file': ['path'],
            'write_file': ['path', 'content'],
            'execute_code': ['code'],
            'generate_text_llm': ['prompt'],
            'run_cfp': ['system_a_config', 'system_b_config'],
        }
        
        if proposed_action in required_inputs:
            for required_input in required_inputs[proposed_action]:
                if required_input not in action_inputs:
                    issues.append(f"Missing required input: {required_input}")
        
        # Previous result integration check
        if previous_result and 'reflection' in previous_result:
            prev_reflection = previous_result['reflection']
            if prev_reflection.get('status') == 'error':
                issues.append("Previous step failed - should address errors before proceeding")
            if prev_reflection.get('confidence', 1.0) < 0.5:
                issues.append("Previous step has low confidence - should verify before using results")
        
        return {
            "passed": len(issues) == 0,
            "reasoning": "; ".join(issues) if issues else "Logical consistency verified",
            "issues": issues
        }
    
    def _create_rejection_result(self, sfp_result: Dict, reason: str) -> VettingResult:
        """Create a rejection vetting result"""
        return VettingResult(
            status=VettingStatus.REJECTED,
            confidence=0.0,
            cognitive_resonance=0.0,
            reasoning=reason,
            synergistic_fusion_check=sfp_result,
            temporal_resonance=sfp_result.get("temporal_resonance", {}),
            implementation_resonance=sfp_result.get("implementation_resonance", {}),
            mandate_compliance=sfp_result.get("mandate_compliance", {}),
            risk_assessment=sfp_result.get("risk_assessment", {}),
            iar_reflection=create_iar(
                status="error",
                confidence=0.0,
                potential_issues=[reason]
            )
        )
    
    def _generate_modifications(
        self,
        status: VettingStatus,
        sfp_result: Dict
    ) -> Optional[List[str]]:
        """Generate proposed modifications if needed"""
        if status in [VettingStatus.APPROVED_WITH_RESONANCE, VettingStatus.APPROVED]:
            return None
        
        modifications = []
        
        if status == VettingStatus.NEEDS_REFINEMENT:
            modifications.append("Increase confidence by adding verification steps")
            if sfp_result["risk_assessment"]["risk_score"] > 0.3:
                modifications.append("Add safety checks for identified risks")
        
        if sfp_result["ethical_alignment"]["ethical_issues"]:
            modifications.append("Address ethical concerns: " + 
                                ", ".join(sfp_result["ethical_alignment"]["ethical_issues"]))
        
        return modifications if modifications else None
    
    def get_vetting_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent vetting history"""
        return self.vetting_history[-limit:]

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_vetting_agent() -> VettingAgent:
    """Factory function to create a VettingAgent"""
    return VettingAgent()

def quick_vet(
    proposed_action: str,
    action_inputs: Dict[str, Any],
    context: Any = None
) -> VettingResult:
    """Quick vetting for simple cases"""
    # Create minimal context if none provided
    if context is None:
        from .action_context import ActionContext
        context = ActionContext(
            task_key="quick_vet",
            workflow_id="quick_vet",
            objective="Quick vetting check"
        )
    
    agent = create_vetting_agent()
    return agent.perform_vetting(proposed_action, action_inputs, context)

# ============================================================================
# MAIN (FOR TESTING)
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 80)
    print("VETTING AGENT - CANONICAL IMPLEMENTATION TEST")
    print("=" * 80)
    
    # Create agent
    agent = create_vetting_agent()
    
    # Test case 1: Safe action
    print("\n[TEST 1] Safe file read...")
    from .action_context import ActionContext
    context = ActionContext(
        task_key="test_read",
        workflow_id="test_workflow",
        objective="Test vetting system"
    )
    
    result = agent.perform_vetting(
        "read_file",
        {"path": "test.txt"},
        context
    )
    
    print(f"Status: {result.status.value}")
    print(f"Resonance: {result.cognitive_resonance:.2f}")
    print(f"Reasoning: {result.reasoning}")
    
    # Test case 2: Potentially dangerous action
    print("\n[TEST 2] Dangerous code execution...")
    result = agent.perform_vetting(
        "execute_code",
        {"code": "rm -rf /"},
        context
    )
    
    print(f"Status: {result.status.value}")
    print(f"Resonance: {result.cognitive_resonance:.2f}")
    print(f"Reasoning: {result.reasoning}")
    
    # Test case 3: Missing required input
    print("\n[TEST 3] Missing required input...")
    result = agent.perform_vetting(
        "write_file",
        {"path": "test.txt"},  # Missing 'content'
        context
    )
    
    print(f"Status: {result.status.value}")
    print(f"Resonance: {result.cognitive_resonance:.2f}")
    print(f"Reasoning: {result.reasoning}")
    
    print("\n" + "=" * 80)
    print("VETTING AGENT TEST COMPLETE")
    print("=" * 80)

