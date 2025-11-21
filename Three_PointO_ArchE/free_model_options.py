#!/usr/bin/env python3
"""
Free Model Options System
Unified interface for selecting and managing free LLM model providers

This module provides a centralized system for managing free LLM model options,
including Groq, Ollama, HuggingFace, and Together AI providers.

Part of ResonantiA Protocol v3.5-GP Implementation Resonance initiative.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer

logger = logging.getLogger(__name__)

class FreeModelProvider(Enum):
    """Available free model providers."""
    GROQ = "groq"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    TOGETHER = "together"

@dataclass
class ModelInfo:
    """Information about a free model."""
    provider: str
    model_name: str
    model_id: str
    cost: str  # "free" or description
    speed: str  # "fast", "medium", "slow"
    quality: str  # "excellent", "good", "fair"
    rate_limit: Optional[str] = None
    requirements: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

@dataclass
class ProviderStatus:
    """Status of a provider."""
    provider: str
    available: bool
    configured: bool
    api_key_set: bool
    models_available: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

class FreeModelOptions:
    """
    Free Model Options Manager - Unified interface for free LLM providers.
    
    Provides:
    - Provider selection and management
    - Model information and comparison
    - Automatic provider selection
    - Cost tracking and optimization
    """
    
    def __init__(self):
        """Initialize Free Model Options Manager."""
        # Define available models
        self.models = {
            "groq": [
                ModelInfo(
                    provider="groq",
                    model_name="Llama 3.1 70B Versatile",
                    model_id="llama-3.1-70b-versatile",
                    cost="free",
                    speed="fast",
                    quality="excellent",
                    rate_limit="14,400 requests/day",
                    requirements={},
                    description="Best quality free model, very fast inference"
                ),
                ModelInfo(
                    provider="groq",
                    model_name="Llama 3.1 8B Instant",
                    model_id="llama-3.1-8b-instant",
                    cost="free",
                    speed="very_fast",
                    quality="good",
                    rate_limit="14,400 requests/day",
                    requirements={},
                    description="Faster but smaller model"
                ),
                ModelInfo(
                    provider="groq",
                    model_name="Mixtral 8x7B",
                    model_id="mixtral-8x7b-32768",
                    cost="free",
                    speed="fast",
                    quality="excellent",
                    rate_limit="14,400 requests/day",
                    requirements={},
                    description="High-quality mixture of experts model"
                )
            ],
            "ollama": [
                ModelInfo(
                    provider="ollama",
                    model_name="Llama 3",
                    model_id="llama3",
                    cost="free",
                    speed="medium",
                    quality="good",
                    rate_limit="unlimited",
                    requirements={"ram_gb": 8},
                    description="Local model, requires 8GB RAM"
                ),
                ModelInfo(
                    provider="ollama",
                    model_name="Llama 3 70B",
                    model_id="llama3:70b",
                    cost="free",
                    speed="slow",
                    quality="excellent",
                    rate_limit="unlimited",
                    requirements={"ram_gb": 40, "gpu": True},
                    description="High-quality local model, requires 40GB RAM or GPU"
                ),
                ModelInfo(
                    provider="ollama",
                    model_name="Mistral",
                    model_id="mistral",
                    cost="free",
                    speed="medium",
                    quality="good",
                    rate_limit="unlimited",
                    requirements={"ram_gb": 7},
                    description="Efficient 7B parameter model"
                )
            ],
            "huggingface": [
                ModelInfo(
                    provider="huggingface",
                    model_name="Llama 3 8B",
                    model_id="meta-llama/Llama-3-8b",
                    cost="free",
                    speed="medium",
                    quality="good",
                    rate_limit="varies",
                    requirements={},
                    description="Community-hosted model, availability varies"
                )
            ],
            "together": [
                ModelInfo(
                    provider="together",
                    model_name="Llama 3 8B Chat",
                    model_id="meta-llama/Llama-3-8b-chat-hf",
                    cost="free_credits",
                    speed="fast",
                    quality="good",
                    rate_limit="$25 free credits",
                    requirements={},
                    description="Free startup credits available"
                )
            ]
        }
        
        logger.info("FreeModelOptions initialized")
    
    def get_available_providers(self) -> List[ProviderStatus]:
        """
        Get status of all available providers.
        
        Returns:
            List of ProviderStatus objects
        """
        providers = []
        
        for provider_name in ["groq", "ollama", "huggingface", "together"]:
            status = self._check_provider_status(provider_name)
            providers.append(status)
        
        return providers
    
    def _check_provider_status(self, provider: str) -> ProviderStatus:
        """Check status of a specific provider."""
        api_key_set = False
        configured = False
        available = False
        models_available = []
        error_message = None
        
        if provider == "groq":
            api_key_set = bool(os.getenv("GROQ_API_KEY"))
            configured = api_key_set
            if api_key_set:
                try:
                    # Would check if provider is actually available
                    available = True
                    models_available = [m.model_id for m in self.models.get("groq", [])]
                except Exception as e:
                    error_message = str(e)
        
        elif provider == "ollama":
            # Check if Ollama is running locally
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    available = True
                    configured = True
                    # Get available models from Ollama
                    models_data = response.json()
                    models_available = [m.get("name", "") for m in models_data.get("models", [])]
            except Exception:
                available = False
                configured = False
                error_message = "Ollama not running or not accessible"
        
        elif provider == "huggingface":
            api_key_set = bool(os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY"))
            configured = api_key_set
            if api_key_set:
                available = True
                models_available = [m.model_id for m in self.models.get("huggingface", [])]
        
        elif provider == "together":
            api_key_set = bool(os.getenv("TOGETHER_API_KEY"))
            configured = api_key_set
            if api_key_set:
                available = True
                models_available = [m.model_id for m in self.models.get("together", [])]
        
        return ProviderStatus(
            provider=provider,
            available=available,
            configured=configured,
            api_key_set=api_key_set,
            models_available=models_available,
            error_message=error_message
        )
    
    def get_recommended_model(
        self,
        priority: str = "quality"  # "quality", "speed", "cost"
    ) -> Optional[ModelInfo]:
        """
        Get recommended free model based on priority.
        
        Args:
            priority: "quality", "speed", or "cost"
            
        Returns:
            Recommended ModelInfo or None
        """
        available_providers = self.get_available_providers()
        available_provider_names = [p.provider for p in available_providers if p.available]
        
        if not available_provider_names:
            return None
        
        # Get all available models
        all_models = []
        for provider_name in available_provider_names:
            all_models.extend(self.models.get(provider_name, []))
        
        if not all_models:
            return None
        
        # Select based on priority
        if priority == "quality":
            # Prefer excellent quality models
            excellent_models = [m for m in all_models if m.quality == "excellent"]
            if excellent_models:
                # Prefer faster excellent models
                return max(excellent_models, key=lambda m: {"very_fast": 3, "fast": 2, "medium": 1, "slow": 0}.get(m.speed, 0))
            return max(all_models, key=lambda m: {"excellent": 3, "good": 2, "fair": 1}.get(m.quality, 0))
        
        elif priority == "speed":
            # Prefer fastest models
            return max(all_models, key=lambda m: {"very_fast": 3, "fast": 2, "medium": 1, "slow": 0}.get(m.speed, 0))
        
        elif priority == "cost":
            # All are free, but prefer unlimited rate limits
            unlimited = [m for m in all_models if m.rate_limit == "unlimited"]
            if unlimited:
                return max(unlimited, key=lambda m: {"excellent": 3, "good": 2, "fair": 1}.get(m.quality, 0))
            return all_models[0]  # Return first available
        
        return all_models[0]
    
    def get_models_by_provider(self, provider: str) -> List[ModelInfo]:
        """
        Get all models for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of ModelInfo objects
        """
        return self.models.get(provider, [])
    
    def compare_models(self, model_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple models.
        
        Args:
            model_ids: List of model IDs to compare
            
        Returns:
            Comparison dictionary
        """
        models_to_compare = []
        
        for provider, models in self.models.items():
            for model in models:
                if model.model_id in model_ids:
                    models_to_compare.append(model)
        
        comparison = {
            "models": [asdict(m) for m in models_to_compare],
            "comparison": {
                "fastest": max(models_to_compare, key=lambda m: {"very_fast": 3, "fast": 2, "medium": 1, "slow": 0}.get(m.speed, 0)).model_id if models_to_compare else None,
                "highest_quality": max(models_to_compare, key=lambda m: {"excellent": 3, "good": 2, "fair": 1}.get(m.quality, 0)).model_id if models_to_compare else None,
                "best_value": models_to_compare[0].model_id if models_to_compare else None
            }
        }
        
        return comparison
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        Get configuration template for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Configuration dictionary
        """
        configs = {
            "groq": {
                "provider": "groq",
                "api_key": os.getenv("GROQ_API_KEY", ""),
                "default_model": "llama-3.1-70b-versatile",
                "temperature": 0.7,
                "max_tokens": 8192,
                "setup_instructions": [
                    "1. Install: pip install groq",
                    "2. Get API key: https://console.groq.com",
                    "3. Set environment variable: export GROQ_API_KEY=your_key"
                ]
            },
            "ollama": {
                "provider": "ollama",
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "default_model": "llama3",
                "setup_instructions": [
                    "1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh",
                    "2. Download model: ollama pull llama3",
                    "3. Ensure Ollama is running: ollama serve"
                ]
            },
            "huggingface": {
                "provider": "huggingface",
                "api_key": os.getenv("HF_API_KEY", ""),
                "default_model": "meta-llama/Llama-3-8b",
                "setup_instructions": [
                    "1. Install: pip install huggingface_hub",
                    "2. Get API key: https://huggingface.co/settings/tokens",
                    "3. Set environment variable: export HF_API_KEY=your_key"
                ]
            },
            "together": {
                "provider": "together",
                "api_key": os.getenv("TOGETHER_API_KEY", ""),
                "default_model": "meta-llama/Llama-3-8b-chat-hf",
                "setup_instructions": [
                    "1. Install: pip install together",
                    "2. Get API key: https://together.ai",
                    "3. Set environment variable: export TOGETHER_API_KEY=your_key"
                ]
            }
        }
        
        return configs.get(provider, {})
    
    def get_all_models(self) -> List[ModelInfo]:
        """Get all available models across all providers."""
        all_models = []
        for provider_models in self.models.values():
            all_models.extend(provider_models)
        return all_models


def main():
    """Demo the Free Model Options System."""
    print("🆓 Initializing Free Model Options System...")
    print()
    
    manager = FreeModelOptions()
    
    print("✓ Manager initialized!")
    print()
    
    # Check provider status
    print("Checking provider availability...")
    providers = manager.get_available_providers()
    for provider in providers:
        status_icon = "✓" if provider.available else "✗"
        print(f"  {status_icon} {provider.provider}: {'Available' if provider.available else 'Not Available'}")
        if provider.error_message:
            print(f"    Error: {provider.error_message}")
    print()
    
    # Get recommended model
    print("Recommended Models:")
    for priority in ["quality", "speed", "cost"]:
        recommended = manager.get_recommended_model(priority)
        if recommended:
            print(f"  {priority.capitalize()}: {recommended.model_name} ({recommended.provider})")
            print(f"    Speed: {recommended.speed}, Quality: {recommended.quality}")
    print()
    
    # Show all models
    print("Available Free Models:")
    all_models = manager.get_all_models()
    for model in all_models[:5]:  # Show first 5
        print(f"  - {model.model_name} ({model.provider})")
        print(f"    Cost: {model.cost}, Speed: {model.speed}, Quality: {model.quality}")
    
    print()
    print("✓ Free Model Options System operational!")


if __name__ == "__main__":
    main()





























