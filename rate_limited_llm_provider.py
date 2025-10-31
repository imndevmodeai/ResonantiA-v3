
import time
import json
import hashlib
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class RateLimitedGoogleProvider:
    """
    Rate-limited wrapper for Google LLM provider with caching and fallbacks.
    """
    
    def __init__(self, api_key: str, config_path: str = "enhanced_mastermind_config.json"):
        self.api_key = api_key
        self.config = self._load_config(config_path)
        self.last_request_time = 0
        self.request_count = 0
        self.cache_dir = self.config["google_api"]["caching"]["cache_dir"]
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize Google provider
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            self.config["google_api"]["model"],
            generation_config={
                "max_output_tokens": self.config["google_api"]["optimization"]["max_tokens"],
                "temperature": self.config["google_api"]["optimization"]["temperature"]
            }
        )
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration file."""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "google_api": {
                "model": "gemini-1.5-pro",
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 15,
                    "retry_delay": 60
                },
                "caching": {
                    "enabled": True,
                    "ttl": 3600
                }
            }
        }
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key for prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and not expired."""
        if not self.config["google_api"]["caching"]["enabled"]:
            return None
            
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, "r") as f:
                cached = json.load(f)
                if datetime.now().timestamp() - cached["timestamp"] < self.config["google_api"]["caching"]["ttl"]:
                    return cached["response"]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None
    
    def _cache_response(self, cache_key: str, response: str) -> None:
        """Cache response with timestamp."""
        if not self.config["google_api"]["caching"]["enabled"]:
            return
            
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        cache_data = {
            "response": response,
            "timestamp": datetime.now().timestamp()
        }
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
    
    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting."""
        if not self.config["google_api"]["rate_limiting"]["enabled"]:
            return
            
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.config["google_api"]["rate_limiting"]["requests_per_minute"]
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response with rate limiting and caching.
        """
        # Check cache first
        cache_key = self._get_cache_key(prompt)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        # Generate response with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text
                
                # Cache the response
                self._cache_response(cache_key, response_text)
                
                return response_text
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    # Rate limited, wait and retry
                    wait_time = self.config["google_api"]["rate_limiting"]["retry_delay"] * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    # Use fallback or raise error
                    return self._use_fallback(prompt, e)
        
        return "Error: Unable to generate response after multiple attempts."
    
    def _use_fallback(self, prompt: str, original_error: Exception) -> str:
        """Use fallback provider if available."""
        fallback_config = self.config.get("fallback_providers", {})
        if not fallback_config.get("enabled"):
            return f"Error: {original_error}"
        
        for provider in fallback_config.get("providers", []):
            api_key = os.environ.get(provider["env_var"])
            if api_key:
                try:
                    return self._call_fallback_provider(provider, prompt, api_key)
                except Exception as e:
                    continue
        
        return f"Error: No fallback providers available. Original error: {original_error}"
    
    def _call_fallback_provider(self, provider: Dict[str, Any], prompt: str, api_key: str) -> str:
        """Call fallback provider."""
        if provider["name"] == "OpenAI":
            import openai
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=provider["model"],
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        elif provider["name"] == "Anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=provider["model"],
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        return "Error: Unknown fallback provider"
