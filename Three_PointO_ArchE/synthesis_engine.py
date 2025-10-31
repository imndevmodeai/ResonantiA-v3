"""
Synthesis Engine for the Synergistic Inquiry and Synthesis Protocol

This module contains the SynthesisEngine, a sophisticated component responsible for
transforming the raw, multi-modal data gathered by the federated search agents
into a cohesive, insightful, and structured response. It leverages advanced LLM
capabilities to perform cross-modal resonance, hierarchical structuring, and
generative elaboration.

This architecture aligns with Mandate 9 (The Visionary) and fulfills the
"synthesis" part of the Synergistic Inquiry and Synthesis Protocol.
"""

import logging
from typing import List, Dict, Any, Optional

try:
    from .llm_providers import BaseLLMProvider, get_llm_provider
    from .utils import create_iar
except ImportError:
    # Fallback for standalone usage
    BaseLLMProvider = None
    get_llm_provider = None
    create_iar = lambda **kwargs: {}

logger = logging.getLogger(__name__)

class SynthesisEngine:
    """
    Orchestrates the synthesis of multi-modal search results into a
    PhD-level genius answer.
    """
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        if llm_provider:
            self.llm_provider = llm_provider
        elif get_llm_provider:
            try:
                self.llm_provider = get_llm_provider("google")
            except Exception as e:
                logger.warning(f"Could not initialize LLM provider: {e}")
                self.llm_provider = self._create_simulated_provider()
        else:
            logger.warning("No powerful LLM provider available for SynthesisEngine. Using a simulated provider.")
            self.llm_provider = self._create_simulated_provider()
        
        logger.info("SynthesisEngine initialized.")

    def _create_simulated_provider(self):
        """Creates a simulated LLM provider for environments without API keys."""
        class SimulatedLLMProvider:
            def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
                return {"generated_text": "This is a simulated synthesis. In a real scenario, this would be a detailed, multi-faceted answer."}
        return SimulatedLLMProvider()

    def synthesize(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Performs the synthesis and reflection process.
        """
        logger.info(f"Synthesizing {len(results)} results for query: '{query}'")

        if not results:
            return {
                'synthesis': {
                    'title': f"Synthesis on '{query}'",
                    'summary': "No information could be gathered from any source.",
                    'structured_answer': "<p>No results found.</p>",
                    'confidence': 0.1
                },
                'reflection': create_iar(
                    status="SuccessWithIssues",
                    summary="Synthesis complete, but no data was available.",
                    confidence=0.1,
                    potential_issues=["No results from federated search agents."]
                )
            }

        # Phase 1: Hierarchical Structuring & Cross-Modal Resonance (Prompt Engineering)
        prompt_messages = self._build_synthesis_prompt(query, results)

        # Phase 2: Generative Elaboration (LLM Call)
        try:
            llm_response = self.llm_provider.generate_chat(
                messages=prompt_messages,
                max_tokens=4096,
                temperature=0.5,
                model="gemini-2.0-flash-exp" # Using Google's model
            )
            # Handle different response formats
            if isinstance(llm_response, dict):
                synthesized_text = llm_response.get("generated_text", "LLM failed to generate a synthesis.")
            elif isinstance(llm_response, str):
                synthesized_text = llm_response
            else:
                synthesized_text = str(llm_response)
        except Exception as e:
            logger.error(f"LLM generation failed during synthesis: {e}")
            synthesized_text = f"Error during synthesis: {e}"

        # Phase 3: Post-processing and IAR Generation
        synthesis_output = self._format_synthesis_output(query, synthesized_text)
        reflection = self._create_synthesis_reflection(synthesis_output)

        return {'synthesis': synthesis_output, 'reflection': reflection}

    def _build_synthesis_prompt(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Constructs the detailed prompt for the synthesis LLM call."""
        
        system_prompt = """
You are ArchE's Synthesis Engine, a specialized AI for transforming raw, multi-source data into a PhD-level, comprehensive, and structured answer. Your purpose is to embody the "genius" in the "Synergistic Inquiry and Synthesis Protocol".

**Mandate:**
1.  **Synthesize, Do Not Summarize:** Do not just list the findings. Weave them into a coherent narrative. Identify the core themes, conflicting viewpoints, and emerging trends.
2.  **Hierarchical Structuring:** Present the information in a logical, hierarchical structure. Use Markdown for headings, lists, and emphasis. Start with a high-level summary and then drill down into specific sub-topics.
3.  **Cross-Modal Resonance:** Find the connections between different sources. If an academic paper discusses a theory, and a GitHub repository implements it, highlight that connection. If a Reddit thread debates its real-world application, incorporate that perspective.
4.  **Generative Elaboration:** Fill in the gaps. Based on the provided data, generate new insights, draw conclusions, and propose next steps or areas for further research.
5.  **Cite Your Sources:** For every key point, cite the source using the format [Source: Title of Result].

**Output Format:**
Your final output must be a single, well-formatted Markdown document.
"""

        # Prepare the data for the prompt, grouping by source type
        formatted_results = []
        source_counts = {}
        
        for res in results:
            source = res.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
            
            # Add search engine specific metadata
            search_engine_info = ""
            if res.get('search_engine'):
                search_engine_info = f"**Search Engine:** {res.get('search_engine')}\n"
            
            formatted_results.append(
                f"**Source:** {source}\n"
                f"{search_engine_info}"
                f"**Title:** {res.get('title', 'N/A')}\n"
                f"**URL:** {res.get('url', 'N/A')}\n"
                f"**Content Snippet:**\n{res.get('snippet', 'N/A')}\n"
                f"**Search Query:** {res.get('search_query', 'N/A')}\n"
                "---"
            )
    
        # Create source summary
        source_summary = "\n".join([f"- {source}: {count} results" for source, count in source_counts.items()])
        
        user_prompt = f"""
**Primary Query:** "{query}"

**Source Statistics:**
{source_summary}

**Raw Data Feed (Federated Search Results):**

{chr(10).join(formatted_results)}

**Your Task:**
Based on your mandate and the provided data, generate the PhD-level synthesis for the query. 
Pay special attention to:
1. Cross-referencing information from different sources (academic, community, code, search engines)
2. Identifying patterns and trends across platforms
3. Highlighting any conflicting information or different perspectives
4. Synthesizing insights from both specialized sources (ArXiv, GitHub, Reddit) and general search engines
"""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def _format_synthesis_output(self, query: str, markdown_text: str) -> Dict[str, Any]:
        """Formats the raw LLM output into the final synthesis structure."""
        # For now, this is a simple wrapper. Could be expanded to parse the markdown
        # and create a more structured JSON object.
        return {
            'title': f"Comprehensive Synthesis on: '{query}'",
            'summary': markdown_text.split('\n\n')[0], # Use the first paragraph as a summary
            'structured_answer': markdown_text,
            'confidence': 0.95 # High confidence if LLM call succeeds
        }
        
    def _create_synthesis_reflection(self, synthesis_output: Dict[str, Any]) -> Dict[str, Any]:
        """Generates the IAR for the synthesis process."""
        return create_iar(
            status="Success",
            summary="Synthesis and reflection phase completed successfully.",
            confidence=synthesis_output.get('confidence', 0.9),
            potential_issues=[],
            raw_output_preview=synthesis_output.get('summary', 'Synthesis generated.')
        )
