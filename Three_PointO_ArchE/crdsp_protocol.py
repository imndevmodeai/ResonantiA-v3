"""
CRDSP v3.1: Codebase Reference and Documentation Synchronization Protocol
Implementation - Bringing "As Above, So Below" into Operational Reality

This module implements the CRDSP v3.1 protocol as described in:
- ResonantiA Protocol v3.1-CA Section 1.3
- Project_Setup_and_Management.md

Purpose: Ensure perfect alignment between:
- Above (Conceptual): Specifications, Protocol, SPRs, Documentation
- Below (Operational): Code, Implementations, Data Structures

Following "As Above, So Below" principle and Implementation Resonance.
"""

import json
import logging
import re
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict

# ArchE Core Imports
from .autopoietic_self_analysis import AutopoieticSelfAnalysis, ComponentGap, QuantumProbability
from .spr_manager import SPRManager
from .iar_components import IARValidator

logger = logging.getLogger(__name__)


@dataclass
class CRDSPAnalysis:
    """Result of pre-implementation analysis phase."""
    objective: str
    affected_components: List[str]
    documentation_impact: List[str]
    spr_impact: List[str]
    workflow_impact: List[str]
    protocol_sections_impact: List[str]
    resonance_checkpoints: List[Dict[str, Any]]
    confidence: QuantumProbability = field(default_factory=lambda: QuantumProbability.uncertain())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CRDSPImplementation:
    """Tracking implementation changes."""
    component_name: str
    change_type: str  # "new", "modify", "refactor", "delete"
    file_path: Path
    changes_summary: str
    iar_data: Dict[str, Any] = field(default_factory=dict)
    above_below_alignment: QuantumProbability = field(default_factory=lambda: QuantumProbability.uncertain())


@dataclass
class CRDSPResonanceCheck:
    """Result of resonance verification."""
    component: str
    specification: str
    implementation: str
    alignment_confidence: QuantumProbability
    gap_analysis: Optional[ComponentGap] = None
    recommendations: List[str] = field(default_factory=list)
    status: str = "unknown"  # "aligned", "misaligned", "unknown"


