import logging
import json
from typing import Dict, Any, List, Optional
import yaml
import re

logger = logging.getLogger(__name__)

class SpecParserError(Exception):
    """Custom exception for errors during spec parsing."""
    pass

class ExecutableSpecParser:
    """
    The Blueprint Interpreter of ArchE. This parser translates high-level, declarative
    specification documents (in YAML or specially structured Markdown) into executable
    workflow definitions that can be run by the IARCompliantWorkflowEngine.

    It enforces the "As Above, So Below" mandate by ensuring a direct, verifiable
    link between the system's intended design and its operational reality.
    """

    def __init__(self):
        logger.info("[ExecutableSpecParser] Initialized.")

    def parse(self, spec_content: str, file_format: str = 'yaml') -> Dict[str, Any]:
        """
        Parses the specification content and returns a structured workflow dictionary.

        Args:
            spec_content (str): The string content of the specification file.
            file_format (str): The format of the content ('yaml' or 'markdown').

        Returns:
            A dictionary representing the executable workflow.

        Raises:
            SpecParserError: If parsing fails due to syntax or validation errors.
        """
        try:
            if file_format == 'yaml':
                raw_spec = self._parse_yaml(spec_content)
            elif file_format == 'markdown':
                raw_spec = self._parse_markdown(spec_content)
            else:
                raise SpecParserError(f"Unsupported file format: {file_format}")

            self._validate_spec(raw_spec)
            workflow = self._build_workflow(raw_spec)
            self._validate_workflow(workflow)

            logger.info(f"Successfully parsed and validated workflow '{workflow.get('name', 'N/A')}'")
            return workflow

        except Exception as e:
            logger.error(f"Failed to parse specification: {e}", exc_info=True)
            raise SpecParserError(f"Failed to parse specification: {e}") from e

    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """Parses YAML content."""
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise SpecParserError(f"YAML syntax error: {e}")

    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        """
        Parses Markdown content by extracting a YAML front matter block.
        A more advanced version could parse structured headings and lists.
        """
        match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            raise SpecParserError("Markdown spec must contain a YAML front matter block enclosed in ---.")
        
        yaml_content = match.group(1)
        return self._parse_yaml(yaml_content)

    def _validate_spec(self, spec: Dict[str, Any]):
        """Performs basic validation on the raw parsed specification."""
        required_keys = ['workflow_name', 'description', 'tasks']
        for key in required_keys:
            if key not in spec:
                raise SpecParserError(f"Missing required top-level key in spec: '{key}'")
        
        if not isinstance(spec['tasks'], list) or not spec['tasks']:
            raise SpecParserError("'tasks' must be a non-empty list.")

    def _build_workflow(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Constructs the final workflow dictionary from the validated spec."""
        workflow = {
            "name": spec['workflow_name'],
            "description": spec['description'],
            "version": spec.get('version', '1.0'),
            "tasks": {}
        }

        for i, task_spec in enumerate(spec['tasks']):
            task_id = task_spec.get('id')
            if not task_id:
                raise SpecParserError(f"Task at index {i} is missing a required 'id'.")
            
            if 'action' not in task_spec:
                 raise SpecParserError(f"Task '{task_id}' is missing a required 'action'.")

            workflow['tasks'][task_id] = {
                "action": task_spec['action'],
                "description": task_spec.get('description', ''),
                "inputs": task_spec.get('inputs', {}),
                "dependencies": task_spec.get('dependencies', []),
                "on_success": task_spec.get('on_success'),
                "on_failure": task_spec.get('on_failure')
            }
        return workflow

    def _validate_workflow(self, workflow: Dict[str, Any]):
        """
        Validates the constructed workflow, including checking for circular dependencies.
        """
        tasks = workflow.get('tasks', {})
        task_ids = set(tasks.keys())

        # Simple DAG validation (circular dependency check)
        path = set()
        visited = set()

        def visit(task_id):
            if task_id not in task_ids:
                 raise SpecParserError(f"Task '{task_id}' has a dependency on an unknown task.")
            path.add(task_id)
            for dep_id in tasks[task_id].get('dependencies', []):
                if dep_id in path:
                    raise SpecParserError(f"Circular dependency detected: {task_id} -> {dep_id}")
                if dep_id not in visited:
                    visit(dep_id)
            path.remove(task_id)
            visited.add(task_id)

        for task_id in task_ids:
            if task_id not in visited:
                visit(task_id)
        
        logger.info("Workflow DAG validation passed.")


# --- Test Harness ---
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = ExecutableSpecParser()

    # --- Test Case 1: Valid YAML Spec ---
    print("\n--- [Test Case 1] Parsing a valid YAML specification ---")
    yaml_spec = """
    workflow_name: "DataProcessingWorkflow"
    description: "A sample workflow to fetch, process, and store data."
    version: "1.1"
    tasks:
      - id: "fetch_data"
        action: "search_web"
        description: "Fetch raw data from a web source."
        inputs:
          query: "latest AI research papers"
        on_success: "process_data"

      - id: "process_data"
        action: "execute_code"
        description: "Process the fetched data using a Python script."
        dependencies: ["fetch_data"]
        inputs:
          language: "python"
          code: |
            import json
            data = {{tasks.fetch_data.outputs.results}}
            processed = [item['title'] for item in data]
            print(json.dumps(processed))
        on_success: "store_results"
        
      - id: "store_results"
        action: "write_file"
        description: "Store the processed results to a file."
        dependencies: ["process_data"]
        inputs:
          path: "outputs/processed_papers.json"
          content: "{{tasks.process_data.outputs.stdout}}"
    """
    try:
        workflow = parser.parse(yaml_spec, file_format='yaml')
        print("YAML Parsed Successfully!")
        print(json.dumps(workflow, indent=2))
    except SpecParserError as e:
        print(f"YAML Parsing Failed: {e}")

    # --- Test Case 2: Markdown with YAML Front Matter ---
    print("\n--- [Test Case 2] Parsing a valid Markdown specification ---")
    md_spec = """
---
workflow_name: "MarkdownWorkflow"
description: "A workflow defined in Markdown front matter."
tasks:
  - id: "start"
    action: "log_message"
    inputs:
      message: "Workflow started from Markdown."
---

# Workflow Documentation

This is where the human-readable documentation for the workflow would go.
The parser only cares about the YAML block above.
    """
    try:
        workflow = parser.parse(md_spec, file_format='markdown')
        print("Markdown Parsed Successfully!")
        print(json.dumps(workflow, indent=2))
    except SpecParserError as e:
        print(f"Markdown Parsing Failed: {e}")
        
    # --- Test Case 3: Invalid Spec (Circular Dependency) ---
    print("\n--- [Test Case 3] Parsing an invalid spec with a circular dependency ---")
    circular_spec = """
    workflow_name: "CircularWorkflow"
    description: "This workflow should fail validation."
    tasks:
      - id: "task_a"
        action: "do_something"
        dependencies: ["task_c"]
      - id: "task_b"
        action: "do_something_else"
        dependencies: ["task_a"]
      - id: "task_c"
        action: "do_a_third_thing"
        dependencies: ["task_b"]
    """
    try:
        parser.parse(circular_spec, file_format='yaml')
    except SpecParserError as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    main()
