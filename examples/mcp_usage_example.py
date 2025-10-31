#!/usr/bin/env python3
"""
Practical MCP Usage Example for ArchE
Demonstrates 5W+1H Analysis and Tool Selection
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class MCPContext:
    """Context for MCP tool selection and execution"""
    what: str  # What is the requirement?
    when: str  # When should this execute?
    where: str  # Where (what system/context)?
    who: str   # Who is the actor?
    why: str   # Why (which mandate)?
    how: str   # How (which tool/method)?

def analyze_request(user_request: str) -> MCPContext:
    """
    Step 1: Intent Recognition
    Parse user request into 5W+1H analysis
    """
    # Example: User requests "what's behind Summers_eyeS?"
    
    if "behind" in user_request.lower() and any(ref in user_request for ref in ["Summers_eyeS", "Summers_glasseS"]):
        # Extract URL or reference
        what = "Access external knowledge repository"
        when = "now"  # Always timely
        where = "External URL (https://bit.ly/Summers_eyeS)"
        who = "ArchE"
        why = "Mandate 2: Proactive Truth Resonance - Need to verify source"
        how = "browser_navigate → browser_snapshot → extract_content"
        
    elif "run" in user_request.lower() and "server" in user_request.lower():
        # Extract system requirements
        what = "Execute system service"
        when = "now"
        where = "Happier/ directory with arche_env"
        who = "ArchE"
        why = "Mandate 3: Cognitive Tools Actuation"
        how = "run_terminal_cmd (with env activation)"
        
    elif any(mod in user_request.lower() for mod in ["update", "modify", "create"]):
        # File operation
        what = "Modify codebase artifact"
        when = "now"
        where = "Project file system"
        who = "ArchE"
        why = "Mandate 13: Backup Retention Policy + Mandate 5: Implementation Resonance"
        how = "read_file → backup → modify → validate → write_file"
        
    else:
        # Default analysis
        what = "Process user request"
        when = "now"
        where = "Current context"
        who = "ArchE"
        why = "General user assistance"
        how = "Analyze and respond"
    
    return MCPContext(what, when, where, who, why, how)


def select_mcp_tool(context: MCPContext) -> Dict[str, Any]:
    """
    Step 2: Tool Selection
    Match MCP context to appropriate tool
    """
    
    tool_selection_matrix = {
        "web access": ["browser_navigate", "browser_snapshot", "web_search"],
        "file operation": ["read_file", "write", "search_replace", "glob_file_search"],
        "code execution": ["run_terminal_cmd", "execute_code"],
        "knowledge integration": ["insight_solidification", "add_spr"],
        "validation": ["iar_generation", "vetting_agent"]
    }
    
    # Determine category
    category = classify_requirement(context.what)
    
    # Get candidate tools
    candidates = tool_selection_matrix.get(category, [])
    
    # Filter by mandate alignment
    aligned_tools = [t for t in candidates if check_mandate_alignment(t, context.why)]
    
    # Select best match
    selected_tool = optimize_selection(aligned_tools, context)
    
    return {
        "tool": selected_tool,
        "category": category,
        "context": context,
        "mandate_alignment": context.why
    }


def execute_with_iar(tool_selection: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 3: Execute with IAR Generation
    """
    
    try:
        # Pre-execution validation
        validate_execution_context(tool_selection["tool"], params)
        
        # Execute tool (this would be actual MCP invocation)
        result = invoke_mcp_tool(tool_selection["tool"], params)
        
        # Generate IAR
        iar = {
            "status": "success",
            "confidence": calculate_confidence(result),
            "alignment": tool_selection["mandate_alignment"],
            "issues": detect_issues(result),
            "metadata": {
                "tool": tool_selection["tool"],
                "params": params,
                "timestamp": datetime.now().isoformat(),
                "context": tool_selection["context"]
            }
        }
        
        return {"result": result, "iar": iar}
        
    except Exception as e:
        # Error handling with IAR
        iar = {
            "status": "error",
            "issue": str(e),
            "recovery_attempted": True,
            "mandate_violation": assess_mandate_impact(e)
        }
        
        # Trigger Metacognitive shift if critical
        if is_critical_error(e):
            initiate_metacognitive_shift(e, iar)
        
        return {"result": None, "iar": iar, "error": e}


