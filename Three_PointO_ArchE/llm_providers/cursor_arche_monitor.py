#!/usr/bin/env python3
"""
Cursor ArchE Request Monitor with Playwright Integration

This script monitors the request queue and processes requests using Cursor ArchE's capabilities.
It can run as a background service or be invoked programmatically.

Usage:
    python -m Three_PointO_ArchE.llm_providers.cursor_arche_monitor
    python -m Three_PointO_ArchE.llm_providers.cursor_arche_monitor --watch
    python -m Three_PointO_ArchE.llm_providers.cursor_arche_monitor --process-all
"""
import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import Playwright
try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available. Basic file monitoring will be used.")

class CursorArchERequestMonitor:
    """
    Monitors and processes requests from the Cursor ArchE communication queue.
    Can use Playwright for advanced monitoring/automation if available.
    """
    
    def __init__(self, comm_dir: Optional[Path] = None):
        """Initialize the request monitor."""
        if comm_dir is None:
            comm_dir = project_root / '.cursor_arche_comm'
        
        self.comm_dir = Path(comm_dir)
        self.requests_dir = self.comm_dir / 'requests'
        self.responses_dir = self.comm_dir / 'responses'
        self.queue_file = self.comm_dir / 'request_queue.json'
        
        # Ensure directories exist
        self.comm_dir.mkdir(exist_ok=True)
        self.requests_dir.mkdir(exist_ok=True)
        self.responses_dir.mkdir(exist_ok=True)
        
        # Playwright resources
        self._playwright = None
        self._browser = None
        self._page = None
        
        logger.info(f"Cursor ArchE Request Monitor initialized. Monitoring: {self.comm_dir}")
    
    def _initialize_playwright(self):
        """Initialize Playwright browser for advanced monitoring."""
        if not PLAYWRIGHT_AVAILABLE:
            return False
        
        if self._playwright is None:
            try:
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(headless=True)
                self._page = self._browser.new_page()
                logger.info("Playwright browser initialized")
                return True
            except Exception as e:
                logger.warning(f"Failed to initialize Playwright: {e}")
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
    
    def _get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get list of pending requests from the queue."""
        if not self.queue_file.exists():
            return []
        
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
                            req_data = json.load(f)
                        if req_data.get('status') == 'pending':
                            requests.append(req_data)
                    except Exception as e:
                        logger.debug(f"Error reading request {req_id}: {e}")
            return requests
        except Exception as e:
            logger.error(f"Error reading queue: {e}")
            return []
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Public method to get list of pending requests."""
        return self._get_pending_requests()
    
    def _process_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Process a single request using Cursor ArchE capabilities.
        
        This method:
        1. Marks the request as 'processing'
        2. Executes the analysis using execute_arche_analysis
        3. Writes the response
        4. Updates the queue
        
        Returns:
            True if processing was successful, False otherwise
        """
        request_id = request_data.get('request_id')
        if not request_id:
            logger.error("Request missing request_id")
            return False
        
        request_file = self.requests_dir / f"{request_id}.json"
        response_file = self.responses_dir / f"{request_id}_response.json"
        
        try:
            # Mark as processing
            request_data['status'] = 'processing'
            request_data['processing_started_at'] = time.time()
            with open(request_file, 'w') as f:
                json.dump(request_data, f, indent=2)
            
            logger.info(f"Processing request: {request_id}")
            
            # Get prompt and context
            prompt = request_data.get('prompt', '')
            context = request_data.get('context', {})
            
            if not prompt:
                raise ValueError("Request missing prompt")
            
            # Execute using ArchE's direct execution
            try:
                from Three_PointO_ArchE.llm_tool import execute_arche_analysis
                response_text = execute_arche_analysis(prompt, context)
                
                if not response_text:
                    raise ValueError("Execution returned empty response")
                
                # Write response
                response_data = {
                    "request_id": request_id,
                    "response": response_text,
                    "status": "completed",
                    "completed_at": time.time(),
                    "execution_time": time.time() - request_data.get('processing_started_at', time.time())
                }
                
                with open(response_file, 'w', encoding='utf-8') as f:
                    json.dump(response_data, f, indent=2)
                
                # Update request status
                request_data['status'] = 'completed'
                request_data['completed_at'] = time.time()
                with open(request_file, 'w') as f:
                    json.dump(request_data, f, indent=2)
                
                # Update queue
                try:
                    with open(self.queue_file, 'r') as f:
                        queue_data = json.load(f)
                    if request_id in queue_data.get("pending_requests", []):
                        queue_data["pending_requests"].remove(request_id)
                    queue_data.setdefault("processed_requests", []).append({
                        "request_id": request_id,
                        "processed_at": time.time()
                    })
                    with open(self.queue_file, 'w') as f:
                        json.dump(queue_data, f, indent=2)
                except Exception as e:
                    logger.warning(f"Failed to update queue: {e}")
                
                logger.info(f"Successfully processed request: {request_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error executing request {request_id}: {e}", exc_info=True)
                
                # Mark as failed
                request_data['status'] = 'failed'
                request_data['error'] = str(e)
                request_data['failed_at'] = time.time()
                with open(request_file, 'w') as f:
                    json.dump(request_data, f, indent=2)
                
                # Write error response
                response_data = {
                    "request_id": request_id,
                    "response": "",
                    "status": "failed",
                    "error": str(e),
                    "failed_at": time.time()
                }
                with open(response_file, 'w', encoding='utf-8') as f:
                    json.dump(response_data, f, indent=2)
                
                return False
        
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}", exc_info=True)
            return False
    
    def process_all_pending(self):
        """Process all pending requests in the queue."""
        logger.info("Processing all pending requests...")
        requests = self._get_pending_requests()
        
        if not requests:
            logger.info("No pending requests found")
            return
        
        logger.info(f"Found {len(requests)} pending request(s)")
        
        for req in requests:
            self._process_request(req)
        
        logger.info("Finished processing all pending requests")
    
    def watch_and_process(self, check_interval: float = 2.0, max_iterations: Optional[int] = None):
        """
        Watch for new requests and process them automatically.
        
        Args:
            check_interval: Seconds between queue checks
            max_iterations: Maximum number of iterations (None for infinite)
        """
        logger.info(f"Starting watch mode (check interval: {check_interval}s)")
        
        # Initialize Playwright if available
        if PLAYWRIGHT_AVAILABLE:
            self._initialize_playwright()
        
        iteration = 0
        try:
            while True:
                if max_iterations and iteration >= max_iterations:
                    break
                
                requests = self._get_pending_requests()
                
                if requests:
                    logger.info(f"Found {len(requests)} pending request(s)")
                    for req in requests:
                        self._process_request(req)
                
                iteration += 1
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("Watch mode interrupted by user")
        finally:
            self._cleanup_playwright()

def main():
    """Main entry point for the monitor script."""
    parser = argparse.ArgumentParser(description='Cursor ArchE Request Monitor')
    parser.add_argument('--watch', action='store_true', 
                       help='Watch for new requests and process them continuously')
    parser.add_argument('--process-all', action='store_true',
                       help='Process all pending requests and exit')
    parser.add_argument('--check-interval', type=float, default=2.0,
                       help='Check interval in seconds for watch mode (default: 2.0)')
    parser.add_argument('--max-iterations', type=int, default=None,
                       help='Maximum iterations for watch mode (default: infinite)')
    parser.add_argument('--comm-dir', type=str, default=None,
                       help='Custom communication directory path')
    
    args = parser.parse_args()
    
    comm_dir = Path(args.comm_dir) if args.comm_dir else None
    monitor = CursorArchERequestMonitor(comm_dir=comm_dir)
    
    if args.process_all:
        monitor.process_all_pending()
    elif args.watch:
        monitor.watch_and_process(
            check_interval=args.check_interval,
            max_iterations=args.max_iterations
        )
    else:
        # Default: process all pending and exit
        monitor.process_all_pending()

if __name__ == '__main__':
    main()

