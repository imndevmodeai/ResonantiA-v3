#!/usr/bin/env python3
"""
Export Knowledge Graph to Markdown format for LLM ingestion
Creates a single .md file with all SPR definitions in readable format
"""

import json
from pathlib import Path
from datetime import datetime

def export_kg_to_markdown(output_file: str = "kg_export.md", max_sprs: int = None):
    """
    Export KG to markdown format for direct LLM ingestion.
    
    Args:
        output_file: Output markdown file path
        max_sprs: Maximum number of SPRs to include (None = all)
    """
    print("📝 Exporting KG to Markdown format...")
    
    # Load the index file
    index_file = Path("knowledge_graph/optimized/spr_index.json")
    if not index_file.exists():
        # Try legacy format
        index_file = Path("knowledge_graph/spr_definitions_tv.json")
        if not index_file.exists():
            raise FileNotFoundError("Knowledge Graph not found")
    
    print(f"  Loading from {index_file}...")
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both dict and list formats
    if isinstance(data, list):
        spr_dict = {spr['spr_id']: spr for spr in data if isinstance(spr, dict) and 'spr_id' in spr}
    else:
        spr_dict = data
    
    total_sprs = len(spr_dict)
    if max_sprs:
        spr_dict = dict(list(spr_dict.items())[:max_sprs])
        print(f"  Limiting to {max_sprs} SPRs (out of {total_sprs} total)")
    
    print(f"  Exporting {len(spr_dict)} SPRs to markdown...")
    
    # Load symbol codex files
    codex_data = {}
    codex_file = Path("knowledge_graph/symbol_codex.json")
    vocab_file = Path("knowledge_graph/protocol_symbol_vocabulary.json")
    
    if codex_file.exists():
        with open(codex_file, 'r', encoding='utf-8') as f:
            codex_data['symbol_codex'] = json.load(f)
    
    if vocab_file.exists():
        with open(vocab_file, 'r', encoding='utf-8') as f:
            codex_data['protocol_vocabulary'] = json.load(f)
    
    # Build markdown content
    lines = [
        "# Knowledge Graph Export",
        "",
        f"**Exported**: {datetime.now().isoformat()}",
        f"**Total SPRs**: {len(spr_dict)}",
        f"**Format**: Markdown for LLM ingestion",
        "",
        "---",
        "",
        "## Symbol Codex",
        "",
        "*The symbol codex is required to decompress Zepto SPRs back to full text.*",
        ""
    ]
    
    # Add symbol codex section
    if codex_data.get('symbol_codex'):
        lines.append("### Symbol Codex")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(codex_data['symbol_codex'], indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
    
    if codex_data.get('protocol_vocabulary'):
        lines.append("### Protocol Symbol Vocabulary")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(codex_data['protocol_vocabulary'], indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## SPR Definitions",
        ""
    ])
    
    # Sort SPRs by ID for consistency
    for spr_id, spr in sorted(spr_dict.items()):
        lines.append(f"### {spr_id}")
        lines.append("")
        
        # Term
        if spr.get('term'):
            lines.append(f"**Term**: {spr['term']}")
            lines.append("")
        
        # Category
        if spr.get('category'):
            lines.append(f"**Category**: {spr['category']}")
            lines.append("")
        
        # Definition
        if spr.get('definition'):
            definition = spr['definition'].strip()
            # Truncate very long definitions
            if len(definition) > 2000:
                definition = definition[:2000] + "... [truncated]"
            lines.append(f"**Definition**:")
            lines.append("")
            lines.append(definition)
            lines.append("")
        
        # Relationships
        if spr.get('relationships'):
            rels = spr['relationships']
            if isinstance(rels, dict) and rels:
                lines.append("**Relationships**:")
                lines.append("")
                for key, value in rels.items():
                    if isinstance(value, list):
                        lines.append(f"- {key}: {', '.join(str(v) for v in value)}")
                    else:
                        lines.append(f"- {key}: {value}")
                lines.append("")
        
        # Zepto SPR (ultra-compressed representation)
        if spr.get('zepto_spr'):
            lines.append(f"**Zepto SPR**: `{spr['zepto_spr']}`")
            lines.append("")
            lines.append("*Note: Zepto SPR is an ultra-compressed representation. Use symbol codex to decompress.*")
            lines.append("")
        
        # Blueprint details
        if spr.get('blueprint_details'):
            lines.append("**Blueprint Details**:")
            lines.append("")
            lines.append(spr['blueprint_details'])
            lines.append("")
        
        # Example application
        if spr.get('example_application'):
            lines.append("**Example Application**:")
            lines.append("")
            lines.append(spr['example_application'])
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Add summary at the end
    lines.extend([
        "## Summary",
        "",
        f"- **Total SPRs exported**: {len(spr_dict)}",
        f"- **Export format**: Markdown",
        f"- **Export date**: {datetime.now().isoformat()}",
        "",
        "### Usage Notes",
        "",
        "This file contains all SPR (Sparse Priming Representation) definitions from the Knowledge Graph.",
        "Each SPR is a cognitive key that activates related concepts and knowledge.",
        "",
        "**Key Fields:**",
        "- **Term**: Human-readable term",
        "- **Category**: Knowledge category",
        "- **Definition**: Full definition/description",
        "- **Zepto SPR**: Ultra-compressed representation (50-200 bytes)",
        "- **Relationships**: Connections to other SPRs",
        "",
        "**To use Zepto SPRs:**",
        "Zepto SPRs require a symbol codex for decompression. The Zepto format provides",
        "extreme compression (642:1 ratio) while preserving semantic meaning.",
        "",
        "The symbol codex is included at the beginning of this document. Use it to",
        "decompress Zepto SPRs back to full narrative text.",
        "",
        "### Decompression Example",
        "",
        "```python",
        "import json",
        "",
        "# Load codex from this document or separate file",
        "with open('symbol_codex.json', 'r') as f:",
        "    codex = json.load(f)",
        "",
        "# Decompress Zepto SPR",
        "zepto_spr = 'Ο|Α'  # Example Zepto SPR",
        "# Use codex to map symbols back to text",
        "# Implementation depends on decompression algorithm",
        "```",
        ""
    ])
    
    # Write to file
    content = "\n".join(lines)
    output_path = Path(output_file)
    
    print(f"  Writing to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  ✅ Exported {len(spr_dict)} SPRs ({file_size_mb:.2f} MB)")
    
    return {
        'output_file': str(output_path),
        'spr_count': len(spr_dict),
        'file_size_mb': file_size_mb,
        'exported_at': datetime.now().isoformat()
    }

