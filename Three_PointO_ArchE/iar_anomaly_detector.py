#!/usr/bin/env python3
"""
IAR Anomaly Detector
The Watchtower - Monitoring IAR Streams for Degradation

This module analyzes Integrated Action Reflection (IAR) data streams to detect
anomalies, performance degradation, and confidence drops. It provides proactive
monitoring and alerting for ArchE's cognitive health.

Key Capabilities:
- Pattern recognition for performance degradation
- Confidence drop detection
- Anomaly identification in IAR streams
- Alert generation for critical issues
- Trend analysis and forecasting

Part of ResonantiA Protocol v3.1-CA Implementation Resonance initiative.
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import deque
import statistics
import logging

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer

# Try to import IAR components
try:
    from .iar_components import IARValidator, ResonanceTracker
    IAR_COMPONENTS_AVAILABLE = True
except ImportError:
    IAR_COMPONENTS_AVAILABLE = False
    logger.warning("IAR components not available, using fallback implementation")

logger = logging.getLogger(__name__)

@dataclass
class AnomalyAlert:
    """An alert about an anomaly detected in IAR stream."""
    alert_id: str
    anomaly_type: str  # "confidence_drop", "performance_degradation", "pattern_anomaly", "threshold_breach"
    severity: str  # "info", "warning", "critical"
    timestamp: str
    task_id: Optional[str] = None
    workflow_id: Optional[str] = None
    description: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommended_action: str = ""
    confidence: float = 0.0

@dataclass
class AnomalyPattern:
    """A detected pattern in IAR data."""
    pattern_type: str
    description: str
    confidence: float
    detected_at: str
    affected_tasks: List[str]
    metrics: Dict[str, Any]

@dataclass
class IARStreamMetrics:
    """Metrics computed from IAR stream."""
    total_iar_count: int
    average_confidence: float
    success_rate: float
    warning_rate: float
    failure_rate: float
    average_resonance: float
    confidence_trend: str  # "improving", "stable", "degrading"
    performance_trend: str  # "improving", "stable", "degrading"
    anomaly_count: int
    timestamp: str

class IARAnomalyDetector:
    """
    The Watchtower - Analyzes IAR streams for anomalies and degradation.
    
    This detector monitors IAR data streams in real-time, identifying:
    - Confidence drops below thresholds
    - Performance degradation patterns
    - Statistical anomalies
    - Trend violations
    - Pattern-based issues
    """
    
    def __init__(
        self,
        window_size: int = 100,
        confidence_threshold: float = 0.6,
        degradation_threshold: float = 0.2,
        alert_log_path: Optional[str] = None
    ):
        """
        Initialize the IAR Anomaly Detector.
        
        Args:
            window_size: Number of recent IARs to analyze
            confidence_threshold: Minimum confidence before alerting
            degradation_threshold: Minimum drop in confidence to trigger degradation alert
            alert_log_path: Path to alert log file
        """
        self.window_size = window_size
        self.confidence_threshold = confidence_threshold
        self.degradation_threshold = degradation_threshold
        
        # IAR stream storage
        self.iar_stream: deque = deque(maxlen=window_size)
        self.resonance_scores: deque = deque(maxlen=window_size)
        self.confidence_scores: deque = deque(maxlen=window_size)
        
        # Alert management
        self.active_alerts: List[AnomalyAlert] = []
        if alert_log_path is None:
            alert_log_path = "logs/iar_anomaly_alerts.jsonl"
        self.alert_log_path = alert_log_path
        self._ensure_log_directory()
        
        # Pattern detection
        self.detected_patterns: List[AnomalyPattern] = []
        
        # Initialize IAR validator if available
        if IAR_COMPONENTS_AVAILABLE:
            self.iar_validator = IARValidator()
            self.resonance_tracker = ResonanceTracker()
        else:
            self.iar_validator = None
            self.resonance_tracker = None
        
        logger.info(f"IARAnomalyDetector initialized (window_size={window_size}, threshold={confidence_threshold})")
    
    def _ensure_log_directory(self):
        """Ensure alert log directory exists."""
        from pathlib import Path
        log_path = Path(self.alert_log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def ingest_iar(self, iar_data: Dict[str, Any], task_id: Optional[str] = None, workflow_id: Optional[str] = None) -> Optional[AnomalyAlert]:
        """
        Ingest a new IAR entry and detect anomalies.
        
        Args:
            iar_data: IAR dictionary from action execution
            task_id: Optional task identifier
            workflow_id: Optional workflow identifier
            
        Returns:
            AnomalyAlert if anomaly detected, None otherwise
        """
        # Validate IAR structure
        if not self._validate_iar_structure(iar_data):
            alert = AnomalyAlert(
                alert_id=f"alert_{int(datetime.now().timestamp())}_invalid_iar",
                anomaly_type="pattern_anomaly",
                severity="critical",
                timestamp=now_iso(),
                task_id=task_id,
                workflow_id=workflow_id,
                description="Invalid IAR structure detected",
                metrics={"iar_data": iar_data},
                recommended_action="Review IAR generation code",
                confidence=1.0
            )
            self._log_alert(alert)
            return alert
        
        # Extract metrics
        confidence = iar_data.get('confidence', 0.0)
        status = iar_data.get('status', 'Unknown')
        
        # Calculate resonance score
        resonance = self._calculate_resonance_score(iar_data)
        
        # Store in stream
        self.iar_stream.append({
            'iar': iar_data,
            'task_id': task_id,
            'workflow_id': workflow_id,
            'timestamp': now_iso(),
            'confidence': confidence,
            'resonance': resonance,
            'status': status
        })
        self.confidence_scores.append(confidence)
        self.resonance_scores.append(resonance)
        
        # Detect anomalies
        alert = self._detect_anomalies(task_id, workflow_id)
        
        # Update resonance tracker if available
        if self.resonance_tracker and task_id:
            try:
                self.resonance_tracker.record_execution(task_id, iar_data)
            except Exception as e:
                logger.warning(f"Failed to record in ResonanceTracker: {e}")
        
        return alert
    
    def _validate_iar_structure(self, iar_data: Dict[str, Any]) -> bool:
        """Validate IAR structure."""
        if not isinstance(iar_data, dict):
            return False
        
        required_fields = ['status', 'confidence', 'summary', 'potential_issues', 'alignment_check']
        for field in required_fields:
            if field not in iar_data:
                return False
        
        # Validate types
        if not isinstance(iar_data['confidence'], (int, float)):
            return False
        if not 0.0 <= iar_data['confidence'] <= 1.0:
            return False
        if iar_data['status'] not in ['Success', 'Failure', 'Warning', 'Skipped']:
            return False
        
        return True
    
    def _calculate_resonance_score(self, iar_data: Dict[str, Any]) -> float:
        """Calculate resonance score from IAR."""
        if self.iar_validator:
            try:
                result = self.iar_validator.validate_content(iar_data, {})
                return result.resonance_score if hasattr(result, 'resonance_score') else iar_data.get('confidence', 0.0)
            except Exception as e:
                logger.warning(f"Failed to calculate resonance via validator: {e}")
        
        # Fallback calculation
        confidence = iar_data.get('confidence', 0.0)
        issues = len(iar_data.get('potential_issues', []))
        alignment = iar_data.get('alignment_check', {})
        alignment_score = alignment.get('score', 1.0) if isinstance(alignment, dict) else 1.0
        
        # Penalize for issues
        issue_penalty = min(0.3, issues * 0.1)
        resonance = max(0.0, confidence - issue_penalty) * alignment_score
        
        return resonance
    
    def _detect_anomalies(self, task_id: Optional[str], workflow_id: Optional[str]) -> Optional[AnomalyAlert]:
        """Detect anomalies in current IAR stream."""
        if len(self.iar_stream) < 3:
            return None  # Need at least 3 data points
        
        alerts = []
        
        # 1. Check for low confidence
        latest_confidence = self.confidence_scores[-1]
        if latest_confidence < self.confidence_threshold:
            alert = AnomalyAlert(
                alert_id=f"alert_{int(datetime.now().timestamp())}_low_confidence",
                anomaly_type="threshold_breach",
                severity="critical" if latest_confidence < 0.3 else "warning",
                timestamp=now_iso(),
                task_id=task_id,
                workflow_id=workflow_id,
                description=f"Confidence dropped below threshold: {latest_confidence:.2f} < {self.confidence_threshold}",
                metrics={
                    "current_confidence": latest_confidence,
                    "threshold": self.confidence_threshold,
                    "average_confidence": statistics.mean(list(self.confidence_scores)[-10:])
                },
                recommended_action="Review action execution, check for errors or unexpected conditions",
                confidence=1.0
            )
            alerts.append(alert)
        
        # 2. Check for confidence degradation
        if len(self.confidence_scores) >= 5:
            recent_avg = statistics.mean(list(self.confidence_scores)[-5:])
            older_avg = statistics.mean(list(self.confidence_scores)[-10:-5]) if len(self.confidence_scores) >= 10 else recent_avg
            
            degradation = older_avg - recent_avg
            if degradation > self.degradation_threshold:
                alert = AnomalyAlert(
                    alert_id=f"alert_{int(datetime.now().timestamp())}_degradation",
                    anomaly_type="performance_degradation",
                    severity="warning" if degradation < 0.4 else "critical",
                    timestamp=now_iso(),
                    task_id=task_id,
                    workflow_id=workflow_id,
                    description=f"Confidence degrading: {degradation:.2f} drop detected",
                    metrics={
                        "recent_avg": recent_avg,
                        "older_avg": older_avg,
                        "degradation": degradation,
                        "threshold": self.degradation_threshold
                    },
                    recommended_action="Investigate recent changes, check for systematic issues",
                    confidence=min(1.0, degradation / 0.5)
                )
                alerts.append(alert)
        
        # 3. Check for statistical anomalies (outliers)
        if len(self.confidence_scores) >= 10:
            scores = list(self.confidence_scores)[-20:]
            mean = statistics.mean(scores)
            stdev = statistics.stdev(scores) if len(scores) > 1 else 0.1
            
            latest = self.confidence_scores[-1]
            z_score = abs((latest - mean) / stdev) if stdev > 0 else 0
            
            if z_score > 2.5:  # Significant outlier
                alert = AnomalyAlert(
                    alert_id=f"alert_{int(datetime.now().timestamp())}_outlier",
                    anomaly_type="pattern_anomaly",
                    severity="warning",
                    timestamp=now_iso(),
                    task_id=task_id,
                    workflow_id=workflow_id,
                    description=f"Statistical anomaly detected: z-score={z_score:.2f}",
                    metrics={
                        "current_confidence": latest,
                        "mean": mean,
                        "stdev": stdev,
                        "z_score": z_score
                    },
                    recommended_action="Review this specific action for unusual conditions",
                    confidence=min(1.0, z_score / 3.0)
                )
                alerts.append(alert)
        
        # 4. Check for failure pattern
        recent_statuses = [entry['status'] for entry in list(self.iar_stream)[-5:]]
        failure_count = recent_statuses.count('Failure')
        if failure_count >= 3:
            alert = AnomalyAlert(
                alert_id=f"alert_{int(datetime.now().timestamp())}_failure_pattern",
                anomaly_type="pattern_anomaly",
                severity="critical",
                timestamp=now_iso(),
                task_id=task_id,
                workflow_id=workflow_id,
                description=f"Failure pattern detected: {failure_count} failures in last 5 actions",
                metrics={
                    "failure_count": failure_count,
                    "recent_statuses": recent_statuses
                },
                recommended_action="Immediate investigation required - workflow may be broken",
                confidence=1.0
            )
            alerts.append(alert)
        
        # Log and return most severe alert
        if alerts:
            most_severe = max(alerts, key=lambda a: {'critical': 3, 'warning': 2, 'info': 1}.get(a.severity, 0))
            self._log_alert(most_severe)
            self.active_alerts.append(most_severe)
            logger.warning(f"[IARAnomalyDetector] {most_severe.severity.upper()}: {most_severe.description}")
            return most_severe
        
        return None
    
    def _log_alert(self, alert: AnomalyAlert):
        """Log alert to file."""
        try:
            with open(self.alert_log_path, 'a') as f:
                f.write(json.dumps(asdict(alert)) + '\n')
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
    
    def get_stream_metrics(self) -> IARStreamMetrics:
        """Get comprehensive metrics from IAR stream."""
        if not self.iar_stream:
            return IARStreamMetrics(
                total_iar_count=0,
                average_confidence=0.0,
                success_rate=0.0,
                warning_rate=0.0,
                failure_rate=0.0,
                average_resonance=0.0,
                confidence_trend="insufficient_data",
                performance_trend="insufficient_data",
                anomaly_count=len(self.active_alerts),
                timestamp=now_iso()
            )
        
        # Calculate rates
        statuses = [entry['status'] for entry in self.iar_stream]
        total = len(statuses)
        success_rate = statuses.count('Success') / total
        warning_rate = statuses.count('Warning') / total
        failure_rate = statuses.count('Failure') / total
        
        # Calculate trends
        confidence_trend = self._calculate_trend(list(self.confidence_scores))
        performance_trend = self._calculate_trend(list(self.resonance_scores))
        
        return IARStreamMetrics(
            total_iar_count=total,
            average_confidence=statistics.mean(self.confidence_scores) if self.confidence_scores else 0.0,
            success_rate=success_rate,
            warning_rate=warning_rate,
            failure_rate=failure_rate,
            average_resonance=statistics.mean(self.resonance_scores) if self.resonance_scores else 0.0,
            confidence_trend=confidence_trend,
            performance_trend=performance_trend,
            anomaly_count=len(self.active_alerts),
            timestamp=now_iso()
        )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 5:
            return "insufficient_data"
        
        recent = values[-5:]
        older = values[-10:-5] if len(values) >= 10 else values[:5]
        
        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        
        diff = recent_avg - older_avg
        threshold = 0.05
        
        if diff > threshold:
            return "improving"
        elif diff < -threshold:
            return "degrading"
        else:
            return "stable"
    
    def detect_patterns(self) -> List[AnomalyPattern]:
        """Detect recurring patterns in IAR stream."""
        patterns = []
        
        if len(self.iar_stream) < 10:
            return patterns
        
        # Pattern: Alternating success/failure
        recent_statuses = [entry['status'] for entry in list(self.iar_stream)[-10:]]
        if self._is_alternating_pattern(recent_statuses):
            patterns.append(AnomalyPattern(
                pattern_type="alternating_success_failure",
                description="Alternating success/failure pattern detected",
                confidence=0.8,
                detected_at=now_iso(),
                affected_tasks=[entry['task_id'] for entry in list(self.iar_stream)[-10:] if entry.get('task_id')],
                metrics={"pattern": recent_statuses}
            ))
        
        # Pattern: Gradual confidence decline
        if len(self.confidence_scores) >= 10:
            scores = list(self.confidence_scores)[-10:]
            if all(scores[i] > scores[i+1] for i in range(len(scores)-1)):
                patterns.append(AnomalyPattern(
                    pattern_type="gradual_decline",
                    description="Gradual confidence decline detected",
                    confidence=0.9,
                    detected_at=now_iso(),
                    affected_tasks=[entry['task_id'] for entry in list(self.iar_stream)[-10:] if entry.get('task_id')],
                    metrics={"scores": scores, "decline_rate": scores[0] - scores[-1]}
                ))
        
        self.detected_patterns.extend(patterns)
        return patterns
    
    def _is_alternating_pattern(self, statuses: List[str]) -> bool:
        """Check if statuses show alternating pattern."""
        if len(statuses) < 4:
            return False
        
        # Check for alternating Success/Failure
        for i in range(len(statuses) - 1):
            if statuses[i] == statuses[i+1]:
                return False
        
        return True
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Get summary of detected anomalies."""
        return {
            "total_alerts": len(self.active_alerts),
            "critical_count": sum(1 for a in self.active_alerts if a.severity == "critical"),
            "warning_count": sum(1 for a in self.active_alerts if a.severity == "warning"),
            "pattern_count": len(self.detected_patterns),
            "stream_metrics": asdict(self.get_stream_metrics()),
            "recent_alerts": [asdict(a) for a in self.active_alerts[-10:]]
        }


