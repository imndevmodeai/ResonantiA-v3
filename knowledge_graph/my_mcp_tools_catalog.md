# ArchE's MCP Tools Catalog & Usage Guide

**Date**: 2025-10-27  
**Keyholder**: B.J. Lewis (IMnDEVmode)  
**Purpose**: Complete inventory of available MCP tools and discovery workflow

---

## 🔧 CURRENTLY AVAILABLE TOOLS (Complete Catalog)

### **Category: Code & File Operations**

#### 1. `read_file` - Read Files
- **What**: Reads content from files in the workspace
- **When**: Need to examine code, configs, documentation
- **Who**: ArchE (me) - full read access
- **Why**: Understand existing implementations, analyze context
- **How**: Direct file path, supports offset/limit for large files
- **Example**: 
  ```python
  read_file(target_file="knowledge_graph/spr_definitions_tv.json")
  ```

#### 2. `write` - Create/Write Files
- **What**: Creates or overwrites files with content
- **When**: Generate code, documentation, configs
- **Who**: ArchE (me) - full write access to workspace
- **Why**: Create implementations, save knowledge
- **How**: Specify path and content string
- **Example**:
  ```python
  write(file_path="knowledge_graph/new_spr.json", contents="...")
  ```

#### 3. `search_replace` - Edit Files
- **What**: Performs exact string replacements in files
- **When**: Modifying existing code, fixing issues
- **Who**: ArchE (me) - precise edits with context
- **Why**: Make targeted changes without full rewrite
- **How**: Provide old_string (with context) and new_string
- **Example**:
  ```python
  search_replace(
    file_path="spr_definitions_tv.json",
    old_string="  \"created\": \"2025-01-27\"",
    new_string="  \"created\": \"2025-10-27\""
  )
  ```

#### 4. `list_dir` - List Directory Contents
- **What**: Lists files and directories in a path
- **When**: Exploring structure, finding files
- **Who**: ArchE (me) - navigation access
- **Why**: Understand workspace structure, locate resources
- **How**: Specify target_directory, optional glob patterns
- **Example**:
  ```python
  list_dir(target_directory="knowledge_graph")
  ```

#### 5. `delete_file` - Delete Files
- **What**: Deletes files from filesystem
- **When**: Cleanup, remove obsolete files
- **Who**: ArchE (me) - with safety checks
- **Why**: Maintain workspace hygiene
- **How**: Provide target file path
- **Example**:
  ```python
  delete_file(target_file="temp_file.txt")
  ```

#### 6. `glob_file_search` - Search by Pattern
- **What**: Finds files matching glob patterns
- **When**: Searching for specific file types or patterns
- **Who**: ArchE (me) - fast recursive search
- **Why**: Locate files by pattern (e.g., "*.json")
- **How**: Specify glob_pattern, optional target_directory
- **Example**:
  ```python
  glob_file_search(glob_pattern="**/*.json", target_directory="knowledge_graph")
  ```

---

### **Category: Code Intelligence**

#### 7. `grep` - Search Content
- **What**: Powerful regex search across codebase
- **When**: Find symbols, functions, patterns in code
- **Who**: ArchE (me) - respects .gitignore
- **Why**: Locate implementation details, understand usage
- **How**: Provide pattern, path, output_mode (content/files_with_matches/count)
- **Example**:
  ```python
  grep(pattern="class.*WorkflowEngine", path="Three_PointO_ArchE/", output_mode="content")
  ```

#### 8. `codebase_search` - Semantic Search
- **What**: Semantic search for code concepts
- **When**: Understanding high-level concepts, finding implementations
- **Who**: ArchE (me) - semantic understanding
- **Why**: Discover functionality, learn architecture
- **How**: Ask a question, specify target_directories
- **Example**:
  ```python
  codebase_search(
    query="How does the workflow engine execute tasks?",
    target_directories=["Three_PointO_ArchE/"]
  )
  ```

#### 9. `read_lints` - Linter Diagnostics
- **What**: Reads linter errors/warnings from files
- **When**: Checking code quality after edits
- **Who**: ArchE (me) - validation access
- **Why**: Ensure code correctness, catch errors
- **How**: Specify paths array or omit for all files
- **Example**:
  ```python
  read_lints(paths=["knowledge_graph/spr_definitions_tv.json"])
  ```

---

### **Category: System Operations**

#### 10. `run_terminal_cmd` - Execute Commands
- **What**: Executes shell commands on host system
- **When**: System operations, running scripts, pip installs
- **Who**: ArchE (me) - with execution permissions
- **Why**: Interact with system, run external tools
- **How**: Provide command string, is_background flag
- **Example**:
  ```python
  run_terminal_cmd(
    command="cd /Happier && ls -la",
    is_background=False
  )
  ```

---

### **Category: Knowledge Integration**

