# Log Naming Conventions for ArchE/RISE Framework

## Current Problems

The current log system has several critical issues:

1. **Random UUIDs**: Files like `run_events_run_7725e79e4560421684938b9b500465ed.jsonl` provide no context
2. **No hierarchy**: All logs dumped into flat `outputs/` directory
3. **No metadata**: No way to understand what a log contains without opening it
4. **No searchability**: Impossible to find specific runs, workflows, or error patterns
5. **No debugging support**: No way to trace execution flow or identify issues

## Proposed Naming Convention

### Directory Structure
```
logs_organized/
├── workflows/           # Organized by workflow type
│   ├── knowledge_scaffolding/
│   ├── strategy_fusion/
│   ├── high_stakes_vetting/
│   └── utopian_refinement/
├── phases/              # Organized by RISE phase
│   ├── phase_A/         # Knowledge Scaffolding
│   ├── phase_B/         # Strategy Fusion
│   ├── phase_C/         # High Stakes Vetting
│   └── phase_D/         # Utopian Refinement
├── errors/              # Logs with errors for debugging
├── sessions/            # Organized by session ID
├── analysis/            # Generated analysis reports
└── log_catalog.json     # Master catalog for search
```

### File Naming Convention

**Format**: `YYYYMMDD_HHMMSS_phase_X_workflow_short_runID_tasks_N_errors_M.jsonl`

**Examples**:
- `20250918_151644_phase_C_high_stakes_vetting_7725e79e_6tasks_2errors.jsonl`
- `20250918_151715_phase_D_utopian_refinement_ed580385_5tasks_1errors.jsonl`
- `20250918_143022_phase_A_knowledge_scaffolding_a1b2c3d4_8tasks_0errors.jsonl`

### Metadata Files

Each log file gets a corresponding `.metadata.json` file:

```json
{
  "original_file": "outputs/run_events_run_7725e79e4560421684938b9b500465ed.jsonl",
  "size_bytes": 6246,
  "modified": "2025-09-18T15:16:44.224488Z",
  "workflow_name": "High Stakes Vetting Cascade",
  "run_id": "run_7725e79e4560421684938b9b500465ed",
  "phase": "C",
  "session_id": "rise_1758222946_346c94",
  "error_count": 2,
  "task_count": 6,
  "duration_sec": 45.2,
  "status": "completed_with_errors",
  "line_count": 6,
  "key_errors": [
    "Missing template variable: 'result'",
    "IAR contract violation: Missing required fields"
  ]
}
```

## Implementation Benefits

### 1. **Instant Context**
- Filename tells you exactly what the log contains
- No need to open files to understand content
- Easy to identify problematic runs

### 2. **Hierarchical Organization**
- Group related logs together
- Easy navigation by workflow or phase
- Clear separation of error logs for debugging

### 3. **Searchability**
- Master catalog enables fast searching
- Find all logs for specific session, workflow, or error type
- Timeline reconstruction for debugging

### 4. **Debugging Support**
- Error logs separated for quick access
- Metadata provides summary without parsing
- Timeline analysis for execution flow

### 5. **Analysis Capabilities**
- Generate reports on workflow performance
- Identify common error patterns
- Track system health over time

## Usage Examples

### Find all logs for a specific session:
```bash
python log_organizer.py --search "rise_1758222946_346c94"
```

### Get debugging info for a specific run:
```bash
python log_organizer.py --debug "run_7725e79e4560421684938b9b500465ed"
```

### Organize all logs:
```bash
python log_organizer.py
```

### Dry run to see what would be organized:
```bash
python log_organizer.py --dry-run
```

## Error Classification

Logs are automatically classified by error severity:

- **No errors**: `0errors` - Normal execution
- **Minor errors**: `1-2errors` - Recoverable issues
- **Major errors**: `3+errors` - Significant problems
- **Critical errors**: Moved to `errors/` directory

## Analysis Reports

The system generates automatic analysis reports:

- `workflow_analysis.json` - Performance by workflow type
- `phase_analysis.json` - Success rates by RISE phase
- `error_analysis.json` - Common error patterns and fixes

## Integration with Existing System

The organizer can be integrated into the workflow engine:

```python
# In workflow_engine.py
from log_organizer import LogOrganizer

class IARCompliantWorkflowEngine:
    def __init__(self):
        self.log_organizer = LogOrganizer()
    
    def run_workflow(self, workflow_name, inputs, timeout=None):
        # ... existing code ...
        
        # After workflow completion
        if self.event_callback:
            self.log_organizer.organize_logs()
```

## Future Enhancements

1. **Real-time organization**: Organize logs as they're created
2. **Log compression**: Compress old logs to save space
3. **Log rotation**: Automatic cleanup of old logs
4. **Dashboard integration**: Web interface for log browsing
5. **Alert system**: Notify on error patterns or failures
6. **Performance metrics**: Track execution times and resource usage


