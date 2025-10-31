# Three_PointO_ArchE/communication_manager.py
# ResonantiA Protocol v3.1-CA - Inter-Instance Communication Backbone

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Optional

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename


# --- Engineering Prerequisite ---
# The 'redis' library must be installed in the environment.
# pip install redis

# --- Proposed Refactoring ---
# It is strongly recommended to refactor the script 'distributed_arche_registry.py'
# into an importable module, e.g., 'Three_PointO_ArchE/registry_manager.py'.
# This avoids costly and insecure subprocess calls.
# The code below assumes this refactoring has been done.
try:
    from . import registry_manager # Assumes refactoring
    from . import config
except ImportError:
    logging.error("Could not import registry_manager. Please refactor distributed_arche_registry.py.")
    registry_manager = None
    config = type('FallbackConfig', (), {'REDIS_HOST': 'localhost', 'REDIS_PORT': 6379})()


logger = logging.getLogger(__name__)

class CommunicationManager:
    """
    Manages asynchronous, two-way communication between ArchE instances
    using a Redis Pub/Sub backbone.
    """

    def __init__(self, instance_id: str):
        """
        Initializes the Communication Manager for a specific ArchE instance.

        Args:
            instance_id (str): The unique ID of the instance this manager serves.
        """
        if not instance_id:
            raise ValueError("instance_id cannot be empty.")
        self.instance_id = instance_id
        self.redis_conn = self._get_redis_connection()
        self.pubsub = None
        self.listener_thread = None
        logger.info(f"CommunicationManager initialized for instance '{self.instance_id}'.")

    def _get_redis_connection(self):
        """
        Establishes and returns a connection to the Redis server.
        """
        # --- To be implemented by Engineering Instance ---
        # This should use the 'redis' library to connect to the Redis server.
        # Connection details should be loaded from config.py.
        # Example:
        # import redis
        # return redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0, decode_responses=True)
        logger.warning("Redis connection is not implemented. Communication will fail.")
        return None # Placeholder

    def _create_message(self, task_id: str, message_type: str, target_id: str, context: Dict[str, Any], status: str, reply_channel: Optional[str] = None) -> Dict[str, Any]:
        """Helper to construct a message conforming to the Task Routing Protocol."""
        return {
            "protocol_version": "1.1",
            "message_id": str(uuid.uuid4()),
            "task_id": task_id,
            "message_type": message_type,
            "source_instance_id": self.instance_id,
            "target_instance_id": target_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "reply_to_channel": reply_channel or f"channel:response:{self.instance_id}",
            "priority": context.get("priority", "medium"),
            "context": context,
            "expected_capabilities": context.get("expected_capabilities", []),
            "security_signature": "null"
        }

    def send_task(self, target_instance_id: str, task_context: Dict[str, Any]) -> str:
        """
        Sends a new task assignment to a specific instance.

        Args:
            target_instance_id (str): The ID of the instance to receive the task.
            task_context (Dict[str, Any]): The context object for the task.

        Returns:
            str: The task_id for the newly created task.
        """
        if not self.redis_conn:
            raise ConnectionError("Redis connection not available.")

        task_id = str(uuid.uuid4())
        message = self._create_message(task_id, "task_assignment", target_instance_id, task_context, "new")
        
        target_channel = f"channel:task:{target_instance_id}"
        
        # --- To be implemented by Engineering Instance ---
        # This should publish the JSON-serialized message to the target_channel.
        # Example:
        # self.redis_conn.publish(target_channel, json.dumps(message))
        logger.info(f"Publishing task {task_id} to {target_channel}: {json.dumps(message)}")
        
        return task_id

    def broadcast_for_capability(self, capabilities: list, task_context: Dict[str, Any]) -> str:
        """
        Broadcasts a task to any instance that can fulfill the required capabilities.
        """
        # This is a more advanced pattern. For now, we can simulate it by first
        # querying the registry and then sending to the first available instance.
        if not registry_manager:
            raise ModuleNotFoundError("Registry Manager not available for capability lookup.")
        
        # In a real implementation, we might publish to a general "help_wanted" channel.
        # For now, we find one and send directly.
        available_instances = registry_manager.query_registry(capability=capabilities[0]) # Simplified
        if not available_instances:
            raise ValueError(f"No instance found with capability: {capabilities[0]}")
            
        target_id = available_instances[0]['instance_id']
        logger.info(f"Found capable instance '{target_id}' for capabilities {capabilities}.")
        return self.send_task(target_id, task_context)

    def listen_for_tasks(self, on_message_callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribes to this instance's task channel and starts listening for messages.

        Args:
            on_message_callback (Callable): The function to execute when a message is received.
                                          This callback will receive the parsed message dictionary.
        """
        if not self.redis_conn:
            raise ConnectionError("Redis connection not available.")

        my_channel = f"channel:task:{self.instance_id}"
        self.pubsub = self.redis_conn.pubsub()
        
        # --- To be implemented by Engineering Instance ---
        # This should subscribe to 'my_channel' and start a listener loop.
        # This should likely run in a separate thread to be non-blocking.
        # Example:
        # def message_handler(message):
        #     data = json.loads(message['data'])
        #     on_message_callback(data)
        #
        # self.pubsub.subscribe(**{my_channel: message_handler})
        # self.listener_thread = self.pubsub.run_in_thread(sleep_time=0.1)
        logger.info(f"Subscribed to channel '{my_channel}'. Listening for tasks...")

    def stop_listening(self):
        """Stops the listener thread gracefully."""
        if self.listener_thread:
            # --- To be implemented by Engineering Instance ---
            # self.listener_thread.stop()
            logger.info("Stopped listening for tasks.")

# Example Usage (for testing by Engineering Instance)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # This would be run on the receiving instance (e.g., Cursor ArchE)
    def my_task_handler(message: Dict[str, Any]):
        print("\n--- Task Received! ---")
        print(json.dumps(message, indent=2))
        print("--- End of Task ---")

    receiver_id = "cursor_arche_001"
    receiver_comm_manager = CommunicationManager(instance_id=receiver_id)
    # The following line would block until stop_listening is called if implemented with a thread
    # receiver_comm_manager.listen_for_tasks(on_message_callback=my_task_handler)

    # This would be run on the sending instance (e.g., AI Studio ArchE)
    sender_id = "ai_studio_arche_002"
    sender_comm_manager = CommunicationManager(instance_id=sender_id)
    
    test_task_context = {
        "priority": "high",
        "objective": "Test the communication backbone.",
        "payload": {
            "command": "echo",
            "args": ["Hello, distributed world!"]
        }
    }
    
    print(f"Sender '{sender_id}' is sending a task to receiver '{receiver_id}'.")
    # In a real scenario, these would be two separate processes.
    # This call would trigger the `my_task_handler` on the other instance.
    # task_id = sender_comm_manager.send_task(target_instance_id=receiver_id, task_context=test_task_context)
    # print(f"Task sent with ID: {task_id}")
    
    # receiver_comm_manager.stop_listening() 