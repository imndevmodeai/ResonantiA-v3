import logging
import uuid
from typing import Dict, Any, List, Optional, Type

logger = logging.getLogger(__name__)

class ScalableAgent:
    """A scalable agent with lifecycle and status management."""

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.status = "initialized"
        logger.info(f"Agent {self.agent_id} created with config: {self.config}")

    def start(self):
        """Starts the agent."""
        self.status = "running"
        logger.info(f"Agent {self.agent_id} started.")

    def stop(self):
        """Stops the agent."""
        self.status = "stopped"
        logger.info(f"Agent {self.agent_id} stopped.")

    def get_status(self) -> str:
        """Returns the current status of the agent."""
        return self.status

class ScalableFramework:
    """A framework for managing a population of scalable agents."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, ScalableAgent] = {}
        self.status = "initialized"
        logger.info(f"ScalableFramework created with config: {self.config}")

    def add_agent(self, agent: ScalableAgent) -> bool:
        """Adds an agent to the framework."""
        if agent.agent_id in self.agents:
            logger.warning(f"Agent {agent.agent_id} already exists in the framework.")
            return False
        self.agents[agent.agent_id] = agent
        logger.info(f"Agent {agent.agent_id} added to the framework.")
        return True

    def start_all_agents(self):
        """Starts all agents in the framework."""
        for agent in self.agents.values():
            agent.start()
        self.status = "running"
        logger.info("All agents started.")

    def stop_all_agents(self):
        """Stops all agents in the framework."""
        for agent in self.agents.values():
            agent.stop()
        self.status = "stopped"
        logger.info("All agents stopped.")

def create_scalable_agent(agent_type: str, config: Dict[str, Any]) -> ScalableAgent:
    """Factory function to create a ScalableAgent."""
    agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
    return ScalableAgent(agent_id, config)

def create_scalable_framework(config: Dict[str, Any]) -> ScalableFramework:
    """Factory function to create a ScalableFramework."""
    return ScalableFramework(config)
