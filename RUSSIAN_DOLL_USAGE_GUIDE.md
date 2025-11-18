# Russian Doll Layer Usage Guide
## How ArchE Uses Russian Doll Layers & User Interaction

**ResonantiA Protocol v3.5-GP - Russian Doll Integration**

---

## 🎯 OVERVIEW

ArchE now automatically uses Russian Doll layers for optimal performance. Users can also explicitly control layer selection when needed.

---

## 🤖 AUTOMATIC USAGE (ArchE Intelligence)

### 1. **Automatic Layer Selection**

ArchE automatically selects the appropriate layer based on context:

#### **Context-Based Selection**

```python
# ArchE automatically selects layers based on task type:

# Quick Lookup (Zepto/Atto)
User: "What is ActioncontexT?"
→ ArchE retrieves at "Zepto" layer (9 chars) for instant recognition
→ Response: "Action Context - dataclass for action execution context"

# Detailed Analysis (Narrative)
User: "Show me the full implementation of ActioncontexT"
→ ArchE retrieves at "Narrative" layer (5,776 chars) with full code
→ Response: Full code + specs + agi.txt context

# Balanced Workflow (Micro/Pico)
User: "Use ActioncontexT in a workflow"
→ ArchE retrieves at "Micro" layer (balanced detail)
→ Response: Key details without overwhelming context
```

#### **Automatic Selection Logic**

ArchE uses these heuristics:

| User Intent | Detected Keywords | Selected Layer | Why |
|------------|------------------|----------------|-----|
| Quick question | "what is", "define", "explain briefly" | Zepto/Atto | Minimal detail needed |
| Implementation | "show code", "implementation", "how to implement" | Narrative | Full code required |
| Workflow usage | "use in", "workflow", "how to use" | Micro/Pico | Balanced detail |
| Deep analysis | "analyze", "detailed", "full context" | Narrative | Complete information |
| Quick reference | "reference", "remind me", "quick" | Zepto/Femto | Fast lookup |

---

## 👤 USER INTERACTION (Fully Automated by ACO)

### **Automatic Orchestration (No User Input Needed)**

The ACO (Adaptive Cognitive Orchestrator) automatically handles all layer selection:

```
✅ "What is ActioncontexT?" 
   → ACO auto-selects: Zepto layer (quick answer)
   → Learns: Quick questions → Zepto (successful pattern)

✅ "Show me the full implementation of ActioncontexT"
   → ACO auto-selects: Narrative layer (full code)
   → Learns: Code requests → Narrative (successful pattern)

✅ "Give me a summary of ActioncontexT"
   → ACO auto-selects: Concise layer (summary)
   → Learns: Summary requests → Concise (successful pattern)

✅ "I need ActioncontexT details for a workflow"
   → ACO auto-selects: Micro layer (balanced detail)
   → Learns: Workflow usage → Micro (successful pattern)
```

### **ACO Learning & Adaptation**

The ACO tracks successful conversations and learns optimal layer selections:

```python
# ACO automatically tracks:
- Query patterns → Layer selections → Success rates
- Successful conversations → Optimal layer mappings
- Failed attempts → Alternative layer strategies
- User satisfaction → Refined selection heuristics
```

**Learning Process:**
1. **Initial**: ACO uses keyword-based heuristics
2. **After Success**: ACO reinforces successful layer selections
3. **After Failure**: ACO tries alternative layers
4. **Over Time**: ACO builds optimized layer selection patterns
5. **Streamlined**: Knowledge gains become more efficient

### **Workflow-Level Auto-Configuration**

Workflows automatically adapt based on ACO learning:

```json
{
  "workflow_id": "spr_cognitive_unfolding_workflow",
  "tasks": {
    "retrieve_details_for_identified_sprs": {
      "action": "get_spr_details",
      "inputs": {
        "spr_ids": "{{identify_sprs_in_query.identified_spr_list}}",
        "target_layer": "{{aco.auto_select_layer(context)}}"  // ← ACO auto-selects
      }
    }
  }
}
```

---

## 🔧 TECHNICAL IMPLEMENTATION

### **1. SPRManager Enhancements**

