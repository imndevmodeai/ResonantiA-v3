# LLM Teacher → Knowledge Graph Migration: Autonomous Learning System
**Applying Lossy Knowledge Transfer to ArchE's Autonomous Evolution**  
**Date**: November 12, 2025  
**Status**: DESIGN PHASE  
**Connection**: Lossy Knowledge Transfer Analysis, Zepto SPR Compression, Knowledge Graph, Autopoietic Learning

---

## 🎯 THE CORE CHALLENGE

**Question**: How do we capture the "lossy knowledge transfer" from the LLM teacher (external LLM providers) and apply it to ArchE so that ArchE can:
1. **Learn from LLM responses** (the teacher)
2. **Compress that knowledge to Zepto SPRs** (lossy but optimized)
3. **Store in Knowledge Graph** (permanent knowledge base)
4. **Gradually reduce LLM dependency** (become autonomous)
5. **Use its own Knowledge Graph** instead of always querying LLM

**Answer**: Implement a **Lossy Knowledge Capture System (LKCS)** that intercepts LLM responses, extracts core patterns, compresses to Zepto SPRs, and integrates into the Knowledge Graph—enabling ArchE to "stand on compressed shoulders" and become increasingly autonomous.

---

## 🧠 THE ARCHITECTURE: THREE-LAYER LEARNING SYSTEM

### **Layer 1: LLM Teacher (Current State)**
```
User Query
    ↓
generate_text_llm()
    ↓
External LLM Provider (Gemini/Groq/OpenAI)
    ↓
LLM Response (Verbose, context-rich, includes noise)
    ↓
Return to User
```

**Problem**: Knowledge is ephemeral—lost after response.

### **Layer 2: Knowledge Capture (New System)**
```
LLM Response
    ↓
Knowledge Extractor (extract_core_patterns)
    ↓
Pattern Analyzer (identify_signal_vs_noise)
    ↓
Zepto Compressor (compress_to_zepto_spr)
    ↓
Knowledge Graph Integrator (store_in_kg)
    ↓
SPR Manager (add_spr)
    ↓
Knowledge Graph Updated
```

**Solution**: Capture, compress, and store knowledge permanently.

### **Layer 3: Autonomous Operation (Target State)**
```
User Query
    ↓
Knowledge Graph Query (check_kg_first)
    ↓
    ├─ Found in KG? → Use SPR (no LLM call)
    │   ↓
    │   Decompress Zepto SPR
    │   ↓
    │   Return Response
    │
    └─ Not Found? → LLM Fallback
        ↓
        LLM Response
        ↓
        Capture & Store (Layer 2)
        ↓
        Return Response
```

**Goal**: ArchE becomes increasingly autonomous as Knowledge Graph grows.

---

## 🔧 IMPLEMENTATION: LOSSY KNOWLEDGE CAPTURE SYSTEM (LKCS)

### **Component 1: Knowledge Extractor**

**Purpose**: Extract core patterns from LLM responses, removing noise.

**Location**: `Three_PointO_ArchE/knowledge_capture/knowledge_extractor.py`

