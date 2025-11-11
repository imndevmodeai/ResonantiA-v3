# Mistral AI Quick Setup Guide

**Status**: ✅ Implemented and ready to use  
**Purpose**: Alternative free tier LLM provider when Groq hits rate limits

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Package

```bash
cd /mnt/3626C55326C514B1/Happier
source arche_env/bin/activate
pip install mistralai
```

### Step 2: Get API Key

1. Go to https://console.mistral.ai
2. Sign up (free tier available)
3. Create an API key
4. Copy the key

### Step 3: Add to Environment

Add to your `.env` file:
```bash
MISTRAL_API_KEY=your_api_key_here
```

Or export it:
```bash
export MISTRAL_API_KEY=your_api_key_here
```

### Step 4: Use It!

**Option A: Environment Variable**
```bash
export ARCHE_LLM_PROVIDER=mistral
python run_analysis.sh
```

**Option B: In Code**
```python
from Three_PointO_ArchE.llm_providers import get_llm_provider

provider = get_llm_provider("mistral")
response = provider.generate("Your prompt here")
```

**Option C: In Workflows**
```json
{
  "inputs": {
    "prompt": "Your prompt here",
    "provider": "mistral",
    "model": "mistral-small-latest"
  }
}
```

---

## 📊 Available Models

- **mistral-small-latest** (Recommended for free tier)
- **mistral-medium-latest** (Better quality)
- **mistral-large-latest** (Best quality)
- **mistral-tiny** (Fastest, smallest)

---

## ✅ Verification

Test the provider:
```bash
source arche_env/bin/activate
python -c "
from Three_PointO_ArchE.llm_providers import get_llm_provider
provider = get_llm_provider('mistral')
response = provider.generate('Say hello!')
print(response)
"
```

---

## 🔄 Switching Between Providers

**Temporary (for this session)**:
```bash
export ARCHE_LLM_PROVIDER=mistral  # or groq, google, cursor
```

**Permanent (in `.env`)**:
```bash
ARCHE_LLM_PROVIDER=mistral
```

**In Code**:
```python
# Use Mistral
provider = get_llm_provider("mistral")

# Use Groq (when limits reset)
provider = get_llm_provider("groq")

# Use Google Gemini
provider = get_llm_provider("google")
```

---

## 🎯 When to Use Mistral

- ✅ Groq hits rate limits (100k tokens/day)
- ✅ Need fast inference (comparable to Groq)
- ✅ Want free tier alternative
- ✅ Testing and development

---

## 📝 Notes

- **Free Tier**: Available for testing and prototyping
- **Speed**: Fast inference (comparable to Groq)
- **Quality**: Excellent (comparable to Groq)
- **Registration**: https://console.mistral.ai
- **Documentation**: https://docs.mistral.ai

---

**Status**: ✅ Ready to use! Just install the package and set your API key.


