#!/usr/bin/env python3
"""
Integrate Expanded Knowledge into ArchE
Parses the extensive knowledge structure and integrates it into ArchE's knowledge graph manager
"""

import re
import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add ArchE to path
sys.path.append('Three_PointO_ArchE')

class ArchEKnowledgeIntegrator:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.spr_definitions = {}
        
    def parse_user_knowledge_input(self, text: str) -> Dict[str, Any]:
        """Parse the extensive knowledge structure from user input"""
        print("🔍 Parsing extensive knowledge structure from user input...")
        
        # Extract all nodes and relationships
        self._extract_comprehensive_structure(text)
        
        # Create the knowledge structure
        knowledge_structure = {
            "metadata": {
                "name": "Expanded Knowledge Graph",
                "description": "Comprehensive knowledge graph covering advanced technologies and domains",
                "created": datetime.now().isoformat(),
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "domains": self._identify_domains()
            },
            "nodes": self.nodes,
            "edges": self.edges,
            "spr_definitions": self._create_spr_definitions()
        }
        
        print(f"✅ Parsed {len(self.nodes)} nodes and {len(self.edges)} edges")
        return knowledge_structure
    
    def _extract_comprehensive_structure(self, text: str):
        """Extract all nodes and edges from the comprehensive text"""
        # Pattern to match node definitions
        node_pattern = r'Node (\d+): ([^\n]+)\n\nSPR: ([^,]+), "([^"]+)"'
        
        # Find all node definitions
        node_matches = re.findall(node_pattern, text)
        
        for match in node_matches:
            node_id = int(match[0])
            node_name = match[1].strip()
            spr_value = float(match[2])
            spr_label = match[3].strip()
            
            self.nodes[str(node_id)] = {
                "id": str(node_id),
                "name": node_name,
                "spr_value": spr_value,
                "spr_label": spr_label,
                "description": f"{node_name} - {spr_label}",
                "domain": self._classify_domain(node_name, spr_label),
                "connections": []
            }
        
        # Pattern to match edges
        edge_pattern = r'\* Node (\d+): ([^,]+), SPR: ([^,]+), "([^"]+)"'
        
        # Find all edge definitions
        edge_matches = re.findall(edge_pattern, text)
        
        for match in edge_matches:
            target_id = int(match[0])
            target_name = match[1].strip()
            target_spr = float(match[2])
            target_label = match[3].strip()
            
            # Find source node
            source_id = self._find_source_node_for_edge(text, target_id)
            
            if source_id and str(source_id) in self.nodes:
                edge = {
                    "source": str(source_id),
                    "target": str(target_id),
                    "relationship": "connects_to",
                    "weight": target_spr,
                    "label": target_label
                }
                self.edges.append(edge)
                
                # Add to source node's connections
                self.nodes[str(source_id)]["connections"].append({
                    "target": str(target_id),
                    "label": target_label,
                    "weight": target_spr
                })
    
    def _find_source_node_for_edge(self, text: str, target_id: int) -> int:
        """Find which node contains the edge to target_id"""
        # Look for the pattern where target_id appears as an edge
        pattern = rf'Node (\d+):[^\\n]*\\n\\nSPR:[^\\n]*\\n\\nEdges:[^\\n]*\\n\\n\\* Node {target_id}:'
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        return None
    
    def _classify_domain(self, name: str, label: str) -> str:
        """Classify nodes into domains"""
        name_lower = name.lower()
        
        if any(term in name_lower for term in ['neural', 'deep learning', 'machine learning', 'ai', 'ml']):
            return "Artificial Intelligence"
        elif any(term in name_lower for term in ['quantum', 'quantum computing']):
            return "Quantum Computing"
        elif any(term in name_lower for term in ['blockchain', 'distributed ledger', 'smart contract']):
            return "Blockchain Technology"
        elif any(term in name_lower for term in ['robotics', 'autonomous', 'robot']):
            return "Robotics & Automation"
        elif any(term in name_lower for term in ['iot', 'internet of things', 'sensor']):
            return "Internet of Things"
        elif any(term in name_lower for term in ['cybersecurity', 'security', 'threat']):
            return "Cybersecurity"
        elif any(term in name_lower for term in ['cognitive', 'neuroscience', 'brain']):
            return "Cognitive Science"
        elif any(term in name_lower for term in ['nano', 'nanotechnology', 'nanomaterials']):
            return "Nanotechnology"
        elif any(term in name_lower for term in ['bio', 'biotechnology', 'genetic']):
            return "Biotechnology"
        elif any(term in name_lower for term in ['data', 'analytics', 'visualization']):
            return "Data Science"
        elif any(term in name_lower for term in ['ar', 'vr', 'augmented', 'virtual']):
            return "Extended Reality"
        elif any(term in name_lower for term in ['5g', 'edge computing', 'networking']):
            return "Network Technology"
        else:
            return "General Technology"
    
    def _identify_domains(self) -> List[str]:
        """Identify all unique domains"""
        domains = set()
        for node in self.nodes.values():
            domains.add(node["domain"])
        return sorted(list(domains))
    
    def _create_spr_definitions(self) -> Dict[str, Any]:
        """Create SPR definitions for key concepts"""
        key_concepts = [
            "Artificial Intelligence", "Machine Learning", "Deep Learning",
            "Quantum Computing", "Blockchain", "Robotics", "IoT", 
            "Cybersecurity", "Cognitive Architecture", "Nanotechnology",
            "Biotechnology", "Data Science", "Extended Reality", 
            "Network Technology", "Human-Computer Interaction"
        ]
        
        spr_definitions = {}
        for concept in key_concepts:
            related_nodes = [node_id for node_id, node in self.nodes.items() 
                           if concept.lower() in node["name"].lower() or 
                              concept.lower() in node["domain"].lower()]
            
            spr_definitions[concept] = {
                "term": concept,
                "definition": f"Core concept in the expanded knowledge graph related to {concept}",
                "category": "Expanded Knowledge",
                "related_nodes": related_nodes
            }
        
        return spr_definitions
    
    def integrate_with_arche(self, knowledge_structure: Dict[str, Any]):
        """Integrate the knowledge structure with ArchE's knowledge graph manager"""
        try:
            from knowledge_graph_manager import KnowledgeGraphManager
            
            # Initialize KG manager
            kg = KnowledgeGraphManager(
                'Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json',
                'Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json',
                'specifications'
            )
            
            # Add new SPR definitions
            for term, definition in knowledge_structure["spr_definitions"].items():
                kg.add_spr_definition(term, definition["definition"], definition["category"])
            
            # Save the expanded knowledge graph
            expanded_kg_file = 'Three_PointO_ArchE/knowledge_graph/expanded_knowledge_tapestry.json'
            
            # Merge with existing knowledge tapestry
            existing_tapestry = kg.load_knowledge_tapestry()
            if existing_tapestry:
                existing_tapestry.update(knowledge_structure["nodes"])
            else:
                existing_tapestry = knowledge_structure["nodes"]
            
            # Save expanded tapestry
            with open(expanded_kg_file, 'w') as f:
                json.dump(existing_tapestry, f, indent=2)
            
            print(f"✅ Integrated {len(knowledge_structure['nodes'])} nodes into ArchE knowledge graph")
            print(f"💾 Saved expanded knowledge tapestry to {expanded_kg_file}")
            
            return True
            
        except ImportError as e:
            print(f"❌ Could not import ArchE knowledge graph manager: {e}")
            return False
        except Exception as e:
            print(f"❌ Error integrating with ArchE: {e}")
            return False

def main():
    """Main function to integrate expanded knowledge into ArchE"""
    integrator = ArchEKnowledgeIntegrator()
    
    # This would be the actual user input text
    # For now, we'll create a sample
    sample_input = """
    Node 1: System Overview
    
    SPR: 0.001, "System Overview"
    
    Edges:
    
    * Node 2: System Architecture, SPR: 0.010, "Architecture"
    * Node 3: System Requirements, SPR: 0.015, "Requirements"
    
    Node 2: System Architecture
    
    SPR: 0.010, "Architecture"
    
    Edges:
    
    * Node 4: Cognitive Architecture, SPR: 0.020, "Cognitive"
    * Node 5: Machine Learning, SPR: 0.025, "Learning"
    * Node 6: Natural Language Processing, SPR: 0.030, "NLP"
    """
    
    # Parse the knowledge structure
    knowledge_structure = integrator.parse_user_knowledge_input(sample_input)
    
    # Integrate with ArchE
    success = integrator.integrate_with_arche(knowledge_structure)
    
    if success:
        print("🎉 Successfully integrated expanded knowledge into ArchE!")
    else:
        print("❌ Failed to integrate knowledge into ArchE")
    
    return knowledge_structure

if __name__ == "__main__":
    main()

