#!/usr/bin/env python3
"""
Check Session State
Display current session information and help diagnose session issues.
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    print("🔍 ArchE Session State Checker")
    print("=" * 50)
    
    # Check session state file
    session_file = Path("session_state.json")
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            print(f"📁 Session file found: {session_file}")
            print(f"📊 Total sessions: {len(session_data)}")
            print()
            
            if session_data:
                print("📋 Active Sessions:")
                print("-" * 50)
                
                for session_id, session_info in session_data.items():
                    created_time = session_info.get('created_time', 0)
                    last_accessed = session_info.get('last_accessed', 0)
                    access_count = session_info.get('access_count', 0)
                    
                    created_str = datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S')
                    last_str = datetime.fromtimestamp(last_accessed).strftime('%Y-%m-%d %H:%M:%S')
                    
                    print(f"Session ID: {session_id}")
                    print(f"  Problem: {session_info.get('problem_description', 'N/A')[:50]}...")
                    print(f"  Created: {created_str}")
                    print(f"  Last Access: {last_str}")
                    print(f"  Access Count: {access_count}")
                    print(f"  User ID: {session_info.get('user_id', 'N/A')}")
                    print()
            else:
                print("📭 No active sessions found")
                
        except Exception as e:
            print(f"❌ Error reading session file: {e}")
    else:
        print("📭 No session state file found")
        print("   This is normal if no sessions have been created yet.")
    
    # Check for any running processes
    print("\n🔍 Checking for running ArchE processes...")
    try:
        import subprocess
        result = subprocess.run([
            "ps", "aux"
        ], capture_output=True, text=True)
        
        archE_processes = []
        for line in result.stdout.split('\n'):
            if 'arche' in line.lower() or 'rise' in line.lower():
                if 'python' in line or 'node' in line:
                    archE_processes.append(line.strip())
        
        if archE_processes:
            print("🔄 Running ArchE processes:")
            for process in archE_processes[:5]:  # Show first 5
                print(f"  {process}")
            if len(archE_processes) > 5:
                print(f"  ... and {len(archE_processes) - 5} more")
        else:
            print("✅ No ArchE processes currently running")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
    
    print("\n💡 Session Management Tips:")
    print("   - Session IDs are now stable and based on problem content")
    print("   - Same problem = Same session ID")
    print("   - Different problems = Different session IDs")
    print("   - Sessions expire after 1 hour of inactivity")
    print("   - Use 'python start_stable_session.py' to start with stable sessions")

if __name__ == "__main__":
    main() 