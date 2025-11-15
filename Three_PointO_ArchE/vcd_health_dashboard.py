#!/usr/bin/env python3
"""
VCD Health Dashboard Backend
Real-time monitoring and visualization backend for Visual Cognitive Debugger

This module provides the backend API and data collection for the VCD Health Dashboard,
including system health monitoring, performance metrics, and alerting.

Part of ResonantiA Protocol v3.5-GP Implementation Resonance initiative.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import deque
import logging
import statistics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Fallback for systems without psutil
    class MockPSUtil:
        @staticmethod
        def virtual_memory():
            class Memory:
                percent = 50.0
            return Memory()
        @staticmethod
        def cpu_percent(interval=0.1):
            return 25.0
    psutil = MockPSUtil()
import os

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer

logger = logging.getLogger(__name__)

@dataclass
class SystemHealth:
    """System health metrics."""
    vcd_bridge_status: str  # "connected", "disconnected", "error"
    active_connections: int
    system_uptime: str
    memory_usage: float  # percentage
    cpu_usage: float  # percentage
    response_time: float  # milliseconds
    timestamp: str

@dataclass
class PerformanceMetrics:
    """Performance metrics data point."""
    timestamp: str
    connection_count: int
    response_time: float
    memory_usage: float
    cpu_usage: float
    message_throughput: int  # messages per second

@dataclass
class ComponentHealth:
    """Health status of a VCD component."""
    component_name: str
    status: str  # "healthy", "degraded", "error"
    metrics: Dict[str, Any]
    last_update: str
    error_count: int = 0

@dataclass
class Alert:
    """System alert."""
    id: str
    level: str  # "info", "warning", "critical"
    type: str  # "system", "performance", "security"
    message: str
    timestamp: str
    status: str  # "active", "acknowledged", "resolved"
    component: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

class VCDHealthCollector:
    """
    VCD Health Collector - Collects system health data.
    
    Provides:
    - System health data collection
    - Performance metrics aggregation
    - Alert condition evaluation
    - Historical data storage
    """
    
    def __init__(
        self,
        vcd_bridge_client: Optional[Any] = None,
        metrics_history_size: int = 1000
    ):
        """
        Initialize VCD Health Collector.
        
        Args:
            vcd_bridge_client: Optional VCD Bridge client for connection status
            metrics_history_size: Number of historical metrics to retain
        """
        self.vcd_bridge_client = vcd_bridge_client
        self.metrics_history: deque = deque(maxlen=metrics_history_size)
        self.alerts: List[Alert] = []
        self.component_health: Dict[str, ComponentHealth] = {}
        self.start_time = datetime.now()
        
        # Alert thresholds
        self.thresholds = {
            "memory_usage": {"warning": 0.8, "critical": 0.9},
            "cpu_usage": {"warning": 0.8, "critical": 0.9},
            "response_time": {"warning": 1000.0, "critical": 5000.0},  # milliseconds
            "connection_count": {"warning": 80, "critical": 100}
        }
        
        logger.info("VCDHealthCollector initialized")
    
    def collect_system_metrics(self) -> SystemHealth:
        """
        Collect current system health metrics.
        
        Returns:
            SystemHealth object
        """
        # Get VCD Bridge status
        vcd_bridge_status = "disconnected"
        active_connections = 0
        response_time = 0.0
        
        if self.vcd_bridge_client:
            try:
                # Check if bridge is connected
                if hasattr(self.vcd_bridge_client, 'is_connected'):
                    if self.vcd_bridge_client.is_connected():
                        vcd_bridge_status = "connected"
                        if hasattr(self.vcd_bridge_client, 'get_connection_count'):
                            active_connections = self.vcd_bridge_client.get_connection_count()
                        if hasattr(self.vcd_bridge_client, 'get_avg_response_time'):
                            response_time = self.vcd_bridge_client.get_avg_response_time()
            except Exception as e:
                logger.warning(f"Failed to get VCD Bridge status: {e}")
                vcd_bridge_status = "error"
        
        # Get system metrics
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
        else:
            # Fallback metrics when psutil not available
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
        
        # Calculate uptime
        uptime_delta = datetime.now() - self.start_time
        uptime_str = str(uptime_delta)
        
        return SystemHealth(
            vcd_bridge_status=vcd_bridge_status,
            active_connections=active_connections,
            system_uptime=uptime_str,
            memory_usage=memory.percent / 100.0,
            cpu_usage=cpu / 100.0,
            response_time=response_time,
            timestamp=now_iso()
        )
    
    def collect_performance_metrics(self) -> PerformanceMetrics:
        """
        Collect performance metrics.
        
        Returns:
            PerformanceMetrics object
        """
        system_health = self.collect_system_metrics()
        
        # Calculate message throughput (simplified - would need actual message counter)
        message_throughput = 0
        if self.vcd_bridge_client and hasattr(self.vcd_bridge_client, 'get_message_throughput'):
            message_throughput = self.vcd_bridge_client.get_message_throughput()
        
        metrics = PerformanceMetrics(
            timestamp=now_iso(),
            connection_count=system_health.active_connections,
            response_time=system_health.response_time,
            memory_usage=system_health.memory_usage,
            cpu_usage=system_health.cpu_usage,
            message_throughput=message_throughput
        )
        
        # Store in history
        self.metrics_history.append(metrics)
        
        return metrics
    
    def collect_component_health(self) -> Dict[str, ComponentHealth]:
        """
        Collect health status of all VCD components.
        
        Returns:
            Dict of component_name -> ComponentHealth
        """
        components = {}
        
        # VCD UI Health
        vcd_ui_health = ComponentHealth(
            component_name="vcd_ui",
            status="healthy",  # Would check actual UI status
            metrics={
                "visualization_modes_active": 3,
                "data_generation_rate": 10.0,  # per second
                "error_rate": 0.0,
                "last_update": now_iso()
            },
            last_update=now_iso(),
            error_count=0
        )
        components["vcd_ui"] = vcd_ui_health
        
        # VCD Bridge Health
        system_health = self.collect_system_metrics()
        bridge_status = "healthy" if system_health.vcd_bridge_status == "connected" else "error"
        
        vcd_bridge_health = ComponentHealth(
            component_name="vcd_bridge",
            status=bridge_status,
            metrics={
                "server_status": system_health.vcd_bridge_status,
                "port_status": "open" if system_health.active_connections >= 0 else "closed",
                "connection_pool": system_health.active_connections,
                "message_queue": 0  # Would get from actual bridge
            },
            last_update=now_iso(),
            error_count=0 if bridge_status == "healthy" else 1
        )
        components["vcd_bridge"] = vcd_bridge_health
        
        # VCD Analysis Agent Health
        vcd_analysis_health = ComponentHealth(
            component_name="vcd_analysis_agent",
            status="healthy",  # Would check actual agent status
            metrics={
                "analysis_status": "idle",
                "session_count": 0,
                "analysis_duration_avg": 0.0,
                "success_rate": 1.0
            },
            last_update=now_iso(),
            error_count=0
        )
        components["vcd_analysis_agent"] = vcd_analysis_health
        
        self.component_health = components
        return components
    
    def evaluate_alert_conditions(self) -> List[Alert]:
        """
        Evaluate alert conditions and generate alerts.
        
        Returns:
            List of new Alert objects
        """
        new_alerts = []
        system_health = self.collect_system_metrics()
        
        # Check memory usage
        if system_health.memory_usage >= self.thresholds["memory_usage"]["critical"]:
            alert = Alert(
                id=f"alert_{int(datetime.now().timestamp())}_high_memory",
                level="critical",
                type="system",
                message=f"High memory usage: {system_health.memory_usage:.1%}",
                timestamp=now_iso(),
                status="active",
                component="system",
                metrics={"memory_usage": system_health.memory_usage}
            )
            new_alerts.append(alert)
        elif system_health.memory_usage >= self.thresholds["memory_usage"]["warning"]:
            alert = Alert(
                id=f"alert_{int(datetime.now().timestamp())}_high_memory",
                level="warning",
                type="system",
                message=f"Memory usage approaching limit: {system_health.memory_usage:.1%}",
                timestamp=now_iso(),
                status="active",
                component="system",
                metrics={"memory_usage": system_health.memory_usage}
            )
            new_alerts.append(alert)
        
        # Check CPU usage
        if system_health.cpu_usage >= self.thresholds["cpu_usage"]["critical"]:
            alert = Alert(
                id=f"alert_{int(datetime.now().timestamp())}_high_cpu",
                level="critical",
                type="performance",
                message=f"High CPU usage: {system_health.cpu_usage:.1%}",
                timestamp=now_iso(),
                status="active",
                component="system",
                metrics={"cpu_usage": system_health.cpu_usage}
            )
            new_alerts.append(alert)
        
        # Check response time
        if system_health.response_time >= self.thresholds["response_time"]["critical"]:
            alert = Alert(
                id=f"alert_{int(datetime.now().timestamp())}_slow_response",
                level="critical",
                type="performance",
                message=f"Slow response time: {system_health.response_time:.0f}ms",
                timestamp=now_iso(),
                status="active",
                component="vcd_bridge",
                metrics={"response_time": system_health.response_time}
            )
            new_alerts.append(alert)
        
        # Check VCD Bridge status
        if system_health.vcd_bridge_status == "error":
            alert = Alert(
                id=f"alert_{int(datetime.now().timestamp())}_bridge_error",
                level="critical",
                type="system",
                message="VCD Bridge is in error state",
                timestamp=now_iso(),
                status="active",
                component="vcd_bridge",
                metrics={"status": system_health.vcd_bridge_status}
            )
            new_alerts.append(alert)
        
        # Add new alerts
        for alert in new_alerts:
            if not any(a.id == alert.id for a in self.alerts):
                self.alerts.append(alert)
                logger.warning(f"[VCDHealth] {alert.level.upper()}: {alert.message}")
        
        return new_alerts
    
    def store_historical_data(self, metrics: PerformanceMetrics):
        """
        Store historical performance data.
        
        Args:
            metrics: PerformanceMetrics to store
        """
        # Already stored in metrics_history deque
        # In production, would also write to time-series database
        pass
    
    def get_historical_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[PerformanceMetrics]:
        """
        Get historical performance metrics.
        
        Args:
            start_time: Start time for query
            end_time: End time for query
            
        Returns:
            List of PerformanceMetrics
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=1)
        if end_time is None:
            end_time = datetime.now()
        
        filtered_metrics = []
        for metric in self.metrics_history:
            metric_time = datetime.fromisoformat(metric.timestamp)
            if start_time <= metric_time <= end_time:
                filtered_metrics.append(metric)
        
        return filtered_metrics


