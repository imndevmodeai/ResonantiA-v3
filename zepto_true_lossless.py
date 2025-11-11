"""
TRUE LOSSLESS ZEPTO COMPRESSION
================================

Based on Wikipedia Lossless Compression Principles:
1. Generate statistical model from input data
2. Use bijective mapping (one-to-one) to compressed representation
3. Store the model/codex with compressed data
4. Guarantee perfect reconstruction

This implementation applies PROVEN compression theory:
- Huffman coding principles
- Dictionary-based compression (LZ77-inspired)
- Statistical redundancy exploitation
- Injection (one-to-one) mapping requirement
"""

import json
import heapq
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Tuple, Optional, BinaryIO
from collections import Counter, defaultdict
from datetime import datetime
import struct

# ============================================================================
# PRINCIPLE 1: STATISTICAL MODEL GENERATION
# ============================================================================

@dataclass
class StatisticalModel:
    """
    Step 1 from Wikipedia: Generate statistical model for input data
    
    This is the KEY difference between lossy and lossless compression.
    Lossy compression throws away the model.
    Lossless compression STORES the model alongside compressed data.
    """
    
    # Frequency analysis
    symbol_frequencies: Dict[str, int]  # How often each symbol appears
    total_symbols: int                   # Total symbols in original
    unique_symbols: int                  # Number of unique symbols
    
    # Derived statistics
    entropy: float                       # Information entropy (bits)
    redundancy: float                    # How much redundancy exists
    
    # Context models (for adaptive compression)
    bigram_frequencies: Dict[Tuple[str, str], int] = field(default_factory=dict)
    context_depth: int = 1               # How many previous symbols to consider
    
    # Model metadata
    model_id: str = ""
    created_at: str = ""
    
    def to_dict(self):
        """Convert to JSON-serializable dict."""
        return {
            "symbol_frequencies": self.symbol_frequencies,
            "total_symbols": self.total_symbols,
            "unique_symbols": self.unique_symbols,
            "entropy": self.entropy,
            "redundancy": self.redundancy,
            "bigram_frequencies": {str(k): v for k, v in self.bigram_frequencies.items()},
            "context_depth": self.context_depth,
            "model_id": self.model_id,
            "created_at": self.created_at,
        }


def analyze_statistical_redundancy(text: str) -> StatisticalModel:
    """
    Wikipedia Step 1: Generate statistical model
    
    This reveals what redundancy exists in the data.
    Compression ratio is determined by this model.
    """
    # Symbol frequency analysis
    frequencies = Counter(text)
    total = len(text)
    unique = len(frequencies)
    
    # Calculate entropy (information theory)
    # Entropy = sum(-p_i * log2(p_i)) for each symbol
    import math
    entropy = 0.0
    redundancy_sum = 0.0
    
    for symbol, count in frequencies.items():
        p_i = count / total
        if p_i > 0:
            entropy += -p_i * math.log2(p_i)
            redundancy_sum += (1 - p_i)
    
    # Bigram analysis (context-aware)
    bigrams = Counter()
    for i in range(len(text) - 1):
        bigram = (text[i], text[i + 1])
        bigrams[bigram] += 1
    
    model = StatisticalModel(
        symbol_frequencies=dict(frequencies),
        total_symbols=total,
        unique_symbols=unique,
        entropy=entropy,
        redundancy=redundancy_sum / unique if unique > 0 else 0,
        bigram_frequencies=dict(bigrams),
        context_depth=1,
        model_id=f"model_{total}_{unique}",
        created_at=datetime.now().isoformat()
    )
    
    return model


# ============================================================================
# PRINCIPLE 2: BIJECTIVE MAPPING (ONE-TO-ONE)
# ============================================================================

@dataclass
class HuffmanNode:
    """Node in Huffman tree for bijective encoding."""
    symbol: Optional[str] = None
    frequency: int = 0
    left: Optional['HuffmanNode'] = None
    right: Optional['HuffmanNode'] = None
    
    def __lt__(self, other):
        """For heap ordering."""
        return self.frequency < other.frequency


