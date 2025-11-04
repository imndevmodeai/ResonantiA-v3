"""
Autopoietic Self-Analysis System
The Mirror of Truth - Map vs Territory Comparison

This module implements the Insight Solidification Engine pattern to analyze
the gap between ArchE's specifications (the map) and actual implementation 
(the territory), generating actionable insights for system evolution.

Philosophical Foundation:
- As Above (Specifications), So Below (Implementation)
- The system that can see itself can improve itself
- Truth emerges from rigorous comparison and reflection
- Quantum superposition for uncertainty (not binary true/false)

Quantum Enhancement:
Instead of boolean states (True/False/None), we use quantum probability states
where uncertainty is quantified as a superposition: |ψ⟩ = α|0⟩ + β|1⟩
This allows us to track confidence levels and collapse to certainty through analysis.
"""

import json
import logging
import re
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import numpy as np

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename


logger = logging.getLogger(__name__)

# Quantum Utils Integration
try:
    from .quantum_utils import superposition_state, calculate_shannon_entropy
    QUANTUM_UTILS_AVAILABLE = True
except ImportError:
    QUANTUM_UTILS_AVAILABLE = False
    logger.warning("quantum_utils not available, using classical probability")


class QuantumProbability:
    """
    Quantum probability state for uncertain analysis results.
    
    Instead of True/False/None, we track probability amplitude.
    |ψ⟩ = √p|1⟩ + √(1-p)|0⟩ where p is probability of True state.
    """
    
    def __init__(self, probability: float, evidence: List[str] = None):
        """
        Initialize quantum probability state.
        
        Args:
            probability: Probability value between 0.0 and 1.0
            evidence: List of evidence factors contributing to this probability
        """
        self.probability = max(0.0, min(1.0, probability))
        self.evidence = evidence or []
        self.collapsed = probability in (0.0, 1.0)
        
    def collapse(self) -> bool:
        """
        Collapse the quantum state to boolean (measurement).
        
        Returns:
            Boolean result based on probability threshold
        """
        self.collapsed = True
        return self.probability >= 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary for serialization."""
        return {
            "probability": self.probability,
            "collapsed": self.collapsed,
            "boolean_value": self.collapse() if not self.collapsed else self.probability >= 0.5,
            "evidence": self.evidence,
            "uncertainty": 1.0 - abs(self.probability - 0.5) * 2,  # 0 = certain, 1 = maximum uncertainty
            "quantum_state": f"|ψ⟩ = {np.sqrt(self.probability):.3f}|1⟩ + {np.sqrt(1-self.probability):.3f}|0⟩"
        }
    
    def __repr__(self) -> str:
        return f"QuantumProbability({self.probability:.3f}, collapsed={self.collapsed})"
    
    def __float__(self) -> float:
        return self.probability
    
    def __bool__(self) -> bool:
        return self.collapse()
    
    @staticmethod
    def certain_true() -> 'QuantumProbability':
        """Create a collapsed certain True state."""
        return QuantumProbability(1.0, ["direct_observation"])
    
    @staticmethod
    def certain_false() -> 'QuantumProbability':
        """Create a collapsed certain False state."""
        return QuantumProbability(0.0, ["direct_observation"])
    
    @staticmethod
    def uncertain(probability: float = 0.5, evidence: List[str] = None) -> 'QuantumProbability':
        """Create an uncertain superposition state."""
        return QuantumProbability(probability, evidence or ["insufficient_data"])


logger = logging.getLogger(__name__)


@dataclass
class ComponentGap:
    """Represents a gap between specification and implementation with quantum confidence."""
    component_name: str
    gap_type: str  # "missing", "partial", "misaligned", "complete"
    specification_path: str
    implementation_path: Optional[str]
    gap_description: str
    confidence_score: float  # Classical alignment score for backward compatibility
    quantum_confidence: Dict[str, Any] = field(default_factory=dict)  # Quantum probability state
    severity: str = "medium"  # "critical", "high", "medium", "low"
    recommended_action: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IAREntry:
    """Integrated Action Reflection entry for transformation tracking."""
    timestamp: str
    phase: str
    action_type: str
    intention: str
    action: str
    reflection: str
    confidence: float
    metadata: Dict[str, Any]
    
    def to_json(self) -> str:
        """Convert to JSON string for logging."""
        return json.dumps(asdict(self), ensure_ascii=False)


class AutopoieticSelfAnalysis:
    """
    The Mirror of Truth - Analyzes the system's own coherence.
    
    This class implements automated map-territory comparison, scanning
    specifications against actual implementations to identify gaps,
    misalignments, and opportunities for evolution.
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize the self-analysis system.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.arche_root = self.project_root / "Three_PointO_ArchE"
        self.spec_root = self.project_root / "specifications"
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # IAR log file
        self.iar_log_path = self.logs_dir / "autopoietic_transformation_iar.jsonl"
        
        # Analysis results
        self.gaps: List[ComponentGap] = []
        self.analysis_summary: Dict[str, Any] = {}
        
        # Component mappings
        self.spec_to_impl: Dict[str, str] = {}
        self.impl_to_spec: Dict[str, str] = {}
        
        logger.info(f"[AutopoieticSelfAnalysis] Initialized with root: {self.project_root}")
        self._log_iar(
            phase="initialization",
            action_type="system_startup",
            intention="Initialize self-analysis infrastructure",
            action="Created AutopoieticSelfAnalysis instance",
            reflection="Self-analysis system ready to compare map and territory",
            confidence=1.0,
            metadata={"project_root": str(self.project_root)}
        )
    
    def _log_iar(
        self,
        phase: str,
        action_type: str,
        intention: str,
        action: str,
        reflection: str,
        confidence: float,
        metadata: Dict[str, Any] = None
    ):
        """Log an IAR entry to the transformation log."""
        entry = IAREntry(
            timestamp=now_iso(),
            phase=phase,
            action_type=action_type,
            intention=intention,
            action=action,
            reflection=reflection,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        with open(self.iar_log_path, 'a') as f:
            f.write(entry.to_json() + '\n')
        
        logger.info(f"[IAR] {phase}/{action_type}: {reflection}")
    
    def discover_specifications(self) -> Dict[str, Path]:
        """
        Discover all specification files.
        
        Returns:
            Dict mapping component names to specification file paths
        """
        specs = {}
        
        if not self.spec_root.exists():
            logger.warning(f"Specification directory not found: {self.spec_root}")
            return specs
        
        for spec_file in self.spec_root.glob("*.md"):
            component_name = spec_file.stem
            specs[component_name] = spec_file
        
        self._log_iar(
            phase="discovery",
            action_type="scan_specifications",
            intention="Discover all specification documents in the map",
            action=f"Scanned {self.spec_root} for specification files",
            reflection=f"Found {len(specs)} specification documents",
            confidence=1.0,
            metadata={"specs_found": list(specs.keys())}
        )
        
        return specs
    
    def discover_implementations(self) -> Dict[str, Path]:
        """
        Discover all implementation files.
        
        Returns:
            Dict mapping component names to implementation file paths
        """
        impls = {}
        
        if not self.arche_root.exists():
            logger.warning(f"Implementation directory not found: {self.arche_root}")
            return impls
        
        for impl_file in self.arche_root.glob("*.py"):
            if impl_file.name == "__init__.py":
                continue
            component_name = impl_file.stem
            impls[component_name] = impl_file
        
        self._log_iar(
            phase="discovery",
            action_type="scan_implementations",
            intention="Discover all implementation files in the territory",
            action=f"Scanned {self.arche_root} for Python implementation files",
            reflection=f"Found {len(impls)} implementation files",
            confidence=1.0,
            metadata={"impls_found": list(impls.keys())}
        )
        
        return impls
    
    def extract_spec_requirements(self, spec_path: Path) -> Dict[str, Any]:
        """
        Extract requirements from a specification file.
        
        Args:
            spec_path: Path to the specification file
            
        Returns:
            Dict containing extracted requirements
        """
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        requirements = {
            "classes": set(),
            "functions": set(),
            "methods": set(),
            "capabilities": [],
            "integrations": [],
            "has_core_class": False,
            "core_class_name": None
        }
        
        # Extract class mentions
        class_patterns = [
            r'class\s+`(\w+)`',
            r'`(\w+)`\s+[Cc]lass',
            r'### Core Class:\s+`(\w+)`',
            r'## .*:\s+`(\w+)`'
        ]
        
        for pattern in class_patterns:
            matches = re.findall(pattern, content)
            requirements["classes"].update(matches)
        
        # Extract function mentions
        func_patterns = [
            r'def\s+`(\w+)`',
            r'`(\w+)\(\)`',
            r'function\s+`(\w+)`',
        ]
        
        for pattern in func_patterns:
            matches = re.findall(pattern, content)
            requirements["functions"].update(matches)
        
        # Extract capabilities from "Key Capabilities" sections
        capability_section = re.search(
            r'## Key Capabilities(.*?)(?=##|\Z)',
            content,
            re.DOTALL
        )
        if capability_section:
            capabilities = re.findall(r'[-*]\s+\*\*(.*?)\*\*', capability_section.group(1))
            requirements["capabilities"] = capabilities
        
        # Extract integration points
        integration_section = re.search(
            r'## Integration Points(.*?)(?=##|\Z)',
            content,
            re.DOTALL
        )
        if integration_section:
            integrations = re.findall(r'[-*]\s+\*\*(.*?)\*\*', integration_section.group(1))
            requirements["integrations"] = integrations
        
        # Check for core class specification
        core_class_match = re.search(r'### Core (?:Class|Function):\s+`(\w+)`', content)
        if core_class_match:
            requirements["has_core_class"] = True
            requirements["core_class_name"] = core_class_match.group(1)
        
        return requirements
    
    def analyze_implementation(self, impl_path: Path) -> Dict[str, Any]:
        """
        Analyze an implementation file with quantum probability states.
        
        Args:
            impl_path: Path to the implementation file
            
        Returns:
            Dict containing implementation analysis with quantum states
        """
        try:
            with open(impl_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                "classes": set(),
                "functions": set(),
                "methods": defaultdict(set),
                "imports": set(),
                "line_count": len(content.split('\n'))
            }
            
            # Iterate through top-level nodes to distinguish functions from methods
            # Ensure tree.body is iterable (should be a list, but defensive check)
            if not hasattr(tree, 'body') or not isinstance(tree.body, (list, tuple)):
                raise ValueError(f"AST tree.body is not a list/tuple in {impl_path}")
            
            for node in tree.body:
                try:
                    if isinstance(node, ast.ClassDef):
                        analysis["classes"].add(node.name)
                        # Ensure node.body is iterable (list of statements)
                        if hasattr(node, 'body') and isinstance(node.body, (list, tuple)):
                            for item in node.body:
                                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                    analysis["methods"][node.name].add(item.name)
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        analysis["functions"].add(node.name)
                    elif isinstance(node, ast.Import):
                        # Ensure node.names is a list/sequence (not bool) and is iterable
                        if hasattr(node, 'names') and node.names:
                            # Explicit type check: node.names must be iterable (list, tuple, etc.)
                            if isinstance(node.names, (list, tuple)):
                                for alias in node.names:
                                    if isinstance(alias, ast.alias) and hasattr(alias, 'name') and alias.name:
                                        # Only add string names (exclude None, bool, etc.)
                                        if isinstance(alias.name, str):
                                            analysis["imports"].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        # Ensure node.module is a string (not bool)
                        if node.module and isinstance(node.module, str):
                            analysis["imports"].add(node.module)
                        # Also handle ImportFrom names (for 'from X import Y' patterns)
                        if hasattr(node, 'names') and node.names and isinstance(node.names, (list, tuple)):
                            for alias in node.names:
                                if isinstance(alias, ast.alias) and hasattr(alias, 'name') and alias.name:
                                    if isinstance(alias.name, str):
                                        analysis["imports"].add(alias.name)
                except Exception as node_error:
                    logger.warning(f"Error processing node in {impl_path}: {node_error}")
                    continue

            # Quantum IAR Compliance Analysis
            iar_evidence = []
            iar_probability = 0.0
            
            # Ensure imports is a set of strings (handle cases where it might not be)
            # Filter out any non-string values that might have slipped through
            import_strings = set()
            for imp in analysis["imports"]:
                try:
                    # Only process string values, skip booleans, None, etc.
                    if isinstance(imp, str) and imp:
                        import_strings.add(imp.lower())
                    elif imp and not isinstance(imp, bool):
                        # Convert to string if it's not a bool
                        import_strings.add(str(imp).lower())
                except (TypeError, AttributeError) as e:
                    logger.warning(f"Error processing import '{imp}' (type: {type(imp)}): {e}")
                    continue
            
            if any("iar" in imp for imp in import_strings):
                iar_probability += 0.5
                iar_evidence.append("iar_imports_detected")
            
            if any("thought_trail" in imp for imp in import_strings):
                iar_probability += 0.3
                iar_evidence.append("thought_trail_integration")
            
            # Check for reflection methods - safely convert sets to strings
            functions_str = str(list(analysis["functions"])) if isinstance(analysis["functions"], (set, list, tuple)) else str(analysis["functions"])
            methods_str = str(dict(analysis["methods"])) if isinstance(analysis["methods"], dict) else str(analysis["methods"])
            if "reflection" in functions_str.lower() or "reflection" in methods_str.lower():
                iar_probability += 0.2
                iar_evidence.append("reflection_methods_found")
            
            analysis["has_iar_compliance"] = QuantumProbability(
                min(1.0, iar_probability),
                iar_evidence or ["no_iar_indicators"]
            )
            
            # Quantum SPR Reference Analysis
            spr_evidence = []
            spr_probability = 0.0
            
            # Use the same import_strings set
            if any("spr_manager" in imp for imp in import_strings):
                spr_probability += 0.5
                spr_evidence.append("spr_manager_imported")
            
            if "SPRManager" in analysis["classes"]:
                spr_probability += 0.5
                spr_evidence.append("spr_manager_class_found")
            
            # Ensure functions is a set before iterating
            function_strings = set()
            for f in analysis["functions"]:
                try:
                    if isinstance(f, str) and f:
                        function_strings.add(f.lower())
                    elif f and not isinstance(f, bool):
                        function_strings.add(str(f).lower())
                except (TypeError, AttributeError):
                    continue
            if any("spr" in f for f in function_strings):
                spr_probability += 0.3
                spr_evidence.append("spr_functions_found")
            
            analysis["has_spr_references"] = QuantumProbability(
                min(1.0, spr_probability),
                spr_evidence or ["no_spr_indicators"]
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze {impl_path}: {e}")
            # When we can't parse, we're in maximum uncertainty (superposition)
            return {
                "classes": set(),
                "functions": set(),
                "methods": defaultdict(set),
                "imports": set(),
                "has_iar_compliance": QuantumProbability.uncertain(
                    0.3,  # Slight bias toward not having it if unparseable
                    ["parse_error", f"exception: {type(e).__name__}"]
                ),
                "has_spr_references": QuantumProbability.uncertain(
                    0.3,
                    ["parse_error", f"exception: {type(e).__name__}"]
                ),
                "line_count": 0,
                "error": str(e)
            }
    
    def compare_component(
        self,
        component_name: str,
        spec_path: Path,
        impl_path: Optional[Path]
    ) -> ComponentGap:
        """
        Compare a single component's specification against its implementation.
        
        Args:
            component_name: Name of the component
            spec_path: Path to specification
            impl_path: Path to implementation (if exists)
            
        Returns:
            ComponentGap describing the alignment
        """
        spec_reqs = self.extract_spec_requirements(spec_path)
        
        if impl_path is None or not impl_path.exists():
            return ComponentGap(
                component_name=component_name,
                gap_type="missing",
                specification_path=str(spec_path),
                implementation_path=None,
                gap_description=f"Component specified but not implemented",
                confidence_score=1.0,
                severity="critical",
                recommended_action=f"Implement {component_name} according to specification",
                evidence={"spec_requirements": str(spec_reqs)}
            )
        
        impl_analysis = self.analyze_implementation(impl_path)
        
        # Ensure we're working with sets (handle error cases)
        spec_classes = set(spec_reqs.get("classes", set()) or set())
        spec_functions = set(spec_reqs.get("functions", set()) or set())
        impl_classes = set(impl_analysis.get("classes", set()) or set())
        impl_functions = set(impl_analysis.get("functions", set()) or set())
        
        # Calculate alignment score
        missing_classes = spec_classes - impl_classes
        missing_functions = spec_functions - impl_functions
        
        total_required = len(spec_reqs["classes"]) + len(spec_reqs["functions"])
        total_missing = len(missing_classes) + len(missing_functions)
        
        if total_required == 0:
            alignment_score = 1.0
        else:
            alignment_score = 1.0 - (total_missing / total_required)
        
        # Determine gap type and severity
        if alignment_score >= 0.9:
            gap_type = "complete"
            severity = "low"
        elif alignment_score >= 0.7:
            gap_type = "partial"
            severity = "medium"
        else:
            gap_type = "misaligned"
            severity = "high"
        
        gap_description_parts = []
        if missing_classes:
            gap_description_parts.append(f"Missing classes: {', '.join(missing_classes)}")
        if missing_functions:
            gap_description_parts.append(f"Missing functions: {', '.join(missing_functions)}")
        
        if not gap_description_parts:
            gap_description = "Implementation aligns well with specification"
        else:
            gap_description = "; ".join(gap_description_parts)
        
        # Create quantum confidence state
        quantum_confidence = {
            "alignment_probability": alignment_score,
            "iar_compliance": impl_analysis.get("has_iar_compliance", QuantumProbability.uncertain()).to_dict(),
            "spr_integration": impl_analysis.get("has_spr_references", QuantumProbability.uncertain()).to_dict(),
            "completeness": {
                "probability": alignment_score,
                "evidence": [
                    f"classes_complete: {len(missing_classes) == 0}",
                    f"functions_complete: {len(missing_functions) == 0}"
                ],
                "uncertainty": 1.0 - alignment_score if total_required > 0 else 0.0
            }
        }
        
        return ComponentGap(
            component_name=component_name,
            gap_type=gap_type,
            specification_path=str(spec_path),
            implementation_path=str(impl_path),
            gap_description=gap_description,
            confidence_score=alignment_score,
            quantum_confidence=quantum_confidence,
            severity=severity,
            recommended_action=f"Review and implement missing elements" if total_missing > 0 else "Maintain and enhance",
            evidence={
                "spec_requirements": {
                    "classes": list(spec_reqs["classes"]),
                    "functions": list(spec_reqs["functions"]),
                    "capabilities": spec_reqs["capabilities"]
                },
                "impl_analysis": {
                    "classes": list(impl_analysis["classes"]),
                    "functions": list(impl_analysis["functions"]),
                    "line_count": impl_analysis["line_count"]
                },
                "missing_classes": list(missing_classes),
                "missing_functions": list(missing_functions),
                "spec_classes": list(spec_classes),
                "impl_classes": list(impl_classes)
            }
        )
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run complete map-territory comparison analysis.
        
        Returns:
            Comprehensive analysis summary
        """
        self._log_iar(
            phase="analysis",
            action_type="full_scan_initiated",
            intention="Execute comprehensive map-territory comparison",
            action="Beginning full system analysis",
            reflection="Scanning all specifications and implementations",
            confidence=1.0,
            metadata={}
        )
        
        specs = self.discover_specifications()
        impls = self.discover_implementations()
        
        # Compare each specification against its implementation
        for component_name, spec_path in specs.items():
            impl_path = impls.get(component_name)
            gap = self.compare_component(component_name, spec_path, impl_path)
            self.gaps.append(gap)
        
        # Identify implemented components without specifications
        for component_name, impl_path in impls.items():
            if component_name not in specs:
                gap = ComponentGap(
                    component_name=component_name,
                    gap_type="undocumented",
                    specification_path="N/A",
                    implementation_path=str(impl_path),
                    gap_description="Implementation exists without specification",
                    confidence_score=0.5,
                    severity="medium",
                    recommended_action="Create specification or deprecate implementation",
                    evidence={}
                )
                self.gaps.append(gap)
        
        # Generate summary
        self.analysis_summary = self._generate_summary()
        
        self._log_iar(
            phase="analysis",
            action_type="full_scan_completed",
            intention="Complete comprehensive analysis",
            action=f"Analyzed {len(specs)} specifications and {len(impls)} implementations",
            reflection=f"Found {len(self.gaps)} gaps with {self.analysis_summary['critical_count']} critical issues",
            confidence=0.95,
            metadata=self.analysis_summary
        )
        
        return self.analysis_summary
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate analysis summary statistics."""
        summary = {
            "total_components_analyzed": len(self.gaps),
            "complete_count": sum(1 for g in self.gaps if g.gap_type == "complete"),
            "partial_count": sum(1 for g in self.gaps if g.gap_type == "partial"),
            "missing_count": sum(1 for g in self.gaps if g.gap_type == "missing"),
            "misaligned_count": sum(1 for g in self.gaps if g.gap_type == "misaligned"),
            "undocumented_count": sum(1 for g in self.gaps if g.gap_type == "undocumented"),
            "critical_count": sum(1 for g in self.gaps if g.severity == "critical"),
            "high_count": sum(1 for g in self.gaps if g.severity == "high"),
            "medium_count": sum(1 for g in self.gaps if g.severity == "medium"),
            "low_count": sum(1 for g in self.gaps if g.severity == "low"),
            "average_alignment": sum(g.confidence_score for g in self.gaps) / len(self.gaps) if self.gaps else 0.0,
            "timestamp": now_iso()
        }
        
        return summary
    
    def get_critical_gaps(self) -> List[ComponentGap]:
        """Get all critical severity gaps."""
        return [g for g in self.gaps if g.severity == "critical"]
    
    def get_high_priority_gaps(self) -> List[ComponentGap]:
        """Get all high and critical severity gaps."""
        return [g for g in self.gaps if g.severity in ("critical", "high")]
    
    def generate_report(self, output_path: Path = None) -> str:
        """
        Generate a human-readable analysis report.
        
        Args:
            output_path: Optional path to save the report
            
        Returns:
            The report as a string
        """
        report_lines = [
            "=" * 80,
            "AUTOPOIETIC SELF-ANALYSIS REPORT",
            "Map vs Territory Comparison",
            "=" * 80,
            "",
            f"Analysis Date: {self.analysis_summary.get('timestamp', 'N/A')}",
            f"Project Root: {self.project_root}",
            "",
            "SUMMARY STATISTICS",
            "-" * 80,
            f"Total Components Analyzed: {self.analysis_summary.get('total_components_analyzed', 0)}",
            f"Complete Implementations: {self.analysis_summary.get('complete_count', 0)}",
            f"Partial Implementations: {self.analysis_summary.get('partial_count', 0)}",
            f"Missing Implementations: {self.analysis_summary.get('missing_count', 0)}",
            f"Misaligned Implementations: {self.analysis_summary.get('misaligned_count', 0)}",
            f"Undocumented Implementations: {self.analysis_summary.get('undocumented_count', 0)}",
            "",
            f"Critical Issues: {self.analysis_summary.get('critical_count', 0)}",
            f"High Priority Issues: {self.analysis_summary.get('high_count', 0)}",
            f"Medium Priority Issues: {self.analysis_summary.get('medium_count', 0)}",
            f"Average Alignment Score: {self.analysis_summary.get('average_alignment', 0):.2%}",
            "",
            "CRITICAL GAPS (Requires Immediate Attention)",
            "-" * 80
        ]
        
        critical_gaps = self.get_critical_gaps()
        if critical_gaps:
            for gap in critical_gaps:
                report_lines.extend([
                    f"",
                    f"Component: {gap.component_name}",
                    f"  Type: {gap.gap_type}",
                    f"  Description: {gap.gap_description}",
                    f"  Recommended Action: {gap.recommended_action}",
                ])
        else:
            report_lines.append("  No critical gaps found.")
        
        report_lines.extend([
            "",
            "HIGH PRIORITY GAPS",
            "-" * 80
        ])
        
        high_gaps = [g for g in self.gaps if g.severity == "high"]
        if high_gaps:
            for gap in high_gaps:
                report_lines.extend([
                    f"",
                    f"Component: {gap.component_name}",
                    f"  Type: {gap.gap_type}",
                    f"  Description: {gap.gap_description}",
                    f"  Alignment Score: {gap.confidence_score:.2%}",
                ])
        else:
            report_lines.append("  No high priority gaps found.")
        
        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80
        ])
        
        report = "\n".join(report_lines)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to {output_path}")
        
        return report
    
    def export_gaps_json(self, output_path: Path = None) -> str:
        """
        Export gaps analysis as JSON.
        
        Args:
            output_path: Optional path to save JSON
            
        Returns:
            JSON string
        """
        export_data = {
            "summary": self.analysis_summary,
            "gaps": [asdict(gap) for gap in self.gaps]
        }
        
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
            logger.info(f"JSON export saved to {output_path}")
        
        return json_str
    
    def verify_system_alignment(self) -> Dict[str, Any]:
        """
        System-wide Above↔Below verification.
        
        Provides comprehensive system alignment check returning structured
        results for system-wide resonance verification.
        
        Returns:
            Dictionary with system alignment status, component details,
            and resonance status
        """
        logger.info("[AutopoieticSelfAnalysis] Verifying system-wide alignment")
        
        # Run full analysis if not already done
        if not self.gaps:
            self.run_full_analysis()
        
        # Calculate component alignments
        component_alignments = []
        for gap in self.gaps:
            alignment_confidence = QuantumProbability(
                probability=gap.confidence_score,
                evidence=gap.evidence.get('alignment_evidence', [])
            )
            
            component_alignments.append({
                "component": gap.component_name,
                "alignment": float(alignment_confidence),
                "gap_type": gap.gap_type,
                "severity": gap.severity,
                "evidence": gap.evidence,
                "recommendations": [gap.recommended_action] if gap.severity in ("critical", "high") else []
            })
        
        # Calculate average alignment
        if component_alignments:
            avg_alignment = sum(c["alignment"] for c in component_alignments) / len(component_alignments)
        else:
            avg_alignment = 0.0
        
        # Determine resonance status
        if avg_alignment >= 0.85:
            resonance_status = "ACHIEVED"
        elif avg_alignment >= 0.70:
            resonance_status = "PARTIAL"
        else:
            resonance_status = "BREAK_DETECTED"
        
        # Generate IAR
        self._log_iar(
            phase="verification",
            action_type="system_alignment_check",
            intention="Verify system-wide Above↔Below alignment",
            action="Completed system alignment verification",
            reflection=f"System alignment: {resonance_status} (average: {avg_alignment:.2%})",
            confidence=avg_alignment,
            metadata={
                "components_checked": len(component_alignments),
                "resonance_status": resonance_status,
                "average_alignment": avg_alignment
            }
        )
        
        return {
            "system_alignment": avg_alignment,
            "components": component_alignments,
            "resonance_status": resonance_status,
            "summary": {
                "total_components": len(component_alignments),
                "aligned_components": sum(1 for c in component_alignments if c["alignment"] >= 0.85),
                "misaligned_components": sum(1 for c in component_alignments if c["alignment"] < 0.85),
                "critical_issues": sum(1 for c in component_alignments if c["severity"] == "critical"),
                "average_alignment": avg_alignment,
                "quantum_confidence": QuantumProbability(
                    probability=avg_alignment,
                    evidence=[
                        f"{len(component_alignments)}_components_verified",
                        f"resonance_status_{resonance_status.lower()}"
                    ]
                ).to_dict()
            },
            "recommendations": self._generate_alignment_recommendations(component_alignments),
            "timestamp": now_iso()
        }
    
    def _generate_alignment_recommendations(
        self,
        component_alignments: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for improving system alignment."""
        recommendations = []
        
        # Critical issues
        critical_components = [c for c in component_alignments if c["severity"] == "critical"]
        if critical_components:
            recommendations.append(
                f"{len(critical_components)} critical alignment issues require immediate attention"
            )
        
        # Low alignment components
        low_alignment = [c for c in component_alignments if c["alignment"] < 0.70]
        if low_alignment:
            recommendations.append(
                f"{len(low_alignment)} components below 70% alignment threshold"
            )
        
        # Missing implementations
        missing = [c for c in component_alignments if c["gap_type"] == "missing"]
        if missing:
            recommendations.append(
                f"{len(missing)} components specified but not implemented"
            )
        
        # Undocumented implementations
        undocumented = [c for c in component_alignments if c["gap_type"] == "undocumented"]
        if undocumented:
            recommendations.append(
                f"{len(undocumented)} implementations lack specifications"
            )
        
        if not recommendations:
            recommendations.append("System alignment is within acceptable thresholds")
        
        return recommendations


def main():
    """Run self-analysis and generate reports."""
    analysis = AutopoieticSelfAnalysis()
    
    print("🔍 Initiating Autopoietic Self-Analysis...")
    print("   Comparing the Map (specifications) with the Territory (code)...")
    print()
    
    summary = analysis.run_full_analysis()
    
    print("✓ Analysis Complete!")
    print()
    
    # Generate and display report
    report = analysis.generate_report()
    print(report)
    
    # Save reports
    timestamp = format_filename()
    report_dir = analysis.project_root / "logs" / "self_analysis"
    report_dir.mkdir(exist_ok=True)
    
    text_report_path = report_dir / f"analysis_report_{timestamp}.txt"
    json_report_path = report_dir / f"analysis_data_{timestamp}.json"
    
    analysis.generate_report(text_report_path)
    analysis.export_gaps_json(json_report_path)
    
    print()
    print(f"📊 Reports saved:")
    print(f"   Text: {text_report_path}")
    print(f"   JSON: {json_report_path}")
    print(f"   IAR Log: {analysis.iar_log_path}")


if __name__ == "__main__":
    main()

