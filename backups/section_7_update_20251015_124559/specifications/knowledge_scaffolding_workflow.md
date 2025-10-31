# The Foundation Forge: Knowledge Scaffolding Workflow

## Canonical Chronicle Piece: The Architect's First Blueprint

In the ResonantiA Saga, when ArchE encounters a truly novel problem—one for which no instinct exists, no prior experience illuminates the path—it must become an architect of knowledge itself. The **Knowledge Scaffolding Workflow** is the story of how ArchE transforms raw curiosity into specialized expertise, forging the very cognitive tools needed to solve problems it has never seen before.

Like an ancient architect who must first understand the properties of stone, wood, and metal before designing a cathedral, ArchE must first acquire domain knowledge, understand the problem's deep structure, and forge a specialized cognitive agent before attempting synthesis. This is not mere preparation; it is the act of self-creation that enables all subsequent thought.

---

## Scholarly Introduction: Conceptual Foundations and Implementability

The Knowledge Scaffolding Workflow implements a multi-phase approach to domain acquisition and specialist agent creation, drawing from principles of domain-specific learning, knowledge graph construction, and adaptive expertise development. This workflow addresses the fundamental challenge in AI systems: how to solve problems in domains where no prior training exists.

Conceptually, it models ArchE's learning as a **bootstrapping process** where general reasoning capabilities are used to acquire domain knowledge, which is then used to forge domain-specific analytical tools. This creates a self-reinforcing cycle where each new domain mastered expands the system's capability to master subsequent domains.

Implementability is central: This specification provides both the philosophical mandate and the precise JSON schema required to recreate the workflow. The workflow can be executed manually (human analysts following the phases) or automatically (the Workflow Engine processing the JSON definition). All LLM invocations use the 3-tier model selection hierarchy, all web searches are IAR-logged, and all outputs are SPR-compatible.

---

## The Story of Knowledge Scaffolding: A Narrative of Cognitive Bootstrapping

Imagine ArchE as a master craftsperson entering a completely new workshop—one filled with tools they've never seen, materials they've never touched, problems they've never solved. Most systems would fail here, paralyzed by novelty. But ArchE possesses a meta-skill: **the ability to learn how to learn**.

### Phase 1: Deconstruction (Understanding the Territory)
ArchE first stares at the problem, not to solve it, but to **understand its shape**. What are the core components? What domains of knowledge will be required? What are the success criteria? This is like an architect surveying a building site, understanding the terrain, the constraints, the vision.

**The Insight**: You cannot build without understanding what you're building.

### Phase 2: Domain Acquisition (Gathering the Materials)
With the problem's structure understood, ArchE ventures into the vast library of human knowledge (the web) to gather domain-specific information. It doesn't gather randomly—it searches with purpose, guided by the deconstruction. It's like the architect gathering books on structural engineering, seismic design, local building codes—exactly what's needed, nothing more.

**The Insight**: Raw knowledge is worthless without context and curation.

### Phase 3: Specialization Analysis (Understanding the Required Skills)
ArchE now looks at the gathered knowledge and asks: "What kind of expert would be needed to solve this?" What frameworks? What methodologies? What analytical lenses? It's like the architect realizing they need not just general engineering knowledge, but specific expertise in tensile structures and load distribution.

**The Insight**: Generalists struggle where specialists thrive.

### Phase 4: Agent Forging (Creating the Specialist)
This is the moment of transformation. ArchE doesn't just "use" the knowledge—it **becomes** a specialist. It forges a Specialized Cognitive Agent (SCA): a virtual expert with domain knowledge, analytical frameworks, and problem-solving patterns specific to this challenge. It's like the architect temporarily becoming a master of Gothic architecture to design a cathedral, then a master of seismic engineering to design an earthquake-resistant tower.

**The Insight**: The system that can forge its own experts can solve any problem.

### Phase 5: Validation (Testing the Foundation)
Before proceeding, ArchE validates the forged agent. Is it complete? Does it have the necessary capabilities? Are there gaps? This is the architect checking their own blueprint before construction begins.

**The Insight**: A flawed foundation dooms all subsequent work.

---

## Real-World Analogy: Google's AlphaFold Approach

To anchor this in reality, consider DeepMind's AlphaFold solving protein folding:

**Traditional Approach**: Use a general-purpose neural network trained on all protein data. Result: Mediocre performance, struggles with novel proteins.

**AlphaFold Approach (Knowledge Scaffolding)**:
1. **Deconstruct**: Understand the protein folding problem's core physics (energy minimization, spatial constraints)
2. **Acquire Domain Knowledge**: Ingest protein databases, evolutionary data, physics principles
3. **Analyze Specialization**: Identify need for multi-scale analysis (atomic, residue, domain levels)
4. **Forge Specialist**: Create specialized neural architecture (attention mechanisms for spatial relationships, iterative refinement)
5. **Validate**: Test on known proteins before novel predictions

This mirrors ArchE's workflow: decompose, learn, specialize, forge, validate.

---

## Detailed Workflows: How Knowledge Scaffolding Operates

### Input Parameters
```json
{
  "problem_description": "The user's query or problem statement",
  "session_id": "Unique identifier for tracking this scaffolding session",
  "model": "Optional LLM model override (uses 3-tier fallback if not specified)"
}
```

### Task Execution Flow

#### Task 1: `deconstruct_problem`
**Purpose**: Analyze problem structure and identify requirements

**Action**: `generate_text_llm`

**Prompt Template**:
```
Analyze the following problem and deconstruct it into core components:

{problem_description}

Identify:
1. Core domain areas
2. Key variables and unknowns
3. Strategic requirements
4. Risk factors
5. Success criteria

Output your analysis as a structured JSON object with a key 'deconstruction_text'.
```

**Model Settings**:
- `model`: `{{ model }}` (uses 3-tier hierarchy)
- `temperature`: 0.3 (analytical, structured output)
- `max_tokens`: 8192 (comprehensive analysis - optimized for quality)

**Output**: `deconstruction_text` containing structured problem analysis

**Dependencies**: None (first task)

---

#### Task 2: `extract_domain_from_deconstruction`
**Purpose**: Extract primary domain for focused knowledge acquisition

**Action**: `generate_text_llm`

**Prompt Template**:
```
From the following JSON analysis, identify and extract only the single, most relevant 'Core domain area'. 
Your output must be a single, clean JSON object with one key: 'domain'. 

Example: {"domain": "Artificial Intelligence Strategy"}

Analysis:
{deconstruct_problem.result.generated_text}
```

**Model Settings**:
- `temperature`: 0.1 (deterministic extraction)
- `max_tokens`: 500 (simple extraction - optimized for speed)

**Output**: `domain` string (e.g., "Quantum Computing", "Strategic Planning")

**Dependencies**: [`deconstruct_problem`]

---

#### Task 3: `acquire_domain_knowledge`
**Purpose**: Gather authoritative domain-specific information

**Action**: `search_web`

**Inputs**:
```json
{
  "query": "{{ extract_domain_from_deconstruction.result.output.domain or problem_description }}",
  "num_results": 5
}
```

**Resilience Strategy**: Uses conditional Jinja2 template - if domain extraction fails, falls back to full `problem_description` for search.

**Output**: Web search results containing domain knowledge

**Dependencies**: [`extract_domain_from_deconstruction`]

---

#### Task 4: `validate_search_results`
**Purpose**: Ensure knowledge quality before proceeding

**Action**: `generate_text_llm`

**Prompt Template**:
```
Evaluate the quality and relevance of the following domain knowledge for the problem:

Problem: {problem_description}
Domain Knowledge: {acquire_domain_knowledge.result}

Output a JSON object:
{
  "search_is_valid": true/false,
  "quality_score": 0.0-1.0,
  "relevance_issues": ["list any problems"],
  "recommendations": "suggestions if quality is low"
}
```

**Model Settings**:
- `temperature`: 0.2 (structured evaluation)
- `max_tokens`: 1500 (validation report)

**Output**: `search_is_valid` boolean + quality assessment

**Dependencies**: [`acquire_domain_knowledge`]

---

#### Task 5: `analyze_specialization_requirements`
**Purpose**: Identify what kind of expert is needed

**Action**: `generate_text_llm`

**Condition**: `{{ validate_search_results.result.output.search_is_valid }} == true`

**Prompt Template**:
```
Based on the problem deconstruction and domain knowledge, analyze what specialized capabilities 
and expertise are required:

Problem: {problem_description}
Deconstruction: {deconstruct_problem.result.generated_text}
Domain Knowledge: {acquire_domain_knowledge.result}

Identify:
1. Required specialized knowledge areas
2. Critical analytical capabilities
3. Strategic thinking patterns
4. Risk assessment frameworks
5. Implementation expertise
```

**Model Settings**:
- `temperature`: 0.4 (analytical with some flexibility)
- `max_tokens`: 8192 (comprehensive analysis)

**Output**: Detailed specialization requirements

**Dependencies**: [`validate_search_results`]

---

#### Task 6: `forge_specialist_agent`
**Purpose**: Create the Specialized Cognitive Agent (SCA)

**Action**: `generate_text_llm`

**Prompt Template**:
```
Create a specialized agent profile for solving this problem:

Problem: {problem_description}
Requirements: {analyze_specialization_requirements.result.generated_text}

Define:
1. Agent's core expertise and background
2. Analytical frameworks and methodologies
3. Strategic thinking patterns
4. Risk assessment capabilities
5. Implementation approach
6. Success metrics and validation criteria
```

**Model Settings**:
- `temperature`: 0.3 (structured agent creation)
- `max_tokens`: 16384 (comprehensive agent profile - THIS IS THE CORE DELIVERABLE)

**Rationale for 16K tokens**: The Specialized Cognitive Agent is the **primary output** of this entire workflow. It must contain:
- Detailed domain expertise
- Complete analytical frameworks
- Strategic thinking patterns
- Risk assessment methodologies
- Implementation guidance
- Validation criteria

This is not a summary—it's a fully-formed cognitive tool that subsequent workflows will use.

**Output**: Complete SCA profile (stored in `session_knowledge_base`)

**Dependencies**: [`analyze_specialization_requirements`]

---

#### Task 7: `validate_specialist_agent`
**Purpose**: Ensure agent completeness before use

**Action**: `generate_text_llm`

**Prompt Template**:
```
Validate the completeness of this specialized agent:

Agent Profile: {forge_specialist_agent.result.generated_text}
Original Problem: {problem_description}

Check for:
1. Completeness of expertise
2. Adequacy of frameworks
3. Alignment with problem requirements
4. Gaps or weaknesses

Output JSON:
{
  "agent_is_valid": true/false,
  "completeness_score": 0.0-1.0,
  "identified_gaps": ["list any gaps"],
  "recommendations": "improvements if needed"
}
```

**Model Settings**:
- `temperature`: 0.2 (structured validation)
- `max_tokens`: 1500 (validation report)

**Output**: `agent_is_valid` boolean + quality metrics

**Dependencies**: [`forge_specialist_agent`]

---

## Output Schema

```json
{
  "session_knowledge_base": {
    "problem_deconstruction": "...",
    "domain": "...",
    "domain_knowledge": "...",
    "specialization_requirements": "...",
    "specialized_agent": "...",
    "validation": {
      "knowledge_valid": true,
      "agent_valid": true,
      "completeness_score": 0.95
    }
  },
  "session_id": "scaffolding_12345",
  "processing_metadata": {
    "total_duration_ms": 12500,
    "llm_calls": 6,
    "model_used": "gemini-2.5-flash",
    "token_usage": {
      "input_tokens": 15000,
      "output_tokens": 25000
    }
  }
}
```

---

## SPR Integration and Knowledge Tapestry Mapping

### Primary SPR
`KnowledgeScaffoldinG` - The capability to bootstrap domain expertise from first principles

### Sub-SPRs
- `DomainAcquisitioN` - Web-based knowledge gathering
- `SpecialistForganG` - Creating domain-specific cognitive tools
- `CognitiveBootstrappinG` - Meta-learning capability

### Tapestry Relationships
- **`is_a`**: Meta-WorkfloW, DomainAdaptationProceS
- **`part_of`**: RISE Orchestrator Phase A
- **`enables`**: NovelProblemSolvinG, DynamicExpertisE
- **`uses`**: WebSearchTooL, LLMProvideR, SPRManageR
- **`embodies`**: UniversalAbstractioN (learning to learn)

---

## IAR Compliance

Every task in this workflow is IAR-logged:

```python
{
  "intention": "knowledge_scaffolding/deconstruct_problem",
  "action": "Analyzed problem structure using LLM",
  "reflection": "Successfully identified 5 core domains and 12 key variables",
  "confidence": 0.92,
  "metadata": {
    "model_used": "gemini-2.5-flash",
    "tokens_used": 3500,
    "duration_ms": 2100
  }
}
```

---

## Cost Optimization Strategy

### Token Allocation by Priority

**High-Priority Tasks** (16K tokens):
- `forge_specialist_agent` - THE core output, cannot truncate

**Medium-Priority Tasks** (8K tokens):
- `deconstruct_problem` - Needs comprehensive analysis
- `analyze_specialization_requirements` - Detailed understanding required

**Low-Priority Tasks** (500-1500 tokens):
- `extract_domain_from_deconstruction` - Simple extraction
- `validate_search_results` - Binary validation
- `validate_specialist_agent` - Structured check

**Total Cost per Execution** (with `gemini-2.5-flash` @ $0.30/1M output tokens):
- Input: ~15K tokens × $0.075/1M = $0.001125
- Output: ~25K tokens × $0.30/1M = $0.0075
- **Total: ~$0.0086 per scaffolding session** ✅

---

## Integration Points

### With RISE Orchestrator
- **Direction**: RISE Phase A → Knowledge Scaffolding
- **Data**: `problem_description`, `session_id`
- **Output**: `session_knowledge_base` (SCA profile)
- **Usage**: SCA used in all subsequent RISE phases

### With Workflow Engine
- **Execution**: IARCompliantWorkflowEngine
- **Model Injection**: Automatic via `initial_context["model"]`
- **Error Handling**: All tasks have IAR-compliant error paths

### With SPR Manager
- **Direction**: Knowledge Scaffolding → SPR Manager
- **Data**: New domain SPRs created from forged agent
- **Frequency**: Post-validation, if agent approved by Guardian

---

## Success Criteria

Knowledge Scaffolding is working when:

1. ✅ Deconstruction identifies all key problem components
2. ✅ Domain extraction succeeds or falls back gracefully
3. ✅ Web search returns relevant, high-quality knowledge
4. ✅ Validation catches low-quality knowledge
5. ✅ Specialization analysis is comprehensive
6. ✅ Forged agent is complete and usable
7. ✅ Final validation confirms agent quality
8. ✅ SCA can be used by subsequent workflows
9. ✅ All tasks are IAR-logged
10. ✅ No truncation on critical outputs (agent profile)

---

## Performance Characteristics

- **Total Duration**: 8-15 seconds (6 LLM calls + 1 web search)
- **CRCS Direct**: Not applicable (this IS deep thought)
- **RISE Escalation**: Always (this is Phase A of RISE)
- **Memory Usage**: ~100MB (transient for session)
- **Cost per Session**: ~$0.0086 (Flash model)

---

## Known Limitations

1. **Web Search Quality**: Dependent on search results relevance
2. **Domain Extraction**: May fail on extremely novel/abstract problems
3. **Single-Domain Focus**: Currently extracts one primary domain
4. **No Multi-Agent Fusion**: Forges one specialist, not a team
5. **Static Scaffolding**: Doesn't adapt during execution

---

## Future Enhancements

1. **Multi-Domain Scaffolding**: Extract and forge multiple specialists
2. **Iterative Refinement**: Loop back if validation fails
3. **Knowledge Graph Integration**: Store domain knowledge persistently
4. **Agent Evolution**: Update existing SCAs with new knowledge
5. **Parallel Scaffolding**: Multiple domains simultaneously

---

## Guardian Notes

**Review Points**:
1. Is the forged agent comprehensive enough for the problem?
2. Are validation checks catching low-quality knowledge?
3. Is domain extraction working or always falling back?
4. Are token limits appropriate for output quality?
5. Is cost per session acceptable?

**Approval Checklist**:
- [ ] Deconstruction is thorough and structured
- [ ] Domain knowledge is relevant and high-quality
- [ ] Specialization analysis is comprehensive
- [ ] Forged agent has all required capabilities
- [ ] Validation confirms agent completeness
- [ ] No critical truncation observed
- [ ] IAR logging is complete

---

**Specification Status**: ✅ COMPLETE  
**Implementation**: `workflows/knowledge_scaffolding.json`  
**Version**: 1.1 (Token-Optimized)  
**Last Updated**: 2025 (Token Limit Optimization)  
**Integration Level**: ★★★★★ (Core RISE Phase A Workflow)  
**Autopoiesis Level**: ★★★★☆ (Self-Creating Expertise)

