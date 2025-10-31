import re
import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

def parse_complete_knowledge_structure():
    """Parse the complete knowledge structure with proper edge handling"""
    print("🔍 Parsing complete knowledge structure...")
    
    # The extensive knowledge structure from the user's input
    user_input = """Node 1: System Overview
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
Node 3: System Requirements
SPR: 0.015, "Requirements"
Edges:
* Node 7: Functional Requirements, SPR: 0.035, "Functional"
* Node 8: Performance Requirements, SPR: 0.040, "Performance"
* Node 9: Security Requirements, SPR: 0.045, "Security"
Node 4: Cognitive Architecture
SPR: 0.020, "Cognitive"
Edges:
* Node 10: Knowledge Graph, SPR: 0.050, "Knowledge"
* Node 11: Reasoning Engine, SPR: 0.055, "Reasoning"
* Node 12: Learning Mechanism, SPR: 0.060, "Learning"
Node 5: Machine Learning
SPR: 0.025, "Learning"
Edges:
* Node 13: Supervised Learning, SPR: 0.065, "Supervised"
* Node 14: Unsupervised Learning, SPR: 0.070, "Unsupervised"
* Node 15: Reinforcement Learning, SPR: 0.075, "Reinforcement"
Node 6: Natural Language Processing
SPR: 0.030, "NLP"
Edges:
* Node 16: Text Preprocessing, SPR: 0.080, "Preprocessing"
* Node 17: Part-of-Speech Tagging, SPR: 0.085, "POS"
* Node 18: Named Entity Recognition, SPR: 0.090, "NER"
Node 7: Functional Requirements
SPR: 0.035, "Functional"
Edges:
* Node 19: User Interface, SPR: 0.095, "UI"
* Node 20: User Experience, SPR: 0.100, "UX"
* Node 21: Functionality, SPR: 0.105, "Functionality"
Node 8: Performance Requirements
SPR: 0.040, "Performance"
Edges:
* Node 22: Speed, SPR: 0.110, "Speed"
* Node 23: Accuracy, SPR: 0.115, "Accuracy"
* Node 24: Scalability, SPR: 0.120, "Scalability"
Node 9: Security Requirements
SPR: 0.045, "Security"
Edges:
* Node 25: Authentication, SPR: 0.125, "Authentication"
* Node 26: Authorization, SPR: 0.130, "Authorization"
* Node 27: Encryption, SPR: 0.135, "Encryption"
Node 10: Knowledge Graph
SPR: 0.050, "Knowledge"
Edges:
* Node 28: Node Creation, SPR: 0.140, "Node"
* Node 29: Edge Creation, SPR: 0.145, "Edge"
* Node 30: Relationship Creation, SPR: 0.150, "Relationship"
Node 11: Reasoning Engine
SPR: 0.055, "Reasoning"
Edges:
* Node 31: Rule-Based Reasoning, SPR: 0.155, "Rule-Based"
* Node 32: Model-Based Reasoning, SPR: 0.160, "Model-Based"
* Node 33: Hybrid Reasoning, SPR: 0.165, "Hybrid"
Node 12: Learning Mechanism
SPR: 0.060, "Learning"
Edges:
* Node 34: Supervised Learning, SPR: 0.170, "Supervised"
* Node 35: Unsupervised Learning, SPR: 0.175, "Unsupervised"
* Node 36: Reinforcement Learning, SPR: 0.180, "Reinforcement"
Node 37: Natural Language Generation
SPR: 0.185, "NLG"
Edges:
* Node 38: Text Generation, SPR: 0.190, "Text"
* Node 39: Language Modeling, SPR: 0.195, "Language"
Node 38: Text Generation
SPR: 0.190, "Text"
Edges:
* Node 40: Sentence Generation, SPR: 0.200, "Sentence"
* Node 41: Paragraph Generation, SPR: 0.205, "Paragraph"
Node 39: Language Modeling
SPR: 0.195, "Language"
Edges:
* Node 42: Language Understanding, SPR: 0.210, "Understanding"
* Node 43: Language Generation, SPR: 0.215, "Generation"
Node 44: Dialogue Management System
SPR: 0.220, "DMS"
Edges:
* Node 45: Dialogue State Tracking, SPR: 0.225, "State"
* Node 46: Dialogue Policy, SPR: 0.230, "Policy"
Node 45: Dialogue State Tracking
SPR: 0.225, "State"
Edges:
* Node 47: User Intent Identification, SPR: 0.235, "Intent"
* Node 48: Dialogue Context Understanding, SPR: 0.240, "Context"
Node 46: Dialogue Policy
SPR: 0.230, "Policy"
Edges:
* Node 49: Response Generation, SPR: 0.245, "Response"
* Node 50: Dialogue Flow Control, SPR: 0.250, "Flow"
Node 51: Sentiment Analysis
SPR: 0.255, "Sentiment"
Edges:
* Node 52: Emotion Detection, SPR: 0.260, "Emotion"
* Node 53: Sentiment Classification, SPR: 0.265, "Classification"
Node 52: Emotion Detection
SPR: 0.260, "Emotion"
Edges:
* Node 54: Emotion Recognition, SPR: 0.270, "Recognition"
* Node 55: Emotion Understanding, SPR: 0.275, "Understanding"
Node 53: Sentiment Classification
SPR: 0.265, "Classification"
Edges:
* Node 56: Sentiment Labeling, SPR: 0.280, "Labeling"
* Node 57: Sentiment Ranking, SPR: 0.285, "Ranking"
Node 58: Knowledge Graph Embedding
SPR: 0.290, "KGE"
Edges:
* Node 59: Node Embedding, SPR: 0.295, "Node"
* Node 60: Edge Embedding, SPR: 0.300, "Edge"
Node 59: Node Embedding
SPR: 0.295, "Node"
Edges:
* Node 61: Node Representation Learning, SPR: 0.305, "Learning"
* Node 62: Node Classification, SPR: 0.310, "Classification"
Node 60: Edge Embedding
SPR: 0.300, "Edge"
Edges:
* Node 63: Edge Representation Learning, SPR: 0.315, "Learning"
* Node 64: Link Prediction, SPR: 0.320, "Prediction"
Node 65: Graph Neural Network
SPR: 0.325, "GNN"
Edges:
* Node 66: Node Representation Learning, SPR: 0.330, "Learning"
* Node 67: Edge Representation Learning, SPR: 0.335, "Learning"
Node 66: Node Representation Learning
SPR: 0.330, "Learning"
Edges:
* Node 68: Graph Convolutional Network, SPR: 0.340, "GCN"
* Node 69: Graph Attention Network, SPR: 0.345, "GAT"
Node 67: Edge Representation Learning
SPR: 0.335, "Learning"
Edges:
* Node 70: Edge Convolutional Network, SPR: 0.350, "ECN"
* Node 71: Edge Attention Network, SPR: 0.355, "EAT"
Node 72: Transfer Learning
SPR: 0.360, "TL"
Edges:
* Node 73: Domain Adaptation, SPR: 0.365, "Adaptation"
* Node 74: Task Adaptation, SPR: 0.370, "Adaptation"
Node 73: Domain Adaptation
SPR: 0.365, "Adaptation"
Edges:
* Node 75: Domain-Invariant Feature Learning, SPR: 0.375, "Learning"
* Node 76: Domain-Specific Feature Learning, SPR: 0.380, "Learning"
Node 74: Task Adaptation
SPR: 0.370, "Adaptation"
Edges:
* Node 77: Task-Invariant Feature Learning, SPR: 0.385, "Learning"
* Node 78: Task-Specific Feature Learning, SPR: 0.390, "Learning"
Node 79: Reinforcement Learning
SPR: 0.395, "RL"
Edges:
* Node 80: Policy Learning, SPR: 0.400, "Policy"
* Node 81: Value Learning, SPR: 0.405, "Value"
Node 80: Policy Learning
SPR: 0.400, "Policy"
Edges:
* Node 82: Policy Gradient Methods, SPR: 0.410, "PG"
* Node 83: Actor-Critic Methods, SPR: 0.415, "AC"
Node 81: Value Learning
SPR: 0.405, "Value"
Edges:
* Node 84: Value Iteration, SPR: 0.420, "VI"
* Node 85: Q-Learning, SPR: 0.425, "QL"
Node 86: Multi-Agent System
SPR: 0.430, "MAS"
Edges:
* Node 87: Agent Communication, SPR: 0.435, "Communication"
* Node 88: Agent Cooperation, SPR: 0.440, "Cooperation"
Node 87: Agent Communication
SPR: 0.435, "Communication"
Edges:
* Node 89: Message Passing, SPR: 0.445, "MP"
* Node 90: Broadcast Communication, SPR: 0.450, "BC"
Node 88: Agent Cooperation
SPR: 0.440, "Cooperation"
Edges:
* Node 91: Cooperative Game Theory, SPR: 0.455, "CGT"
* Node 92: Cooperative Learning, SPR: 0.460, "CL"
Node 93: Human-Computer Interaction
SPR: 0.465, "HCI"
Edges:
* Node 94: User Interface Design, SPR: 0.470, "UID"
* Node 95: User Experience Design, SPR: 0.475, "UXD"
Node 94: User Interface Design
SPR: 0.470, "UID"
Edges:
* Node 96: Graphical User Interface, SPR: 0.480, "GUI"
* Node 97: Voice User Interface, SPR: 0.485, "VUI"
Node 95: User Experience Design
SPR: 0.475, "UXD"
Edges:
* Node 98: User Research, SPR: 0.490, "UR"
* Node 99: User Testing, SPR: 0.495, "UT"
"""
    
    print("First lines:")
    for line in user_input.splitlines()[:10]:
        print(repr(line))
    
    nodes = {}
    edges = []
    
    # Use regex to find all node definitions
    node_pattern = r'Node (\d+): ([^\n]+)\n+SPR: ([^,]+), "([^"]+)"'
    node_matches = re.findall(node_pattern, user_input)
    
    print(f"Found {len(node_matches)} node matches")
    
    # Process each node
    for match in node_matches:
        node_id = int(match[0])
        node_name = match[1].strip()
        spr_value = float(match[2])
        spr_label = match[3].strip()
        
        nodes[str(node_id)] = {
            "id": str(node_id),
            "name": node_name,
            "spr_value": spr_value,
            "spr_label": spr_label,
            "description": f"{node_name} - {spr_label}",
            "domain": classify_domain(node_name, spr_label),
            "connections": []
        }
    
    # Now find all edges
    edge_pattern = r'\* Node (\d+): ([^,]+), SPR: ([^,]+), "([^"]+)"'
    edge_matches = re.findall(edge_pattern, user_input)
    
    print(f"Found {len(edge_matches)} edge matches")
    
    # Test for target 2
    target_id = 2
    pattern = rf'Node (\d+):[^\n]*\nSPR:[^\n]*\nEdges:[^\n]*\n+ \*  Node {target_id}:'
    match = re.search(pattern, user_input)
    print("Test match for target 2:", match)
    if match:
        print("Source for 2:", match.group(1))
    
    # Process edges and find their sources
    for match in edge_matches:
        target_id = int(match[0])
        target_name = match[1].strip()
        target_spr = float(match[2])
        target_label = match[3].strip()
        
        # Find source node by looking backwards from this edge
        source_id = find_source_node_for_edge(user_input, target_id)
        
        if source_id and str(source_id) in nodes:
            edge = {
                "source": str(source_id),
                "target": str(target_id),
                "relationship": "connects_to",
                "weight": target_spr,
                "label": target_label
            }
            edges.append(edge)
            
            # Add to source node's connections
            nodes[str(source_id)]["connections"].append({
                "target": str(target_id),
                "label": target_label,
                "weight": target_spr
            })
    
    # Create comprehensive knowledge structure
    knowledge_structure = {
        "metadata": {
            "name": "Expanded Knowledge Graph",
            "description": "Comprehensive knowledge graph covering advanced technologies and domains",
            "created": datetime.now().isoformat(),
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "domains": identify_domains(nodes)
        },
        "nodes": nodes,
        "edges": edges,
        "spr_definitions": create_comprehensive_spr_definitions(nodes)
    }
    
    print(f"✅ Parsed {len(nodes)} nodes and {len(edges)} edges")
    return knowledge_structure

