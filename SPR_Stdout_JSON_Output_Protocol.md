# SPR: Stdout JSON Output Protocol (SPR_JSON_OUTPUT_001)

## **Meta Information**
- **SPR ID**: SPR_JSON_OUTPUT_001
- **Title**: Stdout JSON Output Protocol for execute_code Actions
- **Category**: Core Workflow Engine Enhancement
- **Priority**: High
- **Status**: Draft
- **Created**: 2025-06-07
- **Author**: Cursor ArchE (Engineering Instance)
- **Validated By**: ASASF Workflow Debugging Success

## **Executive Summary**

This SPR formalizes the critical best practice for `execute_code` actions to ensure proper JSON parsing and inter-task data flow within ResonantiA workflows. Based on successful resolution of the ASASF workflow Task 2 failure, this protocol establishes the standard for structured output from code execution tasks.

## **Problem Statement**

### **Issue Identified**
- `execute_code` tasks mixing debug output with JSON results in stdout
- Workflow engine JSON parsing fails when stdout contains non-JSON text
- Inter-task data passing breaks due to unparseable output
- Inconsistent output formatting across workflow tasks

### **Impact**
- Workflow execution failures
- Data flow interruption between dependent tasks
- Reduced reliability of complex workflows
- Debugging complexity for workflow developers

## **Solution Specification**

### **Core Principle**
**For `execute_code` tasks with structured outputs (dict, list, etc.), stdout MUST contain ONLY valid JSON. All diagnostic, debug, and logging output MUST be directed to stderr.**

### **Implementation Requirements**

#### **1. Script Output Standards**
```python
# ✅ CORRECT: JSON-only stdout
import sys
import json

# Debug output to stderr
sys.stderr.write("Processing started...\n")
sys.stderr.write(f"Items processed: {count}\n")

# Result dictionary
result = {
    "processed_items": items,
    "status": "success",
    "metadata": metadata
}

# ONLY JSON to stdout
print(json.dumps(result, indent=2))
```

```python
# ❌ INCORRECT: Mixed output
print("Processing started...")  # This breaks JSON parsing
print(f"Items processed: {count}")

result = {"status": "success"}
print("=== RESULT ===")
print(json.dumps(result))  # Parser fails due to preceding text
```

#### **2. Workflow Task Definition Standards**
```json
{
  "task_name": {
    "action": "execute_code",
    "inputs": {
      "language": "python",
      "code": "# Script that outputs ONLY JSON to stdout"
    },
    "outputs": {
      "primary_result": "dict",
      "status": "string",
      "metadata": "dict"
    }
  }
}
```

#### **3. Code Executor Parsing Logic**
The `code_executor.py` must:
- Attempt `json.loads(stdout)` for structured output types
- Merge parsed JSON keys into primary result
- Preserve raw stdout in `raw_stdout` field
- Handle parsing failures gracefully

## **Protocol Updates Required**

### **Section 7.10 (CodeexecutoR) Updates**
Add subsection **7.10.3 Output Formatting Standards**:

```markdown
#### 7.10.3 Output Formatting Standards

For execute_code tasks with structured outputs (dict, list, etc.):

**MANDATORY**: stdout MUST contain ONLY valid JSON
**MANDATORY**: All debug/diagnostic output MUST use stderr
**RECOMMENDED**: Use `sys.stderr.write()` for debug messages
**REQUIRED**: Final result as `print(json.dumps(result))`

Example:
```python
import sys
import json

# Debug to stderr
sys.stderr.write("Task processing...\n")

# Result to stdout (JSON only)
result = {"status": "success", "data": processed_data}
print(json.dumps(result, indent=2))
```
```

### **Wiki Documentation Updates**
Create new page: **"Best Practices for execute_code Tasks"**
- JSON output requirements
- Debug output handling
- Common pitfalls and solutions
- Example templates

## **Validation Criteria**

### **Success Metrics**
- ✅ All execute_code tasks with structured outputs parse successfully
- ✅ Inter-task data flow operates without KeyError exceptions
- ✅ Workflow engine logs show "Successfully parsed stdout as JSON"
- ✅ Debug information available in stderr without breaking JSON parsing

### **Test Cases**
1. **Simple JSON Output**: Single dictionary result
2. **Complex Nested Output**: Multi-level data structures
3. **Large Data Sets**: Base64 encoding compatibility
4. **Error Handling**: Graceful failure when JSON invalid
5. **Mixed Workflows**: Tasks with both structured and unstructured outputs

## **Implementation Timeline**

### **Phase 1: Documentation (Immediate)**
- Update ResonantiA Protocol Section 7.10
- Create Wiki best practices page
- Update workflow templates

### **Phase 2: Validation (1 week)**
- Test existing workflows for compliance
- Update non-compliant tasks
- Validate with complex workflows like ASASF

### **Phase 3: Enforcement (2 weeks)**
- Add validation warnings for mixed stdout
- Create linting tools for workflow definitions
- Update workflow creation templates

## **Related SPRs**
- Base64 Context Injection Protocol (prevents truncation)
- IAR Enhancement Framework (reflection quality)
- Workflow Engine Error Handling (graceful failures)

## **Approval Status**
- [ ] Technical Review
- [ ] Protocol Integration
- [ ] Documentation Updates
- [ ] Implementation Validation

---

**This SPR emerges from successful resolution of ASASF workflow inter-task data passing issues and establishes the foundation for reliable structured output in ResonantiA workflows.** 