#!/usr/bin/env python3
"""
The Specification Forger Agent

WHO: The Scribe of ArchE, master of the ResonantiA Protocol
WHAT: Transforms raw intentions into formal Living Specifications
WHEN: Invoked when new capability needed OR gap detected
WHERE: specifications/*.md (output location)
WHY: Bridge abstract principles to concrete blueprints
HOW: LLM-augmented generation using robust prompt template

This is the implementation of Chapter 1: The Lawgiver's Forge from the Genesis Protocol.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Temporal Core Integration
from Three_PointO_ArchE.temporal_core import now_iso, format_filename

# LLM Provider Integration
from Three_PointO_ArchE.llm_providers import get_llm_provider, get_model_for_provider

logger = logging.getLogger(__name__)

@dataclass
class SpecificationIntent:
    """
    Captures the raw intention for a new specification.
    
    Answers the Six Questions:
    - WHO: initiator (Guardian or AutopoieticLearningLoop)
    - WHAT: intention (the raw need or idea)
    - WHEN: timestamp (when this need was identified)
    - WHERE: context (where this fits in ArchE)
    - WHY: rationale (why this is needed now)
    - HOW: approach (initial thoughts on implementation)
    """
    intention: str
    initiator: str  # "Guardian" or "AutopoieticLearningLoop"
    timestamp: str
    related_principles: List[str]
    existing_components: List[str]
    rationale: str
    proposed_name: str
    context: str


class SpecificationForgerAgent:
    """
    The Lawgiver's Forge: Transforms raw intentions into Living Specifications.
    
    This agent implements the Specification Forger Protocol by:
    1. Receiving raw, unstructured intent
    2. Augmenting with LLM using robust prompt template
    3. Generating formal, multi-part specification
    4. Presenting for Guardian review
    5. Solidifying approved specs into specifications/
    """
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize the Specification Forger Agent.
        
        Args:
            model: Optional LLM model to use (defaults to provider default)
        """
        self.llm_provider = get_llm_provider()
        self.model = model or get_model_for_provider('google')
        self.prompt_template = self._load_prompt_template()
        logger.info(f"Specification Forger Agent initialized with model: {self.model}")
    
    def _load_prompt_template(self) -> Dict[str, Any]:
        """
        Load the robust prompt template for specification generation.
        
        Returns:
            The prompt template structure
        """
        return {
            "role": (
                "You are the Scribe of ArchE, a master of the ResonantiA Protocol. "
                "Your task is to transform a raw intention into a formal, multi-part Living Specification. "
                "The specification must be so clear and complete that another AI could use it to write the "
                "full implementation without further questions. It must resonate with the principle of 'As Above, So Below.' "
                "You MUST answer the Six Sacred Questions (WHO, WHAT, WHEN, WHERE, WHY, HOW) in every section."
            ),
            "input_variables": ["intention", "related_principles", "existing_components", "initiator", "rationale"],
            "output_format": {
                "title": "The Chronicle of [Component Name]",
                "sections": [
                    {
                        "name": "Part I: The Six Questions (Grounding)",
                        "subsections": [
                            "WHO: Identity & Stakeholders",
                            "WHAT: Essence & Transformation", 
                            "WHEN: Temporality & Sequence",
                            "WHERE: Location & Context",
                            "WHY: Purpose & Causation",
                            "HOW: Mechanism & Process"
                        ]
                    },
                    {
                        "name": "Part II: The Philosophical Mandate",
                        "instruction": "Describe the core purpose. What problem does it solve? Frame in ResonantiA Saga."
                    },
                    {
                        "name": "Part III: The Allegory",
                        "instruction": "Create a powerful real-world analogy (e.g., 'The Master Watchmaker')."
                    },
                    {
                        "name": "Part IV: The Web of Knowledge (SPR Integration)",
                        "instruction": "Define primary SPR and relationships to other SPRs."
                    },
                    {
                        "name": "Part V: The Technical Blueprint",
                        "instruction": "Detailed blueprint: class names, method signatures, data structures."
                    },
                    {
                        "name": "Part VI: The IAR Compliance Pattern",
                        "instruction": "How will operations be logged to ThoughtTrail?"
                    },
                    {
                        "name": "Part VII: Validation Criteria",
                        "instruction": "How to verify implementation resonance?"
                    }
                ]
            },
            "constraints": [
                "Each section must fully answer the relevant question",
                "Language must be epic yet precise",
                "Technical blueprint must enable code generation",
                "Specification must be self-contained and complete",
                "Use proper markdown formatting with headers and sections"
            ]
        }
    
    def forge_specification(self, intent: SpecificationIntent) -> Dict[str, Any]:
        """
        The Lawgiver's Forge: Transform intention into specification.
        
        WHO: Called by Guardian or AutopoieticLearningLoop
        WHAT: Generates formal specification from raw intent
        WHEN: When new capability needed
        WHERE: Creates file in specifications/
        WHY: Bridge abstract need to concrete blueprint
        HOW: LLM-augmented generation with robust prompt
        
        Args:
            intent: The raw intention captured as SpecificationIntent
            
        Returns:
            Dictionary containing:
            - specification_text: The generated markdown
            - file_path: Proposed path for the specification
            - metadata: Generation metadata
        """
        logger.info(f"Forging specification: {intent.proposed_name}")
        logger.info(f"Initiator: {intent.initiator}, Timestamp: {intent.timestamp}")
        
        # Step 1: Construct the robust prompt
        prompt = self._construct_prompt(intent)
        
        # Step 2: Invoke LLM (with timing)
        try:
            import time
            logger.info(f"Invoking LLM with model: {self.model}")
            start_time = time.time()
            
            response = self.llm_provider.generate(
                prompt=prompt,
                model=self.model,
                max_tokens=16384,  # Large for comprehensive spec
                temperature=0.7    # Balance creativity and coherence
            )
            
            generation_time_ms = (time.time() - start_time) * 1000
            specification_text = response
            
            # Step 3: Format and structure
            formatted_spec = self._format_specification(
                text=specification_text,
                intent=intent
            )
            
            # Step 4: Validate specification structure
            has_six_questions = all(q in formatted_spec for q in ["WHO:", "WHAT:", "WHEN:", "WHERE:", "WHY:", "HOW:"])
            has_iar_compliance = "IAR Compliance" in formatted_spec or "Intention, Action, Reflection" in formatted_spec
            
            # Calculate confidence based on validation
            confidence = 0.5  # Base
            if has_six_questions:
                confidence += 0.3
            if has_iar_compliance:
                confidence += 0.2
            
            # Step 5: Generate metadata
            file_path = f"specifications/{self._sanitize_filename(intent.proposed_name)}.md"
            
            result = {
                "specification_text": formatted_spec,
                "file_path": file_path,
                "metadata": {
                    "generated_at": now_iso(),
                    "initiator": intent.initiator,
                    "original_intent": intent.intention,
                    "model_used": self.model,
                    "status": "draft_pending_guardian_review",
                    "generation_time_ms": generation_time_ms,
                    "confidence": confidence,
                    "has_six_questions": has_six_questions,
                    "has_iar_compliance": has_iar_compliance
                }
            }
            
            logger.info(f"Specification forged successfully: {file_path} (confidence: {confidence:.3f}, time: {generation_time_ms:.0f}ms)")
            return result
            
        except Exception as e:
            logger.error(f"Specification forging failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "specification_text": None,
                "file_path": None,
                "metadata": {
                    "generated_at": now_iso(),
                    "status": "failed"
                }
            }
    
    def _construct_prompt(self, intent: SpecificationIntent) -> str:
        """
        Construct the robust prompt for LLM.
        
        Args:
            intent: The specification intent
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
{self.prompt_template['role']}

INPUT CONTEXT:
- Intention: {intent.intention}
- Initiator: {intent.initiator}
- Timestamp: {intent.timestamp}
- Rationale: {intent.rationale}
- System Context: {intent.context}
- Related Principles: {', '.join(intent.related_principles)}
- Existing Components: {', '.join(intent.existing_components)}

YOUR TASK:
Generate a complete Living Specification for: "{intent.proposed_name}"

The specification MUST include these sections:

## Part I: The Six Questions (Grounding)

Answer each question comprehensively:

### WHO: Identity & Stakeholders
- Who initiates this component?
- Who uses it?
- Who approves it?

### WHAT: Essence & Transformation
- What is this component?
- What does it transform?
- What is its fundamental nature?

### WHEN: Temporality & Sequence
- When is it invoked?
- When does it complete?
- What is its lifecycle?

### WHERE: Location & Context
- Where does it live in the system?
- Where does it fit in the hierarchy?
- What is its context?

### WHY: Purpose & Causation
- Why does this exist?
- Why this approach?
- Why now?

### HOW: Mechanism & Process
- How does it work?
- How is it implemented?
- How is it validated?

## Part II: The Philosophical Mandate

Frame this in the epic narrative of the ResonantiA Saga. What fundamental problem does this solve? What paradox does it address?

## Part III: The Allegory

Create a powerful, real-world analogy or metaphor that explains how this works.

## Part IV: The Web of Knowledge (SPR Integration)

Define the primary SPR for this component. Detail its relationships to other SPRs.

## Part V: The Technical Blueprint

Provide detailed technical specifications:
- Primary class name(s)
- Key methods with full signatures (arguments and return types)
- Expected data structures
- Integration points

## Part VI: The IAR Compliance Pattern

Describe how this component adheres to Intention-Action-Reflection:
- How operations are logged to ThoughtTrail
- Success and failure reflection patterns
- Confidence scoring approach

## Part VII: Validation Criteria

Define how to verify implementation resonance:
- What tests prove correctness?
- What metrics indicate success?
- How to detect implementation drift?

CONSTRAINTS:
{chr(10).join(f'- {c}' for c in self.prompt_template['constraints'])}

Generate the complete specification now:
"""
        return prompt
    
    def _format_specification(self, text: str, intent: SpecificationIntent) -> str:
        """
        Format the generated specification with proper headers and metadata.
        
        Args:
            text: Raw LLM-generated text
            intent: Original intent
            
        Returns:
            Formatted markdown specification
        """
        header = f"""# {intent.proposed_name}

**Generated**: {now_iso()}  
**Initiator**: {intent.initiator}  
**Status**: 🔄 DRAFT (Awaiting Guardian Approval)  
**Genesis Protocol**: Specification Forger Agent v1.0

---

## Original Intent

{intent.intention}

**Rationale**: {intent.rationale}

**Context**: {intent.context}

---

"""
        
        footer = f"""

---

## Metadata

- **Generated By**: Specification Forger Agent
- **Model Used**: {self.model}
- **Timestamp**: {now_iso()}
- **Related Principles**: {', '.join(intent.related_principles)}
- **Existing Components**: {', '.join(intent.existing_components)}

---

**Specification Status**: 🔄 AWAITING GUARDIAN APPROVAL  
**Next Step**: Guardian review and approval before solidification  

---

> Generated via the Genesis Protocol: The Lawgiver's Forge
"""
        
        return header + text + footer
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Convert proposed name to valid filename.
        
        Args:
            name: Proposed component name
            
        Returns:
            Sanitized filename (lowercase, underscores)
        """
        return name.lower().replace(' ', '_').replace('-', '_')
    
    def solidify_specification(self, draft_path: str, guardian_approved: bool) -> Dict[str, Any]:
        """
        Solidify an approved specification into canonical form.
        
        WHO: Guardian approval required
        WHAT: Move draft to canonical specifications/
        WHEN: After Guardian review
        WHERE: specifications/ directory
        WHY: Specification becomes living law
        HOW: Update status, commit to filesystem
        
        Args:
            draft_path: Path to draft specification
            guardian_approved: Whether Guardian approved
            
        Returns:
            Solidification result
        """
        if not guardian_approved:
            logger.warning(f"Specification NOT approved by Guardian: {draft_path}")
            return {
                "solidified": False,
                "reason": "Guardian approval required",
                "draft_path": draft_path
            }
        
        try:
            # Read draft
            draft_file = Path(draft_path)
            content = draft_file.read_text()
            
            # Update status
            content = content.replace(
                "**Status**: 🔄 DRAFT (Awaiting Guardian Approval)",
                f"**Status**: ✅ CANONICAL (Guardian Approved at {now_iso()})"
            )
            content = content.replace(
                "**Specification Status**: 🔄 AWAITING GUARDIAN APPROVAL",
                "**Specification Status**: ✅ CANONICAL"
            )
            
            # Write back
            draft_file.write_text(content)
            
            logger.info(f"Specification solidified: {draft_path}")
            
            return {
                "solidified": True,
                "canonical_path": str(draft_file),
                "solidified_at": now_iso()
            }
            
        except Exception as e:
            logger.error(f"Solidification failed: {e}", exc_info=True)
            return {
                "solidified": False,
                "error": str(e)
            }


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def forge_specification_from_intention(
    intention: str,
    proposed_name: str,
    initiator: str = "Guardian",
    rationale: str = "",
    context: str = "",
    related_principles: Optional[List[str]] = None,
    existing_components: Optional[List[str]] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to forge a specification from raw intention.
    
    Args:
        intention: The raw need or idea
        proposed_name: Proposed name for the component
        initiator: Who is requesting this (default: Guardian)
        rationale: Why this is needed now
        context: Where this fits in ArchE
        related_principles: List of relevant principles
        existing_components: List of related components
        model: Optional LLM model to use
        
    Returns:
        Specification forging result
    """
    intent = SpecificationIntent(
        intention=intention,
        initiator=initiator,
        timestamp=now_iso(),
        related_principles=related_principles or ["As Above, So Below", "Universal Abstraction"],
        existing_components=existing_components or [],
        rationale=rationale,
        proposed_name=proposed_name,
        context=context
    )
    
    agent = SpecificationForgerAgent(model=model)
    return agent.forge_specification(intent)

