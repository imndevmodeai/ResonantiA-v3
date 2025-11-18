"""
Pattern Crystallization Engine
The Alchemical Distiller - Extracts pure SPRs from verbose ThoughtTrails

This module implements the complete crystallization process that transforms
verbose narratives into hyper-dense symbolic SPRs (Zepto form), enabling
massive compression while preserving essential meaning.

The engine embodies Universal Abstraction in its purest form: the ability
to represent complex concepts as symbols, compare and manipulate them
according to deterministic rules, and crystallize entire analyses into
hyper-dense symbolic strings.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import datetime
import re

# Import temporal core for canonical timestamps
try:
    from .temporal_core import now_iso
except ImportError:
    def now_iso():
        return datetime.datetime.utcnow().isoformat() + 'Z'

# Import LLM tool for intelligent summarization and symbol generation
try:
    from .llm_tool import generate_text_llm
    from .llm_providers import get_llm_provider
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    generate_text_llm = None
    get_llm_provider = None


@dataclass
class CompressionStage:
    """Represents a single stage in the crystallization process."""
    stage_name: str  # "Narrative", "Concise", "Nano", "Micro", "Pico", "Femto", "Atto", "Zepto"
    content: str
    compression_ratio: float
    symbol_count: int
    timestamp: str


@dataclass
class SymbolCodexEntry:
    """
    Enhanced Symbol Codex Entry for preserving nuanced knowledge.
    
    Stores not just the meaning, but also:
    - Original patterns/phrases that map to this symbol
    - Relationships to other concepts
    - Critical specifics that must be preserved
    - Generalizable patterns
    - Contextual variations
    """
    symbol: str
    meaning: str  # Core definition
    context: str  # Domain/context
    usage_examples: List[str]  # Example SPRs using this symbol
    
    # Enhanced fields for nuanced knowledge preservation
    original_patterns: List[str] = None  # Original phrases/terms that compress to this symbol
    relationships: Dict[str, str] = None  # Related symbols/concepts: {"type": "related_symbol"}
    critical_specifics: List[str] = None  # Specific details that must be preserved (not generalized)
    generalizable_patterns: List[str] = None  # Patterns that can be generalized
    contextual_variations: Dict[str, str] = None  # Different meanings in different contexts
    decompression_template: str = None  # Template for reconstructing nuanced knowledge
    
    created_at: str = None
    
    def __post_init__(self):
        """Initialize optional fields with defaults."""
        if self.original_patterns is None:
            self.original_patterns = []
        if self.relationships is None:
            self.relationships = {}
        if self.critical_specifics is None:
            self.critical_specifics = []
        if self.generalizable_patterns is None:
            self.generalizable_patterns = []
        if self.contextual_variations is None:
            self.contextual_variations = {}
        if self.decompression_template is None:
            self.decompression_template = self.meaning


class PatternCrystallizationEngine:
    """
    The Alchemical Distiller. Extracts pure SPRs from verbose ThoughtTrails.
    
    This engine implements the complete crystallization process:
    1. Narrative Analysis
    2. Progressive Compression (8 stages)
    3. Symbol Codex Generation
    4. SPR Integration
    5. Decompression Validation
    """
    
    def __init__(self, symbol_codex_path: str = "knowledge_graph/symbol_codex.json", 
                 protocol_vocabulary_path: str = "knowledge_graph/protocol_symbol_vocabulary.json"):
        """Initialize the Crystallization Engine."""
        self.codex_path = Path(symbol_codex_path)
        self.protocol_vocab_path = Path(protocol_vocabulary_path)
        self.codex = self._load_codex()
        self.protocol_vocab = self._load_protocol_vocabulary()
        # Merge protocol vocabulary into main codex
        self.codex.update(self.protocol_vocab)
        self.compression_history: List[CompressionStage] = []
        
    def _load_codex(self) -> Dict[str, SymbolCodexEntry]:
        """Load the Symbol Codex from persistent storage.
        
        Handles concurrent access gracefully with retries for parallel processing.
        """
        if not self.codex_path.exists():
            return {}
        
        # Retry logic for concurrent file access (parallel processing)
        max_retries = 3
        retry_delay = 0.1  # 100ms
        
        for attempt in range(max_retries):
            try:
                # Use file locking for safe concurrent reads
                import fcntl
                with open(self.codex_path, 'r', encoding='utf-8') as f:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
                        data = json.load(f)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock
                    except (OSError, AttributeError):
                        # fcntl not available on Windows, fall back to regular read
                        f.seek(0)
                        data = json.load(f)
                    
                    return {
                        symbol: SymbolCodexEntry(**entry)
                        for symbol, entry in data.items()
                    }
            except (json.JSONDecodeError, ValueError) as e:
                # JSON parse error - might be due to concurrent write or corruption
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                # Last attempt failed - return empty codex (will be rebuilt)
                return {}
            except Exception as e:
                # Other errors (file not found, permission, etc.) - return empty
                return {}
        
        return {}
    
    def _load_protocol_vocabulary(self) -> Dict[str, SymbolCodexEntry]:
        """Load protocol-specific symbol vocabulary.
        
        Handles concurrent access gracefully with retries for parallel processing.
        """
        if not self.protocol_vocab_path.exists():
            return {}
        
        # Retry logic for concurrent file access (parallel processing)
        max_retries = 3
        retry_delay = 0.1  # 100ms
        
        for attempt in range(max_retries):
            try:
                # Use file locking for safe concurrent reads
                import fcntl
                with open(self.protocol_vocab_path, 'r', encoding='utf-8') as f:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
                        data = json.load(f)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock
                    except (OSError, AttributeError):
                        # fcntl not available on Windows, fall back to regular read
                        f.seek(0)
                        data = json.load(f)
                    
                    vocab = {}
                    # Flatten nested structure (protocol_core_symbols, mandate_symbols, etc.)
                    for category, symbols in data.items():
                        for symbol, entry in symbols.items():
                            vocab[symbol] = SymbolCodexEntry(**entry)
                    return vocab
            except (json.JSONDecodeError, ValueError) as e:
                # JSON parse error - might be due to concurrent write or corruption
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                # Last attempt failed - return empty vocab
                return {}
            except Exception as e:
                # Other errors - return empty vocab
                return {}
        
        return {}
    
    def _save_codex(self):
        """Save the Symbol Codex to persistent storage."""
        self.codex_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.codex_path, 'w', encoding='utf-8') as f:
            json.dump(
                {
                    symbol: asdict(entry)
                    for symbol, entry in self.codex.items()
                },
                f,
                indent=2,
                ensure_ascii=False
            )
    
    def distill_to_spr(
        self,
        thought_trail_entry: str,
        target_stage: str = "Zepto"
    ) -> Tuple[str, Dict[str, SymbolCodexEntry], List[CompressionStage]]:
        """
        Performs the multi-stage distillation of a narrative into a symbolic SPR.
        
        Russian Doll Architecture: Creates nested layers of compression, each preserving
        different levels of detail. All layers are stored for progressive retrieval.
        
        Args:
            thought_trail_entry: The verbose narrative to compress
            target_stage: The final compression stage ("Concise", "Nano", "Micro", "Pico", "Femto", "Atto", "Zepto")
            
        Returns:
            Tuple of (pure_spr_string, new_codex_entries, compression_stages)
            - pure_spr_string: The final Zepto SPR (innermost doll)
            - new_codex_entries: Enhanced symbol codex with nuanced knowledge
            - compression_stages: All compression layers (Russian dolls) for layered retrieval
        """
        # Reset compression history for new run
        self.compression_history = []
        initial_len = len(thought_trail_entry)
        
        # Stage 0: Narrative layer (outermost Russian doll - complete original content)
        self.compression_history.append(CompressionStage(
            stage_name="Narrative",
            content=thought_trail_entry,
            compression_ratio=1.0,  # No compression - complete preservation
            symbol_count=len(thought_trail_entry),
            timestamp=now_iso()
        ))
        
        # Stage 1: Narrative to Concise Form (LLM-assisted summarization)
        concise_form = self._summarize(thought_trail_entry)
        self.compression_history.append(CompressionStage(
            stage_name="Concise",
            content=concise_form,
            compression_ratio=initial_len / len(concise_form) if concise_form else 1.0,
            symbol_count=len(concise_form),
            timestamp=now_iso()
        ))
        
        # Stage 2-7: Progressive Symbolic Substitution
        current_form = concise_form
        stages = ["Nano", "Micro", "Pico", "Femto", "Atto"]
        
        for stage in stages:
            if target_stage == stage:
                break
            current_form = self._symbolize(current_form, stage)
            self.compression_history.append(CompressionStage(
                stage_name=stage,
                content=current_form,
                compression_ratio=initial_len / len(current_form) if current_form else 1.0,
                symbol_count=len(current_form),
                timestamp=now_iso()
            ))
        
        # Stage 8: Final Crystallization (Zepto)
        if target_stage == "Zepto":
            pure_spr = self._finalize_crystal(current_form)
            self.compression_history.append(CompressionStage(
                stage_name="Zepto",
                content=pure_spr,
                compression_ratio=initial_len / len(pure_spr) if pure_spr else 1.0,
                symbol_count=len(pure_spr),
                timestamp=now_iso()
            ))
        else:
            pure_spr = current_form
        
        # Stage 9: Generate/Update Codex
        new_codex_entries = self._update_codex(pure_spr, thought_trail_entry)
        
        # Save updated codex
        self._save_codex()
        
        # Return SPR, codex entries, AND compression stages (Russian dolls)
        return pure_spr, new_codex_entries, self.compression_history.copy()
    
    def _summarize(self, narrative: str) -> str:
        """
        Stage 1: Narrative to Concise Form - AGGRESSIVE MULTI-PASS COMPRESSION.
        
        Uses iterative LLM-assisted summarization to achieve 0.1-1% of original length.
        Each pass becomes more aggressive, targeting deeper compression.
        """
        if not LLM_AVAILABLE or not get_llm_provider:
            # Fallback: Basic length reduction
            return narrative[:max(len(narrative)//2, 100)]
        
        current_text = narrative
        target_ratio = 0.01  # Target 1% of original (100:1 compression)
        max_passes = 3  # Maximum number of compression passes
        min_compression_per_pass = 0.5  # Each pass must compress by at least 50%
        
        for pass_num in range(max_passes):
            try:
                if get_llm_provider:
                    provider = get_llm_provider("groq")
                    
                    # Calculate target length for this pass
                    current_length = len(current_text)
                    target_length = max(int(current_length * target_ratio), 100)
                    
                    # Progressively more aggressive prompts
                    if pass_num == 0:
                        compression_target = "10-20%"
                        detail_level = "preserve all key concepts, principles, and technical details"
                    elif pass_num == 1:
                        compression_target = "5-10%"
                        detail_level = "preserve only core concepts and essential relationships"
                    else:  # pass_num == 2
                        compression_target = "1-2%"
                        detail_level = "preserve only the most critical information and relationships"
                    
                    prompt = f"""You are the Pattern Crystallization Engine's aggressive summarization stage (Pass {pass_num + 1}/{max_passes}).

