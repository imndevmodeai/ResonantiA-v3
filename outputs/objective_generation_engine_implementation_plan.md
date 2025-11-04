# Objective Generation Engine: Implementation Plan

**Status**: Ready for Implementation  
**Priority**: High (Core Cognitive Engine)  
**Dependencies**: Universal Abstraction patterns established

---

## Phase 1: Core Infrastructure (Week 1)

### 1.1 Create Feature Extraction Module

**File**: `Three_PointO_ArchE/objective_generation_engine.py`

**Classes to Implement**:
```python
class FeatureVector:
    """Structured representation of query features."""
    temporal_markers: List[TemporalMarker]
    domain_keywords: List[str]
    entities: List[str]
    complexity_indicators: List[str]
    spr_keywords: List[str]
    raw_query: str

class TemporalMarker:
    """Extracted temporal information."""
    type: str  # 'explicit_range', 'age_range', 'future_horizon'
    value: Tuple
    confidence: QuantumProbability

class ObjectiveGenerationEngine:  # Note: Class name uses PascalCase, SPR ID uses Guardian pointS format
    """Main engine class."""
    def extract_features(self, query: str) -> FeatureVector
    def build_temporal_scope(self, features: FeatureVector) -> TemporalScope
    def activate_sprs(self, features: FeatureVector) -> List[ActivatedSPR]
    def select_mandates(self, features: FeatureVector, spr: List[ActivatedSPR]) -> List[Mandate]
    def assemble_objective(self, spr: List[ActivatedSPR], mandates: List[Mandate], features: FeatureVector) -> str
    def assemble_problem_description(self, original_query: str, temporal_scope: TemporalScope, objective: str, activated_sprs: List[ActivatedSPR]) -> str
```

### 1.2 Pattern Matching Infrastructure

**Regex Patterns for Temporal Extraction**:
```python
TEMPORAL_PATTERNS = [
    (r'circa\s+(\d{4})-(\d{4})', 'explicit_range'),
    (r'age\s+(\d+)-(\d+)', 'age_range'),
    (r'(\d+)\s+year[s]?\s+(?:ahead|forward|projection)', 'future_horizon'),
    (r'in\s+(\d+)\s+year[s]?', 'future_point'),
    # ... more patterns
]

DOMAIN_KEYWORD_MAP = {
    'boxing': ['boxing match', 'fight', 'boxer', 'round'],
    'economic': ['economic', 'market', 'financial', 'investment'],
    'scientific': ['experiment', 'hypothesis', 'validation', 'research'],
    # ... more domains
}
```

### 1.3 SPR Keyword Lookup Table

**File**: `Three_PointO_ArchE/objective_generation_engine.py` (as module-level constant)

```python
SPR_KEYWORD_MAP = {
    'historical': 'HistoricalContextualizatioN',
    'emergent': 'EmergenceOverTimE',
    'causal': 'CausalLagDetectioN',
    'predictive': 'FutureStateAnalysiS',
    'predicting': 'FutureStateAnalysiS',
    'temporal': 'TemporalDynamiX',
    'trajectory': 'TrajectoryComparisoN',
    'compare': 'TrajectoryComparisoN',
    'matchup': 'TrajectoryComparisoN',
    # ... comprehensive mapping
}
```

---

## Phase 2: Mandate Selection Rules (Week 1)

### 2.1 Rule-Based Mandate Selector

```python
class MandateSelector:
    """Rule-based mandate selection (no LLM)."""
    
    TEMPORAL_INDICATORS = ['circa', 'age', 'year', 'time horizon', 'trajectory', 'prime']
    COMPLEXITY_KEYWORDS = ['emergent', 'complex system', 'interaction', 'dynamic', 'simulation']
    
    def select_mandates(self, features: FeatureVector, activated_sprs: List[ActivatedSPR]) -> List[Mandate]:
        """Apply deterministic rules."""
        mandates = []
        
        # Rule 1: Temporal → Mandate 6
        if any(ind in features.raw_query.lower() for ind in self.TEMPORAL_INDICATORS):
            mandates.append(Mandate(6, "Temporal Resonance", ...))
        
        # Rule 2: Complex → Mandate 9
        if any(kw in features.raw_query.lower() for kw in self.COMPLEXITY_KEYWORDS):
            mandates.append(Mandate(9, "Complex System Visioning", ...))
        
        # Rule 3: Always include Cognitive Resonance
        mandates.append(Mandate(None, "Cognitive Resonance", ...))
        
        return mandates
```

