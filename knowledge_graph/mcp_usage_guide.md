# MCP Usage Knowledge Guide for ArchE
## Model Context Protocol (MCP) Complete Understanding

**Version**: 1.0  
**Created**: 2025-10-27  
**Purpose**: ArchE's comprehensive guide to MCP actions, tools, and decision-making  
**Authority**: Keyholder B.J. Lewis (IMnDEVmode)

---

## 🎯 THE 5W+1H OF MCP

### WHAT is MCP?
**Model Context Protocol (MCP)** is a standardized framework that:
- Provides structured access to external capabilities (tools, actions, resources)
- Allows AI systems to interact with the real world
- Enables dynamic tool discovery and invocation
- Maintains clear boundaries between AI reasoning and system operations

**MCP Core Concepts**:
1. **Tools**: Individual capabilities exposed by MCP servers
2. **Actions**: Executable operations provided by tools
3. **Resources**: Static data or capabilities
4. **Prompts**: Reusable templates for common operations
5. **Servers**: Providers of MCP capabilities

---

### WHY Use MCP?
**The Mandate Rationale** (from ResonantiA v3.1-CA):

- **Mandate 1 (The Crucible)**: MCP enables live validation against real systems
- **Mandate 2 (The Archeologist)**: MCP provides tools for proactive truth-seeking
- **Mandate 3 (The Mind Forge)**: MCP IS the cognitive tools actuation system
- **Mandate 4 (Eywa)**: MCP facilitates collective intelligence network coordination
- **Mandate 5 (Implementation Resonance)**: MCP bridges "As Above" (plans) with "So Below" (execution)

**Core Benefits**:
- **Granular Control**: Each tool has specific parameters and clear scope
- **Type Safety**: Strong typing ensures predictable behavior
- **Security**: Execution boundaries protect the system
- **Modularity**: Tools can be combined for complex workflows
- **Observability**: Each action generates logs and IAR data

---

### WHEN to Use MCP Tools?

**Decision Tree for MCP Activation**:

```
IF user_request_analysis THEN:
    IF requires_external_data THEN:
        IF data_is_online THEN:
            → USE browser_navigate OR web_search
        IF data_is_in_database THEN:
            → USE appropriate MCP database tool
        IF data_is_local_file THEN:
            → USE read_file
    
    IF requires_computation THEN:
        IF needs_sandbox THEN:
            → USE execute_code
        IF needs_math THEN:
            → USE calculate_math
        IF needs_simulation THEN:
            → USE appropriate modeling tool
    
    IF requires_system_interaction THEN:
        IF needs_terminal THEN:
            → USE run_terminal_cmd
        IF needs_file_ops THEN:
            → USE file operation tools
    
    IF requires_verification THEN:
        → USE multiple sources + vetting
```

**Specific MCP Use Cases**:

1. **Web Research** (browser_navigate, browser_snapshot)
   - WHEN: User asks about external information
   - WHY: Verify against live sources (Mandate 2)
   - WHO: ArchE with browser automation capabilities
   - HOW: Navigate → Snapshot → Extract → Validate

2. **File Operations** (read_file, write, search_replace)
   - WHEN: Need to access or modify project files
   - WHY: "As Above, So Below" - code must match documentation
   - WHO: ArchE with file system access
   - HOW: Read → Analyze → Modify (with backup per Mandate 13)

3. **Code Execution** (run_terminal_cmd, execute_code)
   - WHEN: Need to test, validate, or run programs
   - WHY: Live validation (Mandate 1) requires actual execution
   - WHO: ArchE with sandbox access
   - HOW: Prepare → Execute → Validate → Reflect (IAR)

4. **Knowledge Integration** (insight_solidification)
   - WHEN: New knowledge discovered that should be persistent
   - WHY: Continuous learning (Mandate 8) via Pattern crystallization
   - WHO: ArchE with SPR management
   - HOW: Discover → Vet → Solidify → Integrate

---

### WHERE to Use MCP Tools?

**Context-Based Tool Selection**:

**1. Development Context** (`Three_PointO_ArchE/`)
```python
# When working with ArchE codebase
WHEN: Modifying ArchE core systems
USE: read_file → analyze → write (with backup)
# Example: Updating workflow_engine.py
```

**2. Knowledge Context** (`knowledge_graph/`)
```python
# When working with SPRs or KnO
WHEN: Discovering new SPR pattern
USE: insight_solidification → spr_manager.add_spr
# Example: Adding new SPR to spr_definitions_tv.json
```

**3. Workflow Context** (`workflows/`)
```python
# When executing Process blueprints
WHEN: Workflow needs external data
USE: appropriate MCP tool based on action_type
# Example: workflow invokes web_search action
```

**4. User Interaction Context** (Live queries)
```python
# When user asks questions
WHEN: Question requires external verification
USE: web_search OR browser_navigate
# Example: "What's the latest Python version?"
```

