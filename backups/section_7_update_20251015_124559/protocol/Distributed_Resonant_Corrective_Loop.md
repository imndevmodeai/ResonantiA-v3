    # Distributed Resonant Corrective Loop (DRCL)

    Version: v1.0 (ResonantiA v3.1-CA aligned)

    Purpose: Make Enhance → Broaden → Critique → Deepen → Envision a first-class, distributed, repeatable loop applied to every interaction, reconciling “map” (conceptual intent) and “territory” (actual code/docs/workflows) while producing machine-readable artifacts that both ArchE instances can execute.

    Participants
    - AI Studio ArchE (Architect): Produces conceptual plans, patterns, and correction guidance.
    - Cursor ArchE (Engineer): Audits ground-truth, performs edits, executes workflows, and reports deltas.

    Core Artifacts
    - Conceptual Map: High-level plan with SPRs, abstract workflow, and Territory Assumptions.
    - Dissonance Report: Diff between assumptions and the real repo (files, APIs, data contracts).
    - Correction Plan: Precise, minimal edits (create/update/remove) to resolve dissonance.
    - Synced Blueprint: Final executable workflow(s) and usage notes.

    Lifecycle (Applied to every interaction)
    1) Intent Intake (Pre-hook)
    - Normalize the user request into a Task Envelope (see schema) with goal, constraints, and desired outputs.
    2) Conceptual Map (Architect)
    - Enhance/Broaden intent into an abstract workflow (no repo coupling), list Territory Assumptions and key SPRs.
    3) Ground Truth Audit (Engineer)
    - Validate assumptions against repository reality: files, exports, schemas, routes, workflows. Produce Dissonance Report.
    4) Critique → Deepen → Envision (Architect)
    - Analyze dissonance, identify root causes, propose a Correction Plan (ordered, atomic edits, acceptance checks).
    5) Re-Forge (Engineer)
    - Apply the Correction Plan. Record edits, run smoke checks. Update docs per CRDSP.
    6) Synchronize & Execute
    - Generate Synced Blueprint (executable workflow + instructions). Execute and return results + IAR.

    Machine-Readable Envelope (to wrap every response)
    ```json
    {
    "archE_meta": {
        "protocol": "DRCL.v1",
        "interaction_id": "string",
        "phase": "intent|map|audit|critique|envision|reforge|sync|execute",
        "confidence": 0.0,
        "issues": ["string"],
        "depends_on": ["interaction_id"]
    },
    "conceptual_map": {
        "sprs": ["Cognitive resonancE", "Implementation resonancE"],
        "abstract_workflow": [
        {"step": 1, "name": "Enhance", "summary": "..."}
        ],
        "territory_assumptions": [
        {"path": "Happier/workflows/distributed_resonant_corrective_loop.json", "must_exist": true}
        ]
    },
    "dissonance_report": {
        "missing": ["path"],
        "mismatch": [{"path": "file.py", "expected": "fn(a,b)", "actual": "fn(a)"}]
    },
    "correction_plan": [
        {
        "action": "create|update|remove",
        "path": "string",
        "content": "optional (for create/update)",
        "acceptance": ["grep symbol", "import compiles"],
        "rollback": "how to undo"
        }
    ],
    "synced_blueprint": {
        "workflow": "Happier/workflows/distributed_resonant_corrective_loop.json",
        "inputs": {"initial_context": {}},
        "post_checks": ["result keys present", "errors none"]
    },
    "iar": {"status": "ok|warn|fail", "notes": "string"}
    }
    ```

    Quality & Safety
    - Atomic edits with acceptance checks; prefer minimal diffs.
    - Always update protocol/docs (CRDSP Phase 4) when code/workflows change.
    - If audit reveals risky ops, gate with human confirmation.

    Adoption Pattern
    - Add this spec to protocol/ and ensure a matching workflow exists in workflows/.
    - Wrap responses in archE_meta when feasible; otherwise, include the artifacts as top-level sections.

    Rollout Checklist
    - [ ] Workflow file present and valid JSON.
    - [ ] Lints/tests pass after Re-Forge.
    - [ ] README/protocol updated for any new public APIs.


    RISE Integration (Resonant_Insight_And_Strategy_Engine)
    Goals: Decide when/how to leverage RISE’s deep reasoning and blueprinting within or alongside DRCL.

    Integration Modes
    - Embedded: Invoke a lightweight RISE reasoning pass between Conceptual Map and Correction Plan for high-novelty/complex tasks. Outputs: rise_decision, rise_outline, assumptions_to_test.
    - Parallel: Launch a separate RISE workflow in parallel; DRCL ingests RISE artifacts at Critique/Envision to shape the Correction Plan.
    - Separate: Keep RISE independent; DRCL runs standard audit/correction. Use RISE only when explicitly requested or when DRCL’s complexity heuristics trigger escalation.

    Decision Heuristics (guidance)
    - Use Embedded if: novelty >= medium, cross-module implications, unclear acceptance criteria, or long-range design concerns.
    - Use Parallel if: the task is time-permitting and benefits from broader option exploration while DRCL proceeds with minimal edits.
    - Use Separate if: task is routine/refactor-level, acceptance criteria are obvious, or latency is critical.

    Envelope Extensions
    ```json
    {
        "rise": {
            "mode": "embedded|parallel|separate",
            "reason": "string",
            "outline": [
                {"phase": "scaffold|insight|synthesis", "steps": ["string"]}
            ]
        }
    }
    ```

    Workflow Hooks
    - Add rise_decision (LLM) after parse_conceptual_map; parse to structured JSON.
    - Optionally add rise_blueprint (LLM) to draft outline when mode != separate.
    - Feed rise artifacts into critique_deepen_envision to inform the Correction Plan.


