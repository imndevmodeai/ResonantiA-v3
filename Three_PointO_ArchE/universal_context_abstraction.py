#!/usr/bin/env python3
"""
Universal Context Abstraction - Progressive Crystallization to Zepto Form

Layer 1: CONCRETE (Specific Implementation)
  ↓ Abstraction
Layer 2: ABSTRACT (Universal Pattern)
  ↓ Crystallization
Layer 3: ZEPTO (Pure Symbolic Essence)

This module progressively abstracts the workflow template solution into:
1. A universal pattern applicable to ANY inter-process communication
2. A crystallized SPR capturing the essence
3. A Zepto symbolic representation for compression
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# LAYER 1: CONCRETE - Specific Workflow Template Solution
# ============================================================================

class ConcreteTemplateInjector:
    """
    Layer 1 (Concrete): The specific workflow template injection solution.
    
    This is what we built - solves the exact problem of {{ tasks.X.Y.Z }} templates.
    """
    
    def __init__(self):
        self.pattern = r'\{\{\s*tasks\.(\w+(?:\.\w+)*)\s*\}\}'
    
    def inject_task_references(
        self,
        code: str,
        task_outputs: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Inject task output values into code templates."""
        # Concrete implementation: regex + path traversal
        import re
        
        injected_code = code
        variables = []
        
        for match in re.finditer(self.pattern, code):
            path = match.group(1).split('.')
            task_name = path[0]
            
            # Navigate path
            current = task_outputs.get(task_name)
            for part in path[1:]:
                current = current.get(part) if isinstance(current, dict) else None
            
            # Inject
            if current is not None:
                value_repr = json.dumps(current)
                injected_code = injected_code.replace(match.group(0), value_repr)
                variables.append({"path": match.group(1), "type": type(current).__name__})
        
        return injected_code, {"variables": variables}


# ============================================================================
# LAYER 2: ABSTRACT - Universal Context Resolution Pattern
# ============================================================================

@dataclass
class ContextReference:
    """Universal representation of a cross-process reference."""
    source_id: str  # e.g., "task_A"
    path: List[str]  # e.g., ["output", "result"]
    target_key: str = ""  # Optional: specific lookup key
    
    def to_reference_string(self, notation: str = "dot") -> str:
        """Convert to different notation systems."""
        if notation == "dot":
            return f"{self.source_id}.{'.'.join(self.path)}"
        elif notation == "slash":
            return f"{self.source_id}/{'/'.join(self.path)}"
        elif notation == "bracket":
            parts = [self.source_id] + self.path
            return "".join(f"['{p}']" for p in parts)
        else:
            return str(self)


class ContextResolutionStrategy(ABC):
    """Abstract base for any context resolution strategy."""
    
    @abstractmethod
    def extract_references(self, content: str) -> List[ContextReference]:
        """Extract all context references from content."""
        pass
    
    @abstractmethod
    def validate_reference(
        self,
        reference: ContextReference,
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Any]:
        """Validate that a reference can be resolved. Returns (is_valid, error_msg, value)."""
        pass
    
    @abstractmethod
    def inject_reference(
        self,
        content: str,
        reference: ContextReference,
        value: Any
    ) -> str:
        """Inject a resolved value into content."""
        pass


