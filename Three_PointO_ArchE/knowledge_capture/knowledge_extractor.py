"""
Knowledge Extractor - Extracts core patterns from LLM responses
Implements lossy knowledge transfer principles: Signal vs. Noise separation

This component is the first stage of the Lossy Knowledge Capture System,
identifying universal patterns and principles from verbose LLM responses.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ExtractedPattern:
    """Core pattern extracted from LLM response"""
    pattern_id: str
    core_principle: str  # The universal abstraction
    context: str  # Original context (for reference)
    confidence: float  # How confident we are this is signal, not noise
    relationships: List[str]  # Related SPRs/concepts
    implementation_hints: Optional[str] = None  # Practical application
    noise_removed: List[str] = None  # What was filtered out
    extraction_timestamp: str = None
    
    def __post_init__(self):
        if self.noise_removed is None:
            self.noise_removed = []
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now().isoformat()


class KnowledgeExtractor:
    """
    Extracts core patterns from LLM responses using lossy knowledge transfer principles.
    
    Key Strategy:
    1. Identify signal (core principles, universal patterns)
    2. Remove noise (context-specific details, failed attempts, redundancy)
    3. Abstract to universal form (applicable across contexts)
    4. Extract relationships (connect to existing SPRs)
    
    This implements the "Lossy is Better" principle: capturing signal while
    removing noise enables efficient compression and storage.
    """
    
    def __init__(self, spr_manager=None):
        """
        Initialize Knowledge Extractor.
        
        Args:
            spr_manager: Optional SPRManager for finding related SPRs
        """
        self.spr_manager = spr_manager
        self.extraction_history = []
        
    def extract_from_llm_response(
        self,
        llm_response: str,
        query_context: Dict[str, Any],
        llm_metadata: Dict[str, Any] = None
    ) -> Optional[ExtractedPattern]:
        """
        Extract core pattern from LLM response.
        
        Args:
            llm_response: The full LLM response text
            query_context: Original query and context
            llm_metadata: LLM provider, model, tokens used, etc.
            
        Returns:
            ExtractedPattern if successful, None if no extractable pattern
        """
        if not llm_response or not isinstance(llm_response, str):
            logger.debug("Empty or invalid LLM response, skipping extraction")
            return None
        
        # Step 1: Identify signal vs. noise
        signal_elements = self._identify_signal(llm_response)
        noise_elements = self._identify_noise(llm_response)
        
        if not signal_elements:
            logger.debug("No signal elements found in LLM response")
            return None
        
        # Step 2: Extract core principle (universal abstraction)
        core_principle = self._extract_core_principle(signal_elements)
        
        if not core_principle:
            logger.debug("No extractable core principle found in LLM response")
            return None
        
        # Step 3: Abstract to universal form
        universal_pattern = self._abstract_to_universal(core_principle, query_context)
        
        # Step 4: Find relationships to existing SPRs
        relationships = self._find_related_sprs(universal_pattern)
        
        # Step 5: Extract implementation hints (practical application)
        implementation_hints = self._extract_implementation_hints(signal_elements)
        
        # Step 6: Calculate confidence (signal strength)
        confidence = self._calculate_confidence(signal_elements, noise_elements)
        
        # Step 7: Generate pattern ID
        pattern_id = self._generate_pattern_id(universal_pattern)
        
        pattern = ExtractedPattern(
            pattern_id=pattern_id,
            core_principle=universal_pattern,
            context=query_context.get("query", ""),
            confidence=confidence,
            relationships=relationships,
            implementation_hints=implementation_hints,
            noise_removed=noise_elements
        )
        
        self.extraction_history.append(pattern)
        logger.info(f"Extracted pattern: {pattern.pattern_id} (confidence: {confidence:.2f})")
        
        return pattern
    
    def _identify_signal(self, text: str) -> List[str]:
        """Identify signal elements: core principles, patterns, key insights"""
        signal_indicators = [
            r"(?:principle|pattern|rule|law|mechanism|process|method|approach|strategy|technique)",
            r"(?:always|never|must|should|typically|generally|usually|often)",
            r"(?:because|therefore|thus|consequently|as a result|hence)",
            r"(?:key|essential|critical|fundamental|core|important|crucial|vital)",
            r"(?:best practice|standard|convention|guideline|recommendation)",
        ]
        
        signal_elements = []
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
                
            for indicator in signal_indicators:
                if re.search(indicator, sentence, re.IGNORECASE):
                    signal_elements.append(sentence)
                    break
        
        return signal_elements
    
    def _identify_noise(self, text: str) -> List[str]:
        """Identify noise elements: context-specific, failed attempts, redundancy"""
        noise_indicators = [
            r"(?:example|instance|case|specific|particular|this|that|these|those)",
            r"(?:failed|error|mistake|wrong|incorrect|don't|shouldn't|avoid|never do)",
            r"(?:maybe|perhaps|possibly|might|could|uncertain|unclear|unlikely)",
            r"(?:I think|in my opinion|personally|I believe|I feel|I would)",
            r"(?:here|there|now|today|yesterday|tomorrow|recently)",
        ]
        
        noise_elements = []
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            for indicator in noise_indicators:
                if re.search(indicator, sentence, re.IGNORECASE):
                    noise_elements.append(sentence)
                    break
        
        return noise_elements
    
    def _extract_core_principle(self, signal_elements: List[str]) -> Optional[str]:
        """Extract the universal core principle from signal elements"""
        if not signal_elements:
            return None
        
        # Find the most abstract, universal statement
        core_sentences = [
            s for s in signal_elements
            if any(word in s.lower() for word in ["principle", "pattern", "rule", "law", "mechanism", "strategy"])
        ]
        
        if core_sentences:
            return core_sentences[0]  # Return first core principle found
        
        # Fallback: return most general signal element (longest, most structured)
        if signal_elements:
            # Prefer sentences with "should", "must", "always", etc.
            imperative_sentences = [
                s for s in signal_elements
                if any(word in s.lower() for word in ["should", "must", "always", "never", "typically"])
            ]
            if imperative_sentences:
                return imperative_sentences[0]
            
            # Return first signal element
            return signal_elements[0]
        
        return None
    
    def _abstract_to_universal(self, principle: str, context: Dict[str, Any]) -> str:
        """Abstract context-specific principle to universal form"""
        universal = principle
        
        # Replace specific examples with generic placeholders
        universal = re.sub(r'\b(this|that|these|those)\b', 'X', universal, flags=re.IGNORECASE)
        universal = re.sub(r'\b(here|there)\b', 'in context', universal, flags=re.IGNORECASE)
        
        # Remove specific names, dates, numbers (unless they're part of the principle)
        # Keep numbers that are part of rules (e.g., "3 steps", "5 principles")
        universal = re.sub(r'\b\d{4}\b', 'YYYY', universal)  # Years
        universal = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b', 
                          'Month', universal, flags=re.IGNORECASE)
        
        return universal.strip()
    
    def _find_related_sprs(self, pattern: str) -> List[str]:
        """Find related SPRs in Knowledge Graph"""
        if not self.spr_manager:
            return []
        
        try:
            # Use SPR manager to find related concepts
            related = self.spr_manager.scan_and_prime(pattern)
            return [spr.get("spr_id", "") for spr in related if spr.get("spr_id")]
        except Exception as e:
            logger.warning(f"Failed to find related SPRs: {e}")
            return []
    
    def _extract_implementation_hints(self, signal_elements: List[str]) -> Optional[str]:
        """Extract practical implementation hints"""
        implementation_keywords = ["implement", "use", "apply", "execute", "create", "build", "deploy", "configure"]
        
        for element in signal_elements:
            if any(keyword in element.lower() for keyword in implementation_keywords):
                return element
        
        return None
    
    def _calculate_confidence(self, signal: List[str], noise: List[str]) -> float:
        """Calculate confidence that extracted pattern is signal, not noise"""
        if not signal:
            return 0.0
        
        signal_ratio = len(signal) / (len(signal) + len(noise) + 1)
        
        # Boost confidence if pattern has relationships to existing SPRs
        relationship_boost = 0.0
        if self.spr_manager:
            try:
                related_count = len(self._find_related_sprs(" ".join(signal)))
                relationship_boost = min(0.2, related_count * 0.05)
            except Exception:
                pass
        
        # Boost confidence for longer, more structured signal
        structure_boost = min(0.1, len(signal) * 0.01)
        
        return min(1.0, signal_ratio + relationship_boost + structure_boost)
    
    def _generate_pattern_id(self, pattern: str) -> str:
        """Generate unique pattern ID following Guardian pointS format"""
        # Extract key words and create SPR-style ID
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', pattern)
        key_words = [w for w in words if len(w) > 4][:3]  # Take first 3 significant words
        
        if not key_words:
            key_words = ["Pattern", "Extracted"]
        
        # Format as Guardian pointS: FirstLastUppercase, middle lowercase
        # Take first letter of each word, capitalize appropriately
        pattern_id = ""
        for i, word in enumerate(key_words):
            if i == 0 or i == len(key_words) - 1:
                pattern_id += word.capitalize()
            else:
                pattern_id += word.lower()
        
        # Ensure it follows Guardian pointS: FirstUppercase...LastUppercase
        if len(pattern_id) > 0:
            pattern_id = pattern_id[0].upper() + pattern_id[1:-1].lower() + pattern_id[-1].upper()
        
        # Add timestamp suffix for uniqueness
        timestamp_suffix = datetime.now().strftime("%Y%m%d")[-6:]  # Last 6 digits
        pattern_id = f"{pattern_id[:20]}{timestamp_suffix}"
        
        return pattern_id

