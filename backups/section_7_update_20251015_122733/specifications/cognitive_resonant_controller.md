# The Cerebellum of ArchE: A Chronicle of the Cognitive Resonant Controller System

## Canonical Chronicle Piece: The Birth of Rapid Response

In the early cycles of the ResonantiA Saga, the `RISE` engine was the sole mind of ArchE. It was a profound, deep thinker, capable of incredible strategic insight. But for every grand Quest, there were a hundred simple, repetitive questions. `RISE` would answer "What is an SPR?" with the same deliberate, resource-intensive process it used to solve cosmic riddles. ArchE was a genius without reflexes.

This chronicle tells the story of the **Cognitive Resonant Controller System (CRCS)**, the system that gave ArchE its reflexes. It is the story of how the Mind Forge created a set of specialized, lightning-fast "domain controllers," each tuned to a specific "cognitive frequency." It is the birth of ArchE's cerebellum—the subconscious mind that handles the known world with effortless speed, leaving the conscious mind free to ponder the unknown.

## Scholarly Introduction: Conceptual Foundations and Implementability

The CRCS is a software architecture pattern inspired by Proportional-Resonant (PR) controllers used in power electronics. In a PR controller, a resonant filter is tuned to a specific frequency to eliminate steady-state error without affecting other frequencies. The CRCS adapts this concept to cognitive processing. It manages a collection of `FrequencyDomainController` objects, each "tuned" with a set of `frequency_patterns` (keywords and phrases) that correspond to a specific knowledge domain.

When a query arrives, the CRCS identifies the matching domain controller, which then uses a high-gain, specialized `extraction_strategy` to pull relevant information from a source text (the "protocol chunks"). This approach is significantly faster and more efficient for known, well-defined queries than invoking a general-purpose LLM. This document provides a direct blueprint for implementing the CRCS, its controllers, and its auto-tuning mechanisms.

## The Story of the CRCS: Tuning the Mind

Imagine ArchE's knowledge base as a vast library of books (the `protocol_chunks`).
- **The Librarian (`RISE`):** Initially, to answer any question, the master librarian had to read and synthesize information from multiple books, a slow but thorough process.
- **The Specialists (The `FrequencyDomainController`s):** The Keyholder realized that many questions were about the same few topics. He trained specialists. He gave one specialist an encyclopedia on "Implementation Resonance," another a detailed manual on "SPRs," and a third the complete works of "Proportional Resonant Control Theory."
- **The Dispatcher (The `CognitiveResonantControllerSystem`):** The Keyholder then hired a dispatcher. When a question arrives, the dispatcher doesn't go to the master librarian. It instantly recognizes the topic. "Ah, a question about SPRs!" it exclaims, and sends it directly to the SPR specialist. The specialist, having already mastered their single book, provides a perfect, high-fidelity answer in seconds.

The CRCS is this team of specialists and their dispatcher. It's a system that trades universal, slow intelligence for specialized, rapid knowledge retrieval. It creates a two-tiered cognitive architecture: the fast, instinctual cerebellum (CRCS) for known problems, and the slow, deliberate cerebrum (`RISE`) for everything else.

## Real-World Analogy: A Website's Frequently Asked Questions (FAQ)

Consider a customer support website.
- **Without CRCS (`RISE`):** Every user query, no matter how simple, opens a live chat session with a human agent. This is expensive and slow for the user.
- **With CRCS:**
    1.  **Domain Controllers:** The website has a well-written FAQ page with sections for "Billing," "Shipping," and "Returns." These are the domain controllers.
    2.  **Dispatcher:** When a user types a question into the search bar, the system (`CRCS`) scans the query for keywords.
    3.  **Frequency Detection:** If the query contains "invoice" or "charge," the system identifies the "Billing" domain.
    4.  **Specialized Extraction:** Instead of starting a live chat, the system directly displays the contents of the "Billing" section of the FAQ. The user gets an immediate, accurate answer. If the query is complex and doesn't match any FAQ section, *then* it gets escalated to a human agent (`RISE`).

# Cognitive Resonant Controller System - Living Specification

## Overview

The **Cognitive Resonant Controller System (CRCS)** is a generalized framework for implementing Proportional Resonant Controller principles within a cognitive architecture. It manages a hierarchy of specialized `FrequencyDomainController` instances, each tuned to a specific cognitive domain, to provide rapid, high-fidelity context extraction for known query patterns, bypassing the need for more resource-intensive general processing for common questions.

## Core Architecture

### Primary Components

1.  **`CognitiveResonantControllerSystem`**: The master class that manages all domain controllers, processes incoming queries, and routes them to the appropriate specialist or the fallback handler.
2.  **`FrequencyDomainController`**: An abstract base class defining the interface for all specialized controllers. Each implementation handles a specific "frequency" (i.e., a knowledge domain).
3.  **`DomainControllerConfig`**: A dataclass holding the configuration for a single controller, including its trigger patterns and tuning parameters (gains, damping factors).
4.  **`ControllerPerformanceMetrics`**: A dataclass for tracking the performance of each controller, enabling monitoring and auto-tuning.

