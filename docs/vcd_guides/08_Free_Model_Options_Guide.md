# Free Model Options - Complete How-To Guide

**Component**: Free LLM Model Options Manager  
**Version**: 1.0  
**Created**: 2025-11-19  
**Last Updated**: 2025-11-19 06:42:00 EST  
**File**: `Three_PointO_ArchE/free_model_options.py`

## Overview

The Free Model Options system provides a unified interface for selecting and managing free LLM model providers including Groq, Ollama, HuggingFace, and Together AI. It helps optimize model selection based on quality, speed, and cost requirements.

## Prerequisites

- Python 3.8+
- Optional: Provider API keys
- Optional: Ollama installed locally

## Installation

```bash
# No additional installation required
python3 -c "from Three_PointO_ArchE.free_model_options import FreeModelOptions; print('✅ Available')"

# Optional: Install provider SDKs
pip install groq ollama huggingface_hub together
```

## Basic Usage

### Getting Recommended Model

```python
from Three_PointO_ArchE.free_model_options import FreeModelOptions

manager = FreeModelOptions()

# Get best quality model
quality_model = manager.get_recommended_model(priority="quality")
print(f"Quality: {quality_model.model_name} ({quality_model.provider})")

# Get fastest model
speed_model = manager.get_recommended_model(priority="speed")
print(f"Speed: {speed_model.model_name} ({speed_model.provider})")

# Get best value model
value_model = manager.get_recommended_model(priority="cost")
print(f"Value: {value_model.model_name} ({value_model.provider})")
```

### Checking Provider Status

```python
# Check all providers
providers = manager.get_available_providers()

for provider in providers:
    status = "✅" if provider.available else "❌"
    print(f"{status} {provider.provider}: {'Available' if provider.available else 'Not Available'}")
    if provider.error_message:
        print(f"   Error: {provider.error_message}")
```

## Advanced Usage

### Getting Models by Provider

```python
# Get all Groq models
groq_models = manager.get_models_by_provider("groq")
for model in groq_models:
    print(f"- {model.model_name}: {model.quality} quality, {model.speed} speed")

# Get all Ollama models
ollama_models = manager.get_models_by_provider("ollama")
for model in ollama_models:
    print(f"- {model.model_name}: Requires {model.requirements.get('ram_gb', 0)}GB RAM")
```

### Comparing Models

```python
# Compare specific models
comparison = manager.compare_models([
    "llama-3.1-70b-versatile",
    "llama3:70b",
    "mixtral-8x7b-32768"
])

print(f"Fastest: {comparison['comparison']['fastest']}")
print(f"Highest Quality: {comparison['comparison']['highest_quality']}")
print(f"Best Value: {comparison['comparison']['best_value']}")
```

### Getting Provider Configuration

```python
# Get Groq configuration
groq_config = manager.get_provider_config("groq")
print("Setup Instructions:")
for instruction in groq_config.get("setup_instructions", []):
    print(f"  {instruction}")

# Get Ollama configuration
ollama_config = manager.get_provider_config("ollama")
```

## API Reference

### FreeModelOptions Class

#### `__init__()`
Initialize model options manager.

#### `get_available_providers() -> List[ProviderStatus]`
Get status of all providers.

#### `get_recommended_model(priority="quality") -> Optional[ModelInfo]`
Get recommended model based on priority.

**Parameters:**
- `priority`: "quality", "speed", or "cost"

#### `get_models_by_provider(provider) -> List[ModelInfo]`
Get all models for a provider.

#### `compare_models(model_ids) -> Dict[str, Any]`
Compare multiple models.

#### `get_provider_config(provider) -> Dict[str, Any]`
Get configuration template for provider.

## Available Providers

### Groq
- **Models**: Llama 3.1 70B, Llama 3.1 8B, Mixtral 8x7B
- **Speed**: Very Fast
- **Quality**: Excellent
- **Rate Limit**: 14,400 requests/day
- **Setup**: Requires GROQ_API_KEY

### Ollama
- **Models**: Llama 3, Llama 3 70B, Mistral
- **Speed**: Medium to Slow
- **Quality**: Good to Excellent
- **Rate Limit**: Unlimited (local)
- **Setup**: Requires local Ollama installation

### HuggingFace
- **Models**: Llama 3 8B
- **Speed**: Medium
- **Quality**: Good
- **Rate Limit**: Varies
- **Setup**: Requires HF_API_KEY

### Together AI
- **Models**: Llama 3 8B Chat
- **Speed**: Fast
- **Quality**: Good
- **Rate Limit**: $25 free credits
- **Setup**: Requires TOGETHER_API_KEY

## Configuration

### Setting Up Groq

```bash
# 1. Get API key from https://console.groq.com
# 2. Set environment variable
export GROQ_API_KEY=your_key_here

# 3. Verify
python3 -c "from Three_PointO_ArchE.free_model_options import FreeModelOptions; m = FreeModelOptions(); print(m.get_available_providers()[0])"
```

### Setting Up Ollama

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Download model
ollama pull llama3

# 3. Start Ollama
ollama serve

# 4. Verify
curl http://localhost:11434/api/tags
```

## Troubleshooting

### Provider Not Available

**Problem**: Provider shows as unavailable

**Solutions**:
1. Check API key is set: `echo $GROQ_API_KEY`
2. Verify Ollama is running: `curl http://localhost:11434/api/tags`
3. Check network connectivity
4. Review provider status messages

### No Models Found

**Problem**: `get_recommended_model()` returns None

**Solutions**:
1. Verify at least one provider is available
2. Check provider configuration
3. Review model definitions
4. Verify API keys are valid

## Best Practices

1. **Provider Selection**: Choose based on use case
2. **API Keys**: Store securely in environment variables
3. **Rate Limits**: Monitor usage to avoid limits
4. **Fallback**: Have multiple providers configured
5. **Testing**: Test models before production use

## Examples

### Example 1: Automatic Provider Selection

```python
def select_best_provider():
    manager = FreeModelOptions()
    providers = manager.get_available_providers()
    
    # Find first available provider
    for provider in providers:
        if provider.available:
            model = manager.get_recommended_model(priority="quality")
            return model.provider
    
    return None
```

### Example 2: Model Comparison Tool

```python
def compare_all_models():
    manager = FreeModelOptions()
    all_models = manager.get_all_models()
    
    print("Available Models:")
    for model in all_models:
        print(f"\n{model.model_name} ({model.provider})")
        print(f"  Quality: {model.quality}")
        print(f"  Speed: {model.speed}")
        print(f"  Cost: {model.cost}")
        print(f"  Rate Limit: {model.rate_limit}")
```

## Related Components

- **LLM Providers**: Uses provider implementations
- **VCD Configuration Management**: Stores model configurations
- **VCD Health Dashboard**: Monitors model usage

## Support

For issues:
1. Check provider status
2. Verify API keys
3. Review provider documentation
4. Test with different providers

---

**Previous Guide**: [VCD UI Component Guide](07_VCD_UI_Component_Guide.md)  
**Back to**: [VCD Guides Index](00_VCD_GUIDES_INDEX.md)
