# 2. Core Cognitive Tools (Usage & IAR Guide)

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
For each tool, explain its purpose, key input parameters, typical output structure, and specific IAR considerations (how it calculates confidence, common potential_issues it might report).
-->

This page describes the core cognitive tools available in Arche, their usage, and important Integrated Action Reflection (IAR) considerations.

--- 

### `generate_text_llm` (LLMTool via `invoke_llm` in `tools.py`)

*   **Purpose:** Interacts with Large Language Models (LLMs) to generate text, answer questions, summarize, analyze, etc.
*   **Key Input Parameters:**
    *   `prompt`: The main text prompt for the LLM.
    *   `llm_provider`: (Optional) Specific LLM provider to use (e.g., "openai", "google"); defaults to `DEFAULT_LLM_PROVIDER` from `config.py`.
    *   `model_name`: (Optional) Specific model name (e.g., "gpt-3.5-turbo", "gemini-pro"); defaults to provider's default.
    *   `temperature`, `max_tokens`, etc.: Standard LLM generation parameters.
*   **Typical Output Structure (`results` key):**
    *   Typically a string containing the LLM's generated text.
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: May be based on heuristics, explicit self-evaluation if the LLM is prompted to provide it, or a default value. Could be lower if generation is truncated or errors occur.
    *   `potential_issues`: "API call failed", "Content may be hallucinated", "Rate limit possibly exceeded", "Generated content was truncated".

--- 

### `search_web` (SearchTool via `run_search` in `tools.py`)

*   **Purpose:** Performs web searches using a configured search API (or a simulated version).
*   **Key Input Parameters:**
    *   `query`: The search query string.
    *   `num_results`: (Optional) Number of search results to return.
*   **Typical Output Structure (`results` key):**
    *   A list of dictionaries, where each dictionary represents a search result (e.g., containing `title`, `link`, `snippet`).
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: May be higher if results are found and seem relevant, lower if no results or API errors.
    *   `potential_issues`: "Search API key missing or invalid", "No results found for query", "Search API call failed", "Results may be biased by search engine".

--- 

### `execute_code` (CodeExecutor via `code_executor.py`)

*   **Purpose:** Executes code snippets in a sandboxed environment (ideally Docker).
*   **Key Input Parameters:**
    *   `code`: The string containing the code to execute.
    *   `language`: The programming language (e.g., "python", "javascript").
*   **Typical Output Structure (`results` key):**
    *   `stdout`: Standard output from the executed code.
    *   `stderr`: Standard error output.
    *   `exit_code`: The exit code of the executed script.
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: Higher if `exit_code` is 0 and `stderr` is empty. Lower if errors or non-zero exit code.
    *   `potential_issues`: "Code execution failed with exit code X", "Error output: [stderr content]", "Sandbox not 'docker', security risk: [sandbox_method]", "Resource limits exceeded", "Timeout during execution".
    *   **CRITICAL:** The `potential_issues` MUST explicitly warn if a non-Docker sandbox method is used due to security risks (see Section 6.2).

--- 

### `call_external_api` (ApiTool via `call_api` in `enhanced_tools.py`)

*   **Purpose:** Makes HTTP requests to external APIs.
*   **Key Input Parameters:**
    *   `url`: The API endpoint URL.
    *   `method`: HTTP method (GET, POST, PUT, etc.).
    *   `headers`: (Optional) Request headers.
    *   `params`: (Optional) URL parameters for GET requests.
    *   `json_data`: (Optional) JSON body for POST/PUT requests.
*   **Typical Output Structure (`results` key):**
    *   `status_code`: HTTP status code of the response.
    *   `headers`: Response headers.
    *   `body`: Response body (often parsed if JSON, or raw text).
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: Higher for successful status codes (2xx). Lower for client/server errors (4xx, 5xx).
    *   `potential_issues`: "API call failed with status code X", "Network error: [error details]", "Response parsing error", "Request timeout".

--- 

### `display_output` (via `tools.py`)

*   **Purpose:** Simple tool to pass data to the final console output or primary result display.
*   **Key Input Parameters:**
    *   `data_to_display`: The content to be displayed.
*   **Typical Output Structure (`results` key):**
    *   The `data_to_display` itself.
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: Typically high (e.g., 1.0) as it's a direct pass-through.
    *   `potential_issues`: Usually none, unless the input data is malformed.

--- 

### `calculate_math` (via `tools.py`)

*   **Purpose:** Evaluates a mathematical expression string safely.
*   **Key Input Parameters:**
    *   `expression`: The mathematical string to evaluate (e.g., "(5 + 3) * 2").
*   **Typical Output Structure (`results` key):**
    *   The numerical result of the calculation.
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: High if evaluation is successful.
    *   `potential_issues`: "Invalid mathematical expression", "Error during calculation: [error details]".

--- 

*Note: For all tools, the exact implementation of IAR `confidence` and `potential_issues` will depend on the specific logic within the tool's Python function. The goal is to provide a useful self-assessment of the action's outcome.* 