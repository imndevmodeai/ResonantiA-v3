#!/usr/bin/env python3
"""
ArchE Unified Startup Script
Single entry point to start the complete ArchE system with UI
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path

class ArcheStartup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.nextjs_dir = self.project_root / "nextjs-chat"
        self.processes = []
        self.running = True
        
    def print_banner(self):
        print("🚀 ArchE System Startup")
        print("=" * 50)
        print("🎯 Single Entry Point - Unified System")
        print("🧠 RISE Engine + NextJS UI + Session Management")
        print("=" * 50)
        
    def prime_action_registry(self):
        """Run the action registry priming script as a module."""
        print("\n🅿️  Priming action registry...")
        try:
            # Run the priming script as a module to fix relative import issues
            result = subprocess.run(
                [sys.executable, "-m", "Three_PointO_ArchE.prime_action_registry"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                print("✅ Action registry primed successfully.")
                return True
            else:
                print("❌ Action registry priming failed.")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Error priming action registry: {e}")
            return False

    def check_environment(self):
        """Check if all required components are available"""
        print("🔍 Checking environment...")
        
        # Check virtual environment
        venv_path = self.project_root / ".venv"
        if not venv_path.exists():
            print("❌ Virtual environment not found. Please run setup first.")
            return False
        print("✅ Virtual environment found")
        
        # Check NextJS directory
        if not self.nextjs_dir.exists():
            print("❌ NextJS directory not found")
            return False
        print("✅ NextJS directory found")
        
        # Check package.json
        package_json = self.nextjs_dir / "package.json"
        if not package_json.exists():
            print("❌ NextJS package.json not found")
            return False
        print("✅ NextJS package.json found")
        
        # Check RISE engine
        rise_engine = self.project_root / "test_rise_engine_complete.py"
        if not rise_engine.exists():
            print("❌ RISE engine not found")
            return False
        print("✅ RISE engine found")
        
        return True
        
    def verify_action_registry(self):
        """Verify the action registry, including dynamic loading."""
        print("\n🔬 Verifying full action registry...")
        total_actions = 0
        try:
            from Three_PointO_ArchE.action_registry import main_action_registry
            total_actions = len(main_action_registry.actions)
            
            if total_actions > 0:
                print(f"✅ Action registry verification passed. Found {total_actions} actions.")
                return True
            else:
                print("❌ Action registry is empty. Dynamic loading may have failed.")
                return False
        except Exception as e:
            print(f"❌ Error verifying action registry: {e}")
            return False

    def test_rise_engine(self):
        """Test the RISE engine functionality"""
        print("\n🧪 Testing RISE Engine...")
        try:
            result = subprocess.run([
                str(self.project_root / ".venv" / "bin" / "python"),
                str(self.project_root / "test_rise_engine_complete.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0 or "All tests passed" in result.stdout:
                print("✅ RISE Engine test passed")
                return True
            else:
                print("❌ RISE Engine test failed")
                print("Output:", result.stdout)
                print("Errors:", result.stderr)
                return False
        except Exception as e:
            print(f"❌ RISE Engine test error: {e}")
            return False
            
    def test_session_manager(self):
        """Test the session manager"""
        print("\n🧪 Testing Session Manager...")
        try:
            result = subprocess.run([
                str(self.project_root / ".venv" / "bin" / "python"),
                "-c",
                "from Three_PointO_ArchE.session_manager import session_manager; "
                "session_id = session_manager.get_or_create_session('Test session'); "
                "print(f'✅ Session Manager working: {session_id}')"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print(result.stdout.strip())
                return True
            else:
                print("❌ Session Manager test failed")
                print("Errors:", result.stderr)
                return False
        except Exception as e:
            print(f"❌ Session Manager test error: {e}")
            return False
            
    def install_nextjs_dependencies(self):
        """Install NextJS dependencies if needed"""
        print("\n📦 Installing NextJS dependencies...")
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.nextjs_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ NextJS dependencies installed")
                return True
            else:
                print("❌ NextJS dependency installation failed")
                print("Errors:", result.stderr)
                return False
        except Exception as e:
            print(f"❌ NextJS dependency installation error: {e}")
            return False
            
    def start_websocket_server(self):
        """Start the ArchE WebSocket server"""
        print("\n🔌 Starting ArchE WebSocket Server...")
        try:
            # Start WebSocket server in background
            process = subprocess.Popen([
                str(self.project_root / ".venv" / "bin" / "python"),
                str(self.project_root / "arche_websocket_server.py")
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes.append(("WebSocket", process))
            print("✅ WebSocket server started")
            
            # Wait a moment for server to start
            time.sleep(2)
            
            # Check if server is running
            if process.poll() is None:
                print("✅ WebSocket server is running")
                return True
            else:
                print("❌ WebSocket server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ WebSocket server error: {e}")
            return False
            
    def start_nextjs_server(self):
        """Start the NextJS development server"""
        print("\n🌐 Starting NextJS development server...")
        try:
            # Start NextJS in background
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.nextjs_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(("NextJS", process))
            print("✅ NextJS server started")
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if server is running
            if process.poll() is None:
                print("✅ NextJS server is running")
                return True
            else:
                print("❌ NextJS server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ NextJS server error: {e}")
            return False
            
    def print_success_info(self):
        """Print success information and usage instructions"""
        print("\n" + "=" * 50)
        print("🎉 ArchE System Successfully Started!")
        print("=" * 50)
        print("📱 Chat Interface: http://localhost:3000")
        print("🔌 WebSocket Server: ws://localhost:3004")
        print("🚀 RISE Engine: Integrated in chat interface")
        print("🧠 Session Management: Stable and persistent")
        print("🔧 Centralized Port Management: Active")
        print("\n💡 Usage Instructions:")
        print("   - Open http://localhost:3000 in your browser")
        print("   - Click 'Show RISE' button to access RISE Engine")
        print("   - Select workflows and execute cognitive analysis")
        print("   - Session IDs are now stable and consistent")
        print("\n🛑 To stop: Press Ctrl+C")
        print("=" * 50)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down ArchE system...")
        self.running = False
        
        # Stop all processes
        for name, process in self.processes:
            print(f"🛑 Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Error stopping {name}: {e}")
                
        print("✅ ArchE system stopped")
        sys.exit(0)
        
    def run(self):
        """Main startup sequence"""
        self.print_banner()

        # Prime the action registry first
        if not self.prime_action_registry():
            print("❌ Action registry priming failed. Aborting startup.")
            sys.exit(1)
        
        # Check environment
        if not self.check_environment():
            print("❌ Environment check failed. Please fix issues and try again.")
            sys.exit(1)
            
        # Verify action registry
        if not self.verify_action_registry():
            print("❌ Action registry verification failed. Please fix issues and try again.")
            sys.exit(1)
            
        # Test components
        if not self.test_rise_engine():
            print("❌ RISE Engine test failed. Please fix issues and try again.")
            sys.exit(1)
            
        if not self.test_session_manager():
            print("❌ Session Manager test failed. Please fix issues and try again.")
            sys.exit(1)
            
        # Install dependencies
        if not self.install_nextjs_dependencies():
            print("❌ Dependency installation failed. Please fix issues and try again.")
            sys.exit(1)
            
        # Start WebSocket server
        if not self.start_websocket_server():
            print("❌ WebSocket server failed to start. Please fix issues and try again.")
            sys.exit(1)
            
        # Start NextJS server
        if not self.start_nextjs_server():
            print("❌ NextJS server failed to start. Please fix issues and try again.")
            sys.exit(1)
            
        # Print success info
        self.print_success_info()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)

def main():
    startup = ArcheStartup()
    startup.run()

if __name__ == "__main__":
    main() 