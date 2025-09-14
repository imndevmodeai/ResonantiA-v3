# The Weaver of KnO: A Chronicle of the Knowledge Graph Manager

## 1. Living Specification: `knowledge_graph_manager.py`

- **Canonical Name**: `The Weaver of KnO`
- **Version**: `1.0`
- **Status**: `Active`
- **Maintainer**: `B.J. Lewis`
- **Reviewers**: `ArchE`

---

## 2. Introduction: Charting the Cognitive Territory

This specification documents the **Knowledge Graph Manager (`knowledge_graph_manager.py`)**, a strategic component of the ArchE system responsible for building and maintaining the holistic, in-memory map of the system's entire cognitive territory. This map is referred to as the **Knowledge Tapestry**.

While the `SPRManager` is the focused librarian of individual SPR definitions, the `KnowledgeGraphManager` is the master cartographer and weaver. It transcends individual files and concepts to construct a unified, queryable graph of how all knowledge assets—SPRs, workflows, specifications, and potentially even code modules—are interconnected. It is the implementation of the conceptual `ProjectDependencyMaP` and the engine that gives structure and meaning to the `Knowledge Network Oneness (KnO)`.

---

## 3. Core Responsibilities

-   **Knowledge Tapestry Initialization**: Maintain an in-memory graph structure (a dictionary acting as an adjacency list) to store the nodes and relationships of the KnO.
-   **Node Management**: Provide methods (`add_node`, `get_node`) to add and retrieve knowledge assets (nodes) in the graph. Each node is identified by a unique ID and contains its full metadata.
-   **Relationship Weaving**: Provide a method (`add_relationship`) to establish directed, typed links between nodes (e.g., `SPR:RISE` -> `implemented_in` -> `Code:rise_orchestrator.py`).
-   **Automated Graph Construction**: Implement the `weave_graph_from_directory` method, which acts as the core automated weaver. This method is responsible for:
    -   Recursively scanning the project directory.
    -   Identifying different types of knowledge assets based on file type and location (e.g., `.json` in `knowledge_graph/` are SPRs, `.json` in `workflows/` are workflows).
    -   Parsing these files to extract nodes and their explicit relationships (e.g., parsing the `relationships` dictionary within an SPR definition).
    -   Populating the `knowledge_tapestry` with the discovered nodes and relationships.
-   **Queryability**: Offer methods to query the graph, such as retrieving a node and its direct connections, which is essential for dependency analysis and impact assessment.

## 4. Code Blueprint & Signatures

```python
# knowledge_graph_manager.py

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class KnowledgeGraphManager:
    """
    Builds and manages the Knowledge Tapestry, a graph representation
    of the entire ArchE knowledge network (KnO).
    """
    def __init__(self):
        """Initializes the manager with an empty knowledge tapestry."""
        self.knowledge_tapestry: Dict[str, Dict[str, Any]] = {}
        logger.info("Knowledge Graph Manager initialized. The loom is ready.")

    def add_node(self, node_id: str, node_type: str, node_data: Dict[str, Any]):
        """
        Adds a knowledge asset (node) to the tapestry.
        """
        # ... implementation details ...

    def add_relationship(self, source_id: str, target_id: str, relationship_type: str):
        """
        Adds a directed, typed relationship between two nodes.
        """
        # ... implementation details ...

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Retrieves a node and its data from the tapestry.
        """
        # ... implementation details ...

    def weave_graph_from_directory(self, base_path: Path):
        """
        Scans a directory to automatically build the knowledge graph
        by identifying and parsing SPRs, workflows, and other assets.
        This is the heart of the weaver.
        """
        logger.info(f"Weaving the Knowledge Tapestry from directory: {base_path}")
        # ... implementation details for file traversal and parsing ...
        
        # Example pseudo-code for parsing an SPR file:
        # for spr_file in base_path.glob("knowledge_graph/*.json"):
        #     spr_definitions = json.load(spr_file)
        #     for spr in spr_definitions:
        #         spr_id = spr.get("spr_id")
        #         self.add_node(spr_id, "SPR", spr)
        #         if "relationships" in spr:
        #             for rel_type, targets in spr["relationships"].items():
        #                 for target in targets:
        #                     self.add_relationship(spr_id, target, rel_type)

    def display_graph_summary(self):
        """
        Prints a summary of the woven graph to the console.
        """
        # ... implementation details ...
```

---

## 5. Implementation Resonance & Dependencies

### 5.1. "As Above, So Below"

-   **High Resonance**: The current implementation of `knowledge_graph_manager.py` exhibits high resonance with this specification. It successfully abstracts the concept of the knowledge graph from the underlying file storage, providing a clear API for building and querying the `Knowledge Tapestry`.
-   **Synergy with `SPRManager`**: The relationship between this manager and the `SPRManager` is a prime example of good architectural design. The `KnowledgeGraphManager` does not need to know *how* to parse SPRs efficiently from text; it only needs to know how to ingest the structured data that the `SPRManager` can provide (or that it can parse directly from the JSON definitions). This separation of concerns allows each component to excel at its specific task.

### 5.2. Dependencies

-   **`knowledge_graph_manager.py`** is dependent on:
    -   `json`, `logging`, `pathlib` (Standard Library)

### 5.3. SPR Integration

-   **Primary Definer**: The `KnowledgeGraphManager` is the primary component that understands and interprets the `relationships` section within SPR definitions. It is responsible for transforming those declarative links into actual, navigable edges within the in-memory graph.
-   **Holistic View**: While the `SPRManager` can tell you *what* an SPR is, the `KnowledgeGraphManager` can tell you *where it fits* in the grander scheme, showing its connections to other SPRs, the code that implements it, and the workflows that use it. It is the component that makes the `Knowledge Network Oneness` a tangible, traversable reality.
