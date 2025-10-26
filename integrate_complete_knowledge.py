import json
import os
import sys
from datetime import datetime

# Add ArchE to path
sys.path.append('Three_PointO_ArchE')

from knowledge_graph_manager import KnowledgeGraphManager

def integrate_complete_knowledge():
    """Integrate the complete knowledge structure into ArchE's knowledge graph"""
    print("🚀 INTEGRATING COMPLETE KNOWLEDGE STRUCTURE INTO ARCH E")
    print("=" * 60)
    
    # Load the parsed knowledge structure
    with open('complete_knowledge_structure.json', 'r') as f:
        knowledge_data = json.load(f)
    
    print(f"📊 Loaded knowledge structure:")
    print(f"   • {knowledge_data['metadata']['total_nodes']} nodes")
    print(f"   • {knowledge_data['metadata']['total_edges']} edges")
    print(f"   • Parsing method: {knowledge_data['metadata']['parsing_method']}")
    
    # Initialize ArchE Knowledge Graph Manager
    kg_manager = KnowledgeGraphManager(
        'Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json',
        'Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json',
        'specifications'
    )
    
    print(f"\n🧠 Current ArchE knowledge graph:")
    print(f"   • SPR definitions: {len(kg_manager.spr_definitions)}")
    print(f"   • Knowledge tapestry nodes: {len(kg_manager.knowledge_tapestry.get('nodes', []))}")
    
    # Integrate nodes as SPR definitions
    integrated_sprs = 0
    for node_id, node_data in knowledge_data['nodes'].items():
        spr_id = f"expanded_{node_id}_{node_data['spr_label'].lower().replace(' ', '_')}"
        
        # Create SPR definition
        spr_definition = {
            'spr_id': spr_id,
            'term': node_data['spr_label'],
            'definition': f"Expanded knowledge concept: {node_data['name']} - {node_data['spr_label']}",
            'category': 'Expanded Knowledge',
            'related_sprs': [f"expanded_{conn['target']}_{conn['label'].lower().replace(' ', '_')}" 
                           for conn in node_data['connections']]
        }
        
        # Add to SPR definitions
        if isinstance(kg_manager.spr_definitions, list):
            kg_manager.spr_definitions.append(spr_definition)
        else:
            kg_manager.spr_definitions[spr_id] = spr_definition
        
        integrated_sprs += 1
    
    # Integrate edges as tapestry relationships
    integrated_relationships = 0
    for edge in knowledge_data['edges']:
        # Create relationship entry
        relationship = {
            'source': f"expanded_{edge['source']}",
            'target': f"expanded_{edge['target']}",
            'type': edge['relationship'],
            'properties': {
                'weight': edge['weight'],
                'label': edge['label'],
                'source_name': edge['source_name'],
                'target_name': edge['target_name']
            }
        }
        
        # Add to knowledge tapestry
        if 'relationships' not in kg_manager.knowledge_tapestry:
            kg_manager.knowledge_tapestry['relationships'] = []
        
        kg_manager.knowledge_tapestry['relationships'].append(relationship)
        integrated_relationships += 1
    
    # Save updated knowledge graph
    with open('Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json', 'w') as f:
        json.dump(kg_manager.spr_definitions, f, indent=2)
    
    with open('Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json', 'w') as f:
        json.dump(kg_manager.knowledge_tapestry, f, indent=2)
    
    print(f"\n✅ INTEGRATION COMPLETE:")
    print(f"   • Added {integrated_sprs} new SPR definitions")
    print(f"   • Added {integrated_relationships} new relationships")
    print(f"   • Updated ArchE knowledge graph files")
    
    # Show sample of integrated knowledge
    print(f"\n🔍 SAMPLE INTEGRATED KNOWLEDGE:")
    sample_nodes = list(knowledge_data['nodes'].keys())[:5]
    for node_id in sample_nodes:
        node = knowledge_data['nodes'][node_id]
        print(f"   • Node {node_id}: {node['name']} -> {node['spr_label']}")
        if node['connections']:
            print(f"     Connected to: {[conn['target_name'] for conn in node['connections'][:3]]}")
    
    print(f"\n🎯 ARCH E KNOWLEDGE EXPANSION SUCCESSFUL!")
    print(f"   • Total nodes in ArchE: {len(kg_manager.spr_definitions)}")
    print(f"   • Total relationships: {len(kg_manager.knowledge_tapestry.get('relationships', []))}")
    print(f"   • Ready for sophisticated multi-domain analysis")
    
    return True

if __name__ == "__main__":
    success = integrate_complete_knowledge()
    if success:
        print(f"\n🚀 ArchE is now equipped with expanded knowledge for advanced analysis!")
    else:
        print(f"\n❌ Integration failed")
