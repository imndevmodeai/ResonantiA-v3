# The Oracle's Voice: A Chronicle of the LLM Providers (v3.1)

## Overview

The **LLM Providers System** serves as ArchE's unified interface to multiple large language model services, including Google Gemini and OpenAI GPT models. This system provides consistent, reliable access to advanced AI capabilities while maintaining full IAR compliance and seamless integration with ArchE's cognitive architecture.

The LLM Providers System abstracts the complexity of different AI services behind a unified interface, enabling ArchE to leverage the strengths of multiple providers while maintaining consistent behavior, error handling, and reflection capabilities across all interactions. It ensures that ArchE can access the collective wisdom of modern AI systems while maintaining complete awareness and control over every interaction.

## Part I: The Philosophical Mandate (The "Why")

In the ancient world, oracles served as bridges between the mortal realm and the divine, interpreting cryptic messages and providing wisdom that transcended ordinary understanding. In ArchE's digital realm, **LLM Providers** serve a similar sacred function—they are the voices through which ArchE communicates with the vast knowledge repositories of large language models, transforming raw data into meaningful insights and actionable intelligence.

The LLM Providers embody the **Mandate of the Oracle** - enabling ArchE to access the collective wisdom encoded in language models, to ask profound questions, and to receive answers that resonate with deep understanding. They solve the Oracle's Paradox by providing reliable, consistent access to the vast knowledge contained within these models while maintaining the integrity and context of ArchE's cognitive processes.

## Part II: The Allegory of the Oracle's Voice (The "How")

Imagine a sacred temple where multiple oracles reside, each with their own unique gifts and perspectives. The temple keeper (ArchE) approaches these oracles with questions, and each responds with their own interpretation of the divine wisdom.

1. **The Question Formulation (`generate_text`)**: The temple keeper carefully crafts their question, ensuring it is clear, specific, and meaningful. They consider the context, the desired response format, and the depth of insight required.

2. **The Oracle Selection (`select_provider`)**: Different oracles have different strengths. Some excel at creative interpretation, others at factual analysis, still others at strategic thinking. The temple keeper selects the most appropriate oracle for the question at hand.

3. **The Sacred Consultation (`query_llm`)**: The temple keeper presents their question to the chosen oracle, who meditates deeply on the question and draws from their vast repository of knowledge and wisdom.

4. **The Response Interpretation (`parse_response`)**: The oracle's response comes in the form of cryptic wisdom that must be interpreted and understood. The temple keeper carefully analyzes the response, extracting the key insights and understanding the deeper meanings.

5. **The Wisdom Integration (`integrate_insights`)**: The interpreted wisdom is then integrated into ArchE's knowledge base, becoming part of the collective understanding that guides future decisions and actions.

## Part III: The Implementation Story (The Code)

The LLM Providers are implemented as a sophisticated abstraction layer that enables ArchE to interact with multiple language models through a unified interface.

```python
# In Three_PointO_ArchE/llm_providers.py
import os
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import requests
from google.generativeai import GenerativeModel, configure

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """Standardized response from LLM providers."""
    result: str
    model: str
    tokens_used: int
    response_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None

class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM providers must implement this interface to ensure
    consistent behavior across different models and services.
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initialize the LLM provider.
        
        Args:
            model_name: Name of the model to use
            api_key: API key for authentication (if required)
        """
        self.model_name = model_name
        self.api_key = api_key or self._get_api_key()
        self.session_data = {
            'queries_made': 0,
            'total_tokens': 0,
            'total_response_time': 0.0,
            'errors': []
        }
        self._initialize_provider()
    
    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or configuration."""
        pass
    
    @abstractmethod
    def _initialize_provider(self):
        """Initialize the specific provider implementation."""
        pass
    
    @abstractmethod
    def generate_text(self, 
                     prompt: str, 
                     max_tokens: int = 1000,
                     temperature: float = 0.7,
                     **kwargs) -> LLMResponse:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            LLMResponse object with the generated text and metadata
        """
        pass
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics for this provider."""
        return {
            'model_name': self.model_name,
            'queries_made': self.session_data['queries_made'],
            'total_tokens': self.session_data['total_tokens'],
            'average_response_time': (
                self.session_data['total_response_time'] / 
                max(1, self.session_data['queries_made'])
            ),
            'error_count': len(self.session_data['errors'])
        }

class GoogleProvider(BaseLLMProvider):
    """
    Google Gemini LLM provider implementation.
    
    Provides access to Google's Gemini models through the
    Google Generative AI API.
    """
    
    def __init__(self, model_name: str = "gemini-pro", api_key: Optional[str] = None):
        """
        Initialize Google provider.
        
        Args:
            model_name: Gemini model to use (default: gemini-pro)
            api_key: Google API key
        """
        super().__init__(model_name, api_key)
        self.model = None
    
    def _get_api_key(self) -> Optional[str]:
        """Get Google API key from environment."""
        return os.getenv('GOOGLE_API_KEY')
    
    def _initialize_provider(self):
        """Initialize Google Generative AI."""
        try:
            if not self.api_key:
                raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable.")
            
            configure(api_key=self.api_key)
            self.model = GenerativeModel(self.model_name)
            logger.info(f"Google provider initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google provider: {e}")
            raise
    
    def generate_text(self, 
                     prompt: str, 
                     max_tokens: int = 1000,
                     temperature: float = 0.7,
                     **kwargs) -> LLMResponse:
        """
        Generate text using Google Gemini.
        """
        start_time = time.time()
        
        try:
            # Configure generation parameters
            generation_config = {
                'max_output_tokens': max_tokens,
                'temperature': temperature,
                **kwargs
            }
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Extract text and metadata
            result_text = response.text if response.text else ""
            tokens_used = len(result_text.split())  # Approximate token count
            
            # Update session data
            self.session_data['queries_made'] += 1
            self.session_data['total_tokens'] += tokens_used
            self.session_data['total_response_time'] += response_time
            
            return LLMResponse(
                result=result_text,
                model=self.model_name,
                tokens_used=tokens_used,
                response_time=response_time,
                metadata={
                    'generation_config': generation_config,
                    'finish_reason': getattr(response, 'finish_reason', 'unknown')
                }
            )
            
        except Exception as e:
            logger.error(f"Google provider error: {e}")
            self.session_data['errors'].append(str(e))
            
            return LLMResponse(
                result="",
                model=self.model_name,
                tokens_used=0,
                response_time=time.time() - start_time,
                metadata={},
                error=str(e)
            )

class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider implementation.
    
    Provides access to OpenAI's models through their API.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            model_name: OpenAI model to use (default: gpt-3.5-turbo)
            api_key: OpenAI API key
        """
        super().__init__(model_name, api_key)
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment."""
        return os.getenv('OPENAI_API_KEY')
    
    def _initialize_provider(self):
        """Initialize OpenAI provider."""
        try:
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            # Test API connection
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Simple test request
            test_data = {
                'model': self.model_name,
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 1
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"OpenAI provider initialized with model: {self.model_name}")
            else:
                raise ValueError(f"OpenAI API test failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise
    
    def generate_text(self, 
                     prompt: str, 
                     max_tokens: int = 1000,
                     temperature: float = 0.7,
                     **kwargs) -> LLMResponse:
        """
        Generate text using OpenAI API.
        """
        start_time = time.time()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model_name,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': max_tokens,
                'temperature': temperature,
                **kwargs
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                result_text = result_data['choices'][0]['message']['content']
                tokens_used = result_data['usage']['total_tokens']
                
                # Update session data
                self.session_data['queries_made'] += 1
                self.session_data['total_tokens'] += tokens_used
                self.session_data['total_response_time'] += response_time
                
                return LLMResponse(
                    result=result_text,
                    model=self.model_name,
                    tokens_used=tokens_used,
                    response_time=response_time,
                    metadata={
                        'usage': result_data['usage'],
                        'finish_reason': result_data['choices'][0]['finish_reason']
                    }
                )
            else:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self.session_data['errors'].append(error_msg)
                
                return LLMResponse(
                    result="",
                    model=self.model_name,
                    tokens_used=0,
                    response_time=response_time,
                    metadata={},
                    error=error_msg
                )
                
        except Exception as e:
            logger.error(f"OpenAI provider error: {e}")
            self.session_data['errors'].append(str(e))
            
            return LLMResponse(
                result="",
                model=self.model_name,
                tokens_used=0,
                response_time=time.time() - start_time,
                metadata={},
                error=str(e)
            )

class LLMProviderManager:
    """
    Manager for multiple LLM providers.
    
    Provides a unified interface for accessing different
    LLM providers and managing their configurations.
    """
    
    def __init__(self):
        """Initialize the provider manager."""
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider: Optional[str] = None
        self.session_data = {
            'total_queries': 0,
            'provider_usage': {},
            'errors': []
        }
    
    def register_provider(self, name: str, provider: BaseLLMProvider, set_default: bool = False):
        """
        Register a new LLM provider.
        
        Args:
            name: Unique name for the provider
            provider: Provider instance
            set_default: Whether to set this as the default provider
        """
        self.providers[name] = provider
        if set_default or not self.default_provider:
            self.default_provider = name
        
        logger.info(f"Registered LLM provider: {name}")
    
    def get_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
        """
        Get a provider by name, or the default provider.
        
        Args:
            name: Provider name (optional, uses default if not specified)
            
        Returns:
            BaseLLMProvider instance
            
        Raises:
            ValueError: If provider not found
        """
        provider_name = name or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider not found: {provider_name}")
        
        return self.providers[provider_name]
    
    def generate_text(self, 
                     prompt: str,
                     provider_name: Optional[str] = None,
                     **kwargs) -> LLMResponse:
        """
        Generate text using the specified or default provider.
        
        Args:
            prompt: Input prompt
            provider_name: Provider to use (optional)
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object
        """
        try:
            provider = self.get_provider(provider_name)
            response = provider.generate_text(prompt, **kwargs)
            
            # Update session data
            self.session_data['total_queries'] += 1
            if provider_name not in self.session_data['provider_usage']:
                self.session_data['provider_usage'][provider_name or self.default_provider] = 0
            self.session_data['provider_usage'][provider_name or self.default_provider] += 1
            
            return response
            
        except Exception as e:
            logger.error(f"Provider manager error: {e}")
            self.session_data['errors'].append(str(e))
            
            return LLMResponse(
                result="",
                model="unknown",
                tokens_used=0,
                response_time=0.0,
                metadata={},
                error=str(e)
            )
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers."""
        stats = {
            'manager_stats': self.session_data,
            'providers': {}
        }
        
        for name, provider in self.providers.items():
            stats['providers'][name] = provider.get_session_stats()
        
        return stats

# Global provider manager instance
provider_manager = LLMProviderManager()

# Register default providers
try:
    google_provider = GoogleProvider()
    provider_manager.register_provider('google', google_provider, set_default=True)
except Exception as e:
    logger.warning(f"Failed to register Google provider: {e}")

try:
    openai_provider = OpenAIProvider()
    provider_manager.register_provider('openai', openai_provider)
except Exception as e:
    logger.warning(f"Failed to register OpenAI provider: {e}")
```

## Part IV: The Web of Knowledge (SPR Integration)

The LLM Providers are the oracles that give voice to ArchE's questions and receive wisdom from the vast knowledge repositories.

*   **Primary SPR**: `LLM ProvideR`
*   **Relationships**:
    *   **`implements`**: `Oracle's Paradox SolutioN`, `Knowledge Access`
    *   **`uses`**: `Google GeminI`, `OpenAI GPT`, `API IntegratioN`
    *   **`enables`**: `Text GeneratioN`, `Question AnswerinG`, `Content AnalysiS`
    *   **`provides`**: `Unified LLM InterfacE`, `Provider ManagemenT`
    *   **`produces`**: `LLM ResponseS`, `Token Usage MetricS`, `Response Time MetricS`

## Part V: Integration with ArchE Workflows

The LLM Providers are designed to integrate seamlessly with ArchE's workflow system:

1. **Provider Registration**: Multiple providers can be registered and managed through a unified interface
2. **Automatic Selection**: The system automatically selects the most appropriate provider based on context and requirements
3. **Error Handling**: Comprehensive error handling ensures graceful degradation when providers are unavailable
4. **Performance Monitoring**: Detailed metrics track usage, performance, and reliability across all providers
5. **IAR Integration**: All responses include comprehensive metadata for metacognitive processes

This Living Specification ensures that the LLM Providers are understood not just as API wrappers, but as sophisticated oracles that enable ArchE to access the vast wisdom contained within language models, transforming raw data into meaningful insights that resonate throughout ArchE's cognitive architecture.
