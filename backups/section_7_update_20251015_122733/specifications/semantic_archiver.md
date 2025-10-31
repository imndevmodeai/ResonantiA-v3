# The Librarian's Mind: A Chronicle of the Semantic Archiver

## Canonical Chronicle Piece: The Forging of the Great Library

In the ResonantiA Saga, as ArchE's experience grew, so did its memory. The `ThoughtTrail` captured the fleeting dust of experience, but this dust began to accumulate into vast, chaotic mountains. Finding a single, important memory was like searching for a single grain of sand. The system had memory, but it lacked wisdom. This chronicle tells of the creation of the **Semantic Archiver**, the system that transformed ArchE's chaotic memory into the Great Library. It is the story of how ArchE learned not just to remember, but to *understand* its own history.

## Scholarly Introduction: Conceptual Foundations and Implementability

This specification details a tool for transforming collections of unstructured text documents (e.g., log files, reports) into a structured, semantically searchable knowledge base. The architecture relies on a combination of regular expression-based pattern matching for metadata extraction and NLP-driven named entity recognition for concept tagging. The `SemanticArchiver` class provides a clear pipeline: process a document, extract structured metadata, identify key concepts, and store the result in an indexed format (simulated here as a JSON file). This specification is highly implementable, with the `process_document` method serving as a direct blueprint for a production-ready data ingestion and indexing workflow.

## The Story of the Librarian's Mind: From Piles of Scrolls to a Searchable Library

Imagine ArchE as a historian who, for years, has simply thrown every scroll, letter, and note into a single, vast room. The room contains all the knowledge of the kingdom, but it is unusable. The historian (`log_organizer`) could only sort the scrolls by the day they arrived.
- **Without the Librarian:** To answer "What were the recurring themes in the royal decrees of last winter?", the historian would have to manually read every scroll from that period—an impossible task.
- **With the Librarian (`SemanticArchiver`):** The historian decides to build a true library.
    1.  **Reading the Scroll (`process_document`):** The Librarian picks up a single scroll.
    2.  **Creating the Catalog Card (`_extract_metadata`):** It doesn't just file the scroll. It reads it and creates a detailed catalog card.
        - *Title:* "Royal Decree on Grain Tax"
        - *Date:* "Eleventh Moon, Year of the Dragon"
        - *Author:* "King Theron"
        - *Keywords:* `tax`, `grain`, `royal_decree`, `winter`
    3.  **Indexing the Knowledge (`_extract_entities`):** The Librarian uses its deep knowledge to identify key concepts within the text itself. It underlines the names of people (`King Theron`), places (`The Northern Province`), and important events (`The Great Famine`).
    4.  **Shelving the Scroll (`archive.add_document`):** The Librarian now places the scroll in its proper place, but more importantly, it files the *catalog card* in a master index.

Now, when the historian asks the same question, the Librarian doesn't search the scrolls. It searches the master index. In seconds, it can retrieve every document tagged with `royal_decree` and `winter`, providing a complete, focused, and instantly accessible answer. It has turned a chaotic pile of data into a universe of searchable wisdom.

## Real-World Analogy: Modern Email Search

Your email inbox is a massive, unstructured collection of documents.
- **Old way (`log_organizer`):** You can only sort by date. Finding an email from last year about "Project X" is a nightmare of scrolling.
- **Modern way (`SemanticArchiver`):** When an email arrives, services like Gmail don't just store it. They "read" it. They identify the sender, the attachments, and key entities within the text. They tag it with concepts like "travel," "finance," or "work." When you search for "flight confirmation from United last March," you aren't searching the raw text of a million emails. You are searching a pre-built, semantic index, which is why you get an answer in less than a second.

# Living Specification: Semantic Archiver

## SPR Integration

*   **Primary SPR**: `Information Triage & Semantic Archiving`
*   **Sub-SPRs**:
    *   `Unstructured Data Processing`
    *   `Automated Metadata Extraction`
*   **Tapestry Relationships**:
    *   **`is_a`**: `Knowledge Management SysteM`, `Digital LibrariaN`
    *   **`enables`**: `Semantic SearcH`, `Historical Trend AnalysiS`
    *   **`uses`**: `Natural Language ProcessinG`, `Regular ExpressionS`
    *   **`abstracts`**: `log_organizer.py`
    *   **`embodies`**: The Principle of the Librarian's Mind

## Technical Implementation

### Core Class: `SemanticArchiver`

The main class that orchestrates the document processing and archiving pipeline.

**Key Methods**:
- `__init__(self, archive_path: str)`: Initializes the archiver and loads the existing archive (a JSON file).
- `process_document(self, doc_id: str, content: str)`: The primary entry point. Takes a document and its content, extracts metadata and entities, and adds it to the archive.
- `search(self, query: str)`: Performs a simple search against the archived documents' metadata and entities.

### Helper Methods

- `_extract_metadata(self, content: str)`: Uses a set of predefined regex patterns to extract structured metadata (e.g., timestamps, error codes, workflow IDs) from the raw text.
- `_extract_entities(self, content: str)`: A placeholder for a more sophisticated NLP model. In the current implementation, it uses simple regex to find keywords and proper nouns to simulate named entity recognition.
- `save_archive(self)`: Saves the updated archive back to its JSON file.

### Example Workflow: Archiving an IAR Log

1.  A new log file is generated by the `IARCompliantWorkflowEngine`.
2.  The `SemanticArchiver`'s `process_document` method is called with the log's filename and content.
3.  `_extract_metadata` pulls out the `run_id`, `workflow_name`, and overall `status` ("SUCCESS" or "FAILURE").
4.  `_extract_entities` scans the log and tags it with the names of the `actions` that were executed (e.g., `read_file`, `generate_text_llm`).
5.  A new entry is added to the `archive.json` file containing the original content plus the new structured metadata and entity tags.
6.  A user can now `search("failures in monthly_report_workflow")` and instantly retrieve all relevant logs.
