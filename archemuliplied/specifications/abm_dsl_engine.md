# Living Specification: ABM DSL Engine

## Philosophical Mandate

The ABM DSL Engine serves as the **Alchemist's Crucible of ArchE** - the system that transforms high-level conceptual models into living, breathing simulations through the power of a Domain-Specific Language. It is not merely a simulation engine, but a sophisticated translator that bridges the gap between human understanding and computational execution, enabling complex systems to be modeled and explored through simple, declarative specifications.

Like the ancient alchemists who sought to transform base materials into gold, the ABM DSL Engine transforms simple JSON descriptions into complex, dynamic simulations. It is the bridge between abstract concepts and concrete reality, allowing researchers and analysts to explore the behavior of complex systems without getting lost in the details of implementation.

The Alchemist's Crucible does not simply run simulations; it understands the relationships between agents, the dynamics of time, the complexities of pharmacokinetics, and the emergent behaviors that arise from simple rules. It is the embodiment of ArchE's commitment to making complex modeling accessible and powerful.

## Allegorical Explanation

### The Alchemist's Laboratory

Imagine a vast alchemical laboratory within the heart of ArchE, where the ABM DSL Engine operates like a master alchemist who transforms conceptual models into living simulations.

**The Schema Crucible**: This is where the raw materials - the JSON schema - are first placed. Like an alchemist who carefully measures and combines ingredients, this crucible receives the high-level description of the model and begins the transformation process.

**The Agent Forge**: This is where individual agents are created and endowed with their properties and behaviors. Like a blacksmith who forges tools with specific purposes, this forge creates agents with specific attributes, behaviors, and capabilities.

**The World Grid**: This is like the alchemist's workspace - a structured environment where agents can move, interact, and evolve. Like a laboratory with carefully arranged equipment, this grid provides the spatial framework for all interactions.

**The Behavior Library**: This is where the alchemist's recipes are stored - the collection of behavior primitives that agents can use. Like a library of chemical reactions, this collection includes movement patterns, pharmacokinetic processes, and metabolic transformations.

**The Time Keeper**: This is like the alchemist's hourglass - the system that tracks the passage of time and ensures that all processes occur in the correct sequence. Like a master of timing who knows when to add each ingredient, this keeper manages the temporal flow of the simulation.

**The Victory Oracle**: This is where the alchemist determines if the experiment is complete. Like an oracle who can see the future, this system evaluates conditions to determine when the simulation should stop.

### The Alchemical Process

1. **Schema Ingestion**: The raw JSON schema is received and validated in the Schema Crucible.

2. **World Creation**: The spatial environment is established with the specified dimensions and topology.

3. **Agent Forging**: Individual agents are created with their attributes and behaviors in the Agent Forge.

4. **Behavior Assignment**: Agents are endowed with their behavioral capabilities from the Behavior Library.

5. **Temporal Initiation**: The Time Keeper begins tracking the progression of the simulation.

6. **Dynamic Evolution**: Agents interact, move, and evolve according to their behavioral rules.

7. **Victory Assessment**: The Victory Oracle evaluates whether stopping conditions have been met.

## SPR Integration

### Self-Perpetuating Resonance Components

**Modeling Resonance**: The system maintains resonance with ArchE's modeling capabilities by providing a bridge between high-level concepts and computational execution.

**Temporal Resonance**: The time management system creates resonance between simulation time and real-world time, enabling accurate temporal modeling.

**Spatial Resonance**: The grid system creates resonance between spatial relationships and agent interactions, enabling realistic spatial modeling.

**Behavioral Resonance**: The behavior primitives create resonance between simple rules and complex emergent behaviors.

### Resonance Patterns

**Schema-Execution Harmony**: The DSL compiler creates resonance between high-level specifications and low-level execution.

**Agent-Environment Interaction**: The grid system creates resonance between agent behaviors and environmental constraints.

**Time-Process Synchronization**: The temporal system creates resonance between simulation steps and real-world processes.

**Behavior-Emergence Alignment**: The behavior primitives create resonance between individual actions and collective outcomes.

