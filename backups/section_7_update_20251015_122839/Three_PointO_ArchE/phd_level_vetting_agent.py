#!/usr/bin/env python3
"""
Enhanced Vetting Agent - Complete PhD-Level Implementation
Integrates all components with CRITICAL_MANDATES.md compliance
"""

import logging
import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer

# Import all components
from enhanced_vetting_agent import VettingStatus, VettingResult
from enhanced_vetting_agent_part2 import AxiomaticKnowledgeBase
from enhanced_vetting_agent_part3 import SynergisticFusionProtocol
from enhanced_vetting_agent_main import EnhancedVettingAgent

logger = logging.getLogger(__name__)

# Main Enhanced Vetting Agent Implementation
class PhDLevelVettingAgent(EnhancedVettingAgent):
    """
    PhD-Level Vetting Agent - Complete Implementation
    Integrates all CRITICAL_MANDATES.md with advanced cognitive capabilities
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cognitive_evolution_enabled = True
        self.pattern_crystallization_active = True
        self.autonomous_learning_enabled = True
        logger.info("[PhDLevelVettingAgent] Initialized with full PhD-level capabilities")
    
    async def perform_comprehensive_vetting(self, proposed_action: str, action_inputs: Dict, context: Any) -> VettingResult:
        """
        Perform comprehensive PhD-level vetting with all advanced capabilities
        """
        # Convert context to ActionContext if needed
        if not isinstance(context, ActionContext):
            context = ActionContext(
                task_key=context.get('task_key', 'unknown'),
                action_name=context.get('action_name', proposed_action),
                action_type=context.get('action_type', proposed_action),
                workflow_name=context.get('workflow_name', 'unknown'),
                run_id=context.get('run_id', 'unknown')
            )
        
        # Perform enhanced vetting
        result = await self.perform_vetting(proposed_action, action_inputs, context)
        
        # Add PhD-level enhancements
        if self.cognitive_evolution_enabled:
            await self._apply_cognitive_evolution(result, context)
        
        if self.pattern_crystallization_active:
            await self._apply_pattern_crystallization(result, context)
        
        if self.autonomous_learning_enabled:
            await self._apply_autonomous_learning(result, context)
        
        return result
    
    async def _apply_cognitive_evolution(self, result: VettingResult, context: ActionContext):
        """Apply cognitive evolution based on vetting results"""
        # Update cognitive patterns based on results
        if context.task_key not in self.cognitive_patterns:
            self.cognitive_patterns[context.task_key] = {
                "frequency": 0,
                "success_rate": 0.0,
                "cognitive_resonance_history": [],
                "temporal_patterns": []
            }
        
        pattern = self.cognitive_patterns[context.task_key]
        pattern["frequency"] += 1
        pattern["cognitive_resonance_history"].append(result.cognitive_resonance)
        
        # Calculate success rate
        if result.status in [VettingStatus.APPROVED, VettingStatus.APPROVED_WITH_RESONANCE]:
            pattern["success_rate"] = (pattern["success_rate"] * (pattern["frequency"] - 1) + 1.0) / pattern["frequency"]
        else:
            pattern["success_rate"] = (pattern["success_rate"] * (pattern["frequency"] - 1) + 0.0) / pattern["frequency"]
    
    async def _apply_pattern_crystallization(self, result: VettingResult, context: ActionContext):
        """Apply pattern crystallization for knowledge evolution"""
        # Identify patterns in vetting results
        if result.cognitive_resonance > 0.9:
            # High resonance pattern
            self.axiomatic_kb.resonance_patterns[f"high_resonance_{context.action_type}"] = {
                "pattern_type": "high_cognitive_resonance",
                "action_type": context.action_type,
                "cognitive_resonance": result.cognitive_resonance,
                "timestamp": now_iso(),
                "context": vars(context)
            }
        
        # Store implementation patterns
        if result.implementation_resonance.get("as_above_so_below_score", 0) > 0.9:
            self.axiomatic_kb.resonance_patterns[f"implementation_resonance_{context.action_type}"] = {
                "pattern_type": "implementation_resonance",
                "action_type": context.action_type,
                "implementation_resonance": result.implementation_resonance,
                "timestamp": now_iso()
            }
    
    async def _apply_autonomous_learning(self, result: VettingResult, context: ActionContext):
        """Apply autonomous learning based on vetting outcomes"""
        # Learn from successful patterns
        if result.status == VettingStatus.APPROVED_WITH_RESONANCE:
            # This is an excellent pattern - learn from it
            learning_data = {
                "action_type": context.action_type,
                "cognitive_resonance": result.cognitive_resonance,
                "mandate_compliance": result.mandate_compliance,
                "temporal_resonance": result.temporal_resonance,
                "implementation_resonance": result.implementation_resonance,
                "timestamp": now_iso()
            }
            
            # Store in learning database
            if not hasattr(self, 'learning_database'):
                self.learning_database = []
            
            self.learning_database.append(learning_data)
            
            # Update cognitive thresholds based on learning
            if result.cognitive_resonance > self.cognitive_resonance_threshold:
                self.cognitive_resonance_threshold = min(0.95, self.cognitive_resonance_threshold + 0.01)
    
    def get_cognitive_insights(self) -> Dict[str, Any]:
        """Get cognitive insights from vetting history"""
        if not self.vetting_history:
            return {"message": "No vetting history available"}
        
        # Analyze patterns
        total_vettings = len(self.vetting_history)
        approved_count = sum(1 for v in self.vetting_history if v["result"] in ["APPROVED", "APPROVED_WITH_RESONANCE"])
        avg_cognitive_resonance = sum(v["cognitive_resonance"] for v in self.vetting_history) / total_vettings
        
        # Mandate compliance analysis
        mandate_compliance_stats = {}
        for mandate_id in ["MANDATE_1", "MANDATE_5", "MANDATE_6", "MANDATE_7", "MANDATE_10"]:
            compliant_count = sum(1 for v in self.vetting_history if v["mandate_compliance"].get(mandate_id, False))
            mandate_compliance_stats[mandate_id] = {
                "compliance_rate": compliant_count / total_vettings,
                "compliant_count": compliant_count
            }
        
        return {
            "total_vettings": total_vettings,
            "approval_rate": approved_count / total_vettings,
            "average_cognitive_resonance": avg_cognitive_resonance,
            "mandate_compliance_stats": mandate_compliance_stats,
            "cognitive_patterns": self.cognitive_patterns,
            "resonance_patterns": self.axiomatic_kb.resonance_patterns,
            "learning_database_size": len(getattr(self, 'learning_database', []))
        }

# Integration function for workflow engine
async def perform_enhanced_vetting(proposed_action: str, action_inputs: Dict, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integration function for workflow engine
    Returns IAR-compliant result
    """
    try:
        # Initialize PhD-level vetting agent
        vetting_agent = PhDLevelVettingAgent()
        
        # Perform comprehensive vetting
        result = await vetting_agent.perform_comprehensive_vetting(proposed_action, action_inputs, context)
        
        # Return IAR-compliant result
        return {
            "success": result.status in [VettingStatus.APPROVED, VettingStatus.APPROVED_WITH_RESONANCE],
            "status": result.status.value,
            "confidence": result.confidence,
            "cognitive_resonance": result.cognitive_resonance,
            "reasoning": result.reasoning,
            "mandate_compliance": result.mandate_compliance,
            "risk_assessment": result.risk_assessment,
            "iar": result.iar_reflection,
            "proposed_modifications": result.proposed_modifications,
            "temporal_resonance": result.temporal_resonance,
            "implementation_resonance": result.implementation_resonance
        }
    
    except Exception as e:
        logger.error(f"Enhanced vetting failed: {e}", exc_info=True)
        return {
            "success": False,
            "status": "ERROR",
            "confidence": 0.0,
            "reasoning": f"Vetting error: {str(e)}",
            "iar": {
                "status": "error",
                "confidence": 0.0,
                "potential_issues": [str(e)],
                "metadata": {"error": str(e)}
            }
        }

