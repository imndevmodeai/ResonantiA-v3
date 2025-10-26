#!/usr/bin/env python3
"""
ArchE Log Viewer - Comprehensive log access and analysis tool
"""

import os
import sys
import json
import glob
from datetime import datetime
from pathlib import Path

def show_log_locations():
    """Show all available log locations and their purposes"""
    print("🔍 ARCH E LOG LOCATIONS")
    print("=" * 60)
    
    # Main log directories
    log_dirs = {
        "logs/": "Main ArchE system logs",
        "outputs/": "Execution outputs and results", 
        "outputs/models/": "Saved model artifacts",
        "outputs/reports/": "Generated analysis reports"
    }
    
    for log_dir, description in log_dirs.items():
        if os.path.exists(log_dir):
            files = glob.glob(f"{log_dir}*")
            print(f"\n📁 {log_dir} - {description}")
            print(f"   Files: {len(files)}")
            if files:
                # Show recent files (handle problematic files)
                valid_files = []
                for f in files:
                    try:
                        os.path.getmtime(f)
                        valid_files.append(f)
                    except OSError:
                        continue  # Skip problematic files
                
                recent_files = sorted(valid_files, key=os.path.getmtime, reverse=True)[:3]
                for f in recent_files:
                    try:
                        size = os.path.getsize(f)
                        mtime = datetime.fromtimestamp(os.path.getmtime(f))
                        print(f"   • {os.path.basename(f)} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
                    except OSError:
                        print(f"   • {os.path.basename(f)} (file info unavailable)")
        else:
            print(f"\n📁 {log_dir} - {description} (not found)")

def show_recent_logs():
    """Show the most recent log entries"""
    print("\n🕒 RECENT LOG ENTRIES")
    print("=" * 60)
    
    # Check main system log
    main_log = "logs/arche_system.log"
    if os.path.exists(main_log):
        print(f"\n📋 {main_log} (last 20 lines):")
        print("-" * 40)
        try:
            with open(main_log, 'r') as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(line.strip())
        except Exception as e:
            print(f"Error reading log: {e}")
    
    # Check outputs log
    outputs_log = "outputs/arche_system.log"
    if os.path.exists(outputs_log):
        print(f"\n📋 {outputs_log} (last 20 lines):")
        print("-" * 40)
        try:
            with open(outputs_log, 'r') as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(line.strip())
        except Exception as e:
            print(f"Error reading log: {e}")

def show_semiconductor_analysis_logs():
    """Show logs specifically from the semiconductor analysis"""
    print("\n🔬 SEMICONDUCTOR ANALYSIS LOGS")
    print("=" * 60)
    
    # Check for semiconductor data
    if os.path.exists("semiconductor_shortage_data.csv"):
        print("✅ Semiconductor dataset found:")
        print(f"   File: semiconductor_shortage_data.csv")
        print(f"   Size: {os.path.getsize('semiconductor_shortage_data.csv'):,} bytes")
        print(f"   Modified: {datetime.fromtimestamp(os.path.getmtime('semiconductor_shortage_data.csv')).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show sample data
        print("\n📊 Sample data:")
        try:
            with open("semiconductor_shortage_data.csv", 'r') as f:
                lines = f.readlines()
                print("   " + lines[0].strip())  # Header
                for line in lines[1:4]:  # First 3 data rows
                    print("   " + line.strip())
        except Exception as e:
            print(f"   Error reading data: {e}")
    
    # Check for analysis workflow files
    workflow_files = [
        "semiconductor_analysis_workflow.json",
        "run_semiconductor_analysis.py"
    ]
    
    print("\n📋 Analysis workflow files:")
    for file in workflow_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            mtime = datetime.fromtimestamp(os.path.getmtime(file))
            print(f"   ✅ {file} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"   ❌ {file} (not found)")

def show_execution_summary():
    """Show summary of recent executions"""
    print("\n📈 EXECUTION SUMMARY")
    print("=" * 60)
    
    # Find recent log files
    recent_logs = []
    for log_dir in ["logs/", "outputs/"]:
        if os.path.exists(log_dir):
            for file in glob.glob(f"{log_dir}*.log"):
                mtime = os.path.getmtime(file)
                recent_logs.append((file, mtime))
    
    # Sort by modification time
    recent_logs.sort(key=lambda x: x[1], reverse=True)
    
    print("Recent log files (last 10):")
    for file, mtime in recent_logs[:10]:
        size = os.path.getsize(file)
        dt = datetime.fromtimestamp(mtime)
        print(f"   {dt.strftime('%Y-%m-%d %H:%M')} - {file} ({size:,} bytes)")

def main():
    """Main function"""
    print("🔍 ARCH E LOG VIEWER")
    print("=" * 60)
    print(f"Current directory: {os.getcwd()}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    show_log_locations()
    show_recent_logs()
    show_semiconductor_analysis_logs()
    show_execution_summary()
    
    print("\n" + "=" * 60)
    print("💡 TIPS:")
    print("• Use 'tail -f logs/arche_system.log' to follow live logs")
    print("• Check 'outputs/' directory for execution results")
    print("• Look for files with today's date for recent runs")
    print("• Use 'grep' to search for specific terms in logs")

if __name__ == "__main__":
    main()
