
# === USAGE EXAMPLE ===
# Replace IARCompliantWorkflowEngine with IARCompliantWorkflowEngine

# OLD:
# engine = IARCompliantWorkflowEngine(spr_manager)

# NEW:
engine = IARCompliantWorkflowEngine(spr_manager)

# Get compliance dashboard
dashboard = engine.get_resonance_dashboard()
print(f"IAR Compliance Score: {dashboard['compliance_score']:.2%}")
