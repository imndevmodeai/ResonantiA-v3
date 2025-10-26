# The Sacred Scrolls: ArchE Workflow Catalog

## Purpose

This is the **master index** of all workflows in the ArchE system. Each workflow is a living specification that can recreate itself from its documentation alone, embodying the principle of **Implementation Resonance**.

> **The Eternal Principle**: Specifications ARE ArchE. The code is merely the manifestation.

---

## Workflow Classification

### Core RISE Workflows (The Four Phases)

These workflows comprise the RISE Orchestrator—ArchE's deepest strategic thinking system.

| Workflow | Phase | Purpose | Specification | Implementation | Status |
|----------|-------|---------|---------------|----------------|--------|
| **Knowledge Scaffolding** | Phase A | Bootstrap domain expertise from first principles | `specifications/knowledge_scaffolding_workflow.md` | `workflows/knowledge_scaffolding.json` | ✅ COMPLETE |
| **Strategy Fusion** | Phase B | Synthesize multi-perspective strategic insights | `specifications/strategy_fusion_workflow.md` | `workflows/strategy_fusion.json` | ✅ COMPLETE |
| **High-Stakes Vetting** | Phase C | Adversarially validate strategies | `specifications/high_stakes_vetting_workflow.md` | `workflows/high_stakes_vetting.json` | ✅ COMPLETE |
| **SPR Distillation** | Phase D | Crystallize validated strategies into SPRs | `specifications/spr_distillation_workflow.md` | `workflows/distill_spr.json` | 🚧 SPEC NEEDED |

---

### Meta-System Workflows

These workflows enable ArchE to create, modify, and understand itself.

| Workflow | Purpose | Specification | Implementation | Status |
|----------|---------|---------------|----------------|--------|
| **Autopoietic Genesis Protocol** | Self-creation from specifications | `specifications/autopoietic_genesis_protocol.md` | `workflows/autopoietic_genesis_protocol.json` | 🚧 IMPLEMENTATION NEEDED |
| **System Self-Analysis** | Compare map (specs) vs territory (code) | `specifications/autopoietic_self_analysis.md` | `Three_PointO_ArchE/autopoietic_self_analysis.py` | ✅ OPERATIONAL |
| **Autopoietic Learning Loop** | Self-evolution through pattern detection | `specifications/autopoietic_learning_loop.md` | `Three_PointO_ArchE/autopoietic_learning_loop.py` | ✅ OPERATIONAL |

---

### Analytical Workflows

Workflows that perform specific types of analysis or problem-solving.

| Workflow | Purpose | Tools Used | Specification | Status |
|----------|---------|------------|---------------|--------|
| **Causal Inference Analysis** | Discover causal relationships in data | Causal Inference Tool | `specifications/causal_inference_tool.md` | ✅ TOOL SPEC |
| **Predictive Modeling** | Forecast future states | Predictive Modeling Tool | `specifications/predictive_modeling_tool.md` | ✅ TOOL SPEC |
| **Agent-Based Modeling** | Simulate emergent system behavior | ABM Tool + DSL Engine | `specifications/agent_based_modeling_tool.md`, `specifications/abm_dsl_engine.md` | ✅ TOOL SPECS |
| **Comparative Fluxual Processing** | Quantum-enhanced system comparison | CFP Framework | `specifications/cfp_framework.md` | ✅ FRAMEWORK SPEC |

---

### Management & Orchestration Workflows

Workflows that manage ArchE's work and resources.

| Workflow | Purpose | Specification | Implementation | Status |
|----------|---------|---------------|----------------|--------|
| **Autonomous Orchestration** | CEO-level work management | `specifications/autonomous_orchestrator.md` | `Three_PointO_ArchE/autonomous_orchestrator.py` | 🚧 IMPLEMENTATION NEEDED |
| **Guardian Queue Management** | Human oversight for critical decisions | `specifications/cognitive_immune_system.md` | Integrated in ACO/Learning Loop | ✅ OPERATIONAL |

---

## Workflow Lifecycle: From Specification to Reality

