# VCD Configuration Management - Complete How-To Guide

**Component**: Visual Cognitive Debugger Configuration Management  
**Version**: 1.0  
**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:42:00 EST  
**File**: `Three_PointO_ArchE/vcd_configuration_management.py`

## Overview

The VCD Configuration Management system provides centralized configuration management, validation, versioning, and deployment for all VCD components. It ensures configuration integrity, tracks changes, and enables rollback capabilities.

## Prerequisites

- Python 3.8+
- Write access to configuration directory
- JSON support

## Installation

```bash
# No additional installation required - part of Three_PointO_ArchE
python3 -c "from Three_PointO_ArchE.vcd_configuration_management import VCDConfigurationManager; print('✅ Available')"
```

## Basic Usage

### Initializing Configuration Manager

```python
from Three_PointO_ArchE.vcd_configuration_management import VCDConfigurationManager

manager = VCDConfigurationManager()
```

### Setting Configuration

```python
# Set VCD Bridge configuration
vcd_bridge_config = {
    "server": {
        "host": "localhost",
        "port": 8765,
        "timeout": 5,
        "max_connections": 100
    },
    "websocket": {
        "ping_interval": 20,
        "ping_timeout": 10
    },
    "logging": {
        "level": "INFO",
        "file": "logs/vcd_bridge.log"
    }
}

success, error, validation = manager.set_config(
    "vcd_bridge",
    vcd_bridge_config,
    environment="production",
    author="admin",
    change_description="Initial production configuration"
)

if success:
    print("✅ Configuration saved")
else:
    print(f"❌ Error: {error}")
```

### Getting Configuration

```python
# Get configuration
config = manager.get_config("vcd_bridge", environment="production")

if config:
    print(f"Port: {config['server']['port']}")
```

### Validating Configuration

```python
# Validate without saving
validation = manager.validate_config("vcd_bridge", vcd_bridge_config)

if validation.is_valid:
    print("✅ Configuration is valid")
else:
    print(f"❌ Errors: {validation.errors}")
    print(f"⚠️ Warnings: {validation.warnings}")
```

## Advanced Usage

### Configuration Versioning

```python
# Get configuration history
history = manager.get_config_history("vcd_bridge", environment="production")

for version in history[:5]:  # Last 5 versions
    print(f"Version: {version.version_id}")
    print(f"  Author: {version.author}")
    print(f"  Description: {version.change_description}")
    print(f"  Timestamp: {version.timestamp}")
```

### Rollback Configuration

```python
# Rollback to previous version
success, message = manager.rollback_config(
    "vcd_bridge",
    version_id="1234567890_abc12345",
    environment="production"
)

if success:
    print(f"✅ {message}")
```

### Deploying Configuration

```python
# Deploy configuration to environment
success, message = manager.deploy_config(
    "vcd_bridge",
    environment="production"
)

if success:
    print(f"✅ {message}")
```

## API Reference

### VCDConfigurationManager Class

#### `__init__(config_root=None)`
Initialize configuration manager.

#### `get_config(component, environment="default") -> Optional[Dict]`
Get configuration for a component.

#### `set_config(component, config, environment="default", author="system", change_description="Configuration update") -> Tuple[bool, Optional[str], ValidationResult]`
Set configuration with validation and versioning.

#### `validate_config(component, config) -> ValidationResult`
Validate configuration without saving.

#### `deploy_config(component, environment="default") -> Tuple[bool, str]`
Deploy configuration to target environment.

#### `rollback_config(component, version_id, environment="default") -> Tuple[bool, str]`
Rollback to a previous configuration version.

#### `get_config_history(component, environment="default") -> List[ConfigurationVersion]`
Get configuration change history.

## Configuration Structure

### VCD Bridge Configuration

```yaml
server:
  host: "localhost"
  port: 8765
  timeout: 5
  max_connections: 100
  heartbeat_interval: 30

websocket:
  ping_interval: 20
  ping_timeout: 10
  close_timeout: 10
  max_size: 1048576

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/vcd_bridge.log"
```

## Troubleshooting

### Validation Failures

**Problem**: Configuration validation fails

**Solutions**:
1. Check required fields are present
2. Verify data types match schema
3. Review validation errors in `ValidationResult`
4. Check security warnings

### Configuration Not Found

**Problem**: `get_config()` returns None

**Solutions**:
1. Verify component name is correct
2. Check environment name
3. Verify configuration file exists
4. Check file permissions

## Best Practices

1. **Version Control**: Always use versioning for production configs
2. **Validation**: Validate before saving
3. **Environments**: Use separate environments for dev/staging/prod
4. **Documentation**: Include clear change descriptions
5. **Backup**: Backup configurations before major changes

## Examples

### Example 1: Environment-Specific Configuration

```python
# Development configuration
dev_config = {"server": {"port": 8766, "host": "localhost"}}
manager.set_config("vcd_bridge", dev_config, environment="development")

# Production configuration
prod_config = {"server": {"port": 8765, "host": "0.0.0.0"}}
manager.set_config("vcd_bridge", prod_config, environment="production")
```

### Example 2: Configuration Migration

```python
# Get current config
current = manager.get_config("vcd_bridge", "production")

# Modify
current["server"]["port"] = 9000

# Save with description
manager.set_config(
    "vcd_bridge",
    current,
    environment="production",
    change_description="Port migration to 9000"
)
```

## Related Components

- **VCD Backup & Recovery**: Backs up configuration files
- **VCD Health Dashboard**: Monitors configuration changes
- **VCD Testing Suite**: Tests configuration validation

## Support

For issues:
1. Check configuration files: `config/vcd/`
2. Review validation errors
3. Check configuration history
4. Verify file permissions

---

**Previous Guide**: [VCD Backup & Recovery Guide](04_VCD_Backup_Recovery_Guide.md)  
**Next Guide**: [VCD Testing Suite Guide](06_VCD_Testing_Suite_Guide.md)
