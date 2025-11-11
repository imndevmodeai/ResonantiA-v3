# Codebase Archaeology + RISE Integration Implementation Plan

## Current Status

✅ **CodebaseArchaeologist exists** and is partially integrated into RISE orchestrator
✅ **Action wrappers created** in `codebase_archaeology_actions.py`
❌ **Actions not yet registered** in action registry
❌ **Enhanced workflows not created** (using old text-only workflows)
❌ **Workflow routing bug** (using wrong strategy_fusion.json)

## Critical Issues Identified

### 1. Missing Tool Invocation
- **Problem**: RISE Phase B uses `workflows/strategy_fusion.json` (text-only) instead of `core_workflows/1_cognitive_engine/strategy_fusion.json` (with CFP/ABM/Causal Inference)
- **Impact**: Complex System Visioning tools never invoked
- **Fix**: Update `_execute_phase_b()` to use correct workflow path

### 2. Missing Data Preparation
- **Problem**: CFP, ABM, and Causal Inference tools need prepared data structures
- **Impact**: Even if tools are invoked, they won't have data to work with
- **Fix**: Add data preparation tasks in Phase A/B

### 3. Codebase Archaeology Actions Not Registered
- **Problem**: Workflows can't call `search_codebase`, `synthesize_from_patterns`, `validate_against_patterns`
- **Impact**: Codebase archaeology integration incomplete
- **Fix**: Register actions in action_registry.py

## Implementation Steps

### Step 1: Register Codebase Archaeology Actions

**File**: `Three_PointO_ArchE/action_registry.py`

Add at end of file (after existing registrations):

```python
# Register codebase archaeology actions
try:
    from .codebase_archaeology_actions import (
        search_codebase_action,
        synthesize_from_patterns_action,
        validate_against_patterns_action,
        set_archaeologist
    )
    main_action_registry.register_action("search_codebase", search_codebase_action)
    main_action_registry.register_action("synthesize_from_patterns", synthesize_from_patterns_action)
    main_action_registry.register_action("validate_against_patterns", validate_against_patterns_action)
    logger.info("Codebase archaeology actions registered")
except ImportError as e:
    logger.warning(f"Codebase archaeology actions not available: {e}")
```

**In RISE Orchestrator** (`rise_orchestrator.py`), after initializing CodebaseArchaeologist:

```python
# Set archaeologist for action registry
try:
    from .codebase_archaeology_actions import set_archaeologist
    if self.codebase_archaeologist:
        set_archaeologist(self.codebase_archaeologist)
        logger.info("CodebaseArchaeologist linked to action registry")
except ImportError:
    pass
```

### Step 2: Fix Workflow Routing

**File**: `Three_PointO_ArchE/rise_orchestrator.py`

**Line ~1446**: Change from:
```python
fusion_path = os.path.join(self.workflows_dir, "strategy_fusion.json")
```

To:
```python
# Use enhanced strategy fusion with CFP/ABM/Causal Inference
core_workflows_dir = os.path.join(os.path.dirname(self.workflows_dir), "core_workflows", "1_cognitive_engine")
enhanced_fusion_path = os.path.join(core_workflows_dir, "strategy_fusion.json")
if os.path.exists(enhanced_fusion_path):
    fusion_path = enhanced_fusion_path
    logger.info("Using enhanced strategy_fusion.json with CFP/ABM/Causal Inference")
else:
    fusion_path = os.path.join(self.workflows_dir, "strategy_fusion.json")
    logger.warning("Falling back to basic strategy_fusion.json")
```

### Step 3: Add Data Preparation Tasks

**Create**: `workflows/data_preparation_for_tools.json`

This workflow prepares data structures for CFP, ABM, and Causal Inference tools based on the problem domain.

### Step 4: Create Enhanced Phase A Workflow

**Create**: `workflows/knowledge_scaffolding_with_codebase.json`

Enhances existing `knowledge_scaffolding.json` with:
- Codebase pattern search task
- Synthesis of external + codebase knowledge

### Step 5: Create Enhanced Phase B Workflow

**Update**: `core_workflows/1_cognitive_engine/strategy_fusion.json`

Add codebase archaeology tasks for each pathway:
- `codebase_causal_patterns` - Find causal inference implementations
- `codebase_abm_patterns` - Find ABM implementations  
- `codebase_cfp_patterns` - Find CFP implementations
- `synthesize_causal_insight` - Combine external + codebase
- `synthesize_abm_insight` - Combine external + codebase
- `synthesize_cfp_insight` - Combine external + codebase

### Step 6: Enhance Phase C Vetting

**Update**: `workflows/high_stakes_vetting.json`

Add:
- `codebase_pattern_validation` task using `validate_against_patterns` action

### Step 7: Enhance Phase D SPR Distillation

**Update**: `workflows/distill_spr.json`

Add:
- Detection of novel codebase combinations
- SPR candidate generation from codebase synthesis

## Example: Tyson vs Foreman Query

### What Should Happen:

**Phase A Enhanced**:
1. External search: "Mike Tyson vs George Foreman boxing analysis"
2. **Codebase search**: Finds `agent_based_modeling_tool.py`, `cfp_framework.py`, `causal_inference_tool.py`
3. Synthesize: "Use ABM to simulate fight dynamics, CFP to compare scenarios, Causal Inference to identify win factors"

**Phase B Enhanced**:
1. **Data Preparation**: 
   - Build Tyson state vector: `[power: 0.95, speed: 0.90, defense: 0.75, stamina: 0.80]`
   - Build Foreman state vector: `[power: 0.98, speed: 0.70, defense: 0.85, stamina: 0.90]`
   - Create ABM schema: `FighterAgent` with attributes and behavioral rules
   - Prepare causal data: Historical fight outcomes vs fighter attributes
2. **Run Tools**:
   - CFP: Compare Tyson vs Foreman state evolution over 12 rounds
   - ABM: Simulate 1000 fights with emergent dynamics
   - Causal Inference: Identify which attributes most predict victory
3. **Codebase Synthesis**: Combine tool results with codebase implementation patterns
4. **Final Synthesis**: "Based on CFP trajectory analysis, ABM simulations (Tyson wins 62% of 1000 simulations), and causal analysis (speed + power combination is strongest predictor), **Tyson would win** in early rounds due to speed advantage, but Foreman's power and stamina give him edge in later rounds. Overall: **Tyson 55%, Foreman 45%**"

**Phase C Enhanced**:
- Validate strategy against codebase patterns (IAR compliance, SPR integration)
- Ensure answer aligns with tool results

**Phase D Enhanced**:
- Distill novel combination: "BoxingMatchAnalysiS" SPR combining CFP + ABM + Causal Inference

## Benefits

1. **Self-Awareness**: RISE knows its own capabilities
2. **Grounded Solutions**: External knowledge validated against internal implementation
3. **Novel Synthesis**: Combining codebase patterns creates new solutions
4. **Implementation Resonance**: Solutions align with existing architecture
5. **Actual Tool Usage**: CFP, ABM, Causal Inference actually invoked with data
6. **Real Answers**: Provides actual predictions/analysis, not just text

## Next Actions

1. ✅ Create action wrappers (DONE)
2. ⏳ Register actions in action_registry.py
3. ⏳ Fix workflow routing in rise_orchestrator.py
4. ⏳ Create enhanced workflows
5. ⏳ Add data preparation workflow
6. ⏳ Test with Tyson vs Foreman query




