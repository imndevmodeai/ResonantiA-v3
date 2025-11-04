"""
Enhanced LLM Provider implementation for Cursor ArchE with Playwright-based monitoring.

This provider creates a robust communication bridge that:
1. Creates structured request files in a monitored queue
2. Uses Playwright (optional) for advanced monitoring/automation
3. Provides multiple communication channels (direct execution, file-based, web-based)
4. Includes retry logic and timeout handling
"""
import logging
import os
import sys
import json
import time
import threading
from typing import Optional, Any, List, Dict
from pathlib import Path
from .base import BaseLLMProvider, LLMProviderError

logger = logging.getLogger(__name__)

# Try to import Playwright for advanced monitoring
try:
    from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None
    Browser = None
    Page = None
    PlaywrightTimeout = None

class CursorArchEProviderEnhanced(BaseLLMProvider):
    """
    Enhanced LLM Provider that routes requests to Cursor ArchE with multiple communication channels.
    
    Communication Channels:
    1. Direct Execution: Uses execute_arche_analysis when in Cursor environment (fastest)
    2. File-Based Queue: Creates request files that Cursor ArchE monitors (reliable)
    3. Playwright Bridge: Uses Playwright to monitor/create web-based interface (advanced)
    """
    
    def __init__(self, api_key: str = "cursor_arche_v1", base_url: Optional[str] = None, 
                 enable_playwright: bool = True, **kwargs):
        """
        Initialize Enhanced Cursor ArchE provider.
        
        Args:
            api_key: Not strictly required for Cursor ArchE, but kept for compatibility
            base_url: Optional web-based bridge URL
            enable_playwright: Enable Playwright-based monitoring (if available)
            **kwargs: Additional configuration
        """
        self.api_key = api_key or "cursor_arche_v1"
        self.base_url = base_url
        self.provider_kwargs = kwargs
        self._provider_name = "cursor_arche_enhanced"
        self.enable_playwright = enable_playwright and PLAYWRIGHT_AVAILABLE
        
        # Set up communication directory
        project_root = Path(__file__).parent.parent.parent.parent
        self.comm_dir = project_root / '.cursor_arche_comm'
        self.requests_dir = self.comm_dir / 'requests'
        self.responses_dir = self.comm_dir / 'responses'
        self.queue_file = self.comm_dir / 'request_queue.json'
        
        # Create directories
        self.comm_dir.mkdir(exist_ok=True)
        self.requests_dir.mkdir(exist_ok=True)
        self.responses_dir.mkdir(exist_ok=True)
        
        # Initialize request queue if it doesn't exist
        if not self.queue_file.exists():
            with open(self.queue_file, 'w') as f:
                json.dump({"pending_requests": [], "processed_requests": []}, f)
        
        # Playwright browser instance (lazy-loaded)
        self._playwright = None
        self._browser = None
        self._page = None
        
        logger.info(f"Enhanced Cursor ArchE Provider initialized. Communication directory: {self.comm_dir}")
        if self.enable_playwright:
            logger.info("Playwright monitoring enabled")
    
    def _initialize_client(self) -> Optional[Any]:
        """Cursor ArchE doesn't use a traditional client."""
        return self
    
    def _initialize_playwright(self):
        """Initialize Playwright browser for monitoring (lazy load)."""
        if not self.enable_playwright:
            return False
        
        if self._playwright is None:
            try:
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(headless=True)
                self._page = self._browser.new_page()
                logger.info("Playwright browser initialized for monitoring")
                return True
            except Exception as e:
                logger.warning(f"Failed to initialize Playwright: {e}")
                self.enable_playwright = False
                return False
        return True
    
    def _cleanup_playwright(self):
        """Clean up Playwright resources."""
        if self._browser:
            try:
                self._browser.close()
            except:
                pass
        if self._playwright:
            try:
                self._playwright.stop()
            except:
                pass
        self._browser = None
        self._page = None
        self._playwright = None
    
    def _create_request_file(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Create a structured request file in the queue."""
        request_id = f"arche_req_{int(time.time() * 1000000)}"
        request_file = self.requests_dir / f"{request_id}.json"
        
        request_data = {
            "request_id": request_id,
            "prompt": prompt,
            "context": context or {},
            "timestamp": time.time(),
            "status": "pending",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "priority": context.get("priority", "normal") if context else "normal"
        }
        
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(request_data, f, indent=2)
        
        # Add to queue
        try:
            with open(self.queue_file, 'r') as f:
                queue_data = json.load(f)
            queue_data["pending_requests"].append(request_id)
            with open(self.queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to update queue: {e}")
        
        logger.info(f"Created enhanced Cursor ArchE request: {request_file}")
        return str(request_file)
    
    def _wait_for_response(self, request_id: str, timeout: float = 60.0) -> Optional[str]:
        """Wait for Cursor ArchE to process and respond with multiple check mechanisms."""
        response_file = self.responses_dir / f"{request_id}_response.json"
        start_time = time.time()
        check_interval = 0.5
        last_check = 0
        
        # Try Playwright-based monitoring if enabled
        playwright_monitoring = False
        if self.enable_playwright:
            try:
                if self._initialize_playwright():
                    playwright_monitoring = True
                    logger.info(f"Using Playwright to monitor response for {request_id}")
            except Exception as e:
                logger.debug(f"Playwright monitoring not available: {e}")
        
        while time.time() - start_time < timeout:
            current_time = time.time()
            
            # Check for response file
            if response_file.exists():
                try:
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    response_text = response_data.get('response', '')
                    status = response_data.get('status', 'completed')
                    
                    if status == 'completed' and response_text:
                        # Update queue
                        try:
                            with open(self.queue_file, 'r') as f:
                                queue_data = json.load(f)
                            if request_id in queue_data["pending_requests"]:
                                queue_data["pending_requests"].remove(request_id)
                            queue_data["processed_requests"].append({
                                "request_id": request_id,
                                "processed_at": time.time()
                            })
                            with open(self.queue_file, 'w') as f:
                                json.dump(queue_data, f, indent=2)
                        except Exception as e:
                            logger.warning(f"Failed to update queue after response: {e}")
                        
                        # Clean up response file
                        try:
                            response_file.unlink()
                        except:
                            pass
                        
                        logger.info(f"Received response for {request_id}")
                        return response_text
                except Exception as e:
                    logger.error(f"Error reading response file: {e}")
            
            # Playwright-based monitoring: Check web interface or monitor queue
            if playwright_monitoring and current_time - last_check > 2.0:  # Check every 2 seconds
                try:
                    # Could navigate to a monitoring dashboard if one exists
                    # For now, just log that we're monitoring
                    last_check = current_time
                except Exception as e:
                    logger.debug(f"Playwright monitoring check failed: {e}")
            
            # Check request file status
            request_file = self.requests_dir / f"{request_id}.json"
            if request_file.exists():
                try:
                    with open(request_file, 'r') as f:
                        req_data = json.load(f)
                    if req_data.get('status') == 'processing':
                        logger.debug(f"Request {request_id} is being processed...")
                    elif req_data.get('status') == 'failed':
                        error_msg = req_data.get('error', 'Unknown error')
                        logger.error(f"Request {request_id} failed: {error_msg}")
                        return None
                except:
                    pass
            
            time.sleep(check_interval)
        
        logger.warning(f"Timeout waiting for Cursor ArchE response (request_id: {request_id}, timeout: {timeout}s)")
        return None
    
    @property
    def _is_cursor_environment(self) -> bool:
        """Enhanced check for Cursor environment."""
        return (
            os.environ.get('CURSOR_ENABLED') == '1' or
            os.environ.get('CURSOR') is not None or
            'Cursor' in os.environ.get('TERM_PROGRAM', '') or
            os.path.exists(os.path.expanduser('~/.cursor')) or
            'cursor' in os.path.basename(sys.executable).lower() if hasattr(sys, 'executable') else False
        )
    
    def generate(self, prompt: str, model: str = "cursor-arche-v1", max_tokens: int = 4000, 
                 temperature: float = 0.7, timeout: float = 60.0, **kwargs) -> str:
        """
        Generate text using Enhanced Cursor ArchE provider.
        
        This method tries multiple communication channels:
        1. Direct execution (if in Cursor environment)
        2. Enhanced file-based queue with Playwright monitoring
        3. Fallback mechanisms
        
        Args:
            prompt: Input prompt for processing
            model: Model identifier
            max_tokens: Maximum response length
            temperature: Creativity parameter
            timeout: Maximum wait time for response
            **kwargs: Additional context and parameters
            
        Returns:
            Generated response from Cursor ArchE
        """
        try:
            context = {
                'max_tokens': max_tokens,
                'temperature': temperature,
                'timeout': timeout,
                **kwargs
            }
            
            # Channel 1: Direct execution (fastest, if in Cursor environment)
            if self._is_cursor_environment:
                logger.info("Enhanced Cursor ArchE: Attempting direct execution (Channel 1)")
                try:
                    from ..llm_tool import execute_arche_analysis
                    response_text = execute_arche_analysis(prompt, context)
                    if response_text and response_text.strip():
                        logger.info("Enhanced Cursor ArchE: Direct execution successful")
                        return response_text
                    else:
                        logger.warning("Direct execution returned empty response, trying file-based queue")
                except Exception as e:
                    logger.warning(f"Direct execution failed: {e}, trying file-based queue (Channel 2)")
            
            # Channel 2: Enhanced file-based queue with Playwright monitoring
            logger.info("Enhanced Cursor ArchE: Using file-based queue with monitoring (Channel 2)")
            request_file = self._create_request_file(prompt, context)
            request_id = os.path.splitext(os.path.basename(request_file))[0]
            
            # Signal to Cursor ArchE
            signal_file = self.comm_dir / "NEW_REQUEST"
            with open(signal_file, 'w') as f:
                f.write(f"{request_id}\n{time.time()}\n")
            
            # If Playwright is enabled, could open a monitoring dashboard
            if self.enable_playwright:
                try:
                    self._initialize_playwright()
                    # Could navigate to a dashboard URL if one exists
                    # For now, just use it for enhanced monitoring
                except Exception as e:
                    logger.debug(f"Playwright initialization for monitoring failed: {e}")
            
            # Wait for response with enhanced monitoring
            response_text = self._wait_for_response(request_id, timeout=timeout)
            
            if response_text:
                return response_text
            else:
                # Final fallback: Try direct execution one more time
                if self._is_cursor_environment:
                    logger.info("Enhanced Cursor ArchE: Trying direct execution as final fallback")
                    try:
                        from ..llm_tool import execute_arche_analysis
                        response_text = execute_arche_analysis(prompt, context)
                        if response_text and response_text.strip():
                            return response_text
                    except Exception as e:
                        logger.debug(f"Final fallback direct execution failed: {e}")
                
                raise LLMProviderError(
                    f"Cursor ArchE did not respond within timeout period ({timeout}s). "
                    f"Request ID: {request_id}. Check .cursor_arche_comm/requests/ for request file.",
                    provider="cursor_arche_enhanced"
                )
                
        except LLMProviderError:
            raise
        except Exception as e:
            logger.error(f"Enhanced Cursor ArchE provider error: {e}", exc_info=True)
            raise LLMProviderError(
                f"Enhanced Cursor ArchE generation failed: {str(e)}",
                provider="cursor_arche_enhanced",
                original_exception=e
            )
        finally:
            # Cleanup Playwright if it was initialized
            if self._playwright:
                self._cleanup_playwright()
    
    def generate_chat(self, messages: List[Dict[str, str]], model: str = "cursor-arche-v1", 
                     max_tokens: int = 4000, temperature: float = 0.7, **kwargs) -> str:
        """Generate chat completion using Enhanced Cursor ArchE."""
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user').capitalize()
            content = msg.get('content', '')
            prompt_parts.append(f"{role}: {content}")
        
        context = {
            'messages': messages,
            'conversation_mode': True,
            **kwargs
        }
        
        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        return self.generate(prompt, model, max_tokens, temperature, **context)
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get list of pending requests from the queue."""
        try:
            with open(self.queue_file, 'r') as f:
                queue_data = json.load(f)
            pending_ids = queue_data.get("pending_requests", [])
            
            requests = []
            for req_id in pending_ids:
                req_file = self.requests_dir / f"{req_id}.json"
                if req_file.exists():
                    try:
                        with open(req_file, 'r') as f:
                            requests.append(json.load(f))
                    except:
                        pass
            return requests
        except Exception as e:
            logger.error(f"Error getting pending requests: {e}")
            return []
    
    def __del__(self):
        """Cleanup on deletion."""
        self._cleanup_playwright()

