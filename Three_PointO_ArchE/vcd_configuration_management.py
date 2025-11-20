#!/usr/bin/env python3
"""
VCD Configuration Management System
Centralized configuration management for Visual Cognitive Debugger components

This module provides configuration management, validation, deployment, and
versioning for all VCD system components.

Part of ResonantiA Protocol v3.5-GP Implementation Resonance initiative.
"""

import json
import copy
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import logging
import hashlib

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer

logger = logging.getLogger(__name__)

@dataclass
class ConfigurationVersion:
    """A versioned configuration entry."""
    version_id: str
    component: str
    environment: str
    config_data: Dict[str, Any]
    timestamp: str
    author: str
    change_description: str
    checksum: str
    parent_version: Optional[str] = None

@dataclass
class ValidationResult:
    """Result of configuration validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_errors: List[str] = field(default_factory=list)
    dependency_errors: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    performance_warnings: List[str] = field(default_factory=list)

class ConfigurationValidator:
    """
    Configuration Validator - Validates configuration data.
    
    Provides:
    - Schema validation
    - Dependency checking
    - Security validation
    - Performance validation
    """
    
    def __init__(self):
        """Initialize Configuration Validator."""
        # Define schemas for VCD components
        self.schemas = {
            "vcd_bridge": {
                "type": "object",
                "required": ["server", "websocket", "logging"],
                "properties": {
                    "server": {
                        "type": "object",
                        "required": ["host", "port"],
                        "properties": {
                            "host": {"type": "string"},
                            "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                            "timeout": {"type": "integer", "minimum": 1},
                            "max_connections": {"type": "integer", "minimum": 1},
                            "heartbeat_interval": {"type": "integer", "minimum": 1}
                        }
                    },
                    "websocket": {
                        "type": "object",
                        "properties": {
                            "ping_interval": {"type": "integer", "minimum": 1},
                            "ping_timeout": {"type": "integer", "minimum": 1},
                            "close_timeout": {"type": "integer", "minimum": 1},
                            "max_size": {"type": "integer", "minimum": 1}
                        }
                    },
                    "logging": {
                        "type": "object",
                        "required": ["level"],
                        "properties": {
                            "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                            "format": {"type": "string"},
                            "file": {"type": "string"}
                        }
                    }
                }
            },
            "vcd_ui": {
                "type": "object",
                "required": ["visualization", "performance"],
                "properties": {
                    "visualization": {
                        "type": "object",
                        "properties": {
                            "default_modes": {"type": "array", "items": {"type": "string"}},
                            "refresh_interval": {"type": "integer", "minimum": 1},
                            "data_retention": {"type": "integer", "minimum": 1}
                        }
                    },
                    "performance": {
                        "type": "object",
                        "properties": {
                            "max_data_points": {"type": "integer", "minimum": 1},
                            "compression_enabled": {"type": "boolean"},
                            "cache_size": {"type": "integer", "minimum": 1}
                        }
                    }
                }
            },
            "vcd_analysis_agent": {
                "type": "object",
                "required": ["analysis", "reporting"],
                "properties": {
                    "analysis": {
                        "type": "object",
                        "properties": {
                            "session_timeout": {"type": "integer", "minimum": 1},
                            "max_concurrent_analyses": {"type": "integer", "minimum": 1},
                            "analysis_interval": {"type": "integer", "minimum": 1}
                        }
                    },
                    "reporting": {
                        "type": "object",
                        "properties": {
                            "output_format": {"type": "string", "enum": ["json", "yaml", "text"]},
                            "include_iar": {"type": "boolean"},
                            "save_to_file": {"type": "boolean"}
                        }
                    }
                }
            }
        }
        
        # Define dependencies between components
        self.dependencies = {
            "vcd_ui": ["vcd_bridge"],
            "vcd_analysis_agent": ["vcd_bridge"]
        }
        
        logger.info("ConfigurationValidator initialized")
    
    def validate_schema(self, component: str, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration against schema.
        
        Args:
            component: Component name
            config: Configuration data
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        if component not in self.schemas:
            result.is_valid = False
            result.errors.append(f"Unknown component: {component}")
            return result
        
        schema = self.schemas[component]
        
        # Basic type and structure validation
        if not isinstance(config, dict):
            result.is_valid = False
            result.errors.append("Configuration must be a dictionary")
            return result
        
        # Check required fields
        required = schema.get("required", [])
        for field_name in required:
            if field_name not in config:
                result.is_valid = False
                result.schema_errors.append(f"Missing required field: {field_name}")
        
        # Validate properties
        properties = schema.get("properties", {})
        for field_name, field_value in config.items():
            if field_name in properties:
                field_schema = properties[field_name]
                field_errors = self._validate_field(field_name, field_value, field_schema)
                result.schema_errors.extend(field_errors)
                if field_errors:
                    result.is_valid = False
        
        return result
    
    def _validate_field(self, field_name: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Validate a single field against its schema."""
        errors = []
        
        expected_type = schema.get("type")
        if expected_type:
            type_map = {
                "string": str,
                "integer": int,
                "boolean": bool,
                "object": dict,
                "array": list
            }
            expected_python_type = type_map.get(expected_type)
            if expected_python_type and not isinstance(value, expected_python_type):
                errors.append(f"{field_name}: Expected {expected_type}, got {type(value).__name__}")
        
        # Validate enum
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"{field_name}: Value must be one of {schema['enum']}")
        
        # Validate minimum/maximum
        if isinstance(value, (int, float)):
            if "minimum" in schema and value < schema["minimum"]:
                errors.append(f"{field_name}: Value {value} is below minimum {schema['minimum']}")
            if "maximum" in schema and value > schema["maximum"]:
                errors.append(f"{field_name}: Value {value} exceeds maximum {schema['maximum']}")
        
        # Recursively validate nested objects
        if isinstance(value, dict) and "properties" in schema:
            for nested_field, nested_value in value.items():
                if nested_field in schema["properties"]:
                    nested_errors = self._validate_field(
                        f"{field_name}.{nested_field}",
                        nested_value,
                        schema["properties"][nested_field]
                    )
                    errors.extend(nested_errors)
        
        return errors
    
    def validate_dependencies(self, component: str, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration dependencies.
        
        Args:
            component: Component name
            config: Configuration data
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        if component in self.dependencies:
            required_components = self.dependencies[component]
            # Check if dependent components are configured
            # This is a simplified check - full implementation would verify actual configs exist
            for dep_component in required_components:
                result.warnings.append(f"Component {component} depends on {dep_component} - ensure it is configured")
        
        return result
    
    def validate_security(self, component: str, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration security.
        
        Args:
            component: Component name
            config: Configuration data
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Check for sensitive data exposure
        sensitive_keys = ["password", "secret", "key", "token", "api_key"]
        config_str = json.dumps(config).lower()
        
        for sensitive_key in sensitive_keys:
            if sensitive_key in config_str:
                result.security_issues.append(f"Potential sensitive data detected: {sensitive_key}")
                result.warnings.append(f"Ensure sensitive data is encrypted")
        
        # Check for insecure defaults
        if component == "vcd_bridge":
            server_config = config.get("server", {})
            if server_config.get("host") == "0.0.0.0":
                result.security_issues.append("Binding to 0.0.0.0 exposes service to all interfaces")
        
        return result
    
    def validate_performance(self, component: str, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration performance implications.
        
        Args:
            component: Component name
            config: Configuration data
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        if component == "vcd_bridge":
            server_config = config.get("server", {})
            max_connections = server_config.get("max_connections", 100)
            if max_connections > 1000:
                result.performance_warnings.append("High max_connections may impact performance")
        
        if component == "vcd_ui":
            perf_config = config.get("performance", {})
            max_data_points = perf_config.get("max_data_points", 10000)
            if max_data_points > 100000:
                result.performance_warnings.append("Very high max_data_points may cause memory issues")
        
        return result
    
    def validate_config(self, component: str, config: Dict[str, Any]) -> ValidationResult:
        """
        Perform complete configuration validation.
        
        Args:
            component: Component name
            config: Configuration data
            
        Returns:
            ValidationResult with all validation results
        """
        # Run all validations
        schema_result = self.validate_schema(component, config)
        dep_result = self.validate_dependencies(component, config)
        sec_result = self.validate_security(component, config)
        perf_result = self.validate_performance(component, config)
        
        # Combine results
        combined_result = ValidationResult(
            is_valid=schema_result.is_valid and len(sec_result.security_issues) == 0,
            errors=schema_result.errors,
            warnings=dep_result.warnings + sec_result.warnings + perf_result.performance_warnings,
            schema_errors=schema_result.schema_errors,
            dependency_errors=dep_result.errors,
            security_issues=sec_result.security_issues,
            performance_warnings=perf_result.performance_warnings
        )
        
        return combined_result


class VCDConfigurationManager:
    """
    VCD Configuration Manager - Centralized configuration management.
    
    Provides:
    - Configuration storage and retrieval
    - Version control and history
    - Environment-specific configurations
    - Configuration deployment
    - Rollback capabilities
    """
    
    def __init__(self, config_root: Optional[Path] = None):
        """
        Initialize VCD Configuration Manager.
        
        Args:
            config_root: Root directory for configurations (default: config/vcd/)
        """
        if config_root is None:
            config_root = Path("config/vcd")
        self.config_root = Path(config_root)
        self.config_root.mkdir(parents=True, exist_ok=True)
        
        self.validator = ConfigurationValidator()
        self.history_dir = self.config_root / "history"
        self.history_dir.mkdir(exist_ok=True)
        
        logger.info(f"VCDConfigurationManager initialized with config root: {self.config_root}")
    
    def get_config(
        self,
        component: str,
        environment: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a component.
        
        Args:
            component: Component name
            environment: Environment name (default: "default")
            
        Returns:
            Configuration dictionary or None if not found
        """
        config_path = self.config_root / environment / f"{component}.json"
        
        if not config_path.exists():
            # Try default environment
            if environment != "default":
                config_path = self.config_root / "default" / f"{component}.json"
            if not config_path.exists():
                return None
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config for {component}: {e}")
            return None
    
    def set_config(
        self,
        component: str,
        config: Dict[str, Any],
        environment: str = "default",
        author: str = "system",
        change_description: str = "Configuration update"
    ) -> Tuple[bool, Optional[str], Optional[ValidationResult]]:
        """
        Set configuration for a component.
        
        Args:
            component: Component name
            config: Configuration data
            environment: Environment name
            author: Author of the change
            change_description: Description of the change
            
        Returns:
            Tuple of (success, error_message, validation_result)
        """
        # Validate configuration
        validation_result = self.validator.validate_config(component, config)
        
        if not validation_result.is_valid:
            error_msg = f"Configuration validation failed: {', '.join(validation_result.errors)}"
            logger.error(error_msg)
            return False, error_msg, validation_result
        
        # Create environment directory
        env_dir = self.config_root / environment
        env_dir.mkdir(parents=True, exist_ok=True)
        
        # Get current config for versioning
        current_config = self.get_config(component, environment)
        parent_version = None
        if current_config:
            # Save current version to history
            parent_version = self._save_to_history(component, current_config, environment, author)
        
        # Save new configuration
        config_path = env_dir / f"{component}.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Save to history
            version_id = self._save_to_history(component, config, environment, author, change_description, parent_version)
            
            # Log change
            self._log_config_change(component, environment, author, change_description, version_id)
            
            logger.info(f"Configuration saved: {component} in {environment} (version: {version_id})")
            return True, None, validation_result
            
        except Exception as e:
            error_msg = f"Failed to save configuration: {e}"
            logger.error(error_msg)
            return False, error_msg, validation_result
    
    def validate_config(self, component: str, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration without saving.
        
        Args:
            component: Component name
            config: Configuration data
            
        Returns:
            ValidationResult
        """
        return self.validator.validate_config(component, config)
    
    def deploy_config(
        self,
        component: str,
        environment: str = "default"
    ) -> Tuple[bool, str]:
        """
        Deploy configuration to target environment.
        
        Args:
            component: Component name
            environment: Target environment
            
        Returns:
            Tuple of (success, message)
        """
        config = self.get_config(component, environment)
        if not config:
            return False, f"Configuration not found for {component} in {environment}"
        
        # In a real implementation, this would:
        # 1. Notify components of config change
        # 2. Reload configuration in running components
        # 3. Verify deployment success
        
        logger.info(f"Configuration deployed: {component} to {environment}")
        return True, f"Configuration deployed successfully"
    
    def rollback_config(
        self,
        component: str,
        version_id: str,
        environment: str = "default"
    ) -> Tuple[bool, str]:
        """
        Rollback configuration to a previous version.
        
        Args:
            component: Component name
            version_id: Version ID to rollback to
            environment: Environment name
            
        Returns:
            Tuple of (success, message)
        """
        # Load version from history
        version_path = self.history_dir / f"{component}_{version_id}.json"
        if not version_path.exists():
            return False, f"Version {version_id} not found"
        
        try:
            with open(version_path, 'r') as f:
                version_data = json.load(f)
            
            config_data = version_data.get("config_data", {})
            
            # Restore configuration
            success, error, _ = self.set_config(
                component,
                config_data,
                environment,
                author="system",
                change_description=f"Rollback to version {version_id}"
            )
            
            if success:
                return True, f"Configuration rolled back to version {version_id}"
            else:
                return False, error
                
        except Exception as e:
            return False, f"Rollback failed: {e}"
    
    def get_config_history(self, component: str, environment: str = "default") -> List[ConfigurationVersion]:
        """
        Get configuration history for a component.
        
        Args:
            component: Component name
            environment: Environment name
            
        Returns:
            List of ConfigurationVersion objects
        """
        history = []
        
        # Load all versions from history
        pattern = f"{component}_*.json"
        for version_file in self.history_dir.glob(pattern):
            try:
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                
                if version_data.get("environment") == environment:
                    history.append(ConfigurationVersion(**version_data))
            except Exception as e:
                logger.warning(f"Failed to load version {version_file}: {e}")
        
        # Sort by timestamp
        history.sort(key=lambda v: v.timestamp, reverse=True)
        return history
    
    def _save_to_history(
        self,
        component: str,
        config: Dict[str, Any],
        environment: str,
        author: str,
        change_description: str = "Configuration update",
        parent_version: Optional[str] = None
    ) -> str:
        """Save configuration version to history."""
        version_id = f"{int(datetime.now().timestamp())}_{hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]}"
        
        version = ConfigurationVersion(
            version_id=version_id,
            component=component,
            environment=environment,
            config_data=copy.deepcopy(config),
            timestamp=now_iso(),
            author=author,
            change_description=change_description,
            checksum=hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
            parent_version=parent_version
        )
        
        version_path = self.history_dir / f"{component}_{version_id}.json"
        with open(version_path, 'w') as f:
            json.dump(asdict(version), f, indent=2)
        
        return version_id
    
    def _log_config_change(
        self,
        component: str,
        environment: str,
        author: str,
        description: str,
        version_id: str
    ):
        """Log configuration change to audit log."""
        log_path = self.config_root / "audit_log.jsonl"
        
        log_entry = {
            "timestamp": now_iso(),
            "component": component,
            "environment": environment,
            "author": author,
            "description": description,
            "version_id": version_id
        }
        
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.warning(f"Failed to write audit log: {e}")


def main():
    """Demo the VCD Configuration Management System."""
    print("⚙️ Initializing VCD Configuration Management System...")
    print()
    
    manager = VCDConfigurationManager()
    
    print("✓ Manager initialized!")
    print()
    
    # Example: Set VCD Bridge configuration
    print("Setting VCD Bridge configuration...")
    vcd_bridge_config = {
        "server": {
            "host": "localhost",
            "port": 8765,
            "timeout": 5,
            "max_connections": 100,
            "heartbeat_interval": 30
        },
        "websocket": {
            "ping_interval": 20,
            "ping_timeout": 10,
            "close_timeout": 10,
            "max_size": 1048576
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/vcd_bridge.log"
        }
    }
    
    success, error, validation = manager.set_config(
        "vcd_bridge",
        vcd_bridge_config,
        author="system",
        change_description="Initial VCD Bridge configuration"
    )
    
    if success:
        print("  ✓ Configuration saved successfully")
        print(f"  Validation: {'Valid' if validation.is_valid else 'Invalid'}")
        if validation.warnings:
            print(f"  Warnings: {len(validation.warnings)}")
    else:
        print(f"  ✗ Failed: {error}")
    print()
    
    # Retrieve configuration
    print("Retrieving configuration...")
    retrieved_config = manager.get_config("vcd_bridge")
    if retrieved_config:
        print(f"  ✓ Configuration retrieved (port: {retrieved_config['server']['port']})")
    print()
    
    # Get history
    print("Configuration history:")
    history = manager.get_config_history("vcd_bridge")
    print(f"  Versions: {len(history)}")
    for version in history[:3]:  # Show first 3
        print(f"    - {version.version_id}: {version.change_description}")
    
    print()
    print("✓ VCD Configuration Management System operational!")


if __name__ == "__main__":
    main()























