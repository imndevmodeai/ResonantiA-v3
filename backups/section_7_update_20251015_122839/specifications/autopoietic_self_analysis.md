# Autopoietic Self-Analysis System

**SPR Key**: `autopoietic_self_analysis`  
**Category**: Self-Awareness & Insight Solidification  
**Status**: Implemented & Operational  
**Parent Principle**: Universal Abstraction

## Purpose

The Autopoietic Self-Analysis System is ArchE's "Mirror of Truth" - the capability to compare specifications (Map) against implementations (Territory) and quantify alignment using quantum probability states.

This system embodies the principle: **"The system that can see itself can improve itself."**

## Core Capabilities

### 1. Map-Territory Comparison

**Map (Above)**: Living Specifications in `specifications/*.md`
- Define ideal system structure
- Specify required classes and functions
- Describe intended capabilities

**Territory (Below)**: Implementation files in `Three_PointO_ArchE/*.py`
- Actual code structure
- Implemented classes and functions
- Real capabilities

**The Gap**: Quantified difference between specification and reality

### 2. Quantum Gap Measurement

Instead of binary "implemented/not implemented", gaps are measured as quantum probability states:

```python
ComponentGap(
    component_name="spr_manager",
    gap_type="partial",  # complete, partial, missing, misaligned
    confidence_score=0.73,  # Classical alignment score
    quantum_confidence={
        "alignment_probability": 0.73,
        "iar_compliance": {
            "probability": 0.5,
            "evidence": ["imports_detected", "no_decorators_found"],
            "quantum_state": "|ψ⟩ = 0.707|1⟩ + 0.707|0⟩",
            "uncertainty": 1.0  # Maximum uncertainty
        },
        "spr_integration": {
            "probability": 1.0,
            "evidence": ["direct_observation", "SPRManager_class_found"],
            "quantum_state": "|ψ⟩ = 1.000|1⟩ + 0.000|0⟩",
            "uncertainty": 0.0  # Certain
        }
    }
)
```

### 3. Evidence-Tracked Analysis

Every quantum probability includes evidence:
- **Direct observation**: "class_found", "import_detected"
- **Inference**: "pattern_suggests", "naming_indicates"
- **Uncertainty**: "parse_error", "insufficient_data"

### 4. Comprehensive Reporting

Generates multiple output formats:
- **Human-readable**: Text reports with gap descriptions
- **Machine-readable**: JSON with full quantum states
- **IAR log**: Complete audit trail of analysis

## Architecture

### Key Classes

#### QuantumProbability

```python
class QuantumProbability:
    """Quantum state representation of uncertain values."""
    
    def __init__(self, probability: float, evidence: List[str])
    
    def collapse(self) -> bool
    def to_dict(self) -> Dict[str, Any]
    
    @staticmethod
    def certain_true() -> 'QuantumProbability'
    
    @staticmethod
    def certain_false() -> 'QuantumProbability'
    
    @staticmethod  
    def uncertain(probability: float, evidence: List[str]) -> 'QuantumProbability'
```

**Key Attributes**:
- `probability`: Float [0.0, 1.0] representing quantum amplitude
- `evidence`: List of reasons for this probability
- `collapsed`: Whether state has been measured
- `uncertainty`: Quantified uncertainty (1.0 = maximum)

**Quantum State Representation**:
```
|ψ⟩ = √p|1⟩ + √(1-p)|0⟩
```

#### ComponentGap

```python
@dataclass
class ComponentGap:
    """Represents a gap between specification and implementation."""
    
    component_name: str
    gap_type: str  # "missing", "partial", "misaligned", "complete"
    specification_path: str
    implementation_path: Optional[str]
    gap_description: str
    confidence_score: float  # Classical score [0.0, 1.0]
    quantum_confidence: Dict[str, Any]  # Quantum probability states
    severity: str  # "critical", "high", "medium", "low"
    recommended_action: str
    evidence: Dict[str, Any]
```

#### AutopoieticSelfAnalysis

```python
class AutopoieticSelfAnalysis:
    """Main analysis engine for Map vs Territory comparison."""
    
    def __init__(self, project_root: Path = None)
    
    def discover_specifications(self) -> List[Path]
    def discover_implementations(self) -> List[Path]
    
    def parse_specification(self, spec_path: Path) -> Dict[str, Any]
    def analyze_implementation(self, impl_path: Path) -> Dict[str, Any]
    
    def compare_component(
        self, 
        component_name: str,
        spec_path: Path,
        impl_path: Path
    ) -> ComponentGap
    
    def run_full_analysis(self) -> Dict[str, Any]
    
    def generate_report(self, gaps: List[ComponentGap]) -> str
    def export_json(self, analysis_results: Dict[str, Any]) -> Path
```

