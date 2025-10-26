#!/usr/bin/env python3
"""
VCD-Enhanced ArchE Launcher
This script starts the VCD system and then runs ask_arche.py with VCD integration.
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def main():
    print("🚀 Starting VCD-Enhanced ArchE System...")
    
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir
    
    print(f"📁 Project root: {project_root}")
    
    # Check if VCD bridge exists
    vcd_bridge_path = project_root / "vcd_bridge.py"
    if not vcd_bridge_path.exists():
        print("❌ VCD Bridge not found. Please ensure vcd_bridge.py exists.")
        return 1
    
    # Check if ask_arche.py exists
    ask_arche_path = project_root / "ask_arche.py"
    if not ask_arche_path.exists():
        print("❌ ask_arche.py not found.")
        return 1
    
    print("✅ All required files found.")
    
    # Start VCD Bridge in background
    print("🔧 Starting VCD Bridge...")
    try:
        vcd_process = subprocess.Popen(
            [sys.executable, str(vcd_bridge_path)],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for VCD Bridge to start
        print("⏳ Waiting for VCD Bridge to initialize...")
        time.sleep(3)
        
        # Check if VCD Bridge is still running
        if vcd_process.poll() is not None:
            stdout, stderr = vcd_process.communicate()
            print(f"❌ VCD Bridge failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return 1
        
        print("✅ VCD Bridge started successfully!")
        
    except Exception as e:
        print(f"❌ Failed to start VCD Bridge: {e}")
        return 1
    
    # Run ask_arche.py with VCD integration
    print("🎯 Running ask_arche.py with VCD integration...")
    print("=" * 60)
    
    try:
        # Get query from command line arguments or use default
        query_args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Run ask_arche.py
        result = subprocess.run(
            [sys.executable, str(ask_arche_path)] + query_args,
            cwd=str(project_root)
        )
        
        print("=" * 60)
        print(f"✅ ask_arche.py completed with exit code: {result.returncode}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error running ask_arche.py: {e}")
        return 1
    
    finally:
        # Clean up VCD Bridge process
        print("🧹 Cleaning up VCD Bridge...")
        try:
            vcd_process.terminate()
            vcd_process.wait(timeout=5)
            print("✅ VCD Bridge stopped cleanly")
        except subprocess.TimeoutExpired:
            print("⚠️ VCD Bridge didn't stop cleanly, forcing termination...")
            vcd_process.kill()
        except Exception as e:
            print(f"⚠️ Error stopping VCD Bridge: {e}")
    
    print("🎉 VCD-Enhanced ArchE session completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
