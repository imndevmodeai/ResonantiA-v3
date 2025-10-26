# The Alchemist's Crucible: A Chronicle of the ABM DSL Engine

## Canonical Chronicle Piece: The Worlds in a Bottle

In the ResonantiA Saga, after ArchE had mastered analysis of the past (`CausalInference`) and the future (`PredictiveModeling`), a new frontier emerged: the *possible*. How could the system explore complex "what-if" scenarios, where thousands of independent actors interact in unpredictable ways? This chronicle tells of the forging of the **Alchemist's Crucible**, the `Agent Based ModelinG` Domain-Specific Language (DSL) Engine. It is the story of how ArchE was given the power to create "worlds in a bottle"—_in silico_ laboratories where it could simulate the emergent chaos of complex systems, from cellular biology to market economies.

## Scholarly Introduction: Conceptual Foundations and Implementability

This specification details a Domain-Specific Language (DSL) for Agent-Based Modeling (ABM), designed to be parsed into executable simulations, primarily using the Mesa framework. The DSL's grammar, defined implicitly by the JSON schema in the technical sections, allows users to declare agent populations, environmental grids, behavioral primitives, and victory conditions in a human-readable format. This approach dramatically lowers the barrier to entry for complex systems modeling. The specification is highly implementable; the provided JSON examples can be directly used as test cases for a parser that generates Python code for the Mesa library.

## The Story of the Alchemist's Crucible: A Narrative of Emergence

Imagine ArchE as a brilliant biologist studying a new disease. She can analyze data from past outbreaks, but she wants to know: "What would happen if we introduced a new vaccine that was 70% effective and required a booster every 6 months?"
- **Without the Crucible:** This is almost impossible to answer. The interactions are too complex.
- **With the Crucible (`ABM DSL Engine`):**
    1.  **Writing the Recipe (`JSON Schema`):** The biologist doesn't write thousands of lines of code. Instead, she writes a simple, declarative recipe in the DSL.
        - `world`: "Create a population grid of 10,000 squares, representing a city."
        - `agents`: "Create 1,000 'Human' agents. Give them attributes like 'age' and 'health'. Give them behaviors like 'MoveRandomly' and 'InteractWithNeighbors'."
        - `behaviors`: "Define a 'TransmitDisease' behavior. Define a 'Vaccinate' behavior that changes an agent's 'health' status."
        - `victory_condition`: "Stop the simulation when 'infected_count' is zero."
    2.  **Mixing the Elixir (`create_model_from_schema`):** The biologist hands this recipe to the Alchemist's Crucible. The engine reads the simple recipe and, like magic, transmutes it into a fully formed, complex simulation—a living "world in a bottle."
    3.  **Observing the Reaction (`Simulation`):** ArchE runs the simulation. It watches as the virtual disease spreads, as vaccinated agents show resistance, and as herd immunity begins to emerge. It can run the simulation dozens of times, tweaking the vaccine's effectiveness or the booster schedule.
The Crucible allows ArchE to explore the unpredictable, *emergent* consequences of a policy *before* implementing it in the real world. It turns abstract ideas into living, testable realities.

## Real-World Analogy: SimCity for Business Strategy

A traditional spreadsheet for a business might show revenue and costs. An Agent-Based Model is like turning that spreadsheet into a playable game of *SimCity*.
- **The DSL Recipe:** Instead of cells and formulas, you define the actors:
    - 10,000 `Customer` agents with attributes like `brand_loyalty` and `budget`.
    - 3 `Competitor` agents with `pricing_strategy` behaviors.
    - 50 `Product` agents with `features` and `quality`.
- **The "What-If" Game:** You can now play the game.
    - "What happens if we lower our price by 10%?" -> Run the simulation and watch how many `Customer` agents switch from `Competitor` agents.
    - "What happens if a `Competitor` introduces a new feature?" -> Run the simulation and see how many of your `Customer` agents you lose.
The ABM DSL Engine allows strategists to move beyond static analysis and explore the dynamic, emergent, and often surprising results of their decisions in a complex marketplace.

