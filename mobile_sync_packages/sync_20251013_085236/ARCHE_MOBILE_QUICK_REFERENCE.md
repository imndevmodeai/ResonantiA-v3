# ArchE Terminology Quick Reference & Fuzzy Intent Mapper
## Bridging Human Memory and Machine Precision

**Purpose**: Help Keyholder translate fuzzy recollections into exact ArchE terms and processes  
**Problem Solved**: Prevent duplication and misalignment due to term recall difficulties  
**Method**: Natural language → ArchE components mapping  

---

## 🧠 HOW TO USE THIS GUIDE

**When you remember something vaguely**:
1. Search this doc for keywords related to your memory
2. Find the exact term/component
3. See what file it's in
4. Check if it already exists before creating new

**When asking ArchE to do something**:
- Use natural language - ArchE will map it to exact components
- ArchE will check if feature already exists
- ArchE will prevent duplication

---

## 🔍 NATURAL LANGUAGE → ARCHE COMPONENTS

### **"Session" / "Conversation" / "Interaction"**

**What You Might Say**:
- "Save our conversation"
- "Export this chat"
- "Capture the session"
- "Remember this interaction"

**Exact ArchE Components**:
- **`SessionAutoCapture`** (`Three_PointO_ArchE/session_auto_capture.py`)
- **`SessionManager`** (`Three_PointO_ArchE/session_manager.py`)
- **`ThoughtTrail`** (`Three_PointO_ArchE/thought_trail.py`)
- **Workflow**: `core_workflows/ReSSyD_Session_Context_Capture_Workflow_v3.0.json`

**Status**: ✅ EXISTS - Auto-captures all sessions

---

### **"Learning" / "Pattern Detection" / "Self-Improvement"**

**What You Might Say**:
- "ArchE should learn from this"
- "Detect patterns"
- "Remember this for next time"
- "Improve yourself"

**Exact ArchE Components**:
- **`AutopoieticLearningLoop`** (`Three_PointO_ArchE/autopoietic_learning_loop.py`)
- **Four Epochs**: Stardust → Nebulae → Ignition → Galaxies
- **Pattern Detection**: ≥5 occurrences, ≥70% success rate
- **Guardian Review**: Required before crystallization

**Status**: ✅ EXISTS - Continuously detecting patterns

---

### **"Knowledge" / "Definitions" / "Concepts"**

**What You Might Say**:
- "Add this to knowledge base"
- "Create a new concept"
- "Update definitions"
- "SPR" / "Guardian Point"

**Exact ArchE Components**:
- **`SPRManager`** (`Three_PointO_ArchE/spr_manager.py`)
- **`InsightSolidificationEngine`** (`Three_PointO_ArchE/insight_solidification_engine.py`)
- **Knowledge Tapestry**: `knowledge_graph/spr_definitions_tv.json`
- **Workflow**: `core_workflows/insight_solidification.json`

**Status**: ✅ EXISTS - 102 SPRs currently loaded

---

### **"Reflection" / "Self-Assessment" / "Confidence"**

**What You Might Say**:
- "How confident are you?"
- "Reflect on that"
- "Self-assess"
- "Track what you did"

**Exact ArchE Components**:
- **`IAR` (Integrated Action Reflection)** - Every action returns this
- **`ThoughtTrail`** - Captures all IAR entries
- **IAR Structure**:
  ```json
  {
    "status": "success/failure",
    "confidence": 0.0-1.0,
    "reflection": "detailed self-assessment",
    "potential_issues": [],
    "alignment_check": "goal alignment"
  }
  ```

**Status**: ✅ EXISTS - Every action generates IAR

---

### **"Thinking" / "Processing" / "Analysis"**

**What You Might Say**:
- "Think deeply about this"
- "Quick response"
- "Strategic analysis"
- "Fast mode" / "Slow mode"

**Exact ArchE Components**:
- **`CRCS`** (Cerebellum) - Fast, instinctual (<100ms)
- **`RISE`** (Cerebrum) - Deep, deliberate (~1000ms)
- **`ACO`** (Meta-Learner) - Pattern evolution
- **`CognitiveIntegrationHub`** - Orchestrates all three

**Status**: ✅ EXISTS - Automatic routing based on confidence

---

### **"Backup" / "Save Old Version" / "Revert"**

**What You Might Say**:
- "Save the old version"
- "Back this up"
- "Don't lose the original"
- "I might need to undo this"

