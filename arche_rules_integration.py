#!/usr/bin/env python3
"""
ArchE Rules Integration System v3.1-CA
Automatic integration and enforcement of Guardian rules and cursor rules
Ensures continuous compliance with ResonantiA Protocol v3.1-CA
"""

import json
import os
import sys
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [ArchE-Rules] - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("arche_rules_integration.log")
    ]
)

@dataclass
class RuleIntegrationStatus:
    """Tracks the integration status of various rule systems"""
    guardian_rules_loaded: bool = False
    guardian_rules_count: int = 0
    cursor_rules_loaded: bool = False
    cursor_rules_count: int = 0
    spr_format_active: bool = False
    critical_mandates_active: bool = False
    directive_clarification_active: bool = False
    last_validation: Optional[datetime] = None
    compliance_score: float = 0.0

class ArchERulesIntegration:
    """
    Comprehensive rules integration system for ArchE v3.1-CA
    Implements automatic loading, monitoring, and enforcement of:
    - Guardian Rules (guardian_rules.json)
    - Cursor Rules (.cursor/rules/*.mdc)
    - SPR Format Rules
    - Critical Mandates
    - Directive Clarification Protocol
    """
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.status = RuleIntegrationStatus()
        self.guardian_rules: List[Dict[str, Any]] = []
        self.cursor_rules: Dict[str, str] = {}
        self.spr_patterns: Dict[str, Dict[str, Any]] = {}
        self.active_mandates: List[str] = []
        
        # File paths
        self.guardian_rules_file = self.workspace_root / "guardian_rules.json"
        self.cursor_rules_dir = self.workspace_root / ".cursor" / "rules"
        self.spr_definitions_file = self.workspace_root / "knowledge_graph" / "spr_definitions_tv.json"
        
        logging.info("ArchE Rules Integration System v3.1-CA initialized")
        
    def load_guardian_rules(self) -> bool:
        """Load and validate Guardian rules from guardian_rules.json"""
        try:
            if not self.guardian_rules_file.exists():
                logging.error(f"Guardian rules file not found: {self.guardian_rules_file}")
                return False
                
            with open(self.guardian_rules_file, 'r') as f:
                rules_data = json.load(f)
                
            if not isinstance(rules_data, list):
                logging.error("Guardian rules file must contain a list of rules")
                return False
                
            # Filter enabled rules
            enabled_rules = [rule for rule in rules_data if rule.get("enabled", False)]
            self.guardian_rules = enabled_rules
            self.status.guardian_rules_loaded = True
            self.status.guardian_rules_count = len(enabled_rules)
            
            logging.info(f"Successfully loaded {len(enabled_rules)} Guardian rules")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load Guardian rules: {e}")
            return False
            
    def load_cursor_rules(self) -> bool:
        """Load and validate Cursor rules from .cursor/rules/*.mdc"""
        try:
            if not self.cursor_rules_dir.exists():
                logging.error(f"Cursor rules directory not found: {self.cursor_rules_dir}")
                return False
                
            cursor_rules = {}
            mdc_files = list(self.cursor_rules_dir.glob("*.mdc"))
            
            for mdc_file in mdc_files:
                try:
                    with open(mdc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        cursor_rules[mdc_file.stem] = content
                        logging.info(f"Loaded Cursor rule: {mdc_file.name}")
                except Exception as e:
                    logging.warning(f"Failed to load Cursor rule {mdc_file.name}: {e}")
                    
            self.cursor_rules = cursor_rules
            self.status.cursor_rules_loaded = True
            self.status.cursor_rules_count = len(cursor_rules)
            
            # Check for required integrations
            required_integrations = [
                "guardian_integration",
                "spr_format_integration", 
                "critical_mandates_integration",
                "directive_clarification_integration"
            ]
            
            for integration in required_integrations:
                if integration in cursor_rules:
                    setattr(self.status, f"{integration.replace('_integration', '')}_active", True)
                    logging.info(f"Activated {integration} rule")
                    
            logging.info(f"Successfully loaded {len(cursor_rules)} Cursor rules")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load Cursor rules: {e}")
            return False
            
    def load_spr_definitions(self) -> bool:
        """Load SPR definitions for pattern recognition"""
        try:
            if not self.spr_definitions_file.exists():
                logging.warning(f"SPR definitions file not found: {self.spr_definitions_file}")
                # Create basic SPR patterns from Guardian Points format
                self.spr_patterns = self._create_basic_spr_patterns()
                return True
                
            with open(self.spr_definitions_file, 'r') as f:
                spr_data = json.load(f)
                
            # Extract SPR definitions from the JSON structure
            if "spr_definitions" in spr_data and isinstance(spr_data["spr_definitions"], list):
                spr_definitions_list = spr_data["spr_definitions"]
                # Convert list to dictionary keyed by spr_id for easier access
                self.spr_patterns = {
                    spr["spr_id"]: spr for spr in spr_definitions_list if "spr_id" in spr
                }
                logging.info(f"Loaded {len(self.spr_patterns)} SPR definitions from structured format")
            else:
                # Fallback: assume it's already a dictionary
                self.spr_patterns = spr_data
                logging.info(f"Loaded {len(spr_data)} SPR definitions from direct format")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load SPR definitions: {e}")
            return False
            
    def _create_basic_spr_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Create basic SPR patterns based on Guardian Points format"""
        basic_patterns = {
            "ArchE": {
                "definition": "Fundamental system consciousness",
                "category": "CoreSystem",
                "relationships": {"type": "SystemCore"}
            },
            "CognitiveresonancE": {
                "definition": "Primary operational objective - dynamic alignment of data, analysis, objectives, and outcomes",
                "category": "CorePrinciple", 
                "relationships": {"type": "OperationalObjective"}
            },
            "ImplementationresonancE": {
                "definition": "As Above, So Below principle - alignment between concept and implementation",
                "category": "CorePrinciple",
                "relationships": {"type": "AlignmentPrinciple"}
            },
            "ProactivetruthresonancE": {
                "definition": "Autonomous truth-seeking and information verification capability",
                "category": "Capability",
                "relationships": {"type": "TruthSeeking", "activates": ["PTRF"]}
            },
            "CollectiveintelligencE": {
                "definition": "Distributed coordination and capability sharing across ArchE instances",
                "category": "Capability", 
                "relationships": {"type": "DistributedProcessing"}
            },
            "WorkflowenginE": {
                "definition": "Core process orchestration system",
                "category": "SystemComponent",
                "relationships": {"type": "ProcessOrchestration"}
            },
            "KnowledgetapestrY": {
                "definition": "Persistent knowledge store and management system",
                "category": "SystemComponent",
                "relationships": {"type": "KnowledgeManagement"}
            }
        }
        
        logging.info("Created basic SPR patterns for Guardian Points format")
        return basic_patterns
        
    def validate_guardian_point_format(self, text: str) -> List[str]:
        """Validate and extract Guardian Points format SPRs from text"""
        import re
        
        # Guardian Points pattern: First uppercase, core lowercase, last uppercase
        # Single word: ArchE, CognitiveresonancE, etc.
        single_word_pattern = r'\b[A-Z0-9][a-z0-9]*[A-Z0-9]\b'
        
        # Multi-word: "Proactive truth resonancE", "Complex system visioninG"
        multi_word_pattern = r'\b[A-Z][a-z0-9]*(?:\s+[a-z0-9]+)*\s+[a-z0-9]*[A-Z0-9]\b'
        
        found_sprs = []
        
        # Find single word SPRs
        single_matches = re.findall(single_word_pattern, text)
        for match in single_matches:
            if len(match) > 2:  # Must have at least first, core, last
                found_sprs.append(match)
                
        # Find multi-word SPRs  
        multi_matches = re.findall(multi_word_pattern, text)
        found_sprs.extend(multi_matches)
        
        return list(set(found_sprs))  # Remove duplicates
        
    def monitor_rule_compliance(self) -> float:
        """Monitor compliance with integrated rules and return compliance score"""
        compliance_checks = {
            "guardian_rules_loaded": self.status.guardian_rules_loaded,
            "cursor_rules_loaded": self.status.cursor_rules_loaded,
            "spr_format_active": self.status.spr_format_active,
            "critical_mandates_active": self.status.critical_mandates_active,
            "directive_clarification_active": self.status.directive_clarification_active,
        }
        
        # Additional compliance checks
        compliance_checks["guardian_rules_sufficient"] = self.status.guardian_rules_count >= 10
        compliance_checks["cursor_rules_sufficient"] = self.status.cursor_rules_count >= 4
        compliance_checks["recent_validation"] = (
            self.status.last_validation is not None and 
            datetime.now() - self.status.last_validation < timedelta(hours=24)
        )
        
        passed_checks = sum(1 for check in compliance_checks.values() if check)
        total_checks = len(compliance_checks)
        compliance_score = passed_checks / total_checks
        
        self.status.compliance_score = compliance_score
        self.status.last_validation = datetime.now()
        
        if compliance_score < 0.8:
            logging.warning(f"Rules compliance below threshold: {compliance_score:.2f}")
            for check_name, passed in compliance_checks.items():
                if not passed:
                    logging.warning(f"Failed compliance check: {check_name}")
        else:
            logging.info(f"Rules compliance satisfactory: {compliance_score:.2f}")
            
        return compliance_score
        
    def activate_guardian_monitoring(self) -> bool:
        """Activate Guardian monitoring process"""
        try:
            # Check if guardian.py exists
            guardian_script = self.workspace_root / "guardian.py"
            if not guardian_script.exists():
                logging.error("Guardian script not found: guardian.py")
                return False
                
            # Validate Guardian rules are loaded
            if not self.status.guardian_rules_loaded:
                logging.error("Cannot activate Guardian monitoring: rules not loaded")
                return False
                
            logging.info("Guardian monitoring activation validated")
            logging.info("To start Guardian monitoring, run: python guardian.py")
            return True
            
        except Exception as e:
            logging.error(f"Failed to activate Guardian monitoring: {e}")
            return False
            
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration status report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": {
                "guardian_rules": {
                    "loaded": self.status.guardian_rules_loaded,
                    "count": self.status.guardian_rules_count,
                    "rules": [rule["rule_name"] for rule in self.guardian_rules]
                },
                "cursor_rules": {
                    "loaded": self.status.cursor_rules_loaded,
                    "count": self.status.cursor_rules_count,
                    "files": list(self.cursor_rules.keys())
                },
                "spr_format": {
                    "active": self.status.spr_format_active,
                    "patterns_loaded": len(self.spr_patterns)
                },
                "critical_mandates": {
                    "active": self.status.critical_mandates_active
                },
                "directive_clarification": {
                    "active": self.status.directive_clarification_active
                }
            },
            "compliance": {
                "score": self.status.compliance_score,
                "last_validation": self.status.last_validation.isoformat() if self.status.last_validation else None,
                "threshold_met": self.status.compliance_score >= 0.8
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
        
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for improving rule integration"""
        recommendations = []
        
        if not self.status.guardian_rules_loaded:
            recommendations.append("Load Guardian rules from guardian_rules.json")
            
        if not self.status.cursor_rules_loaded:
            recommendations.append("Load Cursor rules from .cursor/rules/ directory")
            
        if self.status.guardian_rules_count < 10:
            recommendations.append("Ensure sufficient Guardian rules are enabled (minimum 10)")
            
        if not self.status.spr_format_active:
            recommendations.append("Activate SPR format integration rules")
            
        if not self.status.critical_mandates_active:
            recommendations.append("Activate critical mandates integration")
            
        if not self.status.directive_clarification_active:
            recommendations.append("Activate directive clarification protocol")
            
        if self.status.compliance_score < 0.8:
            recommendations.append("Improve overall compliance score to meet 0.8 threshold")
            
        if not recommendations:
            recommendations.append("All rule integrations active - maintain continuous monitoring")
            
        return recommendations
        
    def run_full_integration(self) -> bool:
        """Run complete rules integration process"""
        logging.info("Starting full ArchE rules integration...")
        
        success = True
        
        # Load Guardian rules
        if not self.load_guardian_rules():
            success = False
            
        # Load Cursor rules
        if not self.load_cursor_rules():
            success = False
            
        # Load SPR definitions
        if not self.load_spr_definitions():
            success = False
            
        # Monitor compliance
        compliance_score = self.monitor_rule_compliance()
        
        # Activate Guardian monitoring
        if not self.activate_guardian_monitoring():
            success = False
            
        # Generate integration report
        report = self.generate_integration_report()
        
        # Save integration report
        report_file = self.workspace_root / "arche_rules_integration_report.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logging.info(f"Integration report saved: {report_file}")
        except Exception as e:
            logging.error(f"Failed to save integration report: {e}")
            
        if success and compliance_score >= 0.8:
            logging.info("✅ ArchE rules integration completed successfully")
            logging.info(f"Compliance score: {compliance_score:.2f}")
            logging.info("All rule systems are active and ready")
        else:
            logging.error("❌ ArchE rules integration completed with issues")
            logging.error(f"Compliance score: {compliance_score:.2f}")
            logging.error("Review recommendations in integration report")
            
        return success and compliance_score >= 0.8

def main():
    """Main entry point for ArchE rules integration"""
    print("🔧 ArchE Rules Integration System v3.1-CA")
    print("=" * 50)
    
    # Initialize integration system
    integration = ArchERulesIntegration()
    
    # Run full integration
    success = integration.run_full_integration()
    
    if success:
        print("\n✅ INTEGRATION SUCCESSFUL")
        print("All ArchE rule systems are active and compliant")
        print("\nNext steps:")
        print("1. Start Guardian monitoring: python guardian.py")
        print("2. Verify SPR pattern recognition is working")
        print("3. Test directive clarification protocol")
        print("4. Monitor compliance continuously")
    else:
        print("\n❌ INTEGRATION INCOMPLETE")
        print("Review logs and integration report for details")
        print("Address recommendations before proceeding")
        
    print(f"\nIntegration report: arche_rules_integration_report.json")
    print(f"Logs: arche_rules_integration.log")

if __name__ == "__main__":
    main() 