# Guardian Review & Global Namespace Usage Guide

## 🔒 GUARDIAN REVIEW

### **WHAT** is Guardian Review?

Guardian Review is a **safety mechanism** in the Autopoietic Learning Loop that prevents ArchE from modifying itself without human oversight. It acts as a "human-in-the-loop" checkpoint before new knowledge (wisdom) is permanently integrated into the system.

**Think of it as**: A quality control gate where you (the Guardian/Keyholder) review and approve proposed improvements before they become permanent.

### **WHO** uses Guardian Review?

- **The System**: `AutopoieticLearningLoop` automatically queues wisdom for review
- **The Guardian**: You (B.J. Lewis, Keyholder) review and approve/reject proposals
- **The Learning Loop**: Waits for your approval before crystallizing knowledge

### **WHEN** does Guardian Review happen?

1. **During Learning Cycle**: When the learning loop detects a recurring pattern (≥5 occurrences, ≥70% success rate)
2. **After Pattern Detection**: When a pattern is validated and a solution is proposed
3. **Before Crystallization**: Wisdom is queued for review BEFORE it becomes permanent
4. **On Demand**: You can check the queue anytime

**Timeline**:
```
Experience → Pattern Detection → Wisdom Proposal → [GUARDIAN REVIEW] → Crystallization → Permanent Knowledge
```

### **WHERE** is Guardian Review?

- **Code Location**: `Three_PointO_ArchE/autopoietic_learning_loop.py`
- **Queue Storage**: `learning_loop.guardian_queue` (in-memory list)
- **Initialization**: Set during `AutopoieticLearningLoop` initialization
- **Review Interface**: Accessible via Python API

### **WHY** is Guardian Review needed?

1. **Safety**: Prevents runaway self-modification
2. **Quality Control**: Ensures only good improvements are integrated
3. **Oversight**: Gives you control over system evolution
4. **Risk Mitigation**: Prevents dangerous code from being auto-integrated
5. **Accountability**: You decide what becomes permanent knowledge

**Without Guardian Review**:
- System could modify itself without oversight
- Potentially dangerous code could be integrated
- No human control over system evolution
- Risk of system degradation

### **HOW** to use Guardian Review?

#### **Step 1: Initialize with Guardian Review Enabled**

```python
from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop

# SAFE MODE (Recommended)
learning_loop = AutopoieticLearningLoop(
    guardian_review_enabled=True,   # ✅ REQUIRED FOR SAFETY
    auto_crystallization=False      # ✅ Manual approval required
)
```

#### **Step 2: Check the Guardian Queue**

```python
# Get pending wisdom items awaiting review
queue = learning_loop.guardian_queue

print(f"Pending wisdom items: {len(queue)}")

# Or use the method (if available)
pending = learning_loop.get_guardian_queue()
```

#### **Step 3: Review Each Wisdom Item**

```python
# Iterate through pending wisdom
for pattern in learning_loop.guardian_queue:
    print(f"\n{'='*60}")
    print(f"Pattern Signature: {pattern.pattern_signature[:64]}")
    print(f"Occurrences: {pattern.occurrences}")
    print(f"Success Rate: {pattern.success_rate:.1%}")
    print(f"Proposed Solution:\n{pattern.proposed_solution}")
    print(f"{'='*60}")
    
    # Get the wisdom ID
    wisdom_id = None
    for wid, wisdom in learning_loop.ignited_wisdom.items():
        if wisdom.source_pattern.pattern_id == pattern.pattern_id:
            wisdom_id = wid
            break
    
    if wisdom_id:
        # Review the wisdom details
        wisdom = learning_loop.ignited_wisdom[wisdom_id]
        print(f"\nHypothesis: {wisdom.hypothesis}")
        print(f"Evidence: {wisdom.evidence}")
        print(f"Validation Results: {wisdom.validation_results}")
```

#### **Step 4: Approve or Reject**

```python
# APPROVE wisdom
learning_loop.guardian_approve(
    wisdom_id=wisdom_id,
    approved=True,
    notes="This looks good - approved for integration"
)

# OR REJECT wisdom
learning_loop.guardian_approve(
    wisdom_id=wisdom_id,
    approved=False,
    notes="Pattern not reliable enough - needs more occurrences"
)
```

