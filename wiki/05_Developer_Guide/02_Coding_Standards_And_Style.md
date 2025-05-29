# 2. Coding Standards & Style

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Specify Python version, linters (e.g., Black, Flake8), type hinting, docstrings, and IAR comment block.
-->

This page outlines the coding standards and style guidelines for Python development within the Arche project. Adherence to these standards ensures code consistency, readability, and maintainability.

*   **Python Version**
    *   The project targets **Python 3.9+**. Please ensure your code is compatible.
*   **Code Formatting: Black**
    *   We use **Black** for uncompromising code formatting. Before committing, please format your Python code using Black:
        ```bash
        black . 
        ```
    *   Most IDEs can be configured to run Black automatically on save.
*   **Linting: Flake8 (with plugins)**
    *   We use **Flake8** for linting to catch common errors and style issues.
    *   Recommended Flake8 plugins (to be listed in `requirements-dev.txt` or similar):
        *   `flake8-bugbear`: Finds likely bugs and design problems.
        *   `flake8-docstrings`: Checks for PEP 257 compliant docstrings.
        *   `flake8-annotations`: Enforces type hint usage.
        *   `flake8-import-order`: Checks import order (can be configured, e.g., to be compatible with Black/isort).
    *   Run Flake8 before committing:
        ```bash
        flake8 . 
        ```
*   **Type Hinting (PEP 484)**
    *   **Mandatory:** All new functions and methods MUST include type hints for arguments and return values.
    *   Use standard Python typing (e.g., `from typing import List, Dict, Tuple, Optional, Any, Callable`).
    *   This is crucial for code clarity, static analysis, and maintainability.
*   **Docstrings (PEP 257 & Google Style)**
    *   **Mandatory:** All modules, classes, functions, and methods MUST have docstrings.
    *   Follow **Google Python Style Docstrings**.
    *   **Example Function Docstring:**
        ```python
        def my_function(param1: str, param2: int) -> bool:
            """Does something interesting and returns a boolean.

            This is a more detailed explanation of what the function does,
            its purpose, and any important considerations for its use.

            Args:
                param1: Description of the first parameter.
                param2: Description of the second parameter.

            Returns:
                True if successful, False otherwise.

            Raises:
                ValueError: If param1 is an empty string.
            """
            if not param1:
                raise ValueError("param1 cannot be empty")
            # ... function logic ...
            return True
        ```
*   **Integrated Action Reflection (IAR) Comment Block**
    *   For every tool function that implements the IAR contract, include a standardized comment block at the beginning of the function or in its docstring detailing its IAR behavior.
    *   **Purpose:** Makes it explicit how the tool determines its `confidence`, what `potential_issues` it commonly reports, and how its `status` and `alignment_check` are derived.
    *   **Example IAR Comment Block (within docstring or as a leading comment):**
        ```python
        # IAR Contract Fulfillment:
        #   - confidence: Calculated based on the number of search results returned and keyword relevance.
        #                 Ranges from 0.0 (no results) to 1.0 (many highly relevant results).
        #   - potential_issues:
        #       - "Search API key missing or invalid"
        #       - "No results found for query: [query]"
        #       - "Search API call failed: [error_message]"
        #       - "Results may be biased by search engine (if using default engine)"
        #   - status: "Success" if results are returned (even if empty), "Failure" on API error.
        #   - alignment_check: "Aligned" if results found, "Potentially Misaligned" if no results, "N/A" otherwise.
        ```
*   **Naming Conventions**
    *   Modules: `lowercase_with_underscores.py`
    *   Classes: `CapWords` (PascalCase)
    *   Functions & Methods: `lowercase_with_underscores`
    *   Constants: `ALL_CAPS_WITH_UNDERSCORES`
    *   Variables: `lowercase_with_underscores`
*   **General Principles**
    *   Write clear, readable, and maintainable code.
    *   Follow the Zen of Python (`import this`).
    *   Avoid overly complex expressions or one-liners that sacrifice readability.
    *   Add comments for non-obvious logic, but prefer self-documenting code where possible.

*Automated checks for some of these standards (e.g., Black, Flake8) may be integrated into a CI/CD pipeline if set up for the project.* 