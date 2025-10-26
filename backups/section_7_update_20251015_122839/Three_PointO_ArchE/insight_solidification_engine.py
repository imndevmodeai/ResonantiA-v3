#!/usr/bin/env python3
"""
Insight Solidification Engine - Implementation of InsightsolidificatioN SPR
Operationalizes the formal workflow for integrating vetted knowledge into the Knowledge Tapestry

This module implements the InsightsolidificatioN SPR capability, providing:
- Insight analysis and validation
- Knowledge vetting against existing KnO
- SPR creation and updating via SPRManager
- Learning integration and crystallization
- Continuous self-assessment via IAR

Part of ResonantiA Protocol v3.1-CA Implementation Resonance initiative.
"""

import json
import os
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightType(Enum):
    """Types of insights that can be solidified."""
    CONCEPTUAL = "conceptual"           # New concepts or definitions
    PROCEDURAL = "procedural"           # New methods or workflows
    EMPIRICAL = "empirical"             # Data-driven observations
    RELATIONAL = "relational"           # Connections between existing concepts
    CORRECTIVE = "corrective"           # Updates to existing knowledge
    EMERGENT = "emergent"              # Patterns discovered through analysis

class ValidationStatus(Enum):
    """Status of insight validation process."""
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    CONFLICTING = "conflicting"

class SolidificationMethod(Enum):
    """Methods for solidifying insights."""
    NEW_SPR = "new_spr"                # Create entirely new SPR
    UPDATE_SPR = "update_spr"          # Modify existing SPR
    MERGE_SPRS = "merge_sprs"          # Combine multiple SPRs
    DEPRECATE_SPR = "deprecate_spr"    # Mark SPR as outdated
    RELATIONSHIP_UPDATE = "relationship_update"  # Update SPR relationships

@dataclass
class InsightCandidate:
    """Container for insight awaiting solidification."""
    insight_id: str
    insight_type: InsightType
    core_concept: str
    supporting_details: str
    source_reference: str
    evidence_strength: float
    confidence: float
    suggested_spr_name: Optional[str] = None
    proposed_category: Optional[str] = None
    proposed_relationships: Optional[Dict[str, Any]] = None
    creation_timestamp: str = field(default_factory=lambda: now_iso())

@dataclass
class ValidationResult:
    """Container for insight validation results."""
    insight_id: str
    validation_status: ValidationStatus
    confidence: float
    validation_details: Dict[str, Any]
    conflicts_identified: List[str]
    recommendations: List[str]
    reviewer_notes: str
    validation_timestamp: str = field(default_factory=lambda: now_iso())

@dataclass
class SolidificationPlan:
    """Container for solidification execution plan."""
    insight_id: str
    solidification_method: SolidificationMethod
    target_spr_id: str
    spr_modifications: Dict[str, Any]
    backup_plan: Optional[Dict[str, Any]]
    success_criteria: List[str]
    rollback_triggers: List[str]
    estimated_impact: float

@dataclass
class SolidificationResult:
    """Container for solidification execution results."""
    insight_id: str
    execution_status: str
    spr_changes_made: List[str]
    knowledge_tapestry_updated: bool
    success_metrics: Dict[str, float]
    lessons_learned: List[str]
    follow_up_actions: List[str]
    completion_timestamp: str = field(default_factory=lambda: now_iso())

