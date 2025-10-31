# Living Specification: Prompt Management System

## Philosophical Mandate

The Prompt Management System serves as the **Sacred Scribe of ArchE** - the master of all forms of communication between human intent and artificial intelligence. It is not a single component, but a distributed network of specialized prompt systems, each serving a distinct purpose in the grand orchestration of ArchE's cognitive processes. Like the ancient scribes who maintained different libraries for different types of knowledge - legal texts, religious scriptures, scientific treatises, and philosophical discourses - the Prompt Management System maintains specialized prompt libraries for different cognitive tasks.

The Sacred Scribe does not simply store and retrieve prompts; it crafts them with precision, adapts them to context, and ensures they resonate with ArchE's philosophical framework. It is the guardian of communication protocols, the curator of cognitive frameworks, and the architect of meaningful dialogue between human and artificial intelligence.

## Allegorical Explanation

### The Great Library of Prompts

Imagine a vast, multi-chambered library within the heart of ArchE, where the Sacred Scribe maintains different collections of wisdom, each serving a specific purpose in the system's cognitive processes.

**The Truth-Seeking Chamber**: This is where the Proactive Truth Resonance Framework (PTRF) resides. Like Tesla's methodical approach to invention, this chamber contains prompts that follow a four-phase process:
1. **Hypothetical Model Generation**: Creating initial, confident hypotheses
2. **Lowest Confidence Vector Identification**: Finding the weakest link in the hypothesis
3. **Targeted Verification**: Systematically testing the weakest claim
4. **Synthesis**: Integrating verification results into a refined, trustworthy answer

**The Vetting Chamber**: This chamber houses the ResonantiA Protocol v3.0 vetting system. Like a master craftsman who inspects every detail before approving a work, this system analyzes proposed actions through multiple lenses:
- Logical consistency with previous steps
- Protocol alignment with ArchE's principles
- Action appropriateness and efficiency
- Risk and ethical assessment
- Resonance with the broader system

**The Template Workshop**: Here, Jinja2 templates are crafted and maintained. These are not static documents, but living blueprints that can be dynamically populated with context, variables, and real-time data. Like a master weaver who creates patterns that can be adapted to different materials, these templates provide structure while maintaining flexibility.

**The Integration Forge**: This is where all the different prompt systems come together. The LLM Tool serves as the forge master, taking templates, rendering them with context, and executing them with the appropriate AI models.

### The Scribe's Workflow

1. **Request Analysis**: When a cognitive task is requested, the Sacred Scribe analyzes what type of prompt system is needed.

2. **Template Selection**: Based on the task type, the appropriate prompt template or framework is selected from the relevant chamber.

3. **Context Gathering**: The system gathers all necessary context - variables, file contents, previous step results - to populate the template.

4. **Template Rendering**: The template is rendered with the gathered context, creating a complete and contextualized prompt.

5. **Execution**: The prompt is executed through the appropriate AI model with the specified parameters.

6. **Reflection and Learning**: The results are analyzed and incorporated into the system's growing understanding.

## SPR Integration

### Self-Perpetuating Resonance Components

**Framework Resonance**: Each prompt framework (PTRF, ResonantiA, etc.) maintains resonance with its specific cognitive domain while contributing to the overall system coherence.

**Template Resonance**: The Jinja2 template system creates resonance between static knowledge (templates) and dynamic context (variables and file contents).

**Vetting Resonance**: The vetting system ensures that all actions maintain resonance with ArchE's principles and previous step results.

**Integration Resonance**: The distributed nature of the system creates multiple points of resonance, allowing for specialized optimization while maintaining overall coherence.

### Resonance Patterns

**Multi-Phase Truth Seeking**: The PTRF creates resonance between hypothesis generation and verification, ensuring that claims are systematically tested.

**IAR-Integrated Vetting**: The vetting system maintains resonance with previous step reflections, creating a continuous learning loop.

**Template-Driven Generation**: The template system creates resonance between structured knowledge and dynamic context.

**Distributed Specialization**: Different prompt systems maintain resonance with their specific domains while contributing to overall system coherence.

## Technical Implementation

### Core Components

**`truth_seeking_prompts.py`**:
- **Purpose**: Implements the Proactive Truth Resonance Framework (PTRF)
- **Key Functions**:
  - `format_truth_seeking_prompt()`: Formats prompts with parameters
  - `get_available_prompts()`: Lists available prompt types
- **Prompt Types**:
  - `generate_hypothetical_answer_model`: Creates initial hypotheses
  - `identify_lowest_confidence_vector`: Finds weakest claims
  - `triangulate_and_verify_sources`: Performs targeted verification
  - `synthesize_solidified_truth_packet`: Integrates verification results
  - `handle_verification_conflicts`: Manages conflicting information
  - `handle_verification_failure`: Handles verification failures

**`vetting_prompts.py`**:
- **Purpose**: Implements ResonantiA Protocol v3.0 vetting system
- **Key Functions**:
  - `format_vetting_prompt()`: Formats vetting prompts with IAR integration
  - `perform_scope_limitation_assessment()`: Assesses problem scope limitations
  - `format_synergistic_vetting_prompt()`: Creates synergistic vetting prompts
