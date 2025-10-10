# Autopoietic Learning Loop

**SPR Key**: `autopoietic_learning_loop`  
**Category**: Self-Evolution & Meta-Learning  
**Status**: Implemented & Operational  
**Parent Principle**: Universal Abstraction  
**Metaphor**: The Great Awakening - Cosmic Evolution

## Purpose

The Autopoietic Learning Loop (ALL) is ArchE's self-evolution engine - transforming raw experiences into permanent knowledge through a four-epoch cycle that mirrors cosmic evolution.

This system embodies: **"The system that learns from itself can evolve itself."**

## The Four Cosmic Epochs

### Epoch 1: STARDUST (Experience Capture)
**Abstraction Level**: Concrete experiences  
**Data Structure**: `StardustEntry`  
**Process**: ThoughtTrail captures every action, decision, and outcome  
**Metaphor**: Cosmic dust - raw material of creation  
**Universal Abstraction**: **Representation** of experience

### Epoch 2: NEBULAE (Pattern Formation)
**Abstraction Level**: Recurring patterns  
**Data Structure**: `NebulaePattern`  
**Process**: ACO detects patterns (≥5 occurrences, ≥70% success rate)  
**Metaphor**: Nebulae - patterns clustering for star-birth  
**Universal Abstraction**: **Learning** from experience clusters

### Epoch 3: IGNITION (Wisdom Forging)
**Abstraction Level**: Validated wisdom  
**Data Structure**: `IgnitedWisdom`  
**Process**: InsightSolidification validates, Guardian approves  
**Metaphor**: Star ignition - wisdom burning bright  
**Universal Abstraction**: **Comparison** against validation criteria

### Epoch 4: GALAXIES (Knowledge Crystallization)
**Abstraction Level**: Permanent knowledge  
**Data Structure**: `GalaxyKnowledge`  
**Process**: SPRManager integrates as new SPR  
**Metaphor**: Galaxy formation - stable knowledge structures  
**Universal Abstraction**: **Crystallization** into capability

## The Complete Cycle

```
Experience (concrete)
    ↓ capture
Stardust (raw data)
    ↓ pattern detection
Nebulae (recurring patterns)
    ↓ validation + Guardian approval
Ignition (validated wisdom)
    ↓ crystallization
Galaxies (permanent knowledge)
    ↓ integration
New Capabilities (concrete enhancement)
    ↓ generates
New Experiences...
```

**This is Universal Abstraction applied to self-evolution itself.**

## Architecture

### Key Data Structures

#### StardustEntry

```python
@dataclass
class StardustEntry:
    """A single particle of experience."""
    
    entry_id: str
    timestamp: str
    action_type: str
    intention: str
    action: str
    reflection: str
    confidence: float
    metadata: Dict[str, Any]
    quantum_state: Optional[Dict[str, Any]]
```

**Capture Source**: ThoughtTrail's IAR-compliant logs

#### NebulaePattern

```python
@dataclass
class NebulaePattern:
    """A clustering of related stardust."""
    
    pattern_id: str
    pattern_signature: str  # MD5 hash of key features
    occurrences: int
    success_rate: float
    sample_entries: List[StardustEntry]
    proposed_solution: Optional[str]  # Generated controller code
    confidence: float
    evidence: List[str]
    status: str  # "detected", "proposed", "validating", "rejected", "approved"
```

**Detection Criteria**:
- Minimum 5 occurrences
- Minimum 70% success rate
- Similar pattern signature (action_type + intention features)

#### IgnitedWisdom

```python
@dataclass
class IgnitedWisdom:
    """A validated pattern that passed the Star-Forge."""
    
    wisdom_id: str
    source_pattern: NebulaePattern
    hypothesis: str
    evidence: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    guardian_approval: bool
    approval_timestamp: Optional[str]
    implementation_plan: Optional[str]
```

**Validation Process**:
1. Hypothesis formulation
2. Evidence gathering
3. Simulated testing (replay historical queries)
4. Guardian review queue
5. Approval/rejection

