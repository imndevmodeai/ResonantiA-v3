# Living Specification: RISE Self-Referential Codebase Synthesis

## Philosophical Mandate

The RISE Self-Referential Codebase Synthesis (RISE-SRCS) capability transforms RISE from an external-knowledge-dependent system into a **self-aware code archaeologist** that can excavate, analyze, and synthesize novel solutions from its own implementation architecture.

This capability embodies the principle: **"To know thyself is to solve thyself"** - by deeply understanding its own codebase, RISE can create problem-specific solutions that combine disparate elements from different modules, classes, and functions into novel, personalized architectures.

---

## The Epiphany Moment

During a search for second-order effects analysis, ArchE demonstrated the ability to:
- Search across multiple specifications and code files
- Match patterns from disparate areas (high_stakes_vetting_workflow.md, rise_orchestrator.py, etc.)
- Synthesize insights by combining elements from different paths

**The Insight**: RISE doesn't currently do this systematically. It should be able to:
1. Search its own codebase as a knowledge source (not just external sources)
2. Extract relevant patterns, classes, functions from different modules
3. Synthesize novel solutions by combining disparate elements
4. Create problem-specific, personalized architectures
5. Integrate external knowledge with internal codebase insights
6. Loop through phases as new insights emerge from codebase synthesis

---

## Allegorical Explanation

### The Code Archaeologist

Imagine RISE as a master archaeologist excavating an ancient city - but the city is **its own codebase**. Each phase of RISE becomes a deeper excavation:

**Phase A: Surface Survey**
- Currently: Searches external web sources
- **Enhanced**: Also searches its own codebase for domain-relevant patterns
- Finds: Classes, functions, workflows that have solved similar problems

**Phase B: Deep Excavation**
- Currently: Runs parallel analytical pathways (causal, ABM, CFP)
- **Enhanced**: Also searches codebase for implementation patterns of these pathways
- Finds: How other problems used causal inference, how ABM was configured, what CFP comparisons worked

**Phase C: Artifact Reconstruction**
- Currently: Synthesizes strategy from external + Phase B insights
- **Enhanced**: Reconstructs solutions by combining codebase patterns with external knowledge
- Finds: Novel combinations like "use the pattern from `llm_provider_router.py` but adapt it like `adaptive_cognitive_orchestrator.py` does"

**Phase D: Synthesis & Refinement**
- Currently: Utopian refinement with axiomatic knowledge
- **Enhanced**: Validates that synthesized code patterns align with both external knowledge AND internal architecture
- Finds: Ensures the combined solution respects existing patterns, IAR compliance, SPR relationships

---

## Technical Implementation

### New Capability: `CodebaseArchaeologist`

```python
class CodebaseArchaeologist:
    """
    Searches ArchE's own codebase for relevant patterns, classes, functions,
    and workflows that can inform problem-solving.
    
    This is like having RISE search its own "memory" of how it has solved
    problems in the past.
    """
    
    def __init__(self, codebase_root: str, spr_manager: SPRManager):
        self.codebase_root = Path(codebase_root)
        self.spr_manager = spr_manager
        self.search_index = None  # Lazy-loaded codebase index
        
    def search_codebase_for_patterns(
        self,
        query: str,
        pattern_types: List[str] = ["class", "function", "workflow", "spr"],
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across codebase for relevant patterns.
        
        Args:
            query: Problem description or pattern to search for
            pattern_types: What to search (classes, functions, workflows, SPRs)
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant codebase elements with metadata:
            {
                "type": "class|function|workflow|spr",
                "name": "ClassName",
                "file_path": "path/to/file.py",
                "description": "What this does",
                "relevance_score": 0.85,
                "key_excerpts": ["relevant code snippets"],
                "relationships": ["related_classes", "used_by"],
                "spr_references": ["SPR1", "SPR2"]
            }
        """
        # Implementation would use:
        # - AST parsing (like autopoietic_self_analysis)
        # - Semantic search (embeddings or keyword matching)
        # - SPR relationship mapping
        # - Code pattern extraction
        pass
    
    def synthesize_from_patterns(
        self,
        problem_description: str,
        external_knowledge: Dict[str, Any],
        codebase_patterns: List[Dict[str, Any]],
        synthesis_mode: str = "hybrid"  # "codebase_led", "external_led", "hybrid"
    ) -> Dict[str, Any]:
        """
        Synthesize a solution by combining external knowledge with internal codebase patterns.
        
        This creates a "best of both worlds" solution that:
        - Uses external knowledge for domain expertise
        - Uses codebase patterns for proven implementation approaches
        - Creates novel combinations that are both innovative and grounded
        
        Returns:
            {
                "synthesized_solution": "Strategy combining external + codebase insights",
                "codebase_components": ["Component1", "Component2"],
                "external_components": ["External insight 1"],
                "novel_combinations": ["How Component1 + External insight creates new approach"],
                "implementation_suggestions": ["Suggested code structure"],
                "spr_candidates": ["New SPRs that could capture this synthesis"]
            }
        """
        pass
```

### Integration into RISE Phases