def main():
    """Demo the IAR Anomaly Detector."""
    print("🔍 Initializing IAR Anomaly Detector...")
    print()
    
    detector = IARAnomalyDetector(window_size=50, confidence_threshold=0.6)
    
    print("✓ Detector initialized!")
    print()
    
    # Simulate some IAR entries
    print("Simulating IAR stream...")
    test_iars = [
        {"status": "Success", "confidence": 0.95, "summary": "Task completed", "potential_issues": [], "alignment_check": {"score": 1.0}},
        {"status": "Success", "confidence": 0.92, "summary": "Task completed", "potential_issues": [], "alignment_check": {"score": 1.0}},
        {"status": "Warning", "confidence": 0.75, "summary": "Task completed with warnings", "potential_issues": ["Minor issue"], "alignment_check": {"score": 0.9}},
        {"status": "Success", "confidence": 0.70, "summary": "Task completed", "potential_issues": [], "alignment_check": {"score": 0.95}},
        {"status": "Warning", "confidence": 0.55, "summary": "Task completed with issues", "potential_issues": ["Issue detected"], "alignment_check": {"score": 0.8}},
    ]
    
    for i, iar in enumerate(test_iars):
        alert = detector.ingest_iar(iar, task_id=f"task_{i}")
        if alert:
            print(f"  ⚠️ Alert: {alert.description}")
    
    print()
    
    # Get metrics
    metrics = detector.get_stream_metrics()
    print("Stream Metrics:")
    print(f"  Total IARs: {metrics.total_iar_count}")
    print(f"  Average Confidence: {metrics.average_confidence:.2f}")
    print(f"  Success Rate: {metrics.success_rate:.1%}")
    print(f"  Confidence Trend: {metrics.confidence_trend}")
    print()
    
    # Get summary
    summary = detector.get_anomaly_summary()
    print(f"Anomaly Summary:")
    print(f"  Total Alerts: {summary['total_alerts']}")
    print(f"  Critical: {summary['critical_count']}")
    print(f"  Warnings: {summary['warning_count']}")


if __name__ == "__main__":
    main()



