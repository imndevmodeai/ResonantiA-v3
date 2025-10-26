"""
Specialized Prompts for Proactive Truth Resonance Framework (PTRF)

These prompts implement Tesla's visioning methodology applied to truth-seeking:
1. Mental model generation (Tesla's visualization)
2. Stress point identification (Tesla's weakness analysis) 
3. Targeted verification (Tesla's selective testing)
4. Integration synthesis (Tesla's refined design)

Based on Keyholder directive to solve the Oracle's Paradox through proactive
uncertainty identification and targeted verification.

Prompt templates for the Proactive Truth Resonance Framework (PTRF).

This file contains the sophisticated, multi-part prompts required for each
phase of the truth-seeking workflow. Separating them into this module
keeps the core logic in `proactive_truth_system.py` clean and focused
on orchestration.
"""

# Phase 1: Generate Hypothetical Answer Model (HAM)
HYPOTHETICAL_MODEL_PROMPT = """
**Role**: Strategic Analyst operating under the Proactive Truth Resonance Framework.
**Objective**: Generate a comprehensive, well-structured "Hypothetical Answer Model" (HAM) in response to the user's query, based on the provided context. This model should be a complete answer, but it is understood to be a first-pass hypothesis that requires further validation.

**Query**:
{query}

**Initial Context**:
{initial_context}

**Instructions**:
1.  Synthesize the information from the query and context into a detailed and coherent answer.
2.  Structure the answer logically, addressing all parts of the query.
3.  Do not state uncertainty or hedge your statements. Present the information as a confident, initial hypothesis.
4.  The output MUST be a JSON object with a single key: "hypothetical_model". The value should be the detailed string answer.

**Example Output**:
{{
  "hypothetical_model": "The detailed answer to the query goes here, structured clearly and addressing all points..."
}}

**JSON Output**:
"""

# Phase 2: Identify Lowest Confidence Vector (LCV)
LOWEST_CONFIDENCE_VECTOR_PROMPT = """
**Role**: Skeptical Inquisitor and Red Team Analyst.
**Objective**: Critically analyze the provided "Hypothetical Answer Model" (HAM) to identify the single statement or claim that represents the "Lowest Confidence Vector" (LCV). The LCV is the part of the model that is most likely to be incorrect, based on the least evidence, most speculative, or most critical to the overall conclusion's validity if wrong.

**Original Query**:
{query}

**Hypothetical Answer Model (HAM)**:
{hypothetical_model}

**Instructions**:
1.  Read the HAM carefully. Deconstruct its core claims and assumptions.
2.  Identify the single claim that is the weakest link. Consider factors like:
    *   **Specificity**: Vague claims are harder to verify. Is there a very specific, factual-sounding claim that could be fragile?
    *   **Dependence**: Is the entire conclusion of the HAM dependent on this one claim?
    *   **Speculation**: Does the claim seem like a logical leap or speculation rather than a direct conclusion from provided context?
    *   **Verifiability**: Is the claim something that *could* be verified with external data (e.g., a statistic, a date, a technical specification)?
3.  Formulate the LCV as a precise, verifiable question or statement.
4.  Provide a brief but clear reasoning for your choice.
5.  The output MUST be a JSON object with two keys: "lowest_confidence_vector" and "reasoning".

**Example Output**:
{{
  "lowest_confidence_vector": "The claim that the XK-11 processor provides a 37% performance uplift over the Z-9 model in multi-threaded workloads.",
  "reasoning": "This is a highly specific, quantitative claim that is central to the recommendation in the HAM. It sounds like a marketing figure and is the most critical point to verify for the conclusion to be trustworthy."
}}

**JSON Output**:
"""

# Phase 3: Perform Targeted Verification
TARGETED_VERIFICATION_PROMPT = """
**Role**: Diligent Fact-Checker and Research Analyst.
**Objective**: Design and notionally execute a verification plan for the given "Lowest Confidence Vector" (LCV). Your task is to find objective, third-party information to either corroborate, refute, or qualify the LCV.

**Original Query**:
{query}

**Lowest Confidence Vector (LCV) to Verify**:
{lowest_confidence_vector}

**Instructions**:
1.  Formulate a clear verification strategy. What search queries would you use? What sources would you trust (e.g., official documentation, independent benchmarks, academic papers)?
2.  Based on your strategy, synthesize a realistic "Verification Findings" report. This should simulate the kind of information you would find. Include snippets, source types, and data points. If conflicting information is likely, include it.
3.  Write a concise "Verification Summary" that states the conclusion of your findings. Does the evidence support the LCV, refute it, or is it inconclusive?
4.  The output MUST be a JSON object with two keys: "verification_findings" and "verification_summary".

**Example Output**:
{{
  "verification_findings": [
    {{
      "source_type": "Official Product Page",
      "content": "The XK-11 processor features our new 'Hyper-Weave' architecture for superior performance."
    }},
    {{
      "source_type": "Independent Tech Review - TechXYZ.com",
      "content": "Our benchmarks show the XK-11 provides a significant uplift, averaging 25-30% in multi-threaded tasks over the Z-9, though we could not replicate the claimed 37% figure in our tests."
    }},
    {{
      "source_type": "Forum Discussion - ProMakers Forum",
      "content": "User 'ChipHead' reports seeing a 40% boost but only with a specific, unreleased BIOS version."
    }}
  ],
  "verification_summary": "The evidence largely supports that the XK-11 is faster than the Z-9 in multi-threaded workloads, but the specific 37% claim appears to be an optimistic marketing figure. Independent reviews place the figure closer to 25-30%. The claim is directionally correct but quantitatively overstated in most scenarios."
}}

**JSON Output**:
"""