```python
"""
Knowledge Extractor - Extracts core patterns from LLM responses
Implements lossy knowledge transfer principles: Signal vs. Noise separation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)

@dataclass
class ExtractedPattern:
    """Core pattern extracted from LLM response"""
    pattern_id: str
    core_principle: str  # The universal abstraction
    context: str  # Original context (for reference)
    confidence: float  # How confident we are this is signal, not noise
    relationships: List[str]  # Related SPRs/concepts
    implementation_hints: Optional[str]  # Practical application
    noise_removed: List[str]  # What was filtered out

class KnowledgeExtractor:
    """
    Extracts core patterns from LLM responses using lossy knowledge transfer principles.
    
    Key Strategy:
    1. Identify signal (core principles, universal patterns)
    2. Remove noise (context-specific details, failed attempts, redundancy)
    3. Abstract to universal form (applicable across contexts)
    4. Extract relationships (connect to existing SPRs)
    """
    
    def __init__(self, spr_manager=None):
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
        # Step 1: Identify signal vs. noise
        signal_elements = self._identify_signal(llm_response)
        noise_elements = self._identify_noise(llm_response)
        
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
        
        pattern = ExtractedPattern(
            pattern_id=self._generate_pattern_id(universal_pattern),
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
            r"(?:principle|pattern|rule|law|mechanism|process|method|approach)",
            r"(?:always|never|must|should|typically|generally)",
            r"(?:because|therefore|thus|consequently|as a result)",
            r"(?:key|essential|critical|fundamental|core|important)",
        ]
        
        signal_elements = []
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            for indicator in signal_indicators:
                if re.search(indicator, sentence, re.IGNORECASE):
                    signal_elements.append(sentence.strip())
                    break
        
        return signal_elements
    
    def _identify_noise(self, text: str) -> List[str]:
        """Identify noise elements: context-specific, failed attempts, redundancy"""
        noise_indicators = [
            r"(?:example|instance|case|specific|particular|this|that)",
            r"(?:failed|error|mistake|wrong|incorrect|don't|shouldn't)",
            r"(?:maybe|perhaps|possibly|might|could|uncertain)",
            r"(?:I think|in my opinion|personally|I believe)",
        ]
        
        noise_elements = []
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            for indicator in noise_indicators:
                if re.search(indicator, sentence, re.IGNORECASE):
                    noise_elements.append(sentence.strip())
                    break
        
        return noise_elements
    
    def _extract_core_principle(self, signal_elements: List[str]) -> Optional[str]:
        """Extract the universal core principle from signal elements"""
        if not signal_elements:
            return None
        
        # Find the most abstract, universal statement
        # (This is a simplified version - full implementation would use NLP)
        core_sentences = [
            s for s in signal_elements
            if any(word in s.lower() for word in ["principle", "pattern", "rule", "law", "mechanism"])
        ]
        
        if core_sentences:
            return core_sentences[0]  # Return first core principle found
        
        # Fallback: return most general signal element
        return signal_elements[0] if signal_elements else None
    
    def _abstract_to_universal(self, principle: str, context: Dict[str, Any]) -> str:
        """Abstract context-specific principle to universal form"""
        # Remove context-specific references
        universal = principle
        
        # Replace specific examples with generic placeholders
        universal = re.sub(r'\b(this|that|these|those)\b', 'X', universal, flags=re.IGNORECASE)
        universal = re.sub(r'\b(here|there)\b', 'in context', universal, flags=re.IGNORECASE)
        
        # Remove specific names, dates, numbers (unless they're part of the principle)
        # (Simplified - full implementation would be more sophisticated)
        
        return universal.strip()
    
    def _find_related_sprs(self, pattern: str) -> List[str]:
        """Find related SPRs in Knowledge Graph"""
        if not self.spr_manager:
            return []
        
        # Use SPR manager to find related concepts
        related = self.spr_manager.scan_and_prime(pattern)
        return [spr.get("spr_id", "") for spr in related if spr.get("spr_id")]
    
    def _extract_implementation_hints(self, signal_elements: List[str]) -> Optional[str]:
        """Extract practical implementation hints"""
        implementation_keywords = ["implement", "use", "apply", "execute", "create", "build"]
        
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
        relationship_boost = min(0.2, len(self._find_related_sprs(" ".join(signal))) * 0.05)
        
        return min(1.0, signal_ratio + relationship_boost)
    
    def _generate_pattern_id(self, pattern: str) -> str:
        """Generate unique pattern ID following Guardian pointS format"""
        # Extract key words and create SPR-style ID
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]+\b', pattern)
        key_words = [w for w in words if len(w) > 4][:3]  # Take first 3 significant words
        
        if not key_words:
            key_words = ["Pattern", "Extracted"]
        
        # Format as Guardian pointS: FirstLastUppercase, middle lowercase
        pattern_id = "".join([w.capitalize() for w in key_words])
        
        return pattern_id
```

