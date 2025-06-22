#!/usr/bin/env python3
"""
Test script for the SPR Action Bridge
Tests the critical bridge between SPR definitions and their implementations
"""

import sys
import os
sys.path.append('.')

from Three_PointO_ArchE.spr_action_bridge import SPRBridgeLoader, invoke_spr
from Three_PointO_ArchE.action_registry import invoke_spr_action

def test_spr_bridge_basic():
    """Test basic SPR bridge functionality"""
    print("=== Testing SPR Bridge Basic Functionality ===")
    
    # Initialize the bridge loader
    tapestry_path = "Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json"
    loader = SPRBridgeLoader(tapestry_path)
    
    # Test 1: Load tapestry
    print("Test 1: Loading Knowledge Tapestry...")
    try:
        tapestry = loader.load_tapestry()
        print(f"✅ Successfully loaded {len(tapestry)} SPRs")
        
        # Sample a few SPR IDs
        sample_sprs = list(tapestry.keys())[:5]
        print(f"Sample SPRs: {sample_sprs}")
        
    except Exception as e:
        print(f"❌ Failed to load tapestry: {e}")
        return False
    
    # Test 2: Get specific SPR definition
    print("\nTest 2: Retrieving specific SPR...")
    try:
        spr_def = loader.get_spr_definition("CognitiveresonancE")
        if spr_def:
            print(f"✅ Found CognitiveresonancE SPR")
            print(f"Definition: {spr_def.get('definition', 'No definition')[:100]}...")
            print(f"Blueprint Details: {spr_def.get('blueprint_details', 'None')}")
        else:
            print("❌ CognitiveresonancE SPR not found")
    except Exception as e:
        print(f"❌ Error retrieving SPR: {e}")
    
    # Test 3: Test with non-existent SPR
    print("\nTest 3: Testing non-existent SPR...")
    try:
        result = invoke_spr("NonExistentSPR", {}, loader)
        if result.get("status") == "error" and "not found" in str(result.get("potential_issues", [])):
            print("✅ Correctly handled non-existent SPR")
        else:
            print(f"❌ Unexpected result for non-existent SPR: {result}")
    except Exception as e:
        print(f"❌ Exception handling non-existent SPR: {e}")
    
    return True

def test_action_registry_integration():
    """Test the action registry integration"""
    print("\n=== Testing Action Registry Integration ===")
    
    try:
        # Test through action registry
        result = invoke_spr_action("CognitiveresonancE")
        print(f"Action registry result status: {result.get('status', 'No status')}")
        print(f"Bridge status: {result.get('bridge_status', 'No bridge status')}")
        
        if result.get("error_type") == "SPR_NOT_FOUND":
            print("❌ SPR not found through action registry")
        elif result.get("error_type") == "INVALID_BLUEPRINT":
            print("⚠️  SPR found but has invalid blueprint_details (expected for conceptual SPRs)")
        elif result.get("bridge_status") == "success":
            print("✅ Bridge executed successfully")
        else:
            print(f"⚠️  Bridge result: {result}")
            
    except Exception as e:
        print(f"❌ Action registry integration error: {e}")

def test_spr_with_implementation():
    """Test SPR that should have a real implementation"""
    print("\n=== Testing SPR with Implementation ===")
    
    # Look for SPRs that might have implementations
    tapestry_path = "Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json"
    loader = SPRBridgeLoader(tapestry_path)
    
    try:
        tapestry = loader.load_tapestry()
        
        # Find SPRs with blueprint_details
        sprs_with_blueprints = []
        for spr_id, spr_def in tapestry.items():
            blueprint = spr_def.get('blueprint_details', '')
            if blueprint and '/' in blueprint:
                sprs_with_blueprints.append((spr_id, blueprint))
        
        print(f"Found {len(sprs_with_blueprints)} SPRs with implementation blueprints:")
        for spr_id, blueprint in sprs_with_blueprints[:3]:  # Test first 3
            print(f"  {spr_id}: {blueprint}")
            
            # Try to invoke it
            try:
                result = invoke_spr(spr_id, {}, loader)
                status = result.get("status", "unknown")
                error_type = result.get("error_type", "none")
                print(f"    Result: {status} (error_type: {error_type})")
                
                if error_type == "MODULE_IMPORT_ERROR":
                    print(f"    ⚠️  Module not found - implementation missing")
                elif error_type == "TARGET_NOT_FOUND":
                    print(f"    ⚠️  Target function/class not found in module")
                elif status == "success" or result.get("bridge_status") == "success":
                    print(f"    ✅ Successfully executed!")
                
            except Exception as e:
                print(f"    ❌ Exception: {e}")
                
    except Exception as e:
        print(f"❌ Error testing implementations: {e}")

if __name__ == "__main__":
    print("SPR Action Bridge Test Suite")
    print("=" * 50)
    
    success = test_spr_bridge_basic()
    if success:
        test_action_registry_integration()
        test_spr_with_implementation()
    
    print("\n" + "=" * 50)
    print("Test suite completed.") 