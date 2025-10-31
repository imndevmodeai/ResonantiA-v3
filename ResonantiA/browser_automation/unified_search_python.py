#!/usr/bin/env python3
"""
Unified Search Engine Python Wrapper
Integrates the JavaScript unified search engine with mastermind.interact
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedSearchWrapper:
    """
    Python wrapper for the unified search engine
    Provides seamless integration with mastermind.interact
    """
    
    def __init__(self, 
                 node_path: str = "node",
                 script_path: str = None,
                 debug: bool = False,
                 enable_human_handoff: bool = True,
                 headless: bool = False,
                 timeout: int = 300,
                 max_results: int = 10):
        """
        Initialize the search wrapper
        
        Args:
            node_path: Path to Node.js executable
            script_path: Path to unified_search_engine.js
            debug: Enable debug mode
            enable_human_handoff: Enable human CAPTCHA handoff
            headless: Run browser in headless mode
            timeout: Search timeout in seconds
            max_results: Maximum results per engine
        """
        self.node_path = node_path
        self.script_path = script_path or self._find_script_path()
        self.debug = debug
        self.enable_human_handoff = enable_human_handoff
        self.headless = headless
        self.timeout = timeout
        self.max_results = max_results
        
        # Validate script exists
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Unified search script not found: {self.script_path}")
    
    def _find_script_path(self) -> str:
        """Find the unified search engine script path"""
        possible_paths = [
            "unified_search_engine.js",
            "browser_automation/unified_search_engine.js",
            "../browser_automation/unified_search_engine.js",
            "ResonantiA/browser_automation/unified_search_engine.js"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        raise FileNotFoundError("Could not find unified_search_engine.js")
    
    async def search(self, 
                    query: str, 
                    engines: List[str] = None,
                    options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform search using the unified search engine
        
        Args:
            query: Search query
            engines: List of search engines to use
            options: Additional options
            
        Returns:
            Search results dictionary
        """
        if engines is None:
            engines = ['duckduckgo']
        
        if options is None:
            options = {}
        
        # Prepare command
        cmd = [
            self.node_path,
            self.script_path,
            query,
            ','.join(engines)
        ]
        
        # Add debug flag if enabled
        if self.debug:
            cmd.append('--debug')
        
        # Add additional options
        if options.get('debug'):
            cmd.append('--debug')
        
        logger.info(f"Executing search: {' '.join(cmd)}")
        
        try:
            # Execute the search
            result = await self._execute_search(cmd)
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                'error': str(e),
                'query': query,
                'engines': engines,
                'results': {}
            }
    
    async def _execute_search(self, cmd: List[str]) -> Dict[str, Any]:
        """Execute the search command and parse results"""
        
        # Create process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=self.timeout
        )
        
        # Log stderr for debugging
        if stderr:
            logger.debug(f"Search stderr: {stderr.decode()}")
        
        # Parse results
        if process.returncode == 0:
            try:
                results = json.loads(stdout.decode())
                return results
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse results: {e}")
                return {
                    'error': f'Failed to parse results: {e}',
                    'raw_output': stdout.decode()
                }
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"Search process failed: {error_msg}")
            return {
                'error': f'Process failed: {error_msg}',
                'return_code': process.returncode
            }
    
    def search_sync(self, 
                   query: str, 
                   engines: List[str] = None,
                   options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Synchronous version of search for non-async contexts
        """
        return asyncio.run(self.search(query, engines, options))
    
    async def search_with_handoff(self, 
                                query: str, 
                                engines: List[str] = None,
                                options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search with human CAPTCHA handoff support
        """
        if options is None:
            options = {}
        
        # Ensure human handoff is enabled
        options['enable_human_handoff'] = True
        options['headless'] = False  # Force non-headless for handoff
        
        logger.info(f"Starting search with human handoff: {query}")
        
        # Start the search
        result = await self.search(query, engines, options)
        
        # Check if CAPTCHA handoff is needed
        if self._needs_captcha_handoff(result):
            logger.info("CAPTCHA detected, waiting for human intervention...")
            
            # Wait for human to solve CAPTCHA
            await self._wait_for_captcha_solution()
            
            # Retry the search
            logger.info("Retrying search after CAPTCHA solution...")
            result = await self.search(query, engines, options)
        
        return result
    
    def _needs_captcha_handoff(self, result: Dict[str, Any]) -> bool:
        """Check if CAPTCHA handoff is needed"""
        if 'error' in result:
            error_msg = result['error'].lower()
            captcha_indicators = [
                'captcha',
                'unusual traffic',
                'security check',
                'verify you are human',
                'access denied',
                'blocked'
            ]
            return any(indicator in error_msg for indicator in captcha_indicators)
        
        # Check individual engine results
        for engine, engine_result in result.get('results', {}).items():
            if isinstance(engine_result, dict) and 'error' in engine_result:
                error_msg = engine_result['error'].lower()
                if any(indicator in error_msg for indicator in captcha_indicators):
                    return True
        
        return False
    
    async def _wait_for_captcha_solution(self, timeout: int = 300):
        """Wait for human to solve CAPTCHA"""
        logger.info(f"Waiting up to {timeout} seconds for CAPTCHA solution...")
        
        # In a real implementation, you might:
        # 1. Monitor the browser window
        # 2. Listen for user input
        # 3. Check for completion signals
        
        # For now, we'll just wait and let the user handle it manually
        await asyncio.sleep(timeout)
    
    def get_available_engines(self) -> List[str]:
        """Get list of available search engines"""
        return ['google', 'duckduckgo', 'bing']
    
    def validate_engines(self, engines: List[str]) -> List[str]:
        """Validate and filter search engines"""
        available = self.get_available_engines()
        valid_engines = [engine for engine in engines if engine.lower() in available]
        
        if not valid_engines:
            logger.warning(f"No valid engines found, using default: duckduckgo")
            return ['duckduckgo']
        
        return valid_engines


class MastermindSearchIntegration:
    """
    Integration class for mastermind.interact
    Provides high-level search functionality
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize mastermind search integration
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.search_wrapper = UnifiedSearchWrapper(
            debug=self.config.get('debug', False),
            enable_human_handoff=self.config.get('enable_human_handoff', True),
            headless=self.config.get('headless', False),
            timeout=self.config.get('timeout', 300),
            max_results=self.config.get('max_results', 10)
        )
        
        self.search_history = []
    
    async def search(self, 
                    query: str, 
                    engines: List[str] = None,
                    use_handoff: bool = True,
                    save_results: bool = True) -> Dict[str, Any]:
        """
        Perform search with mastermind integration
        
        Args:
            query: Search query
            engines: Search engines to use
            use_handoff: Enable human CAPTCHA handoff
            save_results: Save results to history
            
        Returns:
            Search results with metadata
        """
        if engines is None:
            engines = ['duckduckgo', 'google']
        
        # Validate engines
        engines = self.search_wrapper.validate_engines(engines)
        
        # Prepare options
        options = {
            'debug': self.config.get('debug', False),
            'enable_human_handoff': use_handoff,
            'headless': not use_handoff
        }
        
        logger.info(f"Mastermind search: {query} on {engines}")
        
        # Perform search
        if use_handoff:
            results = await self.search_wrapper.search_with_handoff(query, engines, options)
        else:
            results = await self.search_wrapper.search(query, engines, options)
        
        # Add metadata
        results['metadata'] = {
            'query': query,
            'engines': engines,
            'timestamp': time.time(),
            'use_handoff': use_handoff,
            'config': self.config
        }
        
        # Save to history
        if save_results:
            self.search_history.append(results)
        
        return results
    
    def search_sync(self, 
                   query: str, 
                   engines: List[str] = None,
                   use_handoff: bool = True,
                   save_results: bool = True) -> Dict[str, Any]:
        """
        Synchronous version of search
        """
        return asyncio.run(self.search(query, engines, use_handoff, save_results))
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history"""
        return self.search_history
    
    def clear_history(self):
        """Clear search history"""
        self.search_history.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search statistics"""
        if not self.search_history:
            return {'total_searches': 0, 'successful_searches': 0}
        
        total = len(self.search_history)
        successful = sum(1 for result in self.search_history if 'error' not in result)
        
        return {
            'total_searches': total,
            'successful_searches': successful,
            'success_rate': successful / total if total > 0 else 0,
            'last_search': self.search_history[-1]['metadata']['timestamp'] if self.search_history else None
        }


# Convenience functions for easy integration
def create_search_integration(config: Dict[str, Any] = None) -> MastermindSearchIntegration:
    """Create a search integration instance"""
    return MastermindSearchIntegration(config)

async def quick_search(query: str, 
                      engines: List[str] = None,
                      config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Quick search function"""
    integration = create_search_integration(config)
    return await integration.search(query, engines)

def quick_search_sync(query: str, 
                     engines: List[str] = None,
                     config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Synchronous quick search function"""
    return asyncio.run(quick_search(query, engines, config))


# Example usage and testing
if __name__ == "__main__":
    async def test_search():
        """Test the search functionality"""
        print("Testing Unified Search Engine...")
        
        # Create integration
        integration = create_search_integration({
            'debug': True,
            'enable_human_handoff': True,
            'headless': False
        })
        
        # Test search
        results = await integration.search(
            query="quantum computing applications",
            engines=['duckduckgo', 'google'],
            use_handoff=True
        )
        
        print("Search Results:")
        print(json.dumps(results, indent=2))
        
        # Print statistics
        stats = integration.get_statistics()
        print(f"\nStatistics: {stats}")
    
    # Run test
    asyncio.run(test_search()) 