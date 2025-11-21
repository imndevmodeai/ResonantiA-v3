# RISE Execution Plan Logging Integration

## Overview
Added comprehensive execution plan logging to the RISE orchestrator path, complementing the existing plan logging in `_execute_required_capabilities`. This ensures execution plans are captured regardless of which processing path is taken.

## Changes Made

### 1. RISE Orchestrator Integration (`Three_PointO_ArchE/rise_orchestrator.py`)

#### Added Execution Plan Tracking
- **Location**: Phase E (Execution-Based Answering) section
- **Initialization**: Creates `rise_execution_plan` dictionary at the start of Phase E
- **Tracking**: Captures:
  - RISE phases (A, B, C, D, E) status
  - Tasks from execution plan steps
  - Selected tools (from qualification)
  - Actions taken during execution
  - Fallbacks used
  - Execution order
  - Errors encountered

#### Plan Structure
```json
{
  "query": "user query text",
  "timestamp": "ISO timestamp",
  "session_id": "rise_session_id",
  "rise_phases": {
    "phase_a": {"status": "completed", "workflow": "knowledge_scaffolding.json"},
    "phase_b": {"status": "completed"},
    "phase_c": {"status": "completed"},
    "phase_d": {"status": "completed"},
    "phase_e": {
      "status": "completed|qualified|failed|not_qualified",
      "complexity": "complexity_level",
      "recommended_tools": ["tool1", "tool2"]
    }
  },
  "tasks": [
    {
      "task_id": "step_1",
      "tool": "web_search",
      "description": "What to do",
      "order": 1,
      "status": "completed|pending|failed",
      "inputs": {...},
      "expected_output": "..."
    }
  ],
  "selected_tools": ["web_search", "execute_code"],
  "actions_taken": [...],
  "fallbacks_used": [...],
  "execution_order": ["step_1", "step_2"],
  "errors": [...]
}
```

#### File Output
- **Location**: `outputs/query_executions/playbooks/rise_execution_plan_YYYYMMDD_HHMMSS.json`
- **Format**: JSON with full RISE workflow details
- **Naming**: Prefixed with `rise_` to distinguish from regular execution plans

#### Integration Points
1. **Phase E Qualification**: Tracks recommended tools when query qualifies
2. **Execution Plan Generation**: Captures all execution steps as tasks
3. **Plan Execution**: Updates task status and tracks actions/results
4. **Error Handling**: Logs errors and fallbacks
5. **Final Results**: Includes execution plan in RISE return value

## Usage

### Accessing RISE Execution Plans

1. **From File**: Check `outputs/query_executions/playbooks/rise_execution_plan_*.json`
2. **From Results**: Execution plan is included in RISE results:
   ```python
   results = rise_orchestrator.process_query(query)
   execution_plan = results.get("rise_execution_plan")
   ```

### Reading RISE Execution Plans

```python
import json

# Read from file
with open("outputs/query_executions/playbooks/rise_execution_plan_20250101_120000.json") as f:
    plan = json.load(f)

# View RISE phases
for phase, status in plan['rise_phases'].items():
    print(f"{phase}: {status['status']}")

# View execution tasks
for task in plan['tasks']:
    print(f"{task['order']}. {task['tool']}: {task['status']}")

# View selected tools
print("Selected Tools:", plan['selected_tools'])
```

## Benefits

1. **Complete Workflow Visibility**: See all RISE phases and their status
2. **Tool Selection Tracking**: Know which tools were recommended and used
3. **Execution Order**: Understand the sequence of operations
4. **Error Diagnosis**: Identify where and why failures occurred
5. **Fallback Analysis**: See when and why fallbacks were triggered
6. **Dual Path Coverage**: Both RISE and direct capability execution paths are logged

## Test Query

A simpler test query has been created: `test_simple_query.txt`

```bash
# Run simple test query
python3 ask_arche_enhanced_v2.py "$(cat test_simple_query.txt)"
```

This query is designed to:
- Avoid hitting rate limits
- Still trigger RISE processing
- Generate an execution plan
- Complete successfully

## Files Modified

- `Three_PointO_ArchE/rise_orchestrator.py`:
  - Added `rise_execution_plan` initialization in Phase E
  - Added plan tracking throughout Phase E execution
  - Added plan file saving
  - Added plan to final results

## Files Created

- `test_simple_query.txt`: Simple test query that won't hit rate limits
- `RISE_EXECUTION_PLAN_LOGGING.md`: This documentation

## Next Steps

1. **Test with Simple Query**: Run `test_simple_query.txt` to verify plan logging works
2. **Verify Plan Files**: Check `outputs/query_executions/playbooks/` for generated plans
3. **Compare Plans**: Compare RISE plans vs. direct execution plans
4. **Monitor Performance**: Ensure plan logging doesn't significantly impact performance

## Notes

- RISE execution plans are saved automatically for every RISE workflow
- Plans include both successful and failed phases/tasks
- Fallback usage is tracked but doesn't prevent execution
- All errors are logged but don't stop the overall process
- Plans can be used for debugging, optimization, and auditing