- **Features**:
  - IAR data integration from previous steps
  - Synergistic Fusion Protocol for scope limitation assessment
  - Comprehensive risk and ethical assessment
  - Logical consistency checking

**Jinja2 Templates**:
- **Location**: `Three_PointO_ArchE/prompts/` directory
- **Template Types**:
  - `code_generation_from_spec.j2`: Code generation from specifications
  - `self_specification_prompt.j2`: Self-specification generation
  - `expert_query_generation.j2`: Expert query formulation
  - `domain_identification.j2`: Domain identification
  - `user_query_parser.j2`: User query parsing

**`llm_tool.py`**:
- **Purpose**: Template rendering and execution engine
- **Key Features**:
  - Jinja2 template loading and rendering
  - File-based variable loading
  - IAR-compliant execution
  - Base64 output encoding
  - Performance monitoring

### Advanced Features

**Multi-Phase Frameworks**:
- **PTRF**: Four-phase truth-seeking process with systematic verification
- **ResonantiA v3.0**: Comprehensive vetting with IAR integration
- **Synergistic Fusion Protocol**: Scope limitation assessment for complex problems

**Template System**:
- **Dynamic Rendering**: Templates can be populated with real-time context
- **File Integration**: External file contents can be incorporated as variables
- **Error Handling**: Robust error handling for template rendering failures
- **Performance Monitoring**: Execution time tracking and logging

**IAR Integration**:
- **Reflection Analysis**: Vetting prompts analyze previous step reflections
- **Confidence Tracking**: System tracks confidence levels across steps
- **Issue Propagation**: Problems identified in one step inform subsequent steps
- **Learning Loop**: Each interaction contributes to system understanding

**Distributed Architecture**:
- **Specialized Components**: Each prompt system optimized for its domain
- **Loose Coupling**: Components can evolve independently
- **Shared Standards**: Common interfaces and protocols
- **Integration Points**: Clear integration with broader ArchE system

### Integration Points

**Environment Configuration**: Uses environment variables for API key management and configuration.

**File System Integration**: Can read external files to incorporate their contents as template variables.

**Logging Integration**: Comprehensive logging that integrates with ArchE's monitoring systems.

**Reflection Integration**: Full IAR compliance ensures resonance with ArchE's self-awareness capabilities.

**Workflow Integration**: Integrates with the Workflow Engine for complex multi-step processes.

## Usage Examples

### Truth-Seeking Framework
```python
# Generate initial hypothesis
hypothesis_prompt = format_truth_seeking_prompt(
    "generate_hypothetical_answer_model",
    query="What is the best approach to climate change?",
    initial_context="Current scientific consensus and policy options"
)

# Identify weakest claim
lcv_prompt = format_truth_seeking_prompt(
    "identify_lowest_confidence_vector",
    query="What is the best approach to climate change?",
    hypothetical_model=hypothesis_result
)

# Perform targeted verification
verification_prompt = format_truth_seeking_prompt(
    "triangulate_and_verify_sources",
    query="What is the best approach to climate change?",
    lowest_confidence_vector=lcv_result
)
```

### Vetting System
```python
# Format vetting prompt with IAR integration
vetting_prompt = format_vetting_prompt(
    objective="Analyze climate change data",
    previous_result=previous_step_result,  # Includes IAR reflection
    current_thought="The data suggests immediate action is needed",
    current_action="execute_code",
    action_inputs={"code": "climate_analysis_script.py"}
)

# Perform scope limitation assessment
scope_assessment = perform_scope_limitation_assessment(
    objective="Analyze climate change data",
    current_thought="The data suggests immediate action is needed",
    action_inputs={"code": "climate_analysis_script.py"},
    context={"user_concerns": "economic impact"}
)
```

### Template Rendering
```python
# Use Jinja2 template with file-based variables
result = generate_text_llm({
    "prompt_template_name": "code_generation_from_spec.j2",
    "template_vars": {
        "specification": "Create a function that sorts a list",
        "language": "Python"
    },
    "template_vars_from_files": {
        "requirements": "requirements.txt",
        "existing_code": "current_implementation.py"
    }
})
```

## Resonance Requirements

1. **Framework Resonance**: All prompt frameworks must maintain alignment with ArchE's philosophical principles while serving their specific domains.

2. **Template Resonance**: All templates must be stored in the `prompts/` directory and follow Jinja2 syntax with proper error handling.

3. **IAR Resonance**: All prompt systems must integrate with the IAR system, analyzing previous reflections and contributing to future understanding.

4. **Vetting Resonance**: All proposed actions must go through appropriate vetting that considers logical consistency, protocol alignment, and ethical implications.

5. **Integration Resonance**: All prompt systems must integrate seamlessly with the broader ArchE system, contributing to overall coherence and learning.

6. **Performance Resonance**: All prompt operations must track execution time and include performance metrics for system optimization.

The Prompt Management System is not just a collection of text templates; it is the Sacred Scribe of ArchE, the master of all forms of communication, the guardian of cognitive frameworks, and the architect of meaningful dialogue between human and artificial intelligence. It ensures that every interaction contributes to the system's growing wisdom and resonance, maintaining the delicate balance between specialized expertise and overall coherence. 