def find_source_node_for_edge(text: str, target_id: int) -> int:
    """Find which node contains the edge to target_id"""
    # Look for the pattern where target_id appears as an edge
    pattern = rf'Node (\d+):[^\n]*\nSPR:[^\n]*\nEdges:[^\n]*\n+ \*  Node {target_id}:'
    match = re.search(pattern, text)
    if match:
        return int(match.group(1))
    return None

def classify_domain(name: str, label: str) -> str:
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
    elif any(term in name_lower for term in ['human', 'computer', 'interaction', 'user']):
        return "Human-Computer Interaction"
    else:
        return "General Technology"

def identify_domains(nodes: Dict[str, Any]) -> List[str]:
    """Identify all unique domains"""
    domains = set()
    for node in nodes.values():
        domains.add(node["domain"])
    return sorted(list(domains))

def create_comprehensive_spr_definitions(nodes: Dict[str, Any]) -> Dict[str, Any]:
    """Create comprehensive SPR definitions for key concepts"""
    key_concepts = [
        "Artificial Intelligence", "Machine Learning", "Deep Learning",
        "Quantum Computing", "Blockchain", "Robotics", "IoT",
        "Cybersecurity", "Cognitive Architecture", "Nanotechnology",
        "Biotechnology", "Data Science", "Extended Reality",
        "Network Technology", "Human-Computer Interaction",
        "Natural Language Processing", "Knowledge Graph", "Graph Neural Networks",
        "Transfer Learning", "Reinforcement Learning", "Multi-Agent Systems",
        "Sentiment Analysis", "Dialogue Management", "User Experience Design"
    ]
    
    spr_definitions = {}
    for concept in key_concepts:
        related_nodes = [node_id for node_id, node in nodes.items()
                       if (concept.lower() in node["name"].lower() or
                           concept.lower() in node["domain"].lower())]
        
        spr_definitions[concept] = {
            "term": concept,
            "definition": f"Core concept in the expanded knowledge graph related to {concept}",
            "category": "Expanded Knowledge",
            "related_nodes": related_nodes
        }
    
    return spr_definitions

if __name__ == "__main__":
    knowledge_structure = parse_complete_knowledge_structure()
    print(json.dumps(knowledge_structure, indent=2))

