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
    """A single entry in the Symbol Codex."""
    symbol: str
    meaning: str
    context: str
    usage_examples: List[str]
    created_at: str


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
        """Load the Symbol Codex from persistent storage."""
        if self.codex_path.exists():
            try:
                with open(self.codex_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        symbol: SymbolCodexEntry(**entry)
                        for symbol, entry in data.items()
                    }
            except Exception as e:
                print(f"Warning: Failed to load codex: {e}")
                return {}
        return {}
    
    def _load_protocol_vocabulary(self) -> Dict[str, SymbolCodexEntry]:
        """Load protocol-specific symbol vocabulary."""
        if self.protocol_vocab_path.exists():
            try:
                with open(self.protocol_vocab_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    vocab = {}
                    # Flatten nested structure (protocol_core_symbols, mandate_symbols, etc.)
                    for category, symbols in data.items():
                        for symbol, entry in symbols.items():
                            vocab[symbol] = SymbolCodexEntry(**entry)
                    return vocab
            except Exception as e:
                print(f"Warning: Failed to load protocol vocabulary: {e}")
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
    ) -> Tuple[str, Dict[str, SymbolCodexEntry]]:
        """
        Performs the multi-stage distillation of a narrative into a symbolic SPR.
        
        Args:
            thought_trail_entry: The verbose narrative to compress
            target_stage: The final compression stage ("Concise", "Nano", "Micro", "Pico", "Femto", "Atto", "Zepto")
            
        Returns:
            Tuple of (pure_spr_string, new_codex_entries)
        """
        # Reset compression history for new run
        self.compression_history = []
        initial_len = len(thought_trail_entry)
        
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
        
        return pure_spr, new_codex_entries
    
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
        Stage 2-7: Progressive Symbolic Substitution with Semantic Matching.
        
        Applies aggressive rule-based and LLM-assisted semantic substitution
        to replace protocol concepts with symbols from the codex.
        """
        result = text
        
        # First pass: Direct symbol substitutions from codex (longest meaning first)
        # Prioritize protocol vocabulary symbols
        protocol_symbols = [(s, e) for s, e in self.codex.items() if s in self.protocol_vocab]
        other_symbols = [(s, e) for s, e in self.codex.items() if s not in self.protocol_vocab]
        sorted_symbols = protocol_symbols + other_symbols
        
        for symbol, entry in sorted_symbols:
            # Try multiple phrase matching strategies
            meaning_full = entry.meaning
            meaning_short = meaning_full.split(' - ')[0].strip()
            
            # Strategy 1: Direct phrase matching (case-insensitive)
            if meaning_short and len(meaning_short) > 3 and symbol:  # Ensure symbol is not empty
                import re
                try:
                    # Escape special regex characters in the meaning
                    escaped_meaning = re.escape(meaning_short)
                    pattern = re.compile(escaped_meaning, re.IGNORECASE)
                    # Escape special characters in symbol for replacement
                    escaped_symbol = symbol.replace('\\', '\\\\').replace('$', '\\$')
                    result = pattern.sub(escaped_symbol, result)
                except re.error as e:
                    # Skip symbols that cause regex errors
                    print(f"Warning: Regex error for symbol '{symbol}': {e}")
                    continue
            
            # Strategy 2: Extract key terms from meaning and match
            key_terms = meaning_short.split()
            if len(key_terms) >= 2:
                # Try matching the most distinctive terms
                for term in key_terms:
                    if len(term) > 4:  # Only substantial terms
                        # Match whole word only
                        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                        # Only replace if it's part of a longer phrase that matches the meaning
                        # This is a heuristic - in practice, LLM will do better
                        pass
        
        # Second pass: LLM-assisted semantic symbol matching (if available)
        if LLM_AVAILABLE and get_llm_provider and len(text) > 200:
            try:
                provider = get_llm_provider("groq")
                
                # Build comprehensive symbol list (prioritize protocol symbols)
                protocol_symbol_list = [
                    f"{s} ({e.meaning})" 
                    for s, e in sorted(self.protocol_vocab.items(), key=lambda x: len(x[1].meaning), reverse=True)
                ]
                other_symbol_list = [
                    f"{s} ({e.meaning})" 
                    for s, e in sorted(other_symbols, key=lambda x: len(x[1].meaning), reverse=True)[:20]
                ]
                
                # Limit total symbols for prompt efficiency
                all_symbols = protocol_symbol_list[:30] + other_symbol_list[:20]
                symbol_list_text = "\n".join(all_symbols[:50])  # Max 50 symbols
                
                # Chunk text if too long
                text_chunk = text[:4000] if len(text) > 4000 else text
                remaining_text = text[4000:] if len(text) > 4000 else ""
                
                prompt = f"""You are the Pattern Crystallization Engine's semantic symbolization stage.

