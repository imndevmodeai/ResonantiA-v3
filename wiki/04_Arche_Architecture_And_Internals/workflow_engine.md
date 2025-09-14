# Core Workflow Engine

## Overview

The Core Workflow Engine is the central component of Arche that manages the execution of workflows, maintains context, and ensures proper integration of all tools and capabilities. In v3.0, it has been enhanced with comprehensive IAR support and temporal capabilities.

## Key Components

### 1. Workflow Context

```python
class WorkflowContext:
    def __init__(self):
        self.state = {}
        self.iar_history = []
        self.temporal_state = {
            'current_time': None,
            'historical_states': [],
            'future_predictions': []
        }
        self.resonance_metrics = {
            'tactical_resonance': 0.0,
            'crystallization_potential': 0.0
        }
```

### 2. ResonanceTracker

```python
class ResonanceTracker:
    def __init__(self):
        self.execution_history = []
        self.resonance_metrics = {
            'avg_tactical_resonance': 0.0,
            'avg_crystallization_potential': 0.0,
            'total_executions': 0
        }
    
    def record_execution(self, task_id, iar_data, context):
        execution_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'task_id': task_id,
            'status': iar_data.get('status'),
            'confidence': iar_data.get('confidence', 0.0),
            'tactical_resonance': iar_data.get('tactical_resonance', 0.0),
            'crystallization_potential': iar_data.get('crystallization_potential', 0.0)
        }
        self.execution_history.append(execution_record)
        self._update_metrics()
```

### 3. IAR Management

```python
class IARManager:
    def __init__(self):
        self.iar_validator = IARValidator()
        self.resonance_tracker = ResonanceTracker()
    
    def process_iar(self, task_id, iar_data, context):
        # Validate IAR structure
        is_valid, issues = self.iar_validator.validate_structure(iar_data)
        if not is_valid:
            raise ValueError(f"Invalid IAR structure: {issues}")
        
        # Track resonance
        self.resonance_tracker.record_execution(task_id, iar_data, context)
        
        # Update context
        context.iar_history.append(iar_data)
        
        return is_valid, issues
```

## Workflow Execution

### 1. Basic Execution

```python
def execute_workflow(workflow_config, initial_context=None):
    context = WorkflowContext() if initial_context is None else initial_context
    iar_manager = IARManager()
    
    for step in workflow_config['steps']:
        # Execute step
        result, iar_data = execute_step(step, context)
        
        # Process IAR
        is_valid, issues = iar_manager.process_iar(step['id'], iar_data, context)
        if not is_valid:
            handle_iar_issues(issues, context)
        
        # Update context
        update_context(context, result, iar_data)
        
        # Check conditions
        if not check_conditions(step, context):
            break
    
    return context
```

### 2. Temporal Workflow Execution

```python
def execute_temporal_workflow(workflow_config, initial_context=None):
    context = WorkflowContext() if initial_context is None else initial_context
    iar_manager = IARManager()
    
    # Initialize temporal state
    context.temporal_state['current_time'] = time.time()
    
    for step in workflow_config['steps']:
        # Execute step with temporal context
        result, iar_data = execute_temporal_step(step, context)
        
        # Process IAR
        is_valid, issues = iar_manager.process_iar(step['id'], iar_data, context)
        if not is_valid:
            handle_iar_issues(issues, context)
        
        # Update temporal context
        update_temporal_context(context, result, iar_data)
        
        # Check temporal conditions
        if not check_temporal_conditions(step, context):
            break
    
    return context
```

## Context Management

### 1. State Updates

```python
def update_context(context, result, iar_data):
    # Update general state
    context.state.update(result)
    
    # Update temporal state
    if 'temporal_data' in result:
        context.temporal_state['historical_states'].append({
            'timestamp': time.time(),
            'state': result['temporal_data']
        })
    
    # Update resonance metrics
    context.resonance_metrics.update({
        'tactical_resonance': iar_data.get('tactical_resonance', 0.0),
        'crystallization_potential': iar_data.get('crystallization_potential', 0.0)
    })
```

### 2. Temporal State Management

```python
def update_temporal_context(context, result, iar_data):
    # Update current time
    context.temporal_state['current_time'] = time.time()
    
    # Handle historical data
    if 'historical_data' in result:
        context.temporal_state['historical_states'].extend(result['historical_data'])
    
    # Handle future predictions
    if 'future_predictions' in result:
        context.temporal_state['future_predictions'].extend(result['future_predictions'])
```

## Error Handling

### 1. IAR Issues

```python
def handle_iar_issues(issues, context):
    # Log issues
    logger.error(f"IAR validation issues: {issues}")
    
    # Update context with error state
    context.state['last_error'] = {
        'type': 'iar_validation',
        'issues': issues,
        'timestamp': time.time()
    }
    
    # Attempt recovery
    if can_recover_from_iar_issues(issues):
        attempt_iar_recovery(context)
    else:
        raise WorkflowExecutionError("Critical IAR validation issues")
```

### 2. Temporal Issues

```python
def handle_temporal_issues(issues, context):
    # Log issues
    logger.error(f"Temporal processing issues: {issues}")
    
    # Update context with error state
    context.state['last_error'] = {
        'type': 'temporal_processing',
        'issues': issues,
        'timestamp': time.time()
    }
    
    # Attempt recovery
    if can_recover_from_temporal_issues(issues):
        attempt_temporal_recovery(context)
    else:
        raise WorkflowExecutionError("Critical temporal processing issues")
```

## Best Practices

1. **Context Management**
   - Maintain clear state boundaries
   - Properly handle temporal data
   - Regular context cleanup

2. **IAR Integration**
   - Validate all IAR data
   - Track resonance metrics
   - Handle IAR issues gracefully

3. **Temporal Processing**
   - Maintain consistent timestamps
   - Handle timezone issues
   - Properly manage historical data

4. **Error Handling**
   - Implement comprehensive error recovery
   - Maintain error history
   - Provide clear error messages

## Related Components

- [IAR Implementation](../03_Using_Arche_Workflows_And_Tools/iar_implementation.md)
- [Temporal Capabilities](../03_Using_Arche_Workflows_And_Tools/temporal_capabilities.md)
- [System Representation](./system_representation.md)
- [Error Handling](../06_Troubleshooting_And_FAQ/error_handling.md) 