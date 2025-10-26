# --- START OF FILE Three_PointO_ArchE/playbook_orchestrator.py ---
import logging
import json
import re # Import the regular expressions module
from typing import Dict, Any, Callable, List
from .tools.enhanced_search_tool import perform_web_search
from .tools.synthesis_tool import invoke_llm_for_synthesis
from .tools.code_executor import execute_code
from .iar_components import IAR_Prepper

# Configure logger for this module
logger = logging.getLogger(__name__)

class PlaybookActionRegistry:
    """
    A lightweight, focused action registry specifically for high-level playbooks.
    It is completely decoupled from the legacy action_registry.py.
    """
    def __init__(self):
        self.actions: Dict[str, Callable] = {}
        self._register_core_actions()

    def _register_core_actions(self):
        """Registers the essential, modern tools needed for strategic workflows."""
        # Use the enhanced search tool with fallback reliability
        self.register_action("search_web", perform_web_search)
        self.register_action("generate_text_llm", invoke_llm_for_synthesis)
        self.register_action("execute_code", execute_code)
        self.register_action("display_output", self.display_output_action)
        logger.info("PlaybookActionRegistry initialized with core strategic actions.")

    def register_action(self, action_type: str, function: Callable):
        self.actions[action_type] = function

    def get_action(self, action_type: str) -> Callable:
        action = self.actions.get(action_type)
        if not action:
            logger.error(f"Action '{action_type}' not found in PlaybookActionRegistry.")
            raise KeyError(f"Action '{action_type}' not found.")
        return action

    def display_output_action(self, content: str, **kwargs) -> Dict[str, Any]:
        """A simple, clean display action for playbook results."""
        import pprint
        print("--- PLAYBOOK OUTPUT ---")
        pprint.pprint(content)
        print("-----------------------")
        return {"status": "success", "message": "Content displayed."}

