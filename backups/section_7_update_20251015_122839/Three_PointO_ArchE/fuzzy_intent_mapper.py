"""
Fuzzy Intent Mapper - Natural Language to ArchE Components
===========================================================

This system interprets vague/imprecise Keyholder requests and maps them to
exact ArchE components, preventing duplication and ensuring alignment.

Implements:
- Mandate 2: Proactive Truth Resonance Framework
- Oracle's Paradox solution
- Natural language understanding
- Component discovery
- Duplication prevention
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class FuzzyIntentMapper:
    """
    Maps fuzzy/vague Keyholder descriptions to exact ArchE components.
    
    Purpose: Bridge human memory limitations and machine precision.
    """
    
    # Component mapping database
    COMPONENT_MAPPINGS = {
        # Session/Conversation related
        "session|conversation|chat|interaction|talk|discuss": {
            "components": [
                {
                    "name": "SessionAutoCapture",
                    "file": "Three_PointO_ArchE/session_auto_capture.py",
                    "purpose": "Auto-captures and exports conversations to markdown",
                    "status": "ACTIVE",
                    "keywords": ["save", "export", "capture", "record", "conversation", "chat"]
                },
                {
                    "name": "SessionManager",
                    "file": "Three_PointO_ArchE/session_manager.py",
                    "purpose": "Manages session persistence and state",
                    "status": "ACTIVE",
                    "keywords": ["session", "state", "persist", "track"]
                },
                {
                    "name": "ThoughtTrail",
                    "file": "Three_PointO_ArchE/thought_trail.py",
                    "purpose": "Captures IAR entries for consciousness stream",
                    "status": "ACTIVE",
                    "keywords": ["memory", "trail", "consciousness", "iar", "record"]
                }
            ]
        },
        
        # Learning/Pattern Detection
        "learn|pattern|improve|evolve|grow|adapt": {
            "components": [
                {
                    "name": "AutopoieticLearningLoop",
                    "file": "Three_PointO_ArchE/autopoietic_learning_loop.py",
                    "purpose": "4-epoch learning cycle (Stardust→Nebulae→Ignition→Galaxies)",
                    "status": "ACTIVE",
                    "keywords": ["learn", "pattern", "detect", "evolve", "improve", "wisdom"]
                },
                {
                    "name": "ACO (Adaptive Cognitive Orchestrator)",
                    "file": "Three_PointO_ArchE/adaptive_cognitive_orchestrator.py",
                    "purpose": "Meta-learning and pattern evolution",
                    "status": "ACTIVE",
                    "keywords": ["meta", "learning", "adapt", "orchestrate"]
                }
            ]
        },
        
        # Knowledge/SPRs
        "knowledge|concept|definition|spr|term|understand": {
            "components": [
                {
                    "name": "SPRManager",
                    "file": "Three_PointO_ArchE/spr_manager.py",
                    "purpose": "Manages SPR definitions and priming",
                    "status": "ACTIVE",
                    "keywords": ["spr", "knowledge", "definition", "prime", "concept"]
                },
                {
                    "name": "InsightSolidificationEngine",
                    "file": "Three_PointO_ArchE/insight_solidification_engine.py",
                    "purpose": "Creates and updates SPRs in Knowledge Tapestry",
                    "status": "ACTIVE",
                    "keywords": ["solidify", "insight", "create spr", "knowledge tapestry"]
                },
                {
                    "name": "Knowledge Tapestry",
                    "file": "knowledge_graph/spr_definitions_tv.json",
                    "purpose": "Central repository of 102 SPR definitions",
                    "status": "ACTIVE",
                    "keywords": ["knowledge base", "definitions", "sprs", "tapestry"]
                }
            ]
        },
        
        # Thinking/Processing
        "think|process|analyze|reason|strategic|fast|slow": {
            "components": [
                {
                    "name": "CRCS (Cognitive Resonant Controller System)",
                    "file": "Integrated in multiple files",
                    "purpose": "Fast, instinctual responses (<100ms)",
                    "status": "ACTIVE",
                    "keywords": ["fast", "quick", "instinct", "cerebellum", "instant"]
                },
                {
                    "name": "RISE Orchestrator",
                    "file": "Three_PointO_ArchE/rise_orchestrator.py",
                    "purpose": "Deep, strategic thinking (~1000ms)",
                    "status": "ACTIVE",
                    "keywords": ["deep", "strategic", "slow", "cerebrum", "thorough"]
                },
                {
                    "name": "CognitiveIntegrationHub",
                    "file": "Three_PointO_ArchE/cognitive_integration_hub.py",
                    "purpose": "Orchestrates CRCS→RISE→ACO routing",
                    "status": "ACTIVE",
                    "keywords": ["orchestrate", "route", "integrate", "hub"]
                }
            ]
        },
        
        # Backup/Safety
        "backup|save|revert|undo|protect|safety": {
            "components": [
                {
                    "name": "BackupRetentionPolicy",
                    "file": "specifications/backup_retention_policy.md",
                    "purpose": "MANDATORY backup before ANY file modification",
                    "status": "ACTIVE (Mandate 13)",
                    "keywords": ["backup", "save", "protect", "revert", "validation"]
                }
            ]
        },
        
        # Workflows/Automation
        "workflow|process|automate|sequence|procedure": {
            "components": [
                {
                    "name": "IARCompliantWorkflowEngine",
                    "file": "Three_PointO_ArchE/workflow_engine.py",
                    "purpose": "Executes Process BlueprintS (JSON workflows)",
                    "status": "ACTIVE",
                    "keywords": ["workflow", "process", "execute", "blueprint", "automate"]
                }
            ]
        },
        
        # Reflection/Confidence
        "reflect|confidence|assess|check|evaluate": {
            "components": [
                {
                    "name": "IAR (Integrated Action Reflection)",
                    "file": "Every action returns IAR dict",
                    "purpose": "Self-assessment: status, confidence, issues, alignment",
                    "status": "ACTIVE (Universal)",
                    "keywords": ["reflect", "confidence", "assess", "iar", "self-check"]
                }
            ]
        }
    }
    
    def __init__(self):
        """Initialize the fuzzy intent mapper."""
        self.compiled_patterns = {}
        self._compile_patterns()
        logger.info("FuzzyIntentMapper initialized")
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        for pattern_str, data in self.COMPONENT_MAPPINGS.items():
            try:
                self.compiled_patterns[pattern_str] = re.compile(
                    pattern_str,
                    re.IGNORECASE
                )
            except re.error as e:
                logger.error(f"Failed to compile pattern '{pattern_str}': {e}")
    
    def map_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Map a fuzzy user query to exact ArchE components.
        
        Args:
            user_query: Vague/imprecise description from user
            
        Returns:
            Dictionary with matched components and recommendations
        """
        user_query_lower = user_query.lower()
        matches = []
        
        # Find matching component categories
        for pattern_str, pattern_obj in self.compiled_patterns.items():
            if pattern_obj.search(user_query_lower):
                components = self.COMPONENT_MAPPINGS[pattern_str]["components"]
                
                # Score each component by keyword relevance
                for component in components:
                    relevance_score = self._calculate_relevance(
                        user_query_lower,
                        component["keywords"]
                    )
                    
                    if relevance_score > 0.3:  # Threshold
                        matches.append({
                            **component,
                            "relevance_score": relevance_score,
                            "pattern_matched": pattern_str
                        })
        
        # Sort by relevance
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Generate recommendations
        recommendation = self._generate_recommendation(user_query, matches)
        
        return {
            "query": user_query,
            "matches": matches,
            "recommendation": recommendation,
            "has_existing_implementation": len(matches) > 0
        }
    
    def _calculate_relevance(self, query: str, keywords: List[str]) -> float:
        """
        Calculate relevance score between query and component keywords.
        
        Args:
            query: User query (lowercase)
            keywords: Component keywords
            
        Returns:
            Relevance score (0.0-1.0)
        """
        score = 0.0
        query_words = set(re.findall(r'\w+', query))
        
        for keyword in keywords:
            keyword_words = set(re.findall(r'\w+', keyword.lower()))
            
            # Exact word matches
            common_words = query_words.intersection(keyword_words)
            if common_words:
                score += len(common_words) * 0.3
            
            # Fuzzy matches
            for qword in query_words:
                for kword in keyword_words:
                    similarity = SequenceMatcher(None, qword, kword).ratio()
                    if similarity > 0.8:
                        score += similarity * 0.2
        
        # Normalize
        return min(score, 1.0)
    
    def _generate_recommendation(self, query: str, matches: List[Dict]) -> str:
        """
        Generate recommendation based on matches.
        
        Args:
            query: Original user query
            matches: List of matched components
            
        Returns:
            Recommendation string
        """
        if not matches:
            return (
                "No existing components found matching your description. "
                "This appears to be a NEW feature request. "
                "Recommend: Detailed specification before implementation."
            )
        
        if len(matches) == 1:
            comp = matches[0]
            return (
                f"✅ **EXISTING COMPONENT FOUND**: `{comp['name']}`\n"
                f"**Location**: `{comp['file']}`\n"
                f"**Purpose**: {comp['purpose']}\n"
                f"**Status**: {comp['status']}\n"
                f"**Recommendation**: Use existing implementation. No new code needed!"
            )
        
        # Multiple matches
        rec = "✅ **MULTIPLE EXISTING COMPONENTS FOUND**:\n\n"
        for i, comp in enumerate(matches[:5], 1):  # Top 5
            rec += (
                f"{i}. **{comp['name']}** ({comp['relevance_score']:.0%} match)\n"
                f"   - File: `{comp['file']}`\n"
                f"   - Purpose: {comp['purpose']}\n"
                f"   - Status: {comp['status']}\n\n"
            )
        
        rec += "**Recommendation**: Review these existing components. Your need may already be met!"
        return rec
    
    def check_for_duplication(self, proposed_feature: str) -> Tuple[bool, List[Dict], str]:
        """
        Check if a proposed feature would duplicate existing functionality.
        
        Args:
            proposed_feature: Description of what user wants to create
            
        Returns:
            Tuple of (is_duplicate, matching_components, recommendation)
        """
        result = self.map_intent(proposed_feature)
        
        is_duplicate = result["has_existing_implementation"]
        matches = result["matches"]
        recommendation = result["recommendation"]
        
        if is_duplicate:
            warning = (
                "⚠️ **DUPLICATION WARNING**\n\n"
                f"The proposed feature '{proposed_feature}' appears to already exist.\n\n"
                f"{recommendation}\n\n"
                "**Action**: Review existing implementations before creating new code."
            )
            return True, matches, warning
        
        return False, [], "✅ No duplication detected. This appears to be a new feature."


# Singleton instance
_mapper_instance = None

def get_mapper() -> FuzzyIntentMapper:
    """Get singleton mapper instance."""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = FuzzyIntentMapper()
    return _mapper_instance


# Convenience function
def interpret_fuzzy_intent(user_query: str) -> Dict[str, Any]:
    """
    Interpret fuzzy user intent and map to exact components.
    
    Args:
        user_query: Vague/imprecise user description
        
    Returns:
        Mapping result with matches and recommendations
    """
    mapper = get_mapper()
    return mapper.map_intent(user_query)


