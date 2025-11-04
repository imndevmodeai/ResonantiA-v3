#!/usr/bin/env python3
"""
Codebase Archaeologist - RISE Self-Referential Codebase Synthesis
The Mirror of Self-Knowledge - ArchE searches its own implementation

This module enables RISE to search its own codebase for relevant patterns,
classes, functions, and workflows that can inform problem-solving. It transforms
RISE from an external-knowledge-dependent system into a self-aware code 
archaeologist that can synthesize novel solutions from its own implementation.

Philosophical Foundation:
- "To know thyself is to solve thyself"
- The system that understands its own architecture can create better solutions
- Combining disparate codebase elements creates novel, personalized architectures
- Grounded innovation: external knowledge validated against internal reality

Integration:
- Uses AutopoieticSelfAnalysis for AST parsing
- Uses SPRManager for relationship mapping
- Integrates with RISE orchestrator phases
"""

import logging
import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

try:
    from .autopoietic_self_analysis import AutopoieticSelfAnalysis
    from .spr_manager import SPRManager
    AUTOPOIETIC_AVAILABLE = True
except ImportError:
    AUTOPOIETIC_AVAILABLE = False
    logger.warning("AutopoieticSelfAnalysis not available, limited functionality")

logger = logging.getLogger(__name__)


@dataclass
class CodebasePattern:
    """Represents a discovered pattern in the codebase"""
    pattern_type: str  # "class", "function", "workflow", "spr", "specification"
    name: str
    file_path: Path
    description: str = ""
    relevance_score: float = 0.0
    key_excerpts: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    spr_references: List[str] = field(default_factory=list)
    implementation_details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "type": self.pattern_type,
            "name": self.name,
            "file_path": str(self.file_path),
            "description": self.description,
            "relevance_score": self.relevance_score,
            "key_excerpts": self.key_excerpts,
            "relationships": self.relationships,
            "spr_references": self.spr_references,
            "implementation_details": self.implementation_details
        }


