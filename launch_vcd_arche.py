#!/usr/bin/env python3
"""
VCD-Enhanced ArchE Launcher - 13 Mandates Compliant
This script launches the complete VCD-Enhanced ArchE system with full mandate compliance.
"""

import subprocess
import time
import sys
import os
import signal
import psutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

class VCDArchELauncher:
    """VCD-Enhanced ArchE Launcher with 13 Mandates Compliance"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.vcd_bridge_process = None
        self.ask_arche_process = None
        self.processes = []
        
    def check_requirements(self) -> bool:
        """Check system requirements - Mandate 1: Autopoietic Self-Analysis"""
        console.print("[blue]🔍 Checking System Requirements...[/blue]")
        
        requirements = {
            "Python": sys.executable,
            "Project Root": str(self.project_root),
            "VCD Bridge": str(self.project_root / "vcd_bridge_fixed.py"),
            "Ask ArchE VCD": str(self.project_root / "ask_arche_vcd_mandates.py"),
            "Virtual Environment": str(self.project_root / "arche_env")
        }
        
        table = Table(title="System Requirements Check")
        table.add_column("Component", style="cyan")
        table.add_column("Path", style="green")
        table.add_column("Status", style="yellow")
        
        all_good = True
        for component, path in requirements.items():
            if Path(path).exists():
                status = "✅ Found"
            else:
                status = "❌ Missing"
                all_good = False
            table.add_row(component, path, status)
        
        console.print(table)
        
        if not all_good:
            console.print("[red]❌ Some requirements are missing. Please check the paths above.[/red]")
            return False
        
        console.print("[green]✅ All requirements satisfied[/green]")
        return True
    
    def kill_existing_processes(self):
        """Kill existing processes - Mandate 13: Graceful Shutdown"""
        console.print("[yellow]🧹 Cleaning up existing processes...[/yellow]")
        
        # Kill processes by name
        process_names = ["vcd_bridge.py", "ask_arche_vcd_mandates.py"]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                for name in process_names:
                    if name in cmdline:
                        console.print(f"[red]🔪 Killing process {proc.info['pid']}: {name}[/red]")
                        proc.kill()
                        time.sleep(0.5)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Kill processes on specific ports
        ports = [8765, 3000]  # VCD Bridge and Next.js
        for port in ports:
            try:
                for conn in psutil.net_connections():
                    if conn.laddr.port == port:
                        proc = psutil.Process(conn.pid)
                        console.print(f"[red]🔪 Killing process on port {port}: PID {conn.pid}[/red]")
                        proc.kill()
                        time.sleep(0.5)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def start_vcd_bridge(self) -> bool:
        """Start VCD Bridge - Mandate 2: Robust Communication"""
        console.print("[blue]🚀 Starting VCD Bridge...[/blue]")
        
        try:
            self.vcd_bridge_process = subprocess.Popen(
                [sys.executable, str(self.project_root / "vcd_bridge_fixed.py")],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(self.vcd_bridge_process)
            
            # Wait for VCD Bridge to start
            console.print("[yellow]⏳ Waiting for VCD Bridge to initialize...[/yellow]")
            time.sleep(3)
            
            # Check if process is still running
            if self.vcd_bridge_process.poll() is None:
                console.print("[green]✅ VCD Bridge started successfully[/green]")
                return True
            else:
                stdout, stderr = self.vcd_bridge_process.communicate()
                console.print(f"[red]❌ VCD Bridge failed to start:[/red]")
                console.print(f"[red]STDOUT: {stdout}[/red]")
                console.print(f"[red]STDERR: {stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Failed to start VCD Bridge: {e}[/red]")
            return False
    
    def start_ask_arche_vcd(self, query: str = None) -> bool:
        """Start VCD-Enhanced Ask ArchE - Mandate 4: Cognitive Processing"""
        console.print("[blue]🎯 Starting VCD-Enhanced Ask ArchE...[/blue]")
        
        try:
            cmd = [sys.executable, str(self.project_root / "ask_arche_vcd_mandates.py")]
            if query:
                cmd.append(query)
            
            self.ask_arche_process = subprocess.Popen(
                cmd,
                cwd=str(self.project_root),
                text=True
            )
            
            self.processes.append(self.ask_arche_process)
            
            console.print("[green]✅ VCD-Enhanced Ask ArchE started[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to start Ask ArchE: {e}[/red]")
            return False
    
    def monitor_processes(self):
        """Monitor processes - Mandate 8: Performance Monitoring"""
        console.print("[blue]📊 Monitoring processes...[/blue]")
        
        try:
            # Wait for ask_arche to complete
            if self.ask_arche_process:
                return_code = self.ask_arche_process.wait()
                console.print(f"[green]✅ Ask ArchE completed with exit code: {return_code}[/green]")
                return True
        except KeyboardInterrupt:
            console.print("\n[yellow]⏹️ Interrupted by user[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Error monitoring processes: {e}[/red]")
            return False
    
    def cleanup(self):
        """Cleanup processes - Mandate 13: Graceful Shutdown"""
        console.print("[blue]🧹 Cleaning up processes...[/blue]")
        
        for process in self.processes:
            if process and process.poll() is None:
                try:
                    console.print(f"[yellow]🔄 Terminating process {process.pid}...[/yellow]")
                    process.terminate()
                    process.wait(timeout=5)
                    console.print(f"[green]✅ Process {process.pid} terminated cleanly[/green]")
                except subprocess.TimeoutExpired:
                    console.print(f"[red]⚠️ Process {process.pid} didn't stop cleanly, forcing...[/red]")
                    process.kill()
                except Exception as e:
                    console.print(f"[yellow]Warning: {e}[/yellow]")
    
    def run(self, query: str = None):
        """Main execution - All 13 Mandates"""
        console.rule("[bold yellow]VCD-Enhanced ArchE Launcher - 13 Mandates Compliant[/bold yellow]")
        
        try:
            # Mandate 1: Autopoietic Self-Analysis
            if not self.check_requirements():
                return 1
            
            # Mandate 13: Graceful Shutdown (cleanup first)
            self.kill_existing_processes()
            
            # Mandate 2: Robust Communication
            if not self.start_vcd_bridge():
                console.print("[yellow]⚠️ Continuing without VCD Bridge...[/yellow]")
            
            # Mandate 4: Cognitive Processing
            if not self.start_ask_arche_vcd(query):
                return 1
            
            # Mandate 8: Performance Monitoring
            if not self.monitor_processes():
                return 1
            
            console.print("[green]🎉 VCD-Enhanced ArchE session completed successfully![/green]")
            return 0
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⏹️ Interrupted by user[/yellow]")
            return 0
        except Exception as e:
            console.print(f"[red]💥 Fatal error: {e}[/red]")
            return 1
        finally:
            # Mandate 13: Graceful Shutdown
            self.cleanup()

def main():
    """Main function"""
    launcher = VCDArchELauncher()
    
    # Get query from command line arguments
    query = None
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        console.print(Panel(f"[bold cyan]Query:[/] '{query}'", expand=False, border_style="cyan"))
    
    # Run the launcher
    exit_code = launcher.run(query)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
