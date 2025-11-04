#!/usr/bin/env python3
"""
Comprehensive Test Suite for Playwright-Based Communication Bridge
===================================================================

Tests the enhanced Cursor ArchE provider with Playwright monitoring capabilities.
"""
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test results tracker
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_result(test_name: str, passed: bool, message: str = "", warning: bool = False):
    """Record a test result."""
    if warning:
        test_results["warnings"].append(f"{test_name}: {message}")
        logger.warning(f"⚠ {test_name}: {message}")
    elif passed:
        test_results["passed"].append(test_name)
        logger.info(f"✓ {test_name}: {message or 'PASSED'}")
    else:
        test_results["failed"].append(f"{test_name}: {message}")
        logger.error(f"✗ {test_name}: {message}")

print("\n" + "="*80)
print("PLAYWRIGHT COMMUNICATION BRIDGE TEST SUITE")
print("="*80 + "\n")

# TEST 1: Check Playwright Installation
print("[TEST 1] Checking Playwright Installation...")
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
    test_result("Playwright Import", True, "Playwright is available")
except ImportError as e:
    PLAYWRIGHT_AVAILABLE = False
    test_result("Playwright Import", False, f"Playwright not available: {e}", warning=True)
    logger.warning("Some tests will be skipped or use fallback modes")

# TEST 2: Import Enhanced Provider
print("\n[TEST 2] Importing Enhanced Cursor ArchE Provider...")
try:
    from Three_PointO_ArchE.llm_providers.cursor_arche_enhanced import CursorArchEProviderEnhanced
    test_result("Provider Import", True, "Successfully imported CursorArchEProviderEnhanced")
except ImportError as e:
    test_result("Provider Import", False, f"Failed to import: {e}")
    sys.exit(1)

# TEST 3: Initialize Enhanced Provider
print("\n[TEST 3] Initializing Enhanced Provider...")
try:
    provider = CursorArchEProviderEnhanced(enable_playwright=PLAYWRIGHT_AVAILABLE)
    test_result("Provider Initialization", True, "Provider initialized successfully")
    
    # Check communication directory structure
    comm_dir = provider.comm_dir
    if comm_dir.exists():
        test_result("Communication Directory", True, f"Directory exists: {comm_dir}")
    else:
        test_result("Communication Directory", False, f"Directory not found: {comm_dir}")
    
    # Check subdirectories
    if (comm_dir / "requests").exists():
        test_result("Requests Directory", True)
    else:
        test_result("Requests Directory", False, "Requests directory not created")
    
    if (comm_dir / "responses").exists():
        test_result("Responses Directory", True)
    else:
        test_result("Responses Directory", False, "Responses directory not created")
    
    # Check queue file
    if provider.queue_file.exists():
        test_result("Queue File", True, f"Queue file exists: {provider.queue_file}")
    else:
        test_result("Queue File", False, f"Queue file not found: {provider.queue_file}")
        
except Exception as e:
    test_result("Provider Initialization", False, f"Failed: {e}")
    sys.exit(1)

# TEST 4: Create Test Request
print("\n[TEST 4] Creating Test Request...")
try:
    test_prompt = "This is a test prompt for the Playwright communication bridge test."
    test_context = {
        "test_id": "playwright_bridge_test",
        "timestamp": time.time(),
        "priority": "high"
    }
    
    request_id = provider._create_request_file(test_prompt, test_context)
    test_result("Request Creation", True, f"Request ID: {request_id}")
    
    # Verify request file exists
    request_file = provider.requests_dir / f"{request_id}.json"
    if request_file.exists():
        test_result("Request File Exists", True, f"File: {request_file}")
        
        # Verify request content
        with open(request_file, 'r') as f:
            request_data = json.load(f)
        
        if request_data.get("prompt") == test_prompt:
            test_result("Request Content", True, "Prompt matches")
        else:
            test_result("Request Content", False, "Prompt mismatch")
        
        if request_data.get("status") == "pending":
            test_result("Request Status", True, "Status is 'pending'")
        else:
            test_result("Request Status", False, f"Unexpected status: {request_data.get('status')}")
    else:
        test_result("Request File Exists", False, f"File not found: {request_file}")
        
except Exception as e:
    test_result("Request Creation", False, f"Failed: {e}")

# TEST 5: Queue Management
print("\n[TEST 5] Testing Queue Management...")
try:
    # Read queue
    with open(provider.queue_file, 'r') as f:
        queue_data = json.load(f)
    
    pending = queue_data.get("pending_requests", [])
    if len(pending) > 0:
        test_result("Queue Has Pending", True, f"Found {len(pending)} pending request(s)")
    else:
        test_result("Queue Has Pending", False, "No pending requests in queue")
    
    # Check if our request is in the queue
    if request_id in pending:
        test_result("Request In Queue", True, "Request ID found in queue")
    else:
        test_result("Request In Queue", False, "Request ID not found in queue")
        
except Exception as e:
    test_result("Queue Management", False, f"Failed: {e}")