class CodebaseArchaeologist:
    """
    Searches ArchE's own codebase for relevant patterns, classes, functions,
    and workflows that can inform problem-solving.
    
    This is like having RISE search its own "memory" of how it has solved
    problems in the past, enabling it to synthesize novel solutions by
    combining proven patterns.
    """
    
    def __init__(
        self,
        codebase_root: str = None,
        spr_manager: Optional[SPRManager] = None,
        autopoietic_analyzer: Optional[AutopoieticSelfAnalysis] = None
    ):
        """
        Initialize the Codebase Archaeologist.
        
        Args:
            codebase_root: Root directory of the codebase (defaults to Three_PointO_ArchE parent)
            spr_manager: Optional SPR manager for relationship mapping
            autopoietic_analyzer: Optional analyzer for AST parsing
        """
        if codebase_root is None:
            # Default to project root (parent of Three_PointO_ArchE)
            codebase_root = Path(__file__).parent.parent
        self.codebase_root = Path(codebase_root)
        
        self.spr_manager = spr_manager
        self.autopoietic_analyzer = autopoietic_analyzer or (
            AutopoieticSelfAnalysis() if AUTOPOIETIC_AVAILABLE else None
        )
        
        # Cache for codebase structure
        self._codebase_index: Optional[Dict[str, Any]] = None
        self._index_valid = False
        
        logger.info(f"CodebaseArchaeologist initialized with root: {self.codebase_root}")
    
    def search_codebase_for_patterns(
        self,
        query: str,
        pattern_types: List[str] = None,
        max_results: int = 10,
        search_mode: str = "semantic"  # "semantic", "exact", "fuzzy"
    ) -> List[CodebasePattern]:
        """
        Semantic search across codebase for relevant patterns.
        
        Args:
            query: Problem description or pattern to search for
            pattern_types: What to search (class, function, workflow, spr, specification)
            max_results: Maximum number of results to return
            search_mode: Search mode (semantic, exact, fuzzy)
            
        Returns:
            List of relevant codebase patterns with metadata
        """
        if pattern_types is None:
            pattern_types = ["class", "function", "workflow", "spr", "specification"]
        
        logger.info(f"Searching codebase for patterns: '{query}' (types: {pattern_types})")
        
        patterns = []
        
        # Search different pattern types
        if "class" in pattern_types:
            patterns.extend(self._search_classes(query, search_mode))
        if "function" in pattern_types:
            patterns.extend(self._search_functions(query, search_mode))
        if "workflow" in pattern_types:
            patterns.extend(self._search_workflows(query, search_mode))
        if "spr" in pattern_types and self.spr_manager:
            patterns.extend(self._search_sprs(query, search_mode))
        if "specification" in pattern_types:
            patterns.extend(self._search_specifications(query, search_mode))
        
        # Score and rank patterns
        patterns = self._score_patterns(patterns, query)
        patterns.sort(key=lambda p: p.relevance_score, reverse=True)
        
        return patterns[:max_results]
    
    def _search_classes(
        self,
        query: str,
        search_mode: str
    ) -> List[CodebasePattern]:
        """Search for class definitions matching the query"""
        patterns = []
        code_dir = self.codebase_root / "Three_PointO_ArchE"
        
        if not code_dir.exists():
            return patterns
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for py_file in code_dir.rglob("*.py"):
            try:
                if not self.autopoietic_analyzer:
                    continue
                
                analysis = self.autopoietic_analyzer.analyze_implementation(py_file)
                classes = analysis.get("classes", set())
                
                for class_name in classes:
                    # Calculate relevance
                    relevance = self._calculate_relevance(
                        class_name, query_terms, query_lower, search_mode
                    )
                    
                    if relevance > 0.3:  # Threshold for inclusion
                        pattern = CodebasePattern(
                            pattern_type="class",
                            name=class_name,
                            file_path=py_file,
                            relevance_score=relevance,
                            description=f"Class {class_name} in {py_file.name}",
                            implementation_details={
                                "methods": list(analysis.get("methods", {}).get(class_name, set())),
                                "imports": list(analysis.get("imports", set()))[:10]  # Limit
                            }
                        )
                        patterns.append(pattern)
                        
            except Exception as e:
                logger.debug(f"Error searching {py_file}: {e}")
                continue
        
        return patterns
    
    def _search_functions(
        self,
        query: str,
        search_mode: str
    ) -> List[CodebasePattern]:
        """Search for function definitions matching the query"""
        patterns = []
        code_dir = self.codebase_root / "Three_PointO_ArchE"
        
        if not code_dir.exists():
            return patterns
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for py_file in code_dir.rglob("*.py"):
            try:
                if not self.autopoietic_analyzer:
                    continue
                
                analysis = self.autopoietic_analyzer.analyze_implementation(py_file)
                functions = analysis.get("functions", set())
                
                for func_name in functions:
                    relevance = self._calculate_relevance(
                        func_name, query_terms, query_lower, search_mode
                    )
                    
                    if relevance > 0.3:
                        pattern = CodebasePattern(
                            pattern_type="function",
                            name=func_name,
                            file_path=py_file,
                            relevance_score=relevance,
                            description=f"Function {func_name} in {py_file.name}",
                            implementation_details={
                                "file": str(py_file),
                                "is_method": False
                            }
                        )
                        patterns.append(pattern)
                        
            except Exception as e:
                logger.debug(f"Error searching {py_file}: {e}")
                continue
        
        return patterns
    
    def _search_workflows(
        self,
        query: str,
        search_mode: str
    ) -> List[CodebasePattern]:
        """Search for workflow JSON files matching the query"""
        patterns = []
        workflows_dir = self.codebase_root / "workflows"
        
        if not workflows_dir.exists():
            return patterns
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for workflow_file in workflows_dir.rglob("*.json"):
            try:
                import json
                with open(workflow_file, 'r') as f:
                    workflow_data = json.load(f)
                
                workflow_name = workflow_data.get("name", workflow_file.stem)
                workflow_desc = workflow_data.get("description", "")
                
                # Calculate relevance from name and description
                combined_text = f"{workflow_name} {workflow_desc}".lower()
                relevance = self._calculate_relevance(
                    combined_text, query_terms, query_lower, search_mode
                )
                
                if relevance > 0.3:
                    pattern = CodebasePattern(
                        pattern_type="workflow",
                        name=workflow_name,
                        file_path=workflow_file,
                        relevance_score=relevance,
                        description=workflow_desc,
                        implementation_details={
                            "tasks_count": len(workflow_data.get("tasks", {})),
                            "version": workflow_data.get("version", "unknown")
                        }
                    )
                    patterns.append(pattern)
                    
            except Exception as e:
                logger.debug(f"Error searching workflow {workflow_file}: {e}")
                continue
        
        return patterns
    
    def _search_sprs(
        self,
        query: str,
        search_mode: str
    ) -> List[CodebasePattern]:
        """Search SPR definitions for relevant patterns"""
        patterns = []
        
        if not self.spr_manager:
            return patterns
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        try:
            # Get all SPRs from manager
            spr_definitions = self.spr_manager.get_all_sprs()
            
            for spr_id, spr_data in spr_definitions.items():
                spr_name = spr_data.get("name", spr_id)
                spr_def = spr_data.get("definition", "")
                
                combined_text = f"{spr_name} {spr_def}".lower()
                relevance = self._calculate_relevance(
                    combined_text, query_terms, query_lower, search_mode
                )
                
                if relevance > 0.3:
                    pattern = CodebasePattern(
                        pattern_type="spr",
                        name=spr_name,
                        file_path=Path("knowledge_graph/spr_definitions_tv.json"),
                        relevance_score=relevance,
                        description=spr_def,
                        spr_references=[spr_id],
                        implementation_details={
                            "spr_id": spr_id,
                            "category": spr_data.get("category", "unknown"),
                            "blueprint_details": spr_data.get("blueprint_details", {})
                        }
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            logger.debug(f"Error searching SPRs: {e}")
        
        return patterns
    
    def _search_specifications(
        self,
        query: str,
        search_mode: str
    ) -> List[CodebasePattern]:
        """Search specification markdown files"""
        patterns = []
        specs_dir = self.codebase_root / "specifications"
        
        if not specs_dir.exists():
            return patterns
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for spec_file in specs_dir.rglob("*.md"):
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title and first paragraph
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else spec_file.stem
                
                # First 500 chars for description
                description = content[:500].replace('\n', ' ').strip()
                
                combined_text = f"{title} {description}".lower()
                relevance = self._calculate_relevance(
                    combined_text, query_terms, query_lower, search_mode
                )
                
                if relevance > 0.3:
                    pattern = CodebasePattern(
                        pattern_type="specification",
                        name=title,
                        file_path=spec_file,
                        relevance_score=relevance,
                        description=description,
                        key_excerpts=[content[:200]]  # First 200 chars as excerpt
                    )
                    patterns.append(pattern)
                    
            except Exception as e:
                logger.debug(f"Error searching spec {spec_file}: {e}")
                continue
        
        return patterns
    
    def _calculate_relevance(
        self,
        text: str,
        query_terms: Set[str],
        query_lower: str,
        search_mode: str
    ) -> float:
        """Calculate relevance score between text and query"""
        if isinstance(text, str):
            text_lower = text.lower()
        else:
            text_lower = str(text).lower()
        
        if search_mode == "exact":
            # Exact match gets highest score
            if query_lower in text_lower:
                return 1.0
            return 0.0
        
        elif search_mode == "fuzzy":
            # Fuzzy matching with word overlap
            text_terms = set(text_lower.split())
            overlap = len(query_terms & text_terms)
            if len(query_terms) == 0:
                return 0.0
            return overlap / len(query_terms)
        
        else:  # semantic (default)
            # Semantic matching: term overlap + substring matching
            text_terms = set(text_lower.split())
            
            # Term overlap score
            overlap = len(query_terms & text_terms)
            term_score = overlap / max(len(query_terms), 1)
            
            # Substring match score
            substring_score = 0.0
            for term in query_terms:
                if term in text_lower:
                    substring_score += 0.1
            
            # Combined score (weighted)
            relevance = (term_score * 0.7) + min(substring_score, 0.3)
            return min(relevance, 1.0)
    
    def _score_patterns(
        self,
        patterns: List[CodebasePattern],
        query: str
    ) -> List[CodebasePattern]:
        """Additional scoring based on pattern relationships and context"""
        # Could enhance with:
        # - SPR relationship weighting
        # - Usage frequency
        # - Recent modification dates
        # - Implementation completeness
        return patterns
    
    def synthesize_from_patterns(
        self,
        problem_description: str,
        external_knowledge: Dict[str, Any],
        codebase_patterns: List[CodebasePattern],
        synthesis_mode: str = "hybrid"  # "codebase_led", "external_led", "hybrid"
    ) -> Dict[str, Any]:
        """
        Synthesize a solution by combining external knowledge with internal codebase patterns.
        
        This creates a "best of both worlds" solution that:
        - Uses external knowledge for domain expertise
        - Uses codebase patterns for proven implementation approaches
        - Creates novel combinations that are both innovative and grounded
        
        Args:
            problem_description: The problem to solve
            external_knowledge: External research/knowledge (from Phase A)
            codebase_patterns: Patterns found in codebase
            synthesis_mode: How to combine (codebase_led, external_led, hybrid)
            
        Returns:
            Synthesized solution dictionary
        """
        logger.info(f"Synthesizing solution from {len(codebase_patterns)} patterns (mode: {synthesis_mode})")
        
        # Extract key components
        codebase_components = [p.name for p in codebase_patterns]
        
        # Identify novel combinations
        novel_combinations = []
        if len(codebase_patterns) >= 2:
            # Suggest combining patterns from different areas
            for i, p1 in enumerate(codebase_patterns[:3]):
                for p2 in codebase_patterns[i+1:min(i+3, len(codebase_patterns))]:
                    if p1.pattern_type != p2.pattern_type:
                        novel_combinations.append(
                            f"Combine {p1.pattern_type} '{p1.name}' with {p2.pattern_type} '{p2.name}'"
                        )
        
        # Generate implementation suggestions
        implementation_suggestions = []
        for pattern in codebase_patterns[:5]:  # Top 5
            if pattern.pattern_type == "class":
                implementation_suggestions.append(
                    f"Use pattern from {pattern.file_path.name}:{pattern.name} "
                    f"(relevance: {pattern.relevance_score:.2f})"
                )
            elif pattern.pattern_type == "workflow":
                implementation_suggestions.append(
                    f"Adapt workflow {pattern.name} for this problem"
                )
        
        # SPR candidates from novel patterns
        spr_candidates = []
        if novel_combinations:
            domain_keywords = set(problem_description.lower().split()[:5])
            spr_name = "".join([w.capitalize() for w in domain_keywords if len(w) > 4]) + "SynthesiS"
            spr_candidates.append({
                "name": spr_name,
                "pattern": novel_combinations[0] if novel_combinations else "Hybrid pattern",
                "codebase_sources": codebase_components[:3],
                "external_sources": external_knowledge.get("summary", "External research")
            })
        
        return {
            "synthesized_solution": (
                f"Solution combining external knowledge with {len(codebase_patterns)} "
                f"internal codebase patterns. Mode: {synthesis_mode}"
            ),
            "codebase_components": codebase_components,
            "external_components": external_knowledge.get("summary", "External research"),
            "novel_combinations": novel_combinations,
            "implementation_suggestions": implementation_suggestions,
            "spr_candidates": spr_candidates,
            "synthesis_mode": synthesis_mode,
            "confidence": min(0.85, 0.5 + (len(codebase_patterns) * 0.05))  # Higher with more patterns
        }
    
    def validate_against_patterns(
        self,
        strategy: Dict[str, Any],
        required_patterns: List[str] = None
    ) -> Dict[str, Any]:
        """
        Check if strategy aligns with existing codebase patterns.
        
        Args:
            strategy: Strategy to validate
            required_patterns: Patterns that must be present (e.g., "IAR compliance")
            
        Returns:
            Validation result with alignment scores
        """
        if required_patterns is None:
            required_patterns = ["IAR compliance", "SPR integration", "workflow compatibility"]
        
        alignment_scores = {}
        strategy_text = str(strategy).lower()
        
        for pattern_name in required_patterns:
            # Search codebase for this pattern
            pattern_results = self.search_codebase_for_patterns(
                query=pattern_name,
                pattern_types=["class", "function", "workflow"],
                max_results=5
            )
            
            # Check if strategy mentions or could use these patterns
            mentions = pattern_name.lower() in strategy_text
            has_related_patterns = len(pattern_results) > 0
            
            alignment_scores[pattern_name] = {
                "mentioned": mentions,
                "related_patterns_found": has_related_patterns,
                "alignment_score": 0.5 if mentions else (0.3 if has_related_patterns else 0.1)
            }
        
        overall_alignment = sum(
            s["alignment_score"] for s in alignment_scores.values()
        ) / len(alignment_scores) if alignment_scores else 0.0
        
        return {
            "overall_alignment": overall_alignment,
            "pattern_alignment": alignment_scores,
            "recommendations": [
                f"Consider integrating {p}" for p, s in alignment_scores.items()
                if s["alignment_score"] < 0.5
            ]
        }