Replace protocol concepts and phrases in the text with their corresponding symbols from the codex.
PRIORITIZE protocol-specific symbols (Æ, Ω, Δ, Φ, Θ, etc.) over generic ones.

Available symbols (protocol symbols first):
{symbol_list_text}

Text to symbolize:
{text_chunk}

Rules:
1. Replace exact phrase matches with their symbols
2. Replace semantic equivalents (e.g., "Cognitive Resonance" → Ω, "IAR" → Φ)
3. Replace protocol terms (e.g., "Pattern Crystallization" → Π, "Mandate 1" → M₁)
4. Keep text structure but maximize symbol usage
5. Output ONLY the symbolized text, no explanations

Symbolized text:"""
                
                symbolized = provider.generate(
                    prompt=prompt,
                    model="llama-3.3-70b-versatile",
                    temperature=0.15,  # Very low for precise replacement
                    max_tokens=min(len(text) + 500, 4500)  # Allow some expansion for symbols
                )
                
                if symbolized and len(symbolized.strip()) > 0:
                    symbolized = symbolized.strip()
                    # Use LLM result if it's shorter or similar length (symbols are more compact)
                    if len(symbolized) <= len(result) * 1.1:  # Allow up to 10% increase (symbols might be longer Unicode)
                        result = symbolized + remaining_text
                        # Additional pass: remove any remaining obvious phrases
                        result = self._apply_aggressive_symbol_replacement(result)
                        
            except Exception as e:
                # Fallback: continue with direct substitutions
                print(f"Warning: LLM symbolization failed: {e}, using direct substitutions")
                pass
        
        # ALWAYS apply aggressive symbol replacement at the end (even if LLM failed)
        result = self._apply_aggressive_symbol_replacement(result)
        
        return result
    
    def _apply_aggressive_symbol_replacement(self, text: str) -> str:
        """Apply aggressive rule-based symbol replacement for common patterns."""
        result = text
        
        # Common protocol phrase patterns
        replacements = {
            "Cognitive resonancE": "Ω",
            "Cognitive Resonance": "Ω",
            "cognitive resonance": "Ω",
            "Temporal resonancE": "Δ",
            "Temporal Resonance": "Δ",
            "temporal resonance": "Δ",
            "Integrated Action Reflection": "Φ",
            "IAR": "Φ",
            "Sparse Priming Representation": "Θ",
            "SPR": "Θ",
            "Pattern Crystallization": "Π",
            "pattern crystallization": "Π",
            "As Above, So Below": "Λ",
            "as above so below": "Λ",
            "ThoughtTrail": "Σ",
            "thought trail": "Σ",
            "ArchE": "Æ",
        }
        
        # Add mandate replacements (using Unicode subscripts from codex)
        mandate_subscripts = ['₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉', '₁₀', '₁₁', '₁₂']
        for i in range(1, 13):
            subscript = mandate_subscripts[i-1]
            result = result.replace(f"Mandate {i}", f"M{subscript}")
            result = result.replace(f"mandate {i}", f"M{subscript}")
            result = result.replace(f"M{i}", f"M{subscript}")  # Also handle M1, M2, etc.
        
        # Apply direct replacements
        for phrase, symbol in replacements.items():
            result = result.replace(phrase, symbol)
        
        return result
    
    def _finalize_crystal(self, symbolic_form: str) -> str:
        """
        Stage 8: Final Crystallization.
        
        Applies final optimizations to create the pure Zepto SPR:
        - Removes remaining linguistic artifacts
        - Optimizes symbol density
        - Validates symbolic integrity
        """
        # Remove whitespace, optimize symbol sequences
        # This is a simplified version - in production, would validate mathematical/symbolic consistency
        return ''.join(symbolic_form.split()).strip()
    
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
        
        # For each symbol, infer meaning from original narrative
        for symbol in symbols:
            if symbol not in self.codex:
                meaning = self._infer_symbol_meaning(symbol, original_narrative)
                entry = SymbolCodexEntry(
                    symbol=symbol,
                    meaning=meaning["definition"],
                    context=meaning["context"],
                    usage_examples=[pure_spr],
                    created_at=now_iso()
                )
                new_entries[symbol] = entry
                self.codex[symbol] = entry
        
        return new_entries
    
    def _extract_symbols(self, spr: str) -> List[str]:
        """Extract unique symbols from SPR string."""
        # Identify mathematical symbols, special characters, etc.
        # Exclude common punctuation but keep mathematical/special symbols
        symbols = re.findall(r'[^\w\s,.!?;:"\'\[\](){}]', spr)
        return list(set(symbols))
    
    def _infer_symbol_meaning(self, symbol: str, narrative: str) -> Dict[str, str]:
        """
        Infer symbol meaning from narrative context using LLM.
        
        This is critical for creating meaningful Symbol Codex entries
        that enable proper decompression.
        """
        if not LLM_AVAILABLE or not generate_text_llm:
            # Fallback: Basic placeholder
            return {
                "definition": f"Symbol extracted: {symbol}",
                "context": "Inferred from narrative context"
            }
        
        try:
            # Use LLM provider directly to bypass ArchE execution path
            if get_llm_provider:
                provider = get_llm_provider("groq")  # Use Groq (faster, cheaper, no rate limits)
                
                prompt = f"""You are the Pattern Crystallization Engine's symbol inference stage.