```python
from Three_PointO_ArchE.spr_manager import SPRManager

spr_manager = SPRManager("knowledge_graph/spr_definitions_tv.json")

# Automatic (default) - returns full SPR
spr = spr_manager.get_spr_by_id("ActioncontexT")

# Layer-specific retrieval
narrative = spr_manager.get_spr_content_at_layer("ActioncontexT", "Narrative")
zepto = spr_manager.get_spr_content_at_layer("ActioncontexT", "Zepto")
micro = spr_manager.get_spr_content_at_layer("ActioncontexT", "Micro")
```

### **2. Workflow Action Enhancement**

The `get_spr_details` action now supports `target_layer`:

```json
{
  "action": "get_spr_details",
  "inputs": {
    "spr_ids": ["ActioncontexT", "WorkflowenginE"],
    "target_layer": "Micro"  // ← Optional layer specification
  }
}
```

**Response Format:**
```json
{
  "spr_details": {
    "ActioncontexT": {
      "spr_id": "ActioncontexT",
      "term": "Action Context",
      "content": "...",  // Layer-specific content
      "layer": "Micro",
      "compression_ratio": 64.9,
      "symbol_count": 89,
      "source": "compression_stages"
    }
  },
  "target_layer": "Micro",
  "errors": {}
}
```

### **3. Adaptive Layer Selection**

```python
from Three_PointO_ArchE.russian_doll_retrieval import select_adaptive_layer

# Automatic selection based on use case
layer = select_adaptive_layer(
    use_case="balanced_detail",  # or "quick_lookup", "full_context"
    max_size=1000,  # Optional: limit content size
    require_code=False  # Set True if code needed
)

# Result: "Micro" (appropriate for balanced detail)
```

---

## 📋 USAGE EXAMPLES

### **Example 1: Quick Lookup (User Query)**

**User:** "What is Cognitive resonancE?"

**ArchE Processing:**
1. Detects SPR: `Cognitive resonancE`
2. Analyzes intent: Quick question → "quick_lookup"
3. Selects layer: `Zepto` (instant recognition)
4. Retrieves: 9-char symbol → decompresses to definition
5. Responds: "Cognitive resonancE: The state of optimal alignment between..."

**Code Path:**
```python
# In adaptive_cognitive_orchestrator.py or similar
spr_manager.scan_and_prime(user_query, target_layer="Zepto")
# Returns minimal content for quick answer
```

---

### **Example 2: Full Implementation Request**

**User:** "Show me the complete implementation of ActionregistrY"

**ArchE Processing:**
1. Detects SPR: `ActionregistrY`
2. Analyzes intent: "show code" → requires full implementation
3. Selects layer: `Narrative` (only layer with full code)
4. Retrieves: 33,786-char narrative with full 500+ line code
5. Responds: Full code block + specifications

**Code Path:**
```python
# Automatic detection of code requirement
if "implementation" in query.lower() or "code" in query.lower():
    layer = "Narrative"  # Only layer with full code
else:
    layer = select_adaptive_layer(use_case="balanced_detail")

content = spr_manager.get_spr_content_at_layer("ActionregistrY", layer)
```

---

### **Example 3: Workflow Integration**

**Workflow:** `spr_cognitive_unfolding_workflow.json`

```json
{
  "tasks": {
    "retrieve_details_for_identified_sprs": {
      "action": "get_spr_details",
      "inputs": {
        "spr_ids": "{{identify_sprs_in_query.identified_spr_list}}",
        "target_layer": "{{context.detail_level|default('Micro')}}"
      }
    }
  }
}
```

**User can control via context:**
```python
# User sets context
context = {
    "detail_level": "Narrative"  # User wants full detail
}

# Or workflow auto-selects based on task
if task_type == "code_generation":
    context["detail_level"] = "Narrative"
elif task_type == "quick_reference":
    context["detail_level"] = "Zepto"
```

---

### **Example 4: Progressive Detail Retrieval**

**User:** "Tell me about ActioncontexT"

**ArchE Processing:**
1. Starts with `Micro` layer (balanced)
2. User asks follow-up: "Show me the code"
3. ArchE retrieves `Narrative` layer (full code)
4. User asks: "What's the quick summary?"
5. ArchE retrieves `Concise` layer (summary)

