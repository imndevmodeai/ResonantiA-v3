from typing import Dict, Callable, Any
import logging
import inspect # Import inspect module
from .display_tool import display_output
from .web_search_tool import search_web
from .llm_tool import generate_text_llm
from .code_executor import execute_code
from .custom_file_tool import read_file_custom, edit_file_custom

logger = logging.getLogger(__name__)
ACTION_REGISTRY: Dict[str, Callable] = {}

def register_action(action_type: str, func: Callable, force: bool = False):
    if action_type in ACTION_REGISTRY and not force:
        raise ValueError(f"Action type '{action_type}' is already registered.")
    ACTION_REGISTRY[action_type] = func
    logger.debug(f"Action '{action_type}' registered.")

# Register core actions
register_action("display_output", display_output)
register_action("search_web", search_web)
register_action("generate_text_llm", generate_text_llm)
register_action("execute_code", execute_code)
register_action("read_file_custom", read_file_custom)
register_action("edit_file_custom", edit_file_custom)

async def execute_action(action_type: str, inputs: Dict[str, Any], context: Any, **kwargs) -> Dict[str, Any]:
    if action_type not in ACTION_REGISTRY:
        raise ValueError(f"Action type '{action_type}' not found in registry.")
    
    action_func = ACTION_REGISTRY[action_type]
    
    # Determine which arguments the action_func expects
    sig = inspect.signature(action_func)
    params = sig.parameters
    
    call_kwargs = {**inputs, **kwargs} # Start with inputs and any extra kwargs
    
    # If the action function expects a 'context' argument, pass it
    if 'context' in params:
        call_kwargs['context'] = context

    # Conditionally await the function based on whether it is a coroutine function
    if inspect.iscoroutinefunction(action_func):
        return await action_func(**call_kwargs)
    else:
        return action_func(**call_kwargs)