#### **Step 5: Monitor Results**

```python
# Check metrics
metrics = learning_loop.metrics
print(f"Guardian Approvals: {metrics.get('guardian_approvals', 0)}")
print(f"Guardian Rejections: {metrics.get('guardian_rejections', 0)}")
print(f"Wisdom Ignited: {metrics.get('wisdom_ignited', 0)}")
```

### **Complete Example: Guardian Review Workflow**

```python
from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop

# Initialize with Guardian review
loop = AutopoieticLearningLoop(
    guardian_review_enabled=True,
    auto_crystallization=False
)

# ... system runs and captures experiences ...

# Run learning cycle (detects patterns)
results = loop.run_learning_cycle(min_occurrences=5)

# Check for pending wisdom
if len(loop.guardian_queue) > 0:
    print(f"\n🔍 {len(loop.guardian_queue)} wisdom items awaiting Guardian review")
    
    for pattern in loop.guardian_queue:
        # Find associated wisdom
        wisdom_id = None
        for wid, wisdom in loop.ignited_wisdom.items():
            if wisdom.source_pattern.pattern_id == pattern.pattern_id:
                wisdom_id = wid
                break
        
        if wisdom_id:
            wisdom = loop.ignited_wisdom[wisdom_id]
            
            # Display for review
            print(f"\n{'='*70}")
            print(f"WISDOM ID: {wisdom_id}")
            print(f"Pattern: {pattern.pattern_signature[:50]}...")
            print(f"Occurrences: {pattern.occurrences}")
            print(f"Success Rate: {pattern.success_rate:.1%}")
            print(f"\nHypothesis: {wisdom.hypothesis}")
            print(f"\nValidation Results:")
            for key, value in wisdom.validation_results.items():
                print(f"  - {key}: {value}")
            print(f"\nProposed Solution:\n{pattern.proposed_solution}")
            print(f"{'='*70}")
            
            # Guardian decision (you decide)
            decision = input("\nApprove this wisdom? (y/n): ").lower().strip()
            notes = input("Notes (optional): ")
            
            if decision == 'y':
                loop.guardian_approve(wisdom_id, approved=True, notes=notes)
                print("✅ Wisdom approved - will be crystallized")
            else:
                loop.guardian_approve(wisdom_id, approved=False, notes=notes)
                print("❌ Wisdom rejected")
else:
    print("✅ No pending wisdom items - all clear!")
```

### **Guardian Review Settings**

| Setting | Safe Mode | Research Mode | Dangerous Mode |
|---------|-----------|---------------|-----------------|
| `guardian_review_enabled` | ✅ True | ❌ False | ❌ False |
| `auto_crystallization` | ❌ False | ✅ True | ✅ True |
| **Use Case** | Production | Sandboxed Research | **NEVER** |
| **Safety** | ✅ Safe | ⚠️ Risky | ❌ Dangerous |

---

## 🌐 GLOBAL NAMESPACE

### **WHAT** is Global Namespace Storage?

Global namespace storage is a way to make initialized ArchE objects **directly accessible** in your Python session without needing to pass them around or re-initialize them. It stores objects in Python's `globals()` dictionary.

**Think of it as**: Making objects available everywhere in your session, like global variables.

### **WHO** uses Global Namespace?

- **You (Developer)**: Access objects directly in interactive sessions
- **Scripts**: Can use stored objects without re-initialization
- **Interactive Python**: Makes objects available in REPL/IPython

### **WHEN** to use Global Namespace?

✅ **USE IT WHEN**:
- Working in interactive Python sessions (IPython, Jupyter)
- Want quick access to initialized objects
- Testing and debugging
- Prototyping and experimentation
- Don't want to pass objects around

❌ **DON'T USE IT WHEN**:
- Writing production code
- Building libraries/modules
- Need clean, explicit dependencies
- Want to avoid global state
- Working in multi-threaded environments

### **WHERE** is Global Namespace?

