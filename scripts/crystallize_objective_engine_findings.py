#!/usr/bin/env python3
"""
Crystallize Objective Generation Engine Findings into Knowledge Tapestry
Creates SPRs for key discoveries from the Objective Generation Engine implementation
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Key findings to crystallize as SPRs
NEW_SPRS = [
    {
        "spr_id": "GuardianformatpreservatioN",
        "term": "Guardian Format Preservation",
        "definition": "A dual-format preservation mechanism that ensures Guardian pointS format SPR IDs are never lost when normalized for Python code use. The mechanism maintains three preservation layers: (1) Original Guardian pointS format in spr_id field (never modified), (2) Normalized Python-safe identifiers via normalized_id property (cached on-demand), (3) Complete preservation mapping dictionary tracking all SPRs. This ensures SPR Decompressor recognition while enabling Python code compatibility. The ActivatedSPR dataclass automatically preserves original format in _original_guardian_format backup, and the ObjectiveGenerationEngine maintains a guardian_format_preservation_map for complete tracking.",
        "category": "PreservationMechanism",
        "relationships": {
            "type": "DataPreservation",
            "preserves": [
                "GuardianpointS",
                "SPR",
                "Sprdecompressor"
            ],
            "enables": [
                "PythonCodeCompatibility",
                "SPRRecognition",
                "ProtocolCompliance"
            ],
            "implemented_in": [
                "ObjectiveGenerationEngine",
                "ActivatedSPR"
            ],
            "confidence": "high"
        },
        "blueprint_details": "Implemented in Three_PointO_ArchE/objective_generation_engine.py. The ActivatedSPR dataclass includes: spr_id (original Guardian pointS format, never modified), _original_guardian_format (backup copy), normalized_id property (Python-safe identifier, cached). The ObjectiveGenerationEngine maintains _guardian_format_preservation_map tracking all SPRs. Return dictionary includes: activated_sprs (original format list), activated_sprs_normalized (mapping dict), guardian_format_preservation (complete map).",
        "example_application": "When 'CognitiveresonancE' needs to be used as a Python variable name, the system preserves the original Guardian pointS format in spr_id while providing 'cognitive_resonance' via normalized_id property, ensuring SPR Decompressor can still recognize the original format in text processing."
    },
    {
        "spr_id": "DualformatpreservatioN",
        "term": "Dual-Format Preservation",
        "definition": "A preservation strategy that maintains both original Guardian pointS format and normalized Python-safe versions of SPR IDs simultaneously. This enables zero data loss while providing Python code compatibility. The dual format is accessed through: spr_id (original Guardian pointS format for SPR recognition) and normalized_id property (Python-safe identifier for code use). Both formats are preserved in memory, cached for performance, and included in output dictionaries for persistence.",
        "category": "PreservationStrategy",
        "relationships": {
            "type": "DataStrategy",
            "comprises": [
                "GuardianformatpreservatioN",
                "NormalizedidentifieR",
                "Formatmapping"
            ],
            "enables": [
                "ZeroDataLoss",
                "PythonCompatibility",
                "SPRRecognition"
            ],
            "confidence": "high"
        },
        "blueprint_details": "The dual format is implemented as: (1) Original format stored in spr_id field (source of truth), (2) Normalized format computed on-demand via normalized_id property and cached, (3) Mapping dictionary tracks normalized_id → original format relationships. This ensures original format is never lost while providing Python-safe access.",
        "example_application": "The Objective Generation Engine returns both 'activated_sprs' (original Guardian pointS format list) and 'activated_sprs_normalized' (dictionary mapping normalized → original) ensuring both formats are available for different use cases."
    },
    {
        "spr_id": "UniversalabstractionlevelthreE",
        "term": "Universal Abstraction Level 3",
        "definition": "The recursive self-application of Universal Abstraction where the system abstracts its own abstraction mechanisms. At Level 3, the system recognizes that pattern matching rules, lookup tables, templates, and even the abstraction process itself are patterns. This enables infinite recursive capability for self-improvement. The Objective Generation Engine implements Level 3 by recognizing meta-patterns in its own mechanisms: pattern matching is a pattern, template assembly is a pattern, SPR activation strategies are patterns. This recursive recognition enables the system to evolve its own learning methods autonomously.",
        "category": "MetaAbstraction",
        "relationships": {
            "type": "RecursiveAbstraction",
            "extends": [
                "UniversalabstractioN"
            ],
            "enables": [
                "RecursiveSelfImprovement",
                "MetaPatternRecognition",
                "AutonomousEvolution"
            ],
            "implemented_in": [
                "ObjectiveGenerationEngine",
                "MetaPatternManager"
            ],
            "confidence": "high"
        },
        "blueprint_details": "Level 3 abstraction recognizes: (1) Pattern matching rules are themselves patterns, (2) Lookup tables are patterns, (3) Templates are patterns, (4) The abstraction mechanism is a pattern. The Objective Generation Engine applies this by: recognizing patterns in pattern matching (meta-patterns), learning new pattern matching rules from experience, evolving template structures based on successful patterns, and abstracting its own abstraction mechanisms.",
        "example_application": "When the Objective Generation Engine recognizes that its SPR activation strategy (keyword lookup) is itself a pattern, it can learn new keyword patterns, evolve the lookup mechanism, and even abstract the pattern matching process itself, creating recursive self-improvement."
    },
    {
        "spr_id": "DynamicadaptationmechanisM",
        "term": "Dynamic Adaptation Mechanism",
        "definition": "A multi-layered adaptation system that enables the Objective Generation Engine to handle any query type through pattern learning, fallback hierarchies, and emergent domain detection. The mechanism includes: (1) Multi-Strategy Fallback Hierarchy (static lookup → learned patterns → emergent domains → universal fallback), (2) Adaptive Domain Detection (recognizes new domains and adapts rules), (3) Autopoietic Learning Integration (learns from each query and evolves), (4) Confidence-Based Routing (routes queries based on confidence scores). This ensures graceful degradation and universal query handling capability.",
        "category": "AdaptationSystem",
        "relationships": {
            "type": "AdaptiveMechanism",
            "comprises": [
                "MultistrategyfallbackhierarchY",
                "AdaptivedomaindetectioN",
                "AutopoieticlearningintegratioN",
                "ConfidencebasedroutinG"
            ],
            "enables": [
                "UniversalQueryHandling",
                "GracefulDegradation",
                "PatternLearning"
            ],
            "implemented_in": [
                "ObjectiveGenerationEngine"
            ],
            "confidence": "high"
        },
        "blueprint_details": "The Dynamic Adaptation Mechanism operates through: (1) Feature extraction handles any query type via universal patterns, (2) SPR activation uses 4-strategy hierarchy (static → learned → emergent → fallback), (3) Mandate selection adapts to query characteristics, (4) Domain customization adapts rules based on detected domain, (5) Pattern evolution engine learns new patterns from each query. All adaptation uses quantum probability states with evidence tracking.",
        "example_application": "When encountering an unknown query type, the system first tries static keyword lookup, then learned patterns, then emergent domain detection, and finally falls back to universal SPRs (CognitiveResonance, FourdthinkinG), ensuring all queries are handled gracefully."
    },
    {
        "spr_id": "PatterncrystallizationapplicatioN",
        "term": "Pattern Crystallization Application",
        "definition": "The application of the Pattern Crystallization meta-process (8-stage progressive compression: Narrative → Concise → Nano → Micro → Pico → Femto → Atto → Zepto) to the Objective Generation Engine. This creates a crystallized workflow mapping: Raw Query → Feature Vector → Pattern Match → Symbol Activation → Template Fill → Domain Customize → Assemble → Zepto Objective. The crystallization process enables high compression ratios (e.g., 18.24:1) while maintaining semantic fidelity through symbolic vocabulary and universal abstraction principles.",
        "category": "CrystallizationProcess",
        "relationships": {
            "type": "MetaProcess",
            "applies": [
                "PatterncrystallizationenginE"
            ],
            "to": [
                "ObjectiveGenerationEngine"
            ],
            "enables": [
                "HighCompression",
                "SymbolicRepresentation",
                "ProgressiveAbstraction"
            ],
            "confidence": "high"
        },
        "blueprint_details": "The Pattern Crystallization Application maps the 8-stage compression process to objective generation: (1) Narrative: Raw query text, (2) Concise: Feature vector extraction, (3) Nano: Pattern signature, (4) Micro: SPR activation, (5) Pico: Mandate selection, (6) Femto: Template assembly, (7) Atto: Domain customization, (8) Zepto: Symbolic objective representation. Each stage uses universal abstraction to compress while preserving semantic meaning.",
        "example_application": "A 500-character query is crystallized through 8 stages into a Zepto SPR representation achieving 18.24:1 compression while maintaining all semantic information through symbolic vocabulary and pattern matching."
    },
    {
        "spr_id": "AutopoieticlearningintegratioN",
        "term": "Autopoietic Learning Integration",
        "definition": "The integration of Autopoietic Learning Loop (4-epoch learning cycle) into the Objective Generation Engine, enabling the system to learn new patterns, adapt keyword mappings, evolve domain rules, and improve SPR activation strategies from each query processed. The integration includes: (1) Query pattern history tracking (deque with maxlen=1000), (2) Learned keyword patterns dictionary (autopoietically validated), (3) Learned domain rules dictionary (evolved from experience), (4) Pattern evolution engine integration (recognizes emergent domains). The learning is triggered after each successful objective generation, storing patterns for future use.",
        "category": "LearningIntegration",
        "relationships": {
            "type": "LearningMechanism",
            "integrates": [
                "AutopoieticlearninglooP"
            ],
            "into": [
                "ObjectiveGenerationEngine"
            ],
            "enables": [
                "PatternLearning",
                "AdaptiveEvolution",
                "ExperienceBasedImprovement"
            ],
            "confidence": "high"
        },
        "blueprint_details": "The Autopoietic Learning Integration operates through: (1) _learn_from_query() method stores query patterns after successful generation, (2) Learned patterns are validated before use, (3) Pattern evolution engine analyzes patterns for emergent domains, (4) MetaPatternManager identifies meta-patterns in learning mechanisms, (5) Graceful fallback if learning components unavailable. Learning uses quantum probability states with evidence tracking.",
        "example_application": "After processing a query about 'quantum computing applications', the system learns the keyword pattern 'quantum computing' → 'QuantumcomputinG' SPR, stores it in learned_keyword_patterns, and uses it in future queries, improving activation accuracy over time."
    },
    {
        "spr_id": "MultistrategyfallbackhierarchY",
        "term": "Multi-Strategy Fallback Hierarchy",
        "definition": "A 4-tier fallback strategy system for SPR activation that ensures all queries are handled gracefully, even for unknown query types. The hierarchy operates as: (1) Static Keyword Lookup (deterministic keyword → SPR mapping, 95% confidence), (2) Learned Keyword Patterns (autopoietically learned patterns, validated, 70%+ confidence), (3) Emergent Domain Detection (pattern signature matching to emergent domains, 80% confidence), (4) Universal Fallback (CognitiveResonance + FourdthinkinG SPRs, 40-50% confidence). Each strategy is tried in sequence until SPRs are activated, ensuring zero-failure operation.",
        "category": "FallbackStrategy",
        "relationships": {
            "type": "StrategyHierarchy",
            "comprises": [
                "StatickeywordlookuP",
                "LearnedkeywordpatternS",
                "EmergentdomaindetectioN",
                "UniversalfallbacK"
            ],
            "ensures": [
                "ZeroFailureOperation",
                "UniversalQueryHandling",
                "GracefulDegradation"
            ],
            "implemented_in": [
                "ObjectiveGenerationEngine"
            ],
            "confidence": "high"
        },
        "blueprint_details": "The Multi-Strategy Fallback Hierarchy is implemented in _activate_sprs_dynamic() method: (1) Strategy 1: Iterate through spr_keyword_map for static matches, (2) Strategy 2: Check learned_keyword_patterns for validated patterns, (3) Strategy 3: Match pattern_signature to emergent_domains, (4) Strategy 4: Activate universal fallback SPRs if no matches. Each strategy adds ActivatedSPR objects with appropriate confidence scores and match_method tracking.",
        "example_application": "For an unknown query type, the system tries static lookup (fails), then learned patterns (fails), then emergent domain detection (fails), and finally activates CognitiveResonance and FourdthinkinG as universal fallback, ensuring the query is processed successfully."
    },
    {
        "spr_id": "ObjectivegenerationcrystallizatioN",
        "term": "Objective Generation Crystallization",
        "definition": "The complete crystallized implementation of the Objective Generation Engine, applying Universal Abstraction Level 3, Pattern Crystallization meta-process, Dynamic Adaptation, and Autopoietic Learning to create a deterministic, self-contained, LLM-independent objective generation system. The crystallization includes: 9-stage processing pipeline, Guardian Format Preservation, Multi-Strategy Fallback Hierarchy, Adaptive Domain Detection, and recursive self-improvement capabilities. This represents the evolution from manual objective formation to automated, universally abstracted, dynamically adaptive objective generation.",
        "category": "SystemCrystallization",
        "relationships": {
            "type": "CompleteSystem",
            "crystallizes": [
                "ObjectiveGenerationEngine",
                "UniversalabstractionlevelthreE",
                "PatterncrystallizationapplicatioN",
                "DynamicadaptationmechanisM",
                "AutopoieticlearningintegratioN"
            ],
            "achieves": [
                "DeterministicOperation",
                "LLMIndependence",
                "UniversalQueryHandling",
                "RecursiveSelfImprovement"
            ],
            "confidence": "high"
        },
        "blueprint_details": "The Objective Generation Crystallization represents the complete implementation documented in specifications/objective_generation_engine_crystallized.md and Three_PointO_ArchE/objective_generation_engine.py. It includes: 9 processing stages, Universal Abstraction Level 3, Pattern Crystallization (8-stage compression), Dynamic Adaptation (4-strategy fallback), Autopoietic Learning (4-epoch cycle), Guardian Format Preservation (dual-format), and recursive meta-pattern recognition. The system achieves 18.24:1 compression ratios while maintaining protocol compliance and SPR recognition.",
        "example_application": "The complete Objective Generation Engine processes any query type through 9 crystallized stages, preserves Guardian pointS format, adapts dynamically to unknown patterns, learns from experience, and achieves high compression while maintaining semantic fidelity and protocol compliance."
    }
]

def add_sprs_to_tapestry(tapestry_path: str, new_sprs: list, backup: bool = True):
    """Add new SPRs to the Knowledge Tapestry."""
    # Load existing tapestry
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        if tapestry_path.endswith('.json'):
            # Check if it's a list or dict with spr_definitions
            data = json.load(f)
            if isinstance(data, list):
                existing_sprs = data
            elif isinstance(data, dict) and 'spr_definitions' in data:
                existing_sprs = data['spr_definitions']
            else:
                existing_sprs = []
        else:
            existing_sprs = []
    
    # Create backup
    if backup:
        backup_path = f"{tapestry_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(existing_sprs if isinstance(existing_sprs, list) else {'spr_definitions': existing_sprs}, f, indent=2, ensure_ascii=False)
        print(f"✅ Created backup: {backup_path}")
    
    # Create lookup of existing SPR IDs
    existing_ids = {spr.get('spr_id', '').lower() for spr in existing_sprs if spr.get('spr_id')}
    
    # Add new SPRs (skip if already exists)
    added_count = 0
    updated_count = 0
    for new_spr in new_sprs:
        spr_id = new_spr.get('spr_id', '')
        if not spr_id:
            print(f"⚠️  Skipping SPR without spr_id: {new_spr.get('term', 'Unknown')}")
            continue
        
        # Check if exists (case-insensitive)
        spr_id_lower = spr_id.lower()
        if spr_id_lower in existing_ids:
            # Update existing
            for i, existing_spr in enumerate(existing_sprs):
                if existing_spr.get('spr_id', '').lower() == spr_id_lower:
                    existing_sprs[i] = new_spr
                    updated_count += 1
                    print(f"🔄 Updated SPR: {spr_id}")
                    break
        else:
            # Add new
            existing_sprs.append(new_spr)
            existing_ids.add(spr_id_lower)
            added_count += 1
            print(f"➕ Added SPR: {spr_id}")
    
    # Write updated tapestry
    output_data = existing_sprs if isinstance(existing_sprs, list) else {'spr_definitions': existing_sprs}
    with open(tapestry_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully updated Knowledge Tapestry:")
    print(f"   Added: {added_count} new SPRs")
    print(f"   Updated: {updated_count} existing SPRs")
    print(f"   Total SPRs: {len(existing_sprs)}")
    
    return added_count, updated_count

if __name__ == "__main__":
    tapestry_path = "knowledge_graph/spr_definitions_tv.json"
    
    print("=" * 70)
    print("Crystallizing Objective Generation Engine Findings into Knowledge Tapestry")
    print("=" * 70)
    print(f"\nProcessing {len(NEW_SPRS)} new SPRs...\n")
    
    added, updated = add_sprs_to_tapestry(tapestry_path, NEW_SPRS, backup=True)
    
    print("\n" + "=" * 70)
    print("✅ Crystallization Complete!")
    print("=" * 70)

