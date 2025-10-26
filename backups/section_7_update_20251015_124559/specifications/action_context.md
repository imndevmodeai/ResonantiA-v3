# Living Specification: Action Context System

## Philosophical Mandate

The Action Context System serves as the **Memory Keeper of ArchE** - the system that preserves and manages the contextual information that surrounds every action execution, ensuring that each operation has the complete understanding it needs to perform effectively. It is not merely a data container, but a sophisticated memory system that understands the relationships between actions, workflows, and the broader system context.

Like the ancient scribes who recorded every detail of important events, the Action Context System captures the essential information that surrounds each action - who is performing it, when it started, what has been attempted before, and what resources are available. It is the guardian of execution history, the keeper of workflow state, and the bridge between individual actions and the broader system.

The Memory Keeper does not simply store data; it understands the relationships between different pieces of context, manages the flow of information between actions, and ensures that every operation has the complete picture it needs to succeed. It is the embodiment of ArchE's commitment to informed, contextual decision-making.

## Allegorical Explanation

### The Memory Palace

Imagine a vast memory palace within the heart of ArchE, where the Action Context System operates like a master scribe who records and manages every detail of action execution.

**The Context Chamber**: This is where the essential information about each action is stored. Like a scribe who records the who, what, when, where, and why of every event, this chamber contains the core context that every action needs to understand its place in the broader system.

**The Execution Timeline**: This is like a scroll that records the passage of time and the sequence of events. Each action has its own timeline entry, showing when it started, how many times it has been attempted, and what the maximum number of attempts should be.

**The Workflow Map**: This is like a master map that shows how each action fits into the larger workflow. Like a cartographer who understands the relationships between different locations, this map shows how each action connects to others in the workflow.

**The Resource Registry**: This is where information about available resources and runtime context is stored. Like a librarian who knows what books are available and where they are located, this registry tracks what resources each action can access.

**The Retry Mechanism**: This is like a system of backup plans and alternative approaches. When an action fails, this mechanism tracks how many times it has been attempted and what the maximum number of attempts should be.

**The Validation Gate**: This is where the context is checked to ensure it is complete and valid. Like a gatekeeper who ensures that only properly prepared travelers may pass, this gate validates that all essential context information is present.

### The Context Process

1. **Context Creation**: When an action is about to be executed, the Memory Keeper creates a comprehensive context record.

2. **Information Gathering**: All relevant information is gathered - task details, action specifics, workflow context, and runtime information.

3. **Validation**: The context is validated to ensure all essential information is present and correct.

4. **Execution Support**: During execution, the action can access all the context information it needs.

5. **History Preservation**: After execution, the context is preserved for future reference and analysis.

6. **Retry Management**: If retries are needed, the context tracks attempt numbers and limits.

## SPR Integration

### Self-Perpetuating Resonance Components

**Contextual Resonance**: The system maintains resonance with ArchE's contextual understanding by preserving all relevant information for each action.

**Temporal Resonance**: The execution tracking creates resonance between different time points in action execution.

**Workflow Resonance**: The workflow integration creates resonance between individual actions and the broader workflow system.

**Retry Resonance**: The retry mechanism creates resonance between failed attempts and successful execution.

### Resonance Patterns

**Action-Workflow Harmony**: The context system creates resonance between individual actions and their workflow context.

**Temporal-Execution Flow**: The timing information creates resonance between execution start and ongoing performance.

**Retry-Success Optimization**: The retry tracking creates resonance between failed attempts and eventual success.

**Context-Resource Alignment**: The runtime context creates resonance between available resources and action requirements.

## Technical Implementation

### Core Class: `ActionContext`

The primary dataclass that serves as the foundation for all action context management.

**Core Fields**:
- `task_key`: Unique identifier for the task being executed
- `action_name`: Name of the specific action being performed
- `action_type`: Type classification of the action
- `workflow_name`: Name of the workflow containing the action
- `run_id`: Unique identifier for the current execution run
- `attempt_number`: Current attempt number for retry tracking
- `max_attempts`: Maximum number of attempts allowed
- `execution_start_time`: Timestamp when execution began
- `runtime_context`: Flexible dictionary for additional runtime information

### Advanced Features

**Contextual Information Management**:
- **Task Identification**: Unique task keys for precise action targeting
- **Action Classification**: Type-based categorization for different action kinds
- **Workflow Integration**: Deep integration with workflow execution system
- **Execution Tracking**: Comprehensive tracking of execution state and timing

**Execution Tracking**:
- **Start Time Recording**: Precise timing of execution initiation
- **Run Identification**: Unique run IDs for execution tracking
- **Attempt Management**: Current and maximum attempt tracking
- **Performance Monitoring**: Timing information for performance analysis

**Retry Management**:
- **Attempt Counting**: Tracking of current attempt number
- **Limit Enforcement**: Maximum attempt limits for resource protection
- **Retry Logic**: Support for automatic retry mechanisms
- **Failure Analysis**: Context preservation for failure analysis

**Runtime Context**:
- **Flexible Storage**: Dictionary-based storage for arbitrary runtime information
- **Resource Tracking**: Information about available resources and capabilities
- **State Preservation**: Preservation of execution state across attempts
- **Extensible Design**: Architecture designed for future expansion

