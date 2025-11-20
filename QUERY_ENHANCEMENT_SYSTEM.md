# Universal Query Enhancement System

## Overview

The Universal Query Enhancement System dynamically discovers ArchE's capabilities and generates optimized queries that maximize effectiveness and robustness. It automatically analyzes user queries, identifies required capabilities, and enhances them to leverage the full spectrum of ArchE's v3.5-GP capabilities.

---

## Architecture

### Components

1. **CapabilityDiscoveryEngine** (`Three_PointO_ArchE/query_enhancement_engine.py`)
   - Discovers all available SPRs from `knowledge_graph/spr_definitions_tv.json`
   - Discovers all registered actions from the action registry
   - Discovers all workflows from the `workflows/` directory
   - Discovers available tools and capabilities
   - Creates a comprehensive capability map

2. **QueryAnalyzer**
   - Analyzes user queries to understand intent
   - Assesses query complexity (simple, medium, complex, very_complex)
   - Detects SPRs mentioned in the query
   - Identifies required capabilities
   - Detects temporal scope
   - Determines analysis types needed (causal, predictive, simulation, etc.)

3. **QueryEnhancementEngine**
   - Generates enhanced queries based on analysis
   - Supports three enhancement levels:
     - **Minimal**: Just adds protocol reference
     - **Moderate**: Adds relevant capabilities
     - **Comprehensive**: Full structured query with all phases
   - Auto-determines enhancement level based on complexity

---

## Usage

### Via Dashboard

1. Enter your query in the query input field
2. Click **"✨ Enhance Query"** button
3. Review the enhanced query and analysis
4. Click **"Use This Query"** to replace your original query
5. Submit the enhanced query

### Via API

```python
POST /api/query/enhance
{
    "query": "How can I monetize ArchE?",
    "enhancement_level": "auto"  # or "minimal", "moderate", "comprehensive"
}
```

Response:
```json
{
    "status": "success",
    "result": {
        "original_query": "...",
        "enhanced_query": "...",
        "query_structure": {...},
        "analysis": {
            "intent": "monetization",
            "complexity": "very_complex",
            "required_capabilities": [...],
            "detected_sprs": [...],
            "temporal_scope": "future",
            "analysis_types": ["causal", "predictive", "simulation"],
            "confidence": 0.95
        },
        "enhancement_metadata": {
            "level": "comprehensive",
            "capabilities_used": 12,
            "sprs_activated": 8,
            "improvement_estimate": "High - Query will leverage full ArchE capabilities"
        }
    }
}
```

### Via Python

```python
from Three_PointO_ArchE.query_enhancement_engine import create_enhancement_engine
from pathlib import Path

# Create enhancement engine
engine = create_enhancement_engine(Path("/path/to/project"))

# Enhance a query
result = engine.enhance_query(
    "How can I monetize ArchE and bring it to market?",
    enhancement_level='auto'
)

print(result['enhanced_query'])
```

---

## How It Works

### 1. Capability Discovery

The system automatically discovers:
- **SPRs**: All Sparse Priming Representations from the knowledge graph
- **Actions**: All registered actions from `action_registry.py`
- **Workflows**: All JSON workflow files in `workflows/`
- **Tools**: Known tool patterns (Causal Inference, Predictive Modeling, ABM, CFP, RISE, etc.)

### 2. Query Analysis

For each query, the system:
- Detects SPRs mentioned in the query
- Assesses complexity based on keywords and length
- Determines intent (monetization, analysis, prediction, etc.)
- Detects temporal scope (historical, current, future)
- Identifies required analysis types
- Maps analysis types to capabilities
- Calculates confidence in ability to answer

### 3. Query Enhancement

Based on the analysis, the system generates an enhanced query that:
- References ResonantiA Protocol v3.5-GP
- Explicitly invokes required capabilities
- Structures the query into phases
- Adds IAR (Integrated Action Reflection) requirements
- Includes temporal resonance validation
- Adds pattern crystallization for complex queries
- Ensures implementation resonance

### Enhancement Levels

#### Minimal
- Just adds protocol reference
- Suitable for simple queries

#### Moderate
- Adds relevant capabilities
- Includes IAR requirements
- Suitable for medium complexity queries