# Living Specification: ABM DSL Engine

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

## How the Alchemist Forges a World: A Real-World Workflow

This workflow details the end-to-end process of using the ABM DSL Engine to create and run a simulation from a simple JSON specification.

1.  **Phase 1: The Blueprint (JSON Schema)**
    *   **Action:** A user or another ArchE process defines the world to be simulated in a JSON object.
    *   **Example (`pk_schema` from above):**
        ```json
        {
          "world": {"width": 1, "height": 1, "step_hours": 0.1, "hours": 24},
          "agents": [{
            "name": "Body", "count": 1,
            "attrs": {"drug": 0, "metabolite": 0, "pH": 7.4},
            "behaviour": [
              "ScheduleDose(drug, 100, at_hour=0)",
              "FirstOrderDecay(drug, t_half=2)",
              "Metabolise(drug, metabolite, 10)"
            ]
          }]
        }
        ```

2.  **Phase 2: The Transmutation (`create_model_from_schema`)**
    *   **Action:** A workflow task calls the `perform_abm` tool with `operation: 'create_model'`, `model_type: 'generic_dsl'`, and the `schema` from Phase 1.
    *   **Process:**
        *   The `create_model_from_schema` function is invoked internally.
        *   **Schema Validation:** It first validates the JSON against its internal rules.
        *   **World Creation:** It creates a `Mesa` model instance and a `Grid` based on the `"world"` parameters.
        *   **Agent Forging:** It iterates through the `"agents"` list. For each entry, it creates the specified `count` of `DSLAgent` instances.
        *   **Attribute & Behavior Assignment:** It assigns the initial `attrs` to each agent and attaches the list of `behaviour` strings.
    *   **Result:** A fully instantiated, in-memory `Mesa` model object is returned, ready for simulation.

3.  **Phase 3: The Observation (`run_simulation`)**
    *   **Action:** A workflow task calls `perform_abm` with `operation: 'run_simulation'`, passing in the `model` object from Phase 2 and `steps: 240`.
    *   **Process:**
        *   The `run_simulation` function loops 240 times.
        *   In each loop, it calls the model's `step()` method.
        *   The `Mesa` scheduler activates each agent's `step()` method.
        *   The agent's `step()` method iterates through its list of behavior strings (e.g., `"FirstOrderDecay(drug, t_half=2)"`).
        *   It parses each string and executes the corresponding internal function (e.g., `_behaviour_first_order_decay(...)`), which modifies the agent's `attrs` in place.
        *   The model's `datacollector` records the state of the agents at the end of each step.
    *   **Result:** The simulation runs to completion, and the function returns the model object, now containing the full history of the simulation in its `datacollector`.

4.  **Phase 4: The Analysis (`analyze_results`)**
    *   **Action:** A final workflow task calls `perform_abm` with `operation: 'analyze_results'`, passing in the simulation results.
    *   **Process:** The analysis function extracts the data from the `datacollector` into a pandas DataFrame, calculates summary statistics, and identifies key events (like convergence or oscillation).
    *   **Result:** A structured dictionary containing the analysis is returned, ready for interpretation or visualization.

## SPR Integration and Knowledge Tapestry Mapping

*   **Primary SPR**: `Agent Based ModelinG` (ABM)
*   **Sub-SPRs**:
    *   `Emergence Over TimE`: The core phenomenon that ABM is designed to study.
    *   `Complex System VisioninG`: The primary capability enabled by this tool.
*   **Tapestry Relationships**:
    *   **`is_a`**: `What-If ScenariO Analysis`, `Simulation FrameworK`
    *   **`part_of`**: The `RISE` Analytical Triad
    *   **`enables`**: `Policy TestinG`, `Strategic ForesighT`
    *   **`uses`**: `Mesa LibrarY`
    *   **`embodies`**: The principle of understanding macro behavior from micro rules.

This Living Tome ensures the ABM DSL Engine is understood not just as a code library, but as the Alchemist's Crucible—a powerful tool for transmuting simple, declarative ideas into living, complex simulations to reveal emergent truths.
