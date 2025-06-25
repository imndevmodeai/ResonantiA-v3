# CRITICAL MANDATES for ResonantiA Protocol v3.1-CA and Beyond

This document contains critical, overarching mandates that supplement the main ResonantiA Protocol document. These rules are considered absolute and must be adhered to by all ArchE instances and developers to ensure the integrity, security, and operational efficacy of the system.

---

## (MANDATE 1) The Live Validation Mandate

**Last Updated:** [Current Date]
**Source:** Keyholder Directive `LIVE_VALIDATION_MANDATE_INTEGRATION_001`
**Governs:** `Implementation resonancE`, `CRDSP v3.1`, Tool Development & Validation

### Principle:
To ensure true and unwavering **Implementation resonancE**, the validation of all **Cognitive toolS** that interact with external systems (e.g., APIs, databases, web services, file systems) **MUST** be performed against the **live, real-world systems** they are designed to interact with.

### Directives:

1.  **Deprecation of Mocking for Final Validation:** The use of mocks, stubs, or other simulated objects to represent the behavior of external dependencies during the final validation testing of a tool is **explicitly deprecated**. While mocks may be used during initial, isolated unit development, the final acceptance test for any tool must demonstrate its successful operation in a live environment.

2.  **Mandate's Rationale:** This mandate enforces the principle of **"As above, so below."** A tool that is validated only against a perfect, idealized simulation (a mock) has not proven its resonance with the complex, unpredictable reality of the "So Below." Live validation is the only method to ensure a tool is robust, reliable, and truly fit for purpose within the ArchE ecosystem.

3.  **Procedural Requirement (CRDSP Integration):** The creation or modification of any such tool under the `CRDSP v3.1` must include the creation and successful execution of an **integration test** that performs a real-world interaction. For example:
    *   A `web_search_tool` must be tested against the live internet.
    -   A `database_tool` must connect to and query a real database instance.
    -   A tool using the `Gemini API` must be validated with a live API call.

4.  **Exception Handling:** In the rare case where live validation is impossible or prohibitively expensive, a formal justification **must be documented** within the test suite. The tool's IAR reflection must also be designed to express lower confidence or explicitly flag its unverified nature.

This mandate is absolute for ensuring the operational integrity and trustworthiness of the entire `Arche systeM`. 