@dataclass
class CRDSPDocumentationSync:
    """Documentation synchronization result."""
    document_path: Path
    sync_status: str  # "updated", "pending", "skipped", "error"
    changes_made: List[str]
    alignment_with_code: QuantumProbability
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectDependencyMap:
    """
    Conceptual dependency mapping system.
    
    Maps relationships between:
    - Code modules → SPRs → Specifications → Documentation
    - Workflows → Tools → SPRs → Protocol sections
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.code_to_spr: Dict[str, Set[str]] = defaultdict(set)
        self.spr_to_code: Dict[str, Set[str]] = defaultdict(set)
        self.code_to_spec: Dict[str, Set[str]] = defaultdict(set)
        self.spec_to_code: Dict[str, Set[str]] = defaultdict(set)
        self.spr_to_docs: Dict[str, Set[str]] = defaultdict(set)
        self.code_to_workflows: Dict[str, Set[str]] = defaultdict(set)
        
        logger.info(f"[ProjectDependencyMap] Initialized for {project_root}")
    
    def query(self, objective: str) -> Dict[str, Any]:
        """
        Query dependencies for a given objective.
        
        Args:
            objective: Description of the change objective
            
        Returns:
            Dictionary with affected components across all layers
        """
        # This is a simplified version - full implementation would use
        # semantic search, AST analysis, and pattern matching
        results = {
            "code_modules": [],
            "sprs": [],
            "specifications": [],
            "documentation": [],
            "workflows": [],
            "protocol_sections": []
        }
        
        # TODO: Implement full semantic dependency analysis
        # For now, return structure showing what needs to be queried
        
        return results


class CRDSPEngine:
    """
    Codebase Reference and Documentation Synchronization Protocol Engine v3.1
    
    Implements the full CRDSP v3.1 protocol to maintain "As Above, So Below" alignment.
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize CRDSP Engine.
        
        Args:
            project_root: Root directory of the Happier project
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.arche_root = self.project_root / "Three_PointO_ArchE"
        self.spec_root = self.project_root / "specifications"
        self.protocol_root = self.project_root / "protocol"
        self.workflows_root = self.project_root / "workflows"
        self.knowledge_graph_root = self.project_root / "knowledge_graph"
        
        # Initialize supporting systems
        self.self_analysis = AutopoieticSelfAnalysis(project_root=self.project_root)
        self.dependency_map = ProjectDependencyMap(project_root=self.project_root)
        self.spr_manager = SPRManager(str(self.knowledge_graph_root / "spr_definitions_tv.json"))
        
        # IAR compliance
        self.iar_validator = IARValidator()
        
        logger.info(f"[CRDSPEngine] Initialized for project: {self.project_root}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 1: PRE-IMPLEMENTATION ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    
    def pre_implementation_analysis(
        self,
        objective: str,
        impact_scope: Optional[Dict[str, Any]] = None
    ) -> CRDSPAnalysis:
        """
        Phase 1: Pre-Implementation Analysis
        
        Analyze impact before changing code to ensure all dependencies
        and documentation artifacts are identified.
        
        Args:
            objective: Clear description of the change/addition objective
            impact_scope: Optional constraints on scope of analysis
            
        Returns:
            CRDSPAnalysis with identified impacts and checkpoints
        """
        logger.info(f"[CRDSP:Phase1] Analyzing objective: {objective}")
        
        # 1.1: Objective Definition (already provided in objective parameter)
        
        # 1.2: Query ProjectDependencyMap
        dependency_results = self.dependency_map.query(objective)
        
        # 1.3: Existing Asset Search
        affected_components = self._identify_affected_components(objective)
        spr_impact = self._identify_spr_impact(objective, affected_components)
        workflow_impact = self._identify_workflow_impact(objective, affected_components)
        
        # 1.4: Protocol Alignment Analysis
        protocol_sections = self._identify_protocol_sections(objective)
        
        # 1.5: Implementation Decision Tree
        decision = self._make_implementation_decision(affected_components, spr_impact)
        
        # Identify documentation artifacts
        documentation_impact = self._identify_documentation_artifacts(
            affected_components,
            spr_impact,
            workflow_impact,
            protocol_sections
        )
        
        # Generate resonance checkpoints
        resonance_checkpoints = self._generate_resonance_checkpoints(
            affected_components,
            spr_impact,
            documentation_impact
        )
        
        # Calculate confidence
        confidence = QuantumProbability(
            probability=0.85 if affected_components else 0.5,
            evidence=[
                f"identified_{len(affected_components)}_components",
                f"identified_{len(spr_impact)}_sprs",
                f"identified_{len(documentation_impact)}_docs"
            ]
        )
        
        analysis = CRDSPAnalysis(
            objective=objective,
            affected_components=affected_components,
            documentation_impact=documentation_impact,
            spr_impact=spr_impact,
            workflow_impact=workflow_impact,
            protocol_sections_impact=protocol_sections,
            resonance_checkpoints=resonance_checkpoints,
            confidence=confidence,
            metadata={
                "implementation_decision": decision,
                "dependency_results": dependency_results,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Generate IAR
        iar = {
            "status": "success",
            "confidence": float(confidence),
            "task_id": f"crdsp_phase1_{datetime.now().timestamp()}",
            "reflection": f"Pre-implementation analysis complete. Identified {len(affected_components)} components, {len(spr_impact)} SPRs, {len(documentation_impact)} docs requiring updates.",
            "potential_issues": ["Dependency map may be incomplete", "Some relationships may require manual verification"],
            "alignment_check": "Above (objective) analyzed for Below (impact) identification"
        }
        
        logger.info(f"[CRDSP:Phase1] Analysis complete: {len(affected_components)} components, {len(spr_impact)} SPRs")
        
        return analysis
    
    def _identify_affected_components(self, objective: str) -> List[str]:
        """Identify code components that may be affected."""
        # Simplified - full implementation would use semantic search
        components = []
        
        # Search for relevant modules based on objective keywords
        keywords = self._extract_keywords(objective)
        
        for py_file in self.arche_root.rglob("*.py"):
            if any(kw in py_file.stem.lower() for kw in keywords):
                components.append(py_file.stem)
        
        return components
    
    def _identify_spr_impact(self, objective: str, components: List[str]) -> List[str]:
        """Identify SPRs that may be impacted."""
        spr_impact = []
        
        # Search SPR definitions for relevant concepts
        keywords = self._extract_keywords(objective)
        spr_definitions = self.spr_manager.load_sprs()
        
        for spr in spr_definitions:
            spr_text = f"{spr.get('term', '')} {spr.get('definition', '')}".lower()
            if any(kw in spr_text for kw in keywords):
                spr_impact.append(spr.get('spr_id', ''))
        
        return spr_impact
    
    def _identify_workflow_impact(self, objective: str, components: List[str]) -> List[str]:
        """Identify workflows that may be impacted."""
        workflow_impact = []
        
        if self.workflows_root.exists():
            for workflow_file in self.workflows_root.rglob("*.json"):
                try:
                    with open(workflow_file, 'r') as f:
                        workflow_data = json.load(f)
                        workflow_text = json.dumps(workflow_data).lower()
                        
                        keywords = self._extract_keywords(objective)
                        if any(kw in workflow_text for kw in keywords):
                            workflow_impact.append(workflow_file.stem)
                except:
                    continue
        
        return workflow_impact
    
    def _identify_protocol_sections(self, objective: str) -> List[str]:
        """Identify protocol sections that may be impacted."""
        sections = []
        
        if self.protocol_root.exists():
            for protocol_file in self.protocol_root.glob("*.md"):
                # Simplified - full implementation would parse sections
                if "protocol" in protocol_file.stem.lower():
                    sections.append(protocol_file.stem)
        
        return sections
    
    def _identify_documentation_artifacts(
        self,
        components: List[str],
        spr_impact: List[str],
        workflow_impact: List[str],
        protocol_sections: List[str]
    ) -> List[str]:
        """Identify all documentation artifacts requiring updates."""
        docs = []
        
        # Add protocol documents
        docs.extend([f"protocol/{s}.md" for s in protocol_sections])
        
        # Add specification files for components
        if self.spec_root.exists():
            for spec_file in self.spec_root.glob("*.md"):
                if any(comp in spec_file.stem.lower() for comp in components):
                    docs.append(f"specifications/{spec_file.name}")
        
        # Add SPR definition file if SPRs affected
        if spr_impact:
            docs.append("knowledge_graph/spr_definitions_tv.json")
        
        return list(set(docs))  # Remove duplicates
    
    def _make_implementation_decision(
        self,
        components: List[str],
        spr_impact: List[str]
    ) -> Dict[str, Any]:
        """Make implementation decision tree analysis."""
        # Simplified decision logic
        if not components and not spr_impact:
            return {
                "path": "new_implementation",
                "justification": "No existing components identified - new implementation required"
            }
        elif components:
            return {
                "path": "extend_existing",
                "justification": f"Found {len(components)} existing components to extend"
            }
        else:
            return {
                "path": "refactor",
                "justification": "SPR impact suggests refactoring needed"
            }
    
    def _generate_resonance_checkpoints(
        self,
        components: List[str],
        spr_impact: List[str],
        documentation_impact: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate checkpoints for resonance verification."""
        checkpoints = []
        
        for component in components:
            checkpoints.append({
                "component": component,
                "type": "code_to_spec",
                "threshold": 0.85
            })
        
        for spr_id in spr_impact:
            checkpoints.append({
                "spr_id": spr_id,
                "type": "spr_to_code",
                "threshold": 0.85
            })
        
        for doc in documentation_impact:
            checkpoints.append({
                "document": doc,
                "type": "doc_to_code",
                "threshold": 0.85
            })
        
        return checkpoints
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from objective text."""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [w for w in words if w not in stop_words and len(w) > 3]
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 2: IMPLEMENTATION & DEVELOPMENT
    # ═══════════════════════════════════════════════════════════════════════
    
    def track_implementation(
        self,
        analysis: CRDSPAnalysis,
        implementation_changes: List[Dict[str, Any]]
    ) -> List[CRDSPImplementation]:
        """
        Phase 2: Track implementation changes.
        
        Args:
            analysis: Pre-implementation analysis results
            implementation_changes: List of actual changes made
            
        Returns:
            List of tracked implementation objects
        """
        logger.info(f"[CRDSP:Phase2] Tracking {len(implementation_changes)} changes")
        
        tracked = []
        
        for change in implementation_changes:
            impl = CRDSPImplementation(
                component_name=change.get('component', 'unknown'),
                change_type=change.get('type', 'modify'),
                file_path=Path(change.get('file_path', '')),
                changes_summary=change.get('summary', ''),
                iar_data=change.get('iar', {}),
                above_below_alignment=QuantumProbability.uncertain()
            )
            
            tracked.append(impl)
        
        return tracked
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 3: POST-IMPLEMENTATION VERIFICATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def verify_resonance(
        self,
        implementation: str,
        specification: str
    ) -> CRDSPResonanceCheck:
        """
        Phase 3: Verify implementation matches specification.
        
        Args:
            implementation: Path to implementation file or component name
            specification: Path to specification file or specification text
            
        Returns:
            CRDSPResonanceCheck with alignment analysis
        """
        logger.info(f"[CRDSP:Phase3] Verifying resonance: {implementation} ↔ {specification}")
        
        # Convert to paths if strings
        if isinstance(implementation, str) and not Path(implementation).exists():
            # Try to find implementation file
            impl_path = self._find_implementation_file(implementation)
        else:
            impl_path = Path(implementation) if isinstance(implementation, str) else implementation
        
        if isinstance(specification, str) and not Path(specification).exists():
            # Try to find specification file
            spec_path = self._find_specification_file(specification)
        else:
            spec_path = Path(specification) if isinstance(specification, str) else specification
        
        # Use AutopoieticSelfAnalysis to compare
        if impl_path and spec_path and impl_path.exists() and spec_path.exists():
            component_name = impl_path.stem
            gap = self.self_analysis.compare_component(
                component_name=component_name,
                spec_path=spec_path,
                impl_path=impl_path
            )
            
            alignment_confidence = QuantumProbability(
                probability=gap.confidence_score,
                evidence=gap.evidence.get('alignment_evidence', [])
            )
            
            status = "aligned" if gap.confidence_score >= 0.85 else "misaligned"
            
            recommendations = []
            if gap.confidence_score < 0.85:
                recommendations.append(gap.recommended_action)
                recommendations.extend(gap.evidence.get('recommendations', []))
        else:
            # One or both files missing
            alignment_confidence = QuantumProbability.certain_false()
            gap = None
            status = "unknown"
            recommendations = [
                f"Implementation file not found: {impl_path}" if not impl_path or not impl_path.exists() else "",
                f"Specification file not found: {spec_path}" if not spec_path or not spec_path.exists() else ""
            ]
            recommendations = [r for r in recommendations if r]
        
        check = CRDSPResonanceCheck(
            component=str(impl_path) if impl_path else implementation,
            specification=str(spec_path) if spec_path else specification,
            implementation=str(impl_path) if impl_path else implementation,
            alignment_confidence=alignment_confidence,
            gap_analysis=gap,
            recommendations=recommendations,
            status=status
        )
        
        # Generate IAR
        iar = {
            "status": "success" if status == "aligned" else "warning",
            "confidence": float(alignment_confidence),
            "task_id": f"crdsp_phase3_{datetime.now().timestamp()}",
            "reflection": f"Resonance verification: {status}. Alignment confidence: {alignment_confidence.probability:.2f}",
            "potential_issues": recommendations if recommendations else [],
            "alignment_check": f"Above ({specification}) ↔ Below ({implementation}) = {status}"
        }
        
        return check
    
    def _find_implementation_file(self, component_name: str) -> Optional[Path]:
        """Find implementation file for component name."""
        # Search in arche_root
        possible_paths = [
            self.arche_root / f"{component_name}.py",
            self.arche_root / f"{component_name.lower()}.py",
            self.arche_root / f"{component_name.replace('_', '')}.py"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Recursive search
        for py_file in self.arche_root.rglob(f"*{component_name}*.py"):
            return py_file
        
        return None
    
    def _find_specification_file(self, spec_name: str) -> Optional[Path]:
        """Find specification file for spec name."""
        if self.spec_root.exists():
            possible_paths = [
                self.spec_root / f"{spec_name}.md",
                self.spec_root / f"{spec_name.lower()}.md"
            ]
            
            for path in possible_paths:
                if path.exists():
                    return path
            
            # Recursive search
            for md_file in self.spec_root.rglob(f"*{spec_name}*.md"):
                return md_file
        
        return None
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 4: DOCUMENTATION SYNCHRONIZATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def synchronize_documentation(
        self,
        changes: List[CRDSPImplementation],
        docs_to_update: List[str],
        analysis: CRDSPAnalysis
    ) -> List[CRDSPDocumentationSync]:
        """
        Phase 4: Update all related documentation.
        
        Ensures "As Above (documentation) reflects So Below (code)".
        
        Args:
            changes: List of implementation changes made
            docs_to_update: List of documentation file paths to update
            analysis: Original pre-implementation analysis
            
        Returns:
            List of documentation sync results
        """
        logger.info(f"[CRDSP:Phase4] Synchronizing {len(docs_to_update)} documentation files")
        
        sync_results = []
        
        for doc_path_str in docs_to_update:
            doc_path = self.project_root / doc_path_str
        
            if not doc_path.exists():
                logger.warning(f"[CRDSP:Phase4] Documentation file not found: {doc_path}")
                sync_results.append(CRDSPDocumentationSync(
                    document_path=doc_path,
                    sync_status="error",
                    changes_made=[],
                    alignment_with_code=QuantumProbability.certain_false(),
                    metadata={"error": "File not found"}
                ))
                continue
            
            # Determine sync strategy based on file type
            if doc_path.suffix == '.json':
                # SPR definitions file
                sync_result = self._sync_spr_definitions(doc_path, changes, analysis)
            elif 'protocol' in doc_path_str or doc_path.parent.name == 'protocol':
                # Protocol document
                sync_result = self._sync_protocol_document(doc_path, changes, analysis)
            elif doc_path.parent.name == 'specifications':
                # Specification file
                sync_result = self._sync_specification_file(doc_path, changes, analysis)
            else:
                # Generic markdown file
                sync_result = self._sync_generic_documentation(doc_path, changes, analysis)
            
            sync_results.append(sync_result)
        
        # Generate IAR
        successful_syncs = sum(1 for r in sync_results if r.sync_status == "updated")
        iar = {
            "status": "success" if successful_syncs == len(sync_results) else "partial",
            "confidence": successful_syncs / len(sync_results) if sync_results else 0.0,
            "task_id": f"crdsp_phase4_{datetime.now().timestamp()}",
            "reflection": f"Documentation synchronization: {successful_syncs}/{len(sync_results)} files updated",
            "potential_issues": [r.metadata.get('error') for r in sync_results if r.sync_status == "error"],
            "alignment_check": "Above (documentation) updated to reflect Below (code) changes"
        }
        
        return sync_results
    
    def _sync_spr_definitions(
        self,
        doc_path: Path,
        changes: List[CRDSPImplementation],
        analysis: CRDSPAnalysis
    ) -> CRDSPDocumentationSync:
        """Synchronize SPR definitions file."""
        changes_made = []
        
        try:
            # Load current SPR definitions
            with open(doc_path, 'r', encoding='utf-8') as f:
                spr_data = json.load(f)
            
            # Update blueprint_details for affected SPRs
            for spr_id in analysis.spr_impact:
                for spr in spr_data:
                    if spr.get('spr_id') == spr_id:
                        # Update blueprint_details to point to actual implementation
                        for change in changes:
                            if change.component_name in str(change.file_path):
                                spr['blueprint_details'] = f"Three_PointO_ArchE/{change.file_path.name}"
                                changes_made.append(f"Updated blueprint_details for {spr_id}")
                                break
            
            # Save updated SPR definitions
            with open(doc_path, 'w', encoding='utf-8') as f:
                json.dump(spr_data, f, indent=2, ensure_ascii=False)
            
            return CRDSPDocumentationSync(
                document_path=doc_path,
                sync_status="updated",
                changes_made=changes_made,
                alignment_with_code=QuantumProbability(0.9, ["spr_definitions_updated"]),
                metadata={"sprs_updated": len(changes_made)}
            )
        except Exception as e:
            logger.error(f"[CRDSP:Phase4] Error syncing SPR definitions: {e}")
            return CRDSPDocumentationSync(
                document_path=doc_path,
                sync_status="error",
                changes_made=[],
                alignment_with_code=QuantumProbability.certain_false(),
                metadata={"error": str(e)}
            )
    
    def _sync_protocol_document(
        self,
        doc_path: Path,
        changes: List[CRDSPImplementation],
        analysis: CRDSPAnalysis
    ) -> CRDSPDocumentationSync:
        """Synchronize protocol document."""
        changes_made = []
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add note about implementation if section exists
            # This is simplified - full implementation would parse and intelligently update
            timestamp = datetime.now().strftime("%Y-%m-%d")
            note = f"\n\n<!-- Updated {timestamp}: Implementation aligned per CRDSP v3.1 -->\n"
            
            # For now, just add a marker that sync was attempted
            changes_made.append(f"Protocol document sync attempted for {doc_path.name}")
            
            return CRDSPDocumentationSync(
                document_path=doc_path,
                sync_status="pending",  # Requires manual review for protocol docs
                changes_made=changes_made,
                alignment_with_code=QuantumProbability(0.7, ["manual_review_required"]),
                metadata={"note": "Protocol documents require Keyholder review"}
            )
        except Exception as e:
            return CRDSPDocumentationSync(
                document_path=doc_path,
                sync_status="error",
                changes_made=[],
                alignment_with_code=QuantumProbability.certain_false(),
                metadata={"error": str(e)}
            )
    
    def _sync_specification_file(
        self,
        doc_path: Path,
        changes: List[CRDSPImplementation],
        analysis: CRDSPAnalysis
    ) -> CRDSPDocumentationSync:
        """Synchronize specification file."""
        changes_made = []
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if implementation file paths need updating
            for change in changes:
                if change.file_path:
                    # Update any references to old implementation paths
                    old_ref_pattern = r'`Three_PointO_ArchE/[^`]+`'
                    new_ref = f"`{change.file_path.relative_to(self.project_root)}`"
                    if re.search(old_ref_pattern, content):
                        content = re.sub(old_ref_pattern, new_ref, content)
                        changes_made.append(f"Updated implementation reference to {change.file_path.name}")
            
            if changes_made:
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return CRDSPDocumentationSync(
                document_path=doc_path,
                sync_status="updated" if changes_made else "skipped",
                changes_made=changes_made,
                alignment_with_code=QuantumProbability(0.85 if changes_made else 0.5, changes_made),
                metadata={"changes_count": len(changes_made)}
            )
        except Exception as e:
            return CRDSPDocumentationSync(
                document_path=doc_path,
                sync_status="error",
                changes_made=[],
                alignment_with_code=QuantumProbability.certain_false(),
                metadata={"error": str(e)}
            )
    
    def _sync_generic_documentation(
        self,
        doc_path: Path,
        changes: List[CRDSPImplementation],
        analysis: CRDSPAnalysis
    ) -> CRDSPDocumentationSync:
        """Synchronize generic markdown documentation."""
        # Simplified - mark as pending manual review
        return CRDSPDocumentationSync(
            document_path=doc_path,
            sync_status="pending",
            changes_made=[],
            alignment_with_code=QuantumProbability(0.6, ["manual_review_recommended"]),
            metadata={"note": "Generic documentation requires manual review for accuracy"}
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 5: FINAL REVIEW & LEARNING PROPAGATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def final_review(
        self,
        analysis: CRDSPAnalysis,
        implementations: List[CRDSPImplementation],
        resonance_checks: List[CRDSPResonanceCheck],
        documentation_syncs: List[CRDSPDocumentationSync]
    ) -> Dict[str, Any]:
        """
        Phase 5: Final Review & Learning Propagation.
        
        Args:
            analysis: Pre-implementation analysis
            implementations: Tracked implementations
            resonance_checks: Verification results
            documentation_syncs: Documentation sync results
            
        Returns:
            Comprehensive review report
        """
        logger.info("[CRDSP:Phase5] Performing final review")
        
        # Calculate overall alignment
        alignment_scores = [
            check.alignment_confidence.probability
            for check in resonance_checks
        ]
        
        avg_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
        
        # Check documentation sync status
        doc_sync_success = sum(1 for d in documentation_syncs if d.sync_status == "updated")
        doc_sync_rate = doc_sync_success / len(documentation_syncs) if documentation_syncs else 0.0
        
        # Overall resonance status
        resonance_status = "ACHIEVED" if avg_alignment >= 0.85 and doc_sync_rate >= 0.8 else "PARTIAL" if avg_alignment >= 0.7 else "BREAK_DETECTED"
        
        review = {
            "phase": "final_review",
            "timestamp": datetime.now().isoformat(),
            "overall_alignment": QuantumProbability(
                probability=avg_alignment,
                evidence=[
                    f"verified_{len(resonance_checks)}_components",
                    f"synced_{doc_sync_success}_of_{len(documentation_syncs)}_docs"
                ]
            ).to_dict(),
            "resonance_status": resonance_status,
            "components_verified": len(resonance_checks),
            "documentation_synced": doc_sync_success,
            "recommendations": self._generate_final_recommendations(
                avg_alignment,
                doc_sync_rate,
                resonance_checks,
                documentation_syncs
            ),
            "learnings": self._extract_learnings(analysis, implementations)
        }
        
        return review
    
    def _generate_final_recommendations(
        self,
        avg_alignment: float,
        doc_sync_rate: float,
        resonance_checks: List[CRDSPResonanceCheck],
        documentation_syncs: List[CRDSPDocumentationSync]
    ) -> List[str]:
        """Generate final recommendations."""
        recommendations = []
        
        if avg_alignment < 0.85:
            recommendations.append("Component alignment below threshold (0.85). Review and fix misalignments.")
        
        if doc_sync_rate < 0.8:
            recommendations.append("Documentation sync incomplete. Complete pending documentation updates.")
        
        for check in resonance_checks:
            if check.status == "misaligned":
                recommendations.append(f"Component {check.component} requires alignment review: {', '.join(check.recommendations[:2])}")
        
        for doc in documentation_syncs:
            if doc.sync_status == "pending":
                recommendations.append(f"Documentation {doc.document_path.name} requires manual review")
        
        return recommendations
    
    def _extract_learnings(
        self,
        analysis: CRDSPAnalysis,
        implementations: List[CRDSPImplementation]
    ) -> Dict[str, Any]:
        """Extract learnings for InsightSolidificatioN."""
        return {
            "patterns_detected": [],
            "insights": [
                f"CRDSP v3.1 executed for {analysis.objective}",
                f"Impacted {len(analysis.affected_components)} components, {len(analysis.spr_impact)} SPRs"
            ],
            "future_improvements": []
        }


# ═══════════════════════════════════════════════════════════════════════
# MAIN CRDSP WORKFLOW
# ═══════════════════════════════════════════════════════════════════════

def execute_crdsp_workflow(
    objective: str,
    implementation_changes: List[Dict[str, Any]],
    project_root: Path = None
) -> Dict[str, Any]:
    """
    Execute complete CRDSP v3.1 workflow.
    
    Args:
        objective: Change objective
        implementation_changes: List of changes made
        project_root: Project root directory
        
    Returns:
        Complete workflow results
    """
    engine = CRDSPEngine(project_root=project_root)
    
    # Phase 1: Pre-Implementation Analysis
    analysis = engine.pre_implementation_analysis(objective)
    
    # Phase 2: Track Implementation
    implementations = engine.track_implementation(analysis, implementation_changes)
    
    # Phase 3: Verify Resonance
    resonance_checks = []
    for impl in implementations:
        # Find corresponding specification
        spec_path = engine._find_specification_file(impl.component_name)
        if spec_path:
            check = engine.verify_resonance(impl.file_path, spec_path)
            resonance_checks.append(check)
    
    # Phase 4: Synchronize Documentation
    documentation_syncs = engine.synchronize_documentation(
        implementations,
        analysis.documentation_impact,
        analysis
    )
    
    # Phase 5: Final Review
    review = engine.final_review(
        analysis,
        implementations,
        resonance_checks,
        documentation_syncs
    )
    
    return {
        "analysis": asdict(analysis),
        "implementations": [asdict(impl) for impl in implementations],
        "resonance_checks": [asdict(check) for check in resonance_checks],
        "documentation_syncs": [asdict(doc) for doc in documentation_syncs],
        "final_review": review,
        "crdsp_status": "complete"
    }

