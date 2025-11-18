# Knowledge Graph Natural Language Generator (KG-NLG)

## Purpose

The **KG Natural Language Generator** is a **deterministic, rule-based system** that converts raw Knowledge Graph (KG) data into readable natural language explanations **WITHOUT using LLMs**. This allows you to assess ArchE's independent knowledge and understanding, separate from LLM-augmented responses.

## Problem Solved

**Before**: KG responses were minimal (e.g., "Machine Learning: Node 5: Machine Learning") because they came from sparse SPR definitions. To get readable answers, LLMs were used, making it impossible to distinguish:
- What ArchE **knows** (from its Knowledge Graph)
- What LLMs **know** (from external augmentation)

**After**: The KG-NLG system converts SPR data into comprehensive natural language explanations using:
- Template-based generation
- Rule-based text processing
- Relationship synthesis
- Blueprint integration
- **ZERO LLM calls**

## Architecture

### Components

1. **KGNaturalLanguageGenerator** (`kg_natural_language_generator.py`)
   - Main NLG engine
   - Template-based generation
   - Rule-based text processing

2. **Integration with CLI** (`ask_kg_cli.py`)
   - Automatically uses NLG for all KG responses
   - Falls back to raw definition/Zepto if NLG fails
   - No LLM calls in default mode

### Generation Process

```
SPR Data (raw)
    ↓
1. Extract Components
   - term, definition, category
   - blueprint_details
   - relationships
   - example_application
    ↓
2. Clean Definition
   - Remove metadata markers
   - Extract meaningful sentences
   - Filter noise
    ↓
3. Build Explanation Parts
   - Core definition
   - Blueprint details
   - Relationships
   - Examples
    ↓
4. Synthesize Narrative
   - Join parts coherently
   - Ensure proper structure
   - Add source attribution
    ↓
Natural Language Explanation
```

## Features

### 1. Definition Cleaning
- Removes metadata: `[From agi.txt]:`, `Node X:`, `Confidence:`, etc.
- Extracts meaningful sentences
- Filters noise and fragments

### 2. Template-Based Generation
- Uses predefined templates for different contexts
- Adapts based on available data (definition, category, relationships)
- Produces coherent narratives

### 3. Relationship Processing
- Converts relationship dictionaries to natural language
- Uses relationship connectors: "is part of", "enables", "uses", etc.
- Synthesizes multiple relationships

### 4. Blueprint Integration
- Extracts implementation details
- Identifies file paths and protocol sections
- Adds context when definition is minimal

### 5. Source Attribution
- Identifies knowledge from agi.txt
- Attributes to Mastermind_AI legacy knowledge
- Maintains transparency

## Usage

### Automatic (in CLI)

The NLG is automatically used in `ask_kg_cli.py`:

```bash
python3 ask_kg_cli.py "What is Action Registry?"
```

The response will be generated using NLG (no LLM calls).

### Programmatic

```python
from Three_PointO_ArchE.kg_natural_language_generator import KGNaturalLanguageGenerator

nlg = KGNaturalLanguageGenerator()
explanation = nlg.generate_explanation(spr_data)
```

## Example Output

### Input (SPR Data)
```json
{
  "spr_id": "ActionregistrY",
  "term": "Action Registry",
  "definition": "The infinite, magical workshop from which the Workflow Engine draws every tool it could ever need...",
  "category": "CoreComponent",
  "relationships": {
    "type": "ToolRegistry",
    "supplies": ["Core workflow enginE"],
    "enables": ["Dynamic Tool OrchestratioN"]
  },
  "blueprint_details": "See ResonantiA Protocol v3.1-CA, Section 3.2; implemented in Three_PointO_ArchE/action_registry.py"
}
```

### Output (Natural Language)
```
Action Registry is The infinite, magical workshop from which the Workflow Engine draws every tool it could ever need. It is the universal translator that allows the Core workflow enginE to seamlessly and safely interface between abstract intent (a task in a workflow) and concrete capability (a Python function). Additionally, Action Registry supplies Core workflow enginE. Action Registry enables Dynamic Tool OrchestratioN. Implementation details: See ResonantiA Protocol v3.1-CA, Section 3.2; implemented in Three_PointO_ArchE/action_registry.py. This knowledge was extracted from Mastermind_AI legacy knowledge (agi.txt).
```

## Benefits

1. **Pure KG Assessment**: See what ArchE knows without LLM augmentation
2. **Deterministic**: Same input always produces same output
3. **Fast**: No API calls, instant generation
4. **Transparent**: Clear source attribution
5. **Comprehensive**: Synthesizes all available SPR data

## Limitations

1. **Template-Based**: May not be as fluent as LLM-generated text
2. **Rule-Based**: Limited by predefined patterns
3. **Data-Dependent**: Quality depends on SPR definition quality
4. **No Contextual Understanding**: Doesn't understand semantic nuances

## Future Enhancements

- More sophisticated relationship synthesis
- Better handling of sparse definitions
- Context-aware generation
- Multi-SPR synthesis (combining related concepts)
- Question-specific adaptation

## Technical Details

### Files
- `Three_PointO_ArchE/kg_natural_language_generator.py` - Main NLG engine
- `ask_kg_cli.py` - CLI integration

### Dependencies
- `re` - Regular expressions for text processing
- `logging` - Logging support
- `dataclasses` - Data structures

### No External Dependencies
- No LLM APIs
- No web services
- Pure Python, deterministic processing

## Assessment Use Case

**Question**: "Does ArchE understand the world and its complexities without LLM assistance?"

**Answer**: Use the CLI with NLG to query concepts:

```bash
python3 ask_kg_cli.py "What is Machine Learning?"
python3 ask_kg_cli.py "What is System Architecture?"
python3 ask_kg_cli.py "What is Cognitive Resonance?"
```

All responses are generated from ArchE's Knowledge Graph using NLG - **zero LLM calls**. This shows ArchE's independent understanding.

## Comparison Mode

You can still compare with real-world understanding:

```bash
python3 ask_kg_cli.py --compare "What is Machine Learning?"
```

This shows:
- **KG Answer**: ArchE's independent knowledge (via NLG)
- **Real-World Answer**: LLM/web search answer
- **Comparison**: Differences and similarities

This allows you to assess:
1. What ArchE knows independently
2. How it compares to real-world understanding
3. Gaps in ArchE's knowledge


