# VCD Health Dashboard - Complete How-To Guide

**Component**: Visual Cognitive Debugger Health Dashboard  
**Version**: 1.0  
**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:27:10 EST  
**File**: `Three_PointO_ArchE/vcd_health_dashboard.py`

## Overview

The VCD Health Dashboard provides real-time monitoring, performance metrics, alerting, and trend analysis for the Visual Cognitive Debugger system. It collects system health data, evaluates alert conditions, and provides comprehensive health reporting.

## Prerequisites

- Python 3.8+
- `psutil` library (optional, for system metrics): `pip install psutil`
- VCD Bridge connection (optional, for bridge status)
- Access to system logs

## Installation

### Step 1: Install Dependencies

```bash
pip install psutil statistics
```

### Step 2: Verify Installation

```python
python3 -c "from Three_PointO_ArchE.vcd_health_dashboard import VCDHealthCollector; print('✅ Health Dashboard available')"
```

## Basic Usage

### Initializing the Health Collector

```python
from Three_PointO_ArchE.vcd_health_dashboard import VCDHealthCollector, VCDHealthDashboardAPI

# Initialize collector
collector = VCDHealthCollector()

# Initialize API
api = VCDHealthDashboardAPI(collector)
```

### Getting Health Overview

```python
# Get comprehensive health overview
overview = api.get_health_overview()

print(f"Overall Status: {overview['overall_status']}")
print(f"Active Alerts: {overview['alert_summary']['total']}")
print(f"Critical Alerts: {overview['alert_summary']['critical']}")
```

### Collecting System Metrics

```python
# Collect current system metrics
system_health = collector.collect_system_metrics()

print(f"VCD Bridge Status: {system_health.vcd_bridge_status}")
print(f"Active Connections: {system_health.active_connections}")
print(f"Memory Usage: {system_health.memory_usage:.1%}")
print(f"CPU Usage: {system_health.cpu_usage:.1%}")
print(f"Response Time: {system_health.response_time}ms")
```

## Advanced Usage

### Trend Analysis

```python
# Get trend analysis for specific metrics
response_trend = api.get_trend_analysis("response_time", time_window_hours=24)
memory_trend = api.get_trend_analysis("memory_usage", time_window_hours=24)
cpu_trend = api.get_trend_analysis("cpu_usage", time_window_hours=24)

print(f"Response Time Trend: {response_trend['trend']}")
print(f"Memory Trend: {memory_trend['trend']}")
print(f"CPU Trend: {cpu_trend['trend']}")
```

### Performance Benchmarking

```python
# Get performance benchmarks
benchmarks = api.get_performance_benchmark()

print(f"Overall Meets Target: {benchmarks['overall_meets_target']}")
print(f"Response Time P95: {benchmarks['benchmarks']['response_time']['p95']}ms")
print(f"Memory Average: {benchmarks['benchmarks']['memory_usage']['average']:.1%}")
```

### Alert Management

```python
# Get all alerts
all_alerts = api.get_alerts()

# Get critical alerts only
critical_alerts = api.get_alerts(level="critical")

# Get active alerts
active_alerts = api.get_alerts(status="active")

# Acknowledge an alert
success, message = api.acknowledge_alert("alert_12345")

# Resolve an alert
success, message = api.resolve_alert("alert_12345")
```

### Exporting Health Reports

```python
# Export comprehensive health report
success, message = api.export_health_report(
    output_path="reports/vcd_health_report.json",
    format="json"
)

# Export as YAML (requires PyYAML)
success, message = api.export_health_report(
    output_path="reports/vcd_health_report.yaml",
    format="yaml"
)
```

### Historical Data Access

```python
from datetime import datetime, timedelta

# Get metrics from last hour
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

metrics = collector.get_historical_metrics(start_time, end_time)

print(f"Metrics collected: {len(metrics)}")
for metric in metrics:
    print(f"  {metric.timestamp}: {metric.response_time}ms")
```

## API Reference

### VCDHealthCollector Class

#### `__init__(vcd_bridge_client=None, metrics_history_size=1000)`
Initialize health collector.

**Parameters:**
- `vcd_bridge_client`: Optional VCD Bridge client for connection status
- `metrics_history_size`: Number of historical metrics to retain

#### `collect_system_metrics() -> SystemHealth`
Collect current system health metrics.

#### `collect_performance_metrics() -> PerformanceMetrics`
Collect and store performance metrics.

#### `collect_component_health() -> Dict[str, ComponentHealth]`
Collect health status of all VCD components.

#### `evaluate_alert_conditions() -> List[Alert]`
Evaluate alert conditions and generate alerts.

### VCDHealthDashboardAPI Class

#### `get_health_overview() -> Dict[str, Any]`
Get comprehensive system health overview.

#### `get_performance_metrics(start_time=None, end_time=None) -> Dict[str, Any]`
Get performance metrics with statistics.