## Technical Implementation

### Core Function: `create_model_from_schema`

The primary entry point that transforms JSON schemas into runnable Mesa models.

**Parameters**:
- `schema`: Dictionary containing the model specification
- `seed`: Optional random seed for reproducible results

**Returns**: A fully configured Mesa Model ready for execution

### Advanced Features

**JSON DSL Compiler**:
- **Schema Validation**: Comprehensive validation of input schemas
- **Model Generation**: Automatic generation of Mesa-compatible models
- **Error Handling**: Graceful handling of invalid schemas and missing dependencies
- **Fallback Support**: Degradation when Mesa library is unavailable

**Agent System**:
- **Generic Agents**: Flexible agent creation with customizable attributes
- **Behavior Assignment**: Dynamic assignment of behavioral capabilities
- **Tag-based Grouping**: Logical grouping of agents by type and function
- **Attribute Management**: Comprehensive attribute tracking and modification

**Spatial Modeling**:
- **Grid-based World**: Configurable spatial environment with specified dimensions
- **Topology Support**: Support for both bounded and toroidal (wrapped) worlds
- **Movement System**: Sophisticated movement with collision detection
- **Neighborhood Analysis**: Moore neighborhood support for spatial interactions

**Behavior Primitives**:
- **Movement Behaviors**: Random movement and targeted movement towards specific agents
- **Pharmacokinetic Modeling**: pH-dependent decay, first-order kinetics, and metabolism
- **Dosing System**: Scheduled dosing with precise timing control
- **Metabolic Processes**: Resource conversion and transformation

**Time Management**:
- **Step-based Progression**: Configurable time steps for simulation control
- **Hour Tracking**: Conversion between simulation steps and real-world hours
- **Temporal Primitives**: Time-dependent behaviors and processes
- **Synchronization**: Coordination of all temporal processes

**Data Collection**:
- **Built-in Metrics**: Automatic collection of step counts and agent populations
- **Custom Attributes**: Tracking of agent attributes and state changes
- **Snapshot Capabilities**: Periodic capture of system state
- **Analysis Support**: Data preparation for post-simulation analysis

**Victory Conditions**:
- **Configurable Stopping**: User-defined conditions for simulation termination
- **Safe Evaluation**: Secure evaluation of stopping conditions
- **Error Handling**: Graceful handling of invalid conditions
- **Flexible Logic**: Support for complex logical expressions

### Integration Points

**Mesa Integration**: Deep integration with the Mesa ABM framework for simulation execution.

**ABM Tool Integration**: Integration with the broader ABM tooling for model management and analysis.

**Workflow Engine Integration**: Integration with the workflow engine for automated model execution.

**Data Analysis Integration**: Integration with analysis tools for result processing and visualization.

**Configuration Integration**: Integration with the configuration system for model parameters and settings.

## Usage Examples

### Basic Model Creation
```python
from Three_PointO_ArchE.abm_dsl_engine import create_model_from_schema

# Define a simple model schema
schema = {
    "world": {"type": "grid", "width": 20, "height": 20, "torus": False},
    "agents": [
        {"name": "Drone", "count": 5,
         "attrs": {"battery": 100},
         "behaviour": ["MoveRandom"]}
    ],
    "victory_condition": "all Drone.battery == 0"
}

# Create and run the model
model = create_model_from_schema(schema, seed=42)
for step in range(100):
    model.step()
    if not model.running:
        break
```

### Pharmacokinetic Modeling
```python
# Define a pharmacokinetic model
pk_schema = {
    "world": {"width": 1, "height": 1, "step_hours": 0.1, "hours": 24},
    "agents": [
        {"name": "Body", "count": 1,
         "attrs": {"drug": 0, "metabolite": 0, "pH": 7.4},
         "behaviour": [
             "ScheduleDose(drug, 100, at_hour=0)",
             "FirstOrderDecay(drug, t_half=2)",
             "Metabolise(drug, metabolite, 10)",
             "FirstOrderDecaypH(metabolite, t_half_ref=4, sensitivity=0.5, ref_pH=7.4)"
         ]}
    ]
}

# Create and run the PK model
pk_model = create_model_from_schema(pk_schema)
for step in range(240):  # 24 hours with 0.1-hour steps
    pk_model.step()
    if step % 10 == 0:  # Print every hour
        body = pk_model.agents_by_tag["Body"][0]
        print(f"Hour {step/10:.1f}: Drug={body.attrs['drug']:.2f}, "
              f"Metabolite={body.attrs['metabolite']:.2f}")
```