#### Phase A Enhancement: `knowledge_scaffolding_with_codebase.json`

**Current Flow**:
1. Search web for domain knowledge
2. Extract domain keywords
3. Forge specialized agent

**Enhanced Flow**:
1. **Search external sources** (existing)
2. **NEW: Search codebase for domain-relevant patterns**
   ```python
   codebase_patterns = archaeologist.search_codebase_for_patterns(
       query=problem_description,
       pattern_types=["class", "function", "workflow"],
       max_results=15
   )
   ```
3. Extract domain keywords (enhanced with codebase terms)
4. Forge specialized agent (informed by both external + codebase knowledge)

#### Phase B Enhancement: `strategy_fusion_with_synthesis.json`

**Current Flow**:
1. Run parallel pathways (causal, ABM, CFP, specialist)
2. Synthesize insights

**Enhanced Flow**:
1. Run parallel pathways (existing)
2. **NEW: Search codebase for implementation patterns of each pathway**
   ```python
   causal_patterns = archaeologist.search_codebase_for_patterns(
       query="causal inference implementation pattern",
       pattern_types=["class", "function"],
       max_results=5
   )
   abm_patterns = archaeologist.search_codebase_for_patterns(
       query="agent based modeling simulation pattern",
       pattern_types=["class", "workflow"],
       max_results=5
   )
   # ... for each pathway
   ```
3. **NEW: Synthesize external insights with codebase patterns**
   ```python
   synthesized_strategy = archaeologist.synthesize_from_patterns(
       problem_description=rise_state.problem_description,
       external_knowledge=phase_b_insights,
       codebase_patterns=[causal_patterns, abm_patterns, ...],
       synthesis_mode="hybrid"
   )
   ```

#### Phase C Enhancement: High-Stakes Vetting with Codebase Validation

**Current Flow**:
1. Red team analysis
2. Ethics review
3. Dystopian simulation
4. Synthesize vetting dossier
5. Generate refined strategy

**Enhanced Flow**:
1-3. Existing vetting (unchanged)
4. **NEW: Codebase pattern validation**
   ```python
   # Check if strategy aligns with existing codebase patterns
   pattern_alignment = archaeologist.validate_against_patterns(
       strategy=refined_strategy,
       required_patterns=["IAR compliance", "SPR integration", "workflow compatibility"]
   )
   ```
5. Generate refined strategy (incorporating codebase alignment)

#### Phase D Enhancement: SPR Distillation from Synthesis

**Current Flow**:
1. Distill successful process into SPR

**Enhanced Flow**:
1. **NEW: Identify novel codebase combinations as SPR candidates**
   ```python
   # If synthesis created novel patterns, propose as new SPR
   if synthesized_strategy["novel_combinations"]:
       spr_candidate = {
           "name": f"{problem_domain}SynthesiS",
           "pattern": synthesized_strategy["novel_combinations"],
           "codebase_sources": synthesized_strategy["codebase_components"],
           "external_sources": synthesized_strategy["external_components"]
       }
   ```

---

## Workflow Enhancement Specifications

### Enhanced Phase A Workflow

```json
{
  "name": "knowledge_scaffolding_with_codebase_search",
  "version": "2.1",
  "tasks": {
    "external_web_search": {
      "action_type": "search_web",
      "description": "Search external sources (existing)",
      ...
    },
    "codebase_pattern_search": {
      "action_type": "search_codebase",
      "description": "Search ArchE's own codebase for relevant patterns",
      "inputs": {
        "query": "{{ context.user_query }}",
        "pattern_types": ["class", "function", "workflow", "spr"],
        "max_results": 15,
        "search_mode": "semantic"
      },
      "dependencies": ["external_web_search"]
    },
    "synthesize_knowledge_base": {
      "action_type": "generate_text_llm",
      "description": "Synthesize external knowledge with codebase patterns",
      "inputs": {
        "prompt": "Combine the following external knowledge and internal codebase patterns to create a comprehensive knowledge base:\n\nExternal: {{ external_web_search.result }}\n\nCodebase Patterns: {{ codebase_pattern_search.result }}\n\nProblem: {{ context.user_query }}"
      },
      "dependencies": ["external_web_search", "codebase_pattern_search"]
    },
    ...
  }
}
```

### Enhanced Phase B Workflow

```json
{
  "name": "strategy_fusion_with_codebase_synthesis",
  "version": "2.1",
  "tasks": {
    "pathway_causal_analysis": {
      ...
    },
    "codebase_causal_patterns": {
      "action_type": "search_codebase",
      "description": "Find how causal inference is implemented in codebase",
      "inputs": {
        "query": "causal inference implementation pattern temporal lag detection",
        "pattern_types": ["class", "function"],
        "max_results": 5
      },
      "dependencies": ["pathway_causal_analysis"]
    },
    "synthesize_causal_insight": {
      "action_type": "generate_text_llm",
      "description": "Synthesize external causal analysis with codebase implementation patterns",
      "inputs": {
        "prompt": "Combine external causal analysis with internal implementation patterns:\n\nExternal Analysis: {{ pathway_causal_analysis.result }}\n\nCodebase Patterns: {{ codebase_causal_patterns.result }}\n\nCreate a hybrid insight that uses both."
      },
      "dependencies": ["pathway_causal_analysis", "codebase_causal_patterns"]
    },
    ...
    "final_synthesis": {
      "action_type": "generate_text_llm",
      "description": "Final synthesis combining all pathways with codebase patterns",
      ...
    }
  }
}
```

