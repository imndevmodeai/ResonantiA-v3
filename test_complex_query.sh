#!/bin/bash
# Complex Query Test Script
# This query will exercise multiple capabilities, fallback mechanisms, and execution plan logging

QUERY="Analyze the projected 5-year economic and social consequences of implementing Universal Basic Income (UBI) in a developed economy, considering:
1. Causal relationships between UBI and labor market participation rates with temporal lag analysis
2. Predictive modeling of inflation trends under different UBI funding scenarios (tax-based vs debt-based)
3. Agent-based simulation of household spending behavior and economic multiplier effects
4. Comparative fluxual processing of UBI implementation scenarios (full UBI vs partial UBI vs control group)
5. Complex system visioning of emergent behaviors including social cohesion, entrepreneurship rates, and healthcare utilization patterns
6. Temporal analysis across historical UBI pilot programs and future state projections
7. Integration of all findings into a comprehensive strategic recommendation framework

Use 4D thinking to understand historical context, current dynamics, and future trajectories. Apply the full spectrum of ArchE's analytical capabilities including Causal InferencE, PredictivE ModelinG TooL, Agent Based ModelinG, ComparativE fluxuaL processinG, and ComplexSystemVisioninG."

echo "Executing complex query test..."
echo "Query: $QUERY"
echo ""

python3 ask_arche_enhanced_v2.py "$QUERY"

echo ""
echo "=========================================="
echo "Execution complete. Check outputs:"
echo "  - Execution Plan: outputs/query_executions/playbooks/execution_plan_*.json"
echo "  - Full Report: outputs/query_executions/arche_enhanced_v2_report_*.md"
echo "=========================================="