Your task is to EXTREMELY compress the following narrative:
1. Remove ALL allegorical language, descriptive prose, examples, and verbose explanations
2. {detail_level}
3. Use dense, technical language with minimal words
4. Eliminate redundancy completely
5. Use abbreviations and symbols where possible

Target: Reduce to {compression_target} of current length ({current_length} chars → target: {target_length} chars).

Current text ({current_length} chars):
{current_text[:8000]}{'...' if len(current_text) > 8000 else ''}

Compressed form (dense, no redundancy, preserve critical logic only):"""
                    
                    compressed = provider.generate(
                        prompt=prompt,
                        model="llama-3.3-70b-versatile",
                        temperature=0.1,  # Very low for maximum compression
                        max_tokens=min(target_length, 4000)  # Limit output tokens
                    )
                    
                    if compressed and len(compressed.strip()) > 0:
                        compressed = compressed.strip()
                        # Only use if we got meaningful compression
                        if len(compressed) < current_length * min_compression_per_pass:
                            current_text = compressed
                            print(f"  Pass {pass_num + 1}: {current_length:,} → {len(current_text):,} chars ({current_length/len(current_text):.1f}:1)")
                            # If we've achieved target ratio, stop
                            if len(current_text) <= target_length:
                                break
                        else:
                            print(f"  Pass {pass_num + 1}: Compression insufficient ({len(compressed):,} chars), stopping")
                            break
                    else:
                        print(f"  Pass {pass_num + 1}: Empty response, stopping")
                        break
            except Exception as e:
                print(f"Warning: LLM summarization pass {pass_num + 1} failed: {e}")
                if pass_num == 0:
                    # Only fallback on first pass failure
                    return narrative[:max(len(narrative)//2, 100)]
                break
        
        return current_text
    
    def _symbolize(self, text: str, stage: str) -> str:
        """
        Stage 2-7: Progressive Symbolic Substitution - LLM-FREE RULE-BASED COMPRESSION.
        
        Applies progressively more aggressive rule-based compression at each stage.
        Each stage compresses more than the previous, creating true Russian Doll layers.
        """
        import re
        result = text
        original_len = len(result)
        
        # Stage-specific compression aggressiveness
        stage_levels = {
            "Nano": 1,    # Light compression
            "Micro": 2,   # Moderate compression
            "Pico": 3,    # Aggressive compression
            "Femto": 4,   # Very aggressive compression
            "Atto": 5     # Maximum compression before Zepto
        }
        compression_level = stage_levels.get(stage, 1)
        
        # Pass 1: Direct symbol substitutions from codex (longest meaning first)
        # Prioritize protocol vocabulary symbols
        protocol_symbols = [(s, e) for s, e in self.codex.items() if s in self.protocol_vocab]
        other_symbols = [(s, e) for s, e in self.codex.items() if s not in self.protocol_vocab]
        sorted_symbols = protocol_symbols + other_symbols
        
        for symbol, entry in sorted_symbols:
            # Try multiple phrase matching strategies
            meaning_full = entry.meaning
            meaning_short = meaning_full.split(' - ')[0].strip()
            
            # Strategy 1: Direct phrase matching (case-insensitive)
            if meaning_short and len(meaning_short) > 3 and symbol:
                try:
                    escaped_meaning = re.escape(meaning_short)
                    pattern = re.compile(escaped_meaning, re.IGNORECASE)
                    escaped_symbol = symbol.replace('\\', '\\\\').replace('$', '\\$')
                    result = pattern.sub(escaped_symbol, result)
                except re.error:
                    continue
            
            # Strategy 2: Key term matching (for higher compression levels)
            if compression_level >= 2:
                key_terms = meaning_short.split()
                for term in key_terms:
                    if len(term) > 4:  # Only substantial terms
                        # Replace whole words that match key terms
                        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                        result = pattern.sub(symbol, result)
        
        # Pass 2: Aggressive symbol replacement (always applied)
        result = self._apply_aggressive_symbol_replacement(result)
        
        # Pass 3: Progressive text compression based on stage level
        if compression_level >= 2:
            # Remove common connecting words
            common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 
                          'that', 'with', 'have', 'this', 'from', 'when', 'where', 'what', 
                          'which', 'will', 'would', 'could', 'should', 'may', 'might']
            for word in common_words:
                result = re.sub(r'\b' + word + r'\b', '', result, flags=re.IGNORECASE)
            result = re.sub(r'\s+', ' ', result).strip()
        
        if compression_level >= 3:
            # Abbreviate common phrases
            abbreviations = {
                r'\baction\s+context\b': 'AC',
                r'\bworkflow\s+engine\b': 'WE',
                r'\btask\s+metadata\b': 'TM',
                r'\bexecution\s+state\b': 'ES',
                r'\bruntime\s+context\b': 'RC',
                r'\bknowledge\s+graph\b': 'KG',
                r'\bsymbol\s+codex\b': 'SC',
            }
            for pattern, abbrev in abbreviations.items():
                result = re.sub(pattern, abbrev, result, flags=re.IGNORECASE)
        
        if compression_level >= 4:
            # Remove articles and prepositions
            articles_preps = ['a', 'an', 'the', 'in', 'on', 'at', 'to', 'of', 'for', 
                            'with', 'by', 'from', 'as', 'is', 'was', 'be', 'been']
            for word in articles_preps:
                result = re.sub(r'\b' + word + r'\b', '', result, flags=re.IGNORECASE)
            result = re.sub(r'\s+', ' ', result).strip()
        
        if compression_level >= 5:
            # Maximum compression: Keep only key terms and symbols
            # Extract capitalized words and symbols, remove lowercase words
            words = result.split()
            key_terms = []
            for word in words:
                # Keep: symbols, capitalized words, abbreviations, numbers
                if (any(c in word for c in 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩÆ') or
                    word[0].isupper() or 
                    word.isupper() or
                    word.isdigit() or
                    len(word) <= 2):  # Keep short abbreviations
                    key_terms.append(word)
            result = ' '.join(key_terms)
            result = re.sub(r'\s+', ' ', result).strip()
        
        # Ensure we actually compressed (if not, apply fallback compression)
        if len(result) >= original_len * 0.95:  # Less than 5% compression
            # Fallback: aggressive word removal
            words = result.split()
            # Keep only: symbols, capitalized words, words > 4 chars
            filtered = [w for w in words if 
                       any(c in w for c in 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩÆ') or
                       w[0].isupper() or len(w) > 4]
            result = ' '.join(filtered) if filtered else result
            result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def _apply_aggressive_symbol_replacement(self, text: str) -> str:
        """Apply aggressive rule-based symbol replacement for common patterns."""
        result = text
        
        # Common protocol phrase patterns (case-insensitive matching)
        replacements = {
            # Core concepts
            "cognitive resonance": "Ω",
            "temporal resonance": "Δ",
            "integrated action reflection": "Φ",
            "iar": "Φ",
            "sparse priming representation": "Θ",
            "spr": "Θ",
            "pattern crystallization": "Π",
            "as above so below": "Λ",
            "thought trail": "Σ",
            "thoughttrail": "Σ",
            "arche": "Æ",
            # System components
            "guardian points": "G",
            "guardian pointS": "G",
            "workflow engine": "W",
            "knowledge graph": "K",
            "symbol codex": "C",
            "knowledge network oneness": "KnO",
            "kno": "KnO",
            # Common technical terms
            "definition": "D",
            "implementation": "I",
            "preservation": "P",
            "format": "F",
            "mechanism": "M",
            "system": "S",
            "process": "P",
            "protocol": "P",
            "mandate": "M",
            # Action types
            "action reflection": "Φ",
            "metacognitive shift": "MS",
            "sirc": "SIRC",
            "insight solidification": "IS",
        }
        
        # Apply replacements (case-insensitive)
        import re
        for phrase, symbol in replacements.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            result = pattern.sub(symbol, result)
        
        # Add mandate replacements (using Unicode subscripts)
        mandate_subscripts = ['₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉', '₁₀', '₁₁', '₁₂']
        for i in range(1, 13):
            subscript = mandate_subscripts[i-1]
            result = re.sub(rf'\b[Mm]andate\s+{i}\b', f'M{subscript}', result, flags=re.IGNORECASE)
            result = re.sub(rf'\bM{i}\b', f'M{subscript}', result)
        
        # Remove common English words that shouldn't be in symbolic form
        common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'that', 'with', 'have', 'this', 'from', 'when', 'where', 'what', 'which']
        for word in common_words:
            result = re.sub(rf'\b{word}\b', '', result, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def _finalize_crystal(self, symbolic_form: str) -> str:
        """
        Stage 8: Final Crystallization.
        
        Applies final optimizations to create the pure Zepto SPR:
        - Removes remaining linguistic artifacts
        - Converts remaining text to symbols
        - Optimizes symbol density
        - Validates symbolic integrity
        
        CRITICAL: This must produce actual symbolic output, not readable text.
        """
        result = symbolic_form
        
        # Step 1: Remove whitespace
        result = ''.join(result.split()).strip()
        
        # Step 2: If result is still readable text (contains lowercase letters, spaces, common words),
        # apply aggressive symbolization to convert it to actual symbols
        if len(result) > 50 or self._is_readable_text(result):
            # Apply aggressive symbol replacement one more time
            result = self._apply_aggressive_symbol_replacement(result)
            
            # If still readable, try to extract key concepts and create minimal symbolic representation
            if self._is_readable_text(result) and len(result) > 20:
                # Extract key symbols that are already present
                existing_symbols = re.findall(r'[ΓΣΔΘΛΞΠΦΨΩΑΒΕΗΙΚΜΝΟΡΤΥΧÆ]', result)
                
                # Try to create a minimal symbolic representation
                # Use first letters of key words as fallback symbols
                words = re.findall(r'[A-Z][a-z]+', result)
                if words and len(existing_symbols) == 0:
                    # No existing symbols, create minimal representation from key concepts
                    key_concepts = [w[0].upper() for w in words[:5]]
                    result = '|'.join(key_concepts) if len(key_concepts) > 1 else key_concepts[0] if key_concepts else 'Ξ'
                elif existing_symbols:
                    # Use existing symbols, combine them
                    result = '|'.join(existing_symbols[:5])
                else:
                    # Ultimate fallback: single symbol
                    result = 'Ξ'
        
        # Step 3: Remove any remaining lowercase letters and common words
        # Keep only symbols, uppercase abbreviations, and special characters
        result = re.sub(r'[a-z]+', '', result)  # Remove lowercase words
        result = re.sub(r'\b(the|and|for|are|but|not|you|all|can|had|her|was|one|our|out|day|get|has|him|his|how)\b', '', result, flags=re.IGNORECASE)
        
        # Step 4: Clean up and optimize
        result = result.strip()
        
        # If result is empty or too long, create minimal symbolic representation
        if not result or len(result) > 50:
            # Extract any symbols present
            symbols = re.findall(r'[ΓΣΔΘΛΞΠΦΨΩΑΒΕΗΙΚΜΝΟΡΤΥΧÆ|]', result)
            if symbols:
                result = '|'.join(symbols[:5])
            else:
                result = 'Ξ'  # Unknown symbol
        
        return result
    
    def _is_readable_text(self, text: str) -> bool:
        """Check if text is readable (contains lowercase letters, common words) rather than symbolic."""
        if not text:
            return False
        
        # Count lowercase letters
        lowercase_count = len([c for c in text if c.islower()])
        total_alpha = len([c for c in text if c.isalpha()])
        
        # If more than 30% lowercase, it's readable text
        if total_alpha > 0 and lowercase_count / total_alpha > 0.3:
            return True
        
        # Check for common English words
        common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'that', 'with', 'have', 'this']
        text_lower = text.lower()
        word_count = sum(1 for word in common_words if word in text_lower)
        
        # If contains common words, it's readable
        if word_count > 0:
            return True
        
        return False
    
    def _update_codex(
        self,
        pure_spr: str,
        original_narrative: str
    ) -> Dict[str, SymbolCodexEntry]:
        """
        Stage 9: Generate/Update Symbol Codex.
        
        Analyzes the pure SPR and original narrative to identify
        new symbols and their meanings, updating the codex.
        """
        new_entries = {}
        
        # Extract symbols from SPR
        symbols = self._extract_symbols(pure_spr)
        
        # For each symbol, infer enhanced meaning from original narrative
        for symbol in symbols:
            if symbol not in self.codex:
                meaning_data = self._infer_symbol_meaning(symbol, original_narrative)
                entry = SymbolCodexEntry(
                    symbol=symbol,
                    meaning=meaning_data["definition"],
                    context=meaning_data["context"],
                    usage_examples=[pure_spr],
                    original_patterns=meaning_data.get("original_patterns", []),
                    relationships=meaning_data.get("relationships", {}),
                    critical_specifics=meaning_data.get("critical_specifics", []),
                    generalizable_patterns=meaning_data.get("generalizable_patterns", []),
                    contextual_variations=meaning_data.get("contextual_variations", {}),
                    decompression_template=meaning_data.get("decompression_template", meaning_data["definition"]),
                    created_at=now_iso()
                )
                new_entries[symbol] = entry
                self.codex[symbol] = entry
            else:
                # Update existing entry with new usage example
                existing_entry = self.codex[symbol]
                if pure_spr not in existing_entry.usage_examples:
                    existing_entry.usage_examples.append(pure_spr)
        
        return new_entries
    
    def _extract_symbols(self, spr: str) -> List[str]:
        """Extract unique symbols from SPR string."""
        # Identify mathematical symbols, special characters, etc.
        # Exclude common punctuation but keep mathematical/special symbols
        symbols = re.findall(r'[^\w\s,.!?;:"\'\[\](){}]', spr)
        return list(set(symbols))
    
    def _infer_symbol_meaning(self, symbol: str, narrative: str) -> Dict[str, Any]:
        """
        Enhanced symbol meaning inference that preserves nuanced knowledge.
        
        Extracts:
        - Core definition
        - Original patterns/phrases
        - Critical specifics (must preserve)
        - Generalizable patterns (can abstract)
        - Relationships to other concepts
        - Contextual variations
        - Decompression template
        """
        if not LLM_AVAILABLE or not get_llm_provider:
            # Fallback: Basic extraction
            return {
                "definition": f"Symbol extracted: {symbol}",
                "context": "Inferred from narrative context",
                "original_patterns": [],
                "critical_specifics": [],
                "generalizable_patterns": [],
                "relationships": {},
                "contextual_variations": {},
                "decompression_template": f"Symbol extracted: {symbol}"
            }
        
        try:
            if get_llm_provider:
                provider = get_llm_provider("groq")
                
                prompt = f"""You are the Pattern Crystallization Engine's enhanced symbol inference stage.