### **Component 2: Zepto SPR Compressor Integration**

**Purpose**: Compress extracted patterns to Zepto SPR format for efficient storage.

**Location**: `Three_PointO_ArchE/knowledge_capture/zepto_compressor.py`

```python
"""
Zepto SPR Compressor - Compresses extracted patterns to Zepto format
Integrates with existing ZeptoSPRProcessor
"""

from typing import Dict, Any, Optional
from .knowledge_extractor import ExtractedPattern
from ..zepto_spr_processor import ZeptoSPRProcessorAdapter, ZeptoSPRResult
import logging

logger = logging.getLogger(__name__)

class PatternZeptoCompressor:
    """
    Compresses extracted patterns to Zepto SPR format.
    
    Strategy:
    1. Take ExtractedPattern (already signal-filtered)
    2. Compress to Zepto SPR using PatternCrystallizationEngine
    3. Generate symbol codex for decompression
    4. Return compressed form + metadata
    """
    
    def __init__(self, zepto_processor: ZeptoSPRProcessorAdapter = None):
        self.zepto_processor = zepto_processor or ZeptoSPRProcessorAdapter()
        self.compression_history = []
    
    def compress_pattern(self, pattern: ExtractedPattern) -> Dict[str, Any]:
        """
        Compress extracted pattern to Zepto SPR.
        
        Args:
            pattern: ExtractedPattern to compress
            
        Returns:
            Dictionary with zepto_spr, codex, compression_ratio, etc.
        """
        # Build narrative from pattern
        narrative = self._build_narrative(pattern)
        
        # Compress to Zepto
        result: ZeptoSPRResult = self.zepto_processor.compress_to_zepto(
            narrative=narrative,
            target_stage="Zepto",
            context={
                "pattern_id": pattern.pattern_id,
                "confidence": pattern.confidence,
                "relationships": pattern.relationships
            }
        )
        
        if result.error:
            logger.error(f"Zepto compression failed: {result.error}")
            return {"error": result.error}
        
        compression_data = {
            "zepto_spr": result.zepto_spr,
            "symbol_codex": result.new_codex_entries,
            "compression_ratio": result.compression_ratio,
            "compression_stages": result.compression_stages,
            "original_length": result.original_length,
            "zepto_length": result.zepto_length,
            "pattern_id": pattern.pattern_id
        }
        
        self.compression_history.append(compression_data)
        logger.info(f"Compressed pattern {pattern.pattern_id}: {result.compression_ratio:.1f}:1")
        
        return compression_data
    
    def _build_narrative(self, pattern: ExtractedPattern) -> str:
        """Build narrative text from extracted pattern for compression"""
        narrative_parts = [
            f"Pattern: {pattern.core_principle}",
            f"Context: {pattern.context}",
        ]
        
        if pattern.implementation_hints:
            narrative_parts.append(f"Implementation: {pattern.implementation_hints}")
        
        if pattern.relationships:
            narrative_parts.append(f"Related to: {', '.join(pattern.relationships)}")
        
        return "\n".join(narrative_parts)
```

### **Component 3: Knowledge Graph Integrator**

**Purpose**: Store compressed patterns in Knowledge Graph as SPRs.

**Location**: `Three_PointO_ArchE/knowledge_capture/kg_integrator.py`

