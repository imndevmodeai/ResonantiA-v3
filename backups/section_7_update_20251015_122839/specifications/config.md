# Living Specification: Configuration System

## Philosophical Mandate

The Configuration System serves as the **Foundation Stone of ArchE** - the bedrock upon which all other components rest, providing the essential parameters, paths, and settings that enable the entire system to function harmoniously. It is not merely a collection of variables, but a sophisticated foundation that understands the relationships between different components and ensures they work together in perfect resonance.

Like the ancient architects who laid the foundation stones of great temples, the Configuration System establishes the fundamental structure that supports all of ArchE's capabilities. It is the keeper of paths, the guardian of settings, and the orchestrator of connections between different components. Without this foundation, the entire system would crumble into chaos.

The Foundation Stone does not simply store values; it understands the relationships between different components, manages the complexity of multiple providers, and ensures that all paths lead to the right destinations. It is the embodiment of ArchE's commitment to systematic organization and harmonious operation.

## Allegorical Explanation

### The Foundation Temple

Imagine a vast temple complex within the heart of ArchE, where the Configuration System operates like the master architect who designed and maintains the entire structure.

**The Central Pillar**: This is the main configuration object that holds all the essential settings. Like the central pillar of a temple that supports the entire structure, this pillar contains the core configuration that all other components depend upon.

**The Path Network**: This is like the network of corridors and passageways that connect all parts of the temple. Each path is carefully mapped and resolved to ensure that every component can find its way to the resources it needs. Like a master architect who knows every corner of the temple, the system maintains absolute knowledge of where everything is located.

**The Provider Chambers**: These are specialized rooms dedicated to different service providers. Like a temple that might have chambers for different deities, the system has dedicated spaces for OpenAI, Google, and other LLM providers, each with their own models and capabilities.

**The Tool Forge**: This is where the tools of ArchE are configured and prepared. Like a blacksmith's forge where different tools are crafted for different purposes, this space contains the settings for ABM tools, code executors, search tools, and other capabilities.

**The Security Sanctum**: This is the most sacred space, where sensitive information like API keys and restricted topics are kept. Like the inner sanctum of a temple that only the initiated may enter, this space is protected and carefully managed.

**The System Observatory**: This is where the overall system settings are monitored and managed. Like the observatory in a temple where the priests track the movements of the stars, this space monitors logging levels, system states, and operational parameters.

### The Foundation Process

1. **Initialization**: When ArchE starts, the Foundation Stone is laid, establishing all the essential paths and settings.

2. **Path Resolution**: All paths are resolved to their absolute locations, ensuring that every component knows exactly where to find its resources.

3. **Provider Configuration**: Each LLM provider is configured with its models, settings, and capabilities.

4. **Tool Preparation**: All tools are configured with their default settings and operational parameters.

5. **Security Establishment**: API keys and security settings are established and protected.

6. **System Harmonization**: All components are brought into resonance with the configuration.

## SPR Integration

### Self-Perpetuating Resonance Components

**Structural Resonance**: The system maintains resonance with ArchE's architectural framework through consistent path management and component organization.

**Provider Resonance**: The multi-provider configuration creates resonance between different LLM services, ensuring optimal performance and reliability.

**Security Resonance**: The security features maintain resonance with ArchE's ethical and safety principles.

**Operational Resonance**: The system settings maintain resonance with ArchE's operational requirements and performance goals.

### Resonance Patterns

**Path-Component Harmony**: The path network creates resonance between different components, ensuring they can find and interact with each other.

**Provider-Performance Optimization**: The provider configuration creates resonance between service capabilities and system performance.

**Security-Operation Balance**: The security settings create resonance between protection and functionality.

**Tool-Capability Alignment**: The tool configuration creates resonance between available tools and system capabilities.

## Technical Implementation

### Core Class: `Config`

The primary class that serves as the foundation for all ArchE configuration.

**Initialization**: Creates a comprehensive configuration object with all necessary settings and paths.

### Advanced Features

**ABM Configuration**:
- **Default Settings**: Agent count, step count, grid size, and model types
- **Performance Limits**: Maximum agents, steps, and parallel processing settings
- **Visualization Options**: Plot formats, save settings, and display preferences
- **Output Management**: Output directory, logging levels, and file management

**LLM Configuration**:
- **Multi-Provider Support**: OpenAI and Google provider configurations
- **Model Management**: Comprehensive model lists for each provider
- **Default Settings**: Temperature, max tokens, and provider preferences
- **Backup Systems**: Fallback models and provider redundancy

**System Configuration**:
- **Logging Management**: Log levels and file management
- **Security Features**: Restricted topics and keyholder override capabilities
- **Operational Settings**: System-wide parameters and preferences

**Path Management**:
- **Absolute Path Resolution**: All paths resolved to absolute locations
- **Component Organization**: Logical organization of all ArchE components
- **Resource Location**: Comprehensive mapping of all system resources
- **Output Management**: Structured output directories for different types of content
- **Architectural Note**: The `workflows` path points to the root of the core workflow directory. Specific, nested file paths within this structure are managed exclusively by the `WorkflowOrchestrator` via its `registry.json` map, decoupling the rest of the system from the physical file layout.

