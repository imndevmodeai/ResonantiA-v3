"""
System Health Monitor
The Observatory - Watching Over ArchE's Vital Signs

This module provides comprehensive health monitoring for ArchE's cognitive
architecture, tracking performance metrics, detecting anomalies, and
generating health dashboards for system oversight.

Monitored Systems:
- CRCS (Cognitive Resonant Controller System) - Response times, success rates
- RISE (Recursive Inquiry & Synthesis Engine) - Usage patterns, confidence
- ACO (Adaptive Cognitive Orchestrator) - Learning events, evolution proposals
- ThoughtTrail - Experience capture rates, buffer health
- Autopoietic Learning Loop - Cycle health, Guardian queue

Philosophical Foundation:
- Self-awareness through self-monitoring
- Early detection of system degradation
- Quantum confidence tracking for health metrics
- Proactive alerting before failure
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import statistics

logger = logging.getLogger(__name__)

# Quantum probability support
try:
    from .autopoietic_self_analysis import QuantumProbability
    QUANTUM_AVAILABLE = True
except ImportError:
    class QuantumProbability:
        def __init__(self, prob: float, evidence: List[str] = None):
            self.probability = prob
        def to_dict(self):
            return {"probability": self.probability}
    QUANTUM_AVAILABLE = False


@dataclass
class HealthMetric:
    """A single health metric measurement."""
    metric_name: str
    value: float
    unit: str
    timestamp: str
    status: str  # "healthy", "warning", "critical", "unknown"
    threshold_info: Dict[str, float]
    quantum_confidence: Optional[Dict[str, Any]] = None


@dataclass
class SystemAlert:
    """An alert about system health."""
    alert_id: str
    severity: str  # "info", "warning", "critical"
    component: str
    message: str
    timestamp: str
    metrics: Dict[str, Any]
    recommended_action: str


@dataclass
class HealthSnapshot:
    """A complete snapshot of system health."""
    snapshot_id: str
    timestamp: str
    overall_health: str  # "healthy", "degraded", "critical"
    overall_confidence: float
    component_health: Dict[str, Dict[str, Any]]
    active_alerts: List[SystemAlert]
    metrics_summary: Dict[str, Any]


class SystemHealthMonitor:
    """
    The Observatory - Comprehensive health monitoring for ArchE.
    
    This monitor continuously tracks the health of all cognitive systems,
    detecting anomalies, generating alerts, and providing dashboards
    for system oversight and maintenance.
    """
    
    def __init__(
        self,
        snapshot_interval_seconds: int = 60,
        history_size: int = 1000,
        alert_log_path: Optional[Path] = None
    ):
        """
        Initialize the System Health Monitor.
        
        Args:
            snapshot_interval_seconds: How often to take health snapshots
            history_size: Number of historical snapshots to retain
            alert_log_path: Path to alert log file
        """
        self.snapshot_interval = snapshot_interval_seconds
        self.history_size = history_size
        
        # Alert logging
        if alert_log_path is None:
            alert_log_path = Path("logs") / "system_health_alerts.jsonl"
        self.alert_log_path = alert_log_path
        self.alert_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Monitoring state
        self.metrics_history: deque = deque(maxlen=history_size)
        self.active_alerts: List[SystemAlert] = []
        self.last_snapshot_time: Optional[datetime] = None
        self.monitoring_start_time = datetime.now()
        
        # Thresholds (configurable)
        self.thresholds = {
            "crcs_response_time_ms": {"warning": 50, "critical": 200},
            "crcs_success_rate": {"warning": 0.7, "critical": 0.5},
            "rise_response_time_ms": {"warning": 1000, "critical": 5000},
            "rise_confidence": {"warning": 0.6, "critical": 0.4},
            "aco_learning_rate": {"warning": 0.01, "critical": 0.001},
            "thought_trail_buffer_usage": {"warning": 0.8, "critical": 0.95},
            "learning_loop_cycle_time_ms": {"warning": 100, "critical": 1000}
        }
        
        # Component references (set externally)
        self.cognitive_hub = None
        self.learning_loop = None
        
        logger.info("[HealthMonitor] Initialized with snapshot_interval={snapshot_interval}s")
    
    def set_components(self, cognitive_hub=None, learning_loop=None):
        """Set references to monitored components."""
        self.cognitive_hub = cognitive_hub
        self.learning_loop = learning_loop
        logger.info("[HealthMonitor] Component references set")
    
    def collect_metrics(self) -> Dict[str, HealthMetric]:
        """
        Collect current health metrics from all systems.
        
        Returns:
            Dict of metric_name -> HealthMetric
        """
        metrics = {}
        now = datetime.now().isoformat()
        
        # Collect CRCS metrics (if available through cognitive hub)
        if self.cognitive_hub and hasattr(self.cognitive_hub, 'get_metrics'):
            try:
                hub_metrics = self.cognitive_hub.get_metrics()
                
                # CRCS response time
                crcs_time = hub_metrics.get('crcs_usage', {}).get('avg_time_ms', 0)
                metrics['crcs_response_time_ms'] = HealthMetric(
                    metric_name="crcs_response_time_ms",
                    value=crcs_time,
                    unit="ms",
                    timestamp=now,
                    status=self._evaluate_status(crcs_time, 'crcs_response_time_ms', lower_is_better=True),
                    threshold_info=self.thresholds['crcs_response_time_ms'],
                    quantum_confidence=QuantumProbability(
                        1.0 if crcs_time > 0 else 0.5,
                        ["measured" if crcs_time > 0 else "no_data"]
                    ).to_dict()
                )
                
                # CRCS usage rate
                crcs_rate = hub_metrics.get('crcs_usage', {}).get('direct_rate', 0)
                metrics['crcs_usage_rate'] = HealthMetric(
                    metric_name="crcs_usage_rate",
                    value=crcs_rate,
                    unit="ratio",
                    timestamp=now,
                    status=self._evaluate_status(crcs_rate, 'crcs_success_rate'),
                    threshold_info=self.thresholds['crcs_success_rate'],
                    quantum_confidence=QuantumProbability(
                        1.0 if crcs_rate >= 0 else 0.5,
                        ["measured"]
                    ).to_dict()
                )
                
                # RISE response time
                rise_time = hub_metrics.get('rise_usage', {}).get('avg_time_ms', 0)
                metrics['rise_response_time_ms'] = HealthMetric(
                    metric_name="rise_response_time_ms",
                    value=rise_time,
                    unit="ms",
                    timestamp=now,
                    status=self._evaluate_status(rise_time, 'rise_response_time_ms', lower_is_better=True),
                    threshold_info=self.thresholds['rise_response_time_ms'],
                    quantum_confidence=QuantumProbability(
                        1.0 if rise_time > 0 else 0.3,
                        ["measured" if rise_time > 0 else "no_data"]
                    ).to_dict()
                )
                
            except Exception as e:
                logger.error(f"[HealthMonitor] Failed to collect cognitive hub metrics: {e}")
        
        # Collect Learning Loop metrics
        if self.learning_loop and hasattr(self.learning_loop, 'get_metrics'):
            try:
                loop_metrics = self.learning_loop.get_metrics()
                
                # Learning rate (stardust capture rate)
                stardust_count = loop_metrics.get('stardust_captured', 0)
                uptime_hours = (datetime.now() - self.monitoring_start_time).total_seconds() / 3600
                learning_rate = stardust_count / max(1, uptime_hours)
                
                metrics['learning_rate'] = HealthMetric(
                    metric_name="learning_rate",
                    value=learning_rate,
                    unit="stardust/hour",
                    timestamp=now,
                    status=self._evaluate_status(learning_rate, 'aco_learning_rate'),
                    threshold_info=self.thresholds['aco_learning_rate'],
                    quantum_confidence=QuantumProbability(
                        0.8,
                        ["calculated_from_metrics"]
                    ).to_dict()
                )
                
                # Guardian queue size
                guardian_queue_size = loop_metrics.get('current_state', {}).get('guardian_queue_size', 0)
                metrics['guardian_queue_size'] = HealthMetric(
                    metric_name="guardian_queue_size",
                    value=guardian_queue_size,
                    unit="items",
                    timestamp=now,
                    status="warning" if guardian_queue_size > 10 else "healthy",
                    threshold_info={"warning": 10, "critical": 50},
                    quantum_confidence=QuantumProbability(1.0, ["direct_measurement"]).to_dict()
                )
                
            except Exception as e:
                logger.error(f"[HealthMonitor] Failed to collect learning loop metrics: {e}")
        
        # System uptime
        uptime_seconds = (datetime.now() - self.monitoring_start_time).total_seconds()
        metrics['system_uptime'] = HealthMetric(
            metric_name="system_uptime",
            value=uptime_seconds,
            unit="seconds",
            timestamp=now,
            status="healthy",
            threshold_info={},
            quantum_confidence=QuantumProbability(1.0, ["system_clock"]).to_dict()
        )
        
        return metrics
    
    def _evaluate_status(
        self,
        value: float,
        metric_name: str,
        lower_is_better: bool = False
    ) -> str:
        """
        Evaluate the health status of a metric.
        
        Args:
            value: Current metric value
            metric_name: Name of the metric
            lower_is_better: Whether lower values are healthier
            
        Returns:
            Status string: "healthy", "warning", "critical"
        """
        if metric_name not in self.thresholds:
            return "unknown"
        
        thresholds = self.thresholds[metric_name]
        warning_threshold = thresholds.get("warning", float('inf'))
        critical_threshold = thresholds.get("critical", float('inf'))
        
        if lower_is_better:
            # For metrics like response time (lower is better)
            if value >= critical_threshold:
                return "critical"
            elif value >= warning_threshold:
                return "warning"
            else:
                return "healthy"
        else:
            # For metrics like success rate (higher is better)
            if value <= critical_threshold:
                return "critical"
            elif value <= warning_threshold:
                return "warning"
            else:
                return "healthy"
    
    def generate_alerts(self, metrics: Dict[str, HealthMetric]) -> List[SystemAlert]:
        """
        Generate alerts based on current metrics.
        
        Args:
            metrics: Current health metrics
            
        Returns:
            List of new alerts
        """
        alerts = []
        
        for metric_name, metric in metrics.items():
            if metric.status == "critical":
                alert = SystemAlert(
                    alert_id=f"alert_{int(time.time())}_{metric_name}",
                    severity="critical",
                    component=metric_name.split('_')[0],  # Extract component name
                    message=f"CRITICAL: {metric_name} is {metric.value:.2f}{metric.unit}, exceeding critical threshold",
                    timestamp=metric.timestamp,
                    metrics={metric_name: metric.value},
                    recommended_action=self._get_recommended_action(metric_name, "critical")
                )
                alerts.append(alert)
                
            elif metric.status == "warning":
                alert = SystemAlert(
                    alert_id=f"alert_{int(time.time())}_{metric_name}",
                    severity="warning",
                    component=metric_name.split('_')[0],
                    message=f"WARNING: {metric_name} is {metric.value:.2f}{metric.unit}, approaching threshold",
                    timestamp=metric.timestamp,
                    metrics={metric_name: metric.value},
                    recommended_action=self._get_recommended_action(metric_name, "warning")
                )
                alerts.append(alert)
        
        # Log new alerts
        for alert in alerts:
            self._log_alert(alert)
            logger.warning(f"[HealthMonitor] {alert.severity.upper()}: {alert.message}")
        
        return alerts
    
    def _get_recommended_action(self, metric_name: str, severity: str) -> str:
        """Get recommended action for a metric issue."""
        recommendations = {
            "crcs_response_time_ms": "Review CRCS controller efficiency, consider optimization",
            "crcs_success_rate": "Analyze CRCS fallback patterns, may need new controllers",
            "rise_response_time_ms": "Check RISE query complexity, consider query optimization",
            "rise_confidence": "Review RISE output quality, may need workflow tuning",
            "learning_rate": "Increase system activity or check ThoughtTrail integration",
            "guardian_queue_size": "Review Guardian queue, approve/reject pending wisdom"
        }
        
        return recommendations.get(metric_name, "Investigate system logs for root cause")
    
    def _log_alert(self, alert: SystemAlert):
        """Log alert to file."""
        try:
            with open(self.alert_log_path, 'a') as f:
                f.write(json.dumps(asdict(alert)) + '\n')
        except Exception as e:
            logger.error(f"[HealthMonitor] Failed to log alert: {e}")
    
    def take_snapshot(self) -> HealthSnapshot:
        """
        Take a complete health snapshot.
        
        Returns:
            HealthSnapshot with current system state
        """
        # Collect metrics
        metrics = self.collect_metrics()
        
        # Generate alerts
        new_alerts = self.generate_alerts(metrics)
        self.active_alerts.extend(new_alerts)
        
        # Clear resolved alerts (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.active_alerts = [
            alert for alert in self.active_alerts
            if datetime.fromisoformat(alert.timestamp) > cutoff_time
        ]
        
        # Calculate overall health
        statuses = [m.status for m in metrics.values()]
        if "critical" in statuses:
            overall_health = "critical"
            overall_confidence = 0.3
        elif "warning" in statuses:
            overall_health = "degraded"
            overall_confidence = 0.6
        else:
            overall_health = "healthy"
            overall_confidence = 0.95
        
        # Group metrics by component
        component_health = {}
        for metric_name, metric in metrics.items():
            component = metric_name.split('_')[0]
            if component not in component_health:
                component_health[component] = {
                    "status": "healthy",
                    "metrics": []
                }
            
            component_health[component]["metrics"].append(asdict(metric))
            
            # Update component status to worst metric status
            if metric.status == "critical":
                component_health[component]["status"] = "critical"
            elif metric.status == "warning" and component_health[component]["status"] != "critical":
                component_health[component]["status"] = "warning"
        
        # Create snapshot
        snapshot = HealthSnapshot(
            snapshot_id=f"snapshot_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            overall_health=overall_health,
            overall_confidence=overall_confidence,
            component_health=component_health,
            active_alerts=self.active_alerts.copy(),
            metrics_summary={
                "total_metrics": len(metrics),
                "healthy_count": sum(1 for m in metrics.values() if m.status == "healthy"),
                "warning_count": sum(1 for m in metrics.values() if m.status == "warning"),
                "critical_count": sum(1 for m in metrics.values() if m.status == "critical")
            }
        )
        
        # Store in history
        self.metrics_history.append(snapshot)
        self.last_snapshot_time = datetime.now()
        
        logger.info(f"[HealthMonitor] Snapshot taken: {snapshot.overall_health} ({snapshot.overall_confidence:.1%} confidence)")
        
        return snapshot
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """
        Generate a comprehensive health dashboard.
        
        Returns:
            Dashboard data suitable for display
        """
        if not self.metrics_history:
            latest_snapshot = self.take_snapshot()
        else:
            latest_snapshot = self.metrics_history[-1]
        
        # Calculate trends (if we have history)
        trends = {}
        if len(self.metrics_history) >= 2:
            trends = self._calculate_trends()
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": {
                "status": latest_snapshot.overall_health,
                "confidence": latest_snapshot.overall_confidence,
                "trend": trends.get("overall", "stable")
            },
            "components": latest_snapshot.component_health,
            "active_alerts": [
                {
                    "severity": alert.severity,
                    "component": alert.component,
                    "message": alert.message,
                    "age_seconds": (datetime.now() - datetime.fromisoformat(alert.timestamp)).total_seconds()
                }
                for alert in latest_snapshot.active_alerts
            ],
            "metrics_summary": latest_snapshot.metrics_summary,
            "system_info": {
                "monitoring_uptime_hours": (datetime.now() - self.monitoring_start_time).total_seconds() / 3600,
                "snapshots_taken": len(self.metrics_history),
                "last_snapshot": latest_snapshot.timestamp
            },
            "trends": trends
        }
        
        return dashboard
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate health trends from history."""
        if len(self.metrics_history) < 2:
            return {}
        
        recent_snapshots = list(self.metrics_history)[-10:]  # Last 10 snapshots
        
        # Overall health trend
        health_scores = {"healthy": 3, "degraded": 2, "critical": 1}
        scores = [health_scores.get(s.overall_health, 0) for s in recent_snapshots]
        
        if len(scores) >= 2:
            recent_avg = statistics.mean(scores[-3:])
            older_avg = statistics.mean(scores[:3])
            
            if recent_avg > older_avg + 0.3:
                overall_trend = "improving"
            elif recent_avg < older_avg - 0.3:
                overall_trend = "degrading"
            else:
                overall_trend = "stable"
        else:
            overall_trend = "insufficient_data"
        
        return {"overall": overall_trend}
    
    def get_health_status(self) -> str:
        """Get current overall health status."""
        if not self.metrics_history:
            self.take_snapshot()
        
        return self.metrics_history[-1].overall_health if self.metrics_history else "unknown"
    
    def should_alert_guardian(self) -> bool:
        """Determine if Guardian should be alerted."""
        if not self.active_alerts:
            return False
        
        # Alert if any critical alerts exist
        return any(alert.severity == "critical" for alert in self.active_alerts)


