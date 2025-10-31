#!/usr/bin/env python3
"""
Knowledge Expansion Parser
Parses the extensive knowledge structure and integrates it into ArchE's knowledge graph
"""

import re
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime

class KnowledgeExpansionParser:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.spr_definitions = {}
        
    def parse_knowledge_structure(self, text: str) -> Dict[str, Any]:
        """Parse the extensive knowledge structure from text"""
        print("🔍 Parsing extensive knowledge structure...")
        
        # Extract all nodes and their relationships
        self._extract_all_nodes_and_edges(text)
        
        # Create comprehensive knowledge graph
        knowledge_graph = {
            "metadata": {
                "name": "Expanded Knowledge Graph",
                "description": "Comprehensive knowledge graph covering AI, ML, quantum computing, blockchain, robotics, IoT, and advanced technologies",
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
        return knowledge_graph
    
    def _extract_all_nodes_and_edges(self, text: str):
        """Extract all nodes and edges from the comprehensive text structure"""
        # Enhanced pattern to match node definitions with various formats
        node_patterns = [
            r'Node (\d+): ([^\n]+)\n\nSPR: ([^,]+), "([^"]+)"',
            r'Node (\d+): ([^\n]+)\n\nSPR: ([^,]+), "([^"]+)"\n\nEdges:',
            r'Node (\d+): ([^\n]+)\n\nSPR: ([^,]+), "([^"]+)"\n\nEdges:\n\n'
        ]
        
        # Find all node definitions
        all_nodes = []
        for pattern in node_patterns:
            matches = re.findall(pattern, text)
            all_nodes.extend(matches)
        
        # Process each node
        for match in all_nodes:
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
                "connections": [],
                "category": self._categorize_node(node_name, spr_label)
            }
        
        # Extract edges with multiple patterns
        edge_patterns = [
            r'\* Node (\d+): ([^,]+), SPR: ([^,]+), "([^"]+)"',
            r'\t\+ Node (\d+): ([^,]+), SPR: ([^,]+), "([^"]+)"',
            r'\t+ Node (\d+): ([^,]+), SPR: ([^,]+), "([^"]+)"'
        ]
        
        all_edges = []
        for pattern in edge_patterns:
            matches = re.findall(pattern, text)
            all_edges.extend(matches)
        
        # Process edges and find their sources
        for match in all_edges:
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
        # Look backwards from the target_id to find the source node
        target_pattern = rf'Node {target_id}:'
        target_pos = text.find(target_pattern)
        
        if target_pos == -1:
            return None
        
        # Look backwards for the previous node definition
        before_target = text[:target_pos]
        node_pattern = r'Node (\d+):[^\\n]*\\n\\nSPR:[^\\n]*\\n\\nEdges:'
        matches = re.findall(node_pattern, before_target)
        
        if matches:
            return int(matches[-1])  # Return the last (closest) match
        
        return None
    
    def _classify_domain(self, name: str, label: str) -> str:
        """Classify nodes into domains based on their names and labels"""
        name_lower = name.lower()
        label_lower = label.lower()
        
        # AI/ML domains
        if any(term in name_lower for term in ['neural', 'deep learning', 'machine learning', 'ai', 'ml', 'artificial intelligence']):
            return "Artificial Intelligence"
        elif any(term in name_lower for term in ['quantum', 'quantum computing', 'quantum simulation']):
            return "Quantum Computing"
        elif any(term in name_lower for term in ['blockchain', 'distributed ledger', 'smart contract', 'cryptocurrency']):
            return "Blockchain Technology"
        elif any(term in name_lower for term in ['robotics', 'autonomous', 'robot', 'swarm robotics']):
            return "Robotics & Automation"
        elif any(term in name_lower for term in ['iot', 'internet of things', 'sensor', 'actuator']):
            return "Internet of Things"
        elif any(term in name_lower for term in ['cybersecurity', 'security', 'threat', 'encryption']):
            return "Cybersecurity"
        elif any(term in name_lower for term in ['cognitive', 'neuroscience', 'brain', 'neuro']):
            return "Cognitive Science"
        elif any(term in name_lower for term in ['nano', 'nanotechnology', 'nanomaterials', 'nanodevices']):
            return "Nanotechnology"
        elif any(term in name_lower for term in ['bio', 'biotechnology', 'genetic', 'synthetic biology']):
            return "Biotechnology"
        elif any(term in name_lower for term in ['data', 'analytics', 'visualization', 'mining']):
            return "Data Science"
        elif any(term in name_lower for term in ['ar', 'vr', 'augmented', 'virtual', 'mixed reality']):
            return "Extended Reality"
        elif any(term in name_lower for term in ['5g', 'edge computing', 'networking', 'communication']):
            return "Network Technology"
        elif any(term in name_lower for term in ['human', 'computer', 'interaction', 'user experience']):
            return "Human-Computer Interaction"
        elif any(term in name_lower for term in ['environmental', 'sustainability', 'climate', 'renewable']):
            return "Environmental Science"
        elif any(term in name_lower for term in ['social', 'psychology', 'sociology', 'anthropology']):
            return "Social Sciences"
        else:
            return "General Technology"
    
    def _categorize_node(self, name: str, label: str) -> str:
        """Categorize nodes into more specific categories"""
        name_lower = name.lower()
        
        if 'algorithm' in name_lower:
            return "Algorithm"
        elif 'network' in name_lower:
            return "Network"
        elif 'system' in name_lower:
            return "System"
        elif 'model' in name_lower:
            return "Model"
        elif 'architecture' in name_lower:
            return "Architecture"
        elif 'framework' in name_lower:
            return "Framework"
        elif 'technology' in name_lower:
            return "Technology"
        elif 'analysis' in name_lower:
            return "Analysis"
        elif 'learning' in name_lower:
            return "Learning"
        elif 'processing' in name_lower:
            return "Processing"
        else:
            return "Concept"
    
    def _identify_domains(self) -> List[str]:
        """Identify all unique domains in the knowledge graph"""
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
            related_nodes = []
            for node_id, node in self.nodes.items():
                if (concept.lower() in node["name"].lower() or 
                    concept.lower() in node["domain"].lower() or
                    concept.lower() in node["category"].lower()):
                    related_nodes.append(node_id)
            
            spr_definitions[concept] = {
                "term": concept,
                "definition": f"Core concept in the expanded knowledge graph related to {concept}",
                "category": "Expanded Knowledge",
                "related_nodes": related_nodes,
                "domain": self._classify_domain(concept, concept)
            }
        
        return spr_definitions

def main():
    """Main function to parse and save the expanded knowledge graph"""
    parser = KnowledgeExpansionParser()
    
    # For demonstration, we'll create a sample structure
    # In practice, this would parse the full user input
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
    knowledge_graph = parser.parse_knowledge_structure(sample_text)
    
    # Save to file
    output_file = "/media/newbu/3626C55326C514B1/Happier/expanded_knowledge_graph.json"
    with open(output_file, 'w') as f:
        json.dump(knowledge_graph, f, indent=2)
    
    print(f"💾 Saved expanded knowledge graph to {output_file}")
    return knowledge_graph

if __name__ == "__main__":
    main()