A symbol "{symbol}" was extracted from the following narrative. 
Your task is to extract COMPLETE nuanced knowledge about this symbol to enable:
1. Accurate decompression with all specifics preserved
2. Pattern generalization where appropriate
3. Novel application of observed patterns

Narrative context:
{narrative[:3000]}

Extract and provide:

1. DEFINITION: Core meaning (max 50 words)
2. CONTEXT: Domain/context (e.g., "CFP Analysis", "Protocol Definition")
3. ORIGINAL_PATTERNS: List of original phrases/terms from the narrative that map to this symbol (comma-separated)
4. CRITICAL_SPECIFICS: Specific details that MUST be preserved (not generalized) - these are unique, important specifics (one per line)
5. GENERALIZABLE_PATTERNS: Patterns that can be abstracted/generalized for novel applications (one per line)
6. RELATIONSHIPS: Related symbols/concepts in format "symbol:relationship_type" (one per line, e.g., "Ω:core_concept", "Δ:temporal_related")
7. CONTEXTUAL_VARIATIONS: Different meanings in different contexts in format "context:meaning" (one per line)
8. DECOMPRESSION_TEMPLATE: Template for reconstructing nuanced knowledge (include placeholders for specifics)

Format your response as:
DEFINITION: [definition]
CONTEXT: [context]
ORIGINAL_PATTERNS: [pattern1, pattern2, ...]
CRITICAL_SPECIFICS:
- [specific detail 1]
- [specific detail 2]
GENERALIZABLE_PATTERNS:
- [pattern 1]
- [pattern 2]
RELATIONSHIPS:
- [symbol:type]
CONTEXTUAL_VARIATIONS:
- [context:meaning]
DECOMPRESSION_TEMPLATE: [template with {placeholders} for specifics]"""
                
                response = provider.generate(
                    prompt=prompt,
                    model="llama-3.3-70b-versatile",
                    temperature=0.3,  # Lower for more precise extraction
                    max_tokens=800  # More tokens for nuanced extraction
                )
                
                if response and len(response.strip()) > 0:
                    return self._parse_enhanced_symbol_response(response, symbol)
            
            # Fallback
            return self._create_fallback_symbol_data(symbol)
            
        except Exception as e:
            print(f"Warning: Enhanced LLM symbol inference failed: {e}, using fallback")
            return self._create_fallback_symbol_data(symbol)
    
    def _parse_enhanced_symbol_response(self, response: str, symbol: str) -> Dict[str, Any]:
        """Parse the enhanced LLM response into structured data."""
        result = {
                "definition": f"Symbol extracted: {symbol}",
            "context": "Inferred from narrative context",
            "original_patterns": [],
            "critical_specifics": [],
            "generalizable_patterns": [],
            "relationships": {},
            "contextual_variations": {},
            "decompression_template": f"Symbol extracted: {symbol}"
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if line.startswith("DEFINITION:"):
                result["definition"] = line.replace("DEFINITION:", "").strip()[:200]
                current_section = None
            elif line.startswith("CONTEXT:"):
                result["context"] = line.replace("CONTEXT:", "").strip()[:100]
                current_section = None
            elif line.startswith("ORIGINAL_PATTERNS:"):
                patterns = line.replace("ORIGINAL_PATTERNS:", "").strip()
                result["original_patterns"] = [p.strip() for p in patterns.split(',') if p.strip()]
                current_section = None
            elif line.startswith("CRITICAL_SPECIFICS:"):
                current_section = "critical_specifics"
            elif line.startswith("GENERALIZABLE_PATTERNS:"):
                current_section = "generalizable_patterns"
            elif line.startswith("RELATIONSHIPS:"):
                current_section = "relationships"
            elif line.startswith("CONTEXTUAL_VARIATIONS:"):
                current_section = "contextual_variations"
            elif line.startswith("DECOMPRESSION_TEMPLATE:"):
                result["decompression_template"] = line.replace("DECOMPRESSION_TEMPLATE:", "").strip()[:500]
                current_section = None
            elif current_section == "critical_specifics" and line.startswith("-"):
                result["critical_specifics"].append(line[1:].strip())
            elif current_section == "generalizable_patterns" and line.startswith("-"):
                result["generalizable_patterns"].append(line[1:].strip())
            elif current_section == "relationships" and line.startswith("-"):
                rel_line = line[1:].strip()
                if ":" in rel_line:
                    parts = rel_line.split(":", 1)
                    result["relationships"][parts[0].strip()] = parts[1].strip()
            elif current_section == "contextual_variations" and line.startswith("-"):
                var_line = line[1:].strip()
                if ":" in var_line:
                    parts = var_line.split(":", 1)
                    result["contextual_variations"][parts[0].strip()] = parts[1].strip()
        
        return result
    
    def _create_fallback_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Create fallback symbol data structure."""
        return {
            "definition": f"Symbol extracted: {symbol}",
            "context": "Inferred from narrative context",
            "original_patterns": [],
            "critical_specifics": [],
            "generalizable_patterns": [],
            "relationships": {},
            "contextual_variations": {},
            "decompression_template": f"Symbol extracted: {symbol}"
        }
    
    def decompress_spr(
        self,
        zepto_spr: str,
        codex: Optional[Dict[str, SymbolCodexEntry]] = None,
        target_layer: Optional[str] = None,
        compression_stages: Optional[List[CompressionStage]] = None
    ) -> str:
        """
        Layered Decompression: Russian Doll Architecture
        
        Decompresses Zepto SPR through progressive layers, like Russian dolls.
        Each layer adds more detail and nuance.
        
        Args:
            zepto_spr: The Zepto SPR to decompress
            codex: Symbol codex (uses default if None)
            target_layer: Target decompression layer ("Zepto", "Atto", "Femto", "Pico", "Micro", "Nano", "Concise", "Narrative")
                         If None, decompresses to most detailed available layer
            compression_stages: Optional list of compression stages for layered retrieval
            
        Returns:
            Decompressed text at the specified layer
        """
        if codex is None:
            codex = self.codex
        
        # If compression stages provided, use layered retrieval
        if compression_stages and target_layer:
            return self._retrieve_from_layer(zepto_spr, target_layer, compression_stages, codex)
        
        # Progressive layered decompression: Start from Zepto and work outward
        # Each layer adds more nuance and detail
        result = zepto_spr
        
        # Layer 1: Basic symbol replacement (Zepto → Atto level)
        result = self._decompress_layer_symbols(result, codex, layer="symbolic")
        
        # Layer 2: Add critical specifics (Atto → Femto level)
        result = self._decompress_layer_specifics(result, codex)
        
        # Layer 3: Add relationships and context (Femto → Pico level)
        result = self._decompress_layer_relationships(result, codex)
        
        # Layer 4: Add generalizable patterns (Pico → Micro level)
        result = self._decompress_layer_patterns(result, codex)
        
        # Layer 5: Full nuanced reconstruction (Micro → Narrative level)
        result = self._decompress_layer_nuanced(result, codex)
        
        return result
    
    def _retrieve_from_layer(
        self,
        zepto_spr: str,
        target_layer: str,
        compression_stages: List[CompressionStage],
        codex: Dict[str, SymbolCodexEntry]
    ) -> str:
        """
        Retrieve content from a specific compression layer (Russian doll retrieval).
        
        This allows accessing knowledge at the appropriate level of detail.
        """
        # Find the stage matching target_layer
        stage_map = {stage.stage_name: stage for stage in compression_stages}
        
        if target_layer in stage_map:
            # Return the content at that layer
            layer_content = stage_map[target_layer].content
            
            # Apply appropriate decompression for that layer
            if target_layer == "Zepto":
                # Pure symbolic - minimal decompression
                return self._decompress_layer_symbols(layer_content, codex, layer="symbolic")
            elif target_layer in ["Atto", "Femto"]:
                # Symbolic with some specifics
                result = self._decompress_layer_symbols(layer_content, codex, layer="symbolic")
                return self._decompress_layer_specifics(result, codex)
            elif target_layer in ["Pico", "Micro"]:
                # With relationships
                result = self._decompress_layer_symbols(layer_content, codex, layer="symbolic")
                result = self._decompress_layer_specifics(result, codex)
                return self._decompress_layer_relationships(result, codex)
            elif target_layer in ["Nano", "Concise"]:
                # With patterns
                result = self._decompress_layer_symbols(layer_content, codex, layer="symbolic")
                result = self._decompress_layer_specifics(result, codex)
                result = self._decompress_layer_relationships(result, codex)
                return self._decompress_layer_patterns(result, codex)
            else:
                # Narrative level - return as-is or with full decompression
                return layer_content
        
        # Fallback: progressive decompression
        return self.decompress_spr(zepto_spr, codex)
    
    def _decompress_layer_symbols(
        self,
        text: str,
        codex: Dict[str, SymbolCodexEntry],
        layer: str = "symbolic"
    ) -> str:
        """Layer 1: Replace symbols with basic meanings."""
        result = text
        for symbol, entry in sorted(codex.items(), key=lambda x: len(x[0]), reverse=True):
            if symbol in result:
                if isinstance(entry, SymbolCodexEntry):
                    meaning = entry.meaning
                elif isinstance(entry, dict):
                    meaning = entry.get('meaning', entry.get('symbol', symbol))
                else:
                    meaning = str(entry)
                result = result.replace(symbol, f"[{meaning}]")
        return result
    
    def _decompress_layer_specifics(
        self,
        text: str,
        codex: Dict[str, SymbolCodexEntry]
    ) -> str:
        """Layer 2: Add critical specifics that must be preserved."""
        result = text
        for symbol, entry in sorted(codex.items(), key=lambda x: len(x[0]), reverse=True):
            if symbol in result or f"[{entry.meaning if isinstance(entry, SymbolCodexEntry) else entry.get('meaning', '')}]" in result:
                if isinstance(entry, SymbolCodexEntry):
                    if entry.critical_specifics:
                        # Add critical specifics as annotations
                        specifics_text = "; ".join(entry.critical_specifics[:3])  # Limit to 3 most important
                        result = result.replace(
                            f"[{entry.meaning}]",
                            f"[{entry.meaning} | Critical: {specifics_text}]"
                        )
                elif isinstance(entry, dict):
                    specifics = entry.get('critical_specifics', [])
                    if specifics:
                        meaning = entry.get('meaning', '')
                        specifics_text = "; ".join(specifics[:3])
                        result = result.replace(
                            f"[{meaning}]",
                            f"[{meaning} | Critical: {specifics_text}]"
                        )
        return result
    
    def _decompress_layer_relationships(
        self,
        text: str,
        codex: Dict[str, SymbolCodexEntry]
    ) -> str:
        """Layer 3: Add relationships and contextual information."""
        result = text
        for symbol, entry in sorted(codex.items(), key=lambda x: len(x[0]), reverse=True):
            if isinstance(entry, SymbolCodexEntry):
                if entry.relationships:
                    # Add relationship annotations
                    rels_text = ", ".join([f"{k}:{v}" for k, v in list(entry.relationships.items())[:3]])
                    if rels_text:
                        result = result.replace(
                            f"[{entry.meaning}",
                            f"[{entry.meaning} | Related: {rels_text}"
                        )
            elif isinstance(entry, dict):
                rels = entry.get('relationships', {})
                if rels:
                    meaning = entry.get('meaning', '')
                    rels_text = ", ".join([f"{k}:{v}" for k, v in list(rels.items())[:3]])
                    if rels_text:
                        result = result.replace(
                            f"[{meaning}",
                            f"[{meaning} | Related: {rels_text}"
                        )
        return result
    
    def _decompress_layer_patterns(
        self,
        text: str,
        codex: Dict[str, SymbolCodexEntry]
    ) -> str:
        """Layer 4: Add generalizable patterns for novel applications."""
        result = text
        for symbol, entry in sorted(codex.items(), key=lambda x: len(x[0]), reverse=True):
            if isinstance(entry, SymbolCodexEntry):
                if entry.generalizable_patterns:
                    # Add pattern annotations
                    patterns_text = "; ".join(entry.generalizable_patterns[:2])
                    if patterns_text:
                        result = result.replace(
                            f"[{entry.meaning}",
                            f"[{entry.meaning} | Patterns: {patterns_text}"
                        )
            elif isinstance(entry, dict):
                patterns = entry.get('generalizable_patterns', [])
                if patterns:
                    meaning = entry.get('meaning', '')
                    patterns_text = "; ".join(patterns[:2])
                    if patterns_text:
                        result = result.replace(
                            f"[{meaning}",
                            f"[{meaning} | Patterns: {patterns_text}"
                        )
        return result
    
    def _decompress_layer_nuanced(
        self,
        text: str,
        codex: Dict[str, SymbolCodexEntry]
    ) -> str:
        """Layer 5: Full nuanced reconstruction with all details."""
        result = text
        for symbol, entry in sorted(codex.items(), key=lambda x: len(x[0]), reverse=True):
            if isinstance(entry, SymbolCodexEntry):
                # Use decompression template if available
                if entry.decompression_template and entry.decompression_template != entry.meaning:
                    # Replace with template, filling in specifics
                    template = entry.decompression_template
                    if entry.critical_specifics:
                        # Fill template placeholders with specifics
                        for i, spec in enumerate(entry.critical_specifics[:3]):
                            template = template.replace(f"{{specific_{i+1}}}", spec)
                    result = result.replace(f"[{entry.meaning}", f"[{template}")
                
                # Add original patterns if available
                if entry.original_patterns:
                    orig_text = " | Original: " + ", ".join(entry.original_patterns[:3])
                    result = result.replace(
                        f"[{entry.meaning}",
                        f"[{entry.meaning}{orig_text}"
                    )
            elif isinstance(entry, dict):
                template = entry.get('decompression_template', entry.get('meaning', ''))
                if template and template != entry.get('meaning', ''):
                    result = result.replace(
                        f"[{entry.get('meaning', '')}",
                        f"[{template}"
                    )
        return result
    
    def validate_compression(
        self,
        original: str,
        zepto_spr: str,
        decompressed: str
    ) -> Dict[str, Any]:
        """
        Validate compression integrity.
        
        Checks that essential meaning is preserved through
        compression and decompression.
        """
        # TODO: Implement semantic similarity check (LLM embedding)
        # TODO: Key concept preservation check
        # TODO: Logical structure validation
        
        compression_ratio = len(original) / len(zepto_spr) if zepto_spr else 1.0
        
        return {
            "compression_ratio": compression_ratio,
            "decompression_accuracy": 0.95,  # Placeholder - would use LLM embedding similarity
            "key_concepts_preserved": True,  # Placeholder
            "logical_structure_intact": True  # Placeholder
        }

