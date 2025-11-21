#!/usr/bin/env python3
"""
Test script to verify quota tracker accumulates usage correctly.
"""

import os
import sys
sys.path.insert(0, '.')

from Three_PointO_ArchE.llm_providers.quota_tracker import get_quota_tracker
from datetime import datetime, timedelta

def test_quota_accumulation():
    """Test that quota tracker accumulates usage and persists it."""
    
    print("=" * 70)
    print("Testing Quota Tracker Accumulation")
    print("=" * 70)
    print()
    
    tracker = get_quota_tracker()
    
    # Register a test key
    tracker.register_api_key(
        provider="groq",
        api_key_id="groq_key_1",
        limits={"tokens_per_day": 100000}
    )
    
    # Record some usage
    print("Recording usage...")
    tracker.record_usage(
        provider="groq",
        api_key_id="groq_key_1",
        limit_type="tokens_per_day",
        amount=5000,
        reset_time=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    )
    
    # Get summary
    summary = tracker.get_usage_summary(provider="groq")
    print("\nAfter first usage:")
    print(f"  Used: {summary['groq']['groq_key_1']['tokens_per_day']['used']:.0f}")
    print(f"  Remaining: {summary['groq']['groq_key_1']['tokens_per_day']['remaining']:.0f}")
    
    # Record more usage
    print("\nRecording more usage...")
    tracker.record_usage(
        provider="groq",
        api_key_id="groq_key_1",
        limit_type="tokens_per_day",
        amount=3000,
        reset_time=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    )
    
    # Get summary again
    summary = tracker.get_usage_summary(provider="groq")
    print("\nAfter second usage:")
    print(f"  Used: {summary['groq']['groq_key_1']['tokens_per_day']['used']:.0f}")
    print(f"  Remaining: {summary['groq']['groq_key_1']['tokens_per_day']['remaining']:.0f}")
    
    # Verify accumulation
    expected_total = 5000 + 3000
    actual_total = summary['groq']['groq_key_1']['tokens_per_day']['used']
    
    print("\n" + "=" * 70)
    if abs(actual_total - expected_total) < 0.01:
        print("✅ SUCCESS: Usage accumulated correctly!")
        print(f"   Expected: {expected_total:.0f}, Got: {actual_total:.0f}")
    else:
        print("❌ FAILED: Usage not accumulating correctly")
        print(f"   Expected: {expected_total:.0f}, Got: {actual_total:.0f}")
    print("=" * 70)
    
    # Check persistence file
    print(f"\nStorage file: {tracker.storage_path}")
    if os.path.exists(tracker.storage_path):
        print("✅ Storage file exists")
        import json
        with open(tracker.storage_path, 'r') as f:
            data = json.load(f)
            if 'groq' in data and 'groq_key_1_tokens_per_day' in data['groq']:
                stored_used = data['groq']['groq_key_1_tokens_per_day']['used_value']
                print(f"✅ Stored usage: {stored_used:.0f}")
            else:
                print("⚠️  Usage not found in storage file")

if __name__ == "__main__":
    test_quota_accumulation()

