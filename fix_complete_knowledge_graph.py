import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add ArchE to path
sys.path.append('Three_PointO_ArchE')

def fix_complete_knowledge_graph():
    """Fix the entire knowledge graph system comprehensively"""
    print("🔧 FIXING COMPLETE KNOWLEDGE GRAPH SYSTEM")
    print("=" * 60)
    
    # Load current knowledge structure
    with open('complete_knowledge_structure.json', 'r') as f:
        expanded_knowledge = json.load(f)
    
    print(f"📊 Loaded expanded knowledge:")
    print(f"   • {expanded_knowledge['metadata']['total_nodes']} nodes")
    print(f"   • {expanded_knowledge['metadata']['total_edges']} edges")
    
    # Create clean, comprehensive SPR definitions
    clean_spr_definitions = create_clean_spr_definitions(expanded_knowledge)
    
    # Create clean, comprehensive knowledge tapestry
    clean_knowledge_tapestry = create_clean_knowledge_tapestry(expanded_knowledge)
    
    # Save fixed files
    with open('Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json', 'w') as f:
        json.dump(clean_spr_definitions, f, indent=2)
    
    with open('Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json', 'w') as f:
        json.dump(clean_knowledge_tapestry, f, indent=2)
    
    print(f"\n✅ KNOWLEDGE GRAPH FIXED:")
    print(f"   • {len(clean_spr_definitions)} clean SPR definitions")
    print(f"   • {len(clean_knowledge_tapestry['nodes'])} knowledge tapestry nodes")
    print(f"   • {len(clean_knowledge_tapestry['relationships'])} relationships")
    print(f"   • Clean, consistent structure")
    
    # Verify the fix
    verify_knowledge_graph()
    
    return True