class VCDHealthDashboardAPI:
    """
    VCD Health Dashboard API - Backend API for dashboard.
    
    Provides RESTful API endpoints for health data access.
    """
    
    def __init__(self, health_collector: VCDHealthCollector):
        """
        Initialize VCD Health Dashboard API.
        
        Args:
            health_collector: VCDHealthCollector instance
        """
        self.collector = health_collector
        logger.info("VCDHealthDashboardAPI initialized")
    
    def get_health_overview(self) -> Dict[str, Any]:
        """
        Get system health overview.
        
        Returns:
            Dictionary with system health overview
        """
        system_health = self.collector.collect_system_metrics()
        component_health = self.collector.collect_component_health()
        alerts = self.collector.evaluate_alert_conditions()
        
        # Calculate overall health status
        overall_status = "healthy"
        if any(a.level == "critical" for a in alerts):
            overall_status = "critical"
        elif any(a.level == "warning" for a in alerts):
            overall_status = "degraded"
        
        return {
            "timestamp": now_iso(),
            "overall_status": overall_status,
            "system_health": asdict(system_health),
            "component_health": {name: asdict(health) for name, health in component_health.items()},
            "active_alerts": [asdict(alert) for alert in alerts if alert.status == "active"],
            "alert_summary": {
                "total": len(alerts),
                "critical": sum(1 for a in alerts if a.level == "critical"),
                "warning": sum(1 for a in alerts if a.level == "warning"),
                "info": sum(1 for a in alerts if a.level == "info")
            }
        }
    
    def get_performance_metrics(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Args:
            start_time: Start time ISO string
            end_time: End time ISO string
            
        Returns:
            Dictionary with performance metrics
        """
        start = datetime.fromisoformat(start_time) if start_time else None
        end = datetime.fromisoformat(end_time) if end_time else None
        
        metrics = self.collector.get_historical_metrics(start, end)
        
        # Calculate statistics
        if metrics:
            response_times = [m.response_time for m in metrics]
            memory_usages = [m.memory_usage for m in metrics]
            cpu_usages = [m.cpu_usage for m in metrics]
            
            return {
                "timestamp": now_iso(),
                "metrics": [asdict(m) for m in metrics],
                "statistics": {
                    "response_time": {
                        "avg": statistics.mean(response_times),
                        "min": min(response_times),
                        "max": max(response_times)
                    },
                    "memory_usage": {
                        "avg": statistics.mean(memory_usages),
                        "min": min(memory_usages),
                        "max": max(memory_usages)
                    },
                    "cpu_usage": {
                        "avg": statistics.mean(cpu_usages),
                        "min": min(cpu_usages),
                        "max": max(cpu_usages)
                    }
                }
            }
        else:
            return {
                "timestamp": now_iso(),
                "metrics": [],
                "statistics": {}
            }
    
    def get_component_health(self) -> Dict[str, Any]:
        """
        Get component health status.
        
        Returns:
            Dictionary with component health
        """
        component_health = self.collector.collect_component_health()
        return {
            "timestamp": now_iso(),
            "components": {name: asdict(health) for name, health in component_health.items()}
        }
    
    def get_alerts(
        self,
        level: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get alerts.
        
        Args:
            level: Filter by alert level
            status: Filter by alert status
            
        Returns:
            Dictionary with alerts
        """
        alerts = self.collector.alerts
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        return {
            "timestamp": now_iso(),
            "alerts": [asdict(alert) for alert in alerts],
            "count": len(alerts)
        }
    
    def acknowledge_alert(self, alert_id: str) -> Tuple[bool, str]:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: ID of alert to acknowledge
            
        Returns:
            Tuple of (success, message)
        """
        for alert in self.collector.alerts:
            if alert.id == alert_id:
                alert.status = "acknowledged"
                return True, "Alert acknowledged"
        return False, "Alert not found"
    
    def resolve_alert(self, alert_id: str) -> Tuple[bool, str]:
        """
        Resolve an alert.
        
        Args:
            alert_id: ID of alert to resolve
            
        Returns:
            Tuple of (success, message)
        """
        for alert in self.collector.alerts:
            if alert.id == alert_id:
                alert.status = "resolved"
                return True, "Alert resolved"
        return False, "Alert not found"


def main():
    """Demo the VCD Health Dashboard Backend."""
    print("📊 Initializing VCD Health Dashboard Backend...")
    print()
    
    collector = VCDHealthCollector()
    api = VCDHealthDashboardAPI(collector)
    
    print("✓ Systems initialized!")
    print()
    
    # Collect metrics
    print("Collecting system metrics...")
    system_health = collector.collect_system_metrics()
    print(f"  VCD Bridge Status: {system_health.vcd_bridge_status}")
    print(f"  Active Connections: {system_health.active_connections}")
    print(f"  Memory Usage: {system_health.memory_usage:.1%}")
    print(f"  CPU Usage: {system_health.cpu_usage:.1%}")
    print()
    
    # Get health overview
    print("Health Overview:")
    overview = api.get_health_overview()
    print(f"  Overall Status: {overview['overall_status']}")
    print(f"  Active Alerts: {overview['alert_summary']['total']}")
    print(f"    Critical: {overview['alert_summary']['critical']}")
    print(f"    Warning: {overview['alert_summary']['warning']}")
    print()
    
    print("✓ VCD Health Dashboard Backend operational!")


if __name__ == "__main__":
    main()