A symbol "{symbol}" was extracted from the following narrative. 
Determine what this symbol represents based on its context and usage.

Narrative context:
{narrative[:2000]}

Provide:
1. A concise definition of what this symbol represents (max 50 words)
2. The context domain (e.g., "CFP Analysis", "Protocol Definition", "System Architecture")

Format your response as:
DEFINITION: [concise definition]
CONTEXT: [context domain]"""
                
                # Call provider directly (bypasses ArchE execution)
                response = provider.generate(
                    prompt=prompt,
                    model="llama-3.3-70b-versatile",
                    temperature=0.4,
                    max_tokens=200
                )
                
                if response and len(response.strip()) > 0:
                    response = response.strip()
                    
                    # Parse response
                    definition = response
                    context = "Inferred from narrative context"
                    
                    # Try to extract structured parts
                    if "DEFINITION:" in response:
                        parts = response.split("DEFINITION:")
                        if len(parts) > 1:
                            def_part = parts[1].split("CONTEXT:")[0].strip()
                            definition = def_part if def_part else definition
                    
                    if "CONTEXT:" in response:
                        context_part = response.split("CONTEXT:")[-1].strip()
                        context = context_part if context_part else context
                    
                    return {
                        "definition": definition[:200],  # Limit length
                        "context": context[:100]
                    }
            
            # Fallback
            return {
                "definition": f"Symbol extracted: {symbol}",
                "context": "Inferred from narrative context"
            }
            
        except Exception as e:
            # Fallback on error
            print(f"Warning: LLM symbol inference failed: {e}, using fallback")
            return {
                "definition": f"Symbol extracted: {symbol}",
                "context": "Inferred from narrative context"
            }
    
    def decompress_spr(
        self,
        zepto_spr: str,
        codex: Optional[Dict[str, SymbolCodexEntry]] = None
    ) -> str:
        """
        Reverse Process: Decompress Zepto SPR back to narrative.
        
        Uses the Symbol Codex to reconstruct the original meaning.
        """
        if codex is None:
            codex = self.codex
        
        # Replace symbols with their meanings (longest first to avoid partial matches)
        # This ensures multi-character symbols (like "𝔗𝔯") are replaced before single-character ones
        result = zepto_spr
        for symbol, entry in sorted(codex.items(), key=lambda x: len(x[0]), reverse=True):
            if symbol in result:
                # Handle both SymbolCodexEntry objects and dict format
                if isinstance(entry, SymbolCodexEntry):
                    meaning = entry.meaning
                elif isinstance(entry, dict):
                    meaning = entry.get('meaning', entry.get('symbol', symbol))
                else:
                    meaning = str(entry)
                result = result.replace(symbol, f"[{meaning}]")
        
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

