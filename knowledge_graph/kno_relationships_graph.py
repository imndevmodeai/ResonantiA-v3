"""
KnO Relationships Graph Builder
Creates a comprehensive visualization of how SPRs interconnect in the Knowledge Network Oneness
"""

import json
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import re

class KnoGraphBuilder:
    """Builds and analyzes the KnO relationships graph from SPR definitions"""
    
    def __init__(self, spr_definitions: List[Dict]):
        self.spr_definitions = spr_definitions
        self.nodes = {}
        self.edges = []
        self.relationship_types = defaultdict(lambda: defaultdict(list))
        self._build_graph()
    
    def _build_graph(self):
        """Build the relationship graph from SPR definitions"""
        
        # Extract all SPRs as nodes
        for spr in self.spr_definitions:
            spr_id = spr.get('spr_id')
            if not spr_id:
                continue
            
            self.nodes[spr_id] = {
                'term': spr.get('term', ''),
                'category': spr.get('category', 'Unknown'),
                'definition': spr.get('definition', ''),
                'relationships': spr.get('relationships', {}),
                'confidence': spr.get('relationships', {}).get('confidence', 'unknown')
            }
        
        # Extract relationships as edges
        for spr_id, node_data in self.nodes.items():
            relationships = node_data.get('relationships', {})
            
            # Parse all relationship fields
            for rel_type, targets in relationships.items():
                if not isinstance(targets, list):
                    targets = [targets]
                
                for target in targets:
                    if isinstance(target, str):
                        self._add_edge(spr_id, target, rel_type)
    
    def _add_edge(self, source: str, target: str, rel_type: str):
        """Add an edge between two SPRs"""
        if target in self.nodes:
            # Normalize relationship type
            normalized_type = self._normalize_rel_type(rel_type)
            self.edges.append({
                'source': source,
                'target': target,
                'type': normalized_type,
                'strength': self._calculate_edge_strength(source, target, normalized_type)
            })
            self.relationship_types[normalized_type][source].append(target)
    
    def _normalize_rel_type(self, rel_type: str) -> str:
        """Normalize relationship type to standard categories"""
        rel_type_lower = rel_type.lower()
        
        # Core relationships
        if 'type' in rel_type_lower:
            return 'type_of'
        if 'part_of' in rel_type_lower or 'is_a_part_of' in rel_type_lower:
            return 'part_of'
        if 'enables' in rel_type_lower or 'allows' in rel_type_lower:
            return 'enables'
        if 'requires' in rel_type_lower or 'needs' in rel_type_lower:
            return 'requires'
        if 'uses' in rel_type_lower or 'utilizes' in rel_type_lower:
            return 'uses'
        if 'supports' in rel_type_lower:
            return 'supports'
        if 'manages' in rel_type_lower:
            return 'manages'
        if 'produces' in rel_type_lower or 'outputs' in rel_type_lower:
            return 'produces'
        if 'triggers' in rel_type_lower:
            return 'triggers'
        if 'informs' in rel_type_lower:
            return 'informs'
        if 'implements' in rel_type_lower:
            return 'implements'
        if 'embodies' in rel_type_lower:
            return 'embodies'
        if 'comprises' in rel_type_lower or 'includes' in rel_type_lower:
            return 'comprises'
        if 'works_with' in rel_type_lower or 'integrates_with' in rel_type_lower:
            return 'integrates_with'
        
        return 'related_to'
    
    def _calculate_edge_strength(self, source: str, target: str, rel_type: str) -> float:
        """Calculate edge strength based on relationship type"""
        strength_map = {
            'part_of': 0.95,
            'type_of': 0.9,
            'enables': 0.85,
            'requires': 0.85,
            'manages': 0.9,
            'produces': 0.8,
            'implements': 0.75,
            'comprises': 0.8,
            'uses': 0.7,
            'supports': 0.7,
            'integrates_with': 0.75,
            'related_to': 0.5
        }
        return strength_map.get(rel_type, 0.5)
    
    def get_graph_metrics(self) -> Dict:
        """Get comprehensive graph metrics"""
        # Calculate centrality measures
        in_degree = Counter()
        out_degree = Counter()
        
        for edge in self.edges:
            out_degree[edge['source']] += 1
            in_degree[edge['target']] += 1
        
        # Find hubs (high connectivity)
        total_degree = {node: in_degree[node] + out_degree[node] for node in self.nodes.keys()}
        hubs = sorted(total_degree.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Category distribution
        categories = Counter([node['category'] for node in self.nodes.values()])
        
        # Relationship type distribution
        rel_type_counts = Counter([edge['type'] for edge in self.edges])
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'categories': dict(categories),
            'relationship_types': dict(rel_type_counts),
            'top_hubs': [(spr_id, degree) for spr_id, degree in hubs],
            'density': len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1)) if len(self.nodes) > 1 else 0,
            'average_degree': sum(total_degree.values()) / len(self.nodes) if self.nodes else 0
        }
    
    def export_graph_data(self) -> Dict:
        """Export graph data for visualization"""
        return {
            'nodes': [
                {
                    'id': spr_id,
                    'label': node_data.get('term', spr_id),
                    'category': node_data.get('category', 'Unknown'),
                    'definition': node_data.get('definition', ''),
                    'confidence': node_data.get('confidence', 'unknown')
                }
                for spr_id, node_data in self.nodes.items()
            ],
            'edges': self.edges,
            'metadata': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'relationship_types': list(set([e['type'] for e in self.edges]))
            }
        }
    
    def get_network_analysis(self) -> Dict:
        """Perform network analysis on the graph"""
        # Find core components (highly connected)
        core_components = []
        for spr_id, node in self.nodes.items():
            connections = [e for e in self.edges if e['source'] == spr_id or e['target'] == spr_id]
            core_components.append({
                'spr_id': spr_id,
                'term': node.get('term'),
                'connections': len(connections),
                'categories': self._get_linked_categories(spr_id)
            })
        
        core_components.sort(key=lambda x: x['connections'], reverse=True)
        
        # Find bridge nodes (connect different areas)
        category_bridges = self._find_category_bridges()
        
        return {
            'core_components': core_components[:30],
            'category_bridges': category_bridges,
            'relationship_analysis': self._analyze_relationships()
        }
    
    def _get_linked_categories(self, spr_id: str) -> Dict[str, int]:
        """Get categories of linked nodes"""
        linked_categories = Counter()
        for edge in self.edges:
            if edge['source'] == spr_id:
                target_data = self.nodes.get(edge['target'], {})
                linked_categories[target_data.get('category', 'Unknown')] += 1
            elif edge['target'] == spr_id:
                source_data = self.nodes.get(edge['source'], {})
                linked_categories[source_data.get('category', 'Unknown')] += 1
        return dict(linked_categories)
    
    def _find_category_bridges(self) -> List[Dict]:
        """Find SPRs that bridge different categories"""
        bridges = []
        for spr_id, node in self.nodes.items():
            linked_cats = set()
            for edge in self.edges:
                if edge['source'] == spr_id:
                    target_cat = self.nodes.get(edge['target'], {}).get('category', 'Unknown')
                    linked_cats.add(target_cat)
                elif edge['target'] == spr_id:
                    source_cat = self.nodes.get(edge['source'], {}).get('category', 'Unknown')
                    linked_cats.add(source_cat)
            
            if len(linked_cats) > 1:
                bridges.append({
                    'spr_id': spr_id,
                    'term': node.get('term'),
                    'bridged_categories': list(linked_cats),
                    'bridge_span': len(linked_cats)
                })
        
        bridges.sort(key=lambda x: x['bridge_span'], reverse=True)
        return bridges[:20]
    
    def _analyze_relationships(self) -> Dict:
        """Analyze the types of relationships"""
        analysis = {
            'most_common_relations': Counter([e['type'] for e in self.edges]).most_common(10),
            'strongest_connections': sorted(self.edges, key=lambda e: e['strength'], reverse=True)[:20],
            'relationship_patterns': self._analyze_patterns()
        }
        return analysis
    
    def _analyze_patterns(self) -> Dict:
        """Analyze relationship patterns"""
        # Find circular dependencies
        cycles = self._find_cycles()
        
        # Find hierarchical structures
        hierarchies = self._find_hierarchies()
        
        return {
            'detected_cycles': len(cycles) > 0,
            'hierarchical_depth': self._calculate_max_depth(hierarchies),
            'cycle_count': len(cycles) if cycles else 0
        }
    
    def _find_cycles(self) -> List[List[str]]:
        """Find circular relationships (simplified)"""
        # This is a simplified cycle detection
        visited = set()
        cycles = []
        
        def dfs(node, path):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            for edge in self.edges:
                if edge['source'] == node:
                    dfs(edge['target'], path + [node])
                elif edge['target'] == node:
                    dfs(edge['source'], path + [node])
        
        for spr_id in self.nodes:
            if spr_id not in visited:
                dfs(spr_id, [])
        
        return cycles[:5]  # Limit to first 5 cycles
    
    def _find_hierarchies(self) -> List[Tuple[str, int]]:
        """Find hierarchical structures (nodes with clear parent-child relationships)"""
        hierarchies = []
        for spr_id, node in self.nodes.items():
            # Count 'part_of' and 'type_of' relationships
            has_parent = any(e['target'] == spr_id and e['type'] in ['part_of', 'type_of'] 
                           for e in self.edges)
            has_children = any(e['source'] == spr_id and e['type'] in ['comprises', 'part_of']
                             for e in self.edges)
            
            if has_parent or has_children:
                hierarchies.append((spr_id, 1 if has_parent else 0))
        
        return hierarchies
    
    def _calculate_max_depth(self, hierarchies: List[Tuple[str, int]]) -> int:
        """Calculate maximum depth of hierarchies"""
        if not hierarchies:
            return 0
        
        # Simplified depth calculation
        depth_map = {}
        for spr_id, _ in hierarchies:
            depth = 0
            for edge in self.edges:
                if edge['target'] == spr_id and edge['type'] in ['part_of', 'type_of']:
                    depth += 1
                    break
            depth_map[spr_id] = depth
        
        return max(depth_map.values()) if depth_map else 0