**Tool Configuration**:
- **ABM Tools**: Agent-based modeling settings and parameters
- **Code Execution**: Timeout settings and execution parameters
- **Search Tools**: Result count and search parameters
- **Prediction Tools**: Model types and forecast horizons
- **Causal Analysis**: Method selection and analysis parameters
- **CFP Tools**: Evolution models and time horizons

**API Key Management**:
- **Secure Storage**: Protected storage of sensitive API keys
- **Provider Association**: Keys associated with specific providers
- **Access Control**: Controlled access to sensitive configuration data

### Integration Points

**Component Integration**: All ArchE components integrate with the configuration system for their settings and paths.

**Provider Integration**: LLM providers integrate with the configuration for their models and settings.

**Tool Integration**: All tools integrate with the configuration for their operational parameters.

**Security Integration**: Security systems integrate with the configuration for access control and restrictions.

**Path Integration**: All components use the configuration for path resolution and resource location.

## Usage Examples

### Basic Configuration Access
```python
from Three_PointO_ArchE.config import get_config

# Get the global configuration
config = get_config()

# Access ABM settings
print(f"Default agents: {config.abm_default_agents}")
print(f"Default steps: {config.abm_default_steps}")
print(f"Grid size: {config.abm_default_grid_size}")

# Access LLM settings
print(f"Default provider: {config.llm.default_provider}")
print(f"Default model: {config.llm.default_model}")
print(f"Temperature: {config.llm.temperature}")
```

### Path Management
```python
# Access system paths
print(f"Project root: {config.paths.project_root}")
print(f"Arche root: {config.paths.arche_root}")
print(f"Knowledge graph: {config.paths.knowledge_graph}")
print(f"Workflows: {config.paths.workflows}")

# Access output paths
print(f"Output models: {config.paths.output_models}")
print(f"Output visualizations: {config.paths.output_visualizations}")
print(f"Output reports: {config.paths.output_reports}")
```

### Provider Configuration
```python
# Access LLM provider settings
openai_config = config.LLM_PROVIDERS['openai']
google_config = config.LLM_PROVIDERS['google']

print(f"OpenAI models: {openai_config['models']}")
print(f"Google default model: {google_config['default_model']}")
print(f"Google backup model: {google_config['backup_model']}")

# Access tool settings
print(f"Code executor timeout: {config.tools.code_executor_timeout}")
print(f"Search result count: {config.tools.search_result_count}")
print(f"Prediction model: {config.tools.prediction_default_model}")
```

### System Settings
```python
# Access system configuration
print(f"Log level: {config.system.log_level}")
print(f"Keyholder override: {config.system.keyholder_override_active}")
print(f"Restricted topics: {config.system.restricted_topics}")

# Access API key status
print(f"OpenAI API key: {'Set' if config.api_keys.openai_api_key else 'Not set'}")
print(f"Google API key: {'Set' if config.api_keys.google_api_key else 'Not set'}")
```

### Advanced Configuration
```python
# Access comprehensive provider information
for provider_name, provider_config in config.LLM_PROVIDERS.items():
    print(f"\n{provider_name.upper()} Configuration:")
    print(f"  Models: {provider_config['models']}")
    print(f"  Default model: {provider_config['default_model']}")
    if 'backup_model' in provider_config:
        print(f"  Backup model: {provider_config['backup_model']}")

# Access all available paths
print("\nAvailable Paths:")
for attr_name in dir(config.paths):
    if not attr_name.startswith('_'):
        path_value = getattr(config.paths, attr_name)
        print(f"  {attr_name}: {path_value}")
```

## Resonance Requirements

1. **Structural Resonance**: All configuration settings must maintain resonance with ArchE's architectural framework and component relationships.

2. **Provider Resonance**: All provider configurations must maintain resonance with their respective service capabilities and limitations.

3. **Security Resonance**: All security settings must maintain resonance with ArchE's ethical principles and safety requirements.

4. **Path Resonance**: All path configurations must maintain resonance with the actual file system structure and component locations. The `WorkflowOrchestrator` is the primary guardian of this resonance for `Process Blueprints`.

5. **Tool Resonance**: All tool configurations must maintain resonance with their operational requirements and performance characteristics.

6. **Operational Resonance**: All system settings must maintain resonance with ArchE's operational requirements and performance goals.

7. **Integration Resonance**: All configuration components must integrate seamlessly with the broader ArchE system, contributing to overall coherence and functionality.

The Configuration System is not just a collection of settings; it is the Foundation Stone of ArchE, the master architect that establishes the fundamental structure supporting all system capabilities. It ensures that every component has the right settings, every path leads to the right destination, and every provider is properly configured for optimal performance. It is the embodiment of the principle that a strong foundation is essential for building great systems.