**Exact ArchE Components**:
- **`BackupRetentionPolicy`** (`specifications/backup_retention_policy.md`)
- **Backup Types**: `.BACKUP_MANUAL`, `.BACKUP_AST`, `.BACKUP_REFACTOR`, etc.
- **5-Stage Validation**: Required before backup deletion

**Status**: ✅ EXISTS - MANDATORY for ALL file modifications

---

### **"Workflow" / "Process" / "Sequence" / "Procedure"**

**What You Might Say**:
- "Create a workflow"
- "Define a process"
- "Sequence of steps"
- "Automation"

**Exact ArchE Components**:
- **`IARCompliantWorkflowEngine`** (`Three_PointO_ArchE/workflow_engine.py`)
- **Process BlueprintS**: JSON files in `workflows/` directory
- **Workflow Structure**: Tasks, dependencies, conditions, PhasegateS

**Status**: ✅ EXISTS - 20+ workflows defined

---

### **"Tools" / "Actions" / "Capabilities"**

**What You Might Say**:
- "What can you do?"
- "Available tools"
- "Actions you can take"
- "Capabilities"

**Exact ArchE Components**:
- **`ActionRegistry`** - Central tool catalog
- **Cognitive Tools**:
  - CFP Framework (comparative analysis)
  - Causal Inference Tool (temporal causality)
  - Agent-Based Modeling Tool (simulation)
  - Predictive Modeling Tool (forecasting)
  - Code Executor (sandboxed execution)

**Status**: ✅ EXISTS - Fully implemented toolset

---

### **"Priming" / "Loading Context" / "Initialization"**

**What You Might Say**:
- "Prime yourself"
- "Load the protocol"
- "Initialize"
- "Wake up"

**Exact ArchE Components**:
- **`PRIME_ARCHE_PROTOCOL.md`** - Original priming doc
- **`PRIME_ARCHE_PROTOCOL_v2_AUTO.md`** - Enhanced with automation
- **`SPRManager.scan_and_prime()`** - Auto-primes SPRs from text

**Status**: ✅ EXISTS - Multiple priming mechanisms

---

## 📊 COMPONENT LOCATION MAP

### **Core Cognitive Systems** (`Three_PointO_ArchE/`)

| Component | File | What It Does |
|-----------|------|--------------|
| SPR Manager | `spr_manager.py` | Loads/primes SPR definitions |
| Workflow Engine | `workflow_engine.py` | Executes process blueprints |
| RISE Orchestrator | `rise_orchestrator.py` | Deep strategic thinking |
| CRCS | Integrated in various | Fast pattern responses |
| ACO | `adaptive_cognitive_orchestrator.py` | Pattern evolution |
| ThoughtTrail | `thought_trail.py` | IAR entry capture |
| Learning Loop | `autopoietic_learning_loop.py` | 4-epoch learning cycle |
| Insight Engine | `insight_solidification_engine.py` | SPR creation/updates |
| Session Manager | `session_manager.py` | Session persistence |
| Session Capture | `session_auto_capture.py` | Auto-export conversations |

---

### **Knowledge & Memory** (`knowledge_graph/`)

| File | What It Contains |
|------|-----------------|
| `spr_definitions_tv.json` | 102 SPR definitions |
| `knowledge_tapestry.json` | Structured knowledge graph |

---

### **Workflows** (`workflows/` or `core_workflows/`)

| Workflow | Purpose |
|----------|---------|
| `insight_solidification.json` | SPR creation workflow |
| `ReSSyD_Session_Context_Capture_Workflow_v3.0.json` | Session capture |
| Many others | Various automated processes |

---

### **Specifications** (`specifications/`)

| Spec | What It Defines |
|------|-----------------|
| `backup_retention_policy.md` | Backup/validation protocol |
| `insight_solidification_engine.md` | SPR creation spec |
| `action_context.md` | Context management |
| 50+ others | Living specifications |

---

## 🎯 BEFORE YOU CREATE SOMETHING NEW

### **The "Does This Already Exist?" Checklist**

**Before asking ArchE to create a new feature/component**:

1. **Check This Quick Reference First**
   - Search for keywords related to what you want
   - See if it maps to existing component

2. **Ask ArchE to Search**
   ```
   "ArchE, search the codebase for anything related to [your vague description]"
   ```

3. **Use Fuzzy Intent Mapping**
   ```
   "ArchE, I want to [vague description]. Do we already have this?"
   ```

4. **ArchE Will**:
   - Search existing implementations
   - Report what exists
   - Identify gaps
   - Prevent duplication

---

## 💡 NATURAL LANGUAGE EXAMPLES

