#!/usr/bin/env python3
"""
Strategic Interaction Model for Agent-Based Modeling
Used by the strategy_fusion workflow to simulate emergent behaviors of key agents.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class StrategicAgent:
    """Represents an agent in the strategic interaction simulation."""
    
    def __init__(self, agent_id: str, agent_type: str, initial_state: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = initial_state.copy()
        self.history = []
        self.connections = []
        
    def update_state(self, new_state: Dict[str, Any]):
        """Update agent state and record history."""
        self.history.append(self.state.copy())
        self.state.update(new_state)
        
    def get_influence_score(self) -> float:
        """Calculate agent's current influence score."""
        base_influence = self.state.get('base_influence', 0.5)
        network_position = len(self.connections) / 10.0  # Normalize by max connections
        recent_activity = len([h for h in self.history[-5:] if h.get('active', False)])
        return min(1.0, base_influence + network_position + recent_activity * 0.1)
        
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Agent decision-making logic based on type and context."""
        if self.agent_type == "stakeholder":
            return self._stakeholder_decision(context)
        elif self.agent_type == "decision_maker":
            return self._decision_maker_decision(context)
        elif self.agent_type == "influencer":
            return self._influencer_decision(context)
        elif self.agent_type == "resistor":
            return self._resistor_decision(context)
        else:
            return {"action": "neutral", "confidence": 0.5}
    
    def _stakeholder_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stakeholder decision logic - focuses on self-interest and risk assessment."""
        risk_tolerance = self.state.get('risk_tolerance', 0.5)
        benefit_threshold = self.state.get('benefit_threshold', 0.3)
        
        perceived_benefit = context.get('perceived_benefit', 0.5)
        perceived_risk = context.get('perceived_risk', 0.5)
        
        if perceived_benefit > benefit_threshold and perceived_risk < (1 - risk_tolerance):
            return {"action": "support", "confidence": min(1.0, perceived_benefit)}
        elif perceived_risk > (1 - risk_tolerance):
            return {"action": "oppose", "confidence": min(1.0, perceived_risk)}
        else:
            return {"action": "neutral", "confidence": 0.5}
    
    def _decision_maker_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decision maker logic - balances multiple factors and stakeholder input."""
        stakeholder_support = context.get('stakeholder_support', 0.5)
        resource_availability = context.get('resource_availability', 0.5)
        timeline_pressure = context.get('timeline_pressure', 0.5)
        
        # Weighted decision based on multiple factors
        decision_score = (
            stakeholder_support * 0.4 +
            resource_availability * 0.3 +
            (1 - timeline_pressure) * 0.3
        )
        
        if decision_score > 0.7:
            return {"action": "proceed", "confidence": decision_score}
        elif decision_score < 0.3:
            return {"action": "delay", "confidence": 1 - decision_score}
        else:
            return {"action": "modify", "confidence": 0.5}
    
    def _influencer_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Influencer logic - seeks to maximize impact and network position."""
        network_opportunity = context.get('network_opportunity', 0.5)
        current_influence = self.get_influence_score()
        strategic_alignment = context.get('strategic_alignment', 0.5)
        
        # Influencers act to maximize their influence
        if network_opportunity > 0.6 and strategic_alignment > 0.4:
            return {"action": "advocate", "confidence": network_opportunity}
        elif current_influence < 0.3:
            return {"action": "build_network", "confidence": 1 - current_influence}
        else:
            return {"action": "maintain_position", "confidence": current_influence}
    
    def _resistor_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resistor logic - opposes change and seeks to maintain status quo."""
        change_magnitude = context.get('change_magnitude', 0.5)
        status_quo_benefit = self.state.get('status_quo_benefit', 0.7)
        
        if change_magnitude > 0.6:
            return {"action": "resist", "confidence": change_magnitude}
        elif status_quo_benefit > 0.8:
            return {"action": "defend_status_quo", "confidence": status_quo_benefit}
        else:
            return {"action": "conditional_acceptance", "confidence": 0.5}


class StrategicInteractionModel:
    """Main model for simulating strategic interactions between agents."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = {}
        self.network = {}
        self.simulation_history = []
        self.current_step = 0
        
        # Initialize agents
        self._initialize_agents()
        self._initialize_network()
        
    def _initialize_agents(self):
        """Initialize agents based on configuration."""
        agent_types = self.config.get('agent_types', ['stakeholder', 'decision_maker', 'influencer', 'resistor'])
        num_agents = self.config.get('num_agents', 100)
        
        for i in range(num_agents):
            agent_type = np.random.choice(agent_types)
            agent_id = f"{agent_type}_{i}"
            
            # Generate random initial state based on agent type
            initial_state = self._generate_initial_state(agent_type)
            
            self.agents[agent_id] = StrategicAgent(agent_id, agent_type, initial_state)
    
    def _generate_initial_state(self, agent_type: str) -> Dict[str, Any]:
        """Generate initial state for an agent based on its type."""
        if agent_type == "stakeholder":
            return {
                'base_influence': np.random.uniform(0.2, 0.8),
                'risk_tolerance': np.random.uniform(0.1, 0.9),
                'benefit_threshold': np.random.uniform(0.2, 0.7),
                'active': np.random.choice([True, False], p=[0.7, 0.3])
            }
        elif agent_type == "decision_maker":
            return {
                'base_influence': np.random.uniform(0.6, 1.0),
                'decision_authority': np.random.uniform(0.7, 1.0),
                'information_access': np.random.uniform(0.5, 1.0),
                'active': True
            }
        elif agent_type == "influencer":
            return {
                'base_influence': np.random.uniform(0.4, 0.9),
                'network_position': np.random.uniform(0.3, 0.8),
                'persuasion_skill': np.random.uniform(0.5, 1.0),
                'active': np.random.choice([True, False], p=[0.8, 0.2])
            }
        elif agent_type == "resistor":
            return {
                'base_influence': np.random.uniform(0.3, 0.7),
                'status_quo_benefit': np.random.uniform(0.6, 1.0),
                'resistance_strength': np.random.uniform(0.5, 1.0),
                'active': np.random.choice([True, False], p=[0.6, 0.4])
            }
        else:
            return {
                'base_influence': np.random.uniform(0.3, 0.6),
                'active': np.random.choice([True, False], p=[0.5, 0.5])
            }
    
    def _initialize_network(self):
        """Initialize agent network connections."""
        agent_ids = list(self.agents.keys())
        
        for agent_id in agent_ids:
            # Each agent connects to 3-8 other agents
            num_connections = np.random.randint(3, 9)
            connections = np.random.choice(
                [aid for aid in agent_ids if aid != agent_id],
                size=min(num_connections, len(agent_ids) - 1),
                replace=False
            )
            
            self.network[agent_id] = list(connections)
            
            # Update agent connections
            for conn_id in connections:
                self.agents[agent_id].connections.append(conn_id)
    
    def step(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one simulation step."""
        self.current_step += 1
        step_results = {
            'step': self.current_step,
            'agent_decisions': {},
            'network_effects': {},
            'emergent_metrics': {}
        }
        
        # Collect all agent decisions
        for agent_id, agent in self.agents.items():
            if agent.state.get('active', False):
                decision = agent.make_decision(context)
                step_results['agent_decisions'][agent_id] = decision
                
                # Update agent state based on decision
                self._update_agent_state(agent, decision, context)
        
        # Calculate network effects
        step_results['network_effects'] = self._calculate_network_effects()
        
        # Calculate emergent metrics
        step_results['emergent_metrics'] = self._calculate_emergent_metrics()
        
        # Record step in history
        self.simulation_history.append(step_results)
        
        return step_results
    
    def _update_agent_state(self, agent: StrategicAgent, decision: Dict[str, Any], context: Dict[str, Any]):
        """Update agent state based on decision and context."""
        action = decision.get('action', 'neutral')
        confidence = decision.get('confidence', 0.5)
        
        # Update influence based on action success
        if action in ['support', 'proceed', 'advocate']:
            agent.state['base_influence'] = min(1.0, agent.state.get('base_influence', 0.5) + 0.05)
        elif action in ['oppose', 'resist']:
            agent.state['base_influence'] = max(0.1, agent.state.get('base_influence', 0.5) - 0.02)
        
        # Update activity level
        agent.state['active'] = confidence > 0.3
    
    def _calculate_network_effects(self) -> Dict[str, Any]:
        """Calculate network-level effects and information flow."""
        total_connections = sum(len(conns) for conns in self.network.values())
        avg_connections = total_connections / len(self.agents) if self.agents else 0
        
        # Calculate network density
        max_possible_connections = len(self.agents) * (len(self.agents) - 1)
        network_density = total_connections / max_possible_connections if max_possible_connections > 0 else 0
        
        # Find key influencers (agents with most connections)
        connection_counts = {aid: len(conns) for aid, conns in self.network.items()}
        top_influencers = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_connections': total_connections,
            'avg_connections': avg_connections,
            'network_density': network_density,
            'top_influencers': top_influencers
        }
    
    def _calculate_emergent_metrics(self) -> Dict[str, Any]:
        """Calculate emergent metrics from agent interactions."""
        active_agents = [a for a in self.agents.values() if a.state.get('active', False)]
        
        if not active_agents:
            return {
                'consensus': 0.0,
                'conflict': 0.0,
                'efficiency': 0.0,
                'adaptation_rate': 0.0
            }
        
        # Calculate consensus (agreement among active agents)
        decisions = [a.history[-1] if a.history else {'action': 'neutral'} for a in active_agents]
        action_counts = {}
        for decision in decisions:
            action = decision.get('action', 'neutral')
            action_counts[action] = action_counts.get(action, 0) + 1
        
        most_common_action = max(action_counts.items(), key=lambda x: x[1])[0]
        consensus = action_counts[most_common_action] / len(active_agents)
        
        # Calculate conflict (diversity of actions)
        conflict = 1 - consensus
        
        # Calculate efficiency (proportion of decisive actions)
        decisive_actions = sum(1 for d in decisions if d.get('action') not in ['neutral', 'maintain_position'])
        efficiency = decisive_actions / len(decisions) if decisions else 0
        
        # Calculate adaptation rate (agents changing their state)
        adaptation_rate = sum(1 for a in active_agents if len(a.history) > 1 and a.history[-1] != a.history[-2]) / len(active_agents)
        
        return {
            'consensus': consensus,
            'conflict': conflict,
            'efficiency': efficiency,
            'adaptation_rate': adaptation_rate
        }
    
    def run_simulation(self, steps: int, context_evolution: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the complete simulation for specified number of steps."""
        if context_evolution is None:
            context_evolution = [{}] * steps
        
        for step in range(steps):
            context = context_evolution[step] if step < len(context_evolution) else {}
            self.step(context)
        
        return {
            'final_state': self._get_final_state(),
            'simulation_history': self.simulation_history,
            'summary_metrics': self._calculate_summary_metrics()
        }
    
    def _get_final_state(self) -> Dict[str, Any]:
        """Get the final state of all agents."""
        return {
            agent_id: {
                'agent_type': agent.agent_type,
                'final_state': agent.state,
                'total_decisions': len(agent.history)
            }
            for agent_id, agent in self.agents.items()
        }
    
    def _calculate_summary_metrics(self) -> Dict[str, Any]:
        """Calculate summary metrics across the entire simulation."""
        if not self.simulation_history:
            return {}
        
        # Extract metrics over time
        consensus_over_time = [step['emergent_metrics']['consensus'] for step in self.simulation_history]
        conflict_over_time = [step['emergent_metrics']['conflict'] for step in self.simulation_history]
        efficiency_over_time = [step['emergent_metrics']['efficiency'] for step in self.simulation_history]
        
        return {
            'avg_consensus': np.mean(consensus_over_time),
            'avg_conflict': np.mean(conflict_over_time),
            'avg_efficiency': np.mean(efficiency_over_time),
            'consensus_trend': np.polyfit(range(len(consensus_over_time)), consensus_over_time, 1)[0],
            'conflict_trend': np.polyfit(range(len(conflict_over_time)), conflict_over_time, 1)[0],
            'efficiency_trend': np.polyfit(range(len(efficiency_over_time)), efficiency_over_time, 1)[0],
            'total_steps': len(self.simulation_history)
        }


def create_strategic_model(config: Dict[str, Any]) -> StrategicInteractionModel:
    """Factory function to create a strategic interaction model."""
    return StrategicInteractionModel(config)


def run_strategic_simulation(config: Dict[str, Any], steps: int = 100) -> Dict[str, Any]:
    """Convenience function to run a strategic simulation."""
    model = create_strategic_model(config)
    return model.run_simulation(steps) 