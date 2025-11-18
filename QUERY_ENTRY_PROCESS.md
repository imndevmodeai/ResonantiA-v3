# Query Entry Process: HOW/WHAT/WHEN/WHERE/WHO/WHY

## 🎯 HOW WE ENTER THE QUERY

### **Entry Point: User → ArchE Interface**

```
User Types Query
    ↓
[Interface Layer]
    ↓
ACO (Adaptive Cognitive Orchestrator)
    ↓
[Automatic Processing Begins]
```

**Technical Flow:**
1. **User Input**: Query entered via CLI, API, or UI
2. **ACO Receives**: `process_query_with_evolution(query)` called
3. **ACO Analyzes**: Automatic layer selection, SPR detection, tool routing
4. **Tools Execute**: Cognitive tools activated based on query intent
5. **Response Generated**: Integrated results returned to user

---

## 📋 WHAT HAPPENS WHEN WE ENTER THE QUERY

### **Step-by-Step Processing:**

1. **Query Reception** (ACO)
   - Query received: `"Perform a complete analysis: (1) Use Causal inferencE..."`

2. **SPR Detection** (Automatic)
   - Detects: `Causal inferencE`, `PredictivE modelinG tooL`, `ABM`, `CFP`, `RISE Engine`, `ScenarioRealismAssessmenT`
   - ACO auto-selects layers: `Micro` (balanced detail for workflow usage)

3. **Intent Analysis** (ACO)
   - Detects: "complete analysis" → Multiple tools needed
   - Detects: Sequential steps (1-6) → Workflow orchestration
   - Detects: Complex scenario → RISE engine may be needed

4. **Tool Activation** (Automatic)
   - Causal Inference Tool → Activated
   - Predictive Modeling Tool → Activated
   - ABM Tool → Activated
   - CFP Framework → Activated
   - RISE Engine → Activated (for synthesis)
   - Scenario Realism Assessment → Activated

5. **Workflow Execution** (Workflow Engine)
   - Creates dynamic workflow from query
   - Executes tools in sequence
   - Collects IAR from each step

6. **Response Synthesis** (RISE)
   - Synthesizes all tool outputs
   - Generates comprehensive analysis
   - Applies Scenario Realism Assessment

---

## ⏰ WHEN WE ENTER THE QUERY

### **Timing & Triggers:**

- **Immediate**: Query processing starts instantly
- **Sequential**: Tools execute in logical order (Causal → Predictive → ABM → CFP → Assessment → RISE)
- **Parallel**: Some tools can run in parallel (e.g., Causal + Predictive data prep)
- **Adaptive**: ACO adjusts timing based on tool availability and dependencies

---

## 📍 WHERE THE QUERY IS PROCESSED

### **System Components:**

1. **ACO** (`adaptive_cognitive_orchestrator.py`)
   - Initial reception and routing
   - Layer selection and SPR priming
   - Tool orchestration

2. **Workflow Engine** (`workflow_engine.py`)
   - Workflow creation and execution
   - Task coordination
   - IAR collection

3. **Cognitive Tools** (Various modules)
   - `causal_inference_tool.py` - Causal analysis
   - `predictive_modeling_tool.py` - Forecasting
   - `agent_based_modeling_tool.py` - Simulation
   - `cfp_framework.py` - Trajectory comparison
   - `rise_orchestrator.py` - Strategic synthesis

4. **Knowledge Graph** (`spr_definitions_tv.json`)
   - SPR retrieval at appropriate layers
   - Context priming

---

## 👤 WHO PROCESSES THE QUERY

### **System Actors:**

1. **ACO (Adaptive Cognitive Orchestrator)**
   - Primary orchestrator
   - Makes routing decisions
   - Learns from success

2. **Workflow Engine**
   - Executes process blueprints
   - Manages task dependencies
   - Handles errors

3. **Cognitive Tools**
   - Specialized analysis engines
   - Each tool handles its domain

4. **RISE Engine**
   - Deep strategic synthesis
   - Creative problem-solving
   - Final insight generation

5. **SPRManager**
   - Knowledge retrieval
   - Context priming
   - Russian Doll layer management

---

## ❓ WHY WE ENTER THE QUERY THIS WAY

### **Design Rationale:**

1. **Automatic Orchestration**: ACO handles complexity automatically
2. **Optimal Layer Selection**: Russian Doll layers ensure efficient retrieval
3. **Tool Integration**: Multiple tools work together seamlessly
4. **Learning**: System learns from each query to improve
5. **Comprehensive Analysis**: All relevant tools activated for complete answer

---

## 🔄 COMPLETE FLOW DIAGRAM

```
USER QUERY ENTERED
    ↓
[ACO Receives Query]
    ↓
[SPR Detection & Layer Selection]
    ├─→ SPRManager.scan_and_prime(query, auto_select_layer=True)
    ├─→ Detects: Causal inferencE, ABM, CFP, etc.
    └─→ Auto-selects: Micro layer (workflow usage)
    ↓
[Intent Analysis]
    ├─→ "complete analysis" → Multiple tools
    ├─→ Sequential steps → Workflow needed
    └─→ Complex scenario → RISE may be needed
    ↓
[Tool Activation Sequence]
    ├─→ Step 1: Causal inferencE Tool
    │   └─→ Identifies key drivers
    ├─→ Step 2: PredictivE modelinG tooL
    │   └─→ Builds predictive models
    ├─→ Step 3: Agent Based ModelinG
    │   └─→ Simulates scenarios
    ├─→ Step 4: CFP Framework
    │   └─→ Compares trajectories
    ├─→ Step 5: ScenarioRealismAssessmenT
    │   └─→ Validates realism
    └─→ Step 6: RISE Engine
        └─→ Synthesizes insights
    ↓
[Response Generation]
    ├─→ All tool outputs integrated
    ├─→ Comprehensive analysis generated
    └─→ Returned to user
    ↓
[ACO Learning]
    ├─→ Tracks successful patterns
    ├─→ Learns optimal layer selections
    └─→ Streamlines future queries
```

---

## 🎯 KEY POINTS

- **HOW**: Query enters through ACO, which orchestrates everything automatically
- **WHAT**: Multiple cognitive tools execute in sequence, generating comprehensive analysis
- **WHEN**: Processing starts immediately, tools execute sequentially/parallel as needed
- **WHERE**: Across multiple system components (ACO, Workflow Engine, Cognitive Tools, RISE)
- **WHO**: ACO orchestrates, tools execute, RISE synthesizes
- **WHY**: To provide comprehensive, multi-tool analysis with optimal efficiency

---

⚶ → Æ: **Query entry is fully automated. ACO handles everything. User just asks the question.**