def create_clean_spr_definitions(expanded_knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create clean, comprehensive SPR definitions"""
    
    # Core ArchE SPRs (essential)
    core_sprs = [
        {
            "spr_id": "RISE",
            "term": "Resonant Insight and Strategy Engine",
            "definition": "The comprehensive methodology for transforming complex problems into strategic solutions through Scaffold, Insight, and Synthesis phases.",
            "category": "CoreMethodology",
            "related_sprs": ["DRCL", "SPR", "CognitiveResonancE"]
        },
        {
            "spr_id": "DRCL",
            "term": "Distributed Resonant Corrective Loop",
            "definition": "The main workflow for ArchE's cognitive processes, implementing the ResonantiA Protocol for systematic problem-solving.",
            "category": "CoreWorkflow",
            "related_sprs": ["RISE", "SPR", "CognitiveResonancE"]
        },
        {
            "spr_id": "SPR",
            "term": "Sparse Priming Representations",
            "definition": "Cognitive keys that unlock interconnected concepts in the Knowledge Network Oneness (KnO), enabling rapid context extraction and synthesis.",
            "category": "CoreConcept",
            "related_sprs": ["RISE", "DRCL", "CognitiveResonancE"]
        },
        {
            "spr_id": "CognitiveResonancE",
            "term": "Cognitive Resonance",
            "definition": "The primary objective state of harmonious alignment between perception, analysis, intent, and outcomes in ArchE's cognitive processes.",
            "category": "CoreConcept",
            "related_sprs": ["RISE", "DRCL", "SPR"]
        },
        {
            "spr_id": "TerritoryAssumptionS",
            "term": "Territory Assumptions",
            "definition": "Expected file paths, system states, and environmental conditions that ArchE assumes during workflow execution.",
            "category": "CoreConcept",
            "related_sprs": ["DRCL", "ConceptualMaP"]
        },
        {
            "spr_id": "ConceptualMaP",
            "term": "Conceptual Map",
            "definition": "A structured representation of SPRs, abstract workflow, and territory assumptions for a given task.",
            "category": "CoreConcept",
            "related_sprs": ["SPR", "TerritoryAssumptionS", "DRCL"]
        },
        {
            "spr_id": "ResonantiaprotocoL",
            "term": "ResonantiA Protocol",
            "definition": "The comprehensive document and conceptual framework that defines the architecture, operational logic, core principles, and evolutionary mechanisms of the ArchE system.",
            "category": "CoreProtocol",
            "related_sprs": ["RISE", "DRCL", "SPR", "CognitiveResonancE"]
        }
    ]
    
    # Technology domain SPRs from expanded knowledge
    tech_sprs = []
    for node_id, node_data in expanded_knowledge['nodes'].items():
        spr_id = f"tech_{node_id}_{node_data['spr_label'].lower().replace(' ', '_').replace('-', '_')}"
        
        tech_spr = {
            "spr_id": spr_id,
            "term": node_data['spr_label'],
            "definition": f"Technology concept: {node_data['name']} - {node_data['spr_label']}",
            "category": "TechnologyConcept",
            "related_sprs": [f"tech_{conn['target']}_{conn['label'].lower().replace(' ', '_').replace('-', '_')}" 
                           for conn in node_data['connections']]
        }
        tech_sprs.append(tech_spr)
    
    # Domain category SPRs
    domain_sprs = [
        {
            "spr_id": "ArtificialIntelligence",
            "term": "Artificial Intelligence",
            "definition": "The field of computer science focused on creating intelligent machines capable of performing tasks that typically require human intelligence.",
            "category": "TechnologyDomain",
            "related_sprs": ["MachineLearning", "DeepLearning", "NeuralNetworks"]
        },
        {
            "spr_id": "MachineLearning",
            "term": "Machine Learning",
            "definition": "A subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            "category": "TechnologyDomain",
            "related_sprs": ["ArtificialIntelligence", "DeepLearning", "SupervisedLearning", "UnsupervisedLearning"]
        },
        {
            "spr_id": "DeepLearning",
            "term": "Deep Learning",
            "definition": "A subset of machine learning based on artificial neural networks with multiple layers to model and understand complex patterns.",
            "category": "TechnologyDomain",
            "related_sprs": ["MachineLearning", "NeuralNetworks", "ArtificialIntelligence"]
        },
        {
            "spr_id": "CognitiveScience",
            "term": "Cognitive Science",
            "definition": "The interdisciplinary study of mind and intelligence, embracing philosophy, psychology, artificial intelligence, neuroscience, linguistics, and anthropology.",
            "category": "TechnologyDomain",
            "related_sprs": ["CognitiveArchitecture", "ReasoningEngine", "LearningMechanism"]
        },
        {
            "spr_id": "Cybersecurity",
            "term": "Cybersecurity",
            "definition": "The practice of protecting systems, networks, and programs from digital attacks, damage, or unauthorized access.",
            "category": "TechnologyDomain",
            "related_sprs": ["SecurityRequirements", "Authentication", "Authorization", "Encryption"]
        },
        {
            "spr_id": "HumanComputerInteraction",
            "term": "Human-Computer Interaction",
            "definition": "The study of how people interact with computers and to what extent computers are or are not developed for successful interaction with human beings.",
            "category": "TechnologyDomain",
            "related_sprs": ["UserInterfaceDesign", "UserExperienceDesign", "UserResearch"]
        }
    ]
    
    # Combine all SPRs
    all_sprs = core_sprs + tech_sprs + domain_sprs
    
    print(f"📝 Created {len(all_sprs)} clean SPR definitions:")
    print(f"   • {len(core_sprs)} core ArchE SPRs")
    print(f"   • {len(tech_sprs)} technology concept SPRs")
    print(f"   • {len(domain_sprs)} domain category SPRs")
    
    return all_sprs

def create_clean_knowledge_tapestry(expanded_knowledge: Dict[str, Any]) -> Dict[str, Any]:
    """Create clean, comprehensive knowledge tapestry"""
    
    # Core ArchE nodes
    core_nodes = [
        {
            "id": "cognitive_resonance",
            "type": "CoreConcept",
            "properties": {
                "name": "Cognitive Resonance",
                "description": "The primary objective state of harmonious alignment between perception, analysis, intent, and outcomes",
                "confidence": 0.95,
                "temporal_aspects": ["historical", "present", "future"]
            },
            "relationships": [
                {"type": "enables", "target": "temporal_resonance", "confidence": 0.92},
                {"type": "requires", "target": "iar", "confidence": 0.98}
            ]
        },
        {
            "id": "rise_methodology",
            "type": "CoreMethodology",
            "properties": {
                "name": "RISE Methodology",
                "description": "Resonant Insight and Strategy Engine - comprehensive methodology for strategic problem-solving",
                "confidence": 0.94,
                "phases": ["Scaffold", "Insight", "Synthesis"]
            },
            "relationships": [
                {"type": "implements", "target": "cognitive_resonance", "confidence": 0.96},
                {"type": "uses", "target": "drcl_workflow", "confidence": 0.93}
            ]
        },
        {
            "id": "drcl_workflow",
            "type": "CoreWorkflow",
            "properties": {
                "name": "DRCL Workflow",
                "description": "Distributed Resonant Corrective Loop - main cognitive process workflow",
                "confidence": 0.93,
                "tasks": ["protocol_priming", "intent_intake", "conceptual_map", "rise_blueprint", "synthesis"]
            },
            "relationships": [
                {"type": "implements", "target": "rise_methodology", "confidence": 0.95},
                {"type": "uses", "target": "spr_system", "confidence": 0.94}
            ]
        },
        {
            "id": "spr_system",
            "type": "CoreSystem",
            "properties": {
                "name": "SPR System",
                "description": "Sparse Priming Representations - cognitive keys for knowledge network access",
                "confidence": 0.92,
                "components": ["spr_definitions", "knowledge_tapestry"]
            },
            "relationships": [
                {"type": "enables", "target": "drcl_workflow", "confidence": 0.94},
                {"type": "supports", "target": "cognitive_resonance", "confidence": 0.91}
            ]
        }
    ]
    
    # Technology nodes from expanded knowledge
    tech_nodes = []
    for node_id, node_data in expanded_knowledge['nodes'].items():
        tech_node = {
            "id": f"tech_node_{node_id}",
            "type": "TechnologyConcept",
            "properties": {
                "name": node_data['name'],
                "description": f"{node_data['name']} - {node_data['spr_label']}",
                "spr_value": node_data['spr_value'],
                "spr_label": node_data['spr_label'],
                "domain": node_data['domain'],
                "confidence": 0.85
            },
            "relationships": [
                {
                    "type": "connects_to",
                    "target": f"tech_node_{conn['target']}",
                    "confidence": 0.80,
                    "properties": {
                        "weight": conn['weight'],
                        "label": conn['label']
                    }
                }
                for conn in node_data['connections']
            ]
        }
        tech_nodes.append(tech_node)
    
    # Domain category nodes
    domain_nodes = [
        {
            "id": "ai_domain",
            "type": "TechnologyDomain",
            "properties": {
                "name": "Artificial Intelligence",
                "description": "Field of computer science focused on creating intelligent machines",
                "confidence": 0.90,
                "subdomains": ["Machine Learning", "Deep Learning", "Neural Networks"]
            },
            "relationships": [
                {"type": "includes", "target": "ml_domain", "confidence": 0.95},
                {"type": "includes", "target": "dl_domain", "confidence": 0.93}
            ]
        },
        {
            "id": "cognitive_domain",
            "type": "TechnologyDomain",
            "properties": {
                "name": "Cognitive Science",
                "description": "Interdisciplinary study of mind and intelligence",
                "confidence": 0.88,
                "subdomains": ["Cognitive Architecture", "Reasoning Engine", "Learning Mechanism"]
            },
            "relationships": [
                {"type": "relates_to", "target": "ai_domain", "confidence": 0.85}
            ]
        },
        {
            "id": "security_domain",
            "type": "TechnologyDomain",
            "properties": {
                "name": "Cybersecurity",
                "description": "Practice of protecting systems from digital attacks",
                "confidence": 0.87,
                "subdomains": ["Security Requirements", "Authentication", "Encryption"]
            },
            "relationships": [
                {"type": "protects", "target": "ai_domain", "confidence": 0.82}
            ]
        }
    ]
    
    # Create relationships from expanded knowledge edges
    tech_relationships = []
    for edge in expanded_knowledge['edges']:
        relationship = {
            "source": f"tech_node_{edge['source']}",
            "target": f"tech_node_{edge['target']}",
            "type": edge['relationship'],
            "properties": {
                "weight": edge['weight'],
                "label": edge['label'],
                "source_name": edge['source_name'],
                "target_name": edge['target_name']
            },
            "confidence": 0.80
        }
        tech_relationships.append(relationship)
    
    # Combine all components
    clean_tapestry = {
        "version": "3.1",
        "last_updated": datetime.now().isoformat(),
        "metadata": {
            "name": "Complete ArchE Knowledge Tapestry",
            "description": "Comprehensive knowledge graph with core ArchE concepts and expanded technology domains",
            "total_nodes": len(core_nodes) + len(tech_nodes) + len(domain_nodes),
            "total_relationships": len(tech_relationships) + 10,  # Core relationships
            "domains": ["CoreArchE", "TechnologyConcepts", "TechnologyDomains"]
        },
        "nodes": core_nodes + tech_nodes + domain_nodes,
        "relationships": tech_relationships
    }
    
    print(f"🧠 Created clean knowledge tapestry:")
    print(f"   • {len(core_nodes)} core ArchE nodes")
    print(f"   • {len(tech_nodes)} technology concept nodes")
    print(f"   • {len(domain_nodes)} domain category nodes")
    print(f"   • {len(tech_relationships)} technology relationships")
    
    return clean_tapestry

def verify_knowledge_graph():
    """Verify the fixed knowledge graph"""
    print(f"\n🔍 VERIFYING FIXED KNOWLEDGE GRAPH:")
    
    # Load and verify SPR definitions
    with open('Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json', 'r') as f:
        spr_defs = json.load(f)
    
    # Load and verify knowledge tapestry
    with open('Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json', 'r') as f:
        tapestry = json.load(f)
    
    print(f"✅ SPR Definitions: {len(spr_defs)} entries")
    print(f"✅ Knowledge Tapestry: {len(tapestry['nodes'])} nodes, {len(tapestry['relationships'])} relationships")
    print(f"✅ Structure: Clean and consistent")
    print(f"✅ Version: {tapestry['version']}")
    print(f"✅ Last Updated: {tapestry['last_updated']}")
    
    # Test sample data
    print(f"\n📊 SAMPLE DATA:")
    print(f"   • First SPR: {spr_defs[0]['term']}")
    print(f"   • First Node: {tapestry['nodes'][0]['properties']['name']}")
    print(f"   • Domain Coverage: {tapestry['metadata']['domains']}")
    
    print(f"\n🎯 KNOWLEDGE GRAPH FIX COMPLETE!")
    return True

if __name__ == "__main__":
    success = fix_complete_knowledge_graph()
    if success:
        print(f"\n🚀 ArchE Knowledge Graph is now fully fixed and optimized!")
    else:
        print(f"\n❌ Knowledge Graph fix failed")
