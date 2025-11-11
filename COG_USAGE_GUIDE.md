# CrystallizedObjectiveGenerator (COG) Usage Guide

## Overview

The `CrystallizedObjectiveGenerator` (COG) transforms natural-language mandates into structured `CrystallizedObjective` artifacts. It implements an 8-stage crystallization process that extracts features, analyzes temporal scope, activates SPRs (Strategic Pattern Recognition), and composes executable steps.

## Table of Contents

1. [How You Use It (Direct Python API)](#how-you-use-it-direct-python-api)
2. [How ArchE Uses It (System Integration)](#how-arche-uses-it-system-integration)
3. [Advanced Usage Patterns](#advanced-usage-patterns)
4. [Integration Examples](#integration-examples)

---

## How You Use It (Direct Python API)

### Basic Usage: Simple Mandate → Objective

```python
from crystallized_objective_generator import (
    CrystallizedObjectiveGenerator,
    SPR
)

# 1. Define your SPR bank (patterns that COG can activate)
def load_my_spr_bank():
    return [
        SPR(
            id="spr_001",
            name="DataCollection",
            tags=["data", "collection", "research"],
            signature={"keywords": ["gather", "collect", "research"]},
            pattern="Collect data from sources X, Y, Z",
            preconditions={"requires_access": True},
            effects={"data_available": True},
            cost=1.0
        ),
        # ... more SPRs
    ]

# 2. Initialize COG
cog = CrystallizedObjectiveGenerator(
    spr_bank_loader=load_my_spr_bank,
    max_candidates=128
)

# 3. Define a mandate (natural language request)
mandate_dict = {
    "id": "mandate_001",
    "issuer": "user",
    "text": "Analyze the economic impact of implementing Universal Basic Income in region Alpha over the next 5 years",
    "priority": 1,
    "tags": ["economic", "policy", "temporal"],
    "domain": "cognitive"
}

# 4. Generate the crystallized objective
objective = cog.generate(mandate_dict)

# 5. Inspect the result
print(f"Acceptance Score: {objective.acceptance_score}")
print(f"Number of Steps: {len(objective.steps)}")
for step in objective.steps:
    print(f"  - {step.title}: {step.description}")
```

### Custom SPR Bank Loading

You can load SPRs from various sources:

```python
import json
from pathlib import Path

# Option 1: Load from JSON file
def load_sprs_from_json():
    spr_file = Path("knowledge_graph/spr_definitions_tv.json")
    with open(spr_file) as f:
        data = json.load(f)
    return [SPR(**spr_dict) for spr_dict in data.get("sprs", [])]

# Option 2: Load from ArchE's SPR Manager
def load_sprs_from_arche():
    from Three_PointO_ArchE.spr_manager import SPRManager
    manager = SPRManager()
    spr_defs = manager.get_all_sprs()
    return [SPR(**spr) for spr in spr_defs]

# Option 3: Hybrid (combine multiple sources)
def load_hybrid_spr_bank():
    spr_list = []
    spr_list.extend(load_sprs_from_json())
    spr_list.extend(load_sprs_from_arche())
    return spr_list

cog = CrystallizedObjectiveGenerator(spr_bank_loader=load_hybrid_spr_bank)
```

### M9/M6 Mandate Customization

COG automatically detects mandate tags and customizes the objective accordingly:

```python
# M9: Complex System Visioning mandate
m9_mandate = {
    "id": "m9_example",
    "issuer": "keyholder",
    "text": "Design a framework for dynamically adjusting analytical strategies based on real-time IAR feedback loops and predicted task difficulty",
    "priority": 9,
    "tags": ["complex_system", "visioning", "adaptive", "iar", "temporal"],
    "domain": "cognitive",
    "constraints": {
        "requires_temporal_reasoning": True,
        "requires_abm": True,
        "requires_cfp": True
    }
}

objective = cog.generate(m9_mandate)
# COG will:
# - Activate ComplexSystemVisioning SPRs
# - Include temporal analysis (H, T, F, C, E, Tr subsystems)
# - Generate steps that incorporate ABM and CFP tools
# - Ensure IAR compliance in all steps
```

### Deterministic vs. Stochastic Mode

```python
# Deterministic: Same mandate → same objective (uses hash-based seed)
objective_det = cog.generate(mandate_dict, mode="deterministic")

# Stochastic: Each run may produce different SPR activations
objective_stoch = cog.generate(mandate_dict, mode="stochastic")

# Custom seed for reproducibility
mandate_with_seed = {**mandate_dict, "seed": 42}
objective_seeded = cog.generate(mandate_with_seed)
```

### Custom Scoring Function

You can customize how COG scores SPR candidates:

```python
def custom_scoring_fn(features, spr, temporal_scope):
    """
    Custom scoring: prioritize SPRs with matching tags
    """
    base_score = 0.5
    mandate_tags = features.categorical.get("tags", [])
    spr_tags = spr.tags
    
    # Boost score for tag matches
    tag_overlap = len(set(mandate_tags) & set(spr_tags))
    tag_score = tag_overlap * 0.2
    
    # Boost for temporal alignment
    temporal_score = 0.1 if temporal_scope.granularity == spr.temporal_hint else 0.0
    
    return base_score + tag_score + temporal_score

cog = CrystallizedObjectiveGenerator(
    spr_bank_loader=load_my_spr_bank,
    scoring_fn=custom_scoring_fn
)
```

### Safety Validation

COG includes built-in safety validation, but you can customize it:

```python
def strict_safety_validator(objective, mandate):
    """
    Custom validator: reject objectives with too many steps or high cost
    """
    issues = []
    
    if len(objective.steps) > 20:
        issues.append("Too many steps (>20)")
    
    total_cost = sum(step.estimated_cost for step in objective.steps)
    if total_cost > 100.0:
        issues.append(f"Total cost too high ({total_cost})")
    
    # Check for dangerous patterns
    for step in objective.steps:
        if "delete" in step.description.lower() and "backup" not in step.description.lower():
            issues.append(f"Step {step.id} may be destructive without backup")
    
    is_valid = len(issues) == 0
    return is_valid, issues

cog = CrystallizedObjectiveGenerator(
    spr_bank_loader=load_my_spr_bank,
    safety_validator=strict_safety_validator
)
```

---

## How ArchE Uses It (System Integration)

### Integration Point: Workflow Engine Pre-Processing

ArchE integrates COG into its workflow engine as a pre-processing step. When a user query arrives, ArchE:

1. **Detects if query requires objective generation** (via RISE orchestrator or cognitive integration hub)
2. **Invokes COG** to crystallize the mandate
3. **Converts the objective** into workflow tasks
4. **Executes the workflow** using the IAR-compliant workflow engine

### Architecture Flow

```
User Query
    ↓
Cognitive Integration Hub
    ↓
RISE Orchestrator (for complex queries)
    ↓
COG.generate(mandate_dict)  ← COG Integration Point
    ↓
CrystallizedObjective (steps, temporal_scope, activated_sprs)
    ↓
Workflow Engine (converts steps → workflow tasks)
    ↓
Action Registry (executes individual actions)
    ↓
IAR-Compliant Results
```

### Code Integration Example

```python
# In Three_PointO_ArchE/cognitive_integration_hub.py or rise_orchestrator.py

from crystallized_objective_generator import CrystallizedObjectiveGenerator
from Three_PointO_ArchE.spr_manager import SPRManager

class ArchECognitiveHub:
    def __init__(self):
        # Initialize COG with ArchE's SPR bank
        self.cog = CrystallizedObjectiveGenerator(
            spr_bank_loader=self._load_arche_spr_bank,
            max_candidates=256  # ArchE uses larger candidate pool
        )
        self.spr_manager = SPRManager()
        self.workflow_engine = IARCompliantWorkflowEngine()
    
    def _load_arche_spr_bank(self):
        """Load SPRs from ArchE's knowledge graph"""
        spr_defs = self.spr_manager.get_all_sprs()
        return [SPR(**spr) for spr in spr_defs]
    
    def process_query(self, query: str, context: Dict[str, Any] = None):
        """
        Main entry point: converts user query into executed workflow
        """
        # 1. Convert query to mandate
        mandate_dict = {
            "id": str(uuid.uuid4()),
            "issuer": context.get("user_id", "user"),
            "text": query,
            "priority": context.get("priority", 1),
            "tags": self._extract_tags(query),
            "domain": "cognitive",
            "context": context or {}
        }
        
        # 2. Generate crystallized objective
        objective = self.cog.generate(mandate_dict, context=context)
        
        # 3. Convert objective steps to workflow tasks
        workflow_tasks = self._objective_to_workflow(objective)
        
        # 4. Execute workflow
        result = self.workflow_engine.execute_workflow(
            workflow_name="dynamic_objective_workflow",
            initial_context={"tasks": workflow_tasks, "objective": objective}
        )
        
        return result
    
    def _objective_to_workflow(self, objective: CrystallizedObjective) -> List[Dict]:
        """
        Converts CrystallizedObjective steps into workflow task definitions
        """
        tasks = []
        for step in objective.steps:
            task = {
                "id": step.id,
                "name": step.title,
                "action": self._map_step_to_action(step),
                "inputs": step.outputs,  # Previous step outputs become inputs
                "dependencies": step.dependencies,
                "conditions": self._build_conditions(step),
                "metadata": step.metadata
            }
            tasks.append(task)
        return tasks
    
    def _map_step_to_action(self, step: Step) -> str:
        """
        Maps a COG step to an ArchE action type
        """
        # Use step metadata or description to determine action
        if "data_collection" in step.metadata.get("tags", []):
            return "data_collection"
        elif "analysis" in step.metadata.get("tags", []):
            return "run_analysis"
        elif "modeling" in step.metadata.get("tags", []):
            return "run_cfp"  # or perform_abm, perform_causal_inference
        else:
            return "generate_text_llm"  # Default fallback
```

### SPR Manager Integration

COG seamlessly integrates with ArchE's SPR Manager:

```python
from Three_PointO_ArchE.spr_manager import SPRManager

class ArchECOGIntegration:
    def __init__(self):
        self.spr_manager = SPRManager()
        self.cog = CrystallizedObjectiveGenerator(
            spr_bank_loader=self._load_from_spr_manager
        )
    
    def _load_from_spr_manager(self):
        """Load SPRs directly from SPR Manager"""
        all_sprs = self.spr_manager.get_all_sprs()
        return [
            SPR(
                id=spr.get("id"),
                name=spr.get("name"),
                tags=spr.get("tags", []),
                signature=spr.get("signature", {}),
                pattern=spr.get("pattern", ""),
                preconditions=spr.get("preconditions", {}),
                effects=spr.get("effects", {}),
                cost=spr.get("cost", 1.0),
                temporal_hint=spr.get("temporal_hint"),
                metadata=spr.get("metadata", {})
            )
            for spr in all_sprs
        ]
```

### Objective → Workflow Conversion

The key integration is converting COG's `CrystallizedObjective` into ArchE's workflow format:

```python
def convert_objective_to_workflow(objective: CrystallizedObjective) -> Dict:
    """
    Converts a CrystallizedObjective into a Process Blueprint (workflow JSON)
    """
    workflow = {
        "name": f"crystallized_objective_{objective.metadata.get('id', 'unknown')}",
        "version": "1.0",
        "description": f"Generated from mandate: {objective.metadata.get('mandate_id')}",
        "tasks": []
    }
    
    for step in objective.steps:
        task = {
            "id": step.id,
            "name": step.title,
            "description": step.description,
            "action": determine_action_type(step),
            "inputs": build_task_inputs(step),
            "dependencies": step.dependencies,
            "conditions": build_conditions(step, objective),
            "metadata": {
                **step.metadata,
                "estimated_cost": step.estimated_cost,
                "temporal_window": step.temporal_window
            }
        }
        workflow["tasks"].append(task)
    
    return workflow
```

### Temporal Resonance Integration

COG's temporal scope integrates with ArchE's 4D thinking capabilities:

```python
def integrate_temporal_resonance(objective: CrystallizedObjective, arche_context: Dict):
    """
    Integrates COG's temporal analysis with ArchE's temporal reasoning engine
    """
    temporal_scope = objective.temporal_scope
    
    # Extract temporal analysis results from COG
    h_analysis = temporal_scope.analysis_results.get("H", {})  # Historical
    t_analysis = temporal_scope.analysis_results.get("T", {})   # Temporal dynamics
    f_analysis = temporal_scope.analysis_results.get("F", {})   # Future state
    c_analysis = temporal_scope.analysis_results.get("C", {})   # Causal
    e_analysis = temporal_scope.analysis_results.get("E", {})   # Emergence
    tr_analysis = temporal_scope.analysis_results.get("Tr", {}) # Trajectory
    
    # Feed into ArchE's temporal reasoning engine
    from Three_PointO_ArchE.temporal_reasoning_engine import TemporalReasoningEngine
    temporal_engine = TemporalReasoningEngine()
    
    # Use COG's temporal insights to inform ArchE's analysis
    enhanced_context = {
        **arche_context,
        "temporal_scope": temporal_scope,
        "temporal_insights": {
            "historical": h_analysis,
            "dynamics": t_analysis,
            "future": f_analysis,
            "causal": c_analysis,
            "emergence": e_analysis,
            "trajectory": tr_analysis
        }
    }
    
    return enhanced_context
```

---

## Advanced Usage Patterns

### Pattern 1: Multi-Stage Objective Refinement

```python
# Stage 1: Generate initial objective
initial_objective = cog.generate(mandate_dict)

# Stage 2: Refine based on feedback
refined_mandate = {
    **mandate_dict,
    "context": {
        **mandate_dict.get("context", {}),
        "previous_objective": initial_objective,
        "feedback": "Need more granular steps for data collection phase"
    }
}
refined_objective = cog.generate(refined_mandate)

# Stage 3: Merge objectives
merged_steps = initial_objective.steps[:2] + refined_objective.steps[2:]
```

### Pattern 2: Objective Comparison (CFP Integration)

```python
# Generate two objectives for the same mandate with different seeds
obj_a = cog.generate({**mandate_dict, "seed": 1})
obj_b = cog.generate({**mandate_dict, "seed": 2})

# Use CFP to compare the two objective trajectories
from cfp_framework import CfpframeworK

# Convert objectives to state vectors
state_a = objective_to_state_vector(obj_a)
state_b = objective_to_state_vector(obj_b)

# Run CFP comparison
cfp_result = CfpframeworK(
    system_a_config={"quantum_state": state_a},
    system_b_config={"quantum_state": state_b}
).run_analysis()

print(f"Objective divergence: {cfp_result['quantum_flux_difference']}")
```

### Pattern 3: Objective Validation Before Execution

```python
def validate_and_execute(mandate_dict):
    # Generate objective
    objective = cog.generate(mandate_dict)
    
    # Validate acceptance score
    if objective.acceptance_score < 0.7:
        print(f"Warning: Low acceptance score ({objective.acceptance_score})")
        print("Explanations:", objective.explanations)
        # Optionally refine or reject
    
    # Check temporal feasibility
    if objective.temporal_scope.end and objective.temporal_scope.end < time.time():
        raise ValueError("Objective deadline has already passed")
    
    # Execute only if validation passes
    if objective.acceptance_score >= 0.7:
        return execute_objective(objective)
    else:
        return {"status": "rejected", "reason": "Low acceptance score"}
```

---

## Integration Examples

### Example 1: RISE Orchestrator Integration

```python
# In Three_PointO_ArchE/rise_orchestrator.py

class RISE_Orchestrator:
    def __init__(self):
        self.cog = CrystallizedObjectiveGenerator(
            spr_bank_loader=self._load_arche_sprs
        )
    
    def process_query(self, query: str):
        # Convert query to mandate
        mandate = self._query_to_mandate(query)
        
        # Generate objective
        objective = self.cog.generate(mandate)
        
        # Use objective in knowledge scaffolding phase
        enriched_problem_description = self._objective_to_problem_description(objective)
        
        # Continue with RISE phases...
        return self._execute_rise_phases(enriched_problem_description)
```

### Example 2: Workflow Engine Action

```python
# Register COG as a workflow action
from Three_PointO_ArchE.action_registry import register_action

@register_action("generate_crystallized_objective")
def generate_crystallized_objective_action(inputs: Dict, context: Dict) -> Dict:
    """
    Workflow action that uses COG to generate objectives
    """
    from crystallized_objective_generator import CrystallizedObjectiveGenerator
    
    mandate_dict = inputs.get("mandate", {})
    cog = CrystallizedObjectiveGenerator(
        spr_bank_loader=lambda: load_sprs_from_context(context)
    )
    
    objective = cog.generate(mandate_dict, context=context)
    
    # Return IAR-compliant result
    return {
        "objective": asdict(objective),
        "reflection": {
            "status": "success",
            "confidence": objective.acceptance_score,
            "issues": objective.explanations if objective.acceptance_score < 0.8 else [],
            "alignment": "high" if objective.acceptance_score >= 0.8 else "medium"
        }
    }
```

### Example 3: M9 Complex Visioning Workflow

```python
# M9 mandate example with full ArchE integration
m9_mandate = {
    "id": "m9_complex_vision",
    "text": "Design an adaptive workflow orchestration system that dynamically adjusts based on IAR feedback",
    "tags": ["complex_system", "visioning", "adaptive", "iar"],
    "priority": 9
}

objective = cog.generate(m9_mandate)

# Convert to workflow
workflow = convert_objective_to_workflow(objective)

# Execute with ArchE's workflow engine
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
engine = IARCompliantWorkflowEngine()
result = engine.execute_workflow(workflow, initial_context={})

# The workflow will:
# - Execute steps in dependency order
# - Generate IAR for each step
# - Use IAR feedback to adjust subsequent steps (adaptive behavior)
# - Integrate with CFP, ABM, and causal inference tools as needed
```

---

## Summary

**For Direct Use:**
- Initialize COG with your SPR bank
- Call `generate()` with a mandate dictionary
- Inspect the returned `CrystallizedObjective`
- Execute the steps manually or convert to your execution framework

**For ArchE Integration:**
- COG acts as a pre-processor before workflow execution
- Converts natural language → structured objective → workflow tasks
- Integrates with SPR Manager, Workflow Engine, and Temporal Reasoning
- Ensures IAR compliance and temporal resonance throughout

The COG is designed to be both a standalone tool for objective generation and a core component of ArchE's cognitive architecture, bridging the gap between human intent and machine execution.