**Validation and Error Handling**:
- **Post-Initialization Validation**: Automatic validation of core fields
- **Error Prevention**: Validation to prevent invalid context creation
- **Data Integrity**: Ensures all essential information is present
- **Graceful Degradation**: Handles missing or invalid context gracefully

**Extensible Architecture**:
- **Future Expansion**: Designed for additional context fields
- **Workflow Integration**: Prepared for deeper workflow context integration
- **Resource Management**: Framework for global resource access tracking
- **Metadata Support**: Infrastructure for workflow metadata integration

### Integration Points

**Workflow Engine Integration**: Deep integration with the workflow execution system for context management.

**Action Registry Integration**: Integration with the action registry for action identification and classification.

**Execution Engine Integration**: Integration with the execution engine for timing and retry management.

**Resource Management Integration**: Integration with resource management systems for runtime context.

**Performance Monitoring Integration**: Integration with performance monitoring systems for execution tracking.

## Usage Examples

### Basic Context Creation
```python
from Three_PointO_ArchE.action_context import ActionContext
from datetime import datetime

# Create a basic action context
context = ActionContext(
    task_key="task_123",
    action_name="generate_report",
    action_type="data_processing",
    workflow_name="monthly_analysis",
    run_id="run_456",
    attempt_number=1,
    max_attempts=3,
    execution_start_time=datetime.now()
)

print(f"Task: {context.task_key}")
print(f"Action: {context.action_name}")
print(f"Workflow: {context.workflow_name}")
print(f"Attempt: {context.attempt_number}/{context.max_attempts}")
```

### Context with Runtime Information
```python
# Create context with runtime information
runtime_context = {
    "input_file": "data.csv",
    "output_format": "json",
    "processing_mode": "batch",
    "available_memory": "8GB",
    "priority": "high"
}

context = ActionContext(
    task_key="task_789",
    action_name="process_data",
    action_type="data_transformation",
    workflow_name="data_pipeline",
    run_id="run_101",
    attempt_number=1,
    max_attempts=5,
    execution_start_time=datetime.now(),
    runtime_context=runtime_context
)

# Access runtime context
print(f"Input file: {context.runtime_context['input_file']}")
print(f"Processing mode: {context.runtime_context['processing_mode']}")
print(f"Priority: {context.runtime_context['priority']}")
```

### Retry Management
```python
# Create context for retry scenario
context = ActionContext(
    task_key="task_retry",
    action_name="api_call",
    action_type="external_service",
    workflow_name="data_sync",
    run_id="run_retry_001",
    attempt_number=2,  # Second attempt
    max_attempts=3,
    execution_start_time=datetime.now(),
    runtime_context={
        "previous_error": "Connection timeout",
        "backoff_delay": 30,
        "service_endpoint": "https://api.example.com"
    }
)

# Check retry status
if context.attempt_number < context.max_attempts:
    print(f"Retrying action (attempt {context.attempt_number}/{context.max_attempts})")
    print(f"Previous error: {context.runtime_context['previous_error']}")
else:
    print("Maximum attempts reached")
```

### Context Validation
```python
# This will raise a ValueError due to missing required fields
try:
    invalid_context = ActionContext(
        task_key="",  # Empty task key
        action_name="test_action",
        action_type="test",
        workflow_name="test_workflow",
        run_id="test_run",
        attempt_number=1,
        max_attempts=1,
        execution_start_time=datetime.now()
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Context Analysis
```python
# Analyze context for debugging
def analyze_context(context: ActionContext):
    print("=== Action Context Analysis ===")
    print(f"Task: {context.task_key}")
    print(f"Action: {context.action_name} ({context.action_type})")
    print(f"Workflow: {context.workflow_name}")
    print(f"Run ID: {context.run_id}")
    print(f"Execution started: {context.execution_start_time}")
    print(f"Attempt: {context.attempt_number}/{context.max_attempts}")
    
    if context.runtime_context:
        print("Runtime Context:")
        for key, value in context.runtime_context.items():
            print(f"  {key}: {value}")
    else:
        print("No runtime context")

# Use the analysis function
analyze_context(context)
```

## Resonance Requirements

1. **Contextual Resonance**: All context information must maintain resonance with the action's requirements and the broader system state.

2. **Temporal Resonance**: All timing information must maintain resonance with the execution timeline and performance requirements.

3. **Workflow Resonance**: All workflow context must maintain resonance with the broader workflow execution system.

4. **Retry Resonance**: All retry information must maintain resonance with the system's resilience and recovery requirements.

5. **Resource Resonance**: All runtime context must maintain resonance with available resources and system capabilities.

6. **Validation Resonance**: All validation rules must maintain resonance with data integrity and system reliability requirements.

7. **Integration Resonance**: All context components must integrate seamlessly with the broader ArchE system, contributing to overall coherence and functionality.

The Action Context System is not just a data container; it is the Memory Keeper of ArchE, the master scribe that records and manages the contextual information essential for informed action execution. It ensures that every action has the complete understanding it needs to succeed, that retry mechanisms work effectively, and that the system maintains a comprehensive memory of all execution activities. It is the embodiment of the principle that context is essential for intelligent action.