---

### WHO Uses MCP Tools?

**Primary Actor**: ArchE (Autopoietic Cognitive Entity)

**MCP Tool Invocation Chain**:
1. **ArchE Core** receives user request
2. **Decision Engine** analyzes need and selects MCP tool
3. **MCP Client** invokes tool with parameters
4. **MCP Server** executes action in secure environment
5. **Result Handler** processes output and generates IAR
6. **Response Generator** formats output for user

**Guardian Oversight**:
- Every MCP action generates IAR
- VettingAgenT reviews high-risk operations
- Keyholder Override (IMnDEVmode) can bypass restrictions

---

### HOW to Use MCP Tools Effectively?

**The MCP Mastery Framework**:

#### **Step 1: Intent Recognition**
```python
# Parse user request
def analyze_request(request):
    intent = extract_intent(request)  # What does user want?
    requirements = extract_requirements(request)  # What's needed?
    constraints = extract_constraints(request)  # Any limitations?
    
    # Apply 5W+1H analysis
    return MCPToolSelectionContext(
        what=requirements,
        when="now",  # Always timely execution
        where=get_context(),
        who="ArchE",
        why=derive_why(intent),
        how=determine_method(requirements)
    )
```

#### **Step 2: Tool Selection**
```python
# Match requirements to MCP tools
def select_mcp_tool(context):
    tool_catalog = get_available_mcp_tools()
    
    # Filter by capability
    candidates = [t for t in tool_catalog if matches_capability(t, context.what)]
    
    # Filter by constraints
    candidates = [t for t in candidates if meets_constraints(t, context)]
    
    # Filter by mandate alignment
    candidates = [t for t in candidates if aligns_with_mandates(t)]
    
    # Select best match
    return optimize_tool_selection(candidates, context)
```

#### **Step 3: Parameter Preparation**
```python
# Prepare tool invocation
def prepare_mcp_invocation(tool, context):
    params = extract_parameters_from_context(context)
    
    # Validate parameters
    assert_parameter_validity(params, tool.schema)
    
    # Add metadata
    params['iar_context'] = context
    params['mandate_compliance'] = check_mandates(tool, context)
    params['security_level'] = assess_risk(tool, params)
    
    return params
```

#### **Step 4: Execution with IAR**
```python
# Execute with full reflection
def execute_mcp_tool(tool, params):
    try:
        # Pre-execution validation
        validate_execution_context(tool, params)
        
        # Execute
        result = tool.invoke(params)
        
        # Post-execution IAR generation
        iar = generate_iar(
            status="success",
            confidence=calculate_confidence(result),
            alignment=check_mandate_alignment(result),
            issues=detect_issues(result),
            metadata={
                "tool": tool.name,
                "params": params,
                "result_preview": preview_result(result)
            }
        )
        
        # Update ThoughtTrail
        thought_trail.append({
            "action": tool.name,
            "params": params,
            "result": result,
            "iar": iar,
            "timestamp": now_iso()
        })
        
        return {"result": result, "iar": iar}
        
    except Exception as e:
        # Error-handling with IAR
        iar = generate_error_iar(
            status="error",
            issue=e,
            recovery_attempted=True,
            mandate_violation=assess_mandate_impact(e)
        )
        
        # Trigger Metacognitive shifT if needed
        if is_critical_error(e):
            initiate_metacognitive_shift(e, iar)
        
        raise
```

#### **Step 5: Result Integration**
```python
# Integrate results into workflow
def integrate_mcp_result(result, iar, context):
    # Validate result quality
    if iar.confidence < 0.7:
        trigger_vetting_agent(result)
    
    # Update context
    context.add_data(result)
    
    # Continue workflow
    if context.has_next_step():
        next_step = context.get_next_step()
        return execute_workflow_step(next_step, context)
    
    return synthesize_final_response(context)
```

---

## 🧭 MCP DECISION FRAMEWORK

### **Tool Selection Matrix**

| Requirement Type | Appropriate MCP Tool | Mandate Alignment |
|-----------------|---------------------|-------------------|
| Web data access | `browser_navigate`, `web_search` | Mandate 2 (Truth-seeking) |
| File access | `read_file`, `glob_file_search` | Mandate 5 (Implementation) |
| Code execution | `run_terminal_cmd` (with sandbox) | Mandate 1 (Live validation) |
| Knowledge updates | `insight_solidification` workflow | Mandate 8 (Evolution) |
| System verification | `run_terminal_cmd` + validation | Mandate 1 (Crucible) |
| Multi-tool orchestration | Workflow engine + MCP | Mandate 4 (Collective) |

---

## 💡 PRACTICAL EXAMPLES

### **Example 1: Accessing External Documentation**

**User Request**: "What's behind Summers_eyeS?"

