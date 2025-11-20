#!/usr/bin/env python3
"""
Export Knowledge Graph for LLM Transfer
Creates comprehensive export packages for sharing KG with another LLM instance
"""

import json
import sqlite3
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

class KGExporter:
    """Export Knowledge Graph in various formats for LLM transfer."""
    
    def __init__(self, kg_root: str = "knowledge_graph"):
        self.kg_root = Path(kg_root)
        self.optimized_dir = self.kg_root / "optimized"
        self.legacy_file = self.kg_root / "spr_definitions_tv.json"
        
    def export_full_legacy_format(self, output_file: str = "kg_export_full.json") -> Dict[str, Any]:
        """
        Export full KG in legacy monolithic format (compatible with standard SPRManager).
        Reconstructs full SPR definitions from optimized storage.
        """
        print("📦 Exporting full KG in legacy format...")
        
        # Try optimized first, fallback to legacy
        if self.optimized_dir.exists() and (self.optimized_dir / "spr_index.json").exists():
            return self._export_from_optimized(output_file)
        elif self.legacy_file.exists():
            return self._export_from_legacy(output_file)
        else:
            raise FileNotFoundError(f"Knowledge Graph not found at {self.kg_root}")
    
    def _export_from_optimized(self, output_file: str) -> Dict[str, Any]:
        """Export from optimized storage, reconstructing full SPRs."""
        index_file = self.optimized_dir / "spr_index.json"
        content_store = self.optimized_dir / "content_store"
        
        print(f"  Loading index from {index_file}...")
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        print(f"  Reconstructing {len(index_data)} SPRs from content store...")
        full_sprs = []
        
        for spr_id, index_entry in index_data.items():
            spr = {
                'spr_id': spr_id,
                'term': index_entry.get('term', ''),
                'category': index_entry.get('category', ''),
                'definition': index_entry.get('definition', ''),
                'relationships': index_entry.get('relationships', {}),
                'zepto_spr': index_entry.get('zepto_spr', ''),
                'symbol_codex': index_entry.get('symbol_codex', {}),
                'blueprint_details': index_entry.get('blueprint_details', ''),
                'example_application': index_entry.get('example_application', ''),
            }
            
            # Load narrative if available
            narrative_hash = index_entry.get('narrative_hash')
            if narrative_hash and content_store:
                narrative_file = content_store / "narratives" / f"{narrative_hash}.json"
                if narrative_file.exists():
                    try:
                        with open(narrative_file, 'r', encoding='utf-8') as f:
                            narrative_data = json.load(f)
                            spr['narrative'] = narrative_data.get('content', '')
                    except Exception as e:
                        print(f"    Warning: Could not load narrative for {spr_id}: {e}")
            
            # Load compression stages if available
            compression_stages_hash = index_entry.get('compression_stages_hash')
            if compression_stages_hash and content_store:
                stages_file = content_store / "compression_stages" / f"{compression_stages_hash}.json"
                if stages_file.exists():
                    try:
                        with open(stages_file, 'r', encoding='utf-8') as f:
                            spr['compression_stages'] = json.load(f)
                    except Exception as e:
                        print(f"    Warning: Could not load compression stages for {spr_id}: {e}")
            
            full_sprs.append(spr)
            
            if len(full_sprs) % 500 == 0:
                print(f"    Progress: {len(full_sprs)}/{len(index_data)} SPRs reconstructed")
        
        # Save as list format (standard SPR format)
        output_path = Path(output_file)
        print(f"  Saving to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(full_sprs, f, indent=2, ensure_ascii=False)
        
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Exported {len(full_sprs)} SPRs ({file_size:.2f} MB)")
        
        return {
            'format': 'legacy_full',
            'spr_count': len(full_sprs),
            'file_size_mb': file_size,
            'output_file': str(output_path),
            'exported_at': datetime.now().isoformat()
        }
    
    def _export_from_legacy(self, output_file: str) -> Dict[str, Any]:
        """Export from legacy format (just copy)."""
        print(f"  Copying from legacy file {self.legacy_file}...")
        shutil.copy(self.legacy_file, output_file)
        
        file_size = Path(output_file).stat().st_size / (1024 * 1024)
        print(f"  ✅ Exported ({file_size:.2f} MB)")
        
        return {
            'format': 'legacy',
            'file_size_mb': file_size,
            'output_file': output_file,
            'exported_at': datetime.now().isoformat()
        }
    
    def export_optimized_package(self, output_dir: str = "kg_export_optimized") -> Dict[str, Any]:
        """
        Export optimized storage structure as a complete package.
        Includes index, database, and content store.
        """
        print("📦 Exporting optimized KG package...")
        
        if not self.optimized_dir.exists():
            raise FileNotFoundError(f"Optimized storage not found at {self.optimized_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Copy index file
        print("  Copying index file...")
        shutil.copy(self.optimized_dir / "spr_index.json", output_path / "spr_index.json")
        
        # Copy database
        db_file = self.optimized_dir / "kg_metadata.db"
        if db_file.exists():
            print("  Copying SQLite database...")
            shutil.copy(db_file, output_path / "kg_metadata.db")
        
        # Copy content store
        content_store = self.optimized_dir / "content_store"
        if content_store.exists():
            print("  Copying content store...")
            shutil.copytree(content_store, output_path / "content_store", dirs_exist_ok=True)
        
        # Create README
        readme_content = f"""# Knowledge Graph Export Package

Exported: {datetime.now().isoformat()}
Format: Optimized Storage

## Contents

- `spr_index.json` - Lightweight index with Zepto SPRs inline
- `kg_metadata.db` - SQLite database for fast queries
- `content_store/` - Content-addressable storage
  - `zepto_index.json` - Zepto hash mapping
  - `narratives/` - Narrative content files
  - `compression_stages/` - Compression stage files

## Usage

To use this package with OptimizedSPRManager:

```python
from Three_PointO_ArchE.spr_manager_optimized import OptimizedSPRManager

manager = OptimizedSPRManager(
    spr_filepath="spr_index.json",
    optimized_dir="."
)
```

## Statistics

- Index size: {Path(output_path / "spr_index.json").stat().st_size / (1024*1024):.2f} MB
- Database size: {Path(output_path / "kg_metadata.db").stat().st_size / (1024*1024):.2f} MB if exists
- Content store: See content_store/ directory
"""
        
        with open(output_path / "README.md", 'w') as f:
            f.write(readme_content)
        
        total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file()) / (1024 * 1024)
        print(f"  ✅ Exported optimized package ({total_size:.2f} MB)")
        
        return {
            'format': 'optimized_package',
            'output_dir': str(output_path),
            'total_size_mb': total_size,
            'exported_at': datetime.now().isoformat()
        }
    
    def export_zepto_minimal(self, output_file: str = "kg_export_zepto_minimal.json") -> Dict[str, Any]:
        """
        Export minimal Zepto-only representation.
        Ultra-compressed format for quick transfer (index + Zepto SPRs only).
        """
        print("📦 Exporting Zepto-minimal format...")
        
        if not self.optimized_dir.exists() or not (self.optimized_dir / "spr_index.json").exists():
            raise FileNotFoundError("Optimized storage required for Zepto export")
        
        index_file = self.optimized_dir / "spr_index.json"
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Extract only essential data: metadata + Zepto SPRs
        minimal_data = {
            'format': 'zepto_minimal',
            'exported_at': datetime.now().isoformat(),
            'spr_count': len(index_data),
            'sprs': {}
        }
        
        for spr_id, index_entry in index_data.items():
            minimal_data['sprs'][spr_id] = {
                'spr_id': spr_id,
                'term': index_entry.get('term', ''),
                'category': index_entry.get('category', ''),
                'zepto_spr': index_entry.get('zepto_spr', ''),
                'symbol_codex': index_entry.get('symbol_codex', {}),
                'relationships': index_entry.get('relationships', {}),
                'zepto_hash': index_entry.get('zepto_hash'),
            }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(minimal_data, f, indent=2, ensure_ascii=False)
        
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Exported {len(index_data)} SPRs in Zepto format ({file_size:.2f} MB)")
        
        return {
            'format': 'zepto_minimal',
            'spr_count': len(index_data),
            'file_size_mb': file_size,
            'output_file': str(output_path),
            'exported_at': datetime.now().isoformat()
        }
    
    def export_for_prompt_injection(self, output_file: str = "kg_prompt_context.txt", max_size_mb: float = 0.5) -> Dict[str, Any]:
        """
        Export KG as formatted text for direct prompt injection.
        Includes SPR definitions in a readable format.
        Optimized to fit within token limits.
        """
        print(f"📦 Exporting KG for prompt injection (max {max_size_mb} MB)...")
        
        # Load SPRs
        if self.optimized_dir.exists() and (self.optimized_dir / "spr_index.json").exists():
            with open(self.optimized_dir / "spr_index.json", 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        elif self.legacy_file.exists():
            with open(self.legacy_file, 'r', encoding='utf-8') as f:
                spr_data = json.load(f)
                if isinstance(spr_data, list):
                    index_data = {spr['spr_id']: spr for spr in spr_data}
                else:
                    index_data = spr_data
        else:
            raise FileNotFoundError("Knowledge Graph not found")
        
        # Format as readable text
        lines = [
            "# Knowledge Graph Export for LLM Context",
            f"# Exported: {datetime.now().isoformat()}",
            f"# Total SPRs: {len(index_data)}",
            "",
            "## SPR Definitions",
            ""
        ]
        
        for spr_id, spr in list(index_data.items())[:1000]:  # Limit to first 1000 for size
            lines.append(f"### {spr_id}")
            lines.append(f"**Term**: {spr.get('term', '')}")
            lines.append(f"**Category**: {spr.get('category', '')}")
            lines.append(f"**Definition**: {spr.get('definition', '')[:500]}...")  # Truncate
            if spr.get('zepto_spr'):
                lines.append(f"**Zepto SPR**: {spr.get('zepto_spr')}")
            lines.append("")
        
        content = "\n".join(lines)
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Exported prompt context ({file_size:.2f} MB, {len(lines)} lines)")
        
        return {
            'format': 'prompt_injection',
            'spr_count': min(1000, len(index_data)),
            'file_size_mb': file_size,
            'output_file': str(output_path),
            'exported_at': datetime.now().isoformat()
        }
    
    def create_transfer_package(self, output_dir: str = "kg_transfer_package", formats: List[str] = None) -> Dict[str, Any]:
        """
        Create comprehensive transfer package with multiple formats.
        """
        if formats is None:
            formats = ['legacy_full', 'optimized', 'zepto_minimal', 'prompt_context']
        
        print(f"📦 Creating comprehensive transfer package...")
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        results = {}
        
        # Export in requested formats
        if 'legacy_full' in formats:
            results['legacy_full'] = self.export_full_legacy_format(
                str(output_path / "kg_full_legacy.json")
            )
        
        if 'optimized' in formats:
            opt_dir = output_path / "optimized"
            opt_dir.mkdir(exist_ok=True)
            # Temporarily change output for optimized export
            old_opt = self.optimized_dir
            results['optimized'] = self.export_optimized_package(str(opt_dir))
        
        if 'zepto_minimal' in formats:
            results['zepto_minimal'] = self.export_zepto_minimal(
                str(output_path / "kg_zepto_minimal.json")
            )
        
        if 'prompt_context' in formats:
            results['prompt_context'] = self.export_for_prompt_injection(
                str(output_path / "kg_prompt_context.txt")
            )
        
        # Create package README
        readme = f"""# Knowledge Graph Transfer Package

Created: {datetime.now().isoformat()}

## Contents

This package contains the Knowledge Graph in multiple formats for different use cases:

"""
        
        for format_name, result in results.items():
            readme += f"### {format_name.replace('_', ' ').title()}\n"
            readme += f"- File: `{Path(result.get('output_file', result.get('output_dir', 'N/A'))).name}`\n"
            readme += f"- Size: {result.get('file_size_mb', result.get('total_size_mb', 'N/A')):.2f} MB\n"
            readme += f"- SPRs: {result.get('spr_count', 'N/A')}\n\n"
        
        readme += """## Usage Recommendations

- **Legacy Full**: Use with standard SPRManager (compatible with existing systems)
- **Optimized**: Use with OptimizedSPRManager (best performance, 96% memory reduction)
- **Zepto Minimal**: Use for quick transfer or when only Zepto SPRs are needed
- **Prompt Context**: Use for direct prompt injection (readable text format)

## Import Instructions

### For Legacy Format:
```python
from Three_PointO_ArchE.spr_manager import SPRManager
manager = SPRManager("kg_full_legacy.json")
```

### For Optimized Format:
```python
from Three_PointO_ArchE.spr_manager_optimized import OptimizedSPRManager
manager = OptimizedSPRManager(
    spr_filepath="optimized/spr_index.json",
    optimized_dir="optimized"
)
```
"""
        
        with open(output_path / "README.md", 'w') as f:
            f.write(readme)
        
        total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file()) / (1024 * 1024)
        print(f"  ✅ Transfer package created ({total_size:.2f} MB total)")
        
        return {
            'package_dir': str(output_path),
            'total_size_mb': total_size,
            'formats': results,
            'created_at': datetime.now().isoformat()
        }


def main():
    """Main export function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export Knowledge Graph for LLM transfer')
    parser.add_argument('--format', choices=['legacy', 'optimized', 'zepto', 'prompt', 'all'],
                       default='all', help='Export format')
    parser.add_argument('--output', type=str, help='Output file/directory')
    parser.add_argument('--kg-root', type=str, default='knowledge_graph',
                       help='Knowledge graph root directory')
    
    args = parser.parse_args()
    
    exporter = KGExporter(kg_root=args.kg_root)
    
    if args.format == 'all':
        # Create comprehensive package
        if args.output:
            output_dir = args.output
        else:
            output_dir = f"kg_transfer_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = exporter.create_transfer_package(output_dir)
        print(f"\n✅ Transfer package created: {result['package_dir']}")
        print(f"   Total size: {result['total_size_mb']:.2f} MB")
        
    elif args.format == 'legacy':
        output_file = args.output or "kg_export_full.json"
        result = exporter.export_full_legacy_format(output_file)
        print(f"\n✅ Exported: {result['output_file']}")
        
    elif args.format == 'optimized':
        output_dir = args.output or "kg_export_optimized"
        result = exporter.export_optimized_package(output_dir)
        print(f"\n✅ Exported: {result['output_dir']}")
        
    elif args.format == 'zepto':
        output_file = args.output or "kg_export_zepto_minimal.json"
        result = exporter.export_zepto_minimal(output_file)
        print(f"\n✅ Exported: {result['output_file']}")
        
    elif args.format == 'prompt':
        output_file = args.output or "kg_prompt_context.txt"
        result = exporter.export_for_prompt_injection(output_file)
        print(f"\n✅ Exported: {result['output_file']}")


if __name__ == "__main__":
    main()