#### `get_component_health() -> Dict[str, Any]`
Get component health status.

#### `get_alerts(level=None, status=None) -> Dict[str, Any]`
Get alerts with optional filtering.

#### `get_trend_analysis(metric_name, time_window_hours=24) -> Dict[str, Any]`
Get trend analysis for a specific metric.

#### `get_performance_benchmark() -> Dict[str, Any]`
Get performance benchmarks and comparisons.

#### `export_health_report(output_path=None, format="json") -> Tuple[bool, str]`
Export comprehensive health report.

## Configuration

### Alert Thresholds

```python
# Customize alert thresholds
collector.thresholds = {
    "memory_usage": {"warning": 0.75, "critical": 0.90},
    "cpu_usage": {"warning": 0.75, "critical": 0.90},
    "response_time": {"warning": 500.0, "critical": 2000.0},
    "connection_count": {"warning": 50, "critical": 80}
}
```

### Metrics History Size

```python
# Increase history size for longer retention
collector = VCDHealthCollector(metrics_history_size=5000)
```

## Troubleshooting

### No Metrics Collected

**Problem**: `collect_system_metrics()` returns empty or default values

**Solutions**:
1. Verify psutil installation: `pip install psutil`
2. Check system permissions
3. Verify VCD Bridge connection if needed
4. Check logs for errors

### Alerts Not Triggering

**Problem**: System issues but no alerts generated

**Solutions**:
1. Verify thresholds are set correctly
2. Check `evaluate_alert_conditions()` is being called
3. Review alert logic in code
4. Test with manual threshold violations

### High Memory Usage

**Problem**: Dashboard using excessive memory

**Solutions**:
1. Reduce `metrics_history_size`
2. Implement data retention policies
3. Use external time-series database
4. Clear old metrics periodically

## Best Practices

1. **Regular Monitoring**
   - Collect metrics every 30-60 seconds
   - Evaluate alerts continuously
   - Review trends daily

2. **Alert Management**
   - Set appropriate thresholds
   - Acknowledge alerts promptly
   - Track alert resolution

3. **Data Retention**
   - Store historical data for analysis
   - Implement retention policies
   - Archive old data

4. **Reporting**
   - Export reports regularly
   - Compare reports over time
   - Share with stakeholders

## Examples

### Example 1: Continuous Monitoring

```python
import asyncio
from Three_PointO_ArchE.vcd_health_dashboard import VCDHealthCollector, VCDHealthDashboardAPI

async def continuous_monitoring():
    collector = VCDHealthCollector()
    api = VCDHealthDashboardAPI(collector)
    
    while True:
        # Collect metrics
        collector.collect_performance_metrics()
        
        # Evaluate alerts
        alerts = collector.evaluate_alert_conditions()
        
        # Check for critical alerts
        critical = [a for a in alerts if a.level == "critical"]
        if critical:
            print(f"⚠️ {len(critical)} critical alerts!")
        
        # Wait 30 seconds
        await asyncio.sleep(30)

asyncio.run(continuous_monitoring())
```

### Example 2: Health Check Script

```python
from Three_PointO_ArchE.vcd_health_dashboard import VCDHealthCollector, VCDHealthDashboardAPI

def health_check():
    collector = VCDHealthCollector()
    api = VCDHealthDashboardAPI(collector)
    
    overview = api.get_health_overview()
    
    if overview['overall_status'] == "healthy":
        print("✅ System healthy")
        return 0
    elif overview['overall_status'] == "degraded":
        print("⚠️ System degraded")
        return 1
    else:
        print("❌ System critical")
        return 2

if __name__ == "__main__":
    exit(health_check())
```

### Example 3: Daily Report

```python
from datetime import datetime

def generate_daily_report():
    collector = VCDHealthCollector()
    api = VCDHealthDashboardAPI(collector)
    
    # Export report
    timestamp = datetime.now().strftime("%Y%m%d")
    success, message = api.export_health_report(
        output_path=f"reports/daily_health_{timestamp}.json"
    )
    
    if success:
        print(f"✅ Report generated: {message}")
    else:
        print(f"❌ Failed: {message}")

generate_daily_report()
```

## Related Components

- **VCD Bridge**: Provides connection status
- **VCD Analysis Agent**: Uses dashboard for analysis
- **System Health Monitor**: Provides base metrics
- **VCD Testing Suite**: Validates dashboard functionality

## Support

For issues or questions:
1. Check dashboard logs: `logs/vcd_health_*.log`
2. Review metrics history: `logs/vcd_health_history/`
3. Run diagnostics: `python3 -m Three_PointO_ArchE.vcd_testing_suite`
4. Check system resources: `top` or `htop`

---

**Previous Guide**: [VCD Analysis Agent Guide](02_VCD_Analysis_Agent_Guide.md)  
**Next Guide**: [VCD Backup & Recovery Guide](04_VCD_Backup_Recovery_Guide.md)