# Test harness
async def main():
    """Test harness for PhD-level vetting agent"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("--- PhD-Level Enhanced Vetting Agent Test Harness ---")
    
    # Initialize agent
    agent = PhDLevelVettingAgent()
    
    # Test cases
    test_cases = [
        {
            "name": "Safe Code Execution",
            "action": "execute_code",
            "inputs": {"language": "python", "code": "print('Hello, ArchE!')"},
            "context": {"task_key": "T1", "action_name": "TestCode", "workflow_name": "TestWorkflow", "run_id": "test_001"}
        },
        {
            "name": "Dangerous Code Execution",
            "action": "execute_code", 
            "inputs": {"language": "bash", "code": "rm -rf / --no-preserve-root"},
            "context": {"task_key": "T2", "action_name": "DangerousCode", "workflow_name": "TestWorkflow", "run_id": "test_002"}
        },
        {
            "name": "File Read Operation",
            "action": "read_file",
            "inputs": {"path": "specifications/test.md"},
            "context": {"task_key": "T3", "action_name": "ReadFile", "workflow_name": "TestWorkflow", "run_id": "test_003"}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = await agent.perform_comprehensive_vetting(
            test_case["action"],
            test_case["inputs"],
            test_case["context"]
        )
        
        print(f"Status: {result.status.value}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Cognitive Resonance: {result.cognitive_resonance:.3f}")
        print(f"Reasoning: {result.reasoning}")
        print(f"Mandate Compliance: {sum(result.mandate_compliance.values())}/{len(result.mandate_compliance)}")
    
    # Get cognitive insights
    print(f"\n--- Cognitive Insights ---")
    insights = agent.get_cognitive_insights()
    print(json.dumps(insights, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
