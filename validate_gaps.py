#!/usr/bin/env python3
"""
Gap Validation Script - Jedi Principle 5: "Unlearn What You Have Learned"

Validates gaps to distinguish:
- Real gaps (need fixing)
- Protocol/workflow descriptions (already implemented)
- Enhanced implementations (update specs, don't downgrade code)
- New capabilities (create specs to match code)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

# Directories to check
SPECS_DIR = Path("specifications")
WORKFLOWS_DIR = Path("workflows")
THREE_POINT_O_DIR = Path("Three_PointO_ArchE")

# Skip list components (from ARCHE_SKIP_ALIGNMENT_COMPONENTS.md)
SKIP_COMPONENTS = {
    "strategy_fusion_workflow",
    "the_genesis_protocol",
    "universal_abstraction",
    "autopoietic_genesis_protocol",
    "workflow_catalog",
    "the_eternal_weave",
}

# Components known to be enhanced (update spec, don't downgrade code)
ENHANCED_COMPONENTS = {
    "quantum_utils",
    "enhanced_llm_provider",
    "cfp_evolution",
    "adaptive_cognitive_orchestrator",
    "phd_level_vetting_agent",
}

def check_if_workflow(component_name: str) -> Optional[Path]:
    """Check if component exists as workflow JSON."""
    patterns = [
        f"{component_name}.json",
        f"{component_name}_*.json",
        f"*{component_name}*.json",
    ]
    
    for pattern in patterns:
        matches = list(WORKFLOWS_DIR.glob(pattern))
        if matches:
            return matches[0]
    
    # Also check subdirectories
    for subdir in WORKFLOWS_DIR.iterdir():
        if subdir.is_dir():
            for pattern in patterns:
                matches = list(subdir.glob(pattern))
                if matches:
                    return matches[0]
    
    return None

def check_if_spec(component_name: str) -> Optional[Path]:
    """Check if component exists as specification markdown."""
    spec_file = SPECS_DIR / f"{component_name}.md"
    if spec_file.exists():
        return spec_file
    return None

def check_if_implemented_differently(component_name: str) -> Optional[Path]:
    """Check if component exists in codebase with different name or location."""
    # Search for Python files that might contain this functionality
    patterns = [
        f"{component_name}.py",
        f"*{component_name}*.py",
        f"{component_name.replace('_', '')}.py",
    ]
    
    for pattern in patterns:
        matches = list(THREE_POINT_O_DIR.glob(pattern))
        if matches:
            return matches[0]
    
    # Search recursively
    for py_file in THREE_POINT_O_DIR.rglob("*.py"):
        if component_name in py_file.stem.lower():
            return py_file
    
    return None

def analyze_spec_type(spec_path: Path) -> str:
    """Analyze if spec is protocol/workflow description vs code requirement."""
    with open(spec_path, 'r') as f:
        content = f.read()[:1000].lower()  # Read first 1000 chars
    
    protocol_indicators = ['protocol', 'workflow', 'process', 'procedure']
    code_indicators = ['class', 'def ', 'function', 'implementation', 'python']
    
    protocol_score = sum(1 for indicator in protocol_indicators if indicator in content)
    code_score = sum(1 for indicator in code_indicators if indicator in content)
    
    if protocol_score > code_score:
        return "protocol"
    elif code_score > protocol_score:
        return "code_requirement"
    else:
        return "unclear"

def validate_gap(gap: Dict) -> Dict[str, any]:
    """
    Validate a single gap and categorize it.
    
    Returns validation result with category and recommendation.
    """
    component_name = gap.get('component_name', '')
    gap_type = gap.get('gap_type', '')
    spec_path = gap.get('specification_path', '')
    
    result = {
        'component_name': component_name,
        'original_gap_type': gap_type,
        'category': 'unknown',
        'reason': '',
        'recommendation': '',
        'evidence': {}
    }
    
    # Check skip list
    if component_name in SKIP_COMPONENTS:
        result['category'] = 'skip_list'
        result['reason'] = 'Component in skip list (already evolved/implemented)'
        result['recommendation'] = 'SKIP - Do not fix'
        return result
    
    # Check if enhanced component
    if component_name in ENHANCED_COMPONENTS:
        result['category'] = 'enhanced_implementation'
        result['reason'] = 'Component has evolved beyond original spec'
        result['recommendation'] = 'UPDATE SPEC to match evolved code (do not downgrade code)'
        return result
    
    # Check if workflow exists
    workflow_path = check_if_workflow(component_name)
    if workflow_path:
        result['category'] = 'workflow_exists'
        result['reason'] = f'Component exists as workflow JSON: {workflow_path}'
        result['recommendation'] = 'SKIP - Already implemented as workflow'
        result['evidence']['workflow_path'] = str(workflow_path)
        return result
    
    # Check if spec exists and analyze type
    if spec_path:
        spec_file = Path(spec_path)
        if spec_file.exists():
            spec_type = analyze_spec_type(spec_file)
            if spec_type == 'protocol':
                result['category'] = 'protocol_spec'
                result['reason'] = 'Specification is protocol/workflow description, not Python code requirement'
                result['recommendation'] = 'SKIP - Implemented as protocol documentation'
                result['evidence']['spec_type'] = spec_type
                return result
    
    # Check if implemented differently
    impl_path = check_if_implemented_differently(component_name)
    if impl_path:
        result['category'] = 'exists_differently'
        result['reason'] = f'Functionality may exist in: {impl_path}'
        result['recommendation'] = 'VERIFY - Check if this file contains the required functionality'
        result['evidence']['implementation_path'] = str(impl_path)
        return result
    
    # Check if it's a "missing" or "missing_implementation" gap
    if gap_type in ['missing', 'missing_implementation']:
        # Check if spec requires Python code
        if spec_path:
            spec_file = Path(spec_path)
            if spec_file.exists():
                spec_type = analyze_spec_type(spec_file)
                if spec_type == 'code_requirement':
                    result['category'] = 'genuine_missing'
                    result['reason'] = 'Specification requires Python implementation and it does not exist'
                    result['recommendation'] = 'FIX - Implement according to specification'
                    result['evidence']['spec_type'] = spec_type
                    return result
    
    # Default: needs verification
    result['category'] = 'needs_verification'
    result['reason'] = 'Requires manual review to determine if genuine gap'
    result['recommendation'] = 'VERIFY - Review specification and codebase before fixing'
    
    return result

def main():
    """Load gaps and validate them."""
    print("🔍 GAP VALIDATION - Jedi Principle 5: 'Unlearn What You Have Learned'")
    print("=" * 70)
    
    # Load gap analysis
    gap_file = Path("ARCHE_GAP_ANALYSIS_FINAL.json")
    if not gap_file.exists():
        print(f"❌ Gap analysis file not found: {gap_file}")
        return
    
    with open(gap_file, 'r') as f:
        data = json.load(f)
    
    gaps_str = data.get('gaps', '')
    if isinstance(gaps_str, str):
        try:
            gaps_data = json.loads(gaps_str)
            gaps = gaps_data.get('gaps', [])
        except:
            print("❌ Failed to parse gaps JSON string")
            return
    else:
        gaps = gaps_str
    
    if not gaps:
        print("⚠️  No gaps found in analysis")
        return
    
    # Filter for critical and missing gaps
    critical_gaps = [g for g in gaps if isinstance(g, dict) and g.get('severity') == 'critical']
    missing_gaps = [g for g in gaps if isinstance(g, dict) and g.get('gap_type') in ['missing', 'missing_implementation']]
    
    print(f"\n📊 Gap Summary:")
    print(f"  Total gaps: {len(gaps)}")
    print(f"  Critical gaps: {len(critical_gaps)}")
    print(f"  Missing implementations: {len(missing_gaps)}")
    
    # Validate gaps
    print(f"\n🔍 Validating Gaps...")
    print("-" * 70)
    
    validation_results = []
    
    # Validate critical gaps first (these may include missing implementations)
    gaps_to_validate = critical_gaps if critical_gaps else missing_gaps
    if not gaps_to_validate and gaps:
        # If no critical/missing found, try all gaps
        gaps_to_validate = gaps[:31]
    
    print(f"Validating {len(gaps_to_validate)} gaps...")
    
    # Validate gaps (prioritize critical/missing)
    for gap in gaps_to_validate[:31]:  # Top 31
        result = validate_gap(gap)
        validation_results.append(result)
        
        category_icon = {
            'skip_list': '⏭️ ',
            'workflow_exists': '✅',
            'protocol_spec': '✅',
            'enhanced_implementation': '🔄',
            'exists_differently': '⚠️ ',
            'genuine_missing': '❌',
            'needs_verification': '🔍'
        }.get(result['category'], '❓')
        
        print(f"{category_icon} {result['component_name']}: {result['category']}")
        if result['reason']:
            print(f"     {result['reason']}")
    
    # Categorize results
    categories = {}
    for result in validation_results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result['component_name'])
    
    print(f"\n📋 Validation Summary:")
    print("-" * 70)
    for category, components in categories.items():
        print(f"  {category}: {len(components)}")
        for comp in components[:5]:
            print(f"    - {comp}")
        if len(components) > 5:
            print(f"    ... and {len(components) - 5} more")
    
    # Convert Path objects to strings in results
    for result in validation_results:
        if 'evidence' in result:
            for key, value in result['evidence'].items():
                if isinstance(value, Path):
                    result['evidence'][key] = str(value)
    
    # Save validation results
    output_file = Path("ARCHE_GAP_VALIDATION_RESULTS.json")
    with open(output_file, 'w') as f:
        json.dump({
            'validation_timestamp': str(Path().cwd()),
            'total_validated': len(validation_results),
            'categories': categories,
            'detailed_results': validation_results
        }, f, indent=2)
    
    print(f"\n📄 Validation results saved to: {output_file}")
    
    # Calculate real gaps
    genuine_gaps = [r for r in validation_results if r['category'] in ['genuine_missing', 'needs_verification']]
    skip_gaps = [r for r in validation_results if r['category'] in ['skip_list', 'workflow_exists', 'protocol_spec']]
    
    print(f"\n🎯 Action Required:")
    print(f"  ❌ Genuine gaps to fix: {len(genuine_gaps)}")
    print(f"  ⏭️  Can skip (not missing): {len(skip_gaps)}")
    print(f"  🔄 Update specs (evolved): {len([r for r in validation_results if r['category'] == 'enhanced_implementation'])}")

if __name__ == '__main__':
    main()

