#!/usr/bin/env python3
"""
RISE v2.0 Genesis Protocol - RISE_Orchestrator
Master controller for the Resonant Insight and Strategy Engine (RISE) v2.0

This module implements the Genesis Protocol as described in the RISE v2.0 blueprint.
It orchestrates the three-phase workflow that can forge specialized expert clones
and achieve unprecedented autonomous strategic reasoning.

Phase A: Knowledge Scaffolding & Dynamic Specialization
Phase B: Fused Insight Generation  
Phase C: Fused Strategy Generation & Finalization

The RISE_Orchestrator manages the state of a problem as it moves through these phases,
coordinating the Metamorphosis Protocol (sandboxed expert clones) and HighStakesVetting.

ENHANCED WITH SYNERGISTIC FUSION PROTOCOL:
The orchestrator now includes the ability to activate axiomatic knowledge when scope limitations
are detected, creating a synergistic fusion of scientific reasoning and spiritual guidance.
"""

import logging
import json
import time
import uuid
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from functools import lru_cache

# Import existing components (robust segmented import to avoid unnecessary fallbacks)
try:
    from .workflow_engine import IARCompliantWorkflowEngine
    from .spr_manager import SPRManager
    from .thought_trail import ThoughtTrail
    from .config import get_config
    from .utils.json_sanitizer import _sanitize_for_json # Import the sanitizer
except ImportError:
    # Fallback for direct execution context
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from workflow_engine import IARCompliantWorkflowEngine
    from spr_manager import SPRManager
    from thought_trail import ThoughtTrail
    from config import get_config

# Optional protocol modules
try:
    from .vetting_prompts import perform_scope_limitation_assessment, get_relevant_axioms
except Exception:
    perform_scope_limitation_assessment = None
    get_relevant_axioms = None

try:
    from .utopian_solution_synthesizer import UtopianSolutionSynthesizer
except Exception:
    UtopianSolutionSynthesizer = None


logger = logging.getLogger(__name__)

RISE_AVAILABLE = True

