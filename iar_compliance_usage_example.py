
# === USAGE EXAMPLE ===
# Replace WorkflowEngine with IARCompliantWorkflowEngine

# OLD:
# engine = WorkflowEngine(spr_manager)

# NEW:
engine = IARCompliantWorkflowEngine(spr_manager)

# Get compliance dashboard
dashboard = engine.get_resonance_dashboard()
print(f"IAR Compliance Score: {dashboard['compliance_score']:.2%}")
