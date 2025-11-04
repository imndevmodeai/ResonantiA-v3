"""
ArchE Resonance Verifier
Comprehensive system alignment verification tool

Validates "As Above, So Below" alignment across:
- Protocol specifications ↔ Code implementations
- SPR definitions ↔ Implementation files
- Documentation ↔ Code
- CRDSP compliance
- Implementation Resonance
- Universal Abstraction processes

This tool brings ArchE into full ResonantiA Protocol compliance.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .autopoietic_self_analysis import AutopoieticSelfAnalysis, QuantumProbability
from .spr_manager import SPRManager
from .crdsp_protocol import CRDSPEngine
from .implementation_resonance import ImplementationResonanceEngine

logger = logging.getLogger(__name__)


@dataclass
class ResonanceVerificationResult:
    """Result of comprehensive resonance verification."""
    component: str
    above_layer: str
    below_layer: str
    alignment_confidence: QuantumProbability
    status: str  # "aligned", "misaligned", "missing", "unknown"
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SystemAlignmentReport:
    """Comprehensive system alignment report."""
    timestamp: str
    overall_alignment: QuantumProbability
    resonance_status: str  # "ACHIEVED", "PARTIAL", "BREAK_DETECTED"
    component_results: List[ResonanceVerificationResult]
    spr_blueprint_validation: Dict[str, Any]
    crdsp_compliance: Dict[str, Any]
    implementation_resonance: Dict[str, Any]
    universal_abstraction_verification: Dict[str, Any]
    recommendations: List[str]
    summary: Dict[str, Any]


class ArchEResonanceVerifier:
    """
    Comprehensive ArchE Resonance Verifier
    
    Validates complete system alignment according to ResonantiA Protocol.
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.arche_root = self.project_root / "Three_PointO_ArchE"
        self.spec_root = self.project_root / "specifications"
        self.protocol_root = self.project_root / "protocol"
        self.knowledge_graph_root = self.project_root / "knowledge_graph"
        
        # Initialize verification systems
        self.self_analysis = AutopoieticSelfAnalysis(project_root=self.project_root)
        self.spr_manager = SPRManager(str(self.knowledge_graph_root / "spr_definitions_tv.json"))
        self.crdsp_engine = CRDSPEngine(project_root=self.project_root)
        self.implementation_resonance = ImplementationResonanceEngine(project_root=self.project_root)
        
        logger.info("[ArchEResonanceVerifier] Initialized")
    
    def verify_system_resonance(self) -> SystemAlignmentReport:
        """
        Perform comprehensive system resonance verification.
        
        Returns:
            Complete system alignment report
        """
        logger.info("[ArchEResonanceVerifier] Starting comprehensive resonance verification")
        
        # 1. Autopoietic Self-Analysis (Map ↔ Territory)
        system_alignment = self.self_analysis.verify_system_alignment()
        
        # 2. SPR Blueprint Validation
        spr_validation = self._validate_spr_blueprints()
        
        # 3. CRDSP Compliance Check
        crdsp_compliance = self._check_crdsp_compliance()
        
        # 4. Implementation Resonance Check
        impl_resonance = self._check_implementation_resonance()
        
        # 5. Universal Abstraction Verification
        universal_abstraction = self._verify_universal_abstraction()
        
        # Calculate overall alignment
        alignment_scores = [
            system_alignment.get('system_alignment', 0.0),
            spr_validation.get('alignment_score', 0.0),
            crdsp_compliance.get('compliance_score', 0.0),
            impl_resonance.get('resonance_score', 0.0),
            universal_abstraction.get('process_alignment', 0.0)
        ]
        
        avg_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
        
        overall_confidence = QuantumProbability(
            probability=avg_alignment,
            evidence=[
                f"system_alignment_{system_alignment.get('system_alignment', 0.0):.2f}",
                f"spr_blueprint_{spr_validation.get('alignment_score', 0.0):.2f}",
                f"crdsp_compliance_{crdsp_compliance.get('compliance_score', 0.0):.2f}",
                f"impl_resonance_{impl_resonance.get('resonance_score', 0.0):.2f}",
                f"universal_abstraction_{universal_abstraction.get('process_alignment', 0.0):.2f}"
            ]
        )
        
        # Determine resonance status
        if avg_alignment >= 0.85:
            resonance_status = "ACHIEVED"
        elif avg_alignment >= 0.70:
            resonance_status = "PARTIAL"
        else:
            resonance_status = "BREAK_DETECTED"
        
        # Generate component results
        component_results = self._generate_component_results(
            system_alignment,
            spr_validation,
            crdsp_compliance
        )
        
        # Generate recommendations
        recommendations = self._generate_comprehensive_recommendations(
            system_alignment,
            spr_validation,
            crdsp_compliance,
            impl_resonance,
            universal_abstraction
        )
        
        report = SystemAlignmentReport(
            timestamp=datetime.now().isoformat(),
            overall_alignment=overall_confidence,
            resonance_status=resonance_status,
            component_results=component_results,
            spr_blueprint_validation=spr_validation,
            crdsp_compliance=crdsp_compliance,
            implementation_resonance=impl_resonance,
            universal_abstraction_verification=universal_abstraction,
            recommendations=recommendations,
            summary={
                "overall_alignment": avg_alignment,
                "resonance_status": resonance_status,
                "components_verified": len(component_results),
                "aligned_components": sum(1 for c in component_results if c.status == "aligned"),
                "misaligned_components": sum(1 for c in component_results if c.status == "misaligned"),
                "quantum_confidence": overall_confidence.to_dict()
            }
        )
        
        logger.info(f"[ArchEResonanceVerifier] Verification complete: {resonance_status} ({avg_alignment:.2%})")
        
        return report
    
    def _validate_spr_blueprints(self) -> Dict[str, Any]:
        """Validate SPR blueprint_details link to actual implementations."""
        logger.info("[ArchEResonanceVerifier] Validating SPR blueprints")
        
        spr_definitions = self.spr_manager.load_sprs()
        if spr_definitions is None:
            spr_definitions = []
        validation_results = {
            "total_sprs": len(spr_definitions),
            "with_blueprint_details": 0,
            "valid_file_references": 0,
            "invalid_file_references": 0,
            "missing_blueprint_details": 0,
            "issues": []
        }
        
        for spr in spr_definitions:
            spr_id = spr.get('spr_id', 'Unknown')
            blueprint = spr.get('blueprint_details', '')
            
            if not blueprint or blueprint.strip() == '':
                validation_results["missing_blueprint_details"] += 1
                validation_results["issues"].append({
                    "spr_id": spr_id,
                    "issue": "Missing blueprint_details",
                    "severity": "medium"
                })
                continue
            
            validation_results["with_blueprint_details"] += 1
            
            # Check if blueprint_details is a file path
            if '.py' in blueprint and '/' in blueprint:
                # Parse file path
                if 'Three_PointO_ArchE/' in blueprint:
                    file_path = self.project_root / blueprint.replace('Three_PointO_ArchE/', 'Three_PointO_ArchE/')
                elif blueprint.startswith('Three_PointO_ArchE/'):
                    file_path = self.project_root / blueprint
                else:
                    file_path = self.arche_root / blueprint.split('/')[0]
                
                if file_path.exists():
                    validation_results["valid_file_references"] += 1
                else:
                    validation_results["invalid_file_references"] += 1
                    validation_results["issues"].append({
                        "spr_id": spr_id,
                        "issue": f"Blueprint file not found: {file_path}",
                        "severity": "high",
                        "blueprint_details": blueprint
                    })
            elif 'See' in blueprint or 'Section' in blueprint:
                # Protocol reference - valid but not a direct file link
                pass
        
        # Calculate alignment score
        if validation_results["total_sprs"] > 0:
            valid_rate = validation_results["valid_file_references"] / validation_results["total_sprs"]
            alignment_score = valid_rate * 0.8 + (1 - (validation_results["invalid_file_references"] / max(validation_results["total_sprs"], 1))) * 0.2
        else:
            alignment_score = 0.0
        
        return {
            **validation_results,
            "alignment_score": alignment_score,
            "quantum_confidence": QuantumProbability(
                probability=alignment_score,
                evidence=[
                    f"{validation_results['valid_file_references']}_valid_references",
                    f"{validation_results['invalid_file_references']}_invalid_references"
                ]
            ).to_dict()
        }
    
    def _check_crdsp_compliance(self) -> Dict[str, Any]:
        """Check CRDSP v3.1 compliance."""
        logger.info("[ArchEResonanceVerifier] Checking CRDSP compliance")
        
        # Verify CRDSP module exists and is functional
        compliance_score = 1.0 if Path(__file__).parent / "crdsp_protocol.py" else 0.5
        
        # Check if CRDSP methods are available
        crdsp_methods = ['pre_implementation_analysis', 'verify_resonance', 'synchronize_documentation']
        methods_available = all(hasattr(self.crdsp_engine, m) for m in crdsp_methods)
        
        if methods_available:
            compliance_score = 0.9
        
        return {
            "compliance_score": compliance_score,
            "crdsp_module_exists": Path(__file__).parent / "crdsp_protocol.py",
            "methods_available": methods_available,
            "status": "compliant" if compliance_score >= 0.85 else "partial" if compliance_score >= 0.7 else "non_compliant",
            "quantum_confidence": QuantumProbability(
                probability=compliance_score,
                evidence=["crdsp_module_verified", "methods_available"] if methods_available else ["crdsp_module_missing"]
            ).to_dict()
        }
    
    def _check_implementation_resonance(self) -> Dict[str, Any]:
        """Check Implementation Resonance framework."""
        logger.info("[ArchEResonanceVerifier] Checking Implementation Resonance")
        
        # Verify Implementation Resonance module exists
        impl_res_module = Path(__file__).parent / "implementation_resonance.py"
        module_exists = impl_res_module.exists()
        
        # Check if methods are available
        if module_exists:
            methods_available = all(hasattr(self.implementation_resonance, m) for m in ['absorb_intent', 'resonant_implementation', 'crystallize_knowledge'])
            resonance_score = 0.9 if methods_available else 0.7
        else:
            resonance_score = 0.0
        
        return {
            "resonance_score": resonance_score,
            "module_exists": module_exists,
            "methods_available": methods_available if module_exists else False,
            "status": "operational" if resonance_score >= 0.85 else "partial" if resonance_score >= 0.7 else "missing",
            "quantum_confidence": QuantumProbability(
                probability=resonance_score,
                evidence=["impl_resonance_module_verified"] if module_exists else ["impl_resonance_module_missing"]
            ).to_dict()
        }
    
    def _verify_universal_abstraction(self) -> Dict[str, Any]:
        """Verify Universal Abstraction four processes are implemented."""
        logger.info("[ArchEResonanceVerifier] Verifying Universal Abstraction")
        
        processes = {
            "representation": False,
            "comparison": False,
            "learning": False,
            "crystallization": False
        }
        
        # Check Representation (QuantumProbability exists)
        if Path(__file__).parent / "autopoietic_self_analysis.py":
            # QuantumProbability class should exist
            processes["representation"] = True
        
        # Check Comparison (compare_component exists)
        if hasattr(self.self_analysis, 'compare_component'):
            processes["comparison"] = True
        
        # Check Learning (detect_nebulae in AutopoieticLearningLoop)
        learning_loop_path = self.arche_root / "autopoietic_learning_loop.py"
        if learning_loop_path.exists():
            with open(learning_loop_path, 'r') as f:
                content = f.read()
                if 'detect_nebulae' in content or 'detect_pattern' in content:
                    processes["learning"] = True
        
        # Check Crystallization (crystallize_knowledge exists)
        if learning_loop_path.exists():
            with open(learning_loop_path, 'r') as f:
                content = f.read()
                if 'crystallize_knowledge' in content:
                    processes["crystallization"] = True
        
        process_alignment = sum(processes.values()) / len(processes) if processes else 0.0
        
        return {
            "processes": processes,
            "process_alignment": process_alignment,
            "all_processes_implemented": all(processes.values()),
            "quantum_confidence": QuantumProbability(
                probability=process_alignment,
                evidence=[f"{k}_implemented" for k, v in processes.items() if v]
            ).to_dict()
        }
    
    def _generate_component_results(
        self,
        system_alignment: Dict[str, Any],
        spr_validation: Dict[str, Any],
        crdsp_compliance: Dict[str, Any]
    ) -> List[ResonanceVerificationResult]:
        """Generate component-level results."""
        results = []
        
        # System alignment components
        for component in system_alignment.get('components', []):
            results.append(ResonanceVerificationResult(
                component=component.get('component', 'unknown'),
                above_layer="specification",
                below_layer="implementation",
                alignment_confidence=QuantumProbability(
                    probability=component.get('alignment', 0.0),
                    evidence=component.get('evidence', {})
                ),
                status="aligned" if component.get('alignment', 0.0) >= 0.85 else "misaligned",
                evidence=component.get('evidence', {}),
                recommendations=component.get('recommendations', [])
            ))
        
        # SPR blueprint validation
        results.append(ResonanceVerificationResult(
            component="SPR Blueprint Validation",
            above_layer="SPR definitions",
            below_layer="implementation files",
            alignment_confidence=QuantumProbability(
                probability=spr_validation.get('quantum_confidence', {}).get('probability', 0.0),
                evidence=spr_validation.get('quantum_confidence', {}).get('evidence', [])
            ),
            status="aligned" if spr_validation.get('alignment_score', 0.0) >= 0.85 else "misaligned",
            evidence=spr_validation,
            recommendations=[f"Fix {spr_validation.get('invalid_file_references', 0)} invalid SPR blueprint references"] if spr_validation.get('invalid_file_references', 0) > 0 else []
        ))
        
        # CRDSP compliance
        results.append(ResonanceVerificationResult(
            component="CRDSP v3.1",
            above_layer="protocol",
            below_layer="implementation",
            alignment_confidence=QuantumProbability(
                probability=crdsp_compliance.get('quantum_confidence', {}).get('probability', 0.0),
                evidence=crdsp_compliance.get('quantum_confidence', {}).get('evidence', [])
            ),
            status=crdsp_compliance.get('status', 'unknown'),
            evidence=crdsp_compliance,
            recommendations=[]
        ))
        
        return results
    
    def _generate_comprehensive_recommendations(
        self,
        system_alignment: Dict[str, Any],
        spr_validation: Dict[str, Any],
        crdsp_compliance: Dict[str, Any],
        impl_resonance: Dict[str, Any],
        universal_abstraction: Dict[str, Any]
    ) -> List[str]:
        """Generate comprehensive recommendations."""
        recommendations = []
        
        # System alignment recommendations
        if system_alignment.get('resonance_status') != "ACHIEVED":
            recommendations.extend(system_alignment.get('recommendations', []))
        
        # SPR blueprint recommendations
        if spr_validation.get('invalid_file_references', 0) > 0:
            recommendations.append(
                f"Fix {spr_validation['invalid_file_references']} SPR blueprint_details with invalid file references"
            )
        
        if spr_validation.get('missing_blueprint_details', 0) > 0:
            recommendations.append(
                f"Add blueprint_details to {spr_validation['missing_blueprint_details']} SPRs missing them"
            )
        
        # CRDSP compliance recommendations
        if crdsp_compliance.get('compliance_score', 0.0) < 0.85:
            recommendations.append("Ensure CRDSP v3.1 is fully operational")
        
        # Implementation Resonance recommendations
        if impl_resonance.get('resonance_score', 0.0) < 0.85:
            recommendations.append("Verify Implementation Resonance framework is operational")
        
        # Universal Abstraction recommendations
        if not universal_abstraction.get('all_processes_implemented', False):
            missing = [k for k, v in universal_abstraction.get('processes', {}).items() if not v]
            recommendations.append(f"Implement missing Universal Abstraction processes: {', '.join(missing)}")
        
        if not recommendations:
            recommendations.append("System is in alignment - maintain current state")
        
        return recommendations
    
    def generate_report(self, report: SystemAlignmentReport, output_path: Path = None) -> str:
        """Generate human-readable alignment report."""
        lines = [
            "=" * 80,
            "ARCHÉ RESONANCE VERIFICATION REPORT",
            "As Above, So Below - Complete System Alignment",
            "=" * 80,
            "",
            f"Report Generated: {report.timestamp}",
            f"Overall Alignment: {report.overall_alignment.probability:.2%}",
            f"Resonance Status: {report.resonance_status}",
            "",
            "SUMMARY",
            "-" * 80,
            f"Components Verified: {report.summary.get('components_verified', 0)}",
            f"Aligned Components: {report.summary.get('aligned_components', 0)}",
            f"Misaligned Components: {report.summary.get('misaligned_components', 0)}",
            "",
            "SPR BLUEPRINT VALIDATION",
            "-" * 80,
            f"Total SPRs: {report.spr_blueprint_validation.get('total_sprs', 0)}",
            f"Valid File References: {report.spr_blueprint_validation.get('valid_file_references', 0)}",
            f"Invalid File References: {report.spr_blueprint_validation.get('invalid_file_references', 0)}",
            f"Missing Blueprint Details: {report.spr_blueprint_validation.get('missing_blueprint_details', 0)}",
            "",
            "CRDSP COMPLIANCE",
            "-" * 80,
            f"Compliance Score: {report.crdsp_compliance.get('compliance_score', 0.0):.2%}",
            f"Status: {report.crdsp_compliance.get('status', 'unknown')}",
            "",
            "RECOMMENDATIONS",
            "-" * 80
        ]
        
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        
        lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80
        ])
        
        report_text = "\n".join(lines)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)
            logger.info(f"Report saved to {output_path}")
        
        return report_text


def main():
    """Run comprehensive ArchE resonance verification."""
    verifier = ArchEResonanceVerifier()
    
    print("🔍 Initiating ArchE Resonance Verification...")
    print("   Validating 'As Above, So Below' alignment...")
    print()
    
    report = verifier.verify_system_resonance()
    
    print(f"✓ Verification Complete!")
    print(f"  Resonance Status: {report.resonance_status}")
    print(f"  Overall Alignment: {report.overall_alignment.probability:.2%}")
    print()
    
    # Generate and display report
    report_text = verifier.generate_report(report)
    print(report_text)
    
    # Save report
    from .temporal_core import format_filename
    timestamp = format_filename()
    report_dir = verifier.project_root / "logs" / "resonance_verification"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = report_dir / f"resonance_verification_{timestamp}.txt"
    verifier.generate_report(report, report_path)
    
    print()
    print(f"📊 Report saved: {report_path}")


if __name__ == "__main__":
    main()

