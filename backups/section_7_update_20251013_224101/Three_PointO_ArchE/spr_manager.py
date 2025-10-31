import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)

class SPRManager:
    """Manages Synergistic Protocol Resonance (SPR) definitions from a JSON file."""

    def __init__(self, spr_filepath: str):
        """
        Initializes the SPRManager and loads the definitions.

        Args:
            spr_filepath: The path to the JSON file containing SPR definitions.
        """
        if not spr_filepath:
            raise ValueError("SPRManager requires a valid file path.")
        
        self.filepath = Path(spr_filepath).resolve()
        self.sprs: Dict[str, Dict[str, Any]] = {}
        self.spr_pattern: Optional[re.Pattern] = None
        self.load_sprs()

    def load_sprs(self):
        """Loads or reloads the SPR definitions from the JSON file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                spr_data = json.load(f)
            
            # The SPR ID is now the 'spr_id' field in the JSON object
            self.sprs = {spr['spr_id']: spr for spr in spr_data if 'spr_id' in spr}
            logger.info(f"Successfully loaded {len(self.sprs)} SPR definitions from {self.filepath}")
        except FileNotFoundError:
            logger.warning(f"SPR file not found at {self.filepath}. Initializing with empty definitions.")
            self.sprs = {}
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from {self.filepath}. Check file for syntax errors.")
            self.sprs = {}
        except (TypeError, KeyError) as e:
            logger.error(f"SPR data format is invalid in {self.filepath}: {e}")
            self.sprs = {}
        
        self._compile_spr_pattern()

    def _compile_spr_pattern(self):
        """
        Compiles a regex pattern to efficiently find all registered SPR keys in a text.
        This is the 'musician learning the music'.
        """
        if not self.sprs:
            self.spr_pattern = None
            return
        # The keys are the spr_id's themselves
        spr_keys = [re.escape(key) for key in self.sprs.keys()]
        # Create a single regex pattern to find any of the keys as whole words
        pattern_str = r'\b(' + '|'.join(spr_keys) + r')\b'
        self.spr_pattern = re.compile(pattern_str)
        logger.info(f"Compiled SPR pattern for {len(spr_keys)} keys.")

    def scan_and_prime(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans a given text for all occurrences of registered SPR keys and returns
        the full definitions for each unique SPR found. This is 'striking the bells'.
        """
        if not self.spr_pattern or not isinstance(text, str):
            return []
        
        found_sprs: Set[str] = set(self.spr_pattern.findall(text))
        
        if found_sprs:
            logger.debug(f"Primed {len(found_sprs)} unique SPRs: {', '.join(sorted(list(found_sprs)))}")
        
        return [self.sprs[key] for key in sorted(list(found_sprs)) if key in self.sprs]
    
    def detect_sprs_with_confidence(self, text: str) -> List[Dict[str, Any]]:
        """
        Enhanced SPR detection with fuzzy matching, confidence scoring, and activation levels.
        Incorporates frontend sophistication into backend processing.
        """
        if not isinstance(text, str) or not text.strip():
            return []
        
        detected_sprs = []
        lower_text = text.lower()
        
        for spr_id, spr_data in self.sprs.items():
            activation_level = self._calculate_spr_activation(lower_text, spr_id)
            
            if activation_level > 0.3:  # Threshold for detection
                confidence_score = self._calculate_spr_confidence(lower_text, spr_id, activation_level)
                
                detected_sprs.append({
                    'spr_id': spr_id,
                    'spr_data': spr_data,
                    'activation_level': activation_level,
                    'confidence_score': confidence_score,
                    'guardian_point': spr_id,
                    'knowledge_network': {
                        'resonance_frequency': self._calculate_resonance_frequency(spr_id),
                        'activation_history': self._get_activation_history(spr_id),
                        'related_sprs': self._get_related_sprs(spr_id)
                    }
                })
        
        # Sort by activation level (highest first)
        detected_sprs.sort(key=lambda x: x['activation_level'], reverse=True)
        
        return detected_sprs
    
    def _calculate_spr_activation(self, text: str, spr_id: str) -> float:
        """Calculate SPR activation level using fuzzy matching techniques."""
        lower_spr = spr_id.lower()
        
        # Check for exact matches
        if lower_spr in text:
            return 0.9
        
        # Check for partial matches using CamelCase decomposition
        words = self._decompose_camelcase(spr_id)
        match_score = 0
        
        for word in words:
            if word.lower() in text:
                match_score += 0.2
        
        # Check for semantic variations
        variations = self._get_semantic_variations(spr_id)
        for variation in variations:
            if variation.lower() in text:
                match_score += 0.15
        
        return min(0.9, match_score)
    
    def _calculate_spr_confidence(self, text: str, spr_id: str, activation_level: float) -> float:
        """Calculate confidence score using weighted factors."""
        context_relevance = self._calculate_context_relevance(text, spr_id)
        semantic_clarity = self._calculate_semantic_clarity(text, spr_id)
        
        return (activation_level * 0.5) + (context_relevance * 0.3) + (semantic_clarity * 0.2)
    
    def _decompose_camelcase(self, text: str) -> List[str]:
        """Decompose CamelCase text into individual words."""
        import re
        return re.findall(r'[A-Z][a-z]*|[a-z]+', text)
    
    def _get_semantic_variations(self, spr_id: str) -> List[str]:
        """Get semantic variations for SPR detection."""
        variations_map = {
            'ExecutableSpecificationPrinciple': ['specification principle', 'executable principle', 'spec principle'],
            'AutopoieticSystemGenesis': ['autopoietic genesis', 'system genesis', 'self-creation'],
            'IntegratedActionReflection': ['action reflection', 'integrated reflection', 'reflection principle', 'IAR'],
            'SparsePrimingRepresentations': ['sparse priming', 'priming representations', 'SPR'],
            'VisualCognitiveDebugger': ['visual debugger', 'cognitive debugger', 'VCD'],
            'ResonantInsightStrategyEngine': ['resonant insight', 'strategy engine', 'RISE'],
            'SynergisticIntentResonanceCycle': ['synergistic intent', 'resonance cycle', 'SIRC'],
            'CognitiveResonanceCycle': ['cognitive resonance', 'resonance cycle', 'CRC']
        }
        return variations_map.get(spr_id, [])
    
    def _calculate_context_relevance(self, text: str, spr_id: str) -> float:
        """Calculate how well the SPR fits the current context."""
        # This would analyze semantic context - for now return a base score
        return 0.7
    
    def _calculate_semantic_clarity(self, text: str, spr_id: str) -> float:
        """Calculate semantic clarity of the SPR in context."""
        # This would analyze semantic clarity - for now return a base score
        return 0.8
    
    def _calculate_resonance_frequency(self, spr_id: str) -> float:
        """Calculate resonance frequency for the SPR."""
        # This would come from historical data - for now return a simulated value
        import random
        return random.uniform(0.2, 1.0)
    
    def _get_activation_history(self, spr_id: str) -> List[str]:
        """Get activation history for the SPR."""
        # This would come from historical data - for now return simulated history
        import random
        count = random.randint(1, 10)
        return [f"{spr_id} activated {count} times in recent sessions"]
    
    def _get_related_sprs(self, spr_id: str) -> List[str]:
        """Get related SPRs for the given SPR."""
        # This would come from relationship data - for now return related SPRs
        all_sprs = list(self.sprs.keys())
        return [spr for spr in all_sprs if spr != spr_id][:3]

    def _save_sprs(self) -> bool:
        """Saves the current state of SPR definitions back to the JSON file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                # The file is a list of the dictionary values
                json.dump(list(self.sprs.values()), f, indent=2)
            logger.info(f"Successfully saved {len(self.sprs)} SPRs to {self.filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save SPR file to {self.filepath}: {e}", exc_info=True)
            return False

    def add_spr(self, spr_definition: Dict[str, Any], save_to_file: bool = True) -> bool:
        """
        Adds a new SPR to the manager and optionally saves the updated ledger to file.
        This is 'forging a new bell'.
        """
        spr_id = spr_definition.get("spr_id")
        if not spr_id:
            logger.error("Cannot add SPR: 'spr_id' is a required field.")
            return False
            
        if spr_id in self.sprs:
            logger.warning(f"SPR with id '{spr_id}' already exists. Overwriting.")
            
        self.sprs[spr_id] = spr_definition
        logger.info(f"Added/Updated SPR '{spr_id}' in memory.")
        
        # Re-compile the pattern to include the new key
        self._compile_spr_pattern()
        
        if save_to_file:
            return self._save_sprs()
        
        return True

    def get_spr_by_id(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single SPR definition by its ID.

        Args:
            spr_id: The ID of the SPR to retrieve.

        Returns:
            A dictionary containing the SPR definition, or None if not found.
        """
        return self.sprs.get(spr_id)

    def get_all_sprs(self) -> List[Dict[str, Any]]:
        """
        Retrieves all loaded SPR definitions.

        Returns:
            A list of all SPR definition dictionaries.
        """
        return list(self.sprs.values())

    def search_sprs(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches SPR definitions for a query string in the name or description.

        Args:
            query: The string to search for.

        Returns:
            A list of matching SPR definitions.
        """
        results = []
        query_lower = query.lower()
        for spr in self.sprs.values():
            name = spr.get('name', '').lower()
            description = spr.get('description', '').lower()
            if query_lower in name or query_lower in description:
                results.append(spr)
        return results