def build_kno_graph(spr_definitions: List[Dict]) -> KnoGraphBuilder:
    """Build the KnO graph from SPR definitions"""
    return KnoGraphBuilder(spr_definitions)


# Main execution
if __name__ == "__main__":
    import sys
    
    # Load SPR definitions
    try:
        with open('knowledge_graph/spr_definitions_tv.json', 'r') as f:
            spr_definitions = json.load(f)
        
        # Build graph
        graph = build_kno_graph(spr_definitions)
        
        # Get metrics
        metrics = graph.get_graph_metrics()
        analysis = graph.get_network_analysis()
        
        # Export for visualization
        graph_data = graph.export_graph_data()
        
        print("=" * 80)
        print("KNOWLEDGE NETWORK ONENESS (KnO) RELATIONSHIPS GRAPH")
        print("=" * 80)
        print(f"\n📊 GRAPH METRICS:")
        print(f"   Total SPRs: {metrics['total_nodes']}")
        print(f"   Total Relationships: {metrics['total_edges']}")
        print(f"   Graph Density: {metrics['density']:.4f}")
        print(f"   Average Connections: {metrics['average_degree']:.2f}")
        
        print(f"\n🏷️  CATEGORIES ({len(metrics['categories'])}):")
        for cat, count in sorted(metrics['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {cat}: {count}")
        
        print(f"\n🔗 RELATIONSHIP TYPES ({len(metrics['relationship_types'])}):")
        for rel_type, count in sorted(metrics['relationship_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {rel_type}: {count}")
        
        print(f"\n⭐ TOP HUBS (Most Connected SPRs):")
        for i, (spr_id, degree) in enumerate(metrics['top_hubs'][:15], 1):
            node = graph.nodes.get(spr_id, {})
            print(f"   {i}. {spr_id} ({node.get('term', 'Unknown')}): {degree} connections")
        
        print(f"\n🌉 CATEGORY BRIDGES (SPRs Connecting Multiple Categories):")
        for bridge in analysis['category_bridges'][:10]:
            print(f"   {bridge['spr_id']} bridges {bridge['bridge_span']} categories: {', '.join(bridge['bridged_categories'])}")
        
        print(f"\n🔗 RELATIONSHIP ANALYSIS:")
        print(f"   Most Common Relations: {analysis['relationship_analysis']['most_common_relations'][:5]}")
        
        # Export graph data
        with open('knowledge_graph/kno_graph_data.json', 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"\n✅ Graph data exported to: knowledge_graph/kno_graph_data.json")
        print("=" * 80)
        
    except FileNotFoundError:
        print("❌ Error: spr_definitions_tv.json not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        sys.exit(1)