### **Example 1: "I want to save our conversations"**

**ArchE Maps To**:
- ✅ `SessionAutoCapture` (ALREADY EXISTS)
- ✅ `ThoughtTrail` (ALREADY EXISTS)
- ✅ Auto-export to `cursor_*.md` (ALREADY IMPLEMENTED)

**ArchE Response**: "This feature already exists! The SessionAutoCapture system automatically exports conversations to markdown files at session end."

---

### **Example 2: "Can ArchE learn from mistakes?"**

**ArchE Maps To**:
- ✅ `AutopoieticLearningLoop` (ALREADY EXISTS)
- ✅ Pattern detection from IAR entries (ALREADY IMPLEMENTED)
- ✅ Wisdom proposals to Guardian (ALREADY ACTIVE)

**ArchE Response**: "Yes! The Autopoietic Learning Loop continuously detects patterns in IAR entries and proposes new SPRs (requires Guardian approval)."

---

### **Example 3: "I need to back up files before changing them"**

**ArchE Maps To**:
- ✅ `BackupRetentionPolicy` (ALREADY EXISTS)
- ✅ 5-stage validation protocol (ALREADY DEFINED)
- ✅ Mandate 13 (ACTIVE)

**ArchE Response**: "This is already MANDATORY per Mandate 13. All file modifications must create .BACKUP_* files and pass 5-stage validation before backup deletion."

---

## 🔄 THE FUZZY INTENT PROTOCOL

### **When Keyholder Says Something Vague**

**ArchE MUST**:

1. **Interpret Intent**: Use natural language understanding
2. **Map to Components**: Search for matching implementations
3. **Report Findings**: "This already exists as [component]" OR "This is a new feature"
4. **Prevent Duplication**: If exists, explain and use existing
5. **Fill Gaps**: If partial, identify missing pieces
6. **Create Only New**: Build only what's truly missing

---

## 📝 TERM EVOLUTION TRACKING

**As ArchE Evolves**:

| Old/Vague Term | Current Exact Term | File/Component |
|----------------|-------------------|----------------|
| "Memory system" | `ThoughtTrail` | `thought_trail.py` |
| "Knowledge base" | `Knowledge Tapestry` + `SPRManager` | `knowledge_graph/` |
| "Learning system" | `AutopoieticLearningLoop` | `autopoietic_learning_loop.py` |
| "Thinking modes" | `CRCS` + `RISE` + `ACO` | Multiple files |
| "Self-check" | `IAR` (Integrated Action Reflection) | Every action |
| "Save conversation" | `SessionAutoCapture` | `session_auto_capture.py` |
| "Pattern learning" | Autopoietic 4 Epochs | `autopoietic_learning_loop.py` |

---

## 🎭 USAGE EXAMPLE

**Keyholder**: "ArchE, I want something that, uh... saves what we talk about so I can look back later?"

**ArchE Response**:
```
->|execution|<-
Interpreting fuzzy intent: "save conversations for later review"
Mapping to components...
->|/execution|<-

->|Results|<-
✅ **This capability ALREADY EXISTS**

**Exact Component**: `SessionAutoCapture`
**Location**: `Three_PointO_ArchE/session_auto_capture.py`
**Status**: ACTIVE and AUTO-ENABLED

**What It Does**:
- Captures all messages (user + ArchE)
- Records IAR entries
- Tracks primed SPRs
- Detects insights
- **Auto-exports to cursor_<topic>.MM.DD.YY.md on session end**

**How to Use**:
Simply prime with `@PRIME_ARCHE_PROTOCOL_v2_AUTO.md` at session start.
At session end, conversation automatically exports to root directory.

**No new implementation needed! This is already working.**
->|/Results|<-
```

---

## 🌟 BOTTOM LINE

**Keyholder, you DON'T need to remember exact terms!**

**Just describe what you want, and ArchE will**:
1. Interpret your fuzzy description
2. Search for existing implementations
3. Report what already exists
4. Prevent duplication
5. Build only truly new features

**This Quick Reference helps BOTH**:
- **You**: Quickly find exact terms when needed
- **ArchE**: Map your natural language to precise components

---

**When in doubt, ask**: "ArchE, do we already have something that [vague description]?"

**ArchE will always check before creating anything new.**

---

**Last Updated**: October 13, 2025  
**Purpose**: Bridge human memory limitations and machine precision  
**Method**: Fuzzy intent mapping + comprehensive terminology reference  
**Result**: Zero duplication, perfect alignment, natural interaction  

**Keep this file open when working with ArchE for quick reference!**