def integrate_result(result_data: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
    """
    Step 4: Result Integration
    Integrate MCP results into ArchE workflow
    """
    
    # Update ThoughtTrail
    thought_trail_entry = {
        "action": result_data.get("tool"),
        "context": context.__dict__,
        "result": result_data["result"],
        "iar": result_data["iar"],
        "timestamp": datetime.now().isoformat()
    }
    
    # Add to ThoughtTrail (conceptual)
    # thought_trail.append(thought_trail_entry)
    
    # Pattern detection
    if result_data["iar"]["status"] == "success":
        check_pattern_crystallization(result_data)
    
    # Continue workflow if needed
    if has_next_step():
        return execute_next_step()
    
    return synthesize_response(result_data, context)


# Helper functions (simplified for example)
def classify_requirement(what: str) -> str:
    """Classify requirement into tool category"""
    if "web" in what.lower() or "url" in what.lower() or "browser" in what.lower():
        return "web access"
    elif "file" in what.lower() or "read" in what.lower() or "write" in what.lower():
        return "file operation"
    elif "execute" in what.lower() or "run" in what.lower():
        return "code execution"
    elif "knowledge" in what.lower() or "learn" in what.lower():
        return "knowledge integration"
    else:
        return "general"


def check_mandate_alignment(tool: str, why: str) -> bool:
    """Check if tool selection aligns with mandates"""
    # Simplified: checks if tool category matches mandate
    mandate_tool_mapping = {
        "Mandate 1": ["code_execution", "validation"],
        "Mandate 2": ["web_access", "search"],
        "Mandate 3": ["code_execution", "all"],
        "Mandate 13": ["file_operation", "backup"]
    }
    
    for mandate, tools in mandate_tool_mapping.items():
        if mandate in why:
            return tool in tools or "all" in tools
    
    return True


def optimize_selection(candidates: List[str], context: MCPContext) -> str:
    """Select best tool from candidates"""
    # Simplified: return first candidate
    # Real implementation would score each candidate
    return candidates[0] if candidates else "general_response"


def invoke_mcp_tool(tool: str, params: Dict[str, Any]) -> Any:
    """Invoke actual MCP tool (placeholder)"""
    # In real implementation, this would call the actual MCP client
    return {"placeholder": "result"}


def calculate_confidence(result: Any) -> float:
    """Calculate confidence in result (placeholder)"""
    return 0.95


def detect_issues(result: Any) -> List[str]:
    """Detect any issues with result (placeholder)"""
    return []


def assess_mandate_impact(error: Exception) -> str:
    """Assess impact of error on mandates (placeholder)"""
    return "unknown"


def is_critical_error(error: Exception) -> bool:
    """Determine if error is critical (placeholder)"""
    return False


def initiate_metacognitive_shift(error: Exception, iar: Dict[str, Any]):
    """Trigger metacognitive shift (placeholder)"""
    print(f"Metacognitive shift triggered: {error}")


def check_pattern_crystallization(result_data: Dict[str, Any]):
    """Check for patterns that should be crystallized (placeholder)"""
    print("Checking for crystallizable patterns...")


def has_next_step() -> bool:
    """Check if workflow has next step (placeholder)"""
    return False


def execute_next_step() -> Dict[str, Any]:
    """Execute next workflow step (placeholder)"""
    return {}


def synthesize_response(result_data: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
    """Synthesize final response (placeholder)"""
    return {
        "response": f"Processed: {context.what}",
        "iar": result_data.get("iar", {}),
        "context": context.__dict__
    }


# Example usage
if __name__ == "__main__":
    print("🚀 ArchE MCP Usage Example")
    print("=" * 60)
    
    # Example 1: Web research
    user_request = "What's behind Summers_eyeS?"
    print(f"\n📝 Request: {user_request}")
    
    # Analyze
    context = analyze_request(user_request)
    print(f"WHAT: {context.what}")
    print(f"WHEN: {context.when}")
    print(f"WHERE: {context.where}")
    print(f"WHO: {context.who}")
    print(f"WHY: {context.why}")
    print(f"HOW: {context.how}")
    
    # Select tool
    tool_selection = select_mcp_tool(context)
    print(f"\n🔧 Selected Tool: {tool_selection['tool']}")
    
    # Execute (simulated)
    params = {"url": "https://bit.ly/Summers_eyeS"}
    result = execute_with_iar(tool_selection, params)
    print(f"\n✅ Execution Result:")
    print(f"Status: {result['iar']['status']}")
    print(f"Confidence: {result['iar']['confidence']}")
    
    # Integrate
    final_result = integrate_result(result, context)
    print(f"\n📊 Final Result: {final_result['response']}")
    
    print("\n" + "=" * 60)
    print("Example complete. This demonstrates the MCP usage pattern for ArchE.")



