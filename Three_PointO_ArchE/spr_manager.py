import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from .thought_trail import log_to_thought_trail

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

    @log_to_thought_trail
    def load_sprs(self):
        """Loads or reloads the SPR definitions from the JSON file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                spr_data = json.load(f)
            
            # Handle both dict and list formats
            if isinstance(spr_data, dict):
                # If it's a dictionary with spr_id keys, use them directly
                self.sprs = spr_data
                logger.info(f"Successfully loaded {len(self.sprs)} SPR definitions from {self.filepath} (dict format)")
            elif isinstance(spr_data, list):
                # If it's a list of objects, extract spr_id keys
                self.sprs = {spr['spr_id']: spr for spr in spr_data if isinstance(spr, dict) and 'spr_id' in spr}
                logger.info(f"Successfully loaded {len(self.sprs)} SPR definitions from {self.filepath} (list format)")
            else:
                logger.error(f"SPR data format is unrecognized in {self.filepath}")
                self.sprs = {}
                
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

    @log_to_thought_trail
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
    
    @log_to_thought_trail
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

    @log_to_thought_trail
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

    @log_to_thought_trail
    def get_spr_by_id(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single SPR definition by its ID.

        Args:
            spr_id: The ID of the SPR to retrieve.

        Returns:
            A dictionary containing the SPR definition, or None if not found.
        """
        return self.sprs.get(spr_id)

    @log_to_thought_trail
    def get_all_sprs(self) -> List[Dict[str, Any]]:
        """
        Retrieves all loaded SPR definitions.

        Returns:
            A list of all SPR definition dictionaries.
        """
        return list(self.sprs.values())

    @log_to_thought_trail
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
    
    # --- Universal Zepto SPR Integration Methods ---
    
    @log_to_thought_trail
    def compress_spr_to_zepto(
        self,
        spr_id: str,
        target_stage: str = "Zepto"
    ) -> Optional[Dict[str, Any]]:
        """
        Compress an SPR definition to Zepto SPR form using universal abstraction.
        
        Args:
            spr_id: The SPR ID to compress
            target_stage: Compression stage target (default: "Zepto")
            
        Returns:
            Dictionary with zepto_spr and metadata, or None if SPR not found
        """
        try:
            from .zepto_spr_processor import compress_to_zepto
            
            spr = self.get_spr_by_id(spr_id)
            if not spr:
                logger.warning(f"SPR '{spr_id}' not found for Zepto compression")
                return None
            
            # Convert SPR definition to narrative form
            narrative = self._spr_to_narrative(spr)
            
            # Compress using universal abstraction
            result = compress_to_zepto(narrative, target_stage)
            
            if result.error:
                logger.error(f"Zepto compression failed for SPR '{spr_id}': {result.error}")
                return None
            
            return {
                'spr_id': spr_id,
                'zepto_spr': result.zepto_spr,
                'compression_ratio': result.compression_ratio,
                'compression_stages': result.compression_stages,
                'new_codex_entries': result.new_codex_entries,
                'original_length': result.original_length,
                'zepto_length': result.zepto_length,
                'processing_time_sec': result.processing_time_sec
            }
            
        except ImportError as e:
            logger.warning(f"Zepto SPR processor not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Error compressing SPR '{spr_id}' to Zepto: {e}", exc_info=True)
            return None
    
    @log_to_thought_trail
    def decompress_zepto_to_spr(
        self,
        zepto_spr: str,
        codex: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Decompress a Zepto SPR back to narrative form using universal abstraction.
        
        Args:
            zepto_spr: The Zepto SPR string to decompress
            codex: Optional symbol codex (uses default if None)
            
        Returns:
            Decompressed narrative string, or None on error
        """
        try:
            from .zepto_spr_processor import decompress_from_zepto
            
            result = decompress_from_zepto(zepto_spr, codex)
            
            if result.error:
                logger.error(f"Zepto decompression failed: {result.error}")
                return None
            
            return result.decompressed_text
            
        except ImportError as e:
            logger.warning(f"Zepto SPR processor not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Error decompressing Zepto SPR: {e}", exc_info=True)
            return None
    
    def _spr_to_narrative(self, spr: Dict[str, Any]) -> str:
        """
        Convert SPR definition dictionary to narrative form for compression.
        
        Args:
            spr: SPR definition dictionary
            
        Returns:
            Narrative string representation
        """
        parts = []
        
        spr_id = spr.get('spr_id', 'Unknown')
        name = spr.get('name', spr_id)
        description = spr.get('description', '')
        category = spr.get('category', '')
        relationships = spr.get('relationships', {})
        blueprint_details = spr.get('blueprint_details', '')
        
        parts.append(f"SPR ID: {spr_id}")
        parts.append(f"Name: {name}")
        if description:
            parts.append(f"Description: {description}")
        if category:
            parts.append(f"Category: {category}")
        if relationships:
            parts.append(f"Relationships: {json.dumps(relationships, indent=2)}")
        if blueprint_details:
            parts.append(f"Blueprint Details: {blueprint_details}")
        
        return "\n".join(parts)
    
    @log_to_thought_trail
    def batch_compress_sprs_to_zepto(
        self,
        spr_ids: Optional[List[str]] = None,
        target_stage: str = "Zepto"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Batch compress multiple SPRs to Zepto form.
        
        Args:
            spr_ids: List of SPR IDs to compress (None = all SPRs)
            target_stage: Compression stage target
            
        Returns:
            Dictionary mapping spr_id to compression results
        """
        if spr_ids is None:
            spr_ids = list(self.sprs.keys())
        
        results = {}
        for spr_id in spr_ids:
            result = self.compress_spr_to_zepto(spr_id, target_stage)
            if result:
                results[spr_id] = result
        
        logger.info(f"Batch compressed {len(results)} SPRs to Zepto form")
        return results
