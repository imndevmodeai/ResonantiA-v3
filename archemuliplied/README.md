## CTaaS (Cognitive Twin as a Service)

### Decision Integrity SLA
- Certified Decision Pack (CDP) must satisfy: IAR.confidence ≥ 0.75 and no ethics/provenance violations.
- Sub‑threshold results trigger Metacognitive shifT or re‑run at no additional pack charge.
- Each CDP carries a Decision Integrity Ledger entry with event IDs and provenance.

### POV Playbook (6–8 Weeks)
1. Week 1: Intake & data handshake; define 1–2 pivotal decisions and KPIs; create baseline CDP(s).
2. Week 2–3: Causal estimation + ABM instantiation; early scenario cohort; acceptance gates.
3. Week 4: Predictive timelines; optional CFP divergence check; refine and certify CDPs.
4. Week 5: Board‑ready review; go/no‑go; implementation plan.
5. Week 6–8: Closed‑loop evaluation on realized outcomes; autonomous recalibration; ROI readout.

### Run the CTaaS Workflow
Execute with your orchestrator/CLI, supplying initial context (scenario, data refs, targets):

```bash
python -m Three_PointO_ArchE.main \
  workflows/ctaas_decision_impact.json \
  -c '{
    "scenario_name": "Price +2% Europe Q4",
    "business_unit": "EMEA-CPG",
    "data_ref": {"x": [0,1,0,1], "z": [1,0,1,0], "y": [0.2,0.9,0.3,1.1]},
    "treatment": "x",
    "outcome": "y",
    "controls": ["z"],
    "time_series_seed": {"y": [1,1.1,1.05,1.2,1.18,1.22]},
    "forecast_target": "y"
  }'
```

This generates a CDP with an aggregated IAR confidence and a summary display output.

### Core Concepts
- **Causal Inference & ABM:** Tools for causal discovery (`causal_inference_tool.py`) and agent-based modeling (`agent_based_modeling_tool.py`) to simulate complex systems and understand underlying drivers.
- **Self-Driving Browser Automation:** A practical, robust implementation (`self_driving_sales/`) using Playwright to automate conversational outreach and follow-up via Google Messages for Web, demonstrating a real-world application of the ResonantiA principles.
*   **"As Above, So Below":** Principle ensuring consistency between concept and implementation.
*   **Advanced Interaction Patterns:** (Section 8) Structured prompts for Keyholder guidance.
*   **Keyholder Supreme Override:** When `IMnDEVmode` key is active, the Keyholder can bypass protocol constraints (Section 1.6).

## Project Structure

```
resonatia_arche/
├── mastermind_ai_v2_9/ # Core Python package
│ ├── __init__.py
│ ├── config.py # Configuration (API keys, paths, etc.)
│ ├── main.py # Main entry point, invokes the Maestro
│ ├── resonantia_maestro.py # The master orchestrator
│ ├── rise_orchestrator.py # RISE Engine orchestrator
│ ├── workflow_engine.py # Executes workflow blueprints
# ... (other core files)
├── workflows/ # Workflow definition JSON files
# ... (workflow files)
├── knowledge_graph/ # Knowledge base components
│ └── spr_definitions_tv.json # SPR definitions
├── logs/ # Runtime logs
├── outputs/ # Generated outputs (results, visualizations)
├── specifications/ # Markdown specification files for components
│ └── resonantia_maestro.md # Spec for the master orchestrator
├── requirements.txt # Python dependencies
└── README.md # This file
```

## Setup Instructions

Detailed setup instructions can be found in **Section 4** of the `ResonantiA Protocol v2.9.5` document. Summary:
1.  Clone/Download.
2.  Create a `.env` file for your API keys and other secrets.
3.  Create & activate virtual environment (`python -m venv .venv`, `source .venv/bin/activate` or `.venv\\Scripts\\activate`).
4.  Install dependencies: `pip install -r requirements.txt`.
5.  Configure: **Edit `mastermind_ai_v2_9/config.py`** - ADD API KEYS (use environment variables recommended), review sandbox settings.
6.  Run: See Basic Usage below.

## Basic Usage

The system is now invoked through the `ResonantiaMaestro` via `main.py`. You can provide a query directly or specify a workflow to run.

1.  **To run a query for the Maestro to orchestrate:**
    ```bash
    python mastermind_ai_v2_9/main.py -q "Your complex query for analysis or design here"
    ```
2.  **To run a specific workflow directly:**
    ```bash
    python mastermind_ai_v2_9/main.py workflows/your_workflow.json
    ```
3.  **To provide additional context:**
    ```bash
    python mastermind_ai_v2_9/main.py -q "Your query" -c '{"some_context_key": "some_value"}'
    ```
4.  Check console for output, `logs/` for detailed logs, and `outputs/` for result files.

## Advanced Usage

*   **SPRs:** Define custom SPRs in `knowledge_graph/spr_definitions_tv.json`. Use them in prompts to trigger internal cognitive unfolding.
*   **Tesla Visioning:** For complex, novel problems, use the `Tesla Visioning Workflow` to guide the system through a structured process of deconstruction, analysis, and synthesis.



