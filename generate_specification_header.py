#!/usr/bin/env python3
"""
Specification Header Generator

Generates the canonical header for ArchE specification documents,
using temporal_core to ensure accurate, UTC-based timestamps.

Usage:
    python generate_specification_header.py --title "Workflow Name" --type workflow
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.temporal_core import now_iso, format_human

def generate_header(title: str, spec_type: str = "workflow") -> str:
    """
    Generate a specification header with accurate temporal metadata.
    
    Args:
        title: The title of the specification
        spec_type: Type of spec (workflow, component, tool, system)
        
    Returns:
        str: Formatted header using temporal_core
    """
    timestamp_iso = now_iso()
    timestamp_human = format_human(timestamp_iso)
    
    header = f"""# {title}

**Date**: {timestamp_human}  
**Type**: {spec_type.upper()}  
**Status**: ✅ ACTIVE  
**Temporal Metadata**: Generated at `{timestamp_iso}`

---

## Canonical Chronicle Piece

[Insert narrative here...]

---

## Technical Implementation

[Insert technical details here...]

---

**Specification Status**: ✅ COMPLETE  
**Last Updated**: {timestamp_iso}  
**Version**: 1.0  
**Maintainer**: Guardian + ArchE (Collaborative)

---

> Generated using temporal_core v1.0 - All timestamps are UTC
"""
    
    return header


def main():
    parser = argparse.ArgumentParser(description="Generate specification header with temporal_core")
    parser.add_argument("--title", type=str, required=True, help="Specification title")
    parser.add_argument("--type", type=str, default="workflow", help="Specification type")
    parser.add_argument("--output", type=str, help="Output file path (optional)")
    
    args = parser.parse_args()
    
    header = generate_header(args.title, args.type)
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(header)
        print(f"✅ Header written to: {output_path}")
    else:
        print(header)
    
    # Also print the raw timestamp for verification
    from Three_PointO_ArchE.temporal_core import now_iso
    print(f"\n⏰ Current UTC time: {now_iso()}")


if __name__ == "__main__":
    main()

