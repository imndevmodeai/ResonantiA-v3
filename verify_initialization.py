#!/usr/bin/env python3
"""
Initialization Verification Script for ArchE Protocol
Verifies all components required for proper session initialization
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def check_virtual_env():
    """Check if virtual environment is activated"""
    venv_path = Path('arche_env/bin/activate')
    if venv_path.exists():
        return True, f"Virtual environment found at: {venv_path}"
    return False, "Virtual environment not found. Run: source arche_env/bin/activate"

def check_file_paths():
    """Verify all referenced file paths exist"""
    required_files = [
        'protocol/ResonantiA_Protocol_v3.5-GP_Canonical.md',
        'protocol/CURRENT_STATE_v3.5-GP.md',
        'protocol/KNO_STATE_UPDATE_v3.5-GP.md',
        'Three_PointO_ArchE/spr_manager.py',
        'Three_PointO_ArchE/workflow_engine.py',
        'knowledge_graph/spr_definitions_tv.json',
    ]
    
    results = {}
    for file_path in required_files:
        path = Path(file_path)
        results[file_path] = path.exists()
    
    return results

def verify_spr_loading():
    """Verify SPR definitions can be loaded"""
    spr_file = Path('knowledge_graph/spr_definitions_tv.json')
    
    if not spr_file.exists():
        return False, "SPR definitions file not found"
    
    try:
        with open(spr_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_sprs = len(data) if isinstance(data, list) else 0
        categories = set()
        
        if isinstance(data, list):
            for spr in data:
                if 'category' in spr:
                    categories.add(spr['category'])
        
        return True, {
            'total_sprs': total_sprs,
            'categories': len(categories),
            'status': 'loaded'
        }
    except Exception as e:
        return False, f"Error loading SPRs: {str(e)}"

def verify_system_components():
    """Verify system components are accessible"""
    components = {
        'SPRManager': 'Three_PointO_ArchE.spr_manager',
        'WorkflowEngine': 'Three_PointO_ArchE.workflow_engine',
        'PatternCrystallizationEngine': 'Three_PointO_ArchE.pattern_crystallization_engine',
    }
    
    results = {}
    for component_name, module_path in components.items():
        try:
            __import__(module_path)
            results[component_name] = True
        except ImportError as e:
            results[component_name] = False
            results[f'{component_name}_error'] = str(e)
    
    return results

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("ArchE Protocol Initialization Verification")
    print("=" * 70)
    print()
    
    # Check virtual environment
    print("1. Virtual Environment Check:")
    venv_ok, venv_msg = check_virtual_env()
    status = "✓" if venv_ok else "✗"
    print(f"   {status} {venv_msg}")
    print()
    
    # Check file paths
    print("2. File Path Verification:")
    file_results = check_file_paths()
    all_files_ok = all(file_results.values())
    for file_path, exists in file_results.items():
        status = "✓" if exists else "✗"
        print(f"   {status} {file_path}")
    print()
    
    # Verify SPR loading
    print("3. SPR Definitions Verification:")
    spr_ok, spr_data = verify_spr_loading()
    if spr_ok and isinstance(spr_data, dict):
        print(f"   ✓ SPR definitions loaded successfully")
        print(f"     Total SPRs: {spr_data['total_sprs']}")
        print(f"     Categories: {spr_data['categories']}")
    else:
        print(f"   ✗ {spr_data}")
    print()
    
    # Verify system components
    print("4. System Components Verification:")
    component_results = verify_system_components()
    for component, status in component_results.items():
        if not component.endswith('_error'):
            status_symbol = "✓" if status else "✗"
            print(f"   {status_symbol} {component}")
            if not status and f'{component}_error' in component_results:
                print(f"      Error: {component_results[f'{component}_error']}")
    print()
    
    # Summary
    print("=" * 70)
    print("Verification Summary:")
    print("=" * 70)
    
    all_checks = [
        ("Virtual Environment", venv_ok),
        ("File Paths", all_files_ok),
        ("SPR Loading", spr_ok),
        ("System Components", all(v for k, v in component_results.items() if not k.endswith('_error')))
    ]
    
    all_passed = all(check[1] for check in all_checks)
    
    for check_name, check_result in all_checks:
        status = "PASS" if check_result else "FAIL"
        print(f"  {status}: {check_name}")
    
    print()
    if all_passed:
        print("✓ All verification checks passed. System ready for initialization.")
        return 0
    else:
        print("✗ Some verification checks failed. Please resolve issues before proceeding.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

