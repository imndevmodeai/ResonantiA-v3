"""
Knowledge Graph Natural Language Generator
Converts KG/SPR data into readable natural language explanations WITHOUT LLM calls.
This allows assessment of ArchE's independent knowledge vs LLM-augmented responses.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NLGContext:
    """Context for natural language generation."""
    spr_data: Dict[str, Any]
    related_sprs: List[Dict[str, Any]] = None
    depth: int = 0
    max_depth: int = 2


class KGNaturalLanguageGenerator:
    """
    Generates natural language explanations from Knowledge Graph data.
    
    Strategy:
    1. Extract all available information from SPR definition
    2. Use template-based generation with rule-based logic
    3. Synthesize relationships, blueprints, examples into coherent narrative
    4. NO LLM calls - pure deterministic transformation
    """
    
    def __init__(self):
        """Initialize the NLG system."""
        self.templates = self._load_templates()
        self.relationship_connectors = {
            "part_of": "is part of",
            "enables": "enables",
            "uses": "uses",
            "related_to": "is related to",
            "implements": "implements",
            "corresponds_to": "corresponds to",
            "supplies": "supplies",
            "catalogs": "catalogs"
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """Load natural language generation templates."""
        return {
            "definition_intro": "{term} is {definition}",
            "definition_with_context": "{term} refers to {definition}. {context}",
            "with_blueprint": "{term} is {definition}. {blueprint}",
            "with_relationships": "{term} is {definition}. It {relationships}",
            "with_example": "{term} is {definition}. For example, {example}",
            "comprehensive": "{term} is {definition}. {blueprint} {relationships} {example}",
            "category_intro": "In the domain of {category}, {term} is {definition}",
            "source_attribution": "This knowledge comes from {source}",
        }
    
    def generate_explanation(self, spr_data: Dict[str, Any], context: Optional[NLGContext] = None) -> str:
        """
        Generate natural language explanation from SPR data.
        
        Args:
            spr_data: SPR definition dictionary
            context: Optional context for generation
            
        Returns:
            Natural language explanation
        """
        if not spr_data:
            return "No information available."
        
        # Extract components
        term = spr_data.get('term', spr_data.get('spr_id', 'Unknown'))
        definition = spr_data.get('definition', '')
        category = spr_data.get('category', '')
        blueprint = spr_data.get('blueprint_details', '')
        example = spr_data.get('example_application', '')
        relationships = spr_data.get('relationships', {})
        source = spr_data.get('source', spr_data.get('enriched_from', ''))
        
        # Clean and process definition
        definition = self._clean_definition(definition)
        
        # Build explanation components
        parts = []
        
        # 1. Core definition (prioritize clean, meaningful definition)
        if definition and len(definition) > 20:
            # Use definition directly if it's substantial
            if category and category not in ['ExtractedKnowledge', 'Unknown']:
                parts.append(f"In the domain of {category}, {term} is {definition}")
            else:
                parts.append(f"{term} is {definition}")
        elif definition:
            # Short definition - try to expand
            if category and category not in ['ExtractedKnowledge', 'Unknown']:
                parts.append(f"{term} is a {category.lower()} concept: {definition}")
            else:
                parts.append(f"{term} is {definition}")
        else:
            # No definition - use relationships or category
            if category and category not in ['ExtractedKnowledge', 'Unknown']:
                parts.append(f"{term} is a {category.lower()} in the Knowledge Graph")
            else:
                parts.append(f"{term} is a concept in the Knowledge Graph")
        
        # 2. Blueprint/Implementation details (only if definition is minimal)
        if blueprint and (not definition or len(definition) < 100):
            blueprint_text = self._process_blueprint(blueprint)
            if blueprint_text and blueprint_text not in parts:
                parts.append(blueprint_text)
        
        # 3. Relationships
        if relationships:
            relationship_text = self._process_relationships(term, relationships)
            if relationship_text:
                parts.append(relationship_text)
        
        # 4. Example application
        if example:
            parts.append(f"For example, {example}")
        
        # 5. Source attribution (if from agi.txt)
        if source and 'agi.txt' in source.lower():
            parts.append(f"This knowledge was extracted from Mastermind_AI legacy knowledge (agi.txt).")
        
        # Combine into coherent narrative
        explanation = self._synthesize_narrative(parts)
        
        return explanation
    
    def _clean_definition(self, definition: str) -> str:
        """Clean and normalize definition text."""
        if not definition:
            return ""
        
        # Remove metadata markers and noise
        definition = re.sub(r'\[From agi\.txt\]:.*?\n', '', definition, flags=re.MULTILINE)
        definition = re.sub(r'\[From Codebase\]:.*?\n', '', definition, flags=re.MULTILINE)
        definition = re.sub(r'Node \d+:', '', definition)
        definition = re.sub(r'Confidence: [\d.]+', '', definition)
        definition = re.sub(r'Edges:', '', definition)
        definition = re.sub(r'SPR mentioned in list from agi\.txt:.*?\n', '', definition, flags=re.MULTILINE)
        definition = re.sub(r'->\|.*?\|<-', '', definition)  # Remove XML-like tags
        definition = re.sub(r'SPR: [\d.]+', '', definition)
        
        # Extract meaningful sentences (remove very short fragments)
        sentences = []
        for sentence in definition.split('.'):
            sentence = sentence.strip()
            # Keep sentences that are substantial or contain key information
            if len(sentence) > 10 and not sentence.startswith(('Node', 'SPR', 'Edges', 'Confidence')):
                sentences.append(sentence)
        
        # If we have good sentences, use them; otherwise try to extract core meaning
        if sentences:
            definition = '. '.join(sentences[:3])  # Use top 3 sentences
        else:
            # Try to extract the first meaningful phrase
            words = definition.split()
            meaningful = []
            skip_next = False
            for i, word in enumerate(words):
                if skip_next:
                    skip_next = False
                    continue
                if word.lower() in ['node', 'spr', 'edges', 'confidence', 'from', 'agi.txt']:
                    skip_next = True
                    continue
                if word and len(word) > 2:
                    meaningful.append(word)
                if len(meaningful) > 20:  # Limit length
                    break
            definition = ' '.join(meaningful)
        
        # Clean up whitespace
        definition = re.sub(r'\n+', ' ', definition)
        definition = re.sub(r'\s+', ' ', definition)
        definition = definition.strip()
        
        # Ensure it ends properly
        if definition and not definition.endswith(('.', '!', '?')):
            definition += '.'
        
        return definition
    
    def _process_blueprint(self, blueprint: str) -> str:
        """Process blueprint details into natural language."""
        if not blueprint:
            return ""
        
        # Extract key information
        if 'implementation' in blueprint.lower() or 'code' in blueprint.lower():
            # Extract file paths
            file_paths = re.findall(r'`([^`]+)`|([A-Za-z_/]+\.py)', blueprint)
            if file_paths:
                files = [f[0] or f[1] for f in file_paths[:2]]
                return f"It is implemented in {', '.join(files)}."
        
        if 'section' in blueprint.lower() or 'protocol' in blueprint.lower():
            # Extract protocol references
            sections = re.findall(r'Section [\d.]+', blueprint)
            if sections:
                return f"Defined in {sections[0]} of the ResonantiA Protocol."
        
        # Generic blueprint processing
        blueprint_clean = re.sub(r'SPR extracted from.*?\.', '', blueprint)
        blueprint_clean = re.sub(r'type: \w+', '', blueprint_clean)
        blueprint_clean = blueprint_clean.strip()
        
        if blueprint_clean and len(blueprint_clean) > 20:
            return f"Implementation details: {blueprint_clean[:200]}"
        
        return ""
    
    def _process_relationships(self, term: str, relationships: Dict[str, Any]) -> str:
        """Process relationships into natural language."""
        if not relationships:
            return ""
        
        relationship_parts = []
        
        # Handle different relationship types
        if isinstance(relationships, dict):
            # Direct relationship dictionary
            for rel_type, targets in relationships.items():
                if rel_type in ['type', 'source', 'original_format', 'node_number', 'edges', 'confidence']:
                    continue  # Skip metadata
                
                if isinstance(targets, list):
                    if targets:
                        connector = self.relationship_connectors.get(rel_type, rel_type.replace('_', ' '))
                        target_list = ', '.join(str(t) for t in targets[:3])
                        relationship_parts.append(f"{term} {connector} {target_list}")
                elif isinstance(targets, (str, int, float)):
                    connector = self.relationship_connectors.get(rel_type, rel_type.replace('_', ' '))
                    relationship_parts.append(f"{term} {connector} {targets}")
        
        if relationship_parts:
            return "Additionally, " + ". ".join(relationship_parts) + "."
        
        return ""
    
    def _synthesize_narrative(self, parts: List[str]) -> str:
        """Synthesize parts into coherent narrative."""
        if not parts:
            return "No information available."
        
        # Remove empty parts
        parts = [p for p in parts if p and p.strip()]
        
        if not parts:
            return "No information available."
        
        # Join with appropriate connectors
        narrative = parts[0]
        
        for i, part in enumerate(parts[1:], 1):
            # Check if part starts with capital or needs connection
            if part[0].isupper() or part.startswith(('It ', 'This ', 'For ', 'Additionally')):
                narrative += " " + part
            else:
                narrative += ". " + part
        
        # Ensure proper sentence structure
        narrative = re.sub(r'\.\s*\.', '.', narrative)  # Remove double periods
        narrative = re.sub(r'\s+', ' ', narrative)  # Normalize whitespace
        narrative = narrative.strip()
        
        # Ensure ends with period
        if narrative and not narrative.endswith(('.', '!', '?')):
            narrative += "."
        
        return narrative
    
    def generate_comprehensive_explanation(
        self,
        spr_data: Dict[str, Any],
        related_sprs: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate comprehensive explanation including related concepts.
        
        Args:
            spr_data: Primary SPR definition
            related_sprs: List of related SPR definitions
            
        Returns:
            Comprehensive natural language explanation
        """
        # Generate base explanation
        explanation = self.generate_explanation(spr_data)
        
        # Add related concepts if available
        if related_sprs:
            related_terms = []
            for related in related_sprs[:3]:  # Limit to 3 related concepts
                term = related.get('term', related.get('spr_id', ''))
                if term:
                    related_terms.append(term)
            
            if related_terms:
                explanation += f" Related concepts include: {', '.join(related_terms)}."
        
        return explanation
    
    def enhance_kg_response(self, kg_response: str, spr_data: Dict[str, Any]) -> str:
        """
        Enhance a minimal KG response with natural language generation.
        
        Args:
            kg_response: Original KG response (may be minimal)
            spr_data: Full SPR definition
            
        Returns:
            Enhanced natural language response
        """
        # If response is too minimal, generate full explanation
        if len(kg_response.strip()) < 100 or kg_response.count('\n') < 2:
            return self.generate_explanation(spr_data)
        
        # Otherwise, enhance existing response
        enhanced = kg_response
        
        # Add blueprint if missing
        if 'blueprint' not in enhanced.lower() and spr_data.get('blueprint_details'):
            blueprint_text = self._process_blueprint(spr_data['blueprint_details'])
            if blueprint_text:
                enhanced += f" {blueprint_text}"
        
        # Add relationships if missing
        if 'relationship' not in enhanced.lower() and spr_data.get('relationships'):
            rel_text = self._process_relationships(
                spr_data.get('term', spr_data.get('spr_id', '')),
                spr_data['relationships']
            )
            if rel_text:
                enhanced += f" {rel_text}"
        
        return enhanced

