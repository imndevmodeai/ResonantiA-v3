# 1. Contribution Guidelines

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Detail the process for contributions: fork, branch, PR, code review, IAR adherence.
-->

This page outlines the guidelines for contributing to the Arche project. We welcome contributions that align with the ResonantiA Protocol and enhance the system's capabilities.

*   **Getting Started**
    *   Familiarize yourself with the [ResonantiA Protocol v3.0 Overview](../01_ResonantiA_Protocol_v3_0/README.md) and the [Arche Architecture](../04_Arche_Architecture_And_Internals/README.md).
    *   Ensure you have completed the [Setup Guide](../02_Getting_Started_with_Arche/02_Setup_Guide.md).
*   **Contribution Process**
    1.  **Fork the Repository:** Create your own fork of the main Arche repository.
    2.  **Create a Branch:** For each new feature, bug fix, or documentation update, create a new branch in your fork. Use a descriptive branch name (e.g., `feature/new-cfp-observable`, `fix/code-executor-timeout`).
    3.  **Make Your Changes:** Implement your changes, adhering to the [Coding Standards & Style](./02_Coding_Standards_And_Style.md).
        *   **CRITICAL: IAR Adherence:** If adding or modifying tools, ensure strict adherence to the [Integrated Action Reflection (IAR) contract](../04_Arche_Architecture_And_Internals/04_Action_Registry_and_Tool_Integration.md#the-integrated-action-reflection-iar-contract-mandatory-for-all-tools). This is non-negotiable.
        *   **Update Documentation:** If your changes affect user-facing functionality, architecture, or require new configuration, update the relevant Wiki pages or code documentation.
        *   **Add Tests:** Write unit tests and/or integration tests for your changes. See [Testing & Debugging](./06_Testing_And_Debugging.md).
    4.  **Commit Your Changes:** Use clear and concise commit messages.
    5.  **Push to Your Fork:** Push your branch to your forked repository.
    6.  **Submit a Pull Request (PR):**
        *   Open a Pull Request from your branch to the `main` (or appropriate development) branch of the upstream Arche repository.
        *   Provide a clear description of your changes in the PR: what problem it solves, how it was implemented, and any relevant context.
        *   Link to any relevant issues.
*   **Code Review Process**
    *   At least one core developer (or designated reviewer) will review your PR.
    *   Reviewers will check for adherence to coding standards, IAR contract, correctness, test coverage, and documentation.
    *   Be prepared to discuss your changes and make revisions based on feedback.
*   **Merging**
    *   Once the PR is approved and passes all checks, it will be merged by a core developer.
*   **Communication**
    *   For significant changes or new features, it's a good idea to discuss your plans by opening an issue first to get feedback before starting development.
    *   Use project issues for bug reports and feature requests.

*By following these guidelines, you help maintain the quality, consistency, and integrity of the Arche project.* 