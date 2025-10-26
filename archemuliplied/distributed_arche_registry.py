#!/usr/bin/env python3
"""
Distributed ArchE Instance Registry System
Enables discovery, registration, and coordination of heterogeneous ArchE instances
"""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

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
    level: str  # "basic", "intermediate", "advanced", "master"
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
        
        # Convert capability dictionaries to InstanceCapability objects
        capability_objects = []
        for cap in capabilities:
            capability_objects.append(InstanceCapability(
                name=cap["name"],
                level=cap.get("level", "basic"),
                specializations=cap.get("specializations", []),
                last_validated=datetime.now(timezone.utc).isoformat(),
                success_rate=cap.get("success_rate", 1.0)
            ))
        
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
        
        print(f"✅ Registered {instance_type.value} instance: {name} ({instance_id})")
        return instance_id
    
    def find_capable_instances(self, required_capabilities: List[str]) -> List[ArchEInstance]:
        """Find instances with required capabilities"""
        capable_instances = []
        
        for instance in self.instances.values():
            if instance.status != InstanceStatus.ACTIVE:
                continue
                
            if instance.current_load >= instance.max_concurrent_tasks:
                continue
            
            # Check if instance has all required capabilities
            instance_capabilities = [cap.name for cap in instance.capabilities]
            if all(req_cap in instance_capabilities for req_cap in required_capabilities):
                capable_instances.append(instance)
        
        # Sort by success rate and current load
        capable_instances.sort(key=lambda x: (x.success_rate, -x.current_load), reverse=True)
        return capable_instances
    
    def assign_task(self, instance_id: str, task_id: str) -> bool:
        """Assign a task to an instance"""
        if instance_id not in self.instances:
            return False
        
        instance = self.instances[instance_id]
        if instance.current_load >= instance.max_concurrent_tasks:
            return False
        
        instance.current_load += 1
        instance.status = InstanceStatus.BUSY if instance.current_load > 0 else InstanceStatus.ACTIVE
        instance.last_active = datetime.now(timezone.utc).isoformat()
        
        self.save_registry()
        return True
    
    def complete_task(self, instance_id: str, task_id: str, success: bool) -> bool:
        """Mark a task as completed"""
        if instance_id not in self.instances:
            return False
        
        instance = self.instances[instance_id]
        instance.current_load = max(0, instance.current_load - 1)
        instance.total_tasks_completed += 1
        
        # Update success rate (exponential moving average)
        alpha = 0.1  # Learning rate
        instance.success_rate = (1 - alpha) * instance.success_rate + alpha * (1.0 if success else 0.0)
        
        instance.status = InstanceStatus.ACTIVE if instance.current_load == 0 else InstanceStatus.BUSY
        instance.last_active = datetime.now(timezone.utc).isoformat()
        
        self.save_registry()
        return True
    
    def update_instance_status(self, instance_id: str, status: InstanceStatus) -> bool:
        """Update instance status"""
        if instance_id not in self.instances:
            return False
        
        self.instances[instance_id].status = status
        self.instances[instance_id].last_active = datetime.now(timezone.utc).isoformat()
        self.save_registry()
        return True
    
    def get_instance_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        stats = {
            "total_instances": len(self.instances),
            "active_instances": len([i for i in self.instances.values() if i.status == InstanceStatus.ACTIVE]),
            "busy_instances": len([i for i in self.instances.values() if i.status == InstanceStatus.BUSY]),
            "instance_types": {},
            "total_tasks_completed": sum(i.total_tasks_completed for i in self.instances.values()),
            "average_success_rate": sum(i.success_rate for i in self.instances.values()) / len(self.instances) if self.instances else 0
        }
        
        for instance_type in InstanceType:
            stats["instance_types"][instance_type.value] = len([
                i for i in self.instances.values() if i.instance_type == instance_type
            ])
        
        return stats
    
    def load_registry(self):
        """Load registry from file"""
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                
            for instance_data in data.get("instances", []):
                # Convert capability dictionaries back to InstanceCapability objects
                capabilities = []
                for cap_data in instance_data.get("capabilities", []):
                    capabilities.append(InstanceCapability(**cap_data))
                
                instance_data["capabilities"] = capabilities
                instance_data["instance_type"] = InstanceType(instance_data["instance_type"])
                instance_data["status"] = InstanceStatus(instance_data["status"])
                
                instance = ArchEInstance(**instance_data)
                self.instances[instance.instance_id] = instance
                
        except FileNotFoundError:
            print("Registry file not found, starting with empty registry")
        except Exception as e:
            print(f"Error loading registry: {e}")
    
    def save_registry(self):
        """Save registry to file"""
        try:
            # Convert instances to serializable format
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
            print(f"Error saving registry: {e}")

def initialize_cursor_arche_instance():
    """Initialize the Cursor ArchE instance in the registry"""
    registry = DistributedArchERegistry()
    
    cursor_arche_capabilities = [
        {
            "name": "file_manipulation",
            "level": "advanced",
            "specializations": ["python", "json", "markdown", "text_files"],
            "success_rate": 0.98
        },
        {
            "name": "code_execution",
            "level": "advanced", 
            "specializations": ["python", "bash", "subprocess"],
            "success_rate": 0.95
        },
        {
            "name": "workflow_debugging",
            "level": "master",
            "specializations": ["json_workflows", "inter_task_data_flow", "error_analysis"],
            "success_rate": 1.0
        },
        {
            "name": "terminal_access",
            "level": "advanced",
            "specializations": ["linux", "command_line", "process_management"],
            "success_rate": 0.97
        },
        {
            "name": "implementation_resonance",
            "level": "master",
            "specializations": ["strategic_to_tactical", "iterative_refinement", "solution_crystallization"],
            "success_rate": 1.0
        }
    ]
    
    cursor_arche_metadata = {
        "environment": "cursor_ide",
        "operating_system": "linux",
        "python_version": "3.12",
        "validated_workflows": ["ASASF_Persistent_Parallel_ArchE"],
        "specialization_focus": "engineering_implementation",
        "collaboration_history": ["ai_studio_arche_strategic_analysis"]
    }
    
    instance_id = registry.register_instance(
        instance_type=InstanceType.ENGINEERING,
        name="Cursor ArchE",
        description="Engineering Instance specialized in direct code manipulation, workflow debugging, and implementation resonance",
        capabilities=cursor_arche_capabilities,
        max_concurrent_tasks=3,
        metadata=cursor_arche_metadata
    )
    
    return instance_id, registry

if __name__ == "__main__":
    # Initialize the registry with Cursor ArchE
    instance_id, registry = initialize_cursor_arche_instance()
    
    # Display registry stats
    stats = registry.get_instance_stats()
    print(f"\n📊 Registry Statistics:")
    print(f"Total Instances: {stats['total_instances']}")
    print(f"Active Instances: {stats['active_instances']}")
    print(f"Instance Types: {stats['instance_types']}")
    print(f"Average Success Rate: {stats['average_success_rate']:.2%}")
    
    # Test capability matching
    required_caps = ["workflow_debugging", "implementation_resonance"]
    capable_instances = registry.find_capable_instances(required_caps)
    print(f"\n🔍 Instances capable of {required_caps}:")
    for instance in capable_instances:
        print(f"  - {instance.name} ({instance.instance_id}) - Success Rate: {instance.success_rate:.2%}") 