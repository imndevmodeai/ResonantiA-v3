# 3. Configuration (`config.py` Deep Dive)

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Explain the purpose of `config.py`, key settings, and how to modify/use it. Emphasize API key security.
-->

This page provides a detailed explanation of the `config.py` file, which is central to Arche's configuration.

*   **CRITICAL: API Key Management (Secure Guide)**
    *   Emphasize the importance of secure API key handling.
    *   **Using Environment Variables (Recommended Method)**
        *   Provide examples for Linux/macOS (e.g., `export OPENAI_API_KEY='your_key_here'`)
        *   Provide examples for Windows Command Prompt (e.g., `set OPENAI_API_KEY=your_key_here`)
        *   Provide examples for Windows PowerShell (e.g., `$env:OPENAI_API_KEY='your_key_here'`)
        *   Explain how `os.environ.get('API_KEY_NAME')` in `config.py` reads these.
    *   **Why NOT to hardcode keys directly in `config.py` or commit them.**
*   **Structure of `LLM_PROVIDERS` in `config.py`**
    *   Explain the dictionary structure (provider name, api_key, default_model, backup_model, etc.).
    *   How to add new providers or modify existing ones.
*   **Configuring Search API Keys**
    *   Explain `SEARCH_API_KEY` and related settings like `SEARCH_PROVIDER`.
*   **Tool Settings**
    *   **`CodeExecutor` (`CODE_EXECUTOR_*` settings)**
        *   `CODE_EXECUTOR_USE_SANDBOX` (True/False) - Importance of `True`.
        *   `CODE_EXECUTOR_SANDBOX_METHOD` ('docker', 'subprocess', 'none') - Strong recommendation for 'docker'. Security implications of other methods.
        *   `CODE_EXECUTOR_DOCKER_IMAGE` - Specifying the Docker image for sandboxing.
        *   Resource limits (e.g., `_MEM_LIMIT`, `_CPU_LIMIT`).
    *   **Default LLM Provider and Model**
        *   `DEFAULT_LLM_PROVIDER`
        *   `DEFAULT_LLM_MODEL`
    *   **Default parameters for Temporal Tools**
        *   `PREDICTIVE_ARIMA_DEFAULT_ORDER`, etc. for Predictive Modeling Tool.
        *   Default settings for Causal Inference Tool.
        *   Default settings for Agent-Based Modeling Tool.
        *   Default settings for CFP Framework (`CFP_DEFAULT_TIMEFRAME`, etc.).
*   **File Paths**
    *   Understanding `BASE_DIR`, `MASTERMIND_DIR`, `WORKFLOW_DIR`, `KNOWLEDGE_DIR`, `LOG_DIR`, `OUTPUT_DIR`.
    *   How these paths are constructed and used.
*   **Logging Configuration**
    *   `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR, CRITICAL) - Impact on verbosity.
    *   `LOG_FILE` - Path to the log file.
*   **Meta-Cognition Thresholds**
    *   `METAC_DISSONANCE_THRESHOLD_CONFIDENCE` - How it triggers Metacognitive shifT based on IAR confidence. 