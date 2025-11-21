# Complex Query Test - UBI Economic Analysis

## Query Overview

This complex query is designed to exercise **all** of ArchE's analytical capabilities and test the fallback mechanisms and execution plan logging we just implemented.

## Query Text

```
Analyze the projected 5-year economic and social consequences of implementing Universal Basic Income (UBI) in a developed economy, considering:
1. Causal relationships between UBI and labor market participation rates with temporal lag analysis
2. Predictive modeling of inflation trends under different UBI funding scenarios (tax-based vs debt-based)
3. Agent-based simulation of household spending behavior and economic multiplier effects
4. Comparative fluxual processing of UBI implementation scenarios (full UBI vs partial UBI vs control group)
5. Complex system visioning of emergent behaviors including social cohesion, entrepreneurship rates, and healthcare utilization patterns
6. Temporal analysis across historical UBI pilot programs and future state projections
7. Integration of all findings into a comprehensive strategic recommendation framework

Use 4D thinking to understand historical context, current dynamics, and future trajectories. Apply the full spectrum of ArchE's analytical capabilities including Causal InferencE, PredictivE ModelinG TooL, Agent Based ModelinG, ComparativE fluxuaL processinG, and ComplexSystemVisioninG.
```

## Why This Query is Complex

### 1. **Multiple Capability Triggers**
- **Causal InferencE**: "Causal relationships... with temporal lag analysis"
- **PredictivE ModelinG TooL**: "Predictive modeling of inflation trends"
- **Agent Based ModelinG**: "Agent-based simulation of household spending"
- **ComparativE fluxuaL processinG**: "Comparative fluxual processing of UBI scenarios"
- **ComplexSystemVisioninG**: "Complex system visioning of emergent behaviors"
- **4D thinkinG**: "Temporal analysis... historical... future"

### 2. **Explicit SPR References**
- Causal InferencE
- PredictivE ModelinG TooL
- Agent Based ModelinG
- ComparativE fluxuaL processinG
- ComplexSystemVisioninG
- 4D thinkinG

### 3. **Multiple Analysis Dimensions**
- Economic analysis
- Social analysis
- Temporal analysis (historical, current, future)
- Comparative analysis (multiple scenarios)
- Causal analysis (with lag detection)
- Predictive analysis (5-year projection)
- Simulation analysis (agent-based)
- Complex systems analysis (emergent behaviors)

### 4. **Integration Requirements**
- Requires synthesis of multiple analytical approaches
- Needs integration of findings into strategic framework
- Demands comprehensive recommendation generation

## Expected Execution Plan Structure

The execution plan should capture:

1. **Query Analysis Phase**
   - Intent: Analysis (complex, multi-dimensional)
   - Complexity: Very High
   - Required Capabilities: All major tools
   - Detected SPRs: Multiple

2. **Capability Execution Phase**
   - Task 1: Causal Inference (temporal lag analysis)
   - Task 2: Predictive Modeling (inflation scenarios)
   - Task 3: Agent-Based Modeling (household behavior)
   - Task 4: CFP (scenario comparison)
   - Task 5: Complex System Visioning (emergent behaviors)
   - Task 6: Temporal Analysis (historical + future)

3. **Synthesis Phase**
   - Integration of all findings
   - Strategic recommendation generation

## Testing Objectives

### 1. **Fallback Mechanisms**
- Test if tools gracefully handle missing dependencies
- Verify fallback chains work correctly
- Ensure system continues even with partial failures

### 2. **Execution Plan Logging**
- Verify all tasks are captured
- Check tool selection is logged
- Confirm execution order is recorded
- Validate fallback usage is tracked
- Ensure errors are properly logged

### 3. **Multi-Capability Integration**
- Test simultaneous execution of multiple tools
- Verify capability results are integrated
- Check response synthesis includes all findings

### 4. **SPR Activation**
- Confirm SPRs are detected and primed
- Verify SPR context is used in analysis
- Check SPR definitions are accessible

## Running the Test

### Option 1: Direct Execution
```bash
python3 ask_arche_enhanced_v2.py "$(cat test_complex_query.txt)"
```

### Option 2: Using Test Script
```bash
./test_complex_query.sh
```

### Option 3: Interactive
```bash
python3 ask_arche_enhanced_v2.py
# Then paste the query when prompted
```

## Expected Outputs

1. **Execution Plan File**
   - Location: `outputs/query_executions/playbooks/execution_plan_*.json`
   - Should contain:
     - All 6+ tasks
     - Selected tools list
     - Execution order
     - Action results
     - Any fallbacks used
     - Any errors encountered

2. **Full Report**
   - Location: `outputs/query_executions/arche_enhanced_v2_report_*.md`
   - Should contain:
     - Comprehensive analysis
     - Integration of all capability results
     - Strategic recommendations
     - Methodology documentation

3. **Console Output**
   - Progress indicators
   - Tool execution status
   - Fallback notifications (if any)
   - Final results

## Verification Checklist

After running, verify:

- [ ] Execution plan file was created
- [ ] Plan contains all expected tasks
- [ ] Tool selection is logged correctly
- [ ] Execution order is sequential/logical
- [ ] All tools attempted execution (or fallback logged)
- [ ] Errors are captured (if any occurred)
- [ ] Fallbacks are documented (if used)
- [ ] Response includes synthesis of all capabilities
- [ ] SPRs were detected and primed
- [ ] Report file was generated

## Analyzing the Results

### Check Execution Plan
```bash
# View latest plan
ls -t outputs/query_executions/playbooks/execution_plan_*.json | head -1 | xargs cat | jq .
```

### Check Task Execution
```bash
# See which tasks executed
cat outputs/query_executions/playbooks/execution_plan_*.json | jq '.tasks[] | {order, tool, status}'
```

### Check Fallbacks
```bash
# See if any fallbacks were used
cat outputs/query_executions/playbooks/execution_plan_*.json | jq '.fallbacks_used'
```

### Check Errors
```bash
# See if any errors occurred
cat outputs/query_executions/playbooks/execution_plan_*.json | jq '.errors'
```

## Success Criteria

The test is successful if:

1. ✅ All tools are attempted (or fallback is logged)
2. ✅ Execution plan captures complete workflow
3. ✅ System handles failures gracefully
4. ✅ Response integrates multiple analytical approaches
5. ✅ Plan file is readable and complete
6. ✅ No critical errors prevent completion

## Notes

- This query is intentionally complex to stress-test the system
- Some tools may not execute if dependencies are missing (this is expected and should trigger fallbacks)
- The execution plan will show exactly what happened, even if some tools failed
- The response should still be comprehensive even with partial tool execution