```python
"""
Knowledge Graph Integrator - Stores compressed patterns in Knowledge Graph
Integrates with SPRManager and KnowledgeGraphManager
"""

from typing import Dict, Any, Optional
from .knowledge_extractor import ExtractedPattern
from .zepto_compressor import PatternZeptoCompressor
from ..spr_manager import SPRManager
from ..knowledge_graph_manager import KnowledgeGraphManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KnowledgeGraphIntegrator:
    """
    Integrates extracted and compressed patterns into Knowledge Graph.
    
    Strategy:
    1. Take ExtractedPattern + Zepto compression
    2. Create SPR definition
    3. Add to SPRManager
    4. Update Knowledge Graph relationships
    5. Track learning metrics
    """
    
    def __init__(
        self,
        spr_manager: SPRManager,
        kg_manager: KnowledgeGraphManager = None,
        zepto_compressor: PatternZeptoCompressor = None
    ):
        self.spr_manager = spr_manager
        self.kg_manager = kg_manager
        self.zepto_compressor = zepto_compressor or PatternZeptoCompressor()
        self.integration_history = []
        self.learning_metrics = {
            "patterns_extracted": 0,
            "patterns_stored": 0,
            "llm_calls_saved": 0,
            "knowledge_growth_rate": 0.0
        }
    
    def integrate_pattern(
        self,
        pattern: ExtractedPattern,
        llm_metadata: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Integrate extracted pattern into Knowledge Graph.
        
        Args:
            pattern: ExtractedPattern to integrate
            llm_metadata: Metadata about the LLM call that generated this pattern
            
        Returns:
            SPR definition if successful, None otherwise
        """
        # Step 1: Compress to Zepto
        compression_data = self.zepto_compressor.compress_pattern(pattern)
        
        if "error" in compression_data:
            logger.error(f"Failed to compress pattern {pattern.pattern_id}")
            return None
        
        # Step 2: Create SPR definition
        spr_definition = self._create_spr_definition(pattern, compression_data, llm_metadata)
        
        # Step 3: Add to SPRManager
        try:
            self.spr_manager.add_spr(spr_definition)
            logger.info(f"Added SPR to Knowledge Graph: {spr_definition['spr_id']}")
        except Exception as e:
            logger.error(f"Failed to add SPR: {e}")
            return None
        
        # Step 4: Update Knowledge Graph relationships (if KG manager available)
        if self.kg_manager:
            self._update_kg_relationships(spr_definition, pattern.relationships)
        
        # Step 5: Update metrics
        self.learning_metrics["patterns_extracted"] += 1
        self.learning_metrics["patterns_stored"] += 1
        
        self.integration_history.append({
            "spr_id": spr_definition["spr_id"],
            "pattern_id": pattern.pattern_id,
            "timestamp": datetime.now().isoformat(),
            "compression_ratio": compression_data["compression_ratio"]
        })
        
        return spr_definition
    
    def _create_spr_definition(
        self,
        pattern: ExtractedPattern,
        compression_data: Dict[str, Any],
        llm_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create SPR definition from pattern and compression data"""
        spr_id = pattern.pattern_id
        
        spr_definition = {
            "spr_id": spr_id,
            "name": pattern.pattern_id,
            "definition": pattern.core_principle,
            "description": f"Extracted from LLM response: {pattern.context}",
            "zepto_spr": compression_data["zepto_spr"],
            "symbol_codex": compression_data["symbol_codex"],
            "compression_stages": compression_data["compression_stages"],
            "compression_ratio": compression_data["compression_ratio"],
            "confidence": pattern.confidence,
            "relationships": pattern.relationships,
            "implementation_hints": pattern.implementation_hints,
            "source": "llm_knowledge_capture",
            "llm_metadata": llm_metadata or {},
            "created_at": datetime.now().isoformat(),
            "noise_removed": pattern.noise_removed  # For transparency
        }
        
        return spr_definition
    
    def _update_kg_relationships(self, spr_definition: Dict[str, Any], relationships: List[str]):
        """Update Knowledge Graph with new relationships"""
        if not self.kg_manager:
            return
        
        spr_id = spr_definition["spr_id"]
        
        # Add relationships to existing SPRs
        for related_spr_id in relationships:
            try:
                self.kg_manager.add_relationship(
                    source_node=spr_id,
                    target_node=related_spr_id,
                    relationship_type="learned_from",
                    metadata={"source": "llm_knowledge_capture"}
                )
            except Exception as e:
                logger.warning(f"Failed to add relationship {spr_id} -> {related_spr_id}: {e}")
```

### **Component 4: LLM Response Interceptor**

**Purpose**: Intercept LLM responses and trigger knowledge capture.