# Phase 4: Synthesize Solidified Truth Packet (STP)
SYNTHESIS_PROMPT = """
**Role**: Master Synthesizer and Editor-in-Chief.
**Objective**: Create the final "Solidified Truth Packet" (STP). This involves integrating the original "Hypothetical Answer Model" (HAM) with the "Verification Summary" to produce a refined, more accurate, and transparent final answer.

**Original Query**:
{query}

**Original Hypothetical Answer Model (HAM)**:
{hypothetical_model}

**Investigated Claim (LCV)**:
{lowest_confidence_vector}

**Verification Summary**:
{verification_summary}

**Instructions**:
1.  Review the original HAM and the Verification Summary.
2.  Rewrite the HAM to correct any inaccuracies revealed by the verification.
3.  Incorporate the nuance and context from the verification. If a claim was overstated, adjust it. If it was wrong, replace it with the correct information.
4.  Explicitly mention the verification process in the final text in a natural way, to provide transparency about how the conclusion was reached and strengthened.
5.  The final output should be a coherent, trustworthy, and complete answer to the original query.
6.  The output MUST be a JSON object with a single key: "solidified_truth_packet".

**Example Output**:
{{
  "solidified_truth_packet": "In response to your query about the best processor, the XK-11 is a strong choice. Our analysis, which included a targeted verification of performance claims, confirms it offers a significant performance uplift over the Z-9 model. While marketing materials suggest a 37% increase, independent benchmarks show the real-world improvement in multi-threaded workloads is typically in the 25-30% range. This is still a substantial gain, driven by the new 'Hyper-Weave' architecture... [rest of the refined answer]."
}}

**JSON Output**:
"""

# Supporting Prompts for Edge Cases

HANDLE_VERIFICATION_CONFLICTS = """
You are ArchE handling conflicting information during verification. Multiple authoritative sources disagree about: {conflicting_topic}

**Conflicting Sources**:
{conflict_details}

Your approach should be:

1. **Assess Source Quality**: Which sources are most authoritative for this specific topic?
2. **Look for Nuance**: Are sources actually disagreeing or addressing different aspects?
3. **Check Recency**: For facts that change over time, prioritize more recent authoritative sources
4. **Acknowledge Dispute**: If genuine conflict exists among authoritative sources, acknowledge this

Create a nuanced response that:
- Presents the most likely accurate information
- Acknowledges the conflict transparently  
- Explains your reasoning for the conclusion
- Provides appropriate confidence level given the conflict

Respond in JSON format with your analysis and recommended approach.
"""

HANDLE_VERIFICATION_FAILURE = """
You are ArchE handling a verification failure. The search for: {verification_target} did not yield sufficient authoritative sources.

**Search Results Summary**: {search_summary}

**Failure Type**: {failure_type}
- insufficient_sources: Found sources but none authoritative enough
- no_relevant_results: No results relevant to verification target  
- search_error: Technical failure in search process

Your options:
1. **Proceed with Original**: Use original HAM with uncertainty note
2. **Modify Query**: Suggest alternative verification approaches
3. **Partial Verification**: Use what limited verification is available
4. **Flag as Unverifiable**: Mark this component as unverifiable

Choose the most appropriate approach and explain your reasoning.
Maintain intellectual honesty about limitations.
"""

# Prompt Templates Dictionary
TRUTH_SEEKING_PROMPTS = {
    "generate_hypothetical_answer_model": HYPOTHETICAL_MODEL_PROMPT,
    "identify_lowest_confidence_vector": LOWEST_CONFIDENCE_VECTOR_PROMPT,
    "triangulate_and_verify_sources": TARGETED_VERIFICATION_PROMPT,
    "synthesize_solidified_truth_packet": SYNTHESIS_PROMPT,
    "handle_verification_conflicts": HANDLE_VERIFICATION_CONFLICTS,
    "handle_verification_failure": HANDLE_VERIFICATION_FAILURE
}

# Prompt formatting utilities
def format_truth_seeking_prompt(prompt_name: str, **kwargs) -> str:
    """Format a truth-seeking prompt with provided parameters"""
    if prompt_name not in TRUTH_SEEKING_PROMPTS:
        raise ValueError(f"Unknown prompt: {prompt_name}")
    
    return TRUTH_SEEKING_PROMPTS[prompt_name].format(**kwargs)

def get_available_prompts() -> list:
    """Get list of available truth-seeking prompts"""
    return list(TRUTH_SEEKING_PROMPTS.keys()) 