import logging
from typing import Dict, Any
from pathlib import Path
import jinja2
import json

logger = logging.getLogger(__name__)

class PromptManager:
    """
    The Sacred Scribe of ArchE. Manages, renders, and formats all forms of 
    communication between human intent and artificial intelligence.
    """
    def __init__(self, templates_dir: str = "prompts/"):
        self.templates_path = Path(templates_dir)
        if not self.templates_path.is_dir():
            raise FileNotFoundError(f"Templates directory not found at: {self.templates_path}")
        
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_path),
            autoescape=jinja2.select_autoescape(['html', 'xml', 'j2'])
        )
        logger.info(f"PromptManager initialized with templates from '{self.templates_path}'")

    def render_template(self, template_name: str, **context: Any) -> str:
        """Renders a Jinja2 template with the given context."""
        try:
            template = self.env.get_template(f"{template_name}.j2")
            return template.render(context)
        except jinja2.TemplateNotFound:
            logger.error(f"Template '{template_name}.j2' not found.")
            raise
        except Exception as e:
            logger.error(f"Error rendering template '{template_name}': {e}")
            raise

    def format_truth_seeking_prompt(self, prompt_type: str, **kwargs: Any) -> str:
        """Formats a prompt for the Proactive Truth Resonance Framework (PTRF)."""
        prompts = {
            "generate_hypothetical_answer_model": "Generate a confident, hypothetical answer for the query: '{query}' based on the context: {initial_context}",
            "identify_lowest_confidence_vector": "From the hypothetical model provided, identify the single claim or vector with the lowest confidence. Model: {hypothetical_model}",
            "triangulate_and_verify_sources": "Verify this specific claim by triangulating across multiple reliable sources. Claim: {lowest_confidence_vector}",
            "synthesize_solidified_truth_packet": "Synthesize the verified information into a solidified truth packet. Original query: {query}. Verification results: {verification_results}",
        }
        prompt_template = prompts.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Unknown truth-seeking prompt type: {prompt_type}")
        return prompt_template.format(**kwargs)

    def format_vetting_prompt(
        self,
        objective: str,
        previous_result: Dict,
        current_thought: str,
        current_action: str,
        action_inputs: Dict
    ) -> str:
        """Formats a vetting prompt with IAR integration."""
        # This is a simplified representation of a complex prompt.
        prompt = f"""
        **VETTING PROTOCOL v3.0**
        **Objective:** {objective}
        **Previous Step IAR:** {json.dumps(previous_result.get('reflection', {}), indent=2)}
        **Current Thought:** {current_thought}
        **Proposed Action:** {current_action}
        **Action Inputs:** {json.dumps(action_inputs, indent=2)}

        **Analysis Required:**
        1.  **Logical Consistency:** Is the current thought a logical progression from the previous result?
        2.  **Protocol Alignment:** Does the proposed action align with ArchE's core principles?
        3.  **Action Appropriateness:** Is this the most efficient and effective action?
        4.  **Risk & Ethics:** Are there any unforeseen risks or ethical concerns?
        5.  **Resonance:** Does this action resonate with the overall goal?
        
        Provide a detailed vetting analysis.
        """
        return prompt.strip()
