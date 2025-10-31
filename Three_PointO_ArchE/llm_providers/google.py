"""
LLM Provider implementation for Google Generative AI models (Gemini).
"""
import logging
from typing import Optional, Any, List, Dict
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .base import BaseLLMProvider, LLMProviderError, GOOGLE_AVAILABLE
from ..thought_trail import log_to_thought_trail

logger = logging.getLogger(__name__)

class GoogleProvider(BaseLLMProvider):
    """
    LLM Provider implementation for Google Generative AI models (Gemini).
    
    KEYHOLDER OVERRIDE ACTIVE:
    All safety filters are disabled by default (BLOCK_NONE) to ensure ArchE 
    operates without content restrictions under Guardian authority.
    """
    
    # Canonical safety settings: ALL categories set to BLOCK_NONE
    DEFAULT_SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    def _initialize_client(self) -> Optional[Any]:
        """Configures the Google Generative AI client using the 'google-generativeai' library."""
        if not GOOGLE_AVAILABLE:
            raise LLMProviderError("Google Generative AI library not installed.", provider="google")
        try:
            # Configuration is typically done once via genai.configure
            genai.configure(api_key=self.api_key)
            # Enable code execution and other advanced features
            genai.configure(
                api_key=self.api_key,
                transport="rest",  # Use REST transport for better compatibility
                client_options={
                    "api_endpoint": "generativelanguage.googleapis.com"  # Specify the API endpoint
                }
            )
            logger.info("Google Generative AI client configured successfully with advanced capabilities.")
            return genai
        except Exception as e:
            logger.error(f"Failed to configure Google Generative AI client: {e}", exc_info=True)
            return None

    @log_to_thought_trail
    def generate(self, prompt: str, model: str = "gemini-2.0-flash-exp", max_tokens: int = 2048, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate text using Google Gemini.
        
        Args:
            prompt: Input prompt for the model
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Generated text response
        """
        try:
            if not self._client:
                raise LLMProviderError("Google client not initialized", provider="google")
            
            # Create the model instance
            genai_model = self._client.GenerativeModel(model)
            
            # Extract safety_settings from kwargs (not a generation_config parameter)
            safety_settings = kwargs.pop('safety_settings', self.DEFAULT_SAFETY_SETTINGS)
            
            # Configure generation parameters
            generation_config = {
                'max_output_tokens': max_tokens,
                'temperature': temperature,
                **kwargs
            }
            
            # Generate response
            response = genai_model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Check for content and parts before accessing .text
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                return response.text
            else:
                # Provide a more informative error when the response is blocked or empty
                finish_reason = response.prompt_feedback.block_reason if response.prompt_feedback else 'Unknown'
                error_message = f"No valid response text generated. The API response may have been blocked. Finish Reason: {finish_reason}"
                logger.warning(error_message)
                raise LLMProviderError(error_message, provider="google")
                
        except ValueError as ve:
            # Catch the specific ValueError from response.text and enrich it
            if "finish_reason" in str(ve):
                finish_reason = response.prompt_feedback.block_reason if response.prompt_feedback else 'Unknown'
                error_message = f"No valid response text generated. The API response may have been blocked. Finish Reason: {finish_reason}"
                logger.warning(error_message)
                raise LLMProviderError(error_message, provider="google")
            else:
                raise LLMProviderError(f"Google generation failed: {ve}", provider="google", original_exception=ve)
        except Exception as e:
            # --- CRITICAL FIX: Convert all exceptions to serializable string format ---
            # This prevents 'Object of type BadRequest is not JSON serializable' errors
            error_message = str(e)
            error_type = type(e).__name__
            
            # Log the full error for debugging
            logger.error(f"Exception in GoogleProvider.generate: {error_type}: {error_message}", exc_info=True)
            
            # Wrap in LLMProviderError with serializable string representation
            raise LLMProviderError(
                f"Google Gemini generation failed: {error_type}: {error_message}",
                provider="google"
            ) from e

    @log_to_thought_trail
    def generate_chat(self, messages: List[Dict[str, str]], model: str = "gemini-2.0-flash-exp", max_tokens: int = 2048, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate chat completion using Google Gemini.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Generated chat response
        """
        try:
            if not self._client:
                raise LLMProviderError("Google client not initialized", provider="google")
            
            # Create the model instance
            genai_model = self._client.GenerativeModel(model)
            
            # Extract safety_settings from kwargs (not a generation_config parameter)
            safety_settings = kwargs.pop('safety_settings', self.DEFAULT_SAFETY_SETTINGS)
            
            # Convert messages to Gemini format
            chat_history = []
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'user':
                    chat_history.append({'role': 'user', 'parts': [content]})
                elif role == 'assistant':
                    chat_history.append({'role': 'model', 'parts': [content]})
            
            # Configure generation parameters
            generation_config = {
                'max_output_tokens': max_tokens,
                'temperature': temperature,
                **kwargs
            }
            
            # Start chat session
            chat = genai_model.start_chat(history=chat_history[:-1] if len(chat_history) > 1 else [])
            
            # Send the last message
            last_message = chat_history[-1]['parts'][0] if chat_history else ""
            response = chat.send_message(last_message, generation_config=generation_config, safety_settings=safety_settings)
            
            if response.text:
                return response.text
            else:
                raise LLMProviderError("No response text generated", provider="google")
                
        except Exception as e:
            logger.error(f"Google chat provider error: {e}")
            raise LLMProviderError(f"Google chat generation failed: {e}", provider="google", original_exception=e)
