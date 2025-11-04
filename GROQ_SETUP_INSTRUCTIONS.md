# Groq Setup Instructions for ArchE

## ✅ Installation Complete

**Groq SDK**: v0.33.0 ✅ Installed  
**Groq Provider**: ✅ Created at `Three_PointO_ArchE/llm_providers/groq_provider.py`

---

## 🔑 Get Your Groq API Key

1. Go to: https://console.groq.com/keys
2. Sign up or log in
3. Create a new API key
4. Copy the key

---

## ⚙️ Configuration

### Step 1: Add API Key to .env

Open `/mnt/3626C55326C514B1/Happier/.env` and add this line:

```bash
GROQ_API_KEY=your_actual_groq_api_key_here
```

Add it near the other API keys section (around line 17).

### Step 2: Verify Setup

```bash
cd /mnt/3626C55326C514B1/Happier
source arche_env/bin/activate
python3 Three_PointO_ArchE/llm_providers/groq_provider.py
```

You should see:
```
✅ Groq provider initialized
Model: llama-3.3-70b-versatile
```

---

## 🚀 Usage

### Quick Generation

```python
from Three_PointO_ArchE.llm_providers.groq_provider import GroqProvider

# Initialize
groq = GroqProvider(model="llama-3.3-70b-versatile")

# Generate
result = groq.generate(
    prompt="Explain quantum computing in simple terms",
    max_tokens=500,
    temperature=0.7
)

print(result['text'])
```

### With System Prompt

```python
result = groq.generate(
    prompt="What are the 3 laws of robotics?",
    system_prompt="You are Isaac Asimov. Answer concisely.",
    max_tokens=300
)
```

### Multi-Turn Chat

```python
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "What is ArchE?"},
    {"role": "assistant", "content": "ArchE is an Autopoietic Cognitive Entity..."},
    {"role": "user", "content": "How does it use Groq?"}
]

result = groq.chat(messages=messages, max_tokens=500)
```

---

## 📊 Available Models

| Model | Context Window | Speed | Best For |
|-------|---------------|-------|----------|
| **llama-3.3-70b-versatile** ⭐ | 128K | Very Fast | General use, reasoning, coding |
| llama-3.1-70b-versatile | 131K | Very Fast | Complex reasoning |
| llama-3.1-8b-instant | 131K | Blazing Fast | Quick responses |
| mixtral-8x7b-32768 | 32K | Fast | Multilingual tasks |
| gemma-7b-it | 8K | Fast | Compact tasks |
| gemma2-9b-it | 8K | Fast | Improved Gemma |

⭐ **Recommended default**: `llama-3.3-70b-versatile`

---

## 🎯 Integration with ArchE

### Use in Workflows

Groq can be used in any ArchE workflow that uses `generate_text_llm` action:

```json
{
  "action_type": "generate_text_llm",
  "inputs": {
    "prompt": "{{query}}",
    "model": "llama-3.3-70b-versatile",
    "provider": "groq",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

### Use in Novel Skill Combinations

Groq's speed makes it perfect for:
- **Multi-Agent Collaborative Analysis** (Routine #3) - Fast agent responses
- **Emergent Domain Auto-Detection** (Routine #7) - Quick pattern recognition
- **Temporal analysis requiring multiple iterations** - Reduced latency

### Benefits for ArchE

1. **Speed**: 500+ tokens/second (10-20x faster than typical APIs)
2. **Cost-Effective**: Lower cost per token than many alternatives
3. **IAR Compatible**: Full IAR reflection support built-in
4. **Llama 3.3 70B**: State-of-the-art reasoning capabilities

---

## 🔧 Advanced Usage

### Change Model

```python
groq = GroqProvider(model="llama-3.1-8b-instant")  # For speed
groq = GroqProvider(model="mixtral-8x7b-32768")    # For multilingual
```

### List Available Models

```python
models = groq.list_models()
for model in models:
    info = groq.get_model_info(model)
    print(f"{model}: {info['name']}")
```

### Streaming (Future Enhancement)

```python
# TODO: Add streaming support for real-time generation
# Will be useful for long-form content and monitoring
```

---

## 🧪 Test Commands

### Basic Test
```bash
cd /mnt/3626C55326C514B1/Happier
source arche_env/bin/activate
python3 Three_PointO_ArchE/llm_providers/groq_provider.py
```

### Interactive Test
```bash
source arche_env/bin/activate
python3 << 'PYTHON_EOF'
from Three_PointO_ArchE.llm_providers.groq_provider import GroqProvider

groq = GroqProvider()
if groq.available:
    result = groq.generate("Write a haiku about AI", max_tokens=100)
    if result['status'] == 'success':
        print("✅ Groq is working!")
        print(f"\n{result['text']}")
        print(f"\nTokens used: {result['usage']['total_tokens']}")
    else:
        print(f"❌ Error: {result['message']}")
else:
    print("❌ Set GROQ_API_KEY in .env file first")
PYTHON_EOF
```

---

## 🔐 Security Notes

- Never commit .env file to git (already in .gitignore)
- Keep GROQ_API_KEY secret
- Rotate keys periodically
- Use environment-specific keys for dev/prod

---

## 📝 Integration Checklist

- [x] Install Groq SDK (v0.33.0)
- [x] Create GroqProvider class
- [x] Add IAR compliance
- [ ] Add GROQ_API_KEY to .env
- [ ] Test provider with sample query
- [ ] Update action_registry to support Groq
- [ ] Update workflow engine to route to Groq
- [ ] Add Groq to Novel Skill Combinations documentation

---

## 🆘 Troubleshooting

### "Groq provider not available"
→ Check that GROQ_API_KEY is set in .env and not the placeholder value

### "ImportError: No module named 'groq'"
→ Run: `source arche_env/bin/activate && pip install groq`

### "API key invalid"
→ Verify your key at https://console.groq.com/keys

### "Rate limit exceeded"
→ Groq has generous rate limits, but check your usage at console.groq.com

---

## 🔗 Resources

- **Groq Console**: https://console.groq.com/
- **Groq Docs**: https://console.groq.com/docs/quickstart
- **API Reference**: https://console.groq.com/docs/api-reference
- **Rate Limits**: https://console.groq.com/docs/rate-limits
- **Models**: https://console.groq.com/docs/models

---

**Status**: ✅ Groq provider ready to use once API key is added to .env!



