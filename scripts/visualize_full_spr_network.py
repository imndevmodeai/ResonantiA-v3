#!/usr/bin/env python3
"""
Full SPR Network Visualization
Creates comprehensive visualization of ALL SPRs and their relationships
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class FullSPRNetworkVisualizer:
    """Visualizes the complete SPR network with all relationships"""
    
    def __init__(self):
        self.project_root = project_root
        self.spr_file = project_root / "knowledge_graph" / "spr_definitions_tv.json"
        self.mapping_file = project_root / "knowledge_graph" / "spr_component_mapping.json"
        self.sprs = {}
        self.component_mappings = {}
        
    def load_data(self):
        """Load all SPRs and component mappings"""
        print("📦 Loading SPR data...")
        
        # Load all SPRs
        with open(self.spr_file, 'r', encoding='utf-8') as f:
            spr_data = json.load(f)
        
        for spr in spr_data:
            spr_id = spr.get('spr_id')
            if spr_id:
                self.sprs[spr_id] = spr
        
        print(f"  ✅ Loaded {len(self.sprs)} SPRs")
        
        # Load component mappings
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            self.component_mappings = {
                'workflows': mapping_data.get('workflow_mappings', {}),
                'actions': mapping_data.get('action_mappings', {}),
                'agents': mapping_data.get('agent_mappings', {}),
                'orchestrators': mapping_data.get('orchestrator_mappings', {}),
                'engines': mapping_data.get('engine_mappings', {})
            }
            print(f"  ✅ Loaded component mappings")
    
    def extract_spr_relationships(self):
        """Extract relationships between SPRs"""
        print("🔗 Extracting SPR relationships...")
        
        relationships = []
        spr_categories = defaultdict(list)
        
        for spr_id, spr_data in self.sprs.items():
            # Categorize SPRs
            category = spr_data.get('category', 'Unknown')
            spr_categories[category].append(spr_id)
            
            # Extract relationships
            rels = spr_data.get('relationships', {})
            if isinstance(rels, dict):
                # Check for related SPRs
                for key, value in rels.items():
                    if key in ['part_of', 'uses', 'requires', 'related_to', 'implements', 'uses_library']:
                        if isinstance(value, list):
                            for related in value:
                                if isinstance(related, str) and related in self.sprs:
                                    relationships.append({
                                        'source': spr_id,
                                        'target': related,
                                        'type': key
                                    })
                        elif isinstance(value, str) and value in self.sprs:
                            relationships.append({
                                'source': spr_id,
                                'target': value,
                                'type': key
                            })
        
        print(f"  ✅ Found {len(relationships)} SPR relationships")
        print(f"  ✅ Categorized into {len(spr_categories)} categories")
        
        return relationships, spr_categories
    
    def generate_comprehensive_visualization(self):
        """Generate comprehensive HTML visualization with all SPRs"""
        print("🎨 Generating comprehensive SPR network visualization...")
        
        # Extract relationships
        spr_relationships, spr_categories = self.extract_spr_relationships()
        
        # Prepare data
        nodes = []
        links = []
        
        # Color scheme by category
        category_colors = {
            'CoreMechanism': '#FFD700',
            'ProcessBlueprint': '#4A90E2',
            'CognitiveTool': '#50C878',
            'Agent': '#FF6B6B',
            'Orchestrator': '#9B59B6',
            'Engine': '#F39C12',
            'SystemComponent': '#95A5A6',
            'ExtractedKnowledge': '#E74C3C',
            'Unknown': '#BDC3C7'
        }
        
        # Add all SPR nodes
        for spr_id, spr_data in self.sprs.items():
            category = spr_data.get('category', 'Unknown')
            nodes.append({
                'id': spr_id,
                'label': spr_id,
                'type': 'spr',
                'category': category,
                'color': category_colors.get(category, '#BDC3C7'),
                'size': 8,
                'term': spr_data.get('term', ''),
                'definition': spr_data.get('definition', '')[:200]
            })
        
        # Add SPR relationship links
        for rel in spr_relationships:
            links.append({
                'source': rel['source'],
                'target': rel['target'],
                'type': 'spr_relationship',
                'rel_type': rel['type']
            })
        
        # Add component mapping links
        component_colors = {
            'workflow': '#3498DB',
            'action': '#2ECC71',
            'agent': '#E74C3C',
            'orchestrator': '#9B59B6',
            'engine': '#F39C12'
        }
        
        component_count = 0
        for comp_type, mappings in self.component_mappings.items():
            for component, spr_id in mappings.items():
                if spr_id in self.sprs:
                    comp_node_id = f"{comp_type.upper()}:{component}"
                    nodes.append({
                        'id': comp_node_id,
                        'label': component[:30],
                        'type': comp_type,
                        'color': component_colors.get(comp_type, '#95A5A6'),
                        'size': 6,
                        'full_name': component
                    })
                    links.append({
                        'source': comp_node_id,
                        'target': spr_id,
                        'type': 'component_mapping',
                        'comp_type': comp_type
                    })
                    component_count += 1
        
        print(f"  ✅ Created {len(nodes)} nodes ({len(self.sprs)} SPRs + {component_count} components)")
        print(f"  ✅ Created {len(links)} links ({len(spr_relationships)} SPR relationships + {component_count} component mappings)")
        
        # Generate HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Complete SPR Network Visualization ({len(self.sprs)} SPRs)</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #0a0a0a; color: #fff; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{ color: #FFD700; margin-bottom: 10px; }}
        .subtitle {{ color: #aaa; margin-bottom: 30px; }}
        .controls {{ display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; align-items: center; }}
        .control-group {{ display: flex; gap: 10px; align-items: center; }}
        button {{ padding: 8px 16px; background: #2a2a2a; color: #fff; border: 1px solid #444; border-radius: 4px; cursor: pointer; }}
        button:hover {{ background: #3a3a3a; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0; }}
        .stat-card {{ background: #1a1a1a; padding: 12px; border-radius: 6px; border-left: 3px solid #FFD700; }}
        .stat-value {{ font-size: 1.8em; font-weight: bold; color: #FFD700; }}
        .stat-label {{ color: #aaa; font-size: 0.85em; }}
        .legend {{ display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }}
        .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 0.9em; }}
        .legend-color {{ width: 16px; height: 16px; border-radius: 3px; }}
        #graph {{ border: 1px solid #333; border-radius: 8px; background: #0a0a0a; }}
        .node {{ cursor: pointer; }}
        .node-label {{ font-size: 9px; fill: #fff; pointer-events: none; }}
        .link {{ stroke: #444; stroke-width: 1; opacity: 0.6; }}
        .link.spr-rel {{ stroke: #FFD700; stroke-width: 1.5; opacity: 0.8; }}
        .link.component {{ stroke: #4A90E2; stroke-width: 1; opacity: 0.5; }}
        .tooltip {{ position: absolute; background: rgba(0,0,0,0.95); color: #fff; padding: 12px; border-radius: 6px; 
                   pointer-events: none; font-size: 11px; max-width: 350px; z-index: 1000; border: 1px solid #444; }}
        .search-box {{ padding: 8px; background: #1a1a1a; border: 1px solid #444; border-radius: 4px; color: #fff; width: 300px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Complete SPR Network Visualization</h1>
        <div class="subtitle">All {len(self.sprs)} SPRs with relationships and component mappings</div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(self.sprs)}</div>
                <div class="stat-label">Total SPRs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-relationships">{len(spr_relationships)}</div>
                <div class="stat-label">SPR Relationships</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-components">{component_count}</div>
                <div class="stat-label">Component Mappings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-nodes">{len(nodes)}</div>
                <div class="stat-label">Total Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-links">{len(links)}</div>
                <div class="stat-label">Total Links</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <input type="text" id="search" class="search-box" placeholder="Search SPR or component...">
                <button onclick="resetView()">Reset View</button>
                <button onclick="toggleSPRs()">Toggle SPRs</button>
                <button onclick="toggleComponents()">Toggle Components</button>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background: #FFD700;"></div><span>Core Mechanism</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #4A90E2;"></div><span>Process Blueprint</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #50C878;"></div><span>Cognitive Tool</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #FF6B6B;"></div><span>Agent</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #9B59B6;"></div><span>Orchestrator</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #F39C12;"></div><span>Engine</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #95A5A6;"></div><span>System Component</span></div>
            <div class="legend-item"><div class="legend-color" style="background: #E74C3C;"></div><span>Extracted Knowledge</span></div>
        </div>
        
        <svg id="graph" width="1600" height="1000"></svg>
        <div class="tooltip" id="tooltip" style="display: none;"></div>
    </div>
    
    <script>
        const data = {{
            nodes: {json.dumps(nodes)},
            links: {json.dumps(links)}
        }};
        
        let showSPRs = true;
        let showComponents = true;
        
        const svg = d3.select('#graph');
        const width = 1600;
        const height = 1000;
        
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(d => {{
                if (d.type === 'spr_relationship') return 80;
                return 120;
            }}))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => d.size + 5));
        
        const link = svg.append('g')
            .selectAll('line')
            .data(data.links)
            .enter().append('line')
            .attr('class', d => d.type === 'spr_relationship' ? 'link spr-rel' : 'link component')
            .attr('stroke-width', d => d.type === 'spr_relationship' ? 1.5 : 1);
        
        const node = svg.append('g')
            .selectAll('circle')
            .data(data.nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => d.size)
            .attr('fill', d => d.color)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('mouseover', showTooltip)
            .on('mouseout', hideTooltip)
            .on('click', highlightNode);
        
        const label = svg.append('g')
            .selectAll('text')
            .data(data.nodes)
            .enter().append('text')
            .attr('class', 'node-label')
            .text(d => d.label.length > 20 ? d.label.substring(0, 20) + '...' : d.label)
            .attr('dx', d => d.size + 3)
            .attr('dy', 4);
        
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        const tooltip = d3.select('#tooltip');
        
        function showTooltip(event, d) {{
            let html = `<strong>${{d.label}}</strong><br/>`;
            if (d.type === 'spr') {{
                html += `Type: SPR<br/>Category: ${{d.category || 'Unknown'}}<br/>`;
                if (d.term) html += `Term: ${{d.term}}<br/>`;
                if (d.definition) html += `<br/>${{d.definition}}`;
            }} else {{
                html += `Type: ${{d.type}}<br/>`;
                if (d.full_name) html += `Full Name: ${{d.full_name}}`;
            }}
            tooltip
                .style('display', 'block')
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .html(html);
        }}
        
        function hideTooltip() {{
            tooltip.style('display', 'none');
        }}
        
        function highlightNode(event, d) {{
            // Highlight connected nodes
            const connectedIds = new Set([d.id]);
            data.links.forEach(link => {{
                if (link.source.id === d.id) connectedIds.add(link.target.id);
                if (link.target.id === d.id) connectedIds.add(link.source.id);
            }});
            
            node.style('opacity', n => connectedIds.has(n.id) ? 1 : 0.1);
            link.style('opacity', l => 
                connectedIds.has(l.source.id) && connectedIds.has(l.target.id) ? 1 : 0.1);
        }}
        
        function resetView() {{
            node.style('opacity', 1);
            link.style('opacity', 1);
            simulation.alpha(1).restart();
        }}
        
        function toggleSPRs() {{
            showSPRs = !showSPRs;
            node.style('display', d => d.type === 'spr' && !showSPRs ? 'none' : null);
        }}
        
        function toggleComponents() {{
            showComponents = !showComponents;
            node.style('display', d => d.type !== 'spr' && !showComponents ? 'none' : null);
        }}
        
        // Search functionality
        document.getElementById('search').addEventListener('input', function(e) {{
            const query = e.target.value.toLowerCase();
            if (!query) {{
                resetView();
                return;
            }}
            
            const matchingIds = new Set();
            data.nodes.forEach(n => {{
                if (n.label.toLowerCase().includes(query) || 
                    (n.term && n.term.toLowerCase().includes(query)) ||
                    (n.full_name && n.full_name.toLowerCase().includes(query))) {{
                    matchingIds.add(n.id);
                }}
            }});
            
            node.style('opacity', n => matchingIds.has(n.id) ? 1 : 0.1);
            link.style('opacity', l => 
                matchingIds.has(l.source.id) || matchingIds.has(l.target.id) ? 1 : 0.1);
        }});
    </script>
</body>
</html>"""
        
        output_file = self.project_root / "knowledge_graph" / "full_spr_network_visualization.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✅ Full network visualization saved to: {output_file}")
        return output_file
    
    def run(self):
        """Execute full visualization generation"""
        print("🌐 Generating Full SPR Network Visualization")
        print("=" * 70)
        
        self.load_data()
        output_file = self.generate_comprehensive_visualization()
        
        print("\n" + "=" * 70)
        print("✅ Full SPR Network Visualization Complete!")
        print(f"📊 File: {output_file}")
        print(f"📈 Includes: {len(self.sprs)} SPRs with all relationships")
        print("=" * 70)

if __name__ == "__main__":
    visualizer = FullSPRNetworkVisualizer()
    visualizer.run()