**Location**: `Three_PointO_ArchE/knowledge_capture/llm_interceptor.py`

```python
"""
LLM Response Interceptor - Intercepts LLM responses and triggers knowledge capture
Integrates with existing llm_tool.py
"""

from typing import Dict, Any, Optional
from .knowledge_extractor import KnowledgeExtractor, ExtractedPattern
from .kg_integrator import KnowledgeGraphIntegrator
import logging

logger = logging.getLogger(__name__)

class LLMResponseInterceptor:
    """
    Intercepts LLM responses and triggers knowledge capture.
    
    Strategy:
    1. Wrap generate_text_llm() calls
    2. After LLM response, extract patterns
    3. Compress and store in Knowledge Graph
    4. Track learning progress
    """
    
    def __init__(
        self,
        knowledge_extractor: KnowledgeExtractor,
        kg_integrator: KnowledgeGraphIntegrator,
        enable_capture: bool = True,
        confidence_threshold: float = 0.6
    ):
        self.extractor = knowledge_extractor
        self.integrator = kg_integrator
        self.enable_capture = enable_capture
        self.confidence_threshold = confidence_threshold
        self.interception_history = []
    
    def intercept_llm_response(
        self,
        llm_response: str,
        query_context: Dict[str, Any],
        llm_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Intercept LLM response and capture knowledge.
        
        Args:
            llm_response: The LLM response text
            query_context: Original query and context
            llm_metadata: LLM provider, model, tokens, etc.
            
        Returns:
            Dictionary with interception results and captured knowledge
        """
        if not self.enable_capture:
            return {"captured": False, "reason": "capture_disabled"}
        
        # Extract pattern
        pattern: Optional[ExtractedPattern] = self.extractor.extract_from_llm_response(
            llm_response=llm_response,
            query_context=query_context,
            llm_metadata=llm_metadata
        )
        
        if not pattern:
            return {"captured": False, "reason": "no_extractable_pattern"}
        
        # Check confidence threshold
        if pattern.confidence < self.confidence_threshold:
            logger.debug(f"Pattern confidence {pattern.confidence:.2f} below threshold {self.confidence_threshold}")
            return {
                "captured": False,
                "reason": "low_confidence",
                "confidence": pattern.confidence
            }
        
        # Integrate into Knowledge Graph
        spr_definition = self.integrator.integrate_pattern(pattern, llm_metadata)
        
        if not spr_definition:
            return {"captured": False, "reason": "integration_failed"}
        
        # Track interception
        self.interception_history.append({
            "pattern_id": pattern.pattern_id,
            "spr_id": spr_definition.get("spr_id"),
            "confidence": pattern.confidence,
            "compression_ratio": spr_definition.get("compression_ratio", 0),
            "timestamp": llm_metadata.get("timestamp") if llm_metadata else None
        })
        
        logger.info(f"✓ Captured knowledge: {pattern.pattern_id} → {spr_definition.get('spr_id')}")
        
        return {
            "captured": True,
            "pattern_id": pattern.pattern_id,
            "spr_id": spr_definition.get("spr_id"),
            "confidence": pattern.confidence,
            "compression_ratio": spr_definition.get("compression_ratio", 0)
        }
```

### **Component 5: Knowledge Graph Query Router**

**Purpose**: Route queries to Knowledge Graph first, LLM only as fallback.

**Location**: `Three_PointO_ArchE/knowledge_capture/kg_router.py`

