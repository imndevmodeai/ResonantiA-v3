"""
Prime Action Registry

This script runs the dynamic action loader to discover all actions and creates a
cached JSON file of the results. This breaks the circular import cycle by
decoupling action discovery from the registry itself.
"""

import json
import os
import logging
import sys

# Add project root to path to resolve relative imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Three_PointO_ArchE.action_registry import main_action_registry
from Three_PointO_ArchE.dynamic_action_loader import discover_and_register_actions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prime_registry():
    """
    Discovers all actions and saves them to a cached JSON file.
    """
    base_path = os.path.dirname(__file__)
    discover_and_register_actions(main_action_registry, base_path)
    
    action_list = list(main_action_registry.actions.keys())
    cache_path = os.path.join(base_path, "action_registry_cache.json")
    
    with open(cache_path, "w") as f:
        json.dump(action_list, f, indent=4)
        
    logger.info(f"Action registry primed. Found {len(action_list)} actions.")
    logger.info(f"Cache saved to {cache_path}")

if __name__ == "__main__":
    prime_registry()
