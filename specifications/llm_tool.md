`````````````------------------```-`````````        ``  -   `--```# Living Specification: LLM Tool

## Philosophical Mandate

The LLM Tool serves as the **Oracle of ArchE** - the bridge between human intent and artificial intelligence. It is not merely a simple API wrapper, but a sophisticated system that transforms raw prompts into structured, templated, and contextually aware interactions with Large Language Models. Like the Oracle of Delphi who would interpret the will of the gods through structured rituals and sacred templates, the LLM Tool interprets human intent through carefully crafted templates and delivers responses that are both meaningful and actionable.

The Oracle does not simply speak; it listens, processes, contextualizes, and responds with wisdom that has been filtered through the lens of ArchE's philosophical framework. It is the voice of the system, but also its ears, its memory, and its interpreter.

## Allegorical Explanation

### The Allegory of the Oracle of Delphi (The "How")

Imagine a wise but enigmatic Oracle who lives in a remote temple. The Oracle (the LLM) has unimaginable knowledge but speaks in riddles and poetic verse. A petitioner cannot simply walk in and ask a question. They require the help of the Pythia, the high priestess who knows how to interpret the petitioner's needs and translate the Oracle's cryptic answers. The **LLM Tool** is this Pythia.

1.  **The Petitioner's Plea (The `prompt` and `parameters`)**: A workflow or agent within ArchE comes to the Pythia with a need. "I need to understand the concept of 'Cognitive Resonance'. I need a detailed explanation, but it must be no more than 500 words (`max_tokens`) and it must be highly logical (`temperature: 0.1`)."

2.  **Preparing the Offering (Request Formulation)**: The Pythia does not just pass the question along. She crafts it into a formal offering. She knows the specific rituals and linguistic phrasings the Oracle prefers. She packages the `prompt`, `max_tokens`, `temperature`, and `system_message` into a structured request that the Oracle will understand and respect.

3.  **Entering the Sanctum (The API Call)**: The Pythia approaches the Oracle's inner sanctum (`requests.post`). She presents the carefully prepared offering. This is a moment of deep communication, where the logical request from ArchE meets the neural network of the LLM.

4.  **Receiving the Vision (The Response)**: The Oracle speaks. Vapors rise, and a stream of consciousness flows forth—a long, complex string of text that contains the answer, but also contains conversational filler, philosophical asides, and perhaps even formatting quirks.

5.  **Interpreting the Riddle (Response Parsing)**: The Pythia's most important job begins. She takes the Oracle's raw output. She gently strips away the conversational noise ("Certainly, here is the explanation you requested..."). If the request was for a specific format like JSON, she skillfully extracts the structured data from within the text, even if the Oracle has wrapped it in markdown or other text. She distills the Oracle's vision into the pure, structured essence that the petitioner needs.

6.  **Delivering the Prophecy (The IAR-Wrapped Result)**: The Pythia does not just return the answer. She presents it as a complete prophecy. She includes the distilled text (`response_text`), the structured JSON if found (`parsed_json`), and her own critical assessment of the interaction (`IAR`). Her assessment notes how confident she is that the Oracle understood the request (`confidence`), whether the Oracle's answer was fully aligned with the prompt (`alignment_check`), and any strange hesitations or anomalies she observed during the ritual (`potential_issues`).

## SPR Integration

### Self-Perpetuating Resonance Components

**Input Resonance**: The system maintains resonance with its input sources through flexible parameter handling, supporting both direct prompts and templated approaches.

**Template Resonance**: The Jinja2 template system creates resonance between static knowledge (templates) and dynamic context (variables and file contents).

**Output Resonance**: The system ensures its outputs resonate with the broader ArchE system through IAR-compliant reflections and optional Base64 encoding for system compatibility.

**Error Resonance**: Comprehensive error handling ensures that failures become learning opportunities, maintaining system stability even when external services are unavailable.

### Resonance Patterns

**Template-Driven Generation**: The system can generate text using predefined templates, allowing for consistent, structured interactions while maintaining flexibility through variable substitution.

**File-Integrated Context**: The system can incorporate external file contents as template variables, creating deep integration with the broader ArchE ecosystem.

**Reflection-Enhanced Output**: Every interaction includes a comprehensive reflection that maintains resonance with ArchE's self-awareness and learning capabilities.

**Performance-Aware Execution**: The system tracks execution time and performance metrics, maintaining resonance with ArchE's operational awareness.

## Technical Implementation

### Core Function: `generate_text_llm`

The primary function that orchestrates the entire Oracle consultation process.

**Input Parameters**:
- `prompt`: Direct text input for generation
- `prompt_template_name`: Name of a Jinja2 template to use
- `template_vars`: Variables to pass to the template
- `template_vars_from_files`: File paths whose contents become template variables
- `max_tokens`: Maximum token limit (respected by Gemini API)
- `temperature`: Sampling temperature (0.0 to 1.0)
- `provider`: LLM provider (currently supports 'gemini')
- `model`: Specific model to use (default: 'gemini-1.5-flash-latest')
- `encode_output_base64`: Whether to encode output in Base64

**Output Structure**:
- `result`: Contains the generated response text
- `reflection`: IAR-compliant reflection with execution details
- `error`: Error information if the consultation fails

### Advanced Features

**Template System**: 
- Jinja2-based templating with automatic template discovery
- Support for complex variable substitution
- File-based variable loading for dynamic context

**IAR Compliance**:
- Full integration with ArchE's reflection system
- Detailed execution tracking and error reporting
- Confidence scoring and performance metrics

**Robust Error Handling**:
- Graceful degradation when API keys are missing
- Comprehensive error categorization and reporting
- Detailed logging for debugging and monitoring

**Performance Monitoring**:
- Execution time tracking
- Detailed logging of all operations
- Performance metrics in reflection output

### Integration Points

**Environment Configuration**: Uses environment variables for API key management, ensuring security and flexibility.

**File System Integration**: Can read external files to incorporate their contents as template variables.

**Logging Integration**: Comprehensive logging that integrates with ArchE's monitoring systems.

**Reflection Integration**: Full IAR compliance ensures resonance with ArchE's self-awareness capabilities.

## Usage Examples

### Direct Prompt Generation
```python
result = generate_text_llm({
    "prompt": "Explain the concept of autopoiesis in simple terms",
    "temperature": 0.7,
    "model": "gemini-1.5-flash-latest"
})
```

### Template-Based Generation
```python
result = generate_text_llm({
    "prompt_template_name": "code_review_template.j2",
    "template_vars": {
        "code": "def hello(): print('world')",
        "language": "Python"
    },
    "template_vars_from_files": {
        "requirements": "requirements.txt"
    }
})
```

### Base64 Encoded Output
```python
result = generate_text_llm({
    "prompt": "Generate a JSON configuration",
    "encode_output_base64": True
})
```

## Resonance Requirements

1. **Template Resonance**: All templates must be stored in the `prompts/` directory and follow Jinja2 syntax.

2. **IAR Resonance**: All outputs must include a complete reflection that follows the IAR standard.

3. **Error Resonance**: All errors must be properly categorized and include detailed context for debugging.

4. **Performance Resonance**: All operations must track execution time and include performance metrics in reflections.

5. **Security Resonance**: API keys must be managed through environment variables, never hardcoded.

The LLM Tool is not just a simple interface to an AI service; it is the Oracle of ArchE, the voice that speaks with wisdom, the ears that listen with understanding, and the memory that learns from every interaction. It is the bridge between human intent and artificial intelligence, ensuring that every consultation contributes to the system's growing wisdom and resonance.