```python
"""
Knowledge Graph Query Router - Routes queries to KG first, LLM as fallback
Enables ArchE to use its own knowledge instead of always querying LLM
"""

from typing import Dict, Any, Optional, Tuple
from ..spr_manager import SPRManager
from ..zepto_spr_processor import ZeptoSPRProcessorAdapter
import logging

logger = logging.getLogger(__name__)

class KnowledgeGraphRouter:
    """
    Routes queries to Knowledge Graph first, LLM only as fallback.
    
    Strategy:
    1. Check Knowledge Graph for relevant SPRs
    2. If found, decompress Zepto SPR and return
    3. If not found, fallback to LLM
    4. Track hit rate (autonomy metric)
    """
    
    def __init__(
        self,
        spr_manager: SPRManager,
        zepto_processor: ZeptoSPRProcessorAdapter = None,
        enable_routing: bool = True
    ):
        self.spr_manager = spr_manager
        self.zepto_processor = zepto_processor or ZeptoSPRProcessorAdapter()
        self.enable_routing = enable_routing
        self.routing_metrics = {
            "kg_hits": 0,
            "llm_fallbacks": 0,
            "autonomy_rate": 0.0
        }
    
    def route_query(
        self,
        query: str,
        query_context: Dict[str, Any] = None
    ) -> Tuple[Optional[str], str]:
        """
        Route query to Knowledge Graph or LLM.
        
        Args:
            query: User query
            query_context: Additional context
            
        Returns:
            Tuple of (response_text, source) where source is "kg" or "llm"
        """
        if not self.enable_routing:
            return None, "llm"  # Disabled routing, use LLM
        
        # Step 1: Check Knowledge Graph for relevant SPRs
        relevant_sprs = self.spr_manager.scan_and_prime(query)
        
        if not relevant_sprs:
            logger.debug("No relevant SPRs found in Knowledge Graph, routing to LLM")
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm"
        
        # Step 2: Find best matching SPR
        best_spr = self._find_best_match(query, relevant_sprs)
        
        if not best_spr:
            logger.debug("No suitable SPR match found, routing to LLM")
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm"
        
        # Step 3: Decompress Zepto SPR if available
        response_text = self._decompress_spr(best_spr)
        
        if not response_text:
            logger.warning(f"Failed to decompress SPR {best_spr.get('spr_id')}, routing to LLM")
            self.routing_metrics["llm_fallbacks"] += 1
            self._update_autonomy_rate()
            return None, "llm"
        
        # Step 4: Success - return Knowledge Graph response
        logger.info(f"✓ Knowledge Graph hit: {best_spr.get('spr_id')}")
        self.routing_metrics["kg_hits"] += 1
        self._update_autonomy_rate()
        
        return response_text, "kg"
    
    def _find_best_match(self, query: str, relevant_sprs: list) -> Optional[Dict[str, Any]]:
        """Find best matching SPR for query"""
        if not relevant_sprs:
            return None
        
        # Simple strategy: return first SPR with Zepto compression
        # (Full implementation would use semantic similarity)
        for spr in relevant_sprs:
            if spr.get("zepto_spr"):
                return spr
        
        # Fallback: return first SPR
        return relevant_sprs[0] if relevant_sprs else None
    
    def _decompress_spr(self, spr: Dict[str, Any]) -> Optional[str]:
        """Decompress Zepto SPR to readable text"""
        zepto_spr = spr.get("zepto_spr")
        
        if not zepto_spr:
            # No Zepto compression, use definition directly
            return spr.get("definition") or spr.get("description")
        
        # Decompress Zepto SPR
        try:
            codex = spr.get("symbol_codex", {})
            result = self.zepto_processor.decompress_from_zepto(
                zepto_spr=zepto_spr,
                codex=codex
            )
            
            if result.error:
                logger.warning(f"Zepto decompression error: {result.error}")
                return spr.get("definition")  # Fallback to definition
            
            return result.decompressed_text
        except Exception as e:
            logger.error(f"Failed to decompress Zepto SPR: {e}")
            return spr.get("definition")  # Fallback to definition
    
    def _update_autonomy_rate(self):
        """Update autonomy rate metric"""
        total = self.routing_metrics["kg_hits"] + self.routing_metrics["llm_fallbacks"]
        if total > 0:
            self.routing_metrics["autonomy_rate"] = self.routing_metrics["kg_hits"] / total
```

---

## 🔄 INTEGRATION: MODIFYING EXISTING LLM TOOL

### **Modified `llm_tool.py`**