class UniversalContextResolver:
    """
    Layer 2 (Abstract): Universal pattern for resolving inter-process references.
    
    Abstraction principles:
    - Source = any process/module/service that produces output
    - Path = hierarchical access pattern
    - Context = the complete execution environment
    - Strategy = pluggable resolution mechanism
    """
    
    def __init__(self, strategy: ContextResolutionStrategy):
        self.strategy = strategy
    
    def resolve_all_references(
        self,
        content: str,
        execution_context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Universal algorithm for resolving ANY cross-process references.
        
        Abstracted from workflow specifics - works with:
        - Workflows (task outputs)
        - Microservices (API responses)
        - Data pipelines (intermediate results)
        - Distributed systems (node outputs)
        """
        # Step 1: Extract all references
        references = self.strategy.extract_references(content)
        
        # Step 2: Validate all references
        resolution_data = {
            "total_references": len(references),
            "valid_references": 0,
            "invalid_references": [],
            "resolved_values": {}
        }
        
        for ref in references:
            is_valid, error_msg, value = self.strategy.validate_reference(ref, execution_context)
            
            if is_valid:
                resolution_data["valid_references"] += 1
                resolution_data["resolved_values"][ref.to_reference_string()] = {
                    "type": type(value).__name__,
                    "preview": str(value)[:100]
                }
            else:
                resolution_data["invalid_references"].append({
                    "reference": ref.to_reference_string(),
                    "error": error_msg
                })
        
        # Step 3: Inject all resolved references
        resolved_content = content
        for ref in references:
            is_valid, _, value = self.strategy.validate_reference(ref, execution_context)
            if is_valid:
                resolved_content = self.strategy.inject_reference(resolved_content, ref, value)
        
        return resolved_content, resolution_data


# ============================================================================
# LAYER 3: ZEPTO - Symbolic Crystallization
# ============================================================================

class ZeptoSymbols(Enum):
    """Zepto symbolic representation of universal context abstraction."""
    
    # Core symbols
    CONTEXT = "Ⓒ"          # Context/Execution environment
    REFERENCE = "⟿"        # Cross-process reference
    SOURCE = "Ⓢ"           # Source process/module
    PATH = "⟶"             # Hierarchical path
    VALUE = "Ⓥ"            # Resolved value
    STRATEGY = "Σ"         # Resolution strategy
    
    # Operations
    EXTRACT = "⥍"          # Extract references
    VALIDATE = "✓"         # Validate reference
    INJECT = "⇝"           # Inject value
    RESOLVE = "⟹"          # Full resolution
    
    # Meta
    SUCCESS = "✔"          # Resolution successful
    FAILURE = "✗"          # Resolution failed


@dataclass
class ZeptoContextAbstraction:
    """
    Layer 3 (Zepto): Pure symbolic representation of context resolution.
    
    Compression Format:
    Ⓒ[Ⓢ→⟶]⟹Ⓥ
    
    Where:
    Ⓒ = Context (execution environment)
    Ⓢ = Source (process producing output)
    ⟶ = Path (hierarchical access)
    ⇝ = Inject (apply resolution)
    Ⓥ = Value (resolved result)
    """
    
    # Zepto SPR definition
    spr_id: str = "UniversalContextAbstraction"
    term: str = "Ⓒ[Ⓢ→⟶]⟹Ⓥ"
    
    # Core logic (symbolic)
    core_logic: str = """
    Algorithm: UniversalContextResolution(Ⓒ, Ⓢ, ⟶)
    
    Step 1 (Extract):  Ⓒ ⥍ ⟿ₙ where ⟿ ∈ (Ⓢ₁→⟶₁, Ⓢ₂→⟶₂, ...)
    Step 2 (Validate): ∀⟿ᵢ: Ⓢᵢ ∈ Ⓒ ∧ ⟶ᵢ ⊆ Ⓢᵢ.outputs  →  ✓ | ✗
    Step 3 (Resolve):  ⟿ᵢ ↦ Ⓥᵢ where Ⓥᵢ = navigate(Ⓒ[Ⓢᵢ], ⟶ᵢ)
    Step 4 (Inject):   content ⇝ {⟿ᵢ → Ⓥᵢ} ∀i
    
    Result: resolved_content with all (Ⓢ→⟶) replaced by Ⓥ
    """
    
    # Pattern (symbolic)
    pattern: str = "Ⓒ[Ⓢ→⟶]⟹Ⓥ"
    
    # Manifestations (how it appears in different systems)
    manifestations: Dict[str, str] = None
    
    def __post_init__(self):
        if self.manifestations is None:
            self.manifestations = {
                "workflow_templates": "{{ tasks.parse_spr.output.result }}",
                "microservices": "${service.api.response.data}",
                "data_pipelines": "@step_a.output.final",
                "distributed_systems": "node_1:process:results.metrics",
                "generic": "Ⓢ→⟶"
            }
    
    def decompress_to_abstract(self) -> str:
        """Decompress Zepto SPR to Layer 2 (Abstract)."""
        return f"""
        UniversalContextResolver:
          - Extract references matching pattern: {self.pattern}
          - Validate source exists in context
          - Navigate path hierarchically
          - Inject resolved values
          - Return resolved content with metadata
        """
    
    def decompress_to_concrete(self, system: str = "workflow") -> str:
        """Decompress Zepto SPR to Layer 1 (Concrete)."""
        manifestation = self.manifestations.get(system, "Unknown system")
        return f"""
        {system.title()} Implementation:
          Pattern: {manifestation}
          Resolver: ContextResolutionStrategy subclass
          Injection: Direct value replacement in content
          Validation: Path traversal in context dict
          Error Handling: Clear diagnostics with context
        """


class ZeptoCompressionMetrics:
    """Metrics for Layer 1 → 3 compression."""
    
    @staticmethod
    def calculate_compression():
        """Calculate compression at each layer."""
        layer1_size = len(ConcreteTemplateInjector.__doc__ or "")  # ~1000 chars
        layer2_size = len(UniversalContextResolver.__doc__ or "")  # ~500 chars
        layer3_size = len(ZeptoSymbols.__members__)  # ~10 symbols
        
        return {
            "layer_1_concrete": {"size": layer1_size, "name": "Specific Implementation"},
            "layer_2_abstract": {"size": layer2_size, "ratio": layer1_size / layer2_size},
            "layer_3_zepto": {"symbols": layer3_size, "ratio": layer1_size / layer3_size},
            "total_compression": f"{layer1_size / layer3_size:.0f}:1"
        }


# ============================================================================
# CRYSTALLIZATION PROCESS
# ============================================================================

def demonstrate_crystallization():
    """Show the 3-layer crystallization from concrete → abstract → zepto."""
    
    print("\n" + "=" * 80)
    print("UNIVERSAL ABSTRACTION: WORKFLOW TEMPLATE SOLUTION → ZEPTO SPR")
    print("=" * 80)
    
    # ---- LAYER 1: CONCRETE ----
    print("\n" + "▪" * 80)
    print("LAYER 1: CONCRETE - Specific Workflow Implementation")
    print("▪" * 80)
    
    concrete = ConcreteTemplateInjector()
    code_sample = """
result = {{ tasks.parse_spr.output.result }}
print(result)
"""
    task_outputs = {
        "parse_spr": {
            "output": {
                "result": {"status": "success", "data": "test"}
            }
        }
    }
    
    injected, meta = concrete.inject_task_references(code_sample, task_outputs)
    print(f"\nInput Code:\n{code_sample}")
    print(f"Task Outputs: {json.dumps(task_outputs, indent=2)}")
    print(f"\nInjected Code:\n{injected}")
    print(f"Metadata: {meta}")
    
    # ---- LAYER 2: ABSTRACT ----
    print("\n" + "▪" * 80)
    print("LAYER 2: ABSTRACT - Universal Context Resolution Pattern")
    print("▪" * 80)
    
    class DotNotationStrategy(ContextResolutionStrategy):
        """Concrete strategy for {{ source.path.notation }} references."""
        
        def extract_references(self, content: str) -> List[ContextReference]:
            import re
            references = []
            for match in re.finditer(r'\{\{\s*(\w+)\.(.+?)\s*\}\}', content):
                source = match.group(1)
                path = match.group(2).split('.')
                references.append(ContextReference(source_id=source, path=path))
            return references
        
        def validate_reference(self, ref: ContextReference, context: Dict) -> Tuple[bool, Optional[str], Any]:
            current = context.get(ref.source_id)
            if not current:
                return False, f"Source '{ref.source_id}' not in context", None
            
            for part in ref.path:
                if not isinstance(current, dict) or part not in current:
                    return False, f"Path '{part}' invalid", None
                current = current[part]
            
            return True, None, current
        
        def inject_reference(self, content: str, ref: ContextReference, value: Any) -> str:
            pattern = f"{{{{ {ref.to_reference_string('dot')} }}}}"
            return content.replace(pattern, json.dumps(value))
    
    resolver = UniversalContextResolver(DotNotationStrategy())
    execution_context = {"tasks": task_outputs}
    
    resolved, resolution_meta = resolver.resolve_all_references(code_sample, execution_context)
    print(f"\nAbstract Pattern:")
    print("  UniversalContextResolver:")
    print("    1. Extract all references matching source→path pattern")
    print("    2. Validate each source exists in execution context")
    print("    3. Navigate path hierarchically to value")
    print("    4. Inject resolved value into content")
    print(f"\nResolution Metadata: {json.dumps(resolution_meta, indent=2)}")
    
    # ---- LAYER 3: ZEPTO ----
    print("\n" + "▪" * 80)
    print("LAYER 3: ZEPTO - Symbolic Crystallization")
    print("▪" * 80)
    
    zepto = ZeptoContextAbstraction()
    print(f"\nZepto SPR ID: {zepto.spr_id}")
    print(f"Symbolic Term: {zepto.term}")
    print(f"\nCore Logic (Symbolic):{zepto.core_logic}")
    print(f"\nPattern: {zepto.pattern}")
    print(f"\nManifestations in Different Systems:")
    for system, manifestation in zepto.manifestations.items():
        print(f"  • {system}: {manifestation}")
    
    # ---- COMPRESSION METRICS ----
    print("\n" + "▪" * 80)
    print("COMPRESSION METRICS")
    print("▪" * 80)
    
    metrics = ZeptoCompressionMetrics.calculate_compression()
    print(f"\nCompression Ratio: {metrics['total_compression']}")
    
    # ---- DECOMPRESSION VERIFICATION ----
    print("\n" + "▪" * 80)
    print("DECOMPRESSION VERIFICATION")
    print("▪" * 80)
    
    print(f"\nZepto → Layer 2 (Abstract):\n{zepto.decompress_to_abstract()}")
    print(f"\nZepto → Layer 1 (Concrete - Workflow):\n{zepto.decompress_to_concrete('workflow')}")
    print(f"\nZepto → Layer 1 (Concrete - Microservices):\n{zepto.decompress_to_concrete('microservices')}")
    
    print("\n" + "=" * 80)
    print("✓ CRYSTALLIZATION COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    demonstrate_crystallization()