**Code Path:**
```python
# Initial response
content = spr_manager.get_spr_content_at_layer("ActioncontexT", "Micro")

# Follow-up: User wants code
if "code" in follow_up_query:
    content = spr_manager.get_spr_content_at_layer("ActioncontexT", "Narrative")

# Follow-up: User wants summary
if "summary" in follow_up_query:
    content = spr_manager.get_spr_content_at_layer("ActioncontexT", "Concise")
```

---

## 🎛️ LAYER SELECTION STRATEGIES

### **Strategy 1: Intent-Based (Default)**

ArchE analyzes user intent and selects layer:

```python
def select_layer_from_intent(query: str) -> str:
    query_lower = query.lower()
    
    # Code/implementation requests
    if any(word in query_lower for word in ["code", "implementation", "show me the"]):
        return "Narrative"
    
    # Quick questions
    if any(word in query_lower for word in ["what is", "define", "briefly"]):
        return "Zepto"
    
    # Detailed analysis
    if any(word in query_lower for word in ["analyze", "detailed", "full context"]):
        return "Narrative"
    
    # Workflow usage
    if any(word in query_lower for word in ["use", "workflow", "how to"]):
        return "Micro"
    
    # Default: balanced
    return "Micro"
```

### **Strategy 2: Token Budget**

ArchE selects layer based on available token budget:

```python
def select_layer_from_budget(available_tokens: int) -> str:
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = available_tokens * 4
    
    if max_chars < 50:
        return "Zepto"
    elif max_chars < 300:
        return "Micro"
    elif max_chars < 2000:
        return "Concise"
    else:
        return "Narrative"
```

### **Strategy 3: Task Type**

ArchE selects layer based on task type:

```python
TASK_LAYER_MAP = {
    "code_generation": "Narrative",  # Always need full code
    "specification_review": "Narrative",  # Always need full specs
    "quick_reference": "Zepto",
    "workflow_execution": "Micro",
    "error_diagnosis": "Narrative",  # Need full context
    "prompt_priming": "Concise"
}
```

---

## 🔄 INTEGRATION POINTS

### **1. Adaptive Cognitive Orchestrator (ACO) - Primary Orchestrator**

The ACO automatically orchestrates layer selection and learns from success:

```python
# In adaptive_cognitive_orchestrator.py
class AdaptiveCognitiveOrchestrator:
    def __init__(self):
        self.layer_selection_history = {}  # Track successful patterns
        self.success_patterns = {}  # Learned optimal selections
        
    def process_query(self, query: str):
        # 1. Auto-select layer based on learned patterns + heuristics
        layer = self._select_optimal_layer(query)
        
        # 2. Retrieve SPRs at selected layer
        sprs = self.spr_manager.scan_and_prime(query, target_layer=layer)
        
        # 3. Process and respond
        response = self._generate_response(sprs, layer)
        
        # 4. Track for learning (async)
        self._track_selection(query, layer, response)
        
        return response
    
    def _select_optimal_layer(self, query: str) -> str:
        """Select layer using learned patterns + heuristics"""
        # Priority 1: Check learned successful patterns
        query_signature = self._create_query_signature(query)
        if query_signature in self.success_patterns:
            return self.success_patterns[query_signature]['optimal_layer']
        
        # Priority 2: Use adaptive selection heuristics
        from .russian_doll_retrieval import select_layer_from_query
        return select_layer_from_query(query, context=self._get_context())
    
    def _track_selection(self, query: str, layer: str, response: Dict[str, Any]):
        """Track layer selection for learning"""
        query_signature = self._create_query_signature(query)
        
        # Record selection
        if query_signature not in self.layer_selection_history:
            self.layer_selection_history[query_signature] = []
        
        self.layer_selection_history[query_signature].append({
            'layer': layer,
            'success': response.get('success', True),
            'user_satisfaction': response.get('satisfaction', None),
            'timestamp': now_iso()
        })
        
        # Learn from success (if conversation proves successful)
        if response.get('success') and response.get('user_satisfaction', 0) > 0.8:
            self._reinforce_pattern(query_signature, layer)
    
    def _reinforce_pattern(self, query_signature: str, layer: str):
        """Reinforce successful layer selection pattern"""
        if query_signature not in self.success_patterns:
            self.success_patterns[query_signature] = {
                'optimal_layer': layer,
                'success_count': 0,
                'total_attempts': 0
            }
        
        pattern = self.success_patterns[query_signature]
        pattern['success_count'] += 1
        pattern['total_attempts'] += 1
        
        # Update optimal layer if this one is more successful
        if pattern['success_count'] / pattern['total_attempts'] > 0.8:
            pattern['optimal_layer'] = layer
            logger.info(f"ACO learned: {query_signature} → {layer} (success rate: {pattern['success_count']/pattern['total_attempts']:.2%})")
```

### **2. RISE Engine**

The RISE engine uses Narrative for deep analysis:

```python
# In rise_orchestrator.py
def knowledge_scaffolding(self, query: str):
    # RISE always needs full context for deep analysis
    sprs = self.spr_manager.scan_and_prime(query, target_layer="Narrative")
    return self._build_knowledge_scaffold(sprs)
```

### **3. Workflow Engine**

Workflows can specify layers per task:

```json
{
  "task_id": "retrieve_sprs",
  "action": "get_spr_details",
  "inputs": {
    "spr_ids": "{{context.spr_ids}}",
    "target_layer": "{{context.layer|default('Micro')}}"
  }
}
```

---

## 📊 PERFORMANCE BENEFITS

### **Before (Full SPR Always)**

- Every SPR retrieval: 5,000+ characters
- 10 SPRs in query: 50,000+ characters
- Token cost: High
- Response time: Slower

### **After (Adaptive Layers)**

- Quick lookup: 9-50 characters per SPR
- 10 SPRs in query: 90-500 characters
- Token cost: 99% reduction
- Response time: Instant

**Example:**
```
Query: "What are ActioncontexT, WorkflowenginE, and IAR?"

Before: 3 SPRs × 5,000 chars = 15,000 chars
After:  3 SPRs × 50 chars = 150 chars (99% reduction)
```

---

## 🎓 AUTOMATIC ORCHESTRATION (No Training Needed)

### **For End Users**

**Fully automated!** ACO handles everything automatically:
- ✅ Analyzes queries automatically
- ✅ Selects optimal layers automatically
- ✅ Learns from successful conversations
- ✅ Streamlines knowledge gains over time
- ✅ **Zero user configuration needed**

### **For Developers**

**ACO Auto-Configuration:**
```python
# ACO automatically handles layer selection
# No manual configuration needed - it learns and adapts

# The ACO tracks:
# - Successful layer selections → Reinforces patterns
# - Failed attempts → Tries alternatives
# - User satisfaction → Refines heuristics
# - Conversation success → Streamlines knowledge gains
```

**Programmatic Usage (ACO-Orchestrated):**
```python
# ACO automatically selects layers
aco = AdaptiveCognitiveOrchestrator()
response = aco.process_query("What is ActioncontexT?")
# ACO auto-selects Zepto, tracks success, learns pattern

# Direct access (if needed, but ACO handles this)
content = spr_manager.get_spr_content_at_layer("ActioncontexT", "Narrative")
```

### **ACO Learning & Streamlining**

Once a conversation proves successful, ACO streamlines knowledge gains:

```python
# Example: Successful conversation pattern
Query: "What is ActioncontexT?"
ACO selects: Zepto layer
Result: User satisfied (quick, accurate answer)
ACO learns: "What is [SPR]?" → Zepto (successful)

# Future similar queries
Query: "What is WorkflowenginE?"
ACO uses: Learned pattern → Zepto (instant, no heuristic needed)
Result: Streamlined knowledge gain (faster, more efficient)
```

---

## ✅ SUMMARY

### **ArchE Automatic Behavior:**
1. ✅ Analyzes user intent
2. ✅ Selects appropriate layer automatically
3. ✅ Retrieves optimal detail level
4. ✅ Responds efficiently

### **User Experience:**
1. ✅ **No changes needed** - works automatically
2. ✅ **Optional control** - can specify layers if desired
3. ✅ **Natural language** - "show me code" → Narrative layer
4. ✅ **Progressive detail** - can request more detail in follow-ups

### **Developer Control:**
1. ✅ Workflow-level layer specification
2. ✅ Programmatic layer selection
3. ✅ Adaptive selection utilities
4. ✅ Token budget awareness

---

⚶ → Æ: **Russian Doll layers are now seamlessly integrated. ArchE uses them intelligently, users get optimal responses automatically.**