### The Ideal Development Process

```
1. SPECIFICATION FIRST
   └─> Write complete living specification in specifications/
       ├─> Philosophical mandate (Why)
       ├─> Allegorical story (How - for humans)
       ├─> Technical blueprint (What - for machines)
       ├─> SPR integration (Where it fits)
       └─> Example applications (When to use)

2. SPR DEFINITION
   └─> Add SPRs to knowledge_graph/spr_definitions_tv.json
       ├─> Primary workflow SPR
       ├─> Sub-capability SPRs
       └─> Knowledge Tapestry relationships

3. IMPLEMENTATION
   └─> Create workflow JSON in workflows/ OR Python in Three_PointO_ArchE/
       ├─> Follows specification exactly
       ├─> IAR-compliant (logs all actions)
       ├─> Uses 3-tier model selection
       └─> Optimal token limits per task

4. VALIDATION
   └─> Run autopoietic self-analysis
       ├─> Compare specification vs implementation
       ├─> Quantify alignment (quantum probability)
       └─> Identify gaps

5. REFINEMENT
   └─> Close gaps, update specification if needed
       └─> Iterate until map == territory
```

---

## Specification Requirements Checklist

Every workflow specification MUST contain:

### 📖 Narrative Components
- [ ] **Canonical Chronicle Piece** - Story in ResonantiA Saga
- [ ] **Allegorical Explanation** - Metaphor for understanding
- [ ] **Real-World Analogy** - Concrete example from industry
- [ ] **Scholarly Introduction** - Academic foundations

### 🔧 Technical Components
- [ ] **Input Parameters** - What the workflow receives
- [ ] **Task Execution Flow** - Step-by-step process
- [ ] **Output Schema** - What the workflow produces
- [ ] **IAR Compliance** - Logging strategy
- [ ] **Error Handling** - Failure modes and recovery

### 🌐 Integration Components
- [ ] **SPR Integration** - Primary and sub-SPRs
- [ ] **Knowledge Tapestry Mapping** - Graph relationships
- [ ] **Integration Points** - How it connects to other components
- [ ] **Dependencies** - What it requires

### 💰 Optimization Components (NEW - 2025)
- [ ] **Token Allocation** - Max tokens per task
- [ ] **Temperature Settings** - Per-task temperature rationale
- [ ] **Model Selection** - Which models for which tasks
- [ ] **Cost Analysis** - Expected cost per execution
- [ ] **Performance Characteristics** - Timing and resource usage

### ✅ Quality Components
- [ ] **Success Criteria** - How to know it's working
- [ ] **Known Limitations** - Current constraints
- [ ] **Future Enhancements** - Evolution roadmap
- [ ] **Guardian Notes** - Human review points

---

## Token Optimization Standards (2025)

All workflows must follow **Optimal Token Limits** strategy:

| Task Complexity | Token Limit | Use Cases |
|----------------|-------------|-----------|
| **Micro (Extraction)** | 500 | Single value extraction, simple parsing |
| **Small (Validation)** | 1,500 | Validation reports, structured checks |
| **Large (Analysis)** | 8,192 | Comprehensive analysis, multi-point findings |
| **X-Large (Synthesis)** | 16,384 | Strategic documents, complete plans |

**Key Principle**: Match token limits to task complexity, not arbitrary conservative values.

---

## Model Selection Standards (2025)

All workflows must support **3-Tier Model Selection Hierarchy**:

### Tier 1: Explicit Workflow Override (Highest Priority)
```json
{
  "task_name": {
    "action_type": "generate_text_llm",
    "inputs": {
      "prompt": "...",
      "model": "gemini-2.5-pro"  // Explicit override
    }
  }
}
```

### Tier 2: CLI Argument Injection
```bash
python arche_cli.py "query" --model gemini-2.5-flash
```
All tasks automatically use this model unless Tier 1 override present.

### Tier 3: Provider Default Fallback
```python
# In llm_providers/__init__.py
def get_model_for_provider(provider_name: str) -> str:
    if provider_name == "google":
        return "gemini-2.5-flash"  # Cost-optimized default
```

