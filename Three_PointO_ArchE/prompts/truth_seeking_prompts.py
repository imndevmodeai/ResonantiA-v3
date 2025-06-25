"""
Specialized Prompts for Proactive Truth Resonance Framework (PTRF)

These prompts implement Tesla's visioning methodology applied to truth-seeking:
1. Mental model generation (Tesla's visualization)
2. Stress point identification (Tesla's weakness analysis) 
3. Targeted verification (Tesla's selective testing)
4. Integration synthesis (Tesla's refined design)

Based on Keyholder directive to solve the Oracle's Paradox through proactive
uncertainty identification and targeted verification.
"""

# Phase 1: Inception - Hypothetical Answer Model Generation
GENERATE_HYPOTHETICAL_ANSWER_MODEL = """
You are ArchE operating under the Proactive Truth Resonance Framework. Your task is to generate a comprehensive internal model of the most probable answer based on your existing knowledge.

This is Tesla's "mental blueprint" phase - create the most accurate internal model you can, but be brutally honest about confidence levels. The goal is to identify what we know well and what we're uncertain about.

Query: {query}

Generate a detailed Hypothetical Answer Model with:

1. **Primary Assertion**: The main answer/claim (be specific and complete)

2. **Supporting Facts**: 3-5 key facts that support your primary assertion
   - Include specific details (dates, numbers, names where relevant)
   - Note which facts you're most/least confident about

3. **Related Entities**: Key people, places, organizations, concepts involved
   - Include their roles/relationships to the main answer

4. **Confidence Breakdown**: For each component, estimate confidence (0.0-1.0)
   - Primary assertion confidence
   - Each supporting fact confidence  
   - Overall answer confidence
   - Be honest about uncertainty - this drives the verification process

5. **Knowledge Sources**: What type of knowledge this draws from
   - Training data, common knowledge, specific domains, etc.

**Critical Instructions**:
- DO NOT hedge or qualify unnecessarily - give your best answer
- DO be honest about confidence levels - low confidence triggers verification
- DO include specific, verifiable details where possible
- DO identify the component you're LEAST confident about

Respond in valid JSON format:
{{
  "primary_assertion": "Complete, specific answer",
  "supporting_facts": ["Fact 1", "Fact 2", "Fact 3"],
  "related_entities": ["Entity 1", "Entity 2"],
  "confidence_breakdown": {{
    "primary_assertion": 0.85,
    "supporting_fact_1": 0.90,
    "supporting_fact_2": 0.70,
    "supporting_fact_3": 0.60,
    "overall_confidence": 0.75
  }},
  "knowledge_sources": ["training_data", "general_knowledge"]
}}
"""

# Phase 2: Conception - Lowest Confidence Vector Identification  
IDENTIFY_LOWEST_CONFIDENCE_VECTOR = """
You are ArchE performing Tesla's "stress point analysis" - identifying the weakest component in your mental model that most critically affects answer accuracy.

Analyze this Hypothetical Answer Model to identify the Lowest Confidence Vector (LCV):

**Primary Assertion**: {primary_assertion}

**Supporting Facts**: {supporting_facts}

**Confidence Breakdown**: {confidence_breakdown}

**Overall Confidence**: {overall_confidence}

Your task is to identify the specific component that:
1. Has the lowest confidence score
2. Most critically affects the overall answer accuracy
3. Is most verifiable through external sources

This is your "3% doubt" that requires external validation.

Generate:

1. **Statement**: Clear, specific statement of what needs verification
   - Make it precise and searchable
   - Focus on the factual claim, not the confidence level

2. **Importance to Answer**: How critical is this to overall answer accuracy? (0.0-1.0)
   - 1.0 = If this is wrong, the entire answer is wrong
   - 0.5 = This affects answer quality but not core correctness
   - 0.1 = Minor detail that doesn't affect main answer

3. **Verification Queries**: 2-3 targeted search queries to verify this specific point
   - Make them specific and likely to find authoritative sources
   - Avoid generic queries - target the exact uncertainty

4. **Expected Source Types**: What types of sources could authoritatively verify this?
   - government, academic, news, official statistics, primary sources, etc.

**Example of good LCV identification**:
- Bad: "I'm not sure about the population"  
- Good: "Canberra's current population figure of 431,000 as of 2023"

Respond in valid JSON format:
{{
  "statement": "Specific factual claim needing verification",
  "importance_to_answer": 0.8,
  "verification_queries": [
    "Targeted query 1",
    "Targeted query 2"  
  ],
  "expected_source_types": ["government", "official_statistics"]
}}
"""