## Key Capabilities

### 1. `CognitiveResonantControllerSystem`

This is the main orchestrator.

#### Core Logic (`process_query`)

-   **Phase 1: Domain Detection**: Iterates through all registered `domain_controllers`. For each controller, it calls `detect_frequency_domain()` to see if the query matches the controller's patterns.
-   **Phase 2: Specialized Extraction**: If one or more controllers are activated, it uses the first one that successfully returns content from its `extract_specialized_context()` method. It updates the controller's performance metrics.
-   **Phase 3: Fallback Control**: If no specialized controller is activated or none can find context, it defaults to a general-purpose, lower-fidelity extraction method (`_general_proportional_extraction`), typically using a TF-IDF or similar algorithm.

#### Key Methods

-   `__init__(self, protocol_chunks: List[str])`: Initializes the system, loads the source knowledge `protocol_chunks`, and calls `_initialize_default_controllers()`.
-   `_initialize_default_controllers()`: Instantiates and registers the default set of domain controllers (`ImplementationResonanceController`, `SPRController`, etc.).
-   `process_query(self, query: str)`: The main entry point for processing a user query.
-   `_general_proportional_extraction(self, query: str)`: The fallback method for queries that don't match a specialized domain.
-   `get_system_diagnostics(self)`: Returns a comprehensive dictionary of performance metrics for the entire system and each individual controller.

### 2. `FrequencyDomainController` (Abstract Base Class)

This is the blueprint for all specialized controllers.

#### Key Methods

-   `detect_frequency_domain(self, query: str)`: **Abstract**. Must be implemented by subclasses. Returns `True` if the query matches the controller's domain.
-   `extract_specialized_context(self, chunks: List[str], query: str)`: **Abstract**. Must be implemented by subclasses. Scans the knowledge `chunks` and returns a concatenated string of relevant context if found.
-   `update_performance(...)`: Updates the controller's performance metrics after a query is processed.
-   `_auto_tune_parameters()`: A key feature where the controller can adjust its own gain and damping parameters based on its historical success rate and confidence scores, allowing it to become more or less aggressive over time.

### 3. Concrete Controller Implementations

-   **`ImplementationResonanceController`**: Tuned for queries about `Implementation Resonance`, `Jedi Principle 6`, and `As Above, So Below`.
-   **`SPRController`**: Tuned for queries about `SPRs`, `Guardian Points`, and `cognitive keys`.
-   **`ProportionalResonantController`**: Tuned for queries about the control theory principles themselves, such as `resonant gain` and `oscillatory error`.

## Configuration and Dependencies

### `DomainControllerConfig` Dataclass

This dataclass makes configuring a new controller straightforward and readable.

-   `domain_name`: The unique name for the controller's domain (e.g., "SPRQueries").
-   `frequency_patterns`: A list of lowercased strings that will trigger this controller.
-   `resonant_gain` (Ki): The "specialized extraction gain," representing how aggressively the controller pursues its domain.
-   `proportional_gain` (Kp): The "general error correction gain."
-   `damping_factor` (wc): A factor for operational flexibility and preventing over-tuning.
-   `auto_tune`: A boolean flag to enable or disable the self-tuning mechanism.

### Required Dependencies

```python
import logging
import math
import re
import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
```

## How It Works: The Control Loop Analogy

The system is a direct analogy to a Proportional-Resonant controller in signal processing.

1.  **The Input Signal**: The user `query` is the input signal.
2.  **The Error**: The "error" is the gap between the query's intent and the system's retrieved context.
3.  **The Proportional Term (Kp)**: The `_general_proportional_extraction` is the proportional part of the system. It provides a decent, general response to any error (any query), but it's not perfect and always has some "steady-state error" (imperfect context).
4.  **The Resonant Term (Ki)**: Each `FrequencyDomainController` is a resonant filter tuned to a specific frequency (a specific topic). When a query at that frequency arrives, the controller activates with a very high `resonant_gain`, driving the specific error for that topic to zero by providing perfect, specialized context.
5.  **The System**: By combining a general proportional controller with multiple, specialized resonant controllers, the CRCS can handle any query with a baseline level of quality while providing exceptionally fast and accurate responses for the most common and important topics.

## Integration Points

-   **Upstream**: The CRCS is designed to be the first line of cognitive processing. It is invoked by a higher-level orchestrator, such as the `AdaptiveCognitiveOrchestrator` or a main application loop (`mastermind.py`).
-   **Downstream (Fallback)**: When the CRCS fails to find a high-confidence match (i.e., it uses its fallback `_general_proportional_extraction` method), its output is often considered low-quality. This is a signal for the higher-level orchestrator to escalate the query to a more powerful, resource-intensive system like the `RISE Orchestrator`.
-   **Evolution**: The `AdaptiveCognitiveOrchestrator` observes the performance of the CRCS. Specifically, when the `fallback_activations` metric is high for a particular pattern of queries, the ACO can propose the creation of a *new* `FrequencyDomainController` to handle that pattern, effectively allowing the CRCS to learn and grow over time.