def export_kg_summary_markdown(output_file: str = "kg_summary.md", top_n: int = 100):
    """
    Export a summary version with top N most important SPRs.
    Useful when full export is too large.
    """
    print(f"📝 Exporting KG Summary (top {top_n} SPRs)...")
    
    # Load index
    index_file = Path("knowledge_graph/optimized/spr_index.json")
    if not index_file.exists():
        index_file = Path("knowledge_graph/spr_definitions_tv.json")
        if not index_file.exists():
            raise FileNotFoundError("Knowledge Graph not found")
    
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        spr_dict = {spr['spr_id']: spr for spr in data if isinstance(spr, dict) and 'spr_id' in spr}
    else:
        spr_dict = data
    
    # Prioritize certain categories or important SPRs
    priority_categories = ['CoreConcept', 'SystemComponent', 'CognitiveTool', 'Workflow']
    priority_sprs = ['Cognitive resonancE', 'IAR', 'KnO', 'SPR', 'Metacognitive shifT', 'SIRC']
    
    # Sort: priority SPRs first, then by category, then alphabetically
    sorted_sprs = []
    
    # Add priority SPRs
    for spr_id in priority_sprs:
        if spr_id in spr_dict:
            sorted_sprs.append((spr_id, spr_dict[spr_id], 0))
    
    # Add priority category SPRs
    for spr_id, spr in spr_dict.items():
        if spr_id not in priority_sprs:
            category = spr.get('category', '')
            priority = 1 if category in priority_categories else 2
            sorted_sprs.append((spr_id, spr, priority))
    
    # Sort by priority, then by ID
    sorted_sprs.sort(key=lambda x: (x[2], x[0]))
    
    # Take top N
    selected = sorted_sprs[:top_n]
    
    # Build markdown
    lines = [
        "# Knowledge Graph Summary",
        "",
        f"**Exported**: {datetime.now().isoformat()}",
        f"**SPRs included**: {len(selected)} (top {top_n} most important)",
        f"**Total SPRs in KG**: {len(spr_dict)}",
        "",
        "---",
        "",
        "## Priority SPR Definitions",
        ""
    ]
    
    for spr_id, spr, _ in selected:
        lines.append(f"### {spr_id}")
        lines.append("")
        
        if spr.get('term'):
            lines.append(f"**Term**: {spr['term']}")
            lines.append("")
        
        if spr.get('category'):
            lines.append(f"**Category**: {spr['category']}")
            lines.append("")
        
        if spr.get('definition'):
            definition = spr['definition'].strip()
            if len(definition) > 1000:
                definition = definition[:1000] + "... [truncated]"
            lines.append(f"**Definition**: {definition}")
            lines.append("")
        
        if spr.get('zepto_spr'):
            lines.append(f"**Zepto SPR**: `{spr['zepto_spr']}`")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    content = "\n".join(lines)
    output_path = Path(output_file)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  ✅ Exported summary ({file_size_mb:.2f} MB)")
    
    return {
        'output_file': str(output_path),
        'spr_count': len(selected),
        'file_size_mb': file_size_mb
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        # Export summary
        result = export_kg_summary_markdown("kg_summary.md", top_n=100)
        print(f"\n✅ Summary exported: {result['output_file']}")
    else:
        # Export full
        result = export_kg_to_markdown("kg_export.md")
        print(f"\n✅ Full export created: {result['output_file']}")
        print(f"   Size: {result['file_size_mb']:.2f} MB")
        print(f"   SPRs: {result['spr_count']}")