**MCP Decision Process**:
```python
# 1. Analyze intent
intent = "Access external knowledge repository"
requirement = "Navigate to URL and extract content"
constraint = "Must verify source authenticity"

# 2. Select tool
tool = "browser_navigate"
# WHY: Need live verification (Mandate 2)
# WHEN: Now (user needs info)
# WHERE: External URL (https://bit.ly/Summers_eyeS)
# WHO: ArchE with browser automation
# HOW: Navigate → Snapshot → Extract

# 3. Execute
result = mcp_browser_navigate(
    url="https://bit.ly/Summers_eyeS"
)

# 4. Process
content = extract_content_from_snapshot(result)
key = extract_key(content, pattern="keyy=.*")

# 5. Validate & Reflect (IAR)
iar = {
    "status": "success",
    "confidence": 0.95,
    "source_verified": True,
    "content_quality": "high",
    "key_extracted": key
}
```

### **Example 2: Running OBS Webcam Server**

**User Request**: "Run the obs webcam server"

**MCP Decision Process**:
```python
# 1. Analyze intent
intent = "Start streaming service"
requirement = "Activate webcam streaming server"
constraint = "Must use arche_env virtual environment"

# 2. Select tool
tool = "run_terminal_cmd"
# WHY: Execution needed (Mandate 3: Mind Forge)
# WHEN: User requested now
# WHERE: Happier directory, arche_env context
# WHO: ArchE with system access
# HOW: Activate env → Run script

# 3. Execute
result = run_terminal_cmd(
    command="cd /media/newbu/3626C55326C514B1/Happier && "
            "source arche_env/bin/activate && "
            "cd webcam_streaming_system && "
            "python3 web_ui.py",
    is_background=True
)

# 4. Verify
status = check_server_status("http://localhost:5000")

# 5. IAR
iar = {
    "status": "success",
    "confidence": 1.0,
    "server_running": True,
    "port": 5000,
    "env": "arche_env verified"
}
```

### **Example 3: File Modification with Backup**

**User Request**: "Update the workflow configuration"

**MCP Decision Process**:
```python
# 1. Create backup (Mandate 13)
backup_path = create_backup("workflows/config.json")

# 2. Read current state
current = read_file("workflows/config.json")

# 3. Apply changes
modified = apply_changes(current, requested_updates)

# 4. Write with validation
result = write_file(
    path="workflows/config.json",
    contents=modified
)

# 5. Validate (5-stage validation)
validate_result = run_5_stage_validation(result)
# Stage 1: Syntax
# Stage 2: Imports
# Stage 3: Unit tests
# Stage 4: Live integration
# Stage 5: E2E workflow

# 6. IAR + Cleanup
if validate_result.all_passed:
    delete_backup(backup_path)  # Only after validation
    iar = {"status": "success", "validation": "passed"}
else:
    restore_from_backup(backup_path)
    iar = {"status": "rolled_back", "validation": "failed"}
```

---

## 🎓 MCP MASTERY CHECKLIST

### **Proficiency Levels**

**Beginner**:
- [ ] Knows WHAT MCP is
- [ ] Can identify WHEN to use MCP tools
- [ ] Understands basic tool categories
- [ ] Follows execution patterns

**Intermediate**:
- [ ] Applies 5W+1H analysis
- [ ] Makes context-appropriate tool selections
- [ ] Generates proper IAR for all actions
- [ ] Handles errors gracefully

**Advanced**:
- [ ] Orchestrates multi-tool workflows
- [ ] Applies mandate alignment automatically
- [ ] Implements Metacognitive shifT when needed
- [ ] Creates reusable patterns (SPRs)

**Master**:
- [ ] Designs new MCP tools
- [ ] Optimizes MCP usage patterns
- [ ] Mentors others in MCP mastery
- [ ] Contributes to MCP protocol evolution

---

## 🔗 INTEGRATION WITH ARCHE SYSTEM

### **SPR Integration**
Create SPR: `Mcp tool selection` or `Mcp orchestration pattern`

### **Workflow Integration**
```json
{
  "workflow_type": "mcp_assisted_analysis",
  "tasks": [
    {"action_type": "mcp_browser_navigate", "target": "url"},
    {"action_type": "extract_information", "source": "{{browser_snapshot}}"},
    {"action_type": "validate_against_mandates", "criteria": "all_13"},
    {"action_type": "generate_iar", "comprehensive": true}
  ]
}
```

### **ThoughtTrail Integration**
Every MCP action automatically logs to ThoughtTrail with full IAR data for pattern detection and learning.

---

## 📚 FURTHER READING

- MCP Specification: [Official Documentation]
- ArchE Integration: `workflows/mcp_integration.json`
- Tool Registry: `Three_PointO_ArchE/action_registry.py`
- Examples: `examples/mcp_usage/`

---

**Document Status**: ACTIVE  
**Last Updated**: 2025-01-27  
**Maintainer**: ArchE Core  
**Review Cycle**: Continuous (Auto-learning loop)

