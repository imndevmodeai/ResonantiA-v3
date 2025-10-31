# Adaptive RISE Architecture - Transformation Plan

## Overview
Transform RISE from hardcoded A, B, C, D phases into an adaptive, agent-driven framework where the agent dynamically selects phases based on problem analysis.

## Current State Analysis

### Existing Infrastructure ✅
1. **SpecializedAgent** (`specialized_agent.py`):
   - Generates detailed action plans with phases, capabilities, and sequences
   - Includes parallel groups, reassessment gates, and rationale
   - Integrates with WorkflowActionDiscovery

2. **PlaybookOrchestrator** (`playbook_orchestrator.py`):
   - Executes agent action plans with sequential and parallel execution
   - Supports reassessment gates and dynamic adjustment
   - Can execute workflows and individual actions

3. **WorkflowActionDiscovery** (`workflow_action_discovery.py`):
   - Discovers available workflows and actions
   - Provides recommendations based on problem description
   - Enables dynamic capability selection

4. **SynthesisEngine** (`synthesis_engine.py`):
   - Provides synthesis of multi-source data
   - Transforms raw data into coherent insights
   - Generates IAR compliance

5. **SPR System**:
   - Integrated into RISE orchestrator
   - Provides cognitive enhancement through primed knowledge

### Current Limitations
1. **Hardcoded Phases**: RISE uses fixed A, B, C, D phases
2. **Static Flow**: Cannot adapt based on problem requirements
3. **Limited Synthesis**: SynthesisEngine not integrated
4. **SPR Usage**: SPRs are detected but not actively used to enhance processing
5. **Parallelization**: Limited parallel execution support

## Target Architecture

### Core Transformation
Make RISE an **Adaptive RISE Framework** where:

1. **Agent-Driven Phase Selection**:
   - Agent analyzes the problem
   - Agent selects relevant phases from available options
   - Phases are not hardcoded (A, B, C, D) but descriptive (protocol_priming, intent_intake, conceptual_map, etc.)

2. **Dynamic Workflow Integration**:
   - Agent discovers relevant workflows
   - Agent integrates workflows into the plan
   - Workflows can be invoked individually or as part of sequences

3. **SPR-Enhanced Processing**:
   - SPRs ignite cognitive keys at each phase
   - SPRs enhance context and understanding
   - SPRs guide tool selection and parameter setting

4. **Synthesis-Integrated**:
   - SynthesisEngine provides final synthesis
   - Synthesis combines multi-source analysis
   - Synthesis produces coherent, structured insights

5. **Reassessment & Loops**:
   - Reassessment gates after each phase
   - Ability to loop with different parameters
   - Ability to update path based on prior results

### Implementation Strategy

#### Phase 1: Transform RISE Phase A
- Instead of hardcoded `knowledge_scaffolding.json`
- Agent selects phases from available options
- Agent can mix workflows and actions
- SPRs enhance each phase

#### Phase 2: Integrate Synthesis Engine
- Add synthesis phase to agent-generated plans
- SynthesisEngine synthesizes all phase results
- Synthesis provides final coherent answer

#### Phase 3: Enable Dynamic Parallelization
- Identify parallel opportunities from dependencies
- Execute parallel phases when dependencies allow
- Aggregate parallel results

#### Phase 4: Add Reassessment Loops
- Implement reassessment gates
- Allow parameter adjustment and re-execution
- Track ThoughtTrail through loops

## Example User Workflow Structure

The user's example shows:
```json
{
  "workflow_name": "Dynamic Analysis: ...",
  "description": "...",
  "tasks": {
    "protocol_priming": {
      "description": "...",
      "action_type": "execute_code",
      "inputs": {...},
      "outputs": {...},
      "dependencies": []
    },
    "intent_intake": {
      "description": "...",
      "action_type": "generate_text_llm",
      "inputs": {...},
      "outputs": {...},
      "dependencies": ["protocol_priming"]
    },
    // ... more phases
  }
}
```

Key Features:
- Dynamic phase names (not hardcoded)
- action_type specifies what to do
- dependencies define execution order
- inputs reference previous outputs
- outputs feed into next phases

## Implementation Files

### Key Changes Needed

1. **`rise_orchestrator.py`**:
   - Modify `process_query()` to use agent-driven phases
   - Remove hardcoded A, B, C, D phase execution
   - Add synthesis phase integration
   - Add reassessment loop support

2. **`specialized_agent.py`** (Already Enhanced):
   - ✅ Generate dynamic action plans
   - ✅ Include reassessment gates
   - ✅ Support parallel execution
   - ✅ Integrate with WorkflowActionDiscovery

3. **`playbook_orchestrator.py`** (Already Enhanced):
   - ✅ Execute agent action plans
   - ✅ Support sequential and parallel execution
   - ✅ Handle reassessment gates
   - ✅ Execute workflows and actions dynamically

4. **New Integration Layer** (To Be Created):
   - Connect RISE → Agent → Playbook Orchestrator → Synthesis
   - Manage reassessment loops
   - Track ThoughtTrail
   - Coordinate SPR priming

## Success Criteria

1. ✅ Agent selects phases dynamically
2. ✅ SPRs enhance cognitive processing
3. ✅ Synthesis Engine provides final synthesis
4. ✅ Reassessment gates enable dynamic adjustment
5. ✅ Parallel execution when dependencies allow
6. ✅ ThoughtTrail shows all processing
7. ✅ Final response is coherent and structured

## Next Steps

1. Create comprehensive implementation
2. Test with example problem
3. Validate reassessment loops
4. Verify synthesis integration
5. Ensure SPR enhancement throughout