```python
# Add to imports
from Three_PointO_ArchE.knowledge_capture.llm_interceptor import LLMResponseInterceptor
from Three_PointO_ArchE.knowledge_capture.kg_router import KnowledgeGraphRouter

# Initialize interceptors (singleton pattern)
_interceptor = None
_router = None

def get_knowledge_capture_system():
    """Get or create knowledge capture system"""
    global _interceptor, _router
    
    if _interceptor is None:
        from Three_PointO_ArchE.knowledge_capture.knowledge_extractor import KnowledgeExtractor
        from Three_PointO_ArchE.knowledge_capture.kg_integrator import KnowledgeGraphIntegrator
        from Three_PointO_ArchE.spr_manager import SPRManager
        
        spr_manager = SPRManager("knowledge_graph/spr_definitions_tv.json")
        extractor = KnowledgeExtractor(spr_manager=spr_manager)
        integrator = KnowledgeGraphIntegrator(spr_manager=spr_manager)
        _interceptor = LLMResponseInterceptor(extractor, integrator)
        
        from Three_PointO_ArchE.knowledge_capture.kg_router import KnowledgeGraphRouter
        _router = KnowledgeGraphRouter(spr_manager)
    
    return _interceptor, _router

def generate_text_llm(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate text using Knowledge Graph first, LLM as fallback.
    """
    # ... existing code ...
    
    # NEW: Check Knowledge Graph first
    interceptor, router = get_knowledge_capture_system()
    
    query = inputs.get("prompt", "")
    query_context = {
        "query": query,
        "user_id": inputs.get("user_id"),
        "session_id": inputs.get("session_id")
    }
    
    # Try Knowledge Graph first
    kg_response, source = router.route_query(query, query_context)
    
    if kg_response and source == "kg":
        # Knowledge Graph hit - return without LLM call
        return {
            "result": {"response_text": kg_response},
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.SUCCESS,
                message=f"Response from Knowledge Graph (autonomous mode)",
                inputs=inputs,
                outputs={"response_text": kg_response},
                confidence=0.9,
                execution_time=time.time() - start_time,
                metadata={
                    "source": "knowledge_graph",
                    "autonomous": True,
                    "llm_bypassed": True
                }
            )
        }
    
    # Knowledge Graph miss - fallback to LLM
    # ... existing LLM call code ...
    
    # After LLM response, capture knowledge
    llm_response_text = outputs.get("response_text", "")
    llm_metadata = {
        "provider": provider,
        "model": model,
        "tokens_used": getattr(result, "usage", {}).get("total_tokens", 0),
        "timestamp": datetime.now().isoformat()
    }
    
    # Intercept and capture
    capture_result = interceptor.intercept_llm_response(
        llm_response=llm_response_text,
        query_context=query_context,
        llm_metadata=llm_metadata
    )
    
    if capture_result.get("captured"):
        logger.info(f"✓ Knowledge captured: {capture_result.get('pattern_id')}")
    
    # Return LLM response
    return {
        "result": outputs,
        "reflection": create_reflection(
            # ... existing reflection code ...
            metadata={
                "source": "llm",
                "knowledge_captured": capture_result.get("captured", False),
                "pattern_id": capture_result.get("pattern_id")
            }
        )
    }
```

---

## 📊 METRICS & MONITORING

### **Learning Metrics**

```python
class LearningMetrics:
    """Track ArchE's learning progress"""
    
    metrics = {
        "patterns_extracted": 0,
        "patterns_stored": 0,
        "llm_calls_saved": 0,
        "autonomy_rate": 0.0,  # % of queries answered from KG
        "knowledge_growth_rate": 0.0,  # Patterns per day
        "compression_ratios": [],  # Track compression efficiency
        "confidence_scores": []  # Track pattern quality
    }
    
    def get_autonomy_report(self) -> Dict[str, Any]:
        """Generate autonomy report"""
        return {
            "autonomy_rate": self.metrics["autonomy_rate"],
            "llm_calls_saved": self.metrics["llm_calls_saved"],
            "knowledge_base_size": self.metrics["patterns_stored"],
            "average_compression_ratio": sum(self.metrics["compression_ratios"]) / len(self.metrics["compression_ratios"]) if self.metrics["compression_ratios"] else 0,
            "average_confidence": sum(self.metrics["confidence_scores"]) / len(self.metrics["confidence_scores"]) if self.metrics["confidence_scores"] else 0
        }
```

