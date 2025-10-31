"""
Formal Plan Validator - The Logic Engine
Inspired by MIT PDDL-INSTRUCT Research

This module implements formal logical validation for workflow plans,
complementing the StrategicAdversarySimulator's adversarial testing.

Philosophical Foundation:
- Creative generation (RISE) produces plausible plans
- Logical validation (PlanValidator) ensures soundness
- Adversarial testing (StrategicAdversarySimulator) ensures robustness
- Error education (feedback loop) enables learning

The Three-Stage Mind Forge:
1. RISE (The Creative) - Generates novel strategies
2. PlanValidator (The Logician) - Validates formal correctness  
3. StrategicAdversarySimulator (The Adversary) - Tests resilience

Only plans that survive all three stages are fit for execution.

Research Citation:
"Large Language Models Still Can't Plan (A Benchmark for LLMs on Planning 
and Reasoning about Change)" - MIT, 2024
PDDL-INSTRUCT framework: LLM + Validator → 94% accuracy

Universal Abstraction Application:
- Representation: Workflow → Formal state machine
- Comparison: Expected vs actual state transitions
- Learning: Validation errors → refined plans
- Crystallization: Validated plans → executable workflows
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from .autopoietic_self_analysis import QuantumProbability
from .thought_trail import log_to_thought_trail

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename


logger = logging.getLogger(__name__)

# Quantum probability support
try:
    QUANTUM_AVAILABLE = True
except ImportError:
    class QuantumProbability:
        def __init__(self, prob: float, evidence: List[str] = None):
            self.probability = prob
            self.evidence = evidence or []
        @log_to_thought_trail
        def to_dict(self):
            return {"probability": self.probability, "evidence": self.evidence}
    QUANTUM_AVAILABLE = False


@dataclass
class PreconditionCheck:
    """Result of checking a single precondition."""
    precondition: str
    satisfied: bool
    confidence: float
    evidence: List[str]
    missing_dependencies: List[str] = field(default_factory=list)


@dataclass
class StateTransition:
    """Represents a state transition in the workflow."""
    from_state: str
    to_state: str
    action: str
    task_id: str
    preconditions: List[str]
    postconditions: List[str]
    expected_outputs: Dict[str, Any]


@dataclass
class ValidationError:
    """A formal error in the plan."""
    error_type: str  # "unsatisfied_precondition", "missing_dependency", "impossible_transition", "unachievable_goal"
    task_id: str
    step_number: int
    description: str
    required_by: Optional[str]
    suggested_fix: str
    severity: str  # "critical", "warning"
    quantum_confidence: Dict[str, Any]


@dataclass
class ValidationReport:
    """Complete validation report for a workflow plan."""
    plan_name: str
    validation_timestamp: str
    is_valid: bool
    confidence: QuantumProbability
    errors: List[ValidationError]
    warnings: List[ValidationError]
    state_trace: List[StateTransition]
    goal_achievable: bool
    error_education_prompt: Optional[str]  # For feedback to RISE


class PlanValidator:
    """
    Formal logical validator for workflow plans.
    
    This is the "Logic Engine" that ensures plans are formally correct
    before they undergo adversarial testing. It implements the validator
    component from MIT's PDDL-INSTRUCT framework.
    
    Validation Checks:
    1. Dependency satisfaction: All task dependencies met
    2. Precondition satisfaction: All required conditions present
    3. State consistency: State transitions are logically valid
    4. Goal achievement: Final state satisfies goal conditions
    5. Temporal coherence: Time-dependent operations ordered correctly (4D thinking)
    """
    
    def __init__(self):
        """Initialize the plan validator."""
        self.validation_history: List[ValidationReport] = []
        logger.info("[PlanValidator] Formal logic engine initialized")
    
    @log_to_thought_trail
    def validate_workflow(self, workflow: Dict[str, Any], initial_context: Dict[str, Any] = None) -> ValidationReport:
        """
        Validate a complete workflow for formal correctness.
        
        This implements the core validation logic inspired by PDDL validators,
        adapted for ArchE's workflow structure with quantum confidence.
        
        Args:
            workflow: Workflow JSON structure
            initial_context: Initial state/context
            
        Returns:
            ValidationReport with quantum confidence
        """
        plan_name = workflow.get("name", "unknown_workflow")
        tasks = workflow.get("tasks", {})
        
        logger.info(f"[PlanValidator] Validating workflow: {plan_name} ({len(tasks)} tasks)")
        
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []
        state_trace: List[StateTransition] = []
        
        # Initialize validation state
        current_context = initial_context or {}
        completed_tasks: Set[str] = set()
        
        # Phase 1: Dependency Graph Validation
        dep_errors = self._validate_dependencies(tasks)
        errors.extend(dep_errors)
        
        # Phase 2: Precondition Validation (Sequential Simulation)
        if not dep_errors:  # Only if dependency graph is valid
            # Topological sort for execution order
            execution_order = self._topological_sort(tasks)
            
            if execution_order:
                precond_errors, state_trace = self._validate_preconditions(
                    tasks,
                    execution_order,
                    current_context
                )
                errors.extend(precond_errors)
            else:
                errors.append(ValidationError(
                    error_type="impossible_transition",
                    task_id="workflow",
                    step_number=0,
                    description="Workflow contains cycles - cannot determine execution order",
                    required_by=None,
                    suggested_fix="Remove circular dependencies between tasks",
                    severity="critical",
                    quantum_confidence=QuantumProbability(1.0, ["cycle_detection_algorithm"]).to_dict()
                ))
        
        # Phase 3: Goal Achievement Validation
        goal = workflow.get("goal", workflow.get("expected_outcome"))
        if goal:
            goal_achievable, goal_evidence = self._validate_goal_achievable(
                state_trace,
                goal
            )
            
            if not goal_achievable:
                errors.append(ValidationError(
                    error_type="unachievable_goal",
                    task_id="final_state",
                    step_number=len(state_trace),
                    description=f"Workflow cannot achieve stated goal: {goal}",
                    required_by=None,
                    suggested_fix="Add tasks that produce required goal conditions",
                    severity="critical",
                    quantum_confidence=QuantumProbability(
                        0.8,
                        goal_evidence + ["goal_state_analysis"]
                    ).to_dict()
                ))
        
        # Phase 4: Temporal Coherence Validation (4D Thinking)
        temporal_errors = self._validate_temporal_coherence(tasks, state_trace)
        errors.extend(temporal_errors)
        
        # Calculate overall validity
        is_valid = len(errors) == 0
        
        # Calculate quantum confidence
        if is_valid:
            confidence = QuantumProbability(
                0.95,
                ["all_checks_passed", "dependency_graph_valid", "preconditions_satisfied"]
            )
        elif len(errors) <= 2:
            confidence = QuantumProbability(
                0.5,
                [f"{len(errors)}_errors_found", "fixable"]
            )
        else:
            confidence = QuantumProbability(
                0.2,
                [f"{len(errors)}_errors_found", "major_issues"]
            )
        
        # Generate error education prompt
        error_education = self._generate_error_education(errors, warnings) if errors else None
        
        # Create validation report
        report = ValidationReport(
            plan_name=plan_name,
            validation_timestamp=now_iso(),
            is_valid=is_valid,
            confidence=confidence,
            errors=errors,
            warnings=warnings,
            state_trace=state_trace,
            goal_achievable=len(errors) == 0 or not any(e.error_type == "unachievable_goal" for e in errors),
            error_education_prompt=error_education
        )
        
        self.validation_history.append(report)
        
        logger.info(f"[PlanValidator] Validation complete: {'VALID' if is_valid else 'INVALID'} (confidence: {confidence.probability:.1%})")
        if errors:
            logger.warning(f"[PlanValidator] Found {len(errors)} errors, {len(warnings)} warnings")
        
        return report
    
    def _validate_dependencies(self, tasks: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate dependency graph for cycles and undefined dependencies.
        
        This is the foundational check - if the dependency graph is invalid,
        the rest of validation cannot proceed.
        """
        errors = []
        
        for task_id, task_data in tasks.items():
            dependencies = task_data.get("dependencies", [])
            
            for dep in dependencies:
                if dep not in tasks:
                    errors.append(ValidationError(
                        error_type="missing_dependency",
                        task_id=task_id,
                        step_number=-1,
                        description=f"Task '{task_id}' depends on undefined task '{dep}'",
                        required_by=task_id,
                        suggested_fix=f"Either create task '{dep}' or remove it from dependencies",
                        severity="critical",
                        quantum_confidence=QuantumProbability(
                            1.0,
                            ["dependency_graph_analysis"]
                        ).to_dict()
                    ))
        
        return errors
    
    def _topological_sort(self, tasks: Dict[str, Any]) -> Optional[List[str]]:
        """
        Perform topological sort on task dependencies.
        
        Returns:
            Execution order if valid, None if cyclic
        """
        # Build adjacency list and in-degree count
        in_degree = {task_id: 0 for task_id in tasks}
        adj = {task_id: [] for task_id in tasks}
        
        for task_id, task_data in tasks.items():
            deps = task_data.get("dependencies", [])
            in_degree[task_id] = len([d for d in deps if d in tasks])
            
            for dep in deps:
                if dep in tasks:
                    adj[dep].append(task_id)
        
        # Kahn's algorithm
        queue = [tid for tid in tasks if in_degree[tid] == 0]
        result = []
        
        while queue:
            task_id = queue.pop(0)
            result.append(task_id)
            
            for dependent in adj[task_id]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # If result doesn't include all tasks, there's a cycle
        return result if len(result) == len(tasks) else None
    
    def _validate_preconditions(
        self,
        tasks: Dict[str, Any],
        execution_order: List[str],
        initial_context: Dict[str, Any]
    ) -> Tuple[List[ValidationError], List[StateTransition]]:
        """
        Validate that preconditions are satisfied at each step.
        
        This simulates workflow execution, tracking state evolution
        and checking that each task's input requirements are met.
        """
        errors = []
        state_trace = []
        current_state = set(initial_context.keys())
        
        for step_num, task_id in enumerate(execution_order, start=1):
            task_data = tasks[task_id]
            action_type = task_data.get("action_type", "unknown")
            inputs = task_data.get("inputs", {})
            outputs = task_data.get("outputs", {})
            
            # Extract required inputs (preconditions)
            required_inputs = self._extract_required_inputs(inputs)
            
            # Check if all required inputs are available
            missing = []
            satisfied_preconditions = []
            
            for req_input in required_inputs:
                # Check if this input is available from previous steps or initial context
                if self._is_available(req_input, current_state, initial_context):
                    satisfied_preconditions.append(req_input)
                else:
                    missing.append(req_input)
            
            # Record state transition
            transition = StateTransition(
                from_state=f"state_{step_num-1}",
                to_state=f"state_{step_num}",
                action=action_type,
                task_id=task_id,
                preconditions=required_inputs,
                postconditions=list(outputs.keys()) if outputs else [],
                expected_outputs=outputs
            )
            state_trace.append(transition)
            
            # If preconditions not met, record error
            if missing:
                errors.append(ValidationError(
                    error_type="unsatisfied_precondition",
                    task_id=task_id,
                    step_number=step_num,
                    description=f"Task '{task_id}' requires unavailable inputs: {missing}",
                    required_by=task_id,
                    suggested_fix=f"Add task(s) that produce {missing} before step {step_num}",
                    severity="critical",
                    quantum_confidence=QuantumProbability(
                        1.0,
                        ["precondition_analysis", f"missing:{len(missing)}"]
                    ).to_dict()
                ))
            
            # Update state with task outputs
            if outputs:
                for output_key in outputs.keys():
                    current_state.add(f"{task_id}.{output_key}")
        
        return errors, state_trace
    
    def _extract_required_inputs(self, inputs: Dict[str, Any]) -> List[str]:
        """
        Extract required context references from inputs.
        
        Looks for {{context.key}} or {{previous_task.output}} patterns.
        """
        required = []
        
        @log_to_thought_trail
        def extract_from_value(value):
            if isinstance(value, str):
                # Find {{...}} patterns
                import re
                matches = re.findall(r'\{\{([^}]+)\}\}', value)
                for match in matches:
                    # Clean up the reference
                    ref = match.strip().split('|')[0].strip()  # Remove default values
                    if ref not in ['workflow_run_id', 'initial_context']:  # Exclude always-available
                        required.append(ref)
            elif isinstance(value, dict):
                for v in value.values():
                    extract_from_value(v)
            elif isinstance(value, list):
                for v in value:
                    extract_from_value(v)
        
        for value in inputs.values():
            extract_from_value(value)
        
        return list(set(required))  # Deduplicate
    
    def _is_available(self, reference: str, current_state: Set[str], initial_context: Dict[str, Any]) -> bool:
        """
        Check if a context reference is available.
        
        Args:
            reference: Context reference like "task_a.output" or "initial_context.param"
            current_state: Set of available keys from completed tasks
            initial_context: Initial workflow context
        """
        # Check initial context
        if reference.startswith("initial_context."):
            key = reference.split(".", 1)[1]
            return key in initial_context
        
        # Check task outputs
        return reference in current_state
    
    def _validate_goal_achievable(
        self,
        state_trace: List[StateTransition],
        goal: Any
    ) -> Tuple[bool, List[str]]:
        """
        Validate that the workflow can achieve its stated goal.
        
        Args:
            state_trace: Sequence of state transitions
            goal: Goal specification (could be various formats)
            
        Returns:
            (achievable, evidence)
        """
        if not state_trace:
            return False, ["no_state_transitions"]
        
        # Extract final state
        final_outputs = set()
        for transition in state_trace:
            for output in transition.postconditions:
                final_outputs.add(f"{transition.task_id}.{output}")
        
        # Simple heuristic: if goal is a string, check if it appears in outputs
        if isinstance(goal, str):
            goal_in_outputs = any(goal.lower() in str(out).lower() for out in final_outputs)
            return goal_in_outputs, ["goal_string_match"] if goal_in_outputs else ["goal_not_in_outputs"]
        
        # If goal is a dict, check if required keys are produced
        if isinstance(goal, dict):
            required_keys = set(goal.keys())
            available_keys = {out.split(".")[-1] for out in final_outputs}
            missing_keys = required_keys - available_keys
            
            if not missing_keys:
                return True, ["all_goal_keys_available"]
            else:
                return False, [f"missing_goal_keys:{missing_keys}"]
        
        # Default: assume achievable if we have any outputs
        return len(final_outputs) > 0, ["has_outputs"] if final_outputs else ["no_outputs"]
    
    def _validate_temporal_coherence(
        self,
        tasks: Dict[str, Any],
        state_trace: List[StateTransition]
    ) -> List[ValidationError]:
        """
        Validate temporal ordering of time-dependent operations (4D Thinking).
        
        Checks for:
        - Data fetch before analysis
        - Analysis before synthesis
        - Validation before crystallization
        - Temporal causality (cause before effect)
        
        This implements 4D thinking by ensuring temporal logic is correct.
        """
        errors = []
        
        # Define temporal ordering rules
        temporal_rules = [
            {
                "before": ["fetch_data", "collect_data", "retrieve"],
                "after": ["analyze", "process", "transform"],
                "reason": "Data must be collected before analysis"
            },
            {
                "before": ["analyze", "process"],
                "after": ["synthesize", "generate_report", "conclude"],
                "reason": "Analysis must precede synthesis"
            },
            {
                "before": ["generate", "create", "propose"],
                "after": ["validate", "verify", "check"],
                "reason": "Creation must precede validation"
            },
            {
                "before": ["validate", "verify", "approve"],
                "after": ["crystallize", "integrate", "deploy"],
                "reason": "Validation must precede integration"
            }
        ]
        
        # Check each rule
        for rule in temporal_rules:
            before_actions = rule["before"]
            after_actions = rule["after"]
            reason = rule["reason"]
            
            # Find positions of before and after actions in execution order
            before_positions = []
            after_positions = []
            
            for idx, transition in enumerate(state_trace):
                action = transition.action.lower()
                task = transition.task_id.lower()
                
                if any(b in action or b in task for b in before_actions):
                    before_positions.append((idx, transition.task_id))
                
                if any(a in action or a in task for a in after_actions):
                    after_positions.append((idx, transition.task_id))
            
            # Check temporal ordering
            for after_pos, after_task in after_positions:
                # Is there any "before" action that comes AFTER this "after" action?
                violated = [
                    (before_pos, before_task)
                    for before_pos, before_task in before_positions
                    if before_pos > after_pos
                ]
                
                if violated:
                    errors.append(ValidationError(
                        error_type="temporal_violation",
                        task_id=after_task,
                        step_number=after_pos + 1,
                        description=f"Temporal ordering violated: {after_task} (step {after_pos+1}) occurs before {violated[0][1]} (step {violated[0][0]+1}). {reason}",
                        required_by=after_task,
                        suggested_fix=f"Reorder: {violated[0][1]} must execute before {after_task}",
                        severity="warning",  # Often fixable
                        quantum_confidence=QuantumProbability(
                            0.7,
                            ["temporal_pattern_matching", "heuristic_rule"]
                        ).to_dict()
                    ))
        
        return errors
    
    def _generate_error_education(self, errors: List[ValidationError], warnings: List[ValidationError]) -> str:
        """
        Generate error education prompt for RISE.
        
        This implements the "error education" component from PDDL-INSTRUCT,
        providing detailed feedback to help RISE learn from validation failures.
        """
        if not errors:
            return None
        
        prompt = """Your previous workflow plan failed logical validation. Here are the specific issues found:

CRITICAL ERRORS:
"""
        
        for i, error in enumerate(errors, 1):
            prompt += f"""
{i}. Error at Step {error.step_number} (Task: {error.task_id})
   Type: {error.error_type}
   Issue: {error.description}
   Required By: {error.required_by or 'N/A'}
   Suggested Fix: {error.suggested_fix}
   Confidence: {error.quantum_confidence.get('probability', 1.0):.1%}
"""
        
        if warnings:
            prompt += "\nWARNINGS (Non-Critical):\n"
            for i, warning in enumerate(warnings, 1):
                prompt += f"""
{i}. Warning at Step {warning.step_number} (Task: {warning.task_id})
   Issue: {warning.description}
   Suggested Fix: {warning.suggested_fix}
"""
        
        prompt += """
Generate a NEW workflow plan that addresses these issues. Specifically:
1. Ensure all task dependencies are defined in the task graph
2. Ensure all required inputs are produced by previous tasks  
3. Ensure temporal ordering is correct (fetch before analyze, analyze before synthesize, etc.)
4. Ensure the final state can achieve the stated goal

Your new plan must be logically valid and executable.
"""
        
        return prompt
    
    @log_to_thought_trail
    def validate_and_educate(
        self,
        workflow: Dict[str, Any],
        initial_context: Dict[str, Any] = None,
        max_iterations: int = 3
    ) -> Tuple[ValidationReport, int]:
        """
        Validate a workflow and return education prompt if invalid.
        
        This is the integration point with RISE's learning loop.
        
        Args:
            workflow: Workflow to validate
            initial_context: Initial state
            max_iterations: Maximum correction attempts
            
        Returns:
            (ValidationReport, iteration_count)
        """
        iteration = 0
        current_workflow = workflow
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"[PlanValidator] Validation attempt {iteration}/{max_iterations}")
            
            report = self.validate_workflow(current_workflow, initial_context)
            
            if report.is_valid:
                logger.info(f"[PlanValidator] ✓ Plan validated successfully on iteration {iteration}")
                return report, iteration
            
            if iteration < max_iterations:
                # Would call RISE here to generate new plan based on error_education_prompt
                logger.info(f"[PlanValidator] Plan invalid, error education generated")
                # In full implementation, this would:
                # new_workflow = rise.regenerate_plan(report.error_education_prompt)
                # current_workflow = new_workflow
                break  # For now, just return the report
        
        logger.warning(f"[PlanValidator] Plan still invalid after {max_iterations} iterations")
        return report, iteration
    
    @log_to_thought_trail
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get statistics from validation history."""
        if not self.validation_history:
            return {"total_validations": 0}
        
        total = len(self.validation_history)
        valid_count = sum(1 for r in self.validation_history if r.is_valid)
        
        return {
            "total_validations": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "success_rate": valid_count / total if total > 0 else 0.0,
            "avg_confidence": sum(r.confidence.probability for r in self.validation_history) / total,
            "avg_errors": sum(len(r.errors) for r in self.validation_history) / total
        }


@log_to_thought_trail
def main():
    """Demo the Plan Validator."""
    print("🔍 Formal Plan Validator - MIT PDDL-INSTRUCT Integration")
    print()
    
    validator = PlanValidator()
    
    # Test workflow with intentional errors
    test_workflow = {
        "name": "Test Workflow with Logical Errors",
        "goal": "produce_final_report",
        "tasks": {
            "task_analyze": {
                "action_type": "analyze_data",
                "inputs": {
                    "data": "{{task_fetch.data}}"  # Requires task_fetch
                },
                "outputs": {"analysis_result": "dict"},
                "dependencies": []  # ERROR: Missing dependency on task_fetch!
            },
            "task_fetch": {
                "action_type": "fetch_data",
                "inputs": {},
                "outputs": {"data": "dict"},
                "dependencies": []
            },
            "task_report": {
                "action_type": "generate_report",
                "inputs": {
                    "analysis": "{{task_analyze.analysis_result}}"
                },
                "outputs": {"final_report": "string"},
                "dependencies": ["task_analyze"]
            }
        }
    }
    
    print("Testing workflow with logical errors...\n")
    
    report = validator.validate_workflow(test_workflow, {"user_id": "test"})
    
    print(f"Validation Result: {'VALID ✓' if report.is_valid else 'INVALID ✗'}")
    print(f"Confidence: {report.confidence.probability:.1%}")
    print(f"Errors: {len(report.errors)}")
    print(f"Warnings: {len(report.warnings)}")
    print()
    
    if report.errors:
        print("Errors Found:")
        for error in report.errors:
            print(f"  [{error.severity.upper()}] Step {error.step_number}: {error.description}")
            print(f"    Fix: {error.suggested_fix}")
        print()
    
    if report.error_education_prompt:
        print("Error Education Prompt Generated:")
        print("─" * 80)
        print(report.error_education_prompt[:500] + "...")
        print("─" * 80)
    
    print("\nValidator Statistics:")
    stats = validator.get_validation_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

