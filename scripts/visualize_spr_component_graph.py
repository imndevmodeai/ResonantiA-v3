#!/usr/bin/env python3
"""
Visual SPR-Component Mapping Graph Generator
Creates interactive visualizations of SPR-component relationships
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib/networkx not available. Generating HTML visualization instead.")

try:
    from plotly.graph_objects import Scatter, Figure
    from plotly.offline import plot
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

class SPRComponentVisualizer:
    """Creates visual representations of SPR-component mappings"""
    
    def __init__(self):
        self.project_root = project_root
        self.mapping_file = project_root / "knowledge_graph" / "spr_component_mapping.json"
        self.mapping_data = None
        self.graph = None
        
    def load_mapping_data(self):
        """Load the component mapping data"""
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")
        
        with open(self.mapping_file, 'r', encoding='utf-8') as f:
            self.mapping_data = json.load(f)
        
        print(f"✅ Loaded mapping data: {len(self.mapping_data.get('workflow_mappings', {}))} workflows, "
              f"{len(self.mapping_data.get('action_mappings', {}))} actions")
    
    def build_network_graph(self):
        """Build a NetworkX graph from the mappings"""
        self.graph = nx.Graph()
        
        # Add SPR nodes
        spr_nodes = set()
        spr_nodes.update(self.mapping_data.get('workflow_mappings', {}).values())
        spr_nodes.update(self.mapping_data.get('action_mappings', {}).values())
        spr_nodes.update(self.mapping_data.get('agent_mappings', {}).values())
        spr_nodes.update(self.mapping_data.get('orchestrator_mappings', {}).values())
        spr_nodes.update(self.mapping_data.get('engine_mappings', {}).values())
        
        for spr in spr_nodes:
            self.graph.add_node(spr, node_type='spr', color='#FFD700', size=500)
        
        # Add workflow nodes and edges
        for wf_id, spr_id in self.mapping_data.get('workflow_mappings', {}).items():
            self.graph.add_node(f"WF:{wf_id}", node_type='workflow', color='#4A90E2', size=300)
            self.graph.add_edge(f"WF:{wf_id}", spr_id, edge_type='maps_to')
        
        # Add action nodes and edges
        for action, spr_id in self.mapping_data.get('action_mappings', {}).items():
            self.graph.add_node(f"ACT:{action}", node_type='action', color='#50C878', size=200)
            self.graph.add_edge(f"ACT:{action}", spr_id, edge_type='maps_to')
        
        # Add agent nodes and edges
        for agent, spr_id in self.mapping_data.get('agent_mappings', {}).items():
            self.graph.add_node(f"AG:{agent}", node_type='agent', color='#FF6B6B', size=250)
            self.graph.add_edge(f"AG:{agent}", spr_id, edge_type='maps_to')
        
        # Add orchestrator nodes and edges
        for orch, spr_id in self.mapping_data.get('orchestrator_mappings', {}).items():
            self.graph.add_node(f"ORCH:{orch}", node_type='orchestrator', color='#9B59B6', size=350)
            self.graph.add_edge(f"ORCH:{orch}", spr_id, edge_type='maps_to')
        
        # Add engine nodes and edges
        for engine, spr_id in self.mapping_data.get('engine_mappings', {}).items():
            self.graph.add_node(f"ENG:{engine}", node_type='engine', color='#F39C12', size=300)
            self.graph.add_edge(f"ENG:{engine}", spr_id, edge_type='maps_to')
        
        print(f"✅ Built graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
    
    def generate_html_visualization(self):
        """Generate an interactive HTML visualization"""
        print("🌐 Generating HTML visualization...")
        
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>SPR-Component Mapping Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #FFD700; }
        .legend { display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }
        .legend-item { display: flex; align-items: center; gap: 8px; }
        .legend-color { width: 20px; height: 20px; border-radius: 3px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #2a2a2a; padding: 15px; border-radius: 8px; border-left: 4px solid #FFD700; }
        .stat-value { font-size: 2em; font-weight: bold; color: #FFD700; }
        .stat-label { color: #aaa; font-size: 0.9em; }
        #graph { border: 1px solid #444; border-radius: 8px; background: #1a1a1a; }
        .node { cursor: pointer; }
        .node-label { font-size: 10px; fill: #fff; pointer-events: none; }
        .link { stroke: #555; stroke-width: 1.5; }
        .tooltip { position: absolute; background: rgba(0,0,0,0.9); color: #fff; padding: 10px; border-radius: 5px; 
                   pointer-events: none; font-size: 12px; max-width: 300px; z-index: 1000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 SPR-Component Mapping Visualization</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="stat-workflows">0</div>
                <div class="stat-label">Workflows</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-actions">0</div>
                <div class="stat-label">Actions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-agents">0</div>
                <div class="stat-label">Agents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-orchestrators">0</div>
                <div class="stat-label">Orchestrators</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-engines">0</div>
                <div class="stat-label">Engines</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-sprs">0</div>
                <div class="stat-label">SPRs</div>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #FFD700;"></div>
                <span>SPR</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #4A90E2;"></div>
                <span>Workflow</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #50C878;"></div>
                <span>Action</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF6B6B;"></div>
                <span>Agent</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #9B59B6;"></div>
                <span>Orchestrator</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #F39C12;"></div>
                <span>Engine</span>
            </div>
        </div>
        
        <svg id="graph" width="1400" height="900"></svg>
        <div class="tooltip" id="tooltip" style="display: none;"></div>
    </div>
    
    <script>
        const data = """ + json.dumps(self._prepare_graph_data()) + """;
        
        // Update stats
        document.getElementById('stat-workflows').textContent = data.summary.total_workflows;
        document.getElementById('stat-actions').textContent = data.summary.total_actions;
        document.getElementById('stat-agents').textContent = data.summary.total_agents;
        document.getElementById('stat-orchestrators').textContent = data.summary.total_orchestrators;
        document.getElementById('stat-engines').textContent = data.summary.total_engines;
        document.getElementById('stat-sprs').textContent = data.sprs.length;
        
        // Setup D3 force simulation
        const svg = d3.select('#graph');
        const width = 1400;
        const height = 900;
        
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));
        
        const link = svg.append('g')
            .selectAll('line')
            .data(data.links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke-width', 2);
        
        const node = svg.append('g')
            .selectAll('circle')
            .data(data.nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => d.size || 10)
            .attr('fill', d => d.color)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('mouseover', showTooltip)
            .on('mouseout', hideTooltip);
        
        const label = svg.append('g')
            .selectAll('text')
            .data(data.nodes)
            .enter().append('text')
            .attr('class', 'node-label')
            .text(d => d.label)
            .attr('dx', 12)
            .attr('dy', 4);
        
        simulation.on('tick', () => {
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
        });
        
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        const tooltip = d3.select('#tooltip');
        
        function showTooltip(event, d) {
            tooltip
                .style('display', 'block')
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .html(`<strong>${d.label}</strong><br/>Type: ${d.type}<br/>ID: ${d.id}`);
        }
        
        function hideTooltip() {
            tooltip.style('display', 'none');
        }
    </script>
</body>
</html>"""
        
        output_file = self.project_root / "knowledge_graph" / "spr_component_visualization.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✅ HTML visualization saved to: {output_file}")
        return output_file
    
    def _prepare_graph_data(self):
        """Prepare graph data for visualization"""
        nodes = []
        links = []
        node_ids = {}
        
        # Color mapping
        colors = {
            'spr': '#FFD700',
            'workflow': '#4A90E2',
            'action': '#50C878',
            'agent': '#FF6B6B',
            'orchestrator': '#9B59B6',
            'engine': '#F39C12'
        }
        
        # Size mapping
        sizes = {
            'spr': 15,
            'workflow': 12,
            'action': 8,
            'agent': 10,
            'orchestrator': 14,
            'engine': 12
        }
        
        # Collect all SPRs
        spr_set = set()
        spr_set.update(self.mapping_data.get('workflow_mappings', {}).values())
        spr_set.update(self.mapping_data.get('action_mappings', {}).values())
        spr_set.update(self.mapping_data.get('agent_mappings', {}).values())
        spr_set.update(self.mapping_data.get('orchestrator_mappings', {}).values())
        spr_set.update(self.mapping_data.get('engine_mappings', {}).values())
        
        # Add SPR nodes
        for spr in spr_set:
            node_id = f"SPR:{spr}"
            node_ids[spr] = node_id
            nodes.append({
                'id': node_id,
                'label': spr,
                'type': 'spr',
                'color': colors['spr'],
                'size': sizes['spr']
            })
        
        # Add workflow nodes and links
        for wf_id, spr_id in self.mapping_data.get('workflow_mappings', {}).items():
            node_id = f"WF:{wf_id}"
            nodes.append({
                'id': node_id,
                'label': wf_id[:30] + ('...' if len(wf_id) > 30 else ''),
                'type': 'workflow',
                'color': colors['workflow'],
                'size': sizes['workflow']
            })
            links.append({
                'source': node_id,
                'target': node_ids.get(spr_id, f"SPR:{spr_id}"),
                'type': 'maps_to'
            })
        
        # Add action nodes and links (sample first 50 to avoid clutter)
        for i, (action, spr_id) in enumerate(list(self.mapping_data.get('action_mappings', {}).items())[:50]):
            node_id = f"ACT:{action}"
            nodes.append({
                'id': node_id,
                'label': action[:25] + ('...' if len(action) > 25 else ''),
                'type': 'action',
                'color': colors['action'],
                'size': sizes['action']
            })
            links.append({
                'source': node_id,
                'target': node_ids.get(spr_id, f"SPR:{spr_id}"),
                'type': 'maps_to'
            })
        
        # Add agent nodes and links
        for agent, spr_id in self.mapping_data.get('agent_mappings', {}).items():
            node_id = f"AG:{agent}"
            nodes.append({
                'id': node_id,
                'label': agent,
                'type': 'agent',
                'color': colors['agent'],
                'size': sizes['agent']
            })
            links.append({
                'source': node_id,
                'target': node_ids.get(spr_id, f"SPR:{spr_id}"),
                'type': 'maps_to'
            })
        
        # Add orchestrator nodes and links
        for orch, spr_id in self.mapping_data.get('orchestrator_mappings', {}).items():
            node_id = f"ORCH:{orch}"
            nodes.append({
                'id': node_id,
                'label': orch,
                'type': 'orchestrator',
                'color': colors['orchestrator'],
                'size': sizes['orchestrator']
            })
            links.append({
                'source': node_id,
                'target': node_ids.get(spr_id, f"SPR:{spr_id}"),
                'type': 'maps_to'
            })
        
        # Add engine nodes and links
        for engine, spr_id in self.mapping_data.get('engine_mappings', {}).items():
            node_id = f"ENG:{engine}"
            nodes.append({
                'id': node_id,
                'label': engine,
                'type': 'engine',
                'color': colors['engine'],
                'size': sizes['engine']
            })
            links.append({
                'source': node_id,
                'target': node_ids.get(spr_id, f"SPR:{spr_id}"),
                'type': 'maps_to'
            })
        
        return {
            'nodes': nodes,
            'links': links,
            'sprs': list(spr_set),
            'summary': self.mapping_data.get('summary', {})
        }
    
    def generate_summary_report(self):
        """Generate a text summary report"""
        print("📄 Generating summary report...")
        
        report_lines = [
            "# SPR-Component Mapping Summary Report",
            "",
            "## Overview",
            f"- **Total Workflows**: {self.mapping_data['summary']['total_workflows']}",
            f"- **Total Actions**: {self.mapping_data['summary']['total_actions']}",
            f"- **Total Agents**: {self.mapping_data['summary']['total_agents']}",
            f"- **Total Orchestrators**: {self.mapping_data['summary']['total_orchestrators']}",
            f"- **Total Engines**: {self.mapping_data['summary']['total_engines']}",
            "",
            "## Mapping Coverage",
            f"- **Mapped Workflows**: {self.mapping_data['summary']['mapped_workflows']} / {self.mapping_data['summary']['total_workflows']}",
            f"- **Mapped Actions**: {self.mapping_data['summary']['mapped_actions']} / {self.mapping_data['summary']['total_actions']}",
            f"- **Mapped Agents**: {self.mapping_data['summary']['mapped_agents']} / {self.mapping_data['summary']['total_agents']}",
            f"- **Mapped Orchestrators**: {self.mapping_data['summary']['mapped_orchestrators']} / {self.mapping_data['summary']['total_orchestrators']}",
            f"- **Mapped Engines**: {self.mapping_data['summary']['mapped_engines']} / {self.mapping_data['summary']['total_engines']}",
            "",
            "## Key SPRs by Component Type",
            "",
            "### Workflow SPRs",
        ]
        
        # Group workflows by SPR
        wf_by_spr = defaultdict(list)
        for wf, spr in self.mapping_data['workflow_mappings'].items():
            wf_by_spr[spr].append(wf)
        
        for spr, wfs in sorted(wf_by_spr.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            report_lines.append(f"- **{spr}**: {len(wfs)} workflows")
        
        report_lines.extend([
            "",
            "### Action SPRs",
        ])
        
        # Group actions by SPR
        act_by_spr = defaultdict(list)
        for act, spr in self.mapping_data['action_mappings'].items():
            act_by_spr[spr].append(act)
        
        for spr, acts in sorted(act_by_spr.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            report_lines.append(f"- **{spr}**: {len(acts)} actions")
        
        report_lines.extend([
            "",
            "### Agent SPRs",
        ])
        
        for agent, spr in sorted(self.mapping_data['agent_mappings'].items()):
            report_lines.append(f"- **{agent}** → {spr}")
        
        report_lines.extend([
            "",
            "### Orchestrator SPRs",
        ])
        
        for orch, spr in sorted(self.mapping_data['orchestrator_mappings'].items()):
            report_lines.append(f"- **{orch}** → {spr}")
        
        report_lines.extend([
            "",
            "### Engine SPRs",
        ])
        
        for engine, spr in sorted(self.mapping_data['engine_mappings'].items()):
            report_lines.append(f"- **{engine}** → {spr}")
        
        report_content = "\n".join(report_lines)
        
        report_file = self.project_root / "knowledge_graph" / "spr_component_mapping_summary.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"  ✅ Summary report saved to: {report_file}")
        return report_file
    
    def run(self):
        """Execute visualization generation"""
        print("🎨 Generating SPR-Component Visualizations")
        print("=" * 70)
        
        self.load_mapping_data()
        self.build_network_graph()
        
        # Generate HTML visualization
        html_file = self.generate_html_visualization()
        
        # Generate summary report
        report_file = self.generate_summary_report()
        
        print("\n" + "=" * 70)
        print("✅ Visualization Complete!")
        print(f"📊 Interactive Graph: {html_file}")
        print(f"📄 Summary Report: {report_file}")
        print("\n💡 Open the HTML file in your browser to explore the interactive graph!")
        print("=" * 70)

if __name__ == "__main__":
    visualizer = SPRComponentVisualizer()
    visualizer.run()






