---

## Phase 3: Template Assembly (Week 2)

### 3.1 Template Loader

**File**: `protocol/templates/enhancement_skeleton_pattern.txt`

```python
ENHANCEMENT_SKELETON_TEMPLATE = """
->|EnhancementDirectives|<-
    ->|Objective|<-
        {protocol_version} capabilities to achieve deep Temporal Resonance 
        and Cognitive Resonance on {query_description}. Execute a temporally-aware, 
        multi-dimensional analytical sequence that integrates: {capabilities}. 
        This analysis must honor {mandates} while maintaining Implementation 
        Resonance throughout.
    ->|/Objective|<-
->|/EnhancementDirectives|<-
"""
```

### 3.2 Domain Rule Lookup Tables

```python
DOMAIN_EXPLANATION_RULES = {
    'boxing': {
        'TemporalDynamiX': 'how the fight evolves round-by-round',
        'EmergenceOverTimE': 'ABM showing how agent interactions create unpredictable outcomes',
    },
    'economic': {
        'FutureStateAnalysiS': 'predicting outcomes across time horizons',
        'TemporalDynamiX': '5-year economic projections',
    },
    # ... more domains
}
```

### 3.3 Assembly Logic

```python
def assemble_objective(
    activated_sprs: List[ActivatedSPR],
    mandates: List[Mandate],
    features: FeatureVector,
    template: str
) -> str:
    """Assemble objective via string substitution."""
    # Build capability list
    capability_list = []
    for spr in activated_sprs:
        explanation = generate_domain_explanation(spr, features)
        capability_list.append(f"{spr.spr_id} ({explanation})")
    
    capabilities_text = ", ".join(capability_list)
    
    # Build mandate references
    mandate_refs = [f"Mandate {m.number} ({m.name})" for m in mandates if m.number]
    mandates_text = " and ".join(mandate_refs)
    
    # Template substitution
    return template.format(
        protocol_version="v3.5-GP (Genesis Protocol)",
        capabilities=capabilities_text,
        mandates=mandates_text,
        query_description=features.domain_description
    )
```

---

## Phase 4: Integration with RISE Orchestrator (Week 2)

### 4.1 Modify RISE_Orchestrator.process_query()

**File**: `Three_PointO_ArchE/rise_orchestrator.py`

```python
def process_query(self, problem_description: str, ...):
    # ... existing code ...
    
    # NEW: Objective Generation (if not already enriched)
    if not self._is_enriched_problem_description(problem_description):
        engine = ObjectiveGenerationEngine(
            spr_manager=self.spr_manager,
            template_path="protocol/templates/enhancement_skeleton_pattern.txt"
        )
        problem_description = engine.generate_enriched_problem_description(problem_description)
    
    # Continue with existing workflow execution
    # ...
```

### 4.2 Integration Points

- **Before**: Knowledge Scaffolding workflow receives raw query
- **After**: Knowledge Scaffolding workflow receives enriched problem_description with Objective

---

## Phase 5: Testing & Validation (Week 3)

### 5.1 Deterministic Output Tests

```python
def test_deterministic_output():
    """Same query → same objective."""
    query = "Who would win in a boxing match between Mike Tyson (circa 1986-1988) and George Foreman (circa 1973-1974)?"
    
    engine = ObjectiveGenerationEngine()
    objective_1 = engine.generate_enriched_problem_description(query)
    objective_2 = engine.generate_enriched_problem_description(query)
    
    assert objective_1 == objective_2, "Output must be deterministic"
```

### 5.2 SPR Match Accuracy Tests

```python
def test_spr_matching():
    """Verify keyword → SPR matching."""
    query = "Analyze the emergent dynamics of complex systems"
    
    engine = ObjectiveGenerationEngine()
    features = engine.extract_features(query)
    activated_sprs = engine.activate_sprs(features, spr_definitions)
    
    assert 'EmergenceOverTimE' in [spr.spr_id for spr in activated_sprs]
    assert 'ComplexsystemvisioninG' in [spr.spr_id for spr in activated_sprs]
```

### 5.3 Template Compliance Tests

```python
def test_template_compliance():
    """Verify generated objective matches Enhancement_Skeleton_Pattern."""
    # ... test implementation
```

---

## Phase 6: SPR Integration (Week 3)

### 6.1 Add SPR to Knowledge Tapestry

**Script**: `scripts/add_objective_generation_engine_spr.py`

```python
from Three_PointO_ArchE.spr_manager import SPRManager

spr_manager = SPRManager('knowledge_graph/spr_definitions_tv.json')

spr_definition = {
        "spr_id": "Objective generation enginE",
    "term": "Objective Generation Engine",
    # ... full definition from outputs/objective_generation_engine_spr.json
}

spr_manager.add_spr(spr_definition, overwrite_if_exists=False)
```

### 6.2 Update Related SPRs

- Update `Enhancement Skeleton PatterN` SPR to reference Objective generation enginE
- Update `SIRC ProtocoL` SPR to include Objective generation enginE in its components
- Update `RISE OrchestratoR` SPR to reference Objective generation enginE integration

---

## Phase 7: Documentation & ThoughtTrail Integration (Week 4)

### 7.1 IAR Generation

```python
def generate_objective_iar(
    objective: str,
    activated_sprs: List[ActivatedSPR],
    mandates: List[Mandate],
    confidence: float
) -> Dict[str, Any]:
    """Generate IAR for objective generation."""
    return {
        "status": "completed",
        "summary": f"Objective assembled with {len(activated_sprs)} SPRs and {len(mandates)} mandates",
        "confidence": QuantumProbability(confidence, evidence=[
            f"sprs_activated: {len(activated_sprs)}",
            f"mandates_selected: {len(mandates)}",
            "deterministic_assembly",
            "no_llm_dependencies"
        ]),
        "alignment_check": {
            "objective_alignment": 1.0,
            "protocol_alignment": 1.0
        },
        "raw_output_preview": objective[:200] + "..."
    }
```

### 7.2 ThoughtTrail Logging

```python
@log_to_thought_trail
def generate_enriched_problem_description(self, query: str) -> str:
    """Generate with automatic ThoughtTrail logging."""
    # ... implementation
```

---

## Success Criteria

1. ✅ **Deterministic**: Same query → same objective (100% repeatability)
2. ✅ **LLM-Independent**: No LLM calls in core generation path
3. ✅ **Template Compliant**: All objectives match Enhancement_Skeleton_Pattern structure
4. ✅ **SPR Accuracy**: Keyword matching activates correct SPRs (≥90% accuracy)
5. ✅ **Mandate Alignment**: Temporal queries → Mandate 6, Complex → Mandate 9
6. ✅ **Quantum States**: All confidence scores use QuantumProbability with evidence
7. ✅ **Integration**: Seamlessly integrated with RISE_Orchestrator
8. ✅ **ThoughtTrail**: All operations logged with IAR

---

## Implementation Priority

**Critical Path**:
1. Feature Extraction Module (Phase 1.1)
2. SPR Keyword Lookup (Phase 1.3)
3. Template Assembly (Phase 3)
4. RISE Integration (Phase 4)

**Can Be Parallelized**:
- Mandate Selection Rules (Phase 2)
- Domain Rule Tables (Phase 3.2)
- Testing Framework (Phase 5)

---

**Ready for Implementation**: The specification provides complete blueprints. Implementation can begin immediately with Phase 1.

