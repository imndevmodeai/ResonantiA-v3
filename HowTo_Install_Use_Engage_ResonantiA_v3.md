# ResonantiA v3.0: HowTo_Install_Use_Engage.md

This document provides instructions for installing, using, and engaging with the ResonantiA v3.0 project, specifically the `Three_PointO_ArchE` package.

## 1. Installation

These instructions assume a Python 3.9+ environment.

**1.1. Virtual Environment Setup:**

Creating a virtual environment is strongly recommended for isolating project dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/macOS
.venv\Scripts\activate  # On Windows
```

**1.2. Package Installation:**

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

**1.3. API Key Configuration:**

ResonantiA v3.0 may require API keys for various services (e.g., LLMs, vector databases).  **Never** hardcode API keys directly in your code. Instead, use environment variables.

```bash
# Example (adapt to your specific API keys)
export OPENAI_API_KEY="your_openai_api_key"
export PINECONE_API_KEY="your_pinecone_api_key" 
# ... other API keys
```

**1.4. Code Executor Sandbox (Docker - Optional):**

If `CODE_EXECUTOR_SANDBOX_METHOD` is set to `docker` in your configuration, ensure Docker is installed and running.  This provides a sandboxed environment for code execution.  The `Three_PointO_ArchE` package will handle Docker interaction automatically if configured correctly.


## 2. Basic Usage

**2.1. Running a Workflow:**

Workflows are executed using the `main` module:

```bash
python -m Three_PointO_ArchE.main <workflow_name> <arguments>
```

For example, to execute the `example_workflow` with input `"Hello, world!"`:

```bash
python -m Three_PointO_ArchE.main example_workflow "Hello, world!"
```

**2.2. Interpreting JSON Outputs:**

The output of each workflow execution is a JSON object. This object contains the results of each task in the workflow, including the final output.

**2.3. Understanding IAR Reflections:**

Each task's output within the JSON includes an `reflection` dictionary, which is the IAR (Internal Action Reflection). This dictionary provides insights into the task's execution, including:

* `reasoning`: The reasoning behind the actions taken by the task.
* `actions`: A list of actions performed.
* `observations`: Observations made during execution.
* `hypotheses`: Any hypotheses formed.
* `uncertainties`: Identified uncertainties or potential issues.

Examining the `reflection` dictionary is crucial for understanding the behavior and decision-making process of each task within a workflow.

## 3. Advanced Features

**3.1. Leveraging IAR in Workflows:**

IAR data can be used to dynamically adjust workflow execution. For example, a task can examine the `reflection` of a previous task to make informed decisions.

**3.2. Temporal Tools:**

ResonantiA v3.0 provides tools for temporal reasoning, including:

* **Prediction:** Forecasting future states based on past data.
* **Causal Inference:** Identifying cause-and-effect relationships.
* **Agent-Based Modeling (ABM):** Simulating complex systems.

**3.3. Meta-cognitive Patterns:**

These patterns enable higher-level reasoning and self-improvement:

* **SIRC (Sense-Interpret-Respond-Critique):** A cycle for iterative learning and adaptation.
* **Metacognitive Shift:** Changing the level of abstraction or perspective.
* **Insight Solidification:** Consolidating new knowledge and integrating it into existing understanding.

**3.4. Keyholder Override (`Keyy`):**

The Keyholder Override mechanism (using the provided `Keyy`) allows direct intervention in the system's operation.  **Use with extreme caution.**  This feature is primarily for debugging, emergency intervention, or overriding potentially harmful actions.  Improper use can compromise system integrity and safety.  Consult the ResonantiA Protocol v3.0 documentation for detailed guidelines.

## 4. Creating a New Project Instance

1. Create a new directory for your project.
2. Copy the core files and directory structure from the `Three_PointO_ArchE` package.
3. Adapt the `config.yaml` file to your specific needs.
4. Create new workflows within the `workflows` directory.
5. Populate the `agents` directory with any custom agents.
6. Install the required dependencies as described in Section 1.


This `HowTo_Install_Use_Engage.md` document is part of the ASASF Canonical Self-Definition Package for ResonantiA v3.0.  Refer to the full protocol documentation for comprehensive details. 