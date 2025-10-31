#!/usr/bin/env python3
"""
Dynamic Port Detection for ArchE System
Automatically finds available ports and assigns them to system components.
"""

import socket
import os
import json
import subprocess
import time
from typing import Dict, List, Optional

class PortDetector:
    """Dynamic port detection and assignment for ArchE system components."""
    
    def __init__(self):
        self.port_ranges = {
            'nextjs': (3000, 3010),      # Next.js frontend
            'arche': (3005, 3015),       # ArchE backend
            'websocket': (3004, 3014),   # WebSocket server
        }
        self.assigned_ports = {}
    
    def kill_process_on_port(self, port: int) -> bool:
        """Kill any process using the specified port."""
        try:
            if os.name == 'nt':  # Windows
                cmd = f'netstat -ano | findstr :{port}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line and 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                print(f"   🗑️  Killing process {pid} on port {port}")
                                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                                return True
            else:  # Unix/Linux/Mac
                cmd = f'lsof -ti:{port}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            print(f"   🗑️  Killing process {pid} on port {port}")
                            subprocess.run(f'kill -9 {pid}', shell=True)
                            return True
        except Exception as e:
            print(f"   ⚠️  Could not kill process on port {port}: {e}")
        
        return False
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def find_available_port(self, start_port: int, end_port: int) -> Optional[int]:
        """Find the first available port in the given range."""
        for port in range(start_port, end_port + 1):
            if self.is_port_available(port):
                return port
            else:
                # Try to kill process on this port
                if self.kill_process_on_port(port):
                    time.sleep(1)  # Wait for process to be killed
                    if self.is_port_available(port):
                        return port
        return None
    
    def detect_ports(self) -> Dict[str, int]:
        """Detect and assign available ports for all components."""
        print("🔍 Detecting available ports...")
        
        for component, (start_port, end_port) in self.port_ranges.items():
            port = self.find_available_port(start_port, end_port)
            if port:
                self.assigned_ports[component] = port
                print(f"   ✅ {component.upper()}: Port {port}")
            else:
                print(f"   ❌ {component.upper()}: No available ports in range {start_port}-{end_port}")
                # Fallback to any available port
                fallback_port = self.find_available_port(8000, 9000)
                if fallback_port:
                    self.assigned_ports[component] = fallback_port
                    print(f"   🔄 {component.upper()}: Using fallback port {fallback_port}")
                else:
                    raise RuntimeError(f"Could not find any available port for {component}")
        
        return self.assigned_ports
    
    def update_environment(self, ports: Dict[str, int]):
        """Update environment variables with detected ports."""
        env_updates = {
            'NEXTJS_PORT': ports.get('nextjs'),
            'ARCHE_PORT': ports.get('arche'),
            'WEBSOCKET_PORT': ports.get('websocket'),
            'WEBSOCKET_URL': f"ws://localhost:{ports.get('arche')}" if ports.get('arche') else None,
        }
        
        # Update current process environment
        for key, value in env_updates.items():
            if value is not None:
                os.environ[key] = str(value)
                print(f"   🔧 Set {key}={value}")
        
        return env_updates
    
    def save_to_env_file(self, ports: Dict[str, int], env_file: str = '.env'):
        """Save detected ports to .env file."""
        env_content = []
        
        # Read existing .env file if it exists
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                existing_lines = f.readlines()
            
            # Update port values in existing content
            for line in existing_lines:
                if line.strip().startswith('#') or '=' not in line:
                    env_content.append(line)
                    continue
                
                key, value = line.split('=', 1)
                key = key.strip()
                
                if key == 'NEXTJS_PORT' and ports.get('nextjs'):
                    env_content.append(f"{key}={ports['nextjs']}\n")
                elif key == 'ARCHE_PORT' and ports.get('arche'):
                    env_content.append(f"{key}={ports['arche']}\n")
                elif key == 'WEBSOCKET_PORT' and ports.get('websocket'):
                    env_content.append(f"{key}={ports['websocket']}\n")
                elif key == 'WEBSOCKET_URL' and ports.get('arche'):
                    env_content.append(f"{key}=ws://localhost:{ports['arche']}\n")
                else:
                    env_content.append(line)
        else:
            # Create new .env file with detected ports
            env_content = [
                "# ArchE System Environment - Auto-generated\n",
                "# Ports dynamically detected and assigned\n\n",
                f"NEXTJS_PORT={ports.get('nextjs', '')}\n",
                f"ARCHE_PORT={ports.get('arche', '')}\n",
                f"WEBSOCKET_PORT={ports.get('websocket', '')}\n",
                f"WEBSOCKET_URL=ws://localhost:{ports.get('arche', '')}\n",
                f"ARCHE_HOST=localhost\n",
                f"WEBSOCKET_HOST=localhost\n",
                f"NEXTJS_HOST=localhost\n\n",
                "# Add other configuration as needed\n",
                "ARCHE_ENVIRONMENT=development\n",
                "ARCHE_LOG_LEVEL=INFO\n",
                "ARCHE_DEBUG_MODE=false\n",
            ]
        
        with open(env_file, 'w') as f:
            f.writelines(env_content)
        
        print(f"   💾 Saved port configuration to {env_file}")
    
    def generate_startup_config(self, ports: Dict[str, int]) -> Dict[str, any]:
        """Generate startup configuration for the system."""
        return {
            'ports': ports,
            'urls': {
                'frontend': f"http://localhost:{ports.get('nextjs')}",
                'backend': f"ws://localhost:{ports.get('arche')}",
                'websocket': f"ws://localhost:{ports.get('websocket')}",
            },
            'environment': {
                'NEXTJS_PORT': ports.get('nextjs'),
                'ARCHE_PORT': ports.get('arche'),
                'WEBSOCKET_PORT': ports.get('websocket'),
                'WEBSOCKET_URL': f"ws://localhost:{ports.get('arche')}",
            }
        }

def main():
    """Main function to detect and configure ports."""
    detector = PortDetector()
    
    try:
        # Detect available ports
        ports = detector.detect_ports()
        
        # Update environment variables
        env_updates = detector.update_environment(ports)
        
        # Save to .env file
        detector.save_to_env_file(ports)
        
        # Generate startup configuration
        config = detector.generate_startup_config(ports)
        
        print("\n🎯 Port Detection Complete!")
        print("=" * 50)
        print(f"🌐 Frontend: {config['urls']['frontend']}")
        print(f"🧠 Backend: {config['urls']['backend']}")
        print(f"🔌 WebSocket: {config['urls']['websocket']}")
        print("=" * 50)
        
        # Save configuration for startup scripts
        with open('.port_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration saved to .port_config.json")
        print("🚀 Ready to start ArchE system with detected ports!")
        
        return config
        
    except Exception as e:
        print(f"❌ Port detection failed: {e}")
        return None

if __name__ == "__main__":
    main() 