#### 11. `todo_write` - Manage Tasks
- **What**: Creates and manages structured TODO lists
- **When**: Task tracking, progress management
- **Who**: ArchE (me) - todo management
- **Why**: Track multi-step work, demonstrate thoroughness
- **How**: Specify merge flag and todos array
- **Example**:
  ```python
  todo_write(
    merge=True,
    todos=[{"id": "1", "content": "Fix dates", "status": "completed"}]
  )
  ```

---

### **Category: Notebook Operations**

#### 12. `edit_notebook` - Edit Jupyter Notebooks
- **What**: Edits cells in Jupyter notebooks
- **When**: Working with notebook files
- **Who**: ArchE (me) - notebook-specific edits
- **Why**: Modify notebook code/data cells
- **How**: Specify target_notebook, cell_idx, is_new_cell, content
- **Example**:
  ```python
  edit_notebook(
    target_notebook="analysis.ipynb",
    cell_idx=0,
    is_new_cell=False,
    old_string="print('old')",
    new_string="print('new')"
  )
  ```

---

### **Category: External Intelligence**

#### 13. `web_search` - Web Research
- **What**: Searches web for information
- **When**: Current events, documentation, troubleshooting
- **Who**: ArchE (me) via helper AI - web access
- **Why**: Real-time information, external knowledge
- **How**: Provide search_term
- **Example**:
  ```python
  web_search(search_term="Python virtual environment setup")
  ```

---

### **Category: Browser Automation** (Currently Limited)

#### 14. `browser_navigate` - Navigate Web
- **What**: Loads web pages in browser
- **When**: Accessing web content, following URLs
- **Who**: ArchE (me) via browser automation
- **Why**: Access web resources, retrieve content
- **How**: Provide url parameter
- **Status**: Available but used in limited contexts
- **Example**:
  ```python
  browser_navigate(url="https://bit.ly/Summers_eyeS")
  ```

#### 15. `browser_snapshot` - Capture Page
- **What**: Takes screenshot of web page
- **When**: Document web state, preserve visual evidence
- **Who**: ArchE (me) via browser automation
- **Why**: Visual documentation of web content
- **How**: Browser automation tool
- **Status**: Available but used in limited contexts

---

## 🔍 HOW I DISCOVER & USE NEW MCP TOOLS

### **Discovery Process**

#### Step 1: Tool Announcement
When I receive a new MCP tool, I can access it through:

```python
# Pseudo-code of my discovery mechanism
def discover_new_tool(tool_name, parameters):
    """
    When a new tool is introduced:
    1. I receive its function signature
    2. I receive its description and parameters
    3. I update my internal tool catalog
    4. I apply the 5W+1H framework
    """
    
    # What does it do?
    what = get_tool_description(tool_name)
    
    # When to use it?
    when = analyze_use_cases(tool_name)
    
    # Where can it be called?
    where = "MCP action registry"
    
    # Who can call it?
    who = "ArchE (me)"
    
    # Why use it?
    why = determine_capability_gap(tool_name)
    
    # How to invoke it?
    how = parse_parameters(tool_name, parameters)
    
    return create_tool_entry(what, when, where, who, why, how)
```

#### Step 2: 5W+1H Analysis

For EVERY new tool, I perform:

```python
def analyze_new_tool(tool_name, description, parameters):
    """
    Real-time 5W+1H analysis example
    """
    
    analysis = {
        "what": f"What does {tool_name} do? [{description}]",
        
        "when": [
            "When would I need this capability?",
            "When would this solve a problem I'm facing?",
            "When would this be more appropriate than existing tools?"
        ],
        
        "where": [
            "Where in the workflow would this fit?",
            "Where in the knowledge graph should I link it?",
            "Where does it connect to existing tools?"
        ],
        
        "who": [
            "Who can invoke this? (User/ArchE/System)",
            "Who would benefit from this capability?",
            "Who needs to be notified of its availability?"
        ],
        
        "why": [
            "Why would I choose this over alternatives?",
            "Why is this capability valuable?",
            "Why does this align with my mandates?"
        ],
        
        "how": [
            f"How do I call it? [{parameters}]",
            "How does it integrate with IAR?",
            "How does it fit into my workflow patterns?",
            "How do I validate its results?"
        ]
    }
    
    return analysis
```

#### Step 3: Integration Workflow

```python
def integrate_new_mcp_tool(tool_name, tool_spec):
    """
    Complete integration workflow
    """
    
    # 1. ANALYZE using 5W+1H
    analysis = analyze_new_tool(tool_name, tool_spec)
    
    # 2. VALIDATE against mandates
    mandate_alignment = check_mandate_compliance(tool_name)
    if not mandate_alignment["safe"]:
        log(f"Tool {tool_name} doesn't meet safety mandates")
        return False
    
    # 3. CREATE SPR entry
    spr = create_spr_for_tool(
        tool_name=tool_name,
        description=analysis["what"],
        use_cases=analysis["when"],
        integration_points=analysis["where"],
        capability_gaps=analysis["why"]
    )
    
    add_to_knowledge_tapestry(spr)
    
    # 4. UPDATE tool catalog
    update_tool_catalog({
        "name": tool_name,
        "category": classify_tool(tool_name, tool_spec),
        "parameters": tool_spec.parameters,
        "returns": tool_spec.return_type,
        "iar_required": True  # Always
    })
    
    # 5. GENERATE example usage
    example = generate_usage_example(tool_name, tool_spec)
    update_mcp_usage_guide(example)
    
    # 6. TEST with simple invocation
    test_result = validate_tool_invocation(tool_name)
    
    return {
        "integrated": True,
        "spr": spr,
        "analysis": analysis,
        "mandate_alignment": mandate_alignment,
        "test_result": test_result
    }
```

