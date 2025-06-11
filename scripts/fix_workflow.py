import json
import os

# Define the path to the workflow file
workflow_path = 'workflows/Search_Comparison_Workflow_v1_0.json'

try:
    # Step 1: Read the existing workflow file
    with open(workflow_path, 'r') as f:
        workflow_data = json.load(f)

    # Step 2: Programmatically modify the Python dictionary
    
    # Modify the second search task
    if 'perform_internal_search' in workflow_data['tasks']:
        # Rename the task key
        workflow_data['tasks']['perform_duckduckgo_search'] = workflow_data['tasks'].pop('perform_internal_search')
        
        # Update the task content
        ddg_task = workflow_data['tasks']['perform_duckduckgo_search']
        ddg_task['description'] = "Perform a search using DuckDuckGo to provide an alternative external search perspective."
        ddg_task['action_type'] = "search_web"
        ddg_task['inputs'] = {
            "query": "{{ initial_context.user_query }}",
            "explanation": "To gather an alternative perspective on the search topic from DuckDuckGo: {{ initial_context.search_topic_context }}",
            "num_results": 10,
            "provider": "duckduckgo"
        }
        
    # Modify the comparison task
    if 'compare_search_results' in workflow_data['tasks']:
        compare_task = workflow_data['tasks']['compare_search_results']
        compare_task['description'] = "Analyze and compare Puppeteer (Google) and DuckDuckGo search results to identify insights and opportunities."
        compare_task['dependencies'] = [
            "perform_external_search",
            "perform_duckduckgo_search"
        ]
        
        # Update the input data mapping
        compare_task['inputs']['input_data'] = {
            "puppeteer_search_results": "{{ perform_external_search.results }}",
            "puppeteer_search_reflection": "{{ perform_external_search.reflection }}",
            "duckduckgo_search_results": "{{ perform_duckduckgo_search.results }}",
            "duckduckgo_search_reflection": "{{ perform_duckduckgo_search.reflection }}"
        }
        
        # Correct the Python code block to be a valid, single-line JSON string
        python_code = """
import sys
import json

# Initialize IAR-related variables with defaults
puppeteer_confidence = 'N/A'
puppeteer_status = 'N/A'
puppeteer_issues = []
duckduckgo_confidence = 'N/A'
duckduckgo_status = 'N/A'
duckduckgo_issues = []

input_json_str = sys.stdin.read()
data = json.loads(input_json_str)

puppeteer_data = data.get('puppeteer_search_results', [])
puppeteer_reflection_data = data.get('puppeteer_search_reflection', {})
if isinstance(puppeteer_reflection_data, str) and puppeteer_reflection_data:
    try:
        puppeteer_reflection_data = json.loads(puppeteer_reflection_data)
    except json.JSONDecodeError:
        puppeteer_reflection_data = {}
elif not isinstance(puppeteer_reflection_data, dict):
     puppeteer_reflection_data = {}

duckduckgo_data = data.get('duckduckgo_search_results', [])
duckduckgo_reflection_data = data.get('duckduckgo_search_reflection', {})
if isinstance(duckduckgo_reflection_data, str) and duckduckgo_reflection_data:
    try:
        duckduckgo_reflection_data = json.loads(duckduckgo_reflection_data)
    except json.JSONDecodeError:
        duckduckgo_reflection_data = {}
elif not isinstance(duckduckgo_reflection_data, dict):
    duckduckgo_reflection_data = {}

# Extract IAR details
puppeteer_confidence = puppeteer_reflection_data.get('confidence', 'N/A')
puppeteer_status = puppeteer_reflection_data.get('status', 'N/A')
puppeteer_issues = puppeteer_reflection_data.get('potential_issues', [])
if puppeteer_issues is None: puppeteer_issues = []

duckduckgo_confidence = duckduckgo_reflection_data.get('confidence', 'N/A')
duckduckgo_status = duckduckgo_reflection_data.get('status', 'N/A')
duckduckgo_issues = duckduckgo_reflection_data.get('potential_issues', [])
if duckduckgo_issues is None: duckduckgo_issues = []

puppeteer_results_count = len(puppeteer_data) if puppeteer_data is not None else 0
duckduckgo_results_count = len(duckduckgo_data) if duckduckgo_data is not None else 0

puppeteer_summary_text = f'Puppeteer (Google) search returned {puppeteer_results_count} items.'
duckduckgo_summary_text = f'DuckDuckGo search returned {duckduckgo_results_count} items.'

comparison_notes = []
if puppeteer_results_count > 0 and duckduckgo_results_count > 0:
    comparison_notes.append(f'Both Puppeteer ({puppeteer_results_count}) and DuckDuckGo ({duckduckgo_results_count}) searches found relevant data.')
elif puppeteer_results_count > 0:
    comparison_notes.append(f'Puppeteer search ({puppeteer_results_count}) found results, DuckDuckGo yielded none.')
elif duckduckgo_results_count > 0:
    comparison_notes.append(f'DuckDuckGo search ({duckduckgo_results_count}) found results, Puppeteer yielded none.')
else:
    comparison_notes.append("Neither Puppeteer nor DuckDuckGo searches yielded results.")

if puppeteer_results_count > duckduckgo_results_count:
    comparison_notes.append('Puppeteer (Google) appears to have found a broader set of results.')
elif duckduckgo_results_count > duckduckgo_results_count:
    comparison_notes.append('DuckDuckGo found more direct hits, suggesting a more focused result set.')
else:
    if puppeteer_results_count > 0 : comparison_notes.append('Comparable number of results from both search engines.')

# Add IAR-informed notes
iar_notes = []
iar_notes.append(f"Puppeteer Search IAR: Status='{puppeteer_status}', Confidence={puppeteer_confidence}.")
if puppeteer_issues:
    iar_notes.append(f"Puppeteer Search Potential Issues: {'; '.join(map(str,puppeteer_issues))}.")
if isinstance(puppeteer_confidence, (float, int)) and puppeteer_confidence < 0.7:
    iar_notes.append("Note: Puppeteer search confidence is moderate/low, results should be cross-verified.")

iar_notes.append(f"DuckDuckGo Search IAR: Status='{duckduckgo_status}', Confidence={duckduckgo_confidence}.")
if duckduckgo_issues:
    iar_notes.append(f"DuckDuckGo Search Potential Issues: {'; '.join(map(str,duckduckgo_issues))}.")
if isinstance(duckduckgo_confidence, (float, int)) and duckduckgo_confidence < 0.7:
    iar_notes.append("Note: DuckDuckGo search confidence is moderate/low, results should be cross-verified.")

# Combine all notes
all_notes = comparison_notes + iar_notes
insight_text = ' '.join(all_notes)
full_comparison_summary = f'{puppeteer_summary_text} {duckduckgo_summary_text} Comparison Insight & IAR Assessment: {insight_text}'

print(full_comparison_summary)
"""
        compare_task['inputs']['code'] = python_code

    # Step 3: Write the corrected dictionary back to the file
    with open(workflow_path, 'w') as f:
        json.dump(workflow_data, f, indent=2)

    print(f"Successfully corrected and updated {workflow_path}")

except FileNotFoundError:
    print(f"Error: The workflow file '{workflow_path}' was not found.")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON from {workflow_path}: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}") 