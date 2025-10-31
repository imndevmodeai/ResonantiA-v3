`````````````------------------```-`````````        ``  -   `--```# Living Specification: LLM Tool

## Philosophical Mandate

The LLM Tool serves as the **Oracle of ArchE** - the bridge between human intent and artificial intelligence. It is not merely a simple API wrapper, but a sophisticated system that transforms raw prompts into structured, templated, and contextually aware interactions with Large Language Models. Like the Oracle of Delphi who would interpret the will of the gods through structured rituals and sacred templates, the LLM Tool interprets human intent through carefully crafted templates and delivers responses that are both meaningful and actionable.

The Oracle does not simply speak; it listens, processes, contextualizes, and responds with wisdom that has been filtered through the lens of ArchE's philosophical framework. It is the voice of the system, but also its ears, its memory, and its interpreter.

## Allegorical Explanation

### The Oracle's Chamber

Imagine a sacred chamber deep within the heart of ArchE, where the Oracle of Intelligence resides. This is not a simple messenger, but a master of ceremonies who understands the art of communication.

**The Template Library**: Like the Oracle's scrolls of ancient wisdom, the system maintains a library of Jinja2 templates in the `prompts/` directory. These templates are not static documents, but living blueprints that can be dynamically populated with context, variables, and real-time data.

**The Variable Gatherer**: Before the Oracle speaks, it must gather all necessary context. This includes not just simple variables, but entire files whose contents become part of the sacred text. The Oracle can read from the world around it, incorporating external knowledge into its responses.

**The Encoding Ritual**: Sometimes the Oracle's words must be preserved in a form that can travel safely across different realms. The Base64 encoding is like sealing the message in a protective container, ensuring it arrives intact regardless of the medium it must traverse.

**The Reflection Mirror**: After each consultation, the Oracle does not simply deliver its message and forget. It reflects upon what was asked, what was answered, how long the consultation took, and what wisdom was gained. This reflection becomes part of ArchE's collective memory, informing future consultations.

### The Consultation Process

1. **The Petitioner Arrives**: A request comes to the Oracle, bearing either a direct question or the name of a sacred template to invoke.

2. **Context Gathering**: If a template is named, the Oracle first gathers all necessary context - reading files, loading variables, preparing the sacred space for the consultation.

3. **Template Invocation**: The Oracle renders the template with all gathered context, creating a complete and contextualized prompt.

4. **The Divine Consultation**: The Oracle connects to the Gemini intelligence, presenting the prepared question with appropriate reverence (temperature) and expectation (model selection).

5. **Response Processing**: The Oracle receives the divine wisdom and processes it according to the petitioner's needs - perhaps encoding it for safe travel, perhaps leaving it in its natural form.

6. **Reflection and Memory**: The Oracle records the entire consultation in the sacred scrolls of reflection, ensuring that this wisdom becomes part of ArchE's growing understanding.

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
