#!/usr/bin/env python3
"""
Extract and display codebase patterns found during Phase B of RISE execution
"""

import re
import json
from pathlib import Path

def extract_patterns_from_log(log_file):
    """Extract pattern search queries and results from log"""
    patterns_found = []
    current_query = None
    
    with open(log_file, 'r') as f:
        for line in f:
            # Find search queries
            if "Searching codebase for patterns:" in line:
                match = re.search(r"'([^']+)' \(types:", line)
                if match:
                    current_query = match.group(1)
                    patterns_found.append({
                        'query': current_query,
                        'type': 'search_query',
                        'timestamp': line.split(' - ')[0] if ' - ' in line else ''
                    })
            
            # Find synthesis results
            if "Synthesizing solution from" in line:
                match = re.search(r'from (\d+) patterns', line)
                if match:
                    count = match.group(1)
                    patterns_found.append({
                        'type': 'synthesis',
                        'pattern_count': int(count),
                        'timestamp': line.split(' - ')[0] if ' - ' in line else ''
                    })
            
            # Find completion messages
            if "Synthesized solution from" in line:
                match = re.search(r'from (\d+) codebase patterns', line)
                if match:
                    count = match.group(1)
                    patterns_found.append({
                        'type': 'completion',
                        'pattern_count': int(count),
                        'timestamp': line.split(' - ')[0] if ' - ' in line else ''
                    })
    
    return patterns_found

def display_patterns(patterns):
    """Display extracted patterns in a readable format"""
    print("=" * 80)
    print("🏛️ CODEBASE PATTERNS FOUND IN PHASE B - RISE-SRCS EXECUTION")
    print("=" * 80)
    print()
    
    queries = [p for p in patterns if p['type'] == 'search_query']
    synthesis = [p for p in patterns if p['type'] == 'synthesis']
    completion = [p for p in patterns if p['type'] == 'completion']
    
    print("📋 SEARCH QUERIES EXECUTED:")
    print("-" * 80)
    for i, query_info in enumerate(queries, 1):
        print(f"{i}. Query: \"{query_info['query']}\"")
        print(f"   Timestamp: {query_info['timestamp']}")
        print()
    
    if synthesis:
        print("🔄 SYNTHESIS OPERATION:")
        print("-" * 80)
        for synth in synthesis:
            print(f"   Patterns synthesized: {synth['pattern_count']}")
            print(f"   Timestamp: {synth['timestamp']}")
            print()
    
    if completion:
        print("✅ COMPLETION STATUS:")
        print("-" * 80)
        for comp in completion:
            print(f"   Total patterns processed: {comp['pattern_count']}")
            print(f"   Timestamp: {comp['timestamp']}")
            print()
    
    print("=" * 80)
    print("SUMMARY:")
    print(f"  - Total search queries: {len(queries)}")
    if synthesis:
        print(f"  - Patterns synthesized: {synthesis[0]['pattern_count']}")
    if completion:
        print(f"  - Patterns completed: {completion[0]['pattern_count']}")
    print("=" * 80)

if __name__ == "__main__":
    log_file = Path("/mnt/3626C55326C514B1/Happier/rise_execution_output.log")
    
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        exit(1)
    
    print(f"📂 Reading log file: {log_file}")
    patterns = extract_patterns_from_log(log_file)
    display_patterns(patterns)

