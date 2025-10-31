#!/usr/bin/env python3
"""
ArchE Knowledge Integration
Integrates the extensive knowledge structure directly into ArchE's knowledge graph files
"""

import re
import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

class ArchEKnowledgeIntegration:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.spr_definitions = {}
        
    def parse_extensive_knowledge(self, text: str) -> Dict[str, Any]:
        """Parse the extensive knowledge structure from user input"""
        print("🔍 Parsing extensive knowledge structure...")
        
        # Extract all nodes and relationships
        self._extract_all_nodes_and_edges(text)
        
        # Create comprehensive knowledge structure
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
            "spr_definitions": self._create_comprehensive_spr_definitions()
        }
        
        print(f"✅ Parsed {len(self.nodes)} nodes and {len(self.edges)} edges")
        return knowledge_structure
    
    def _extract_all_nodes_and_edges(self, text: str):
        """Extract all nodes and edges from the comprehensive text"""
        # Enhanced pattern to match node definitions
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
    
    def _create_comprehensive_spr_definitions(self) -> Dict[str, Any]:
        """Create comprehensive SPR definitions for key concepts"""
        key_concepts = [
            "Artificial Intelligence", "Machine Learning", "Deep Learning",
            "Quantum Computing", "Blockchain", "Robotics", "IoT", 
            "Cybersecurity", "Cognitive Architecture", "Nanotechnology",
            "Biotechnology", "Data Science", "Extended Reality", 
            "Network Technology", "Human-Computer Interaction",
            "Environmental Science", "Social Sciences", "Neural Networks",
            "Computer Vision", "Natural Language Processing", "Swarm Intelligence",
            "Explainability", "Transparency", "Quantum Algorithms",
            "Smart Contracts", "Autonomous Systems", "Edge Computing"
        ]
        
        spr_definitions = {}
        for concept in key_concepts:
            related_nodes = [node_id for node_id, node in self.nodes.items()
                           if (concept.lower() in node["name"].lower() or 
                               concept.lower() in node["domain"].lower())]
            
            spr_definitions[concept] = {
                "term": concept,
                "definition": f"Core concept in the expanded knowledge graph related to {concept}",
                "category": "Expanded Knowledge",
                "related_nodes": related_nodes
            }
        
        return spr_definitions
    
    def integrate_with_arche_files(self, knowledge_structure: Dict[str, Any]):
        """Integrate the knowledge structure with ArchE's knowledge graph files"""
        try:
            # Paths to ArchE knowledge graph files
            spr_definitions_path = 'Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json'
            knowledge_tapestry_path = 'Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json'
            
            # Load existing SPR definitions
            existing_spr_definitions = []
            if os.path.exists(spr_definitions_path):
                with open(spr_definitions_path, 'r') as f:
                    existing_spr_definitions = json.load(f)
            
            # Add new SPR definitions
            for term, definition in knowledge_structure["spr_definitions"].items():
                new_spr = {
                    "spr_id": term,
                    "term": definition["term"],
                    "definition": definition["definition"],
                    "category": definition["category"],
                    "related_nodes": definition["related_nodes"]
                }
                existing_spr_definitions.append(new_spr)
            
            # Save updated SPR definitions
            with open(spr_definitions_path, 'w') as f:
                json.dump(existing_spr_definitions, f, indent=2)
            
            # Load existing knowledge tapestry
            existing_tapestry = {}
            if os.path.exists(knowledge_tapestry_path):
                with open(knowledge_tapestry_path, 'r') as f:
                    existing_tapestry = json.load(f)
            
            # Merge with existing knowledge tapestry
            existing_tapestry.update(knowledge_structure["nodes"])
            
            # Save updated knowledge tapestry
            with open(knowledge_tapestry_path, 'w') as f:
                json.dump(existing_tapestry, f, indent=2)
            
            print(f"✅ Integrated {len(knowledge_structure['nodes'])} nodes into ArchE knowledge graph")
            print(f"💾 Updated SPR definitions: {spr_definitions_path}")
            print(f"💾 Updated knowledge tapestry: {knowledge_tapestry_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error integrating with ArchE files: {e}")
            return False

def main():
    """Main function to integrate expanded knowledge into ArchE"""
    integrator = ArchEKnowledgeIntegration()
    
    # Sample input for testing (in practice, this would be the full user input)
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
    knowledge_structure = integrator.parse_extensive_knowledge(sample_input)
    
    # Integrate with ArchE files
    success = integrator.integrate_with_arche_files(knowledge_structure)
    
    if success:
        print("🎉 Successfully integrated expanded knowledge into ArchE!")
    else:
        print("❌ Failed to integrate knowledge into ArchE")
    
    return knowledge_structure

if __name__ == "__main__":
    main()

