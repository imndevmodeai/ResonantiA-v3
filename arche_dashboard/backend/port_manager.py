#!/usr/bin/env python3
"""
Port Manager for ArchE Dashboard
Handles port conflict detection and automatic port selection.
Ensures multiple dashboard instances can run without conflicts.
"""

import socket
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class PortManager:
    """Manages port allocation and conflict detection."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize PortManager.
        
        Args:
            config_file: Optional path to port configuration file
        """
        self.config_file = config_file or Path(__file__).parent.parent / "port_config.json"
        self.default_port = int(os.environ.get("DASHBOARD_PORT", "8000"))
        self.port_range_start = 8000
        self.port_range_end = 8999
        self.used_ports = set()
        self._load_config()
    
    def _load_config(self):
        """Load port configuration from file if it exists."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.used_ports = set(config.get("used_ports", []))
                    logger.info(f"Loaded port config: {len(self.used_ports)} ports in use")
            except Exception as e:
                logger.warning(f"Failed to load port config: {e}")
    
    def _save_config(self):
        """Save port configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({
                    "used_ports": list(self.used_ports),
                    "default_port": self.default_port
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save port config: {e}")
    
    def is_port_available(self, port: int) -> bool:
        """
        Check if a port is available.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0  # Port is available if connection fails
        except Exception as e:
            logger.debug(f"Error checking port {port}: {e}")
            return False
    
    def find_available_port(self, start_port: Optional[int] = None) -> int:
        """
        Find an available port starting from the given port.
        
        Args:
            start_port: Starting port number (defaults to default_port)
            
        Returns:
            Available port number
        """
        start = start_port or self.default_port
        
        # First, try the default/preferred port
        if self.is_port_available(start) and start not in self.used_ports:
            self.used_ports.add(start)
            self._save_config()
            return start
        
        # Search for available port in range
        for port in range(start, self.port_range_end + 1):
            if port not in self.used_ports and self.is_port_available(port):
                self.used_ports.add(port)
                self._save_config()
                logger.info(f"Found available port: {port}")
                return port
        
        # If no port found in range, try below start port
        for port in range(start - 1, self.port_range_start - 1, -1):
            if port not in self.used_ports and self.is_port_available(port):
                self.used_ports.add(port)
                self._save_config()
                logger.info(f"Found available port (below range): {port}")
                return port
        
        raise RuntimeError(f"No available ports found in range {self.port_range_start}-{self.port_range_end}")
    
    def release_port(self, port: int):
        """
        Release a port (mark it as available).
        
        Args:
            port: Port number to release
        """
        if port in self.used_ports:
            self.used_ports.remove(port)
            self._save_config()
            logger.info(f"Released port: {port}")
    
    def get_port_info(self) -> Dict:
        """
        Get information about port usage.
        
        Returns:
            Dictionary with port information
        """
        return {
            "default_port": self.default_port,
            "used_ports": list(self.used_ports),
            "available_ports": [
                p for p in range(self.port_range_start, self.port_range_end + 1)
                if p not in self.used_ports and self.is_port_available(p)
            ][:10]  # First 10 available
        }

# Global port manager instance
_port_manager: Optional[PortManager] = None

def get_port_manager() -> PortManager:
    """Get or create global port manager instance."""
    global _port_manager
    if _port_manager is None:
        _port_manager = PortManager()
    return _port_manager


