# Three_PointO_ArchE/registry_manager.py
"""
Distributed ArchE Instance Registry System
Enables discovery, registration, and coordination of heterogeneous ArchE instances
"""

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class InstanceType(Enum):
    ENGINEERING = "engineering"
    ANALYTICAL = "analytical"
    INTERFACE = "interface"
    SPECIALIZED = "specialized"

class InstanceStatus(Enum):
    ACTIVE = "active"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

@dataclass
class InstanceCapability:
    name: str
    level: str
    specializations: List[str]
    last_validated: str
    success_rate: float

@dataclass
class ArchEInstance:
    instance_id: str
    instance_type: InstanceType
    name: str
    description: str
    capabilities: List[InstanceCapability]
    status: InstanceStatus
    last_active: str
    total_tasks_completed: int
    success_rate: float
    current_load: int
    max_concurrent_tasks: int
    metadata: Dict[str, Any]

class DistributedArchERegistry:
    """Central registry for distributed ArchE instance management"""

    def __init__(self, registry_file: str = "arche_registry.json"):
        self.registry_file = registry_file
        self.instances: Dict[str, ArchEInstance] = {}
        self.load_registry()

    def register_instance(self,
                         instance_type: InstanceType,
                         name: str,
                         description: str,
                         capabilities: List[Dict[str, Any]],
                         max_concurrent_tasks: int = 5,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Register a new ArchE instance"""
        instance_id = f"{instance_type.value}_{uuid.uuid4().hex[:8]}"
        capability_objects = [
            InstanceCapability(
                name=cap["name"],
                level=cap.get("level", "basic"),
                specializations=cap.get("specializations", []),
                last_validated=datetime.now(timezone.utc).isoformat(),
                success_rate=cap.get("success_rate", 1.0)
            ) for cap in capabilities
        ]
        instance = ArchEInstance(
            instance_id=instance_id,
            instance_type=instance_type,
            name=name,
            description=description,
            capabilities=capability_objects,
            status=InstanceStatus.ACTIVE,
            last_active=datetime.now(timezone.utc).isoformat(),
            total_tasks_completed=0,
            success_rate=1.0,
            current_load=0,
            max_concurrent_tasks=max_concurrent_tasks,
            metadata=metadata or {}
        )
        self.instances[instance_id] = instance
        self.save_registry()
        logger.info(f"Registered {instance_type.value} instance: {name} ({instance_id})")
        return instance_id

    def find_capable_instances(self, required_capabilities: List[str]) -> List[ArchEInstance]:
        """Find instances with required capabilities"""
        capable_instances = []
        for instance in self.instances.values():
            if instance.status != InstanceStatus.ACTIVE:
                continue
            if instance.current_load >= instance.max_concurrent_tasks:
                continue
            
            instance_capabilities = {cap.name for cap in instance.capabilities}
            if all(req_cap in instance_capabilities for req_cap in required_capabilities):
                capable_instances.append(instance)
        
        capable_instances.sort(key=lambda x: (x.success_rate, -x.current_load), reverse=True)
        return capable_instances

    def get_instance(self, instance_id: str) -> Optional[ArchEInstance]:
        return self.instances.get(instance_id)

    def save_registry(self):
        """Save registry to file"""
        try:
            serializable_instances = []
            for instance in self.instances.values():
                instance_dict = asdict(instance)
                instance_dict["instance_type"] = instance.instance_type.value
                instance_dict["status"] = instance.status.value
                serializable_instances.append(instance_dict)

            data = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "instances": serializable_instances
            }
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving registry: {e}")

    def load_registry(self):
        """Load registry from file"""
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)

            for instance_data in data.get("instances", []):
                try:
                    capabilities = [InstanceCapability(**cap_data) for cap_data in instance_data.get("capabilities", [])]
                    instance_data["capabilities"] = capabilities
                    instance_data["instance_type"] = InstanceType(instance_data["instance_type"])
                    instance_data["status"] = InstanceStatus(instance_data["status"])
                    instance = ArchEInstance(**instance_data)
                    self.instances[instance.instance_id] = instance
                except (TypeError, KeyError) as e:
                    logger.warning(f"Could not load instance data, skipping. Error: {e}. Data: {instance_data}")

        except FileNotFoundError:
            logger.warning("Registry file not found, starting with empty registry.")
        except Exception as e:
            logger.error(f"Error loading registry: {e}")

# --- Singleton Instance ---
_registry_instance = None

def get_registry() -> DistributedArchERegistry:
    """Gets a singleton instance of the registry."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = DistributedArchERegistry()
    return _registry_instance

# --- Public API ---

def query_registry(capability: str) -> List[Dict[str, Any]]:
    """
    Queries the registry for instances with a specific capability.

    Args:
        capability (str): The capability to search for.

    Returns:
        List[Dict[str, Any]]: A list of instance dictionaries matching the criteria.
    """
    registry = get_registry()
    instances = registry.find_capable_instances([capability])
    # Convert to list of dicts for external consumers
    return [asdict(instance) for instance in instances]

def register_new_instance(**kwargs) -> str:
    """Registers a new instance. A wrapper for the class method."""
    registry = get_registry()
    return registry.register_instance(**kwargs) 