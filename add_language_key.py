import json

WORKFLOW_FILE = 'workflows/asf_master_protocol_generation.json'

def add_language_to_workflow():
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {WORKFLOW_FILE} was not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {WORKFLOW_FILE}: {e}")
        return

    tasks_updated = []
    for task_name, task_data in workflow_data.get('tasks', {}).items():
        if task_data.get('action') == 'execute_code':
            if 'action_config' in task_data:
                if 'language' not in task_data['action_config']:
                    task_data['action_config']['language'] = 'python'
                    tasks_updated.append(task_name)
            else:
                task_data['action_config'] = {'language': 'python'}
                tasks_updated.append(task_name)


    if tasks_updated:
        try:
            with open(WORKFLOW_FILE, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            print(f"Successfully added language to tasks in '{WORKFLOW_FILE}': {', '.join(tasks_updated)}")
        except Exception as e:
            print(f"Error writing to {WORKFLOW_FILE}: {e}")
    else:
        print("No tasks requiring the language key were found or updated.")

if __name__ == "__main__":
    add_language_to_workflow() 