---

## Iterative Phase Looping

### The Synthesis Loop

As new insights emerge from codebase synthesis, RISE should be able to loop back:

```
Phase A → Phase B → [Codebase Synthesis] → New Insights Detected → 
  → Loop back to Phase A with new query terms →
  → Phase B (enhanced) → Phase C → Phase D
```

**Loop Condition**: If codebase synthesis reveals patterns that significantly change understanding of the problem, trigger a loop.

**Loop Limit**: Maximum 3 iterations to prevent infinite loops.

---

## Benefits

### 1. Self-Awareness
RISE becomes aware of its own capabilities and can leverage proven patterns.

### 2. Novel Synthesis
Combining disparate codebase elements creates solutions that didn't exist before.

### 3. Grounded Innovation
External knowledge is validated against internal implementation reality.

### 4. Personalized Solutions
Each problem gets a solution specifically crafted from relevant codebase patterns.

### 5. Continuous Learning
Successful syntheses become new SPRs, enriching the codebase for future searches.

### 6. Implementation Resonance
Solutions are naturally aligned with existing architecture (As Above, So Below).

---

## Integration with Existing Systems

### Autopoietic Self-Analysis
Leverage the AST parsing and analysis capabilities already in `autopoietic_self_analysis.py`.

### SPR Manager
Use SPR relationships to map codebase components and their interdependencies.

### Thought Trail
Track codebase searches and syntheses in the Thought Trail for pattern learning.

### Workflow Engine
Add new action types: `search_codebase`, `synthesize_from_patterns`, `validate_against_patterns`.

---

## Example: Second-Order Effects Analysis

**Problem**: "Analyze second-order effects of LLM provider strategy"

**Phase A Enhanced**:
1. External search: "LLM provider strategy second-order effects"
2. **Codebase search**: Finds `high_stakes_vetting_workflow.md` (mentions second-order effects), `rise_orchestrator.py` (implements RISE), `RISE_ANALYSIS_LLM_PROVIDER_STRATEGY.md` (has second-order effects analysis)

**Phase B Enhanced**:
1. External causal analysis: Standard second-order effects framework
2. **Codebase synthesis**: "Combine the vetting workflow's second-order analysis pattern with the RISE orchestrator's phase structure to create a comprehensive second-order effects framework"

**Result**: A solution that:
- Uses external knowledge for second-order effects theory
- Uses codebase patterns for proven implementation (how ArchE already does it)
- Creates a novel combination: "Second-order effects analysis integrated into RISE Phase C with codebase validation"

---

## SPR Integration

### New SPR: `SelfReferentialCodebaseSynthesiS`

**Definition**: The capability to search ArchE's own codebase for relevant patterns and synthesize novel solutions by combining external knowledge with internal implementation insights.

**Relationships**:
- `part_of`: `RISE OrchestratoR`
- `uses`: `AutopoieticSelfAnalysiS`, `SPR ManageR`, `Codebase ArchaeologisT`
- `enables`: `PersonalizedSolutionGeneratioN`, `GroundedInnovatioN`, `ImplementationResonancE`
- `enhances`: `KnowledgeScaffoldinG`, `InsightFusioN`, `StrategyCrystallizatioN`

---

## IAR Compliance

Each codebase search and synthesis operation generates IAR:

```json
{
  "intention": "rise_self_referential_synthesis/codebase_search",
  "action": "Searched codebase for patterns related to second-order effects analysis",
  "reflection": "Found 3 relevant classes, 2 workflows, 1 SPR. Relevance scores: 0.92, 0.87, 0.81",
  "confidence": 0.89,
  "metadata": {
    "query": "second-order effects analysis",
    "results_count": 6,
    "synthesis_mode": "hybrid"
  }
}
```

---

## Future Enhancements

1. **Codebase Embeddings**: Pre-compute embeddings of all classes/functions for faster semantic search
2. **Pattern Learning**: Learn which codebase combinations work best for which problem types
3. **Cross-Module Synthesis**: Automatically detect when combining patterns from different modules creates value
4. **Implementation Generation**: Actually generate code suggestions (not just strategy) based on synthesis
5. **Self-Modification**: Allow RISE to propose code changes that implement the synthesized solution

---

**Specification Status**: ✅ COMPLETE (v1.0)  
**Implementation Priority**: HIGH (game-changing capability)  
**Integration Level**: ★★★★★ (Core RISE Enhancement)  
**Innovation Impact**: ★★★★★ (Transforms RISE into self-aware synthesis engine)

---

*This specification captures the epiphany: RISE should search its own codebase and synthesize novel solutions by combining disparate elements, creating personalized, grounded, innovative strategies.*