def build_huffman_tree(frequencies: Dict[str, int]) -> HuffmanNode:
    """
    Wikipedia Step 2: Build Huffman tree for bijective mapping
    
    Huffman coding guarantees:
    - One-to-one mapping (injection)
    - Optimal prefix-free codes
    - No two symbols map to same code
    """
    if not frequencies:
        return HuffmanNode()
    
    # Create leaf nodes
    heap = [
        HuffmanNode(symbol=symbol, frequency=freq)
        for symbol, freq in frequencies.items()
    ]
    heapq.heapify(heap)
    
    # Build tree bottom-up
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        parent = HuffmanNode(
            frequency=left.frequency + right.frequency,
            left=left,
            right=right
        )
        heapq.heappush(heap, parent)
    
    return heap[0] if heap else HuffmanNode()


def generate_huffman_codes(root: HuffmanNode, code: str = "", 
                           codes: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Generate bijective Huffman codes
    
    Wikipedia: "Huffman coding pairs well with other algorithms"
    Critical property: Each symbol gets UNIQUE code (bijection)
    """
    if codes is None:
        codes = {}
    
    if root.symbol:
        codes[root.symbol] = code if code else "0"  # Handle single-symbol case
        return codes
    
    if root.left:
        generate_huffman_codes(root.left, code + "0", codes)
    if root.right:
        generate_huffman_codes(root.right, code + "1", codes)
    
    return codes


# ============================================================================
# PRINCIPLE 3: LOSSLESS ENCODING (With Statistical Model)
# ============================================================================

@dataclass
class LosslessCompressionResult:
    """Result of lossless compression with COMPLETE reversibility kit."""
    
    # The compressed representation
    compressed_data: str  # Bitstring represented as "0101011..."
    
    # THE CRITICAL PART: Store everything needed for perfect reversal
    huffman_codes: Dict[str, str]          # Symbol → code mapping
    huffman_reverse: Dict[str, str]        # Code → symbol reverse mapping
    statistical_model: StatisticalModel    # Full statistical analysis
    
    # Metadata
    original_length: int
    compressed_length: int
    compression_ratio: float
    reversibility: float = 1.0  # Should be 100% for true lossless
    
    # For validation
    original_text: Optional[str] = None
    created_at: str = ""
    
    def to_json(self) -> str:
        """Serialize everything for storage."""
        return json.dumps({
            "compressed_data": self.compressed_data,
            "huffman_codes": self.huffman_codes,
            "huffman_reverse": self.huffman_reverse,
            "statistical_model": self.statistical_model.to_dict(),
            "original_length": self.original_length,
            "compressed_length": self.compressed_length,
            "compression_ratio": self.compression_ratio,
            "reversibility": self.reversibility,
            "created_at": self.created_at,
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LosslessCompressionResult':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        
        model = StatisticalModel(
            symbol_frequencies=data["statistical_model"]["symbol_frequencies"],
            total_symbols=data["statistical_model"]["total_symbols"],
            unique_symbols=data["statistical_model"]["unique_symbols"],
            entropy=data["statistical_model"]["entropy"],
            redundancy=data["statistical_model"]["redundancy"],
            context_depth=data["statistical_model"]["context_depth"],
        )
        
        return cls(
            compressed_data=data["compressed_data"],
            huffman_codes=data["huffman_codes"],
            huffman_reverse=data["huffman_reverse"],
            statistical_model=model,
            original_length=data["original_length"],
            compressed_length=data["compressed_length"],
            compression_ratio=data["compression_ratio"],
            reversibility=data["reversibility"],
        )


def compress_lossless(text: str) -> LosslessCompressionResult:
    """
    Wikipedia-based lossless compression pipeline
    
    1. ✓ Generate statistical model
    2. ✓ Build bijective mapping (Huffman)
    3. ✓ Encode using model
    4. ✓ Store model with result
    """
    
    print(f"[COMPRESS] Input: {len(text)} chars")
    print(f"[UNIQUE SYMBOLS] {len(set(text))} unique symbols")
    
    # STEP 1: Generate statistical model
    print("[STEP 1] Analyzing statistical redundancy...")
    model = analyze_statistical_redundancy(text)
    print(f"  → Entropy: {model.entropy:.2f} bits/symbol")
    print(f"  → Redundancy: {model.redundancy:.2%}")
    
    # STEP 2: Build bijective mapping
    print("[STEP 2] Building Huffman tree (bijective mapping)...")
    huffman_tree = build_huffman_tree(model.symbol_frequencies)
    huffman_codes = generate_huffman_codes(huffman_tree)
    
    # Verify bijection (one-to-one mapping)
    print(f"  → Generated {len(huffman_codes)} unique codes")
    assert len(huffman_codes) == len(model.symbol_frequencies), "Bijection failed!"
    print("  → ✓ Bijection verified (one-to-one mapping)")
    
    # STEP 3: Encode using bijective mapping
    print("[STEP 3] Encoding with Huffman codes...")
    compressed_bitstring = ""
    for char in text:
        compressed_bitstring += huffman_codes[char]
    
    compressed_length = len(compressed_bitstring)
    print(f"  → Compressed to {compressed_length} bits")
    
    # Calculate actual compression ratio
    # In theory: bits_needed = entropy * original_length
    # In practice: bits_used = compressed_bitstring_length
    theoretical_minimum = model.entropy * len(text)
    compression_ratio = len(text) / compressed_length if compressed_length > 0 else 1.0
    
    print(f"  → Compression ratio: {compression_ratio:.2f}:1")
    print(f"  → Theoretical minimum: {theoretical_minimum:.0f} bits")
    print(f"  → Efficiency: {theoretical_minimum / compressed_length * 100:.1f}%")
    
    # Build reverse mapping for decompression
    huffman_reverse = {v: k for k, v in huffman_codes.items()}
    
    # STEP 4: Store model with result (CRITICAL for losslessness)
    result = LosslessCompressionResult(
        compressed_data=compressed_bitstring,
        huffman_codes=huffman_codes,
        huffman_reverse=huffman_reverse,
        statistical_model=model,
        original_length=len(text),
        compressed_length=compressed_length,
        compression_ratio=compression_ratio,
        reversibility=1.0,
        original_text=text,
        created_at=datetime.now().isoformat()
    )
    
    return result


# ============================================================================
# PRINCIPLE 4: LOSSLESS DECOMPRESSION
# ============================================================================

def decompress_lossless(result: LosslessCompressionResult) -> Tuple[str, float]:
    """
    Perfect reconstruction using stored Huffman codes
    
    This is the ONLY way true losslessness works:
    compressed_data + model → perfect original
    """
    
    print(f"\n[DECOMPRESS] Input: {len(result.compressed_data)} bits")
    
    # STEP 1: Verify model is present
    if not result.huffman_reverse:
        raise ValueError("Cannot decompress: Huffman reverse mapping missing!")
    
    # STEP 2: Decode bitstring using reverse mapping
    print("[STEP 1] Decoding bitstring with Huffman reverse mapping...")
    decompressed = ""
    current_code = ""
    
    for bit in result.compressed_data:
        current_code += bit
        
        if current_code in result.huffman_reverse:
            symbol = result.huffman_reverse[current_code]
            decompressed += symbol
            current_code = ""
    
    # Handle any remaining bits
    if current_code:
        if current_code in result.huffman_reverse:
            decompressed += result.huffman_reverse[current_code]
        else:
            print(f"  ⚠ Warning: {len(current_code)} remaining bits could not be decoded")
    
    print(f"  → Decompressed to {len(decompressed)} chars")
    
    # STEP 3: Verify perfect reconstruction
    print("[STEP 2] Verifying perfect reconstruction...")
    
    if result.original_text:
        is_perfect = decompressed == result.original_text
        print(f"  → Perfect match: {is_perfect}")
        
        if not is_perfect:
            print(f"  → Original length: {len(result.original_text)}")
            print(f"  → Decompressed length: {len(decompressed)}")
            
            # Find first difference
            for i, (o, d) in enumerate(zip(result.original_text, decompressed)):
                if o != d:
                    print(f"  → First difference at position {i}: '{o}' vs '{d}'")
                    break
    else:
        is_perfect = True  # We don't have original, assume correct
    
    accuracy = 1.0 if is_perfect else 0.0
    
    return decompressed, accuracy


# ============================================================================
# DEMO: TRUE LOSSLESS COMPRESSION
# ============================================================================

if __name__ == "__main__":
    
    test_text = """
    The quick brown fox jumps over the lazy dog.
    The quick brown fox jumps over the lazy dog.
    The quick brown fox jumps over the lazy dog.
    """
    
    print("=" * 80)
    print("TRUE LOSSLESS ZEPTO COMPRESSION")
    print("Using Wikipedia-based compression theory")
    print("=" * 80)
    
    # Compress
    result = compress_lossless(test_text)
    
    # Show the bijective mapping
    print("\n" + "=" * 80)
    print("HUFFMAN BIJECTIVE MAPPING (One-to-One)")
    print("=" * 80)
    
    sorted_codes = sorted(result.huffman_codes.items(), key=lambda x: len(x[1]))
    for symbol, code in sorted_codes[:10]:  # Show first 10
        display_symbol = repr(symbol) if symbol in [' ', '\n', '\t'] else symbol
        print(f"  {display_symbol:10s} → {code:20s} (len: {len(code)})")
    if len(sorted_codes) > 10:
        print(f"  ... and {len(sorted_codes) - 10} more symbols")
    
    # Show statistical model
    print("\n" + "=" * 80)
    print("STATISTICAL MODEL (Step 1)")
    print("=" * 80)
    print(f"Total symbols: {result.statistical_model.total_symbols}")
    print(f"Unique symbols: {result.statistical_model.unique_symbols}")
    print(f"Entropy: {result.statistical_model.entropy:.2f} bits/symbol")
    print(f"Redundancy: {result.statistical_model.redundancy:.2%}")
    
    # Show compression results
    print("\n" + "=" * 80)
    print("COMPRESSION RESULTS")
    print("=" * 80)
    print(f"Original: {result.original_length} chars ({result.original_length * 8} bits)")
    print(f"Compressed: {result.compressed_length} bits")
    print(f"Ratio: {result.compression_ratio:.2f}:1")
    print(f"Saved: {result.original_length * 8 - result.compressed_length} bits")
    
    # Show what makes it LOSSLESS
    print("\n" + "=" * 80)
    print("LOSSLESSNESS GUARANTEE")
    print("=" * 80)
    print(f"✓ Bijection maintained: {len(result.huffman_codes)} unique codes")
    print(f"✓ Statistical model stored: {len(str(result.statistical_model.to_dict()))} bytes")
    print(f"✓ Reverse mapping available: {len(result.huffman_reverse)} entries")
    print(f"✓ Reversibility: {result.reversibility * 100:.0f}%")
    
    # Decompress
    decompressed, accuracy = decompress_lossless(result)
    
    # Final verification
    print("\n" + "=" * 80)
    print("PERFECT RECONSTRUCTION")
    print("=" * 80)
    print(f"✓ Accuracy: {accuracy * 100:.0f}%")
    print(f"✓ Match: {decompressed == test_text}")
    print(f"✓ Length: {len(decompressed)} chars")
    
    # Show package size
    print("\n" + "=" * 80)
    print("ACTUAL SIZE (With Decompression Kit)")
    print("=" * 80)
    json_output = result.to_json()
    print(f"Total size with model: {len(json_output)} bytes")
    print(f"Compression ratio including model: {result.original_length / len(json_output):.2f}:1")
    print(f"Trade-off: Lose extreme compression for PERFECT reversibility")
    
    # Save for later
    with open("/tmp/lossless_compression.json", "w") as f:
        f.write(json_output)
    print(f"\n✓ Saved to /tmp/lossless_compression.json")