# TEST 6: Playwright Browser Initialization (if available)
if PLAYWRIGHT_AVAILABLE:
    print("\n[TEST 6] Testing Playwright Browser Initialization...")
    try:
        initialized = provider._initialize_playwright()
        if initialized:
            test_result("Playwright Init", True, "Playwright browser initialized")
            
            # Test that browser and page exist
            if provider._browser:
                test_result("Browser Instance", True, "Browser instance created")
            else:
                test_result("Browser Instance", False, "Browser instance is None")
            
            if provider._page:
                test_result("Page Instance", True, "Page instance created")
            else:
                test_result("Page Instance", False, "Page instance is None")
            
            # Clean up
            provider._cleanup_playwright()
            test_result("Playwright Cleanup", True, "Resources cleaned up")
        else:
            test_result("Playwright Init", False, "Failed to initialize Playwright")
    except Exception as e:
        test_result("Playwright Init", False, f"Exception: {e}")
else:
    print("\n[TEST 6] Skipping Playwright Tests (not available)")

# TEST 7: Import Monitor Service
print("\n[TEST 7] Importing Monitor Service...")
try:
    from Three_PointO_ArchE.llm_providers.cursor_arche_monitor import CursorArchERequestMonitor
    test_result("Monitor Import", True, "Monitor service imported")
except ImportError as e:
    test_result("Monitor Import", False, f"Failed to import: {e}")

# TEST 8: Initialize Monitor Service
print("\n[TEST 8] Initializing Monitor Service...")
try:
    monitor = CursorArchERequestMonitor(comm_dir=provider.comm_dir)
    test_result("Monitor Initialization", True, "Monitor initialized")
    
    # Check that monitor uses same comm directory
    if monitor.comm_dir == provider.comm_dir:
        test_result("Monitor Comm Dir", True, "Monitor uses correct comm directory")
    else:
        test_result("Monitor Comm Dir", False, "Comm directory mismatch")
        
except Exception as e:
    test_result("Monitor Initialization", False, f"Failed: {e}")

# TEST 9: Monitor Get Pending Requests
print("\n[TEST 9] Testing Monitor Request Detection...")
try:
    pending = monitor.get_pending_requests()
    if isinstance(pending, list):
        test_result("Get Pending Requests", True, f"Found {len(pending)} pending request(s)")
    else:
        test_result("Get Pending Requests", False, f"Unexpected return type: {type(pending)}")
        
except Exception as e:
    test_result("Get Pending Requests", False, f"Failed: {e}")

# TEST 10: Provider Direct Execution (if in Cursor)
print("\n[TEST 10] Testing Direct Execution Path...")
try:
    # Check if we're in Cursor environment
    in_cursor = provider._is_cursor_environment
    if in_cursor:
        test_result("Cursor Detection", True, "Running in Cursor environment")
        
        # Try direct execution
        test_prompt = "Respond with 'TEST PASSED' if you receive this."
        try:
            from Three_PointO_ArchE.llm_tool import execute_arche_analysis
            response = execute_arche_analysis(test_prompt, {"test": True})
            if response:
                test_result("Direct Execution", True, f"Response received: {response[:50]}...")
            else:
                test_result("Direct Execution", False, "Empty response")
        except Exception as e:
            test_result("Direct Execution", False, f"Failed: {e}", warning=True)
    else:
        test_result("Cursor Detection", False, "Not in Cursor environment (expected for file-based testing)")
        
except Exception as e:
    test_result("Direct Execution Test", False, f"Exception: {e}", warning=True)

# TEST 11: Generate Method (Full Flow)
print("\n[TEST 11] Testing Full Generation Flow...")
try:
    test_prompt = "What is 2+2? Respond with just the number."
    
    # Try generation with enhanced provider
    # This will attempt direct execution first, then fall back to file-based
    response = provider.generate(test_prompt, max_tokens=100)
    
    if response:
        test_result("Generate Method", True, f"Response received: {response[:100]}...")
    else:
        test_result("Generate Method", False, "No response received", warning=True)
        
except Exception as e:
    test_result("Generate Method", False, f"Failed: {e}", warning=True)

# TEST 12: Cleanup Test Resources
print("\n[TEST 12] Cleaning Up Test Resources...")
try:
    # Clean up test request file
    if 'request_id' in locals():
        request_file = provider.requests_dir / f"{request_id}.json"
        if request_file.exists():
            request_file.unlink()
            test_result("Test Request Cleanup", True, "Test request file removed")
    
    # Clean up provider Playwright resources
    if provider._browser or provider._playwright:
        provider._cleanup_playwright()
    
    # Clean up monitor Playwright resources
    if monitor._browser or monitor._playwright:
        monitor._cleanup_playwright()
    
    test_result("Resource Cleanup", True, "All resources cleaned up")
    
except Exception as e:
    test_result("Resource Cleanup", False, f"Failed: {e}")

# FINAL SUMMARY
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"✓ Passed: {len(test_results['passed'])}")
print(f"✗ Failed: {len(test_results['failed'])}")
print(f"⚠ Warnings: {len(test_results['warnings'])}")
print()

if test_results['passed']:
    print("PASSED TESTS:")
    for test in test_results['passed']:
        print(f"  ✓ {test}")

if test_results['failed']:
    print("\nFAILED TESTS:")
    for test in test_results['failed']:
        print(f"  ✗ {test}")

if test_results['warnings']:
    print("\nWARNINGS:")
    for warning in test_results['warnings']:
        print(f"  ⚠ {warning}")

print("\n" + "="*80)

# Exit with appropriate code
if test_results['failed']:
    sys.exit(1)
elif test_results['warnings']:
    sys.exit(0)  # Warnings don't fail the test
else:
    print("\n🎉 ALL TESTS PASSED!")
    sys.exit(0)

