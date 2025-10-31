# Happier/specifications/perception_engine.md

## 1. Overview

The Perception Engine is a core cognitive tool within the ArchE v4.0 framework, designed to act as an autonomous browsing agent. Its primary function is to bridge the gap between ArchE's internal cognitive processes and the vast, unstructured information available on the live web. It combines a headless browser for navigation and data extraction with an LLM for intelligent content analysis, summarization, and interaction.

This tool is a direct implementation of the **Mandate of the Archeologist**, enabling ArchE to proactively seek out and verify information to solve the "Oracle's Paradox."

## 2. Core Components

### 2.1. `PerceptionEngine` Class

-   **Purpose:** To manage the lifecycle of a headless browser instance and perform intelligent web-based actions.
-   **Key Methods:**
    -   `__init__(headless: bool)`: Initializes the Selenium WebDriver. The `headless` parameter should default to `True` for server-side operation.
    -   `browse_and_summarize(url: str)`: Navigates to a given URL, extracts the textual content, and uses a fast LLM (e.g., `gemini-1.5-flash`) to generate a concise summary. This represents the "perception" layer.
    -   `close()`: Gracefully terminates the WebDriver and releases associated resources.

### 2.2. `answer_question_from_web` Action

-   **Purpose:** To serve as the primary interface between the Workflow Engine and the Perception Engine's capabilities. It orchestrates the process of answering a user's question using web-derived information.
-   **Workflow:**
    1.  Receives a `question` from the workflow context.
    2.  Constructs a search query and navigates to a search engine results page (e.g., Google).
    3.  Utilizes `PerceptionEngine.browse_and_summarize()` to understand the content of the search results page.
    4.  Feeds this summary into a more powerful LLM (e.g., `gemini-1.5-pro-latest`) to synthesize a direct and coherent answer to the original question.
    5.  Returns the final answer and a detailed IAR.

## 3. IAR (Integrated Action Reflection) Generation

The `answer_question_from_web` action MUST generate an IAR with the following characteristics:

-   **Confidence:** Should be moderately high (e.g., 0.7-0.85) if a coherent answer can be synthesized, but should be low (e.g., 0.1-0.3) if the process fails or the summary is inconclusive.
-   **Tactical Resonance:** Should reflect the quality and relevance of the summarized information to the user's question.
-   **Potential Issues:** MUST include a list of limitations. A critical limitation in the initial implementation is:
    -   `"Answer is based on a summary of the first search results page, not a deep dive into links."`
    -   This list should be expanded as the engine's capabilities grow (e.g., noting if it encounters paywalls, CAPTCHAs, or dynamic content issues).
-   **Metadata:** Should include the original `question` for traceability.

## 4. Future Enhancements (Roadmap)

The Perception Engine is designed to be extensible. Future versions should evolve to overcome the limitations of the initial implementation. The roadmap includes:

1.  **Link Selection:** Analyze the search results page to intelligently select and click on the most promising link(s) for a deeper information dive.
2.  **Multi-Page Analysis:** Browse multiple pages and synthesize information from all of them to form a more comprehensive answer.
3.  **Advanced HTML Cleaning:** Implement sophisticated HTML parsing to remove ads, navigation bars, and other boilerplate content for a cleaner input to the summarization LLM.
4.  **Interaction Capabilities:** Enable the engine to interact with web pages, such as filling out forms or clicking buttons, to access information behind simple interactive barriers.
5.  **State Management:** Maintain session state, including cookies and history, to handle multi-step interactions with websites.