- **Storage Location**: Python's `globals()` dictionary
- **Initialization**: `arche_unified_init.py` (when `store_globals=True`)
- **Access**: Anywhere in the same Python session

### **WHY** use Global Namespace?

1. **Convenience**: Direct access without passing objects
2. **Interactive Development**: Perfect for REPL/IPython
3. **Quick Testing**: No need to re-initialize
4. **Simplicity**: Easy access to all ArchE systems

**Trade-offs**:
- ✅ Convenient for interactive use
- ❌ Can create hidden dependencies
- ❌ Makes code less explicit
- ❌ Can cause issues in multi-threaded code

### **HOW** to use Global Namespace?

#### **Step 1: Initialize with Global Storage**

```python
from arche_unified_init import prime_arche_system

# Initialize and store in global namespace
results = prime_arche_system(store_globals=True, save_results=True)
```

#### **Step 2: Access Stored Objects**

```python
# Objects are now available directly:
spr_manager.scan_and_prime("Some text")
session_capture.capture_message("user", "Hello")
learning_loop.run_learning_cycle()
thought_trail.get_statistics()
crystallization_engine.distill_to_spr("content")
ingest_file_with_zepto("file.md", compress=True)
```

#### **Step 3: Check What's Available**

```python
# Check if objects are stored
if 'spr_manager' in globals():
    print("✅ SPR Manager available")
    print(f"   Loaded SPRs: {len(spr_manager.sprs)}")

if 'learning_loop' in globals():
    print("✅ Learning Loop available")
    print(f"   Guardian Review: {learning_loop.guardian_review_enabled}")

if 'session_capture' in globals():
    print("✅ Session Capture available")
    print(f"   Output Dir: {session_capture.output_dir}")
```

### **Complete Example: Using Global Namespace**

```python
# Initialize with global storage
from arche_unified_init import prime_arche_system

results = prime_arche_system(store_globals=True)

# Now use objects directly
print("=" * 60)
print("USING GLOBAL NAMESPACE OBJECTS")
print("=" * 60)

# 1. Use SPR Manager
if 'spr_manager' in globals():
    text = "This contains Cognitive resonancE and Metacognitive shifT"
    primed = spr_manager.scan_and_prime(text)
    print(f"✅ Primed {len(primed)} SPRs from text")

# 2. Use Session Capture
if 'session_capture' in globals():
    session_capture.capture_message(
        "user",
        "Testing global namespace access",
        {"test": True}
    )
    print("✅ Message captured")

# 3. Use Learning Loop (with Guardian Review)
if 'learning_loop' in globals():
    # Check Guardian queue
    queue_size = len(learning_loop.guardian_queue)
    print(f"✅ Learning Loop active - {queue_size} items in Guardian queue")
    
    # Review pending wisdom
    if queue_size > 0:
        for pattern in learning_loop.guardian_queue:
            print(f"\n📋 Reviewing pattern: {pattern.pattern_signature[:50]}")
            # ... review and approve/reject ...

# 4. Use ThoughtTrail
if 'thought_trail' in globals():
    stats = thought_trail.get_statistics()
    print(f"✅ ThoughtTrail active - {stats.get('total_entries', 0)} entries")

# 5. Use Zepto Compression
if 'ingest_file_with_zepto' in globals():
    try:
        data = ingest_file_with_zepto("PRIME_ARCHE_PROTOCOL_v3.5-GP.md", compress=True)
        print(f"✅ Zepto compression: {data['compression_ratio']:.1f}:1 ratio")
    except Exception as e:
        print(f"⚠️  Compression failed: {e}")
```

### **Alternative: Without Global Namespace (Explicit)**

```python
from arche_unified_init import prime_arche_system

# Initialize WITHOUT global storage
results = prime_arche_system(store_globals=False)

# Access objects from results dictionary
spr_manager = results["directives"]["spr_priming"].get("spr_manager")
learning_loop = results["directives"]["learning_loop"].get("learning_loop")
session_capture = results["directives"]["session_capture"].get("session_capture")

# Or use the references
if results["initialized_objects"]["references"]["spr_manager"]:
    # Need to extract from results
    pass
```