def main():
    """Demo the System Health Monitor."""
    print("🏥 Initializing System Health Monitor...")
    print()
    
    monitor = SystemHealthMonitor(snapshot_interval_seconds=30)
    
    print("✓ Monitor initialized!")
    print()
    
    # Take initial snapshot
    print("Taking health snapshot...")
    snapshot = monitor.take_snapshot()
    print(f"  Overall Health: {snapshot.overall_health}")
    print(f"  Confidence: {snapshot.overall_confidence:.1%}")
    print(f"  Active Alerts: {len(snapshot.active_alerts)}")
    print()
    
    # Generate dashboard
    print("Generating health dashboard...")
    dashboard = monitor.generate_dashboard()
    
    print("\nHealth Dashboard:")
    print(f"  Status: {dashboard['overall_health']['status']}")
    print(f"  Confidence: {dashboard['overall_health']['confidence']:.1%}")
    print(f"  Trend: {dashboard['overall_health']['trend']}")
    print()
    
    print("Component Health:")
    for component, health in dashboard['components'].items():
        print(f"  {component}: {health['status']} ({len(health['metrics'])} metrics)")
    
    print()
    print(f"Monitoring uptime: {dashboard['system_info']['monitoring_uptime_hours']:.2f} hours")
    print(f"Snapshots taken: {dashboard['system_info']['snapshots_taken']}")


if __name__ == "__main__":
    main()