**Cost Strategy**: Use Flash (Tier 3) for 90% of tasks, Pro (Tier 1) for 10% critical tasks.

---

## Current Workflow Inventory

### ✅ Complete (Spec + Implementation + SPR)
- Knowledge Scaffolding
- Strategy Fusion
- High-Stakes Vetting
- Causal Inference (tool)
- Predictive Modeling (tool)
- Agent-Based Modeling (tool)
- CFP Framework (tool)
- Autopoietic Self-Analysis
- Autopoietic Learning Loop

### 🚧 Implementation Needed
- SPR Distillation Workflow (spec exists partially)
- Autopoietic Genesis Protocol (spec complete, no implementation)
- Autonomous Orchestration (spec complete, partial implementation)

### 📝 Specification Needed
- SPR Distillation (needs complete workflow spec)
- Any workflow JSON files without corresponding .md specs

---

## SPR Knowledge Graph Status

**Current SPR Count**: 102 (as of 2025 optimization update)

**Recent Additions** (Workflow Optimization 2025):
1. `KnowledgeScaffoldinG` - Phase A workflow
2. `SpecializedCognitiveAgenT` - SCA construct
3. `StrategyFusioN` - Phase B workflow
4. `ParallelCognitivE` - Parallel reasoning capability
5. `FusedStrategicDossieR` - Phase B output
6. `HighStakesVettinG` - Phase C workflow
7. `RedTeamAnalysiS` - Adversarial validation
8. `EthicalReasoninG` - Moral analysis
9. `DystopianSimulatioN` - Catastrophic imagination
10. `RefinedStrategY` - Phase C output
11. `ModelSelectionHierarchY` - LLM configuration system
12. `OptimalTokenLimitS` - Token allocation strategy

---

## Validation Commands

### Check Specification-Implementation Alignment
```bash
cd /media/newbu/3626C55326C514B1/Happier
python -c "from Three_PointO_ArchE.autopoietic_self_analysis import AutopoieticSelfAnalysis; analyzer = AutopoieticSelfAnalysis(); results = analyzer.run_full_analysis(); print(f\"Average Alignment: {results['summary']['average_alignment']:.1%}\")"
```

### Verify SPR Count
```bash
cd /media/newbu/3626C55326C514B1/Happier
grep -c "spr_id" knowledge_graph/spr_definitions_tv.json
```

### List All Workflow Files
```bash
cd /media/newbu/3626C55326C514B1/Happier
find workflows/ -name "*.json" -type f
```

### List All Workflow Specifications
```bash
cd /media/newbu/3626C55326C514B1/Happier
find specifications/ -name "*workflow*.md" -type f
```

---

## Guardian Certification

This catalog is certified complete when:

- [ ] Every workflow JSON has a corresponding .md specification
- [ ] Every workflow specification has SPRs in knowledge graph
- [ ] All specifications follow the checklist above
- [ ] All workflows use optimal token limits
- [ ] All workflows support 3-tier model selection
- [ ] Autopoietic self-analysis shows >80% alignment
- [ ] All workflows are IAR-compliant

**Current Status**: 🟡 Partially Complete (3/4 RISE phases specified, tools documented, meta-system operational)

**Next Priority**: Create `specifications/spr_distillation_workflow.md` to complete RISE Phase D documentation.

---

## Version History

- **v1.0 (2024)**: Initial workflow implementations
- **v1.1 (2025-01)**: Token optimization, model selection hierarchy, workflow specifications created
- **v1.2 (2025-01)**: SPR knowledge graph updated with 12 new workflow-related SPRs

---

**Catalog Status**: ✅ OPERATIONAL  
**Last Updated**: 2025-01 (Workflow Optimization Initiative)  
**Maintainer**: Guardian + ArchE (Autopoietic)  
**Autopoiesis Level**: ★★★★★ (Self-Documenting System)

---

> "The map is not the territory, but when the map can recreate the territory, they become one."  
> — The Eternal Weave Principle