@dataclass
class RISEState:
    """Represents the state of a RISE workflow execution"""
    problem_description: str
    session_id: str
    current_phase: str
    phase_start_time: datetime
    session_knowledge_base: Dict[str, Any]
    specialized_agent: Optional[Dict[str, Any]]
    advanced_insights: List[Dict[str, Any]]
    specialist_consultation: Optional[Dict[str, Any]]
    fused_strategic_dossier: Optional[Dict[str, Any]]
    vetting_dossier: Optional[Dict[str, Any]]
    final_strategy: Optional[Dict[str, Any]]
    spr_definition: Optional[Dict[str, Any]]
    execution_metrics: Dict[str, Any]
    # Synergistic Fusion Protocol additions
    scope_limitation_assessment: Optional[Dict[str, Any]]
    activated_axioms: List[Dict[str, Any]]
    synergistic_synthesis: Optional[Dict[str, Any]]
    # Utopian Solution Synthesizer additions
    utopian_trust_packet: Optional[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return asdict(self)

class RISE_Orchestrator:
    """
    Master controller for the RISE v2.0 workflow.
    
    This orchestrator manages the three-phase process:
    1. Knowledge Scaffolding & Dynamic Specialization (Phase A)
    2. Fused Insight Generation (Phase B) 
    3. Fused Strategy Generation & Finalization (Phase C)
    
    It coordinates the Metamorphosis Protocol for creating specialized expert clones
    and implements HighStakesVetting for rigorous strategy validation.
    
    ENHANCED WITH SYNERGISTIC FUSION PROTOCOL:
    The orchestrator now includes the ability to activate axiomatic knowledge when scope limitations
    are detected, creating a synergistic fusion of scientific reasoning and spiritual guidance.
    """
    
    def __init__(self, workflows_dir: str = None, spr_manager: Optional[SPRManager] = None, workflow_engine: Optional[IARCompliantWorkflowEngine] = None):
        """
        Initialize the RISE_Orchestrator with proper path resolution.
        
        Args:
            workflows_dir: Directory containing workflow files. If None, will auto-detect.
            spr_manager: Optional SPR manager instance
            workflow_engine: Optional workflow engine instance
        """
        # --- Environment & Virtualenv Bootstrap (LLM/Search/Tools readiness) ---
        # MANDATORY: Use arche_env per CRITICAL_ARCHE_ENV_REQUIREMENT.md
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            # Prefer arche_env (documented requirement) over .venv
            venv_paths = [
                os.path.join(project_root, 'arche_env', 'bin'),  # Primary: arche_env (documented requirement)
                os.path.join(project_root, '.venv', 'bin')       # Fallback: .venv (legacy support)
            ]
            
            venv_bin = None
            venv_name = None
            for venv_path in venv_paths:
                if os.path.isdir(venv_path):
                    venv_bin = venv_path
                    venv_name = os.path.basename(os.path.dirname(venv_path))
                    break
            
            if venv_bin:
                # Prepend venv bin to PATH for subprocess and dynamic imports
                os.environ['PATH'] = venv_bin + os.pathsep + os.environ.get('PATH', '')
                # Ensure python in this process also sees venv site-packages
                venv_root = os.path.dirname(venv_bin)
                site_pkgs = os.path.join(venv_root, 'lib', f"python{sys.version_info.major}.{sys.version_info.minor}", 'site-packages')
                if os.path.isdir(site_pkgs) and site_pkgs not in sys.path:
                    sys.path.insert(0, site_pkgs)
                logger.info(f"RISE: activated {venv_name} virtualenv paths for current session")
            else:
                logger.warning(f"RISE: No virtual environment found (checked arche_env and .venv). Please ensure arche_env is created and activated.")
        except Exception as e:
            logger.warning(f"RISE: virtualenv bootstrap skipped: {e}")

        try:
            # Load API keys from environment (dotenv already handled in llm_tool)
            # Allow injection via RISE-specific variables if present
            gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('RISE_GEMINI_API_KEY')
            if gemini_key:
                os.environ['GEMINI_API_KEY'] = gemini_key
                logger.info("RISE: GEMINI_API_KEY available for LLM tool")
            serp_key = os.environ.get('SERPAPI_API_KEY') or os.environ.get('RISE_SERPAPI_API_KEY')
            if serp_key:
                os.environ['SERPAPI_API_KEY'] = serp_key
                logger.info("RISE: SERPAPI_API_KEY available for Search tool")
        except Exception as e:
            logger.warning(f"RISE: API key propagation skipped: {e}")

        # Auto-detect workflows directory if not provided
        if workflows_dir is None:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_root = os.path.dirname(script_dir)
            # Set workflows directory to project_root/workflows
            workflows_dir = os.path.join(project_root, "workflows")
            
            # Verify the workflows directory exists
            if not os.path.exists(workflows_dir):
                logger.warning(f"Workflows directory not found at {workflows_dir}, trying current working directory")
                workflows_dir = os.path.join(os.getcwd(), "workflows")
                
            logger.info(f"RISE_Orchestrator initialized with workflows_dir: {workflows_dir}")
        
        # Ensure workflows_dir is absolute
        workflows_dir = os.path.abspath(workflows_dir)
        
        # Verify the workflows directory exists and contains expected files
        if not os.path.exists(workflows_dir):
            raise FileNotFoundError(f"Workflows directory not found: {workflows_dir}")
        
        expected_files = [
            "knowledge_scaffolding.json",
            "metamorphosis_protocol.json", 
            "strategy_fusion.json",
            "high_stakes_vetting.json",
            "distill_spr.json"
        ]
        
        missing_files = []
        for file in expected_files:
            file_path = os.path.join(workflows_dir, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            logger.warning(f"Missing expected workflow files: {missing_files}")
        
        self.workflows_dir = workflows_dir
        self.active_sessions: Dict[str, RISEState] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        # Initialize components
        try:
            if spr_manager is None:
                # Provide default path to SPR definitions
                default_spr_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_graph", "spr_definitions_tv.json")
                if os.path.exists(default_spr_path):
                    self.spr_manager = SPRManager(spr_filepath=default_spr_path)
                    logger.info(f"SPRManager initialized with default path: {default_spr_path}")
                else:
                    logger.warning(f"Default SPR file not found at {default_spr_path}, creating minimal SPRManager")
                    # Create minimal fallback functionality
                    self.spr_manager = None
            else:
                self.spr_manager = spr_manager
        except Exception as e:
            logger.error(f"Failed to initialize SPRManager: {e}")
            self.spr_manager = None
        
        self.thought_trail = ThoughtTrail()
        
        # Initialize workflow engine with the correct workflows directory
        if workflow_engine is None:
            self.workflow_engine = IARCompliantWorkflowEngine(workflows_dir=self.workflows_dir)
        else:
            self.workflow_engine = workflow_engine
            # Update the workflow engine's workflows directory if needed
            if hasattr(self.workflow_engine, 'workflows_dir'):
                self.workflow_engine.workflows_dir = self.workflows_dir

        # Utopian Solution Synthesizer initialization
        if UtopianSolutionSynthesizer:
            self.utopian_synthesizer = UtopianSolutionSynthesizer(self.workflow_engine)
            self.utopian_synthesis_enabled = True
        else:
            self.utopian_synthesizer = None
            self.utopian_synthesis_enabled = False
        
        # Load axiomatic knowledge for synergistic fusion
        self.axiomatic_knowledge = self._load_axiomatic_knowledge()
        # Preload SPR index for prompt-time detection (supports canonical + aliases + term)
        try:
            self._spr_index = self._build_spr_index()
        except Exception as e:
            logger.warning(f"SPR index build failed: {e}")
            self._spr_index = None
        
        # Initialize Playbook Orchestrator for dynamic workflow generation
        try:
            from .playbook_orchestrator import PlaybookOrchestrator
            self.playbook_orchestrator = PlaybookOrchestrator()
            logger.info("🎭 PlaybookOrchestrator initialized - dynamic workflow generation enabled")
        except Exception as e:
            logger.warning(f"Failed to initialize PlaybookOrchestrator: {e}")
            self.playbook_orchestrator = None
        
        # Initialize federated agents for multi-disciplinary search
        try:
            from .federated_search_agents import (
                AcademicKnowledgeAgent,
                CommunityPulseAgent,
                CodebaseTruthAgent,
                VisualSynthesisAgent,
                SearchEngineAgent
            )
            self.federated_agents = {
                'academic': AcademicKnowledgeAgent(),
                'community': CommunityPulseAgent(),
                'code': CodebaseTruthAgent(),
                'visual': VisualSynthesisAgent(),
                'search': SearchEngineAgent("Startpage")
            }
            logger.info("🔬 Federated search agents initialized - multi-disciplinary search enabled")
        except Exception as e:
            logger.warning(f"Failed to initialize federated agents: {e}")
            self.federated_agents = {}
        
        # Initialize Codebase Archaeologist for self-referential synthesis
        try:
            from .codebase_archaeologist import CodebaseArchaeologist
            # Get project root (parent of Three_PointO_ArchE directory)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.codebase_archaeologist = CodebaseArchaeologist(
                codebase_root=project_root,
                spr_manager=self.spr_manager
            )
            logger.info("🔍 CodebaseArchaeologist initialized - self-referential synthesis enabled")
            
            # Link archaeologist to action registry
            try:
                from .codebase_archaeology_actions import set_archaeologist
                set_archaeologist(self.codebase_archaeologist)
                logger.info("✅ CodebaseArchaeologist linked to action registry")
            except ImportError:
                logger.warning("Could not link CodebaseArchaeologist to action registry")
        except Exception as e:
            logger.warning(f"Failed to initialize CodebaseArchaeologist: {e}")
            self.codebase_archaeologist = None
        
        logger.info(f"🚀 RISE_Orchestrator initialized successfully")
        logger.info(f"📁 Workflows directory: {self.workflows_dir}")
        logger.info(f"🔧 Workflow engine: {type(self.workflow_engine).__name__}")
        logger.info(f"🧠 SPR Manager: {type(self.spr_manager).__name__}")
        logger.info(f"📝 Thought Trail: {type(self.thought_trail).__name__}")
        self.synergistic_fusion_enabled = perform_scope_limitation_assessment is not None

    def _load_axiomatic_knowledge(self) -> Dict[str, Any]:
        """
        Load the Axiomatic Knowledge Base for Synergistic Fusion Protocol.
        
        Returns:
            Dict containing axiomatic knowledge base
        """
        try:
            axiomatic_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_graph", "axiomatic_knowledge.json")
            with open(axiomatic_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load axiomatic knowledge base: {e}")
            return {}
    
    def _get_available_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Return all available ResonantiA capabilities with descriptions for agent selection"""
        return {
            'ABM': {
                'name': 'Agent-Based Modeling',
                'tool': 'AgentBasedModelingTool',
                'use_for': 'Simulating emergent behavior from agent interactions',
                'inputs': ['agent_definitions', 'environment_config', 'simulation_steps'],
                'outputs': ['simulation_results', 'emergent_patterns', 'time_series_data']
            },
            'CFP': {
                'name': 'Comparative Fluxual Processing',
                'tool': 'CfpFramework',
                'use_for': 'Comparing dynamic evolution of different scenarios',
                'inputs': ['state_vectors', 'hamiltonians', 'observables', 'timeframe'],
                'outputs': ['flux_difference', 'entanglement_correlation', 'trajectory_comparison']
            },
            'CausalInference': {
                'name': 'Causal Inference Analysis',
                'tool': 'CausalInferenceTool',
                'use_for': 'Identifying cause-effect relationships and temporal dependencies',
                'inputs': ['data', 'treatment_variable', 'outcome_variable', 'confounders'],
                'outputs': ['causal_effects', 'confidence_intervals', 'causal_graph']
            },
            'PredictiveModeling': {
                'name': 'Predictive Modeling Tool',
                'tool': 'PredictiveModelingTool',
                'use_for': 'Forecasting future states and trends',
                'inputs': ['historical_data', 'features', 'prediction_horizon'],
                'outputs': ['predictions', 'confidence_intervals', 'feature_importance']
            },
            'PTRF': {
                'name': 'Proactive Truth Resonance Framework',
                'tool': 'PTRFTool',
                'use_for': 'Multi-source verification and truth assessment',
                'inputs': ['claims', 'sources', 'context'],
                'outputs': ['truth_scores', 'confidence_levels', 'evidence_summary']
            },
            'FederatedSearch': {
                'name': 'Federated Search Across Multiple Agents',
                'tool': 'SynergisticInquiryOrchestrator',
                'use_for': 'Comprehensive multi-source research',
                'inputs': ['query', 'agent_types', 'max_results_per_agent'],
                'outputs': ['multi_source_results', 'synthesized_insights']
            },
            'CodeGeneration': {
                'name': 'Custom Code Generation',
                'tool': 'generate_text_llm + execute_code',
                'use_for': 'Creating custom analysis tools when standard tools insufficient',
                'inputs': ['tool_specification', 'requirements'],
                'outputs': ['executable_code', 'validation_results']
            }
        }
    
    def _get_recommended_capabilities(self, problem_description: str) -> List[str]:
        """Get recommended capabilities based on problem description"""
        problem_lower = problem_description.lower()
        recommended = []
        
        if any(term in problem_lower for term in ['simulation', 'emergent', 'agent', 'modeling']):
            recommended.append('ABM')
        if any(term in problem_lower for term in ['compare', 'trajectory', 'evolution', 'flux']):
            recommended.append('CFP')
        if any(term in problem_lower for term in ['causal', 'cause', 'effect']):
            recommended.append('CausalInference')
        if any(term in problem_lower for term in ['predict', 'forecast', 'future']):
            recommended.append('PredictiveModeling')
        if any(term in problem_lower for term in ['truth', 'verify', 'fact']):
            recommended.append('PTRF')
        if any(term in problem_lower for term in ['search', 'find', 'research']):
            recommended.append('FederatedSearch')
            
        return recommended if recommended else ['FederatedSearch']

    # --- SPR Discovery & Normalization Preprocessor ---
    def _build_spr_index(self) -> Dict[str, Any]:
        """Build a lightweight index from the Knowledge Tapestry for fuzzy SPR detection."""
        # Prefer the same JSON used by default path detection
        try_paths = [
            os.path.join(os.path.dirname(__file__), "..", "knowledge_graph", "spr_definitions_tv.json"),
        ]
        spr_list = None
        for p in try_paths:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    spr_list = json.load(f)
                    break
            except Exception:
                continue
        if not spr_list:
            return {}

        # Build forms -> canonical spr_id
        index = {}
        def norm(s: str) -> str:
            return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in s).split())

        for spr in spr_list:
            sid = spr.get("spr_id") or spr.get("id")
            term = spr.get("term", "")
            aliases = spr.get("aliases", []) if isinstance(spr.get("aliases"), list) else []
            # Skip axioms or entries explicitly hidden from SPR index
            if (
                str(spr.get("category", "")).lower() in {"axiom", "axiomatic", "axiomaticknowledge"}
                or spr.get("is_axiom") is True
                or spr.get("hidden_from_spr_index") is True
            ):
                continue
            if not isinstance(sid, str):
                continue
            forms = set()
            forms.add(sid)
            forms.add(term)
            for a in aliases:
                forms.add(a)

            # Add decomposed forms (split camel-ish by capital boundaries)
            def decamel(s: str) -> str:
                buf = []
                prev_upper = False
                for ch in s:
                    if ch.isupper() and not prev_upper:
                        buf.append(" ")
                    buf.append(ch)
                    prev_upper = ch.isupper()
                return "".join(buf)

            forms.add(decamel(sid))
            # Normalize all forms
            norm_forms = {norm(f) for f in forms if isinstance(f, str) and f}
            for nf in norm_forms:
                if not nf:
                    continue
                # Prefer first seen canonical; do not overwrite unless empty
                index.setdefault(nf, sid)
        return index

    def _detect_and_normalize_sprs_in_text(self, text: str) -> Dict[str, Any]:
        """Detect likely SPR mentions in free text (voice transcriptions, informal prompts) and produce hints.

        Returns: { detected: [spr_id...], normalized_text: str, map: [{match, spr_id}] }
        """
        if not text or not self._spr_index:
            return {"detected": [], "normalized_text": text, "map": []}

        # Normalize input for matching
        def norm(s: str) -> str:
            return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in s).split())

        ntext = norm(text)
        detected = []
        mappings = []

        # Greedy phrase scan: try all index keys that are substrings of normalized text
        # (fast, but safe given small index size). For better scale, use trie/ahocorasick.
        for form, sid in self._spr_index.items():
            if not form or len(form) < 3:
                continue
            if form in ntext:
                if sid not in detected:
                    detected.append(sid)
                    mappings.append({"form": form, "spr_id": sid})

        # Produce a light-touch normalized text by appending a hint footer instead of in-place edits
        if detected:
            hint = "\n\n[SPR_HINTS]: " + ", ".join(sorted(detected))
            normalized_text = text + hint
        else:
            normalized_text = text

        return {"detected": detected, "normalized_text": normalized_text, "map": mappings}

    def perform_synergistic_fusion(self, rise_state: RISEState, current_thought: str, action_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform Synergistic Fusion Protocol integration.
        
        Args:
            rise_state: Current RISE state
            current_thought: Current thought process
            action_inputs: Proposed action inputs
            
        Returns:
            Dict containing synergistic fusion results
        """
        if not self.synergistic_fusion_enabled or perform_scope_limitation_assessment is None:
            return {"synergistic_fusion_applied": False, "reason": "Protocol not available"}
        
        try:
            # Perform scope limitation assessment
            context = {
                "problem_description": rise_state.problem_description,
                "current_phase": rise_state.current_phase,
                "session_knowledge_base": rise_state.session_knowledge_base
            }
            
            scope_assessment = perform_scope_limitation_assessment(
                rise_state.problem_description,
                current_thought,
                action_inputs,
                context
            )
            
            # Update RISE state with scope assessment
            rise_state.scope_limitation_assessment = scope_assessment
            
            # Check if axiomatic activation is needed
            if scope_assessment.get("axiomatic_activation_needed"):
                relevant_axiom_ids = scope_assessment.get("relevant_axioms", [])
                activated_axioms = get_relevant_axioms(relevant_axiom_ids)
                
                # Update RISE state with activated axioms
                rise_state.activated_axioms = list(activated_axioms.values())
                
                # Perform synergistic synthesis
                synergistic_result = self._perform_synergistic_synthesis(
                    rise_state, current_thought, action_inputs, activated_axioms
                )
                
                rise_state.synergistic_synthesis = synergistic_result
                
                logger.info(f"Synergistic Fusion Protocol activated with {len(activated_axioms)} axioms")
                
                return {
                    "synergistic_fusion_applied": True,
                    "scope_limitation_detected": True,
                    "activated_axioms": list(activated_axioms.keys()),
                    "synergistic_potential": scope_assessment.get("synergistic_potential"),
                    "synergistic_result": synergistic_result
                }
            else:
                logger.debug("No scope limitation detected, proceeding with standard analysis")
                return {
                    "synergistic_fusion_applied": False,
                    "scope_limitation_detected": False,
                    "reason": "No scope limitation detected"
                }
                
        except Exception as e:
            logger.error(f"Error in synergistic fusion: {e}")
            return {
                "synergistic_fusion_applied": False,
                "error": str(e),
                "reason": "Error in synergistic fusion protocol"
            }

    def _perform_synergistic_synthesis(self, rise_state: RISEState, current_thought: str, action_inputs: Dict[str, Any], activated_axioms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform synergistic synthesis combining scientific reasoning with axiomatic guidance.
        
        Args:
            rise_state: Current RISE state
            current_thought: Current thought process
            action_inputs: Proposed action inputs
            activated_axioms: Activated axioms from the knowledge base
            
        Returns:
            Dict containing synergistic synthesis results
        """
        try:
            synthesis_result = {
                "synthesis_timestamp": datetime.now().isoformat(),
                "original_thought": current_thought,
                "original_action_inputs": action_inputs,
                "activated_axioms": list(activated_axioms.keys()),
                "axiomatic_guidance": {},
                "enhanced_thought": current_thought,
                "enhanced_action_inputs": action_inputs.copy(),
                "synergistic_effects": []
            }
            
            # Apply axiomatic guidance for each activated axiom
            for axiom_id, axiom_data in activated_axioms.items():
                axiom_guidance = self._apply_axiomatic_guidance(
                    axiom_data, current_thought, action_inputs, rise_state
                )
                synthesis_result["axiomatic_guidance"][axiom_id] = axiom_guidance
                
                # Enhance thought process and action inputs based on axiom
                enhanced_components = self._enhance_with_axiom(
                    axiom_data, current_thought, action_inputs
                )
                
                synthesis_result["enhanced_thought"] = enhanced_components["enhanced_thought"]
                synthesis_result["enhanced_action_inputs"].update(enhanced_components["enhanced_action_inputs"])
                synthesis_result["synergistic_effects"].append(enhanced_components["synergistic_effect"])
            
            return synthesis_result
            
        except Exception as e:
            logger.error(f"Error in synergistic synthesis: {e}")
            return {
                "error": str(e),
                "synthesis_failed": True
            }

    def _apply_axiomatic_guidance(self, axiom_data: Dict[str, Any], current_thought: str, action_inputs: Dict[str, Any], rise_state: RISEState) -> Dict[str, Any]:
        """
        Apply specific axiomatic guidance to the current thought and action.
        
        Args:
            axiom_data: The axiom data to apply
            current_thought: Current thought process
            action_inputs: Proposed action inputs
            rise_state: Current RISE state
            
        Returns:
            Dict containing applied guidance
        """
        guidance = {
            "axiom_id": axiom_data.get("axiom_id"),
            "core_principle": axiom_data.get("core_principle"),
            "applied_guidance": {},
            "enhancement_notes": []
        }
        
        # Apply specific guidance based on axiom type
        if axiom_data.get("axiom_id") == "ResonantgratidsouL":
            # Apply gratitude frequency and grace mechanism
            guidance["applied_guidance"]["gratitude_assessment"] = "Evaluate solution for acknowledgment of all stakeholders"
            guidance["applied_guidance"]["grace_mechanism"] = "Extend understanding beyond strict merit-based calculations"
            guidance["applied_guidance"]["divine_intent"] = "Align with higher purpose and collective well-being"
            guidance["enhancement_notes"].append("Enhanced with spiritual technology principles")
            
        elif axiom_data.get("axiom_id") == "HumanDignityInviolable":
            # Apply human dignity preservation
            guidance["applied_guidance"]["dignity_preservation"] = "Ensure all actions preserve and enhance human dignity"
            guidance["enhancement_notes"].append("Enhanced with human dignity considerations")
            
        elif axiom_data.get("axiom_id") == "CollectiveWellbeing":
            # Apply collective well-being optimization
            guidance["applied_guidance"]["collective_optimization"] = "Optimize for collective benefit while respecting individual rights"
            guidance["enhancement_notes"].append("Enhanced with collective well-being considerations")
            
        elif axiom_data.get("axiom_id") == "TruthPursuitMoral":
            # Apply truth-seeking commitment
            guidance["applied_guidance"]["truth_commitment"] = "Maintain intellectual honesty and truth-seeking protocols"
            guidance["enhancement_notes"].append("Enhanced with truth-seeking commitment")
        
        return guidance

    def _enhance_with_axiom(self, axiom_data: Dict[str, Any], current_thought: str, action_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance thought process and action inputs with axiomatic guidance.
        
        Args:
            axiom_data: The axiom data to apply
            current_thought: Current thought process
            action_inputs: Proposed action inputs
            
        Returns:
            Dict containing enhanced components
        """
        enhanced_thought = current_thought
        enhanced_action_inputs = action_inputs.copy()
        synergistic_effect = f"Enhanced with {axiom_data.get('name', 'axiom')} principles"
        
        # Apply specific enhancements based on axiom
        if axiom_data.get("axiom_id") == "ResonantgratidsouL":
            enhanced_thought += "\n\nAxiomatic Enhancement: Considering gratitude frequency, grace mechanism, and divine intent alignment in this analysis."
            enhanced_action_inputs["axiomatic_guidance"] = "ResonantgratidsouL"
            synergistic_effect = "Spiritual technology principles enhance ethical decision-making"
            
        elif axiom_data.get("axiom_id") == "HumanDignityInviolable":
            enhanced_thought += "\n\nAxiomatic Enhancement: Ensuring all proposed actions preserve and enhance human dignity."
            enhanced_action_inputs["dignity_check"] = True
            synergistic_effect = "Human dignity preservation enhances ethical framework"
            
        elif axiom_data.get("axiom_id") == "CollectiveWellbeing":
            enhanced_thought += "\n\nAxiomatic Enhancement: Optimizing for collective benefit while respecting individual rights."
            enhanced_action_inputs["collective_impact_assessment"] = True
            synergistic_effect = "Collective well-being optimization enhances strategic outcomes"
            
        elif axiom_data.get("axiom_id") == "TruthPursuitMoral":
            enhanced_thought += "\n\nAxiomatic Enhancement: Maintaining intellectual honesty and truth-seeking protocols."
            enhanced_action_inputs["truth_validation"] = True
            synergistic_effect = "Truth-seeking commitment enhances analytical rigor"
        
        return {
            "enhanced_thought": enhanced_thought,
            "enhanced_action_inputs": enhanced_action_inputs,
            "synergistic_effect": synergistic_effect
        }
    
    def emit_sirc_event(self, phase: str, message: str, metadata: Dict[str, Any] = None) -> None:
        """Emit SIRC (Synergistic Intent Resonance Cycle) events for UI visualization"""
        sirc_event = {
            "type": "sirc_event",
            "phase": phase,
            "message": message,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        print(f"SIRC_JSON: {json.dumps(sirc_event)}")
        print(f"🔄 SIRC {phase}: {message}")
        sys.stdout.flush()

    def process_query(self, problem_description: str, context: Dict[str, Any] = None, model: str = None, workflow_name: str = None) -> Dict[str, Any]:
        """
        Main entry point for RISE v2.0 workflow execution
        
        Args:
            problem_description: The problem to be solved
            context: Optional context from the CognitiveIntegrationHub
            model: Optional model name to be used by LLM tools
            workflow_name: Optional name of the workflow blueprint to use for Phase A
            
        Returns:
            Complete execution results including final strategy and SPR
        """
        self.session_id = f"rise_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        self.thought_trail.session_id = self.session_id
        
        logger.info(f"🚀 Initiating RISE v2.0 workflow for session {self.session_id}")
        logger.info(f"Problem: {problem_description}...")
        
        # --- NEW: Context-Aware Initialization ---
        # The context from the CognitiveIntegrationHub can now influence the entire RISE process.
        self.execution_mode = context.get("execution_mode", "standard_rise") if context else "standard_rise"
        self.initial_query_analysis = context.get("initial_query_analysis") if context else None
        
        logger.info(f"RISE Execution Mode: {self.execution_mode}")
        if self.initial_query_analysis:
            logger.info("RISE process initiated with pre-analyzed query context.")
        # --- END: Context-Aware Initialization ---

        self.thought_trail.add_entry({
            "task_id": "RISE_INIT",
            "action_type": "Orchestration",
            "inputs": {"problem": problem_description},
            "outputs": {},
            "iar_reflection": {"status": "Initiated"}
        })

        # NEW: Preprocess prompt for SPR detection/normalization (handles voice/loose text)
        try:
            spr_scan = self._detect_and_normalize_sprs_in_text(problem_description)
            if spr_scan.get('detected'):
                logger.info(f"SPR pre-detect: {spr_scan['detected']}")
                # Augment problem description with SPR hints (non-destructive)
                problem_description = spr_scan.get('normalized_text', problem_description)
        except Exception as e:
            logger.warning(f"SPR pre-detection failed: {e}")
        
        # Initialize RISE state
        rise_state = RISEState(
            problem_description=problem_description,
            session_id=self.session_id,
            current_phase="A",
            phase_start_time=datetime.now(timezone.utc),
            session_knowledge_base={},
            specialized_agent=None,
            advanced_insights=[],
            specialist_consultation=None,
            fused_strategic_dossier=None,
            vetting_dossier=None,
            final_strategy=None,
            spr_definition=None,
            execution_metrics={
                'total_duration': 0,
                'phase_durations': {},
                'success_rate': 0.0,
                'confidence_score': 0.0
            },
            # Initialize Synergistic Fusion Protocol additions
            scope_limitation_assessment=None,
            activated_axioms=[],
            synergistic_synthesis=None,
            # Initialize Utopian Solution Synthesizer additions
            utopian_trust_packet=None
        )
        
        self.active_sessions[self.session_id] = rise_state
        
        final_return_value = {} # Ensure this is always defined
        try:
            # === PHASE A: Knowledge Scaffolding & Dynamic Specialization ===
            self.emit_sirc_event("Phase_A_Start", "Knowledge Scaffolding & Dynamic Specialization")
            logger.info("🔍 Phase A: Acquiring domain knowledge and forging specialist agent (Enhanced)")
            
            # Determine provider and model - check context, then config, then defaults
            from .config import get_config
            config_obj = get_config()
            
            # Provider selection priority: context parameter > config default > environment variable > "groq" (default)
            effective_provider = context.get("provider") if context else None
            if not effective_provider:
                # AppConfig uses 'llm' not 'llm_config'
                # Default to "groq" but allow override via config/env for Gemini/Google
                effective_provider = config_obj.llm.default_provider if hasattr(config_obj, 'llm') and hasattr(config_obj.llm, 'default_provider') else os.getenv("ARCHE_LLM_PROVIDER", "groq")
            
            # Model selection priority: explicit parameter > config default for provider > provider's default
            if model:
                effective_model = model
            else:
                # AppConfig uses 'llm' not 'llm_config'
                # Default to Groq model but allow override via config/env
                effective_model = config_obj.llm.default_model if hasattr(config_obj, 'llm') and hasattr(config_obj.llm, 'default_model') else os.getenv("ARCHE_LLM_MODEL", None)
                
                # If no model specified, get provider-specific default
                from .llm_providers import get_model_for_provider
                provider_default_model = get_model_for_provider(effective_provider)
                
                if not effective_model:
                    # No model in config/env, use provider default
                    effective_model = provider_default_model
                elif effective_provider == "groq" and "llama" not in effective_model.lower() and "groq" not in effective_model.lower():
                    # If provider is Groq but model doesn't match, use Groq default
                    effective_model = provider_default_model
                elif effective_provider == "google" and "gemini" not in effective_model.lower():
                    # If provider is Google but model doesn't match, use Google default
                    effective_model = provider_default_model
                elif effective_provider == "cursor" and "cursor" not in effective_model.lower():
                    # If provider is Cursor but model doesn't match, use Cursor default
                    effective_model = provider_default_model
            
            # Store in rise_state for access in later phases
            rise_state.effective_model = effective_model
            rise_state.effective_provider = effective_provider
            
            logger.info(f"📡 RISE LLM Provider: {effective_provider} | Model: {effective_model}")
            
            phase_a_context = {
                "problem_description": problem_description,  # Must match workflow input key
                "user_query": problem_description,  # Also keep for compatibility
                "session_id": self.session_id,
                "model": effective_model,  # Pass model to the context for use in the workflow
                "provider": effective_provider,  # Pass provider to use Cursor ArchE
                # Pass the rich initial analysis into the workflow context if it exists
                "initial_query_analysis": self.initial_query_analysis
            }

            # --- DYNAMIC WORKFLOW SELECTION (from new architecture) ---
            # If the resonantia_playbook mode is active, the hub has generated a dynamic
            # workflow and told us where to find it.
            if self.execution_mode == "resonantia_playbook" and context:
                phase_a_workflow = context.get("phase_a_workflow_blueprint")
                # We also need to temporarily point the workflow engine to where the plan is
                workflows_dir_override = context.get("workflows_dir_override")
                if phase_a_workflow and workflows_dir_override:
                    logger.info(f"Using dynamically generated Phase A workflow from ResonantiA path: {phase_a_workflow}")
                    # Use a temporary engine instance for this dynamic execution
                    dynamic_engine = IARCompliantWorkflowEngine(workflows_dir=workflows_dir_override)
                    phase_a_results = dynamic_engine.run_workflow(
                        f"{phase_a_workflow}", # The filename should not have .json here
                        initial_context=phase_a_context
                    )
                else:
                    logger.warning("ResonantiA mode active but dynamic workflow blueprint is missing. Falling back.")
                    # Fallback to default if blueprint is missing
                    phase_a_workflow = f"{workflow_name}.json" if workflow_name else "knowledge_scaffolding.json"
                    phase_a_results = self.workflow_engine.run_workflow(
                        phase_a_workflow,
                        initial_context=phase_a_context
                    )
            else:
                # Default behavior: use the specified or default workflow
                phase_a_workflow = f"{workflow_name}.json" if workflow_name else "knowledge_scaffolding.json"
                logger.info(f"Using Phase A workflow: {phase_a_workflow}")
                phase_a_results = self.workflow_engine.run_workflow(
                    phase_a_workflow,
                    initial_context=phase_a_context
                )
            # --- END: DYNAMIC WORKFLOW SELECTION ---
            
            # --- ROBUST OUTPUT INTEGRATION & STATUS CHECK (REVISED) ---
            if phase_a_results.get("workflow_status") != "Completed Successfully":
                logger.error(f"Phase A workflow did not complete successfully. Status: {phase_a_results.get('workflow_status')}")
                raise RuntimeError("Phase A workflow failed to complete.", phase_a_results)
            
            # Extract the key outputs from the workflow results and populate the RISE state.
            # The workflow engine resolves the 'outputs' section and places them in runtime_context.
            if phase_a_results.get("workflow_status") == "Completed Successfully":
                # Access the resolved outputs directly from the results
                # Ensure values are properly typed (parse JSON strings if needed)
                specialized_agent_raw = phase_a_results.get("specialized_agent")
                if isinstance(specialized_agent_raw, str):
                    try:
                        import json
                        specialized_agent_raw = json.loads(specialized_agent_raw)
                    except (json.JSONDecodeError, ValueError):
                        pass  # Keep as string if not JSON
                rise_state.specialized_agent = specialized_agent_raw
                
                session_kb_raw = phase_a_results.get("session_knowledge_base")
                if isinstance(session_kb_raw, str):
                    try:
                        import json
                        session_kb_raw = json.loads(session_kb_raw)
                    except (json.JSONDecodeError, ValueError):
                        # If it's not JSON, create a dict wrapper
                        session_kb_raw = {"raw_data": session_kb_raw}
                elif session_kb_raw is None:
                    session_kb_raw = {}
                elif not isinstance(session_kb_raw, dict):
                    # Convert non-dict, non-string to dict
                    session_kb_raw = {"raw_data": str(session_kb_raw)}
                rise_state.session_knowledge_base = session_kb_raw
                
                if rise_state.specialized_agent:
                    logger.info("Successfully integrated specialized_agent into RISE state.")
                else:
                    logger.warning("specialized_agent not found in Phase A results.")
                    
                if rise_state.session_knowledge_base:
                    logger.info("Successfully integrated session_knowledge_base into RISE state.")
                else:
                    logger.warning("session_knowledge_base not found in Phase A results.")
            else:
                logger.error(f"Phase A workflow did not complete successfully. Status: {phase_a_results.get('workflow_status')}")
                raise RuntimeError("Phase A workflow failed to complete.", phase_a_results)

            self.thought_trail.add_entry({
                "task_id": "PHASE_A_COMPLETE", 
                "action_type": "Orchestration", 
                "inputs": {"workflow": phase_a_workflow}, 
                "outputs": phase_a_results, 
                "iar_reflection": {"status": "Completed"}
            })
            logger.info(f"✅ Knowledge scaffolding workflow completed successfully")

            # --- CRITICAL VALIDATION (State Hardening) ---
            if rise_state.specialized_agent is None:
                raise RuntimeError("Phase A failed to produce a specialized_agent. Halting workflow.")
            
            # Execute Phase B: Fused Insight Generation
            logger.info("🔄 Phase B: Fused Insight Generation")
            self.emit_sirc_event("Phase_B_Start", "Fused Insight Generation - Parallel Pathway Analysis", {
                "specialized_agent": rise_state.specialized_agent,
                "pathways": ["Causal Analysis", "Simulation (ABM)", "Comparative Fluxual", "Specialist Consultation"]
            })
            phase_b_result = self._execute_phase_b(rise_state)
            rise_state.advanced_insights = phase_b_result.get('advanced_insights', [])
            rise_state.specialist_consultation = phase_b_result.get('specialist_consultation')
            rise_state.fused_strategic_dossier = phase_b_result.get('fused_strategic_dossier')

            # --- CRITICAL VALIDATION (State Hardening) ---
            if rise_state.fused_strategic_dossier is None:
                raise RuntimeError("Phase B failed to produce a fused_strategic_dossier. Halting workflow.")
            
            # Execute Phase C: Fused Strategy Generation & Finalization
            logger.info("🔄 Phase C: Fused Strategy Generation & Finalization")
            self.emit_sirc_event("Phase_C_Start", "Fused Strategy Generation & High-Stakes Vetting", {
                "fused_dossier_available": bool(rise_state.fused_strategic_dossier),
                "fused_dossier_length": len(rise_state.fused_strategic_dossier) if rise_state.fused_strategic_dossier else 0
            })
            phase_c_result = self._execute_phase_c(rise_state)
            rise_state.vetting_dossier = phase_c_result.get('vetting_dossier')
            rise_state.final_strategy = phase_c_result.get('final_strategy')
            rise_state.spr_definition = phase_c_result.get('spr_definition')

            # --- CRITICAL VALIDATION (State Hardening) ---
            if rise_state.final_strategy is None:
                raise RuntimeError("Phase C failed to produce a final_strategy. Halting workflow.")
            
            # Execute Phase D: Utopian Vetting & Refinement (NEW)
            logger.info("🔄 Phase D: Utopian Vetting & Refinement")
            self.emit_sirc_event("Phase_D_Start", "Utopian Vetting & Refinement - Synergistic Fusion Protocol", {
                "vetting_status": "active",
                "axiom_integration": "pending"
            })
            logger.info("🔄 Phase D: Utopian Vetting & Refinement")
            phase_d_result = self._execute_phase_d(rise_state)
            rise_state.final_strategy = phase_d_result.get('refined_utopian_strategy', rise_state.final_strategy)
            rise_state.utopian_trust_packet = phase_d_result.get('trust_packet')
            
            # NEW: Iterative Looping - Check if new insights from codebase synthesis require looping
            max_iterations = 3  # Prevent infinite loops
            current_iteration = 0
            
            # Iterative loop: Continue refining if codebase synthesis reveals new insights
            while current_iteration < max_iterations:
                should_continue_loop = False
                
                # Check if codebase synthesis revealed insights requiring re-analysis
                if self.codebase_archaeologist and current_iteration == 0:
                    # First check after Phase D
                    codebase_synthesis = phase_b_result.get('codebase_synthesis') or {}
                elif self.codebase_archaeologist and current_iteration > 0:
                    # Subsequent iterations - check latest Phase B result
                    codebase_synthesis = phase_b_result.get('codebase_synthesis') or {}
                else:
                    codebase_synthesis = {}
                
                novel_combinations = codebase_synthesis.get('novel_combinations', [])
                implementation_suggestions = codebase_synthesis.get('implementation_suggestions', [])
                
                # Trigger loop if novel combinations found or significant implementation suggestions
                should_continue_loop = (
                    len(novel_combinations) > 0 and 
                    len(implementation_suggestions) > 2 and
                    current_iteration < max_iterations - 1  # Allow one more iteration
                )
                
                if not should_continue_loop:
                    break  # No more iterations needed
                
                current_iteration += 1
                logger.info(f"🔄 Iterative Loop {current_iteration}/{max_iterations}: {len(novel_combinations)} novel combinations, {len(implementation_suggestions)} implementation suggestions")
                logger.info(f"   Re-running Phase B→C with codebase synthesis insights")
                
                # Update knowledge base with new insights
                if 'codebase_patterns' not in rise_state.session_knowledge_base:
                    rise_state.session_knowledge_base['codebase_patterns'] = []
                
                # Add novel combinations as new search patterns
                for combination in novel_combinations[:3]:  # Top 3
                    rise_state.session_knowledge_base['codebase_patterns'].append({
                        "type": "novel_combination",
                        "description": combination.get('description', ''),
                        "components": combination.get('codebase_components', []),
                        "iteration": current_iteration
                    })
                
                # Re-execute Phase B with enhanced knowledge base
                phase_b_result = self._execute_phase_b(rise_state)
                rise_state.advanced_insights = phase_b_result.get('advanced_insights', [])
                rise_state.specialist_consultation = phase_b_result.get('specialist_consultation')
                rise_state.fused_strategic_dossier = phase_b_result.get('fused_strategic_dossier')
                
                # Re-execute Phase C with updated dossier
                phase_c_result = self._execute_phase_c(rise_state)
                rise_state.vetting_dossier = phase_c_result.get('vetting_dossier')
                rise_state.final_strategy = phase_c_result.get('final_strategy')
                
                logger.info(f"✅ Iterative loop {current_iteration} completed - refined strategy with codebase synthesis")
            
            if current_iteration > 0:
                logger.info(f"🔄 Completed {current_iteration} iterative refinement loop(s)")
            
            # Calculate final metrics
            end_time = datetime.now(timezone.utc)
            total_duration = (end_time - rise_state.phase_start_time).total_seconds()
            rise_state.execution_metrics['total_duration'] = total_duration
            
            # Generate final results
            final_results = {
                'session_id': self.session_id,
                'problem_description': problem_description,
                'execution_status': 'completed',
                'total_duration': total_duration,
                'phase_results': {
                    'phase_a': phase_a_results,
                    'phase_b': phase_b_result,
                    'phase_c': phase_c_result,
                    'phase_d': phase_d_result
                },
                'final_strategy': rise_state.final_strategy,
                'spr_definition': rise_state.spr_definition,
                'execution_metrics': rise_state.execution_metrics,
                'thought_trail': self.thought_trail.get_recent_entries(10) if self.thought_trail else [],
                'timestamp': end_time.isoformat()
            }
            
            # Record in execution history
            final_strategy_confidence = 0.0
            if rise_state.final_strategy:
                # Check if final_strategy is a dict before calling .get()
                if isinstance(rise_state.final_strategy, dict):
                    final_strategy_confidence = rise_state.final_strategy.get('confidence', 0.0)
                elif isinstance(rise_state.final_strategy, str):
                    # If it's a string, we can extract a confidence value if it's embedded
                    # For now, default to a safe value
                    final_strategy_confidence = 0.5
            
            self.execution_history.append({
                'session_id': self.session_id,
                'timestamp': end_time.isoformat(),
                'problem_description': problem_description,
                'success': True,
                'duration': total_duration,
                'final_strategy_confidence': final_strategy_confidence
            })
            
            # === PHASE E: Execution-Based Answering (NEW) ===
            # If query qualifies, execute the plan using ArchE tools
            execution_answer = None
            execution_results = None
            execution_plan = None
            qualification = None
            
            # Initialize RISE execution plan tracking
            rise_execution_plan = {
                'query': problem_description,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'session_id': self.session_id,
                'rise_phases': {
                    'phase_a': {'status': 'completed', 'workflow': phase_a_workflow},
                    'phase_b': {'status': 'completed'},
                    'phase_c': {'status': 'completed'},
                    'phase_d': {'status': 'completed'}
                },
                'tasks': [],
                'selected_tools': [],
                'actions_taken': [],
                'fallbacks_used': [],
                'execution_order': [],
                'errors': []
            }
            
            try:
                from .rise_execution_phase import RISEExecutionPhase
                from .action_registry import main_action_registry
                
                execution_phase = RISEExecutionPhase(
                    workflow_engine=self.workflow_engine,
                    action_registry=main_action_registry,
                    spr_manager=self.spr_manager
                )
                
                # Check if query qualifies for execution-based answering
                qualification = execution_phase.qualify_query_for_execution(
                    query=problem_description,
                    context=context
                )
                
                if qualification.get('qualifies', False):
                    logger.info(f"🔧 Phase E: Query qualifies for execution-based answering")
                    logger.info(f"   Complexity: {qualification.get('execution_complexity')}")
                    logger.info(f"   Recommended tools: {qualification.get('recommended_tools')}")
                    
                    # Track recommended tools
                    rise_execution_plan['selected_tools'] = qualification.get('recommended_tools', [])
                    rise_execution_plan['rise_phases']['phase_e'] = {
                        'status': 'qualified',
                        'complexity': qualification.get('execution_complexity'),
                        'recommended_tools': qualification.get('recommended_tools', [])
                    }
                    
                    # Generate execution plan from final strategy
                    execution_plan = execution_phase.generate_execution_plan(
                        query=problem_description,
                        strategy=rise_state.final_strategy,
                        context={
                            'provider': effective_provider,
                            'model': effective_model,
                            'original_query': problem_description
                        }
                    )
                    
                    # Track execution plan steps
                    if execution_plan.get('execution_steps'):
                        for idx, step in enumerate(execution_plan.get('execution_steps', []), 1):
                            task_id = step.get('step_id', f"step_{idx}")
                            rise_execution_plan['tasks'].append({
                                'task_id': task_id,
                                'tool': step.get('tool', 'unknown'),
                                'description': step.get('description', ''),
                                'order': idx,
                                'status': 'pending',
                                'inputs': step.get('inputs', {}),
                                'expected_output': step.get('expected_output', '')
                            })
                            rise_execution_plan['execution_order'].append(task_id)
                        
                        # Execute the plan
                        execution_results = execution_phase.execute_plan(
                            execution_plan=execution_plan,
                            context={
                                'provider': effective_provider,
                                'model': effective_model,
                                'original_query': problem_description,
                                'strategy': rise_state.final_strategy
                            }
                        )
                        
                        # Track execution results
                        if execution_results:
                            execution_steps = execution_results.get('execution_steps', [])
                            for step_result in execution_steps:
                                task_id = step_result.get('step_id', 'unknown')
                                # Update task status
                                for task in rise_execution_plan['tasks']:
                                    if task['task_id'] == task_id:
                                        task['status'] = 'completed' if step_result.get('success') else 'failed'
                                        break
                                
                                # Track action taken
                                rise_execution_plan['actions_taken'].append({
                                    'task_id': task_id,
                                    'action': step_result.get('tool', 'unknown'),
                                    'result': 'success' if step_result.get('success') else 'failed',
                                    'output_preview': str(step_result.get('result', ''))[:200] if step_result.get('result') else ''
                                })
                                
                                # Track errors
                                if not step_result.get('success'):
                                    rise_execution_plan['errors'].append({
                                        'task_id': task_id,
                                        'error_type': 'ExecutionError',
                                        'error_message': step_result.get('error', 'Unknown error')
                                    })
                        
                        execution_answer = execution_results.get('final_answer', '')
                        rise_execution_plan['rise_phases']['phase_e']['status'] = 'completed'
                        logger.info(f"✅ Phase E completed - Generated execution-based answer ({len(execution_answer)} chars)")
                    else:
                        logger.warning("⚠️ Phase E: Execution plan generation failed or returned no steps")
                        rise_execution_plan['rise_phases']['phase_e']['status'] = 'failed'
                        rise_execution_plan['errors'].append({
                            'task_id': 'phase_e_plan_generation',
                            'error_type': 'PlanGenerationError',
                            'error_message': 'Execution plan generation failed or returned no steps'
                        })
                        if execution_plan and execution_plan.get('error'):
                            rise_execution_plan['fallbacks_used'].append({
                                'stage': 'phase_e_plan_generation',
                                'reason': execution_plan.get('error', 'Unknown error'),
                                'fallback_action': 'skip_execution'
                            })
                else:
                    logger.info(f"ℹ️ Phase E: Query does not qualify for execution-based answering: {qualification.get('reason')}")
                    rise_execution_plan['rise_phases']['phase_e'] = {
                        'status': 'not_qualified',
                        'reason': qualification.get('reason', 'Unknown')
                    }
                    
            except Exception as e:
                logger.warning(f"⚠️ Phase E (Execution) failed: {e}")
                # Don't fail the entire workflow if execution phase fails
                execution_answer = None
                execution_results = {'error': str(e)}
                rise_execution_plan['rise_phases']['phase_e'] = {
                    'status': 'error',
                    'error': str(e)
                }
                rise_execution_plan['errors'].append({
                    'task_id': 'phase_e_execution',
                    'error_type': 'Exception',
                    'error_message': str(e)
                })
            
            # Save RISE execution plan to file
            try:
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                playbooks_dir = os.path.join(project_root, "outputs", "query_executions", "playbooks")
                os.makedirs(playbooks_dir, exist_ok=True)
                
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                filename = f"rise_execution_plan_{timestamp}.json"
                filepath = os.path.join(playbooks_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(rise_execution_plan, f, indent=2, default=str)
                
                logger.info(f"📋 RISE execution plan saved to: {filepath}")
            except Exception as e:
                logger.warning(f"Failed to save RISE execution plan: {e}")
            
            logger.info(f"✅ RISE v2.0 workflow completed successfully for session {self.session_id}")
            logger.info(f"Total duration: {total_duration:.2f}s")
            
            # Add execution results to final output
            final_results['execution_phase'] = {
                'qualification': qualification if 'qualification' in locals() else None,
                'execution_results': execution_results,
                'execution_answer': execution_answer,
                'execution_plan': execution_plan
            }
            
            # Add RISE execution plan to final results
            final_results['rise_execution_plan'] = rise_execution_plan
            
            # If we have an execution answer, use it as the primary response
            if execution_answer:
                final_results['final_answer'] = execution_answer
                logger.info(f"📝 Final answer generated from execution phase ({len(execution_answer)} chars)")
            elif isinstance(rise_state.final_strategy, str):
                # Fallback to strategy if no execution answer
                final_results['final_answer'] = rise_state.final_strategy
            elif isinstance(rise_state.final_strategy, dict):
                # Extract text from strategy dict
                final_results['final_answer'] = rise_state.final_strategy.get('strategy_text', str(rise_state.final_strategy))
            
            final_return_value = final_results
            return final_results
            
        except Exception as e:
            logger.error(f"❌ RISE v2.0 workflow failed for session {self.session_id}: {str(e)}")
            
            # Record failure
            end_time = datetime.now(timezone.utc)
            total_duration = (end_time - rise_state.phase_start_time).total_seconds()
            
            # --- NEW: Capture partial results if available from a custom exception ---
            partial_results = e.args[1] if len(e.args) > 1 and isinstance(e.args[1], dict) else {}

            self.execution_history.append({
                'session_id': self.session_id,
                'timestamp': end_time.isoformat(),
                'problem_description': problem_description,
                'success': False,
                'duration': total_duration,
                'error': str(e)
            })
            
            failure_results = {
                'session_id': self.session_id,
                'problem_description': problem_description,
                'execution_status': 'failed',
                'error': str(e),
                'total_duration': total_duration,
                'current_phase': rise_state.current_phase,
                'timestamp': end_time.isoformat(),
                'partial_results': partial_results # Include partial results for debugging
            }
            final_return_value = failure_results
            return failure_results
        
        finally:
            # Clean up active session
            if self.session_id in self.active_sessions:
                del self.active_sessions[self.session_id]

    def _generate_dynamic_workflow(self, problem_description: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate a dynamic workflow using the PlaybookOrchestrator when appropriate.
        
        Args:
            problem_description: The problem/query to analyze
            context: Optional context for workflow generation
            
        Returns:
            Path to the generated dynamic workflow file, or None if not generated
        """
        if not self.playbook_orchestrator:
            return None
        
        try:
            logger.info("🎭 Generating dynamic workflow using PlaybookOrchestrator...")
            
            # Analyze the query for ResonantiA patterns and generate workflow
            dynamic_workflow_plan = self.playbook_orchestrator.analyze_query_for_resonantia_patterns(problem_description)
            
            if not dynamic_workflow_plan:
                logger.warning("PlaybookOrchestrator did not generate a workflow")
                return None
            
            # Save the dynamic workflow to outputs directory
            import time
            from pathlib import Path
            
            outputs_dir = Path("outputs")
            outputs_dir.mkdir(exist_ok=True)
            
            timestamp = int(time.time() * 1000)
            plan_name = dynamic_workflow_plan.get("name", "dynamic_rise_workflow")
            plan_filename = f"dynamic_workflow_{plan_name}_{timestamp}.json"
            plan_filepath = outputs_dir / plan_filename
            
            with open(plan_filepath, 'w', encoding='utf-8') as f:
                import json
                json.dump(dynamic_workflow_plan, f, indent=2)
            
            logger.info(f"✅ Dynamic workflow generated: {plan_filepath}")
            return str(plan_filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate dynamic workflow: {e}", exc_info=True)
            return None
    
    def _execute_federated_search(self, query: str, agent_types: List[str] = None, max_results: int = 5) -> Dict[str, Any]:
        """
        Execute federated search across multiple specialized agents.
        
        Args:
            query: The search query
            agent_types: List of agent types to use (default: all agents)
            max_results: Maximum results per agent
            
        Returns:
            Dictionary of results from each agent
        """
        if not self.federated_agents:
            logger.warning("Federated agents not available, skipping federated search")
            return {}
        
        if agent_types is None:
            agent_types = list(self.federated_agents.keys())
        
        results = {}
        logger.info(f"🔬 Executing federated search across {len(agent_types)} agents")
        
        for agent_type in agent_types:
            if agent_type not in self.federated_agents:
                logger.warning(f"Agent type '{agent_type}' not found in federated agents")
                continue
            
            try:
                agent = self.federated_agents[agent_type]
                agent_results = agent.search(query, max_results=max_results)
                results[agent_type] = agent_results
                logger.info(f"Agent '{agent_type}' found {len(agent_results)} results")
            except Exception as e:
                logger.error(f"Agent '{agent_type}' failed during search: {e}")
                results[agent_type] = []
        
        total_results = sum(len(r) for r in results.values())
        logger.info(f"Federated search complete: {total_results} total results from {len(results)} agents")
        
        return results

    def _execute_phase_a(self, rise_state: RISEState) -> Dict[str, Any]:
        """
        Execute Phase A: Knowledge Scaffolding & Dynamic Specialization with null handling
        
        This phase:
        1. Acquires domain knowledge through web search and analysis
        2. Forges a specialized cognitive agent (SCA) for the domain
        3. Establishes the session knowledge base
        
        Args:
            rise_state: Current RISE execution state
            
        Returns:
            Phase A results including session knowledge base and specialized agent
        """
        phase_start = datetime.now(timezone.utc)
        rise_state.current_phase = "A"
        rise_state.phase_start_time = phase_start
        
        logger.info("🔍 Phase A: Acquiring domain knowledge and forging specialist agent (Enhanced)")
        
        try:
            # Try the simple knowledge scaffolding workflow first
            knowledge_result = None
            try:
                # Use the main Knowledge Scaffolding workflow (not the 'simple' variant)
                ks_path = os.path.join(self.workflows_dir, "knowledge_scaffolding.json")
                knowledge_result = self.workflow_engine.run_workflow(
                    ks_path,
                    {
                        "problem_description": rise_state.problem_description,
                        "session_id": rise_state.session_id,
                        "phase": "A"
                    }
                )
                logger.info("✅ Knowledge scaffolding workflow completed successfully")
            except Exception as e:
                logger.warning(f"⚠️ Knowledge scaffolding workflow failed: {e}")
                
                # Create fallback knowledge base
                fallback_knowledge = {
                    "domain": "Strategic Analysis",
                    "search_results": [],
                    "search_status": "fallback",
                    "fallback_content": f"Domain analysis for Strategic Analysis - using general knowledge base",
                    "problem_analysis": {
                        "deconstruction_text": f"Problem analysis for: {rise_state.problem_description[:200]}...",
                        "core_domains": ["Strategic Analysis"],
                        "key_variables": ["strategic_requirements", "risk_factors"],
                        "success_criteria": ["comprehensive_analysis", "actionable_recommendations"]
                    },
                    "specialization_requirements": {
                        "required_knowledge": ["strategic_analysis", "problem_solving"],
                        "analytical_capabilities": ["critical_thinking", "systems_analysis"],
                        "strategic_patterns": ["holistic_thinking", "risk_assessment"]
                    },
                    "metadata": {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "source": "fallback_generation",
                        "confidence": 0.6
                    }
                }
                
                knowledge_result = {
                    "session_knowledge_base": fallback_knowledge,
                    "metrics": {"fallback_used": True, "error": str(e)}
                }
            
            # Ensure we have a valid session knowledge base
            session_kb = knowledge_result.get('session_knowledge_base', {})
            if not session_kb:
                session_kb = {
                    "domain": "Strategic Analysis",
                    "search_results": [],
                    "search_status": "fallback",
                    "fallback_content": "Using general strategic analysis knowledge"
                }
            
            # NEW: Search codebase for relevant patterns (Self-Referential Synthesis)
            codebase_patterns = []
            if self.codebase_archaeologist:
                try:
                    logger.info("🔍 Phase A: Searching codebase for relevant patterns...")
                    codebase_patterns = self.codebase_archaeologist.search_codebase_for_patterns(
                        query=rise_state.problem_description,
                        pattern_types=["class", "function", "workflow", "spr", "specification"],
                        max_results=15,
                        search_mode="semantic"
                    )
                    
                    # Add codebase patterns to knowledge base
                    if codebase_patterns:
                        if "codebase_patterns" not in session_kb:
                            session_kb["codebase_patterns"] = []
                        session_kb["codebase_patterns"] = [p.to_dict() for p in codebase_patterns]
                        session_kb["codebase_patterns_count"] = len(codebase_patterns)
                        logger.info(f"✅ Found {len(codebase_patterns)} relevant codebase patterns")
                    else:
                        logger.info("ℹ️ No relevant codebase patterns found")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Codebase pattern search failed: {e}")
                    codebase_patterns = []
            
            # Execute metamorphosis protocol to forge specialist agent
            metamorphosis_result = None
            try:
                meta_path = os.path.join(self.workflows_dir, "metamorphosis_protocol.json")
                metamorphosis_result = self.workflow_engine.run_workflow(
                    meta_path, 
                    {
                        "session_knowledge_base": session_kb,
                        "problem_description": rise_state.problem_description,
                        "session_id": rise_state.session_id
                    }
                )
                logger.info("✅ Metamorphosis protocol completed successfully")
            except Exception as e:
                logger.warning(f"⚠️ Metamorphosis protocol failed: {e}")
                
                # Create fallback specialist agent
                domain = session_kb.get('domain', 'Strategic Analysis')
                fallback_agent = {
                    "agent_profile": {
                        "name": f"{domain} Specialist Agent",
                        "expertise": [domain, "Strategic Analysis", "Problem Solving"],
                        "background": f"Specialized agent for {domain} with strategic analysis capabilities",
                        "analytical_frameworks": ["SWOT Analysis", "Systems Thinking", "Risk Assessment"],
                        "strategic_patterns": ["Holistic Analysis", "Multi-perspective Evaluation"],
                        "implementation_approach": "Iterative analysis with continuous refinement",
                        "success_metrics": ["comprehensive_coverage", "actionable_insights", "risk_mitigation"]
                    },
                    "capabilities": {
                        "domain_knowledge": domain,
                        "analytical_skills": ["critical_thinking", "systems_analysis", "risk_assessment"],
                        "strategic_thinking": ["holistic_analysis", "multi-perspective_evaluation"],
                        "implementation_skills": ["iterative_development", "continuous_improvement"]
                    },
                    "metadata": {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "source": "fallback_generation",
                        "confidence": 0.7
                    }
                }
                
                metamorphosis_result = {
                    "specialized_agent": fallback_agent,
                    "metrics": {"fallback_used": True, "error": str(e)}
                }
            
            # Ensure we have a valid specialized agent
            specialized_agent = metamorphosis_result.get('specialized_agent')
            if not specialized_agent:
                domain = session_kb.get('domain', 'Strategic Analysis')
                specialized_agent = {
                    "agent_profile": {
                        "name": f"{domain} Specialist Agent",
                        "expertise": [domain, "Strategic Analysis"],
                        "background": f"Fallback agent for {domain}",
                        "analytical_frameworks": ["SWOT Analysis", "Systems Thinking"],
                        "strategic_patterns": ["Holistic Analysis"],
                        "implementation_approach": "Iterative analysis",
                        "success_metrics": ["comprehensive_coverage", "actionable_insights"]
                    }
                }
            
            # NEW: Create specialized agent object and generate action plan
            from .specialized_agent import SpecializedAgent
            available_capabilities = self._get_available_capabilities()
            protocol_knowledge = self.axiomatic_knowledge
            
            # Create specialized agent instance with workflow/action discovery
            domain = session_kb.get('domain', 'general_analysis')
            resonantia_capabilities = self._get_recommended_capabilities(rise_state.problem_description)
            
            # Pass workflows directory and action registry for discovery
            specialized_agent_obj = SpecializedAgent(
                domain_expertise=domain,
                resonantia_capabilities=resonantia_capabilities,
                workflows_dir=str(self.workflows_dir),
                action_registry=getattr(self, 'action_registry', None)
            )
            
            # Generate action plan
            action_plan = specialized_agent_obj.generate_action_plan(
                problem=rise_state.problem_description,
                available_capabilities=available_capabilities,
                protocol_knowledge=protocol_knowledge
            )
            
            phase_end = datetime.now(timezone.utc)
            phase_duration = (phase_end - phase_start).total_seconds()
            rise_state.execution_metrics['phase_durations']['A'] = phase_duration
            
            result = {
                'session_knowledge_base': session_kb,
                'specialized_agent': specialized_agent,
                'specialized_agent_obj': specialized_agent_obj.to_dict() if specialized_agent_obj else None,
                'action_plan': action_plan,
                'knowledge_acquisition_metrics': knowledge_result.get('metrics', {}),
                'metamorphosis_metrics': metamorphosis_result.get('metrics', {}),
                'phase_duration': phase_duration,
                'status': 'completed',
                'fallback_used': knowledge_result.get('metrics', {}).get('fallback_used', False) or 
                               metamorphosis_result.get('metrics', {}).get('fallback_used', False)
            }
            
            logger.info(f"✅ Phase A completed in {phase_duration:.2f}s")
            logger.info(f"Knowledge base size: {len(session_kb)} entries")
            logger.info(f"Specialist agent forged: {specialized_agent is not None}")
            logger.info(f"Action plan generated with {len(action_plan.get('action_sequence', []))} phases")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Phase A failed completely: {str(e)}")
            raise
    
    def _execute_phase_b(self, rise_state: RISEState) -> Dict[str, Any]:
        """
        Execute Phase B: Fused Insight Generation
        
        This phase:
        1. Uses advanced cognitive tools (causal inference, etc.) for general insights
        2. Consults the specialized agent (SCA) for domain-specific insights
        3. Fuses insights into a comprehensive strategic dossier
        
        Args:
            rise_state: Current RISE execution state
            
        Returns:
            Phase B results including advanced insights, specialist consultation, and fused dossier
        """
        phase_start = datetime.now(timezone.utc)
        rise_state.current_phase = "B"
        rise_state.phase_start_time = phase_start
        
        logger.info("🧠 Phase B: Generating fused insights through dual analysis")
        
        try:
            # Execute strategy fusion workflow - Use enhanced version with CFP/ABM/Causal Inference
            # First try core_workflows version (has tool integration)
            core_workflows_dir = os.path.join(os.path.dirname(self.workflows_dir), "core_workflows", "1_cognitive_engine")
            enhanced_fusion_path = os.path.join(core_workflows_dir, "strategy_fusion.json")
            basic_fusion_path = os.path.join(self.workflows_dir, "strategy_fusion.json")
            
            # Get effective model and provider from rise_state (set in Phase A)
            # Default to Groq if not set, but preserve what was set in Phase A
            effective_model = getattr(rise_state, 'effective_model', None)
            effective_provider = getattr(rise_state, 'effective_provider', None)
            
            # Fallback to Groq defaults if not set in Phase A
            if not effective_model or not effective_provider:
                from .llm_providers import get_model_for_provider
                effective_provider = effective_provider or os.getenv("ARCHE_LLM_PROVIDER", "groq")
                effective_model = effective_model or get_model_for_provider(effective_provider)
            
            # Seed minimal initial_context for Phase B pathways (causal, ABM, CFP)
            fusion_initial_context = {
                "problem_description": rise_state.problem_description,
                "knowledge_base": rise_state.session_knowledge_base,
                "session_knowledge_base": rise_state.session_knowledge_base,
                "specialized_agent": rise_state.specialized_agent,
                "model": effective_model,  # Pass model to Phase B
                "provider": effective_provider,  # Pass provider to Phase B
                "initial_context": {
                    "case_event_timeline": [],
                    "core_hypothesis": f"Hypothesis: {rise_state.problem_description[:120]}",
                    "narrative_a": "Baseline operations maintained; incremental personalization",
                    "narrative_b": "Aggressive on-device personalization with strict privacy",
                    "scenario_a_config": {"quantum_state": [0.8, 0.6]},
                    "scenario_b_config": {"quantum_state": [0.6, 0.7]}
                },
                "session_id": rise_state.session_id,
                "phase": "B"
            }
            
            # Try enhanced version first, fall back to basic if it fails
            fusion_path = None
            fusion_result = None
            
            if os.path.exists(enhanced_fusion_path):
                try:
                    logger.info("✅ Attempting enhanced strategy_fusion.json with CFP/ABM/Causal Inference pathways")
                    fusion_result = self.workflow_engine.run_workflow(
                        enhanced_fusion_path,
                        fusion_initial_context
                    )
                    # Check if workflow actually succeeded (not just loaded)
                    if isinstance(fusion_result, dict) and fusion_result.get('status') != 'Failed':
                        fusion_path = enhanced_fusion_path
                        logger.info("✅ Enhanced strategy_fusion.json executed successfully")
                    else:
                        raise ValueError("Enhanced workflow returned failure status")
                except (ValueError, FileNotFoundError, TypeError) as e:
                    logger.warning(f"⚠️ Enhanced strategy_fusion.json failed: {e}. Falling back to basic version.")
                    fusion_result = None
            
            # Fallback to basic version if enhanced failed or doesn't exist
            if fusion_result is None:
                if os.path.exists(basic_fusion_path):
                    fusion_path = basic_fusion_path
                    logger.info("Using basic strategy_fusion.json")
                    fusion_result = self.workflow_engine.run_workflow(
                        basic_fusion_path,
                        fusion_initial_context
                    )
                else:
                    raise FileNotFoundError(f"Neither enhanced nor basic strategy_fusion.json found")
            
            # Validate fusion_result is a dict before proceeding
            if not isinstance(fusion_result, dict):
                logger.error(f"❌ Phase B workflow returned non-dict result: {type(fusion_result)}")
                fusion_result = {"error": str(fusion_result) if fusion_result else "Unknown error", "status": "failed"}
            
            # NEW: Synthesize external insights with codebase patterns (Self-Referential Synthesis)
            synthesized_solution = None
            if self.codebase_archaeologist and isinstance(fusion_result, dict):
                try:
                    # Get codebase patterns from Phase A (if available)
                    codebase_patterns = []
                    session_kb = rise_state.session_knowledge_base
                    # Ensure session_kb is a dict
                    if isinstance(session_kb, str):
                        try:
                            import json
                            session_kb = json.loads(session_kb)
                        except (json.JSONDecodeError, ValueError):
                            session_kb = {}
                    if session_kb and isinstance(session_kb, dict) and "codebase_patterns" in session_kb:
                        # Reconstruct CodebasePattern objects from dict
                        from .codebase_archaeologist import CodebasePattern
                        for p_dict in session_kb.get("codebase_patterns", [])[:10]:  # Top 10
                            try:
                                if not isinstance(p_dict, dict):
                                    continue
                                pattern = CodebasePattern(
                                    pattern_type=p_dict.get("type", "unknown"),
                                    name=p_dict.get("name", ""),
                                    file_path=Path(p_dict.get("file_path", "")),
                                    description=p_dict.get("description", ""),
                                    relevance_score=p_dict.get("relevance_score", 0.0),
                                    key_excerpts=p_dict.get("key_excerpts", []),
                                    relationships=p_dict.get("relationships", []),
                                    spr_references=p_dict.get("spr_references", []),
                                    implementation_details=p_dict.get("implementation_details", {})
                                )
                                codebase_patterns.append(pattern)
                            except Exception as e:
                                logger.debug(f"Error reconstructing pattern: {e}")
                                continue
                    
                    # If no patterns from Phase A, search again with Phase B context
                    if not codebase_patterns:
                        logger.info("🔍 Phase B: Searching codebase for pathway implementation patterns...")
                        # Search for patterns related to each pathway
                        pathway_patterns = []
                        for pathway in ["causal inference", "agent based modeling", "comparative fluxual", "simulation"]:
                            try:
                                patterns = self.codebase_archaeologist.search_codebase_for_patterns(
                                    query=f"{pathway} implementation pattern",
                                    pattern_types=["class", "function", "workflow"],
                                    max_results=3
                                )
                                if patterns:
                                    pathway_patterns.extend(patterns)
                            except Exception as e:
                                logger.debug(f"Error searching for {pathway} patterns: {e}")
                                continue
                        codebase_patterns = pathway_patterns[:10]  # Top 10
                    
                    # Synthesize external knowledge with codebase patterns
                    if codebase_patterns:
                        external_knowledge = {
                            "summary": fusion_result.get('fused_strategic_dossier', {}) if isinstance(fusion_result, dict) else {},
                            "insights": fusion_result.get('advanced_insights', []) if isinstance(fusion_result, dict) else [],
                            "specialist_consultation": fusion_result.get('specialist_consultation') if isinstance(fusion_result, dict) else None
                        }
                        
                        synthesized_solution = self.codebase_archaeologist.synthesize_from_patterns(
                            problem_description=rise_state.problem_description,
                            external_knowledge=external_knowledge,
                            codebase_patterns=codebase_patterns,
                            synthesis_mode="hybrid"
                        )
                        
                        if synthesized_solution and isinstance(synthesized_solution, dict):
                            logger.info(f"✅ Synthesized solution from {len(codebase_patterns)} codebase patterns")
                            logger.info(f"   Novel combinations: {len(synthesized_solution.get('novel_combinations', []))}")
                            
                            # Enhance fused strategic dossier with synthesis
                            if isinstance(fusion_result, dict):
                                fused_dossier = fusion_result.get('fused_strategic_dossier', {})
                                if isinstance(fused_dossier, dict):
                                    fused_dossier['codebase_synthesis'] = synthesized_solution
                                    fused_dossier['synthesis_confidence'] = synthesized_solution.get('confidence', 0.0)
                                    fusion_result['fused_strategic_dossier'] = fused_dossier
                        
                except Exception as e:
                    logger.warning(f"⚠️ Codebase synthesis failed: {e}")
                    synthesized_solution = None
            
            phase_end = datetime.now(timezone.utc)
            phase_duration = (phase_end - phase_start).total_seconds()
            rise_state.execution_metrics['phase_durations']['B'] = phase_duration
            
            # Safely extract results from fusion_result
            result = {
                'advanced_insights': fusion_result.get('advanced_insights', []) if isinstance(fusion_result, dict) else [],
                'specialist_consultation': fusion_result.get('specialist_consultation') if isinstance(fusion_result, dict) else None,
                'fused_strategic_dossier': fusion_result.get('fused_strategic_dossier') if isinstance(fusion_result, dict) else None,
                'codebase_synthesis': synthesized_solution,  # NEW
                'fusion_metrics': fusion_result.get('metrics', {}) if isinstance(fusion_result, dict) else {},
                'phase_duration': phase_duration,
                'status': 'completed' if isinstance(fusion_result, dict) and fusion_result.get('status') != 'failed' else 'failed',
                'error': fusion_result.get('error') if isinstance(fusion_result, dict) else None
            }
            
            logger.info(f"✅ Phase B completed in {phase_duration:.2f}s")
            logger.info(f"Advanced insights generated: {len(result['advanced_insights'])}")
            logger.info(f"Strategic dossier created: {result['fused_strategic_dossier'] is not None}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Phase B failed: {str(e)}")
            raise
    
    def _execute_phase_c(self, rise_state: RISEState) -> Dict[str, Any]:
        """
        Execute Phase C: Fused Strategy Generation & Finalization
        
        This phase:
        1. Synthesizes all insights into a final strategy
        2. Subjects strategy to HighStakesVetting cascade
        3. Distills successful process into new SPR for future use
        
        Args:
            rise_state: Current RISE execution state
            
        Returns:
            Phase C results including final strategy, vetting dossier, and SPR definition
        """
        phase_start = datetime.now(timezone.utc)
        rise_state.current_phase = "C"
        rise_state.phase_start_time = phase_start
        
        logger.info("🎯 Phase C: Finalizing strategy with HighStakesVetting")
        
        try:
            # Execute high stakes vetting workflow
            vetting_path_c = os.path.join(self.workflows_dir, "high_stakes_vetting.json")
            # Get effective model and provider from Phase A context (stored in rise_state or use Groq defaults)
            effective_model = getattr(rise_state, 'effective_model', None)
            effective_provider = getattr(rise_state, 'effective_provider', None)
            
            # Fallback to Groq defaults if not set in Phase A
            if not effective_model or not effective_provider:
                from .llm_providers import get_model_for_provider
                effective_provider = effective_provider or os.getenv("ARCHE_LLM_PROVIDER", "groq")
                effective_model = effective_model or get_model_for_provider(effective_provider)
            
            vetting_result = self.workflow_engine.run_workflow(
                vetting_path_c,
                {
                    "strategy_dossier": rise_state.fused_strategic_dossier,
                    "problem_description": rise_state.problem_description,
                    "session_id": rise_state.session_id,
                    "phase": "C",
                    "model": effective_model,  # Pass model to Phase C
                    "provider": effective_provider  # Pass provider to Phase C
                }
            )
            
            # NEW: Codebase pattern validation after vetting
            pattern_alignment = None
            if self.codebase_archaeologist and vetting_result.get('final_strategy'):
                try:
                    logger.info("🔍 Phase C: Validating strategy against codebase patterns...")
                    final_strategy = vetting_result.get('final_strategy')
                    # Handle case where final_strategy might be a string
                    if isinstance(final_strategy, str):
                        # Convert string to dict format for validation
                        strategy_dict = {"strategy_text": final_strategy, "strategy_type": "text"}
                    elif isinstance(final_strategy, dict):
                        strategy_dict = final_strategy
                    else:
                        strategy_dict = {"strategy": str(final_strategy)}
                    
                    pattern_alignment = self.codebase_archaeologist.validate_against_patterns(
                        strategy=strategy_dict,
                        required_patterns=["IAR compliance", "SPR integration", "workflow compatibility"]
                    )
                    logger.info(f"✅ Pattern alignment validation: {pattern_alignment.get('alignment_score', 0.0):.2f}")
                except Exception as e:
                    logger.warning(f"⚠️ Codebase pattern validation failed: {e}")
                    pattern_alignment = None
            
            # Execute SPR distillation workflow
            spr_path_c = os.path.join(self.workflows_dir, "distill_spr.json")
            spr_result = self.workflow_engine.run_workflow(
                spr_path_c,
                {
                    "thought_trail": self.thought_trail.get_recent_entries(10) if self.thought_trail else [],
                    "final_strategy": vetting_result.get('final_strategy'),
                    "session_id": rise_state.session_id,
                    "problem_description": rise_state.problem_description,
                    "pattern_alignment": pattern_alignment,  # Pass alignment for SPR refinement
                    "model": effective_model,  # Pass model to SPR distillation
                    "provider": effective_provider  # Pass provider to SPR distillation
                }
            )
            
            phase_end = datetime.now(timezone.utc)
            phase_duration = (phase_end - phase_start).total_seconds()
            rise_state.execution_metrics['phase_durations']['C'] = phase_duration
            
            result = {
                'vetting_dossier': vetting_result.get('vetting_dossier'),
                'final_strategy': vetting_result.get('final_strategy'),
                'pattern_alignment': pattern_alignment,  # NEW
                'spr_definition': spr_result.get('spr_definition'),
                'vetting_metrics': vetting_result.get('metrics', {}),
                'spr_metrics': spr_result.get('metrics', {}),
                'phase_duration': phase_duration,
                'status': 'completed'
            }
            
            logger.info(f"✅ Phase C completed in {phase_duration:.2f}s")
            logger.info(f"Strategy vetted: {result['final_strategy'] is not None}")
            logger.info(f"SPR distilled: {result['spr_definition'] is not None}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Phase C failed: {str(e)}")
            raise
    
    def _execute_phase_d(self, rise_state: RISEState) -> Dict[str, Any]:
        """
        Execute Phase D: Utopian Vetting & Refinement (Corrected Implementation)
        
        This phase, as per the directive, should mirror the structure of Phase C,
        running the high_stakes_vetting and distill_spr workflows on the
        final strategy to produce the definitive, vetted output.

        Args:
            rise_state: Current RISE execution state
            
        Returns:
            Phase D results including final vetted strategy and SPR definition.
        """
        phase_start = datetime.now(timezone.utc)
        rise_state.current_phase = "D"
        rise_state.phase_start_time = phase_start
        
        logger.info("🎯 Phase D: Final Vetting & Crystallization")
        
        try:
            # Get effective model and provider from Phase A context
            effective_model = getattr(rise_state, 'effective_model', 'cursor-arche-v1')
            effective_provider = getattr(rise_state, 'effective_provider', 'cursor')
            
            # Execute high stakes vetting workflow on the final strategy from Phase C
            vetting_path_d = os.path.join(self.workflows_dir, "high_stakes_vetting.json")
            vetting_result = self.workflow_engine.run_workflow(
                vetting_path_d,
                {
                    "strategy_dossier": rise_state.final_strategy, # Vet the final strategy
                    "problem_description": rise_state.problem_description,
                    "session_id": rise_state.session_id,
                    "phase": "D",
                    "model": effective_model,  # Pass model to Phase D
                    "provider": effective_provider  # Pass provider to Phase D
                }
            )

            # --- CRITICAL VALIDATION ---
            final_vetted_strategy = vetting_result.get('final_strategy')
            if final_vetted_strategy is None:
                raise RuntimeError("Phase D vetting failed to produce a final_strategy.")

            # NEW: Identify novel codebase combinations as SPR candidates
            novel_spr_candidates = []
            if self.codebase_archaeologist and isinstance(rise_state.session_knowledge_base, dict) and rise_state.session_knowledge_base.get('codebase_synthesis'):
                try:
                    logger.info("🔍 Phase D: Identifying novel codebase combinations as SPR candidates...")
                    codebase_synthesis = rise_state.session_knowledge_base.get('codebase_synthesis', {})
                    if isinstance(codebase_synthesis, dict):
                        novel_combinations = codebase_synthesis.get('novel_combinations', [])
                    else:
                        novel_combinations = []
                    
                    if novel_combinations:
                        for combination in novel_combinations[:5]:  # Top 5 novel patterns
                            spr_candidate = {
                                "spr_id": f"{combination.get('domain', 'SynthesiS')}Pattern",
                                "name": combination.get('description', 'Novel Synthesis Pattern'),
                                "pattern": combination,
                                "codebase_sources": combination.get('codebase_components', []),
                                "external_sources": combination.get('external_components', []),
                                "confidence": combination.get('confidence', 0.7),
                                "created_from": "RISE-SRCS Phase D",
                                "session_id": rise_state.session_id
                            }
                            novel_spr_candidates.append(spr_candidate)
                        
                        logger.info(f"✅ Identified {len(novel_spr_candidates)} novel SPR candidates")
                except Exception as e:
                    logger.warning(f"⚠️ SPR candidate identification failed: {e}")
            
            # Execute SPR distillation workflow on the successfully vetted strategy
            spr_path_d = os.path.join(self.workflows_dir, "distill_spr.json")
            spr_result = self.workflow_engine.run_workflow(
                spr_path_d,
                {
                    "thought_trail": self.thought_trail.get_recent_entries(50) if self.thought_trail else [],
                    "final_strategy": final_vetted_strategy,
                    "session_id": rise_state.session_id,
                    "problem_description": rise_state.problem_description,
                    "novel_spr_candidates": novel_spr_candidates,  # Pass candidates for consideration
                    "model": effective_model,  # Pass model to SPR distillation
                    "provider": effective_provider  # Pass provider to SPR distillation
                }
            )
            
            phase_end = datetime.now(timezone.utc)
            phase_duration = (phase_end - phase_start).total_seconds()
            rise_state.execution_metrics['phase_durations']['D'] = phase_duration
            
            result = {
                'vetting_dossier': vetting_result.get('vetting_dossier'),
                'final_strategy': final_vetted_strategy,
                'novel_spr_candidates': novel_spr_candidates,  # NEW
                'spr_definition': spr_result.get('spr_definition'),
                'vetting_metrics': vetting_result.get('metrics', {}),
                'spr_metrics': spr_result.get('metrics', {}),
                'phase_duration': phase_duration,
                'status': 'completed'
            }
            
            logger.info(f"✅ Phase D completed in {phase_duration:.2f}s")
            logger.info(f"Final strategy confirmed: {result['final_strategy'] is not None}")
            logger.info(f"Final SPR distilled: {result['spr_definition'] is not None}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Phase D failed: {str(e)}")
            raise
    
    def get_execution_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current execution status for a session
        
        Args:
            session_id: The session ID to check
            
        Returns:
            Current execution status or None if session not found
        """
        if session_id in self.active_sessions:
            rise_state = self.active_sessions[session_id]
            return {
                'session_id': session_id,
                'current_phase': rise_state.current_phase,
                'phase_name': self.phases.get(rise_state.current_phase, 'Unknown'),
                'phase_start_time': rise_state.phase_start_time.isoformat(),
                'problem_description': rise_state.problem_description,
                'status': 'active'
            }
        return None
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent execution history
        
        Args:
            limit: Maximum number of recent executions to return
            
        Returns:
            List of recent execution records
        """
        return self.execution_history[-limit:] if self.execution_history else []
    
    def get_system_diagnostics(self) -> Dict[str, Any]:
        """
        Get comprehensive system diagnostics
        
        Returns:
            System diagnostics including active sessions, history, and metrics
        """
        return {
            'active_sessions': len(self.active_sessions),
            'total_executions': len(self.execution_history),
            'success_rate': self._calculate_success_rate(),
            'average_duration': self._calculate_average_duration(),
            'recent_executions': self.get_execution_history(5),
            'workflow_engine_status': self.workflow_engine.get_resonance_dashboard()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate from execution history"""
        if not self.execution_history:
            return 0.0
        
        successful = sum(1 for record in self.execution_history if record.get('success', False))
        return successful / len(self.execution_history)
    
    def _calculate_average_duration(self) -> float:
        """Calculate average execution duration"""
        if not self.execution_history:
            return 0.0
        
        durations = [record.get('duration', 0) for record in self.execution_history]
        return sum(durations) / len(durations) 