#### Comprehensive
- Full structured query with phases
- All required capabilities explicitly invoked
- Complete IAR integration
- Temporal resonance validation
- Pattern crystallization
- Implementation resonance check
- Suitable for complex/very_complex queries

---

## Example

### Original Query
```
How can I monetize ArchE?
```

### Enhanced Query (Comprehensive)
```
Apply the full spectrum of ResonantiA Protocol v3.5-GP (Genesis Protocol) capabilities to achieve deep Temporal Resonance and Cognitive Resonance on this query. Execute a temporally-aware, multi-dimensional analytical sequence that integrates all advanced capabilities while maintaining Implementation Resonance throughout.

PRIMARY OBJECTIVE:

How can I monetize ArchE?

REQUIRED ANALYSIS COMPONENTS:

(1) Use Causal InferencE with CausalLagDetectioN to identify causal relationships and temporal lags.
(2) Apply PredictivE ModelinG TooL with FutureStateAnalysiS to forecast outcomes with confidence intervals.
(3) Execute Agent Based ModelinG with HumanFactorModelinG and EmergenceOverTimE to simulate complex dynamics.
(4) Utilize ComparativE FluxuaL ProcessinG (CFP) with TrajectoryComparisoN to compare alternative scenarios.
(5) Apply ComplexSystemVisioninG to model emergent behaviors and system interactions.
(6) Synthesize all findings through the RISE engine to generate comprehensive, actionable recommendations.
(7) Ensure Temporal resonancE by integrating future context and validating temporal coherence.
(8) Generate comprehensive IAR (Integrated Action Reflection) reflections for each phase, assessing confidence, alignment, and potential issues.
(9) Apply Pattern crystallizatioN to identify and solidify key insights for future use.

FINAL OUTPUT REQUIREMENTS:

- Comprehensive analysis with all phase results
- IAR reflections for each major step
- Temporal coherence validation
- Implementation feasibility assessment
- Crystallized insights and patterns
```

---

## Integration Points

### Dashboard Integration
- **Endpoint**: `/api/query/enhance`
- **UI**: "✨ Enhance Query" button in query interface
- **Display**: Enhanced query container with analysis

### Workflow Integration
- Can be used as a preprocessing step before query submission
- Can be integrated into custom workflows
- Can be used for query optimization in batch processing

---

## Benefits

1. **Automatic Capability Discovery**: No manual maintenance of capability lists
2. **Intelligent Enhancement**: Queries are enhanced based on actual requirements
3. **Maximized Effectiveness**: Ensures all relevant capabilities are leveraged
4. **Robustness**: Adds validation and IAR requirements
5. **Completeness**: Ensures queries are comprehensive and well-structured
6. **Adaptability**: Automatically adjusts enhancement level based on complexity

---

## Future Enhancements

1. **Learning from Past Queries**: Analyze successful queries to improve enhancement
2. **Custom Enhancement Templates**: Allow users to define custom enhancement patterns
3. **Multi-Query Optimization**: Enhance multiple related queries together
4. **Capability Recommendation**: Suggest additional capabilities that might be useful
5. **Query Validation**: Validate enhanced queries before submission
6. **Performance Metrics**: Track improvement in query effectiveness

---

## Technical Details

### File Structure
```
Three_PointO_ArchE/
  └── query_enhancement_engine.py  # Main enhancement engine

arche_dashboard/
  └── backend/
      └── api.py  # API endpoint for enhancement
  └── frontend/
      └── index.html  # UI for query enhancement
```

### Dependencies
- `Three_PointO_ArchE.spr_manager` - For SPR discovery
- `Three_PointO_ArchE.action_registry` - For action discovery
- Standard library: `json`, `logging`, `re`, `pathlib`, `typing`

---

## Status

✅ **Implemented**: Core enhancement engine, capability discovery, query analysis  
✅ **Integrated**: Dashboard API endpoint and UI  
✅ **Tested**: Basic functionality verified  
🔄 **In Progress**: Performance optimization, learning from past queries  
📋 **Planned**: Custom templates, multi-query optimization

---

**Last Updated**: 2025-11-20