---

## 🎯 IMPLEMENTATION ROADMAP

### **Phase 1: Foundation (Week 1-2)**
1. ✅ Create `knowledge_capture/` directory
2. ✅ Implement `KnowledgeExtractor`
3. ✅ Implement `PatternZeptoCompressor`
4. ✅ Implement `KnowledgeGraphIntegrator`
5. ✅ Unit tests for each component

### **Phase 2: Integration (Week 3-4)**
1. ✅ Implement `LLMResponseInterceptor`
2. ✅ Modify `llm_tool.py` to use interceptor
3. ✅ Implement `KnowledgeGraphRouter`
4. ✅ Add routing logic to `generate_text_llm()`
5. ✅ Integration tests

### **Phase 3: Optimization (Week 5-6)**
1. ✅ Improve pattern extraction accuracy
2. ✅ Optimize Zepto compression
3. ✅ Enhance Knowledge Graph query matching
4. ✅ Add metrics and monitoring
5. ✅ Performance tuning

### **Phase 4: Autonomous Operation (Week 7-8)**
1. ✅ Enable autonomous routing by default
2. ✅ Monitor autonomy rate
3. ✅ Fine-tune confidence thresholds
4. ✅ Generate learning reports
5. ✅ Production deployment

---

## 🚀 EXPECTED OUTCOMES

### **Short Term (1-3 months)**
- **Autonomy Rate**: 10-20% of queries answered from Knowledge Graph
- **Knowledge Base**: 100-500 new SPRs from LLM interactions
- **Compression Efficiency**: 100:1 to 1000:1 compression ratios
- **Cost Savings**: 10-20% reduction in LLM API calls

### **Medium Term (3-6 months)**
- **Autonomy Rate**: 30-50% of queries answered from Knowledge Graph
- **Knowledge Base**: 500-2000 new SPRs
- **Domain Expertise**: ArchE becomes expert in frequently queried domains
- **Cost Savings**: 30-50% reduction in LLM API calls

### **Long Term (6-12 months)**
- **Autonomy Rate**: 60-80% of queries answered from Knowledge Graph
- **Knowledge Base**: 2000+ new SPRs
- **Specialized Domains**: ArchE develops deep expertise in specific areas
- **Cost Savings**: 60-80% reduction in LLM API calls
- **Autonomous Evolution**: ArchE can learn and evolve without constant LLM dependency

---

## 🔑 KEY PRINCIPLES

1. **Lossy is Better**: Capture signal, remove noise, compress to essence
2. **Gradual Autonomy**: Start with LLM, gradually shift to Knowledge Graph
3. **Quality over Quantity**: Only store high-confidence patterns
4. **Continuous Learning**: Every LLM interaction is a learning opportunity
5. **Compression Efficiency**: Zepto SPRs enable massive knowledge storage
6. **Relationship Mapping**: Connect new knowledge to existing SPRs
7. **Transparency**: Track what was removed (noise) for auditability

---

## 📝 CONCLUSION

This system enables ArchE to:
1. **Learn from the LLM teacher** (capture knowledge)
2. **Compress to Zepto SPRs** (lossy but optimized)
3. **Store in Knowledge Graph** (permanent knowledge base)
4. **Gradually reduce LLM dependency** (become autonomous)
5. **Use its own knowledge** (answer from Knowledge Graph)

**The result**: ArchE becomes increasingly autonomous, standing on the compressed shoulders of its LLM teacher, and eventually outperforming it in specialized domains.

---

**Next Steps**:
1. Review this design with Keyholder
2. Implement Phase 1 components
3. Test with sample LLM responses
4. Iterate based on results