## Analysis Flow

### Phase 1: Discovery

```
specifications/ directory
  ├── Scan for *.md files
  ├── Extract component names
  └── Build specification index

Three_PointO_ArchE/ directory  
  ├── Scan for *.py files
  ├── Parse AST for classes/functions
  └── Build implementation index
```

### Phase 2: Specification Parsing

For each specification:
1. Extract required classes (look for "Class:" or class names)
2. Extract required functions
3. Extract described capabilities
4. Build requirement structure

### Phase 3: Implementation Analysis

For each implementation:
1. Parse Python AST
2. Extract classes and their methods
3. Extract top-level functions
4. Extract imports
5. Analyze IAR compliance (quantum probability)
6. Analyze SPR references (quantum probability)

### Phase 4: Comparison

For each (specification, implementation) pair:
1. Match classes: `required ∩ implemented`
2. Match functions: `required ∩ implemented`
3. Calculate missing: `required - implemented`
4. Compute alignment score: `|matched| / |required|`
5. Generate quantum confidence states
6. Determine severity based on gaps
7. Create ComponentGap object

### Phase 5: Reporting

Generate outputs:
1. Text report: Human-readable gap summary
2. JSON export: Full quantum-enhanced data
3. IAR log: Audit trail entries
4. Console output: Real-time progress

## Quantum Probability Enhancement

### Why Quantum States?

**Problem with classical approaches**:
```python
has_iar_compliance = None  # Unknown - zero information
```

**Solution with quantum states**:
```python
has_iar_compliance = QuantumProbability(
    0.3,  # 30% confidence
    evidence=["parse_error", "exception: TypeError"]
)
# quantum_state: |ψ⟩ = 0.548|1⟩ + 0.837|0⟩
# uncertainty: 0.6
```

**Benefits**:
- Quantified uncertainty vs unknowable uncertainty
- Evidence tracking explains the probability
- Gradual refinement possible (0.3 → 0.5 → 0.8 → 1.0)
- Enables probabilistic decision-making
- Measurable improvement tracking

### Quantum Probability Heuristics

#### For IAR Compliance:

```python
probability = 0.0
evidence = []

if "iar" in imports:
    probability += 0.5
    evidence.append("iar_imports_detected")

if "thought_trail" in imports:
    probability += 0.3
    evidence.append("thought_trail_integration")

if "reflection" in method_names:
    probability += 0.2
    evidence.append("reflection_methods_found")

return QuantumProbability(min(1.0, probability), evidence)
```

#### For Parse Failures:

```python
# When we can't parse the file
return QuantumProbability.uncertain(
    0.3,  # Slight bias toward "not having it"
    evidence=["parse_error", f"exception: {type(e).__name__}"]
)
```

The 0.3 probability reflects: "We couldn't parse, so probably the feature isn't there, but we can't be certain."

## IAR Compliance

Every analysis action is logged:

```python
self.log_iar_entry(
    intention="analysis/full_scan_initiated",
    action="Scanning all specifications and implementations",
    reflection=f"Found {len(specs)} specifications, {len(impls)} implementations",
    confidence=1.0
)
```

IAR log stored in: `logs/autopoietic_transformation_iar.jsonl`

## Usage Examples

### Basic Analysis

```python
from Three_PointO_ArchE.autopoietic_self_analysis import AutopoieticSelfAnalysis

# Initialize analyzer
analyzer = AutopoieticSelfAnalysis()

# Run full analysis
results = analyzer.run_full_analysis()

# Results include:
# - gaps: List[ComponentGap]
# - summary: Dict with counts and metrics
# - quantum_enhanced: True
```

### Analyze Single Component

```python
gap = analyzer.compare_component(
    component_name="cognitive_resonant_controller",
    spec_path=Path("specifications/crcs.md"),
    impl_path=Path("Three_PointO_ArchE/cognitive_resonant_controller.py")
)

print(f"Alignment: {gap.confidence_score:.1%}")
print(f"IAR Compliance: {gap.quantum_confidence['iar_compliance']['probability']:.1%}")
print(f"Severity: {gap.severity}")
```

### Access Quantum States

```python
quantum_state = gap.quantum_confidence['iar_compliance']
print(f"Probability: {quantum_state['probability']}")
print(f"Evidence: {quantum_state['evidence']}")
print(f"Quantum notation: {quantum_state['quantum_state']}")
print(f"Uncertainty: {quantum_state['uncertainty']}")
```

## Output Files

### Analysis Report (Text)

Location: `logs/self_analysis/analysis_report_YYYYMMDD_HHMMSS.txt`

Format:
```
================================================================================
AUTOPOIETIC SELF-ANALYSIS REPORT
Map vs Territory Comparison
================================================================================

SUMMARY STATISTICS
--------------------------------------------------------------------------------
Total Components Analyzed: 155
Complete Implementations: 25
Partial Implementations: 0
Missing Implementations: 9
Misaligned Implementations: 20

CRITICAL GAPS (Requires Immediate Attention)
--------------------------------------------------------------------------------
[List of critical gaps with descriptions]

HIGH PRIORITY GAPS
--------------------------------------------------------------------------------
[List of high priority gaps]
```

### Analysis Data (JSON)

Location: `logs/self_analysis/analysis_data_YYYYMMDD_HHMMSS.json`

Format:
```json
{
  "summary": {
    "total_components_analyzed": 155,
    "average_alignment": 0.5452,
    "timestamp": "2025-10-10T07:25:19.046525"
  },
  "gaps": [
    {
      "component_name": "spr_manager",
      "gap_type": "partial",
      "quantum_confidence": {
        "alignment_probability": 0.73,
        "iar_compliance": {
          "probability": 0.5,
          "quantum_state": "|ψ⟩ = 0.707|1⟩ + 0.707|0⟩",
          "evidence": ["imports_detected", "no_decorators"],
          "uncertainty": 1.0
        }
      }
    }
  ]
}
```

### IAR Log (JSONL)

Location: `logs/autopoietic_transformation_iar.jsonl`

Format: One JSON object per line
```json
{"timestamp": "2025-10-10T07:25:17.706", "intention": "initialization/system_startup", "action": "Self-analysis system ready", "reflection": "Ready to compare map and territory", "confidence": 1.0}
{"timestamp": "2025-10-10T07:25:17.706", "intention": "analysis/full_scan_initiated", "action": "Scanning all specifications and implementations", "reflection": "Found 54 specs, 146 implementations", "confidence": 1.0}
```

## Integration Points

### With Autopoietic Learning Loop

Self-analysis results feed into the learning loop:
1. Detected gaps → patterns (Nebulae)
2. Recurring gap types → wisdom proposals (Ignition)
3. Approved fixes → knowledge crystallization (Galaxies)

### With System Health Monitor

Gap metrics tracked as health indicators:
- Average alignment score
- Critical gap count
- Alignment trend over time

### With Cognitive Integration Hub

Analysis informs cognitive routing:
- Low alignment → RISE prioritization
- High alignment → CRCS confidence boost

## Success Criteria

Analysis system is working correctly when:

1. ✅ Discovers all specifications and implementations
2. ✅ Parses specifications without errors
3. ✅ Analyzes implementations with AST parsing
4. ✅ Generates quantum probabilities (not None/null)
5. ✅ Includes evidence in all probabilities
6. ✅ Handles parse failures gracefully
7. ✅ Produces readable reports
8. ✅ Exports machine-readable JSON
9. ✅ Logs all actions to IAR
10. ✅ Can analyze itself (self-application)

## Performance Characteristics

- **Specification scan**: ~10ms for 54 files
- **Implementation scan**: ~50ms for 146 files
- **Single component analysis**: ~1-5ms
- **Full analysis**: ~0.5-2 seconds
- **Report generation**: ~50ms
- **JSON export**: ~100ms

## Known Limitations

1. **Specification Parsing**: Basic regex-based, may miss complex structures
2. **AST Parsing**: Fails on syntax errors (handled with quantum uncertainty)
3. **Heuristic-Based**: IAR/SPR detection uses patterns, not semantic analysis
4. **Manual Mapping**: Spec names must match implementation filenames

## Future Enhancements

1. **Semantic Analysis**: Use LLM to understand specifications deeply
2. **Auto-Healing**: Propose code changes to close gaps
3. **Continuous Monitoring**: Watch for spec/impl changes
4. **Diff Analysis**: Compare current vs previous scans
5. **Visualization**: Gap dashboards and alignment graphs

## Guardian Notes

**Review Points**:
1. Are quantum probabilities being used appropriately?
2. Is evidence meaningful (not just ["computed"])?
3. Are severity classifications reasonable?
4. Can the system analyze itself without infinite loops?
5. Are recommendations actionable?

---

**Specification Status**: ✅ IMPLEMENTED  
**Implementation**: `Three_PointO_ArchE/autopoietic_self_analysis.py`  
**Version**: 1.0  
**Self-Analysis Result**: Confidence 1.0 (Self-documenting specification)