class InsightValidator:
    """Validates insights against existing knowledge and quality standards."""
    
    def __init__(self, knowledge_tapestry_path: str, config: Optional[Dict[str, Any]] = None):
        """Initialize insight validator."""
        self.knowledge_tapestry_path = knowledge_tapestry_path
        self.config = config or self._get_default_config()
        self.existing_sprs = self._load_existing_sprs()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for insight validation."""
        return {
            'min_confidence_threshold': 0.7,
            'min_evidence_strength': 0.6,
            'conflict_detection_enabled': True,
            'relationship_validation_enabled': True,
            'duplicate_detection_threshold': 0.8
        }
    
    def _load_existing_sprs(self) -> Dict[str, Any]:
        """Load existing SPRs from Knowledge Tapestry."""
        try:
            if os.path.exists(self.knowledge_tapestry_path):
                with open(self.knowledge_tapestry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {spr.get('spr_id', spr.get('name', '')): spr 
                           for spr in data.get('spr_definitions', [])}
            return {}
        except Exception as e:
            logger.error(f"Error loading existing SPRs: {e}")
            return {}
    
    def validate_insight(self, insight: InsightCandidate) -> ValidationResult:
        """
        Validate an insight candidate against existing knowledge and quality standards.
        
        Args:
            insight: InsightCandidate to validate
            
        Returns:
            ValidationResult with validation outcome and details
        """
        logger.info(f"Validating insight: {insight.insight_id}")
        
        try:
            validation_details = {}
            conflicts_identified = []
            recommendations = []
            
            # Quality threshold validation
            quality_check = self._validate_quality_thresholds(insight)
            validation_details['quality_check'] = quality_check
            
            if not quality_check['passed']:
                return ValidationResult(
                    insight_id=insight.insight_id,
                    validation_status=ValidationStatus.REJECTED,
                    confidence=0.1,
                    validation_details=validation_details,
                    conflicts_identified=['quality_threshold_failure'],
                    recommendations=['improve_evidence_strength', 'increase_confidence'],
                    reviewer_notes=f"Failed quality thresholds: {quality_check['failures']}"
                )
            
            # Duplicate detection
            duplicate_check = self._check_for_duplicates(insight)
            validation_details['duplicate_check'] = duplicate_check
            
            if duplicate_check['duplicates_found']:
                conflicts_identified.extend(duplicate_check['duplicate_sprs'])
                recommendations.append('consider_merging_with_existing')
            
            # Conflict detection
            if self.config['conflict_detection_enabled']:
                conflict_check = self._detect_conflicts(insight)
                validation_details['conflict_check'] = conflict_check
                conflicts_identified.extend(conflict_check['conflicts'])
            
            # Relationship validation
            if self.config['relationship_validation_enabled'] and insight.proposed_relationships:
                relationship_check = self._validate_relationships(insight)
                validation_details['relationship_check'] = relationship_check
                
                if not relationship_check['valid']:
                    recommendations.append('revise_proposed_relationships')
            
            # Determine overall validation status
            validation_status = self._determine_validation_status(
                conflicts_identified, duplicate_check, quality_check
            )
            
            # Calculate overall confidence
            confidence = self._calculate_validation_confidence(
                quality_check, duplicate_check, conflict_check if 'conflict_check' in validation_details else None
            )
            
            # Generate recommendations
            if not recommendations:
                recommendations = self._generate_recommendations(insight, validation_details)
            
            result = ValidationResult(
                insight_id=insight.insight_id,
                validation_status=validation_status,
                confidence=confidence,
                validation_details=validation_details,
                conflicts_identified=conflicts_identified,
                recommendations=recommendations,
                reviewer_notes=self._generate_reviewer_notes(insight, validation_details)
            )
            
            logger.info(f"Validation complete for {insight.insight_id}: {validation_status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error validating insight {insight.insight_id}: {e}")
            return ValidationResult(
                insight_id=insight.insight_id,
                validation_status=ValidationStatus.REJECTED,
                confidence=0.0,
                validation_details={"error": str(e)},
                conflicts_identified=['validation_error'],
                recommendations=['retry_validation'],
                reviewer_notes=f"Validation failed due to error: {str(e)}"
            )
    
    def _validate_quality_thresholds(self, insight: InsightCandidate) -> Dict[str, Any]:
        """Validate insight against quality thresholds."""
        failures = []
        
        if insight.confidence < self.config['min_confidence_threshold']:
            failures.append(f"confidence_too_low: {insight.confidence}")
        
        if insight.evidence_strength < self.config['min_evidence_strength']:
            failures.append(f"evidence_too_weak: {insight.evidence_strength}")
        
        if not insight.core_concept or len(insight.core_concept.strip()) < 5:
            failures.append("core_concept_insufficient")
        
        if not insight.supporting_details or len(insight.supporting_details.strip()) < 10:
            failures.append("supporting_details_insufficient")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures,
            'confidence_score': insight.confidence,
            'evidence_score': insight.evidence_strength
        }
    
    def _check_for_duplicates(self, insight: InsightCandidate) -> Dict[str, Any]:
        """Check for duplicate or very similar existing SPRs."""
        duplicates = []
        similarity_scores = {}
        
        for spr_id, spr_data in self.existing_sprs.items():
            # Simple similarity check based on core concept and term
            similarity = self._calculate_concept_similarity(
                insight.core_concept, 
                spr_data.get('definition', spr_data.get('description', ''))
            )
            
            similarity_scores[spr_id] = similarity
            
            if similarity > self.config['duplicate_detection_threshold']:
                duplicates.append(spr_id)
        
        return {
            'duplicates_found': len(duplicates) > 0,
            'duplicate_sprs': duplicates,
            'similarity_scores': similarity_scores,
            'highest_similarity': max(similarity_scores.values()) if similarity_scores else 0.0
        }
    
    def _calculate_concept_similarity(self, concept1: str, concept2: str) -> float:
        """Calculate similarity between two concepts (simplified implementation)."""
        if not concept1 or not concept2:
            return 0.0
        
        # Simple word overlap similarity
        words1 = set(concept1.lower().split())
        words2 = set(concept2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _detect_conflicts(self, insight: InsightCandidate) -> Dict[str, Any]:
        """Detect potential conflicts with existing knowledge."""
        conflicts = []
        conflict_details = {}
        
        # Check for contradictory definitions
        for spr_id, spr_data in self.existing_sprs.items():
            if self._concepts_contradict(insight.core_concept, spr_data.get('definition', '')):
                conflicts.append(f"contradicts_{spr_id}")
                conflict_details[spr_id] = "contradictory_definition"
        
        return {
            'conflicts': conflicts,
            'conflict_details': conflict_details,
            'conflict_count': len(conflicts)
        }
    
    def _concepts_contradict(self, concept1: str, concept2: str) -> bool:
        """Check if two concepts contradict each other (simplified implementation)."""
        # Simple contradiction detection based on negation words
        negation_words = ['not', 'never', 'opposite', 'contrary', 'against']
        
        concept1_lower = concept1.lower()
        concept2_lower = concept2.lower()
        
        # If one concept contains negation words and shares other words with the other
        words1 = set(concept1_lower.split())
        words2 = set(concept2_lower.split())
        
        negation_in_1 = any(neg in words1 for neg in negation_words)
        negation_in_2 = any(neg in words2 for neg in negation_words)
        
        if negation_in_1 != negation_in_2:  # One has negation, other doesn't
            common_words = words1.intersection(words2) - set(negation_words)
            return len(common_words) > 1  # Share significant words
        
        return False
    
    def _validate_relationships(self, insight: InsightCandidate) -> Dict[str, Any]:
        """Validate proposed relationships against existing SPRs."""
        if not insight.proposed_relationships:
            return {'valid': True, 'issues': []}
        
        issues = []
        
        # Check if referenced SPRs exist
        for rel_type, rel_targets in insight.proposed_relationships.items():
            if isinstance(rel_targets, list):
                for target in rel_targets:
                    if target not in self.existing_sprs:
                        issues.append(f"referenced_spr_not_found: {target}")
            elif isinstance(rel_targets, str):
                if rel_targets not in self.existing_sprs:
                    issues.append(f"referenced_spr_not_found: {rel_targets}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'relationships_checked': len(insight.proposed_relationships)
        }
    
    def _determine_validation_status(self, conflicts: List[str], duplicate_check: Dict[str, Any], 
                                   quality_check: Dict[str, Any]) -> ValidationStatus:
        """Determine overall validation status."""
        if not quality_check['passed']:
            return ValidationStatus.REJECTED
        
        if conflicts:
            return ValidationStatus.CONFLICTING
        
        if duplicate_check['duplicates_found']:
            return ValidationStatus.NEEDS_REVISION
        
        return ValidationStatus.VALIDATED
    
    def _calculate_validation_confidence(self, quality_check: Dict[str, Any], 
                                       duplicate_check: Dict[str, Any],
                                       conflict_check: Optional[Dict[str, Any]]) -> float:
        """Calculate overall validation confidence."""
        base_confidence = 0.8
        
        # Adjust for quality
        if quality_check['passed']:
            base_confidence += 0.1
        else:
            base_confidence -= 0.3
        
        # Adjust for duplicates
        if duplicate_check['duplicates_found']:
            base_confidence -= 0.2
        
        # Adjust for conflicts
        if conflict_check and conflict_check['conflicts']:
            base_confidence -= 0.3
        
        return max(0.0, min(1.0, base_confidence))
    
    def _generate_recommendations(self, insight: InsightCandidate, 
                                validation_details: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if validation_details.get('duplicate_check', {}).get('duplicates_found'):
            recommendations.append('consider_updating_existing_spr_instead')
        
        if validation_details.get('conflict_check', {}).get('conflicts'):
            recommendations.append('resolve_conflicts_with_existing_knowledge')
        
        if insight.confidence < 0.9:
            recommendations.append('gather_additional_evidence')
        
        return recommendations if recommendations else ['proceed_with_solidification']
    
    def _generate_reviewer_notes(self, insight: InsightCandidate, 
                               validation_details: Dict[str, Any]) -> str:
        """Generate detailed reviewer notes."""
        notes = [f"Insight validation completed for: {insight.core_concept}"]
        
        quality_check = validation_details.get('quality_check', {})
        if quality_check.get('passed'):
            notes.append("✓ Quality thresholds met")
        else:
            notes.append(f"✗ Quality issues: {quality_check.get('failures', [])}")
        
        duplicate_check = validation_details.get('duplicate_check', {})
        if duplicate_check.get('duplicates_found'):
            notes.append(f"⚠ Potential duplicates: {duplicate_check.get('duplicate_sprs', [])}")
        
        conflict_check = validation_details.get('conflict_check', {})
        if conflict_check and conflict_check.get('conflicts'):
            notes.append(f"⚠ Conflicts detected: {conflict_check.get('conflicts', [])}")
        
        return " | ".join(notes)

class SPRManager:
    """Manages SPR creation, updating, and persistence in the Knowledge Tapestry."""
    
    def __init__(self, knowledge_tapestry_path: str):
        """Initialize SPR manager."""
        self.knowledge_tapestry_path = knowledge_tapestry_path
        self.backup_path = f"{knowledge_tapestry_path}.backup"
        
    def create_backup(self) -> bool:
        """Create backup of current Knowledge Tapestry."""
        try:
            if os.path.exists(self.knowledge_tapestry_path):
                import shutil
                shutil.copy2(self.knowledge_tapestry_path, self.backup_path)
                logger.info("Knowledge Tapestry backup created")
                return True
            return False
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self) -> bool:
        """Restore Knowledge Tapestry from backup."""
        try:
            if os.path.exists(self.backup_path):
                import shutil
                shutil.copy2(self.backup_path, self.knowledge_tapestry_path)
                logger.info("Knowledge Tapestry restored from backup")
                return True
            return False
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def add_spr(self, spr_data: Dict[str, Any], overwrite_if_exists: bool = False) -> bool:
        """Add new SPR to Knowledge Tapestry."""
        try:
            # Load current tapestry
            tapestry_data = self._load_tapestry()
            
            spr_id = spr_data.get('spr_id', spr_data.get('name', ''))
            if not spr_id:
                logger.error("SPR must have spr_id or name")
                return False
            
            # Check if SPR already exists
            existing_sprs = {spr.get('spr_id', spr.get('name', '')): i 
                           for i, spr in enumerate(tapestry_data.get('spr_definitions', []))}
            
            if spr_id in existing_sprs:
                if overwrite_if_exists:
                    # Update existing SPR
                    tapestry_data['spr_definitions'][existing_sprs[spr_id]] = spr_data
                    logger.info(f"Updated existing SPR: {spr_id}")
                else:
                    logger.warning(f"SPR {spr_id} already exists, use overwrite_if_exists=True to update")
                    return False
            else:
                # Add new SPR
                tapestry_data['spr_definitions'].append(spr_data)
                logger.info(f"Added new SPR: {spr_id}")
            
            # Save updated tapestry
            return self._save_tapestry(tapestry_data)
            
        except Exception as e:
            logger.error(f"Error adding SPR: {e}")
            return False
    
    def update_spr(self, spr_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing SPR with new data."""
        try:
            tapestry_data = self._load_tapestry()
            
            # Find SPR to update
            for i, spr in enumerate(tapestry_data.get('spr_definitions', [])):
                if spr.get('spr_id', spr.get('name', '')) == spr_id:
                    # Apply updates
                    tapestry_data['spr_definitions'][i].update(updates)
                    logger.info(f"Updated SPR: {spr_id}")
                    return self._save_tapestry(tapestry_data)
            
            logger.warning(f"SPR {spr_id} not found for update")
            return False
            
        except Exception as e:
            logger.error(f"Error updating SPR: {e}")
            return False
    
    def _load_tapestry(self) -> Dict[str, Any]:
        """Load Knowledge Tapestry data."""
        try:
            if os.path.exists(self.knowledge_tapestry_path):
                with open(self.knowledge_tapestry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'spr_definitions': []}
        except Exception as e:
            logger.error(f"Error loading tapestry: {e}")
            return {'spr_definitions': []}
    
    def _save_tapestry(self, data: Dict[str, Any]) -> bool:
        """Save Knowledge Tapestry data."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.knowledge_tapestry_path), exist_ok=True)
            
            with open(self.knowledge_tapestry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("Knowledge Tapestry saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tapestry: {e}")
            return False

class InsightSolidificationEngine:
    """
    Main engine implementing InsightsolidificatioN SPR capabilities.
    
    Orchestrates the complete workflow for analyzing, vetting, and integrating
    new knowledge into the Knowledge Tapestry via SPR creation/updating.
    """
    
    def __init__(self, knowledge_tapestry_path: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the insight solidification engine."""
        self.knowledge_tapestry_path = knowledge_tapestry_path
        self.config = config or self._get_default_config()
        self.validator = InsightValidator(knowledge_tapestry_path, config)
        self.spr_manager = SPRManager(knowledge_tapestry_path)
        self.solidification_history: List[SolidificationResult] = []
        
        logger.info("InsightSolidificationEngine initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for insight solidification."""
        return {
            'auto_backup_enabled': True,
            'validation_required': True,
            'rollback_on_failure': True,
            'learning_enabled': True,
            'max_solidification_attempts': 3
        }
    
    def solidify_insight(self, insight: InsightCandidate) -> SolidificationResult:
        """
        Main entry point for insight solidification workflow.
        
        Validates insight, creates solidification plan, and executes integration
        into the Knowledge Tapestry.
        
        Args:
            insight: InsightCandidate to solidify
            
        Returns:
            SolidificationResult with execution outcome
        """
        logger.info(f"Starting insight solidification: {insight.insight_id}")
        
        try:
            # Create backup if enabled
            if self.config['auto_backup_enabled']:
                backup_success = self.spr_manager.create_backup()
                if not backup_success:
                    logger.warning("Failed to create backup, proceeding without backup")
            
            # Validate insight
            if self.config['validation_required']:
                validation_result = self.validator.validate_insight(insight)
                
                if validation_result.validation_status != ValidationStatus.VALIDATED:
                    return SolidificationResult(
                        insight_id=insight.insight_id,
                        execution_status="validation_failed",
                        spr_changes_made=[],
                        knowledge_tapestry_updated=False,
                        success_metrics={'validation_confidence': validation_result.confidence},
                        lessons_learned=[f"Validation failed: {validation_result.validation_status.value}"],
                        follow_up_actions=validation_result.recommendations
                    )
            
            # Create solidification plan
            solidification_plan = self._create_solidification_plan(insight, validation_result if 'validation_result' in locals() else None)
            
            # Execute solidification
            execution_result = self._execute_solidification(solidification_plan, insight)
            
            # Store result in history
            self.solidification_history.append(execution_result)
            
            logger.info(f"Insight solidification complete: {insight.insight_id}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error in insight solidification: {e}")
            
            # Attempt rollback if enabled
            if self.config['rollback_on_failure'] and self.config['auto_backup_enabled']:
                rollback_success = self.spr_manager.restore_backup()
                rollback_note = "rollback_successful" if rollback_success else "rollback_failed"
            else:
                rollback_note = "rollback_not_attempted"
            
            return SolidificationResult(
                insight_id=insight.insight_id,
                execution_status="error",
                spr_changes_made=[],
                knowledge_tapestry_updated=False,
                success_metrics={'error_occurred': 1.0},
                lessons_learned=[f"Solidification failed: {str(e)}", rollback_note],
                follow_up_actions=['investigate_error', 'retry_solidification']
            )
    
    def _create_solidification_plan(self, insight: InsightCandidate, 
                                  validation_result: Optional[ValidationResult]) -> SolidificationPlan:
        """Create detailed plan for solidifying the insight."""
        # Determine solidification method
        if validation_result and validation_result.validation_details.get('duplicate_check', {}).get('duplicates_found'):
            method = SolidificationMethod.UPDATE_SPR
            target_spr_id = validation_result.validation_details['duplicate_check']['duplicate_sprs'][0]
        else:
            method = SolidificationMethod.NEW_SPR
            target_spr_id = insight.suggested_spr_name or f"insight_{insight.insight_id}"
        
        # Prepare SPR modifications
        spr_modifications = {
            'spr_id': target_spr_id,
            'term': insight.core_concept.split(':')[0].strip() if ':' in insight.core_concept else insight.core_concept,
            'definition': insight.supporting_details,
            'category': insight.proposed_category or 'GeneratedInsight',
            'relationships': insight.proposed_relationships or {},
            'metadata': {
                'version': '1.0',
                'status': 'active',
                'created_by': f'InsightSolidificationEngine_{insight.source_reference}',
                'created_date': now_iso()[:10],
                'source_reference': insight.source_reference,
                'confidence': insight.confidence,
                'evidence_strength': insight.evidence_strength
            }
        }
        
        return SolidificationPlan(
            insight_id=insight.insight_id,
            solidification_method=method,
            target_spr_id=target_spr_id,
            spr_modifications=spr_modifications,
            backup_plan={'restore_from_backup': True},
            success_criteria=['spr_created_or_updated', 'knowledge_tapestry_saved'],
            rollback_triggers=['save_failure', 'validation_error'],
            estimated_impact=insight.confidence * insight.evidence_strength
        )
    
    def _execute_solidification(self, plan: SolidificationPlan, 
                              insight: InsightCandidate) -> SolidificationResult:
        """Execute the solidification plan."""
        spr_changes_made = []
        success_metrics = {}
        lessons_learned = []
        follow_up_actions = []
        
        try:
            if plan.solidification_method == SolidificationMethod.NEW_SPR:
                # Create new SPR
                success = self.spr_manager.add_spr(plan.spr_modifications, overwrite_if_exists=False)
                if success:
                    spr_changes_made.append(f"created_spr_{plan.target_spr_id}")
                    success_metrics['creation_success'] = 1.0
                    lessons_learned.append(f"Successfully created new SPR for insight type: {insight.insight_type.value}")
                else:
                    return SolidificationResult(
                        insight_id=insight.insight_id,
                        execution_status="spr_creation_failed",
                        spr_changes_made=spr_changes_made,
                        knowledge_tapestry_updated=False,
                        success_metrics={'creation_success': 0.0},
                        lessons_learned=['SPR creation failed'],
                        follow_up_actions=['investigate_creation_failure']
                    )
            
            elif plan.solidification_method == SolidificationMethod.UPDATE_SPR:
                # Update existing SPR
                success = self.spr_manager.update_spr(plan.target_spr_id, plan.spr_modifications)
                if success:
                    spr_changes_made.append(f"updated_spr_{plan.target_spr_id}")
                    success_metrics['update_success'] = 1.0
                    lessons_learned.append(f"Successfully updated existing SPR with new insight")
                else:
                    return SolidificationResult(
                        insight_id=insight.insight_id,
                        execution_status="spr_update_failed",
                        spr_changes_made=spr_changes_made,
                        knowledge_tapestry_updated=False,
                        success_metrics={'update_success': 0.0},
                        lessons_learned=['SPR update failed'],
                        follow_up_actions=['investigate_update_failure']
                    )
            
            # Calculate overall success
            overall_success = len(spr_changes_made) > 0
            success_metrics['overall_success'] = 1.0 if overall_success else 0.0
            success_metrics['estimated_impact_achieved'] = plan.estimated_impact if overall_success else 0.0
            
            # Generate follow-up actions
            if overall_success:
                follow_up_actions = ['monitor_spr_usage', 'validate_integration']
                if insight.proposed_relationships:
                    follow_up_actions.append('validate_relationship_consistency')
            
            return SolidificationResult(
                insight_id=insight.insight_id,
                execution_status="completed_successfully",
                spr_changes_made=spr_changes_made,
                knowledge_tapestry_updated=overall_success,
                success_metrics=success_metrics,
                lessons_learned=lessons_learned,
                follow_up_actions=follow_up_actions
            )
            
        except Exception as e:
            logger.error(f"Error executing solidification plan: {e}")
            return SolidificationResult(
                insight_id=insight.insight_id,
                execution_status="execution_error",
                spr_changes_made=spr_changes_made,
                knowledge_tapestry_updated=False,
                success_metrics={'execution_error': 1.0},
                lessons_learned=[f"Execution error: {str(e)}"],
                follow_up_actions=['debug_execution_error', 'retry_with_simpler_plan']
            )
    
    def get_solidification_analytics(self) -> Dict[str, Any]:
        """Get analytics on insight solidification performance."""
        if not self.solidification_history:
            return {"message": "No solidification history available"}
        
        recent_results = self.solidification_history[-10:]
        
        analytics = {
            "total_solidifications": len(self.solidification_history),
            "recent_solidifications": len(recent_results),
            "success_rate": sum(1 for r in recent_results if r.execution_status == "completed_successfully") / len(recent_results),
            "average_impact": sum(r.success_metrics.get('estimated_impact_achieved', 0) for r in recent_results) / len(recent_results),
            "most_common_insight_type": self._get_most_common_insight_type(),
            "knowledge_growth_rate": self._calculate_knowledge_growth_rate()
        }
        
        return analytics
    
    def _get_most_common_insight_type(self) -> str:
        """Get the most commonly solidified insight type."""
        # This would need access to original insights, simplified for now
        return "conceptual"  # Placeholder
    
    def _calculate_knowledge_growth_rate(self) -> float:
        """Calculate rate of knowledge growth."""
        if len(self.solidification_history) < 2:
            return 0.0
        
        successful_solidifications = [
            r for r in self.solidification_history 
            if r.execution_status == "completed_successfully"
        ]
        
        # Simple growth rate based on successful solidifications per time period
        return len(successful_solidifications) / len(self.solidification_history)
    
    def generate_iar_reflection(self, result: SolidificationResult) -> Dict[str, Any]:
        """
        Generate IAR reflection for insight solidification process.
        
        Implements the self-awareness requirement for all ArchE actions.
        """
        success_score = result.success_metrics.get('overall_success', 0.0)
        
        potential_issues = []
        if result.execution_status != "completed_successfully":
            potential_issues.append(f"execution_status_{result.execution_status}")
        if not result.knowledge_tapestry_updated:
            potential_issues.append("knowledge_tapestry_not_updated")
        if not result.spr_changes_made:
            potential_issues.append("no_spr_changes_made")
        
        return {
            "status": "completed" if success_score > 0 else "failed",
            "confidence": success_score,
            "potential_issues": potential_issues,
            "alignment_check": "high" if success_score > 0.8 else "medium" if success_score > 0.5 else "low",
            "tactical_resonance": success_score,
            "crystallization_potential": "high" if success_score > 0.8 and len(potential_issues) == 0 else "medium",
            "timestamp": now_iso(),
            "insight_solidified": result.insight_id,
            "spr_changes_made": result.spr_changes_made,
            "knowledge_impact": result.success_metrics.get('estimated_impact_achieved', 0.0),
            "lessons_learned": result.lessons_learned
        }

# Factory function for easy integration
def create_insight_solidification_engine(knowledge_tapestry_path: str, 
                                       config: Optional[Dict[str, Any]] = None) -> InsightSolidificationEngine:
    """Factory function to create a configured insight solidification engine."""
    return InsightSolidificationEngine(knowledge_tapestry_path, config)

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    knowledge_path = "../knowledge_graph/spr_definitions_tv.json"
    engine = create_insight_solidification_engine(knowledge_path)
    
    # Sample insight for testing
    sample_insight = InsightCandidate(
        insight_id="test_insight_001",
        insight_type=InsightType.CONCEPTUAL,
        core_concept="Adaptive Learning Pattern",
        supporting_details="A pattern observed in system behavior where repeated exposure to similar problems leads to improved performance through dynamic parameter adjustment.",
        source_reference="System Analysis Task XYZ",
        evidence_strength=0.85,
        confidence=0.9,
        suggested_spr_name="AdaptiveLearningPatternN",
        proposed_category="LearningMechanism",
        proposed_relationships={
            "type": "CognitiveMechanism",
            "related_to": ["MetacognitiveshifT", "InsightsolidificatioN"],
            "enables": ["SystemImprovement", "KnowledgeEvolution"]
        }
    )
    
    # Solidify insight
    result = engine.solidify_insight(sample_insight)
    analytics = engine.get_solidification_analytics()
    iar_reflection = engine.generate_iar_reflection(result)
    
    print("InsightsolidificatioN Engine Test Results:")
    print(f"Execution Status: {result.execution_status}")
    print(f"SPR Changes: {result.spr_changes_made}")
    print(f"Knowledge Updated: {result.knowledge_tapestry_updated}")
    print(f"Success Metrics: {result.success_metrics}")
    print(f"Lessons Learned: {result.lessons_learned}")
    
    print(f"\nAnalytics: {analytics}")
    print(f"\nIAR Reflection: {iar_reflection}") 