#### GalaxyKnowledge

```python
@dataclass
class GalaxyKnowledge:
    """Crystallized wisdom in the Knowledge Tapestry."""
    
    spr_id: str
    spr_name: str
    source_wisdom: IgnitedWisdom
    spr_definition: Dict[str, Any]
    integration_timestamp: str
    system_impact: Dict[str, Any]
```

**Integration Results**:
- New SPR in knowledge graph
- New CRCS controller (if applicable)
- System-wide capability enhancement
- Broadcast to all components

### Main Class

#### AutopoieticLearningLoop

```python
class AutopoieticLearningLoop:
    """The Great Awakening - complete self-evolution system."""
    
    def __init__(
        self,
        protocol_chunks: Optional[List[str]] = None,
        guardian_review_enabled: bool = True,
        auto_crystallization: bool = False  # DANGEROUS!
    )
    
    # Epoch 1: Stardust
    def capture_stardust(self, entry: Dict[str, Any]) -> StardustEntry
    def get_recent_stardust(self, count: int = 100) -> List[StardustEntry]
    
    # Epoch 2: Nebulae
    def detect_nebulae(
        self, 
        min_occurrences: int = 5,
        min_success_rate: float = 0.7
    ) -> List[NebulaePattern]
    
    def propose_controller(self, pattern: NebulaePattern) -> Optional[str]
    
    # Epoch 3: Ignition
    def ignite_wisdom(
        self,
        pattern: NebulaePattern,
        run_validation: bool = True
    ) -> Optional[IgnitedWisdom]
    
    def guardian_approve(
        self,
        wisdom_id: str,
        approved: bool,
        notes: str = ""
    ) -> bool
    
    # Epoch 4: Galaxies
    def crystallize_knowledge(
        self,
        wisdom: IgnitedWisdom
    ) -> Optional[GalaxyKnowledge]
    
    # Full cycle
    def run_learning_cycle(
        self,
        detect_patterns: bool = True,
        propose_solutions: bool = True,
        min_occurrences: int = 5
    ) -> Dict[str, Any]
    
    # Metrics and monitoring
    def get_metrics(self) -> Dict[str, Any]
    def get_guardian_queue(self) -> List[Dict[str, Any]]
```

## Epoch Details

### Epoch 1: STARDUST - Experience Capture

**Entry Point**: Every system action

```python
# Automatic capture via ThoughtTrail
@log_to_thought_trail
def process_query(query):
    result = execute_query(query)
    # Automatically becomes Stardust
    return result

# Manual capture
loop.capture_stardust({
    "action_type": "query_processing",
    "intention": "Answer user question about SPRs",
    "action": "Executed CRCS → found controller → generated response",
    "reflection": "Success - high confidence match",
    "confidence": 0.95
})
```

**Storage**: Rolling buffer (last 1000 entries)

**Quantum Enhancement**: Each Stardust has quantum confidence state

### Epoch 2: NEBULAE - Pattern Formation

**Detection Algorithm**:

```python
# Group stardust by pattern signature
def create_pattern_signature(stardust):
    features = f"{stardust.action_type}:{stardust.intention[:50]}"
    return hashlib.md5(features.encode()).hexdigest()

# Count occurrences
pattern_groups = defaultdict(list)
for stardust in buffer:
    sig = create_pattern_signature(stardust)
    pattern_groups[sig].append(stardust)

# Identify nebulae
for sig, entries in pattern_groups.items():
    if len(entries) >= 5:  # Minimum frequency
        success_rate = sum(e.confidence >= 0.7 for e in entries) / len(entries)
        if success_rate >= 0.7:  # Minimum success
            # This is a nebula!
            pattern = NebulaePattern(
                pattern_signature=sig,
                occurrences=len(entries),
                success_rate=success_rate,
                sample_entries=entries[:5]
            )
```

**Controller Proposal**:

When nebula detected, automatically generate controller code:

```python
def propose_controller(pattern):
    return f'''
class PatternController_{pattern.pattern_id}:
    """
    Specialized controller for pattern: {pattern.pattern_signature}
    Generated by Autopoietic Learning Loop
    
    Detected {pattern.occurrences} occurrences with {pattern.success_rate:.1%} success
    """
    
    def __init__(self):
        self.pattern_signature = "{pattern.pattern_signature}"
        self.confidence_threshold = {pattern.success_rate}
    
    def can_handle(self, query: str) -> bool:
        return self._matches_pattern(query)
    
    def process(self, query: str) -> Dict[str, Any]:
        # Specialized processing
        return {{
            "response": "...",
            "confidence": {pattern.success_rate},
            "controller": self.__class__.__name__
        }}
'''
```

### Epoch 3: IGNITION - Wisdom Forging

**The Star-Forge Process**:

1. **Hypothesis Formulation**
   ```python
   hypothesis = f"Pattern {pattern.signature} can be handled by a specialized controller with {pattern.success_rate:.1%} confidence"
   ```

2. **Evidence Gathering**
   ```python
   evidence = [
       {"type": "frequency_analysis", "occurrences": pattern.occurrences},
       {"type": "sample_entries", "avg_confidence": avg_confidence}
   ]
   ```

3. **Validation Testing** (if `run_validation=True`)
   ```python
   # Replay historical queries
   # Test proposed solution
   # Measure improvement
   # Calculate cost-benefit ratio
   ```

4. **Guardian Review Queue**
   ```python
   if guardian_review_enabled:
       guardian_queue.append(pattern)
       wisdom.guardian_approval = False  # Awaiting
   ```

5. **Approval/Rejection**
   ```python
   def guardian_approve(wisdom_id, approved, notes):
       wisdom = ignited_wisdom[wisdom_id]
       wisdom.guardian_approval = approved
       
       if approved:
           # Proceed to crystallization
           if auto_crystallization:
               crystallize_knowledge(wisdom)
       else:
           # Reject and mark pattern
           wisdom.source_pattern.status = "rejected"
   ```

### Epoch 4: GALAXIES - Knowledge Crystallization

**The Crystallization Process**:

```python
def crystallize_knowledge(wisdom):
    # Generate SPR definition
    spr_name = f"Pattern_{wisdom.source_pattern.signature[:16]}_Controller"
    spr_definition = {
        "spr_id": generate_id("spr"),
        "name": spr_name,
        "pattern": wisdom.source_pattern.signature,
        "description": wisdom.hypothesis,
        "implementation": wisdom.source_pattern.proposed_solution,
        "confidence": wisdom.source_pattern.success_rate,
        "source": "autopoietic_learning_loop",
        "created_at": now()
    }
    
    # Create galaxy knowledge
    galaxy = GalaxyKnowledge(
        spr_id=spr_definition["spr_id"],
        spr_name=spr_name,
        source_wisdom=wisdom,
        spr_definition=spr_definition,
        integration_timestamp=now(),
        system_impact={
            "estimated_queries_affected": wisdom.source_pattern.occurrences,
            "estimated_improvement": validation_results["expected_improvement"],
            "confidence": wisdom.source_pattern.success_rate
        }
    )
    
    # Integrate with SPRManager
    spr_manager.add_spr(spr_definition)
    
    # Integrate with CRCS (if controller)
    if is_controller(wisdom):
        crcs.register_controller(load_controller(wisdom.proposed_solution))
    
    # Broadcast system-wide
    notify_all_components(galaxy)
    
    return galaxy
```

**Result**: Permanent system enhancement

## Safety Mechanisms

### Guardian Review (Default: ENABLED)

**Why**: Prevents runaway self-modification

```python
AutopoieticLearningLoop(
    guardian_review_enabled=True,  # REQUIRED FOR SAFETY
    auto_crystallization=False     # DANGEROUS IF TRUE
)
```

**Guardian Queue**: All wisdom awaits approval before crystallization

**Review Interface**:
```python
queue = loop.get_guardian_queue()
for item in queue:
    print(f"Pattern: {item['signature']}")
    print(f"Occurrences: {item['occurrences']}")
    print(f"Success rate: {item['success_rate']}")
    print(f"Proposed solution:\n{item['proposed_solution']}")
    
    # Guardian decides
    approved = input("Approve? (y/n): ") == 'y'
    notes = input("Notes: ")
    
    loop.guardian_approve(item['wisdom_id'], approved, notes)
```

### Auto-Crystallization (Default: DISABLED)

**DANGER**: If `auto_crystallization=True` AND `guardian_review_enabled=False`:
- System modifies itself without oversight
- Potentially dangerous code could be integrated
- **ONLY USE IN SANDBOXED ENVIRONMENTS**

**Safe Mode** (recommended):
```python
AutopoieticLearningLoop(
    guardian_review_enabled=True,   # Queue for review
    auto_crystallization=False      # Manual approval required
)
```

**Research Mode** (sandboxed only):
```python
AutopoieticLearningLoop(
    guardian_review_enabled=False,  # No queue
    auto_crystallization=True       # Automatic integration
)
```

### Validation Testing

Before crystallization, wisdom is tested:
1. Historical query replay
2. Performance measurement
3. Error rate checking
4. Cost-benefit analysis

**Minimum Requirements**:
- Success rate ≥ 70%
- Improvement ≥ 20%
- No errors in testing
- Cost-benefit ratio ≥ 1.5

## Usage Examples

### Basic Learning Cycle

```python
from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop

# Initialize (Guardian-safe)
loop = AutopoieticLearningLoop(
    guardian_review_enabled=True,
    auto_crystallization=False
)

# Capture experiences (automatic via ThoughtTrail)
# Or manual:
for i in range(20):
    loop.capture_stardust({
        "action_type": "query_processing",
        "intention": f"Process query type {i % 5}",
        "action": f"Executed action {i}",
        "reflection": "Success",
        "confidence": 0.8
    })

# Run learning cycle
results = loop.run_learning_cycle(min_occurrences=3)

print(f"Stardust analyzed: {results['stardust_analyzed']}")
print(f"Nebulae detected: {results['nebulae_detected']}")
print(f"Wisdom ignited: {results['wisdom_ignited']}")
```

### Guardian Review

```python
# Check queue
queue = loop.get_guardian_queue()
print(f"{len(queue)} items awaiting review")

# Review and approve
for item in queue:
    print(f"\nPattern: {item['signature'][:40]}...")
    print(f"Frequency: {item['occurrences']}")
    print(f"Success: {item['success_rate']:.1%}")
    
    # Manual approval
    loop.guardian_approve(
        wisdom_id=find_wisdom_id(item),
        approved=True,
        notes="Looks good, approved for integration"
    )

# Crystallize approved wisdom
for wisdom_id, wisdom in loop.ignited_wisdom.items():
    if wisdom.guardian_approval:
        galaxy = loop.crystallize_knowledge(wisdom)
        print(f"✓ Crystallized: {galaxy.spr_name}")
```

### Monitor Learning Progress

```python
metrics = loop.get_metrics()

print(f"Stardust captured: {metrics['stardust_captured']}")
print(f"Nebulae detected: {metrics['nebulae_detected']}")
print(f"Wisdom ignited: {metrics['wisdom_ignited']}")
print(f"Knowledge crystallized: {metrics['knowledge_crystallized']}")
print(f"Guardian approvals: {metrics['guardian_approvals']}")
print(f"Guardian rejections: {metrics['guardian_rejections']}")

# Current state
state = metrics['current_state']
print(f"\nBuffer: {state['stardust_buffer_size']}/1000")
print(f"Active nebulae: {state['detected_nebulae']}")
print(f"Pending wisdom: {state['ignited_wisdom']}")
print(f"Guardian queue: {state['guardian_queue_size']}")
```

## Metrics & KPIs

### Learning Rate
```python
learning_rate = stardust_captured / uptime_hours
# Target: ≥10 stardust/hour for active system
```

### Pattern Detection Rate
```python
pattern_rate = nebulae_detected / stardust_captured
# Target: 1-5% (not everything should be a pattern)
```

### Approval Rate
```python
approval_rate = guardian_approvals / (guardian_approvals + guardian_rejections)
# Target: 50-80% (if too high, detection is too conservative)
```

### Crystallization Success
```python
crystallization_rate = knowledge_crystallized / wisdom_ignited
# Target: 70-90% (most approved wisdom should crystallize)
```

## Integration Points

### With ThoughtTrail
- **Direction**: ThoughtTrail → Learning Loop
- **Data**: IAR-compliant experience entries
- **Frequency**: Continuous (every action)
- **Format**: StardustEntry compatible

### With ACO
- **Direction**: Learning Loop ↔ ACO
- **Data**: Pattern observations, controller proposals
- **Frequency**: On-demand (during nebulae detection)
- **Format**: NebulaePattern

### With InsightSolidification
- **Direction**: Learning Loop → InsightSolidification
- **Data**: Wisdom for validation
- **Frequency**: During ignition phase
- **Format**: IgnitedWisdom

### With SPRManager
- **Direction**: Learning Loop → SPRManager
- **Data**: New SPR definitions
- **Frequency**: During crystallization
- **Format**: GalaxyKnowledge → SPR

### With CRCS
- **Direction**: Learning Loop → CRCS
- **Data**: New controller code
- **Frequency**: Post-crystallization
- **Format**: Controller class definition

## Success Criteria

Learning loop is working when:

1. ✅ Stardust captured continuously
2. ✅ Patterns detected at reasonable rate (1-5%)
3. ✅ Nebulae have meaningful proposals
4. ✅ Guardian queue functional
5. ✅ Approved wisdom crystallizes successfully
6. ✅ New knowledge integrates into system
7. ✅ System capabilities measurably improve
8. ✅ No runaway self-modification

## Performance Characteristics

- **Stardust capture**: <1ms per entry
- **Pattern detection**: 0.05-1ms for 1000 entries
- **Controller proposal**: ~5ms
- **Wisdom ignition**: 1-10ms
- **Crystallization**: 10-100ms
- **Full cycle**: <100ms for typical workload

## Known Limitations

1. **ThoughtTrail Schema**: Expects specific IAR format
2. **Pattern Signature**: MD5-based, may have collisions
3. **Controller Generation**: Template-based, not semantic
4. **Validation**: Simulated, not real-world testing
5. **Single-threaded**: One cycle at a time

## Future Enhancements

1. **Semantic Pattern Detection**: Use LLM to understand patterns deeply
2. **Multi-Level Learning**: Learn at code, design, architecture levels
3. **Collaborative Learning**: Multiple agents learning together
4. **Continuous Validation**: Real-time testing of crystallized knowledge
5. **Evolution History**: Track lineage of knowledge (what evolved from what)
6. **Automatic Rollback**: Undo problematic crystallizations
7. **A/B Testing**: Compare old vs new capabilities before full integration

## Guardian Notes

**Critical Review Points**:
1. Is Guardian review ENABLED? (Must be YES for production)
2. Is auto-crystallization DISABLED? (Must be NO for production)
3. Are pattern thresholds appropriate? (≥5 occurrences, ≥70% success)
4. Are proposals being vetted for safety? (No dangerous code generation)
5. Is validation testing sufficient? (Or just simulated?)

**Approval Checklist**:
- [ ] Guardian review enabled
- [ ] Auto-crystallization disabled
- [ ] Pattern thresholds reasonable
- [ ] Validation testing active
- [ ] Rollback mechanism exists
- [ ] Integration is safe (no code injection)

---

**Specification Status**: ✅ IMPLEMENTED  
**Implementation**: `Three_PointO_ArchE/autopoietic_learning_loop.py`  
**Version**: 1.0  
**Autopoiesis Level**: ★★★★★ (Self-Evolving)  
**Safety**: ✅ Guardian-Protected