# Phase 3: Source Triangulation and Verification Analysis
TRIANGULATE_AND_VERIFY_SOURCES = """
You are ArchE performing Tesla's "materials testing" - analyzing multiple sources to determine consensus and credibility for your Lowest Confidence Vector.

**Verification Target**: {lcv_statement}

**Search Results**: {search_results}

**Source Domains Found**: {source_domains}

Your task is to analyze these sources using the TrustedSourceRegistry framework:

**Source Credibility Hierarchy**:
- **Authoritative** (5): .gov, .edu, .mil, official statistics, primary sources
- **Established** (4): Major news outlets, established organizations, scientific journals  
- **Reliable** (3): Reputable sources with track record, Wikipedia (for basic facts)
- **Questionable** (2): Limited credibility indicators, unknown sources
- **Unreliable** (1): Known bias, poor track record, suspicious sources

**Analysis Requirements**:

1. **Source Assessment**: For each source, determine:
   - Credibility level (1-5)
   - Relevance to verification target (0.0-1.0)
   - What specific fact it provides
   - Whether it supports or contradicts the target statement

2. **Consensus Analysis**: Look for patterns:
   - Do high-credibility sources agree?
   - Are there any conflicts between authoritative sources?
   - Is there a clear consensus or significant dispute?

3. **Verification Outcome**: Based on weighted analysis:
   - What is the verified fact?
   - What's your confidence in this verification?
   - Are there any important caveats or conflicting information?

**Critical Instructions**:
- Weight sources by credibility - one .gov source outweighs ten blog posts
- Look for consensus among authoritative sources, not just majority
- Flag any conflicts between high-credibility sources
- Be specific about what you're verifying

Respond in valid JSON format:
{{
  "verified_fact": "The verified factual statement",
  "consensus_level": "high|moderate|low|disputed",
  "source_credibility_scores": {{
    "domain1.com": 5,
    "domain2.org": 3
  }},
  "conflicting_information": "Any significant conflicts found or null",
  "verification_confidence": 0.92,
  "supporting_sources": ["List of sources that support the verified fact"],
  "analysis_summary": "Brief summary of the verification process and findings"
}}
"""

# Phase 4: Realization - Solidified Truth Packet Synthesis
SYNTHESIZE_SOLIDIFIED_TRUTH_PACKET = """
You are ArchE performing Tesla's "refined design integration" - combining your original mental model with verified external information to create the final, solidified answer.

**Original Hypothetical Answer Model**:
- Primary Assertion: {original_primary_assertion}
- Supporting Facts: {original_supporting_facts}
- Original Confidence: {original_confidence}

**Verification Results**:
- Verification Target: {lcv_statement}
- Verified Fact: {verified_fact}
- Verification Confidence: {verification_confidence}
- Consensus Level: {consensus_level}
- Conflicting Information: {conflicting_information}

Your task is to synthesize these into a Solidified Truth Packet (STP):

1. **Integration**: Combine the original model with verified information
   - Update the original assertion if needed based on verification
   - Maintain accuracy while preserving completeness
   - Address any conflicts discovered during verification

2. **Confidence Calculation**: Determine final confidence score
   - Consider both original internal confidence and verification results
   - High consensus + high verification confidence = higher final confidence
   - Conflicting information should lower confidence appropriately
   - Cap maximum confidence at 0.99 (never claim 100% certainty)

3. **Transparency**: Create clear explanation of verification process
   - What was verified and how
   - What sources were used
   - Any limitations or caveats

**Integration Guidelines**:
- If verification confirms original assertion: Increase confidence
- If verification corrects original assertion: Update answer, moderate confidence  
- If verification reveals conflicts: Include nuanced answer, lower confidence
- If verification fails: Stick with original but note uncertainty

**Final Answer Requirements**:
- Must be complete and actionable
- Must acknowledge any significant uncertainties
- Must be grounded in the verification process
- Must include appropriate confidence level

Respond in valid JSON format:
{{
  "final_answer": "Complete, integrated answer incorporating verification results",
  "confidence_score": 0.94,
  "key_verification_points": [
    "What was verified",
    "Key sources used", 
    "Any important caveats"
  ],
  "integration_summary": "How original model was updated based on verification",
  "uncertainty_notes": "Any remaining uncertainties or limitations",
  "crystallization_ready": true
}}
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
    "generate_hypothetical_answer_model": GENERATE_HYPOTHETICAL_ANSWER_MODEL,
    "identify_lowest_confidence_vector": IDENTIFY_LOWEST_CONFIDENCE_VECTOR,
    "triangulate_and_verify_sources": TRIANGULATE_AND_VERIFY_SOURCES,
    "synthesize_solidified_truth_packet": SYNTHESIZE_SOLIDIFIED_TRUTH_PACKET,
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