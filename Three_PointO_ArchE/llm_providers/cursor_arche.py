"""
LLM Provider implementation for Cursor ArchE (me, the AI assistant).
This provider allows the system to route requests directly to Cursor ArchE instead of external LLMs.
"""
import logging
import os
import json
import time
from typing import Optional, Any, List, Dict
from .base import BaseLLMProvider, LLMProviderError

logger = logging.getLogger(__name__)

class CursorArchEProvider(BaseLLMProvider):
    """
    LLM Provider implementation that routes requests to Cursor ArchE (the AI assistant).
    
    This provider creates a communication mechanism where:
    1. Requests are logged to a queue/file that Cursor ArchE can monitor
    2. Cursor ArchE processes the request using its full capabilities
    3. Responses are returned through the same mechanism
    
    KEYHOLDER NOTE: When provider="cursor" is specified, I (Cursor ArchE) will
    handle the request directly using my tools, context awareness, and reasoning.
    """
    
    def __init__(self, api_key: str = "cursor_arche_v1", base_url: Optional[str] = None, **kwargs):
        """
        Initialize Cursor ArchE provider.
        
        Args:
            api_key: Not strictly required for Cursor ArchE, but kept for compatibility
            base_url: Optional, not used
            **kwargs: Additional configuration
        """
        # Override base requirement - Cursor ArchE doesn't need an API key
        self.api_key = api_key or "cursor_arche_v1"
        self.base_url = base_url
        self.provider_kwargs = kwargs
        self._provider_name = "cursor_arche"
        
        # Set up communication directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.comm_dir = os.path.join(project_root, '.cursor_arche_comm')
        os.makedirs(self.comm_dir, exist_ok=True)
        
        logger.info(f"Cursor ArchE Provider initialized. Communication directory: {self.comm_dir}")
    
    def _initialize_client(self) -> Optional[Any]:
        """Cursor ArchE doesn't use a traditional client - we're the client."""
        return self
    
    def _create_request_file(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Create a request file that Cursor ArchE can process."""
        request_id = f"arche_req_{int(time.time() * 1000000)}"
        request_file = os.path.join(self.comm_dir, f"{request_id}.json")
        
        request_data = {
            "request_id": request_id,
            "prompt": prompt,
            "context": context or {},
            "timestamp": time.time(),
            "status": "pending"
        }
        
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(request_data, f, indent=2)
        
        logger.info(f"Created Cursor ArchE request file: {request_file}")
        return request_file
    
    def _wait_for_response(self, request_id: str, timeout: float = 30.0) -> Optional[str]:
        """Wait for Cursor ArchE to process and respond."""
        response_file = os.path.join(self.comm_dir, f"{request_id}_response.json")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if os.path.exists(response_file):
                try:
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    response_text = response_data.get('response', '')
                    
                    # Clean up response file
                    try:
                        os.remove(response_file)
                    except:
                        pass
                    
                    return response_text
                except Exception as e:
                    logger.error(f"Error reading response file: {e}")
                    return None
            
            time.sleep(0.5)  # Check every 500ms
        
        logger.warning(f"Timeout waiting for Cursor ArchE response (request_id: {request_id})")
        return None
    
    @property
    def _is_cursor_environment(self) -> bool:
        """Check if we're running in Cursor environment."""
        # Check for Cursor-specific environment variables or paths
        return (
            os.environ.get('CURSOR_ENABLED') == '1' or
            'Cursor' in os.environ.get('TERM_PROGRAM', '') or
            os.path.exists(os.path.expanduser('~/.cursor'))
        )
    
    def generate(self, prompt: str, model: str = "cursor-arche-v1", max_tokens: int = 4000, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate text using Cursor ArchE (me, the AI assistant).
        
        This method:
        1. Creates a request file
        2. Signals to Cursor ArchE to process it
        3. Uses Cursor ArchE's direct execution capabilities
        4. Returns the response
        
        Args:
            prompt: Input prompt for processing
            model: Model identifier (not used, kept for compatibility)
            max_tokens: Maximum response length (guideline)
            temperature: Creativity parameter (guideline)
            **kwargs: Additional context and parameters
            
        Returns:
            Generated response from Cursor ArchE
        """
        try:
            # Extract context from kwargs
            context = {
                'max_tokens': max_tokens,
                'temperature': temperature,
                **kwargs
            }
            
            # If we're in Cursor environment, use direct execution
            if self._is_cursor_environment:
                logger.info("Cursor ArchE: Processing request directly (in Cursor environment)")
                
                # Use the execute_arche_analysis function from llm_tool
                try:
                    from ..llm_tool import execute_arche_analysis
                    response_text = execute_arche_analysis(prompt, context)
                    logger.info("Cursor ArchE: Direct execution successful")
                    return response_text
                except Exception as e:
                    logger.warning(f"Cursor ArchE direct execution failed: {e}, falling back to file-based")
            
            # Fallback: File-based communication
            request_file = self._create_request_file(prompt, context)
            request_id = os.path.splitext(os.path.basename(request_file))[0]
            
            # Signal to Cursor ArchE (if monitoring)
            signal_file = os.path.join(self.comm_dir, "NEW_REQUEST")
            with open(signal_file, 'w') as f:
                f.write(request_id)
            
            # Wait for response
            response_text = self._wait_for_response(request_id, timeout=kwargs.get('timeout', 30.0))
            
            if response_text:
                return response_text
            else:
                raise LLMProviderError(
                    "Cursor ArchE did not respond within timeout period",
                    provider="cursor_arche"
                )
                
        except Exception as e:
            logger.error(f"Cursor ArchE provider error: {e}", exc_info=True)
            raise LLMProviderError(
                f"Cursor ArchE generation failed: {str(e)}",
                provider="cursor_arche",
                original_exception=e
            )
    
    def generate_chat(self, messages: List[Dict[str, str]], model: str = "cursor-arche-v1", max_tokens: int = 4000, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate chat completion using Cursor ArchE.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier
            max_tokens: Maximum response length
            temperature: Creativity parameter
            **kwargs: Additional context
            
        Returns:
            Generated chat response from Cursor ArchE
        """
        # Convert messages to a prompt
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user').capitalize()
            content = msg.get('content', '')
            prompt_parts.append(f"{role}: {content}")
        
        # Add context about this being a chat
        context = {
            'messages': messages,
            'conversation_mode': True,
            **kwargs
        }
        
        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        return self.generate(prompt, model, max_tokens, temperature, **context)