class PlaybookOrchestrator:
    """
    Executes a strategic playbook (workflow JSON) using the focused PlaybookActionRegistry.
    """
    def __init__(self):
        self.registry = PlaybookActionRegistry()

    def run_playbook(self, playbook_path: str, initial_context: Dict = None) -> Dict[str, Any]:
        """
        Loads and executes a playbook from a JSON file.
        This is a simplified, robust implementation of the workflow engine logic.
        """
        logger.info(f"Orchestrating playbook: {playbook_path}")
        context = initial_context or {}
        
        try:
            with open(playbook_path, 'r') as f:
                playbook = json.load(f)
        except Exception as e:
            logger.critical(f"Failed to load playbook file '{playbook_path}': {e}", exc_info=True)
            return {"status": "error", "message": f"Failed to load playbook: {e}"}

        # Simple topological sort for dependency resolution
        task_order = self._resolve_task_order(playbook['tasks'])
        
        for task_key in task_order:
            task_def = playbook['tasks'][task_key]
            action_type = task_def['action_type']
            
            # Resolve inputs with the new, robust method
            resolved_inputs, missing_dependency = self._resolve_inputs_robustly(task_def.get('inputs', {}), context)
            
            iar_prepper = IAR_Prepper(task_key, resolved_inputs)

            # --- GRACEFUL FAILURE ---
            if missing_dependency:
                logger.warning(f"Skipping task '{task_key}' because its dependency '{missing_dependency}' was not met.")
                context[task_key] = iar_prepper.finish_with_skip(f"Dependency not met: {missing_dependency}")
                continue

            try:
                logger.info(f"Executing task '{task_key}' with action '{action_type}'...")
                action_func = self.registry.get_action(action_type)
                
                # Execute action and get result
                result = action_func(**resolved_inputs)
                
                # --- Minimal normalization for downstream templates ---
                try:
                    if action_type == 'execute_code' and isinstance(result, Dict) and result.get('stdout'):
                        parsed = json.loads(result['stdout'])
                        if isinstance(parsed, Dict):
                            result = parsed
                    elif action_type == 'generate_text_llm' and isinstance(result, Dict):
                        # Accept either direct text or IAR-wrapped
                        generated = None
                        if 'generated_text' in result:
                            generated = result['generated_text']
                        elif 'result' in result and isinstance(result['result'], Dict):
                            generated = result['result'].get('generated_text')
                        if generated is not None:
                            result = {'response_text': generated}
                except Exception:
                    # Leave result as-is if normalization fails
                    pass
                
                context[task_key] = result
                logger.info(f"Task '{task_key}' completed successfully.")
                
            except Exception as e:
                logger.error(f"Execution failed for task '{task_key}': {e}", exc_info=True)
                error_result = iar_prepper.finish_with_error(str(e))
                context[task_key] = error_result
                # In this simple engine, we halt on first error
                return {"status": "error", "message": f"Task '{task_key}' failed.", "final_context": context}

        logger.info(f"Playbook '{playbook['name']}' orchestrated successfully.")
        return {"status": "success", "final_context": context}

    def _resolve_inputs_robustly(self, input_template: Any, context: Dict) -> tuple[Any, str | None]:
        """
        Robustly resolves {{variable}} placeholders from the context in any data structure.
        Returns the resolved structure and the name of the first missing dependency, if any.
        """
        if isinstance(input_template, dict):
            resolved_dict = {}
            for key, value in input_template.items():
                resolved_value, missing_dep = self._resolve_inputs_robustly(value, context)
                if missing_dep:
                    return None, missing_dep
                resolved_dict[key] = resolved_value
            return resolved_dict, None
        
        elif isinstance(input_template, list):
            resolved_list = []
            for item in input_template:
                resolved_item, missing_dep = self._resolve_inputs_robustly(item, context)
                if missing_dep:
                    return None, missing_dep
                resolved_list.append(resolved_item)
            return resolved_list, None

        elif isinstance(input_template, str):
            missing_dependency = None
            
            def replacer(match):
                nonlocal missing_dependency
                if missing_dependency: return "" # Stop trying if one already failed

                full_path = match.group(1).strip()
                # Support simple default filter syntax: var.path | default(...)
                m = re.match(r"^(.*?)\|\s*default\((.*)\)$", full_path)
                default_literal = None
                if m:
                    full_path = m.group(1).strip()
                    default_literal = m.group(2).strip()

                parts = full_path.split('.')
                task_key = parts[0]
                
                if task_key not in context:
                    # If default is provided, return it directly
                    if default_literal is not None:
                        return default_literal
                    missing_dependency = match.group(1).strip()
                    return ""

                val = context[task_key]
                try:
                    for part in parts[1:]:
                        if isinstance(val, dict):
                            if part in val:
                                val = val[part]
                            elif 'result' in val and isinstance(val['result'], dict) and part in val['result']:
                                val = val['result'][part]
                            else:
                                raise KeyError(part)
                        elif isinstance(val, list) and part.isdigit():
                            val = val[int(part)]
                        else:
                            if isinstance(val, (dict, list)):
                                return json.dumps(val)
                            if isinstance(val, str):
                                return json.dumps(val)
                            return str(val)
                except (KeyError, IndexError, TypeError, json.JSONDecodeError):
                    # Use default if available
                    if default_literal is not None:
                        return default_literal
                    missing_dependency = match.group(1).strip()
                    return ""
                
                # If the resolved value is falsy and default exists, use default
                if (val is None or (isinstance(val, str) and val.strip() == "")) and default_literal is not None:
                    return default_literal

                if isinstance(val, (dict, list)):
                    return json.dumps(val)
                return str(val)

            resolved_string = re.sub(r"\{\{\s*(.*?)\s*\}\}", replacer, input_template)
            
            if missing_dependency:
                return None, missing_dependency
            
            # Attempt to parse the resolved string as JSON if it's the only thing
            try:
                if resolved_string.strip().startswith(('{', '[')):
                    return json.loads(resolved_string), None
            except json.JSONDecodeError:
                pass # It's just a string, not JSON, which is fine.

            return resolved_string, None

        else:
            return input_template, None # Not a string, dict, or list, so no templates to resolve

    def _resolve_task_order(self, tasks: Dict) -> List[str]:
        """Performs a simple topological sort to determine execution order."""
        from collections import deque
        
        graph = {key: set(val.get('dependencies', [])) for key, val in tasks.items()}
        in_degree = {key: 0 for key in graph}
        for u in graph:
            for v in graph[u]:
                in_degree[u] += 1
        
        queue = deque([key for key in in_degree if in_degree[key] == 0])
        order = []
        
        while queue:
            u = queue.popleft()
            order.append(u)
            for v_key, deps in graph.items():
                if u in deps:
                    in_degree[v_key] -= 1
                    if in_degree[v_key] == 0:
                        queue.append(v_key)
        
        if len(order) != len(tasks):
            raise ValueError("Cycle detected in task dependencies or dependencies not met.")
            
        return order

# --- Global Orchestrator Instance ---
main_orchestrator = PlaybookOrchestrator()

def run_playbook(playbook_path: str) -> Dict[str, Any]:
    """Convenience function to run a playbook with the main orchestrator."""
    return main_orchestrator.run_playbook(playbook_path)
