#!/usr/bin/env python3
"""
SPR_compressor Knowledge Graph Parser
Parses the extensive SPR_compressor knowledge structure into ArchE-compatible format
"""

import re
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime

class SPRCompressorParser:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.node_counter = 0
        
    def parse_spr_structure(self, text: str) -> Dict[str, Any]:
        """Parse the SPR_compressor structure from text"""
        print("🔍 Parsing SPR_compressor knowledge structure...")
        
        # Extract nodes and their relationships
        self._extract_nodes_and_edges(text)
        
        # Create the knowledge graph structure
        knowledge_graph = {
            "metadata": {
                "name": "SPR_compressor Knowledge Graph",
                "description": "Comprehensive knowledge graph covering AI, ML, quantum computing, blockchain, and advanced technologies",
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
        return knowledge_graph
    
    def _extract_nodes_and_edges(self, text: str):
        """Extract nodes and edges from the text structure"""
        # Pattern to match node definitions
        node_pattern = r'Node (\d+): ([^\n]+)\n\nSPR: ([^,]+), "([^"]+)"'
        
        # Pattern to match edges
        edge_pattern = r'\* Node (\d+): ([^,]+), SPR: ([^,]+), "([^"]+)"'
        
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
        
        # Find all edge definitions
        edge_matches = re.findall(edge_pattern, text)
        
        for match in edge_matches:
            target_id = int(match[0])
            target_name = match[1].strip()
            target_spr = float(match[2])
            target_label = match[3].strip()
            
            # Find the source node (the one containing this edge)
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
        """Classify nodes into domains based on their names and labels"""
        name_lower = name.lower()
        label_lower = label.lower()
        
        # AI/ML domains
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
        """Identify all unique domains in the knowledge graph"""
        domains = set()
        for node in self.nodes.values():
            domains.add(node["domain"])
        return sorted(list(domains))
    
    def _create_spr_definitions(self) -> Dict[str, Any]:
        """Create SPR definitions for key concepts"""
        key_concepts = [
            "SPR_compressor", "Artificial Intelligence", "Machine Learning", 
            "Quantum Computing", "Blockchain", "Robotics", "IoT", 
            "Cybersecurity", "Cognitive Architecture", "Nanotechnology"
        ]
        
        spr_definitions = {}
        for concept in key_concepts:
            spr_definitions[concept] = {
                "term": concept,
                "definition": f"Core concept in the SPR_compressor knowledge graph related to {concept}",
                "category": "SPR_compressor",
                "related_nodes": [node_id for node_id, node in self.nodes.items() 
                                 if concept.lower() in node["name"].lower() or 
                                    concept.lower() in node["domain"].lower()]
            }
        
        return spr_definitions

def main():
    """Main function to parse and save the SPR_compressor knowledge graph"""
    parser = SPRCompressorParser()
    
    # Read the SPR_compressor text (this would be the user's input)
    # For now, we'll create a sample structure
    sample_text = """
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
    
    # Parse the structure
    knowledge_graph = parser.parse_spr_structure(sample_text)
    
    # Save to file
    output_file = "/media/newbu/3626C55326C514B1/Happier/spr_compressor_knowledge_graph.json"
    with open(output_file, 'w') as f:
        json.dump(knowledge_graph, f, indent=2)
    
    print(f"💾 Saved SPR_compressor knowledge graph to {output_file}")
    return knowledge_graph

if __name__ == "__main__":
    main()