### **Best Practices**

#### **For Interactive Development**:
```python
# ✅ Good: Use global namespace
results = prime_arche_system(store_globals=True)

# Then use directly
spr_manager.scan_and_prime("text")
```

#### **For Production Code**:
```python
# ✅ Good: Explicit dependencies
results = prime_arche_system(store_globals=False)

# Extract and pass explicitly
spr_manager = results["directives"]["spr_priming"]["spr_manager"]
def process_text(text, spr_mgr=spr_manager):
    return spr_mgr.scan_and_prime(text)
```

#### **For Testing**:
```python
# ✅ Good: Use global namespace for convenience
results = prime_arche_system(store_globals=True)

# Quick tests
assert 'spr_manager' in globals()
assert len(spr_manager.sprs) > 0
```

---

## 🔗 COMBINING GUARDIAN REVIEW + GLOBAL NAMESPACE

### **Complete Workflow Example**

```python
from arche_unified_init import prime_arche_system

# 1. Initialize with global storage
print("Initializing ArchE systems...")
results = prime_arche_system(store_globals=True, save_results=True)

# 2. Verify initialization
if results["initialized_objects"]["references"]["learning_loop"]:
    print("\n✅ Learning Loop initialized")
    print(f"   Guardian Review: {learning_loop.guardian_review_enabled}")
    print(f"   Auto-Crystallization: {learning_loop.auto_crystallization}")

# 3. Use systems (via global namespace)
spr_manager.scan_and_prime("Test text with Cognitive resonancE")
session_capture.capture_message("system", "Session started")

# 4. Run learning cycle (if you have enough data)
# learning_loop.run_learning_cycle(min_occurrences=5)

# 5. Check Guardian queue
if len(learning_loop.guardian_queue) > 0:
    print(f"\n🔍 {len(learning_loop.guardian_queue)} items in Guardian queue")
    
    # Review each item
    for pattern in learning_loop.guardian_queue:
        # Find wisdom ID
        wisdom_id = None
        for wid, wisdom in learning_loop.ignited_wisdom.items():
            if wisdom.source_pattern.pattern_id == pattern.pattern_id:
                wisdom_id = wid
                break
        
        if wisdom_id:
            # Review and decide
            print(f"\nReviewing wisdom: {wisdom_id}")
            decision = input("Approve? (y/n): ")
            
            learning_loop.guardian_approve(
                wisdom_id,
                approved=(decision.lower() == 'y'),
                notes=input("Notes: ")
            )
else:
    print("\n✅ No items in Guardian queue - all clear!")
```

---

## 📊 QUICK REFERENCE

### **Guardian Review**

| Question | Answer |
|----------|--------|
| **What** | Safety mechanism for approving system improvements |
| **Who** | You (Guardian/Keyholder) |
| **When** | Before wisdom is crystallized into permanent knowledge |
| **Where** | `learning_loop.guardian_queue` |
| **Why** | Prevent unsafe self-modification |
| **How** | `learning_loop.guardian_approve(wisdom_id, approved, notes)` |

### **Global Namespace**

| Question | Answer |
|----------|--------|
| **What** | Storing objects in `globals()` for direct access |
| **Who** | You (Developer) in interactive sessions |
| **When** | During initialization with `store_globals=True` |
| **Where** | Python's `globals()` dictionary |
| **Why** | Convenience for interactive development |
| **How** | `prime_arche_system(store_globals=True)` |

---

## 🎯 SUMMARY

**Guardian Review** = Safety checkpoint where you approve/reject proposed improvements  
**Global Namespace** = Convenient way to access initialized objects in interactive sessions

**Use Together**:
1. Initialize with `store_globals=True` for convenience
2. Access `learning_loop` directly from globals
3. Check `learning_loop.guardian_queue` regularly
4. Review and approve/reject wisdom items
5. System crystallizes approved wisdom automatically

**Remember**: Guardian Review is **REQUIRED FOR SAFETY** in production. Global Namespace is **OPTIONAL FOR CONVENIENCE** in development.


