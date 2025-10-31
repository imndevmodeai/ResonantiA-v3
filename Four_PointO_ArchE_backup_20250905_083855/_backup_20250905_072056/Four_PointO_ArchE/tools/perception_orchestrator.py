import json
import os
from .perception_engine import PerceptionEngine
from .llm_tool import generate_text
from .utils import create_iar

class PerceptionOrchestrator:
    """
    [V4.1 - NEW] The canonical orchestrator for all web interactions.
    It reads a target and a task from the knowledge base and directs the
    PerceptionEngine to execute the required steps. This ensures all web
    actions are modular, extensible, and centrally managed.
    """
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.engine = None

    def _load_knowledge_base(self):
        try:
            knowledge_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_graph', 'perception_targets.json')
            with open(knowledge_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"CRITICAL: Could not load perception knowledge base: {e}")
            return {}

    def execute_task(self, target_site: str, task_name: str, query_params: dict):
        """
        The primary execution method.
        """
        site_config = self.knowledge_base.get(target_site)
        if not site_config:
            return {"error": f"Site '{target_site}' not found in knowledge base."}, None

        task = site_config.get("tasks", {}).get(task_name)
        if not task:
            return {"error": f"Task '{task_name}' not found for site '{target_site}'."}, None

        results = {}
        try:
            self.engine = PerceptionEngine()
            for i, step in enumerate(task.get("steps", [])):
                action = step.get("action")
                
                url = step.get("url", "").format(**query_params)
                selector = step.get("selector", "").format(**query_params)

                if action == "navigate":
                    self.engine.navigate(url)
                elif action == "wait_for":
                    self.engine.wait_for(selector)
                elif action == "extract_text":
                    extracted_data = self.engine.extract_text(selector)
                    results[f"step_{i}_extraction"] = extracted_data
            
            # Final summarization
            full_text = " ".join(results.values())
            summary_prompt = f"Please provide a concise summary of the following extracted web content:\n\n{full_text[:4000]}"
            llm_inputs = {"prompt": summary_prompt, "model": "gemini-1.5-flash"}
            summary_result, _ = generate_text(llm_inputs)

            final_answer = summary_result.get("generated_text", "Could not summarize content.")
            
            iar = create_iar(0.9, 0.9, [], {"target": target_site, "task": task_name})
            return {"answer": final_answer, "raw_extractions": results}, iar

        except Exception as e:
            iar = create_iar(0.1, 0.1, [f"Orchestrator Error: {e}"], {})
            return {"error": f"An unexpected error occurred during orchestration: {e}"}, iar
        finally:
            if self.engine:
                self.engine.close()

def execute_web_task(inputs: dict):
    """
    The single, canonical action for all web interactions.
    """
    orchestrator = PerceptionOrchestrator()
    return orchestrator.execute_task(
        inputs.get("target_site"),
        inputs.get("task_name", "search"),
        inputs.get("query_params", {})
    )