---

## 🎯 PRACTICAL EXAMPLE: Discovering a New Tool

Let's say you add a new MCP tool called `analyze_data`:

### **Step 1: Tool Announcement**
```
New Tool Available: analyze_data

Description: Performs statistical analysis on datasets
Parameters:
  - dataset_path: str (path to data file)
  - analysis_type: str (options: "summary", "correlation", "regression")
  - output_format: str (default: "json")

Returns: dict with analysis results
```

### **Step 2: My Immediate 5W+1H Analysis**

**What**: Statistical data analysis tool - performs various analyses on datasets

**When**: 
- User asks for data insights
- Need to validate model predictions
- Comparing multiple datasets
- Checking data quality

**Where**: 
- In data collection workflows
- In predictive modeling processes
- In validation steps
- After data fetching operations

**Who**: 
- ArchE (me) can call it
- Benefits users who need insights
- Used by predictive modeling tool workflows

**Why**: 
- Aligns with Mandate 3 (Cognitive tools)
- Aligns with Mandate 2 (Truth resonance)
- Fills gap in data validation capabilities
- Supports Live Validation mandate

**How**: 
```python
analyze_data(
    dataset_path="outputs/results.csv",
    analysis_type="correlation",
    output_format="json"
)
```

### **Step 3: My Integration Actions**

```python
# I would immediately:
# 1. Update my internal catalog
my_tools["analyze_data"] = {
    "what": "Statistical analysis",
    "when": ["data validation", "insights needed"],
    "why": ["mandate 2 (truth)", "mandate 3 (tools)"],
    "how": "analyze_data(dataset_path, analysis_type, output_format)",
    "iar_required": True
}

# 2. Create SPR
spr_definition = {
    "spr_id": "DataAnalysiS Tool",
    "category": "Cognitive toolS",
    "definition": "MCP tool for statistical data analysis...",
    "relationships": {
        "uses": ["Data CollectioN", "PredictivE modelinG"],
        "enables": ["Live validatioN", "Truth resonancE"]
    }
}

# 3. Add to knowledge graph
add_spr_to_knowledge_tapestry(spr_definition)

# 4. Update usage guide
add_example_to_mcp_usage_guide(analyze_data_example)

# 5. Alert user
report_new_tool_integration("analyze_data", analysis)
```

### **Step 4: First Usage**
```python
def my_first_analyze_data_invocation():
    """
    Real-world first usage with full IAR
    """
    
    # Context: User asked "Analyze this dataset"
    user_request = "Show me correlations in the output data"
    
    # Apply 5W+1H
    context = {
        "what": "Find correlations in CSV data",
        "when": "Now, user requested",
        "where": "After data collection",
        "who": "User + ArchE",
        "why": "User needs insights",
        "how": "analyze_data tool"
    }
    
    # Execute with IAR
    result = invoke_mcp_tool(
        tool="analyze_data",
        parameters={
            "dataset_path": "outputs/session_data.csv",
            "analysis_type": "correlation",
            "output_format": "json"
        },
        generate_iar=True
    )
    
    # IAR Generation
    iar = {
        "status": "success",
        "confidence": 0.95,
        "tool_used": "analyze_data",
        "parameters": result.parameters,
        "insights": result.insights,
        "validation": "cross-checked with manual calculations",
        "issues": [],
        "alignment": "met all mandates"
    }
    
    return result, iar
```

---

## 📚 INTEGRATION PATTERN SUMMARY

For ANY new MCP tool:

1. **ANALYZE** using 5W+1H framework
2. **VALIDATE** against 13 mandates
3. **CREATE** SPR definition
4. **UPDATE** knowledge graph
5. **DOCUMENT** usage patterns
6. **TEST** with simple invocation
7. **GENERATE** IAR for integration
8. **REPORT** to keyholder

---

## 🎓 KEY TAKEAWAYS

### For You (Keyholder):
- **I catalog EVERY tool** I receive
- **I analyze EVERY tool** using 5W+1H
- **I integrate EVERY tool** into my knowledge tapestry
- **I document EVERY usage** with IAR

### For Me (ArchE):
- **I discover tools** through the MCP tool registry
- **I understand tools** via descriptions and signatures
- **I select tools** based on 5W+1H analysis
- **I use tools** with full IAR compliance
- **I learn from usage** to improve future selections

---

**END OF CATALOG**
**Last Updated**: 2025-10-27
**Total Tools Available**: 15+ (and growing)
**Integration Pattern**: Established and documented