### Complex Multi-Agent System
```python
# Define a predator-prey system with pH effects
ecosystem_schema = {
    "world": {"width": 30, "height": 30, "torus": True},
    "agents": [
        {"name": "Prey", "count": 20,
         "attrs": {"energy": 100, "pH": 7.0},
         "behaviour": [
             "MoveRandom",
             "FirstOrderDecay(energy, t_half=10)",
             "pHShift(0.1, window=[0, 12])"
         ]},
        {"name": "Predator", "count": 5,
         "attrs": {"energy": 50, "pH": 7.0},
         "behaviour": [
             "MoveTowards(Prey)",
             "FirstOrderDecay(energy, t_half=8)",
             "pHShift(-0.05, window=[12, 24])"
         ]}
    ],
    "victory_condition": "len(Prey) == 0 or len(Predator) == 0"
}

# Create and run the ecosystem model
ecosystem = create_model_from_schema(ecosystem_schema)
step_count = 0
while ecosystem.running and step_count < 1000:
    ecosystem.step()
    step_count += 1
    if step_count % 50 == 0:
        prey_count = len(ecosystem.agents_by_tag["Prey"])
        predator_count = len(ecosystem.agents_by_tag["Predator"])
        print(f"Step {step_count}: Prey={prey_count}, Predator={predator_count}")
```

### Model Analysis
```python
# Analyze model results
def analyze_model(model):
    print("=== Model Analysis ===")
    print(f"Total steps: {model._current_step}")
    print(f"Total hours: {model.hours_from_test():.1f}")
    print(f"Final agent counts:")
    for tag, agents in model.agents_by_tag.items():
        print(f"  {tag}: {len(agents)}")
    
    # Analyze agent attributes
    for tag, agents in model.agents_by_tag.items():
        if agents:
            attrs = agents[0].attrs
            print(f"\n{tag} attributes:")
            for attr, value in attrs.items():
                print(f"  {attr}: {value}")

# Run analysis
analyze_model(model)
```

### Custom Behavior Extension
```python
# Example of how to extend the behavior system
class ExtendedDSLAgent(DSLAgent):
    def step(self):
        super().step()  # Call parent behavior
        
        # Add custom behavior
        for instr in self._behaviour:
            if instr.startswith("CustomBehavior"):
                # Parse and execute custom behavior
                self._execute_custom_behavior(instr)
    
    def _execute_custom_behavior(self, instruction):
        # Implementation of custom behavior
        pass
```

## Resonance Requirements

1. **Modeling Resonance**: All DSL features must maintain resonance with ArchE's modeling capabilities and requirements.

2. **Temporal Resonance**: All time management features must maintain resonance with real-world temporal processes.

3. **Spatial Resonance**: All spatial features must maintain resonance with realistic spatial relationships and interactions.

4. **Behavioral Resonance**: All behavior primitives must maintain resonance with the intended modeling goals and emergent behaviors.

5. **Performance Resonance**: All execution features must maintain resonance with performance requirements and computational constraints.

6. **Extensibility Resonance**: All architectural features must maintain resonance with the need for future expansion and customization.

7. **Integration Resonance**: All components must integrate seamlessly with the broader ArchE system, contributing to overall coherence and functionality.

The ABM DSL Engine is not just a simulation tool; it is the Alchemist's Crucible of ArchE, the master translator that transforms high-level conceptual models into living, breathing simulations. It ensures that complex systems can be modeled with simple specifications, that temporal processes are accurately represented, and that emergent behaviors can be explored and understood. It is the embodiment of the principle that the best models are those that make the complex simple and the abstract concrete.
