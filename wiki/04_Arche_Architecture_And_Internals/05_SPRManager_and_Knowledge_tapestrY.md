# 5. SPRManager and Knowledge tapestrY (`spr_manager.py`, `knowledge_graph/spr_definitions_tv.json`)

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Explain the role of SPRManager in CRUD operations on spr_definitions_tv.json and the conceptual SPR Decompressor.
-->

This page details the `SPRManager` (`spr_manager.py`), its role in managing the `Knowledge tapestrY` (`knowledge_graph/spr_definitions_tv.json`), and the conceptual `SPR Decompressor` that enables cognitive activation through Sparse Priming Representations (SPRs).

*   **The Knowledge tapestrY (`spr_definitions_tv.json`)**
    *   **Purpose:** Serves as the persistent, structured knowledge base for Arche. It defines all recognized SPRs, their meanings, relationships, and associated operational data.
    *   **Location:** `knowledge_graph/spr_definitions_tv.json`.
    *   **Format:** A JSON file, typically a dictionary where keys are the SPR terms (Guardian pointS format, e.g., `Cognitive resonancE`).
    *   **Structure of an SPR Entry (Example fields - Protocol Section 2.1 & 3.1.2):**
        *   `term`: The SPR term itself.
        *   `definition`: Clear, concise textual definition.
        *   `type`: Category (e.g., "Concept", "Process", "Tool", "Principle", "Heuristic").
        *   `related_to`: List of other SPR terms it is semantically or functionally connected to (forming a conceptual graph).
        *   `enables`: List of capabilities, other SPRs, or cognitive functions it helps activate or make accessible.
        *   `implemented_by`: (If applicable) Pointers to specific code modules, workflow files, or protocol sections that realize this SPR.
        *   `blueprint_details`: (If applicable) Parameters, configurations, template prompts, or structural information needed for its activation or use by the `SPR Decompressor` or tools.
        *   `confidence_score`: (Optional, perhaps meta-data) Confidence in the current definition or its utility.
        *   `last_updated_by`: (Optional, meta-data) Who/what last modified this SPR (e.g., "Keyholder", "InsightSolidificatioN_Workflow_ID").
*   **`SPRManager` (`spr_manager.py` - Protocol Section 7.5)**
    *   **Purpose:** Provides a programmatic interface for all Create, Read, Update, and Delete (CRUD) operations on the `Knowledge tapestrY`.
    *   **Key Responsibilities & Methods (Conceptual):**
        *   `load_knowledge_tapestry()`: Reads `spr_definitions_tv.json` into an in-memory representation (e.g., a dictionary) at system startup or when needed.
        *   `save_knowledge_tapestry()`: Writes the current in-memory representation back to `spr_definitions_tv.json`, ensuring persistence.
        *   `get_spr_definition(spr_term)`: Retrieves the full definition entry for a given SPR term.
        *   `add_spr(spr_definition)`: Adds a new SPR entry to the knowledge base. Used by `InsightSolidificatioN`.
        *   `update_spr(spr_term, updated_fields)`: Modifies an existing SPR entry.
        *   `delete_spr(spr_term)`: Removes an SPR (use with caution).
        *   `find_related_sprs(spr_term, relationship_type)`: Navigates the graph to find connected SPRs.
        *   `validate_spr_structure(spr_definition)`: Ensures a new or updated SPR conforms to the required schema.
    *   **Ensures Consistency:** The `SPRManager` is crucial for maintaining the integrity and consistency of the knowledge base.
*   **The SPR Decompressor (Conceptual - Protocol Section 3.2)**
    *   **Purpose:** The mechanism by which encountering an SPR (e.g., in text, Keyholder input, or system-generated content) triggers a deeper cognitive activation or "unfolding" of its meaning and associated knowledge/capabilities within Arche's `Knowledge Network Oneness (KnO)`.
    *   **How it Works (Conceptually):**
        1.  An SPR term is recognized (e.g., by a text processing module or an LLM).
        2.  The `SPR Decompressor` is invoked with this term.
        3.  It uses the `SPRManager` to retrieve the full `spr_definition` from the `Knowledge tapestrY`.
        4.  It interprets the `definition`, `related_to`, `enables`, and especially the `blueprint_details` fields.
        5.  **Activation:** This interpretation leads to:
            *   Loading relevant data or parameters into the current context.
            *   Priming specific LLM prompts or cognitive tool configurations.
            *   Activating or making available related functions or sub-workflows.
            *   Adjusting internal reasoning pathways or priorities.
        *   The goal is not just to retrieve information, but to change Arche's internal state and processing disposition in a way that reflects a deep understanding of the SPR.
    *   **Example:** Encountering the SPR `Temporal Causal Analysis` might cause the `SPR Decompressor` to load default parameters for the `CausalInferenceTool`, prime prompts related to identifying time lags, and make the `temporal_causal_analysis_workflow.json` more readily available or suggested.
    *   The `SPR Decompressor` is a key part of making Arche more than a simple lookup system; it allows SPRs to act as true cognitive keys.

*The `SPRManager` provides the mechanics for knowledge storage and retrieval, while the `SPR Decompressor` embodies the dynamic process of using that knowledge to inform and guide Arche's cognitive operations.* 