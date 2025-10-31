"""
Dynamic Action Loader for ArchE

This module scans the ArchE codebase to discover and register all available actions
automatically, ensuring the Playbook Orchestrator has full visibility into the
system's capabilities.
"""

import os
import importlib
import inspect
import logging
from typing import List, Dict, Any, Callable

logger = logging.getLogger(__name__)

def is_action_function(func: Callable) -> bool:
    """
    Determines if a function is an action based on its docstring.
    """
    if not inspect.isfunction(func):
        return False
    
    docstring = inspect.getdoc(func)
    return docstring and "[IAR Enabled]" in docstring

def discover_and_register_actions(registry: Any, base_path: str):
    """
    Dynamically discovers and registers all actions in the codebase.
    """
    logger.info("Starting dynamic action discovery...")
    
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file)
                # Make the module name relative to the base_path
                relative_path = os.path.relpath(module_path, base_path)
                module_name = "Three_PointO_ArchE." + os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
                
                try:
                    module = importlib.import_module(module_name)
                    for name, func in inspect.getmembers(module, is_action_function):
                        action_name = name # Use the function name as the action name
                        registry.register_action(action_name, func)
                        logger.info(f"Dynamically registered action '{action_name}' from {module_name}")
                except Exception as e:
                    logger.warning(f"Could not import or inspect module {module_name}: {e}")

    logger.info("Dynamic action discovery completed.")
