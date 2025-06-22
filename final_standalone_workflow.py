import json
import os
import sys
import subprocess
import google.generativeai as genai

def run_final_standalone_workflow():
    """
    A completely standalone script to execute the search and synthesis process,
    avoiding all internal project imports to bypass the architectural flaws.
    """
    user_query = "look up her last 3 porn performances"
    
    # 1. Execute the Puppeteer search script using a subprocess
    print("--- Running Puppeteer Search ---")
    search_script_path = os.path.join('ResonantiA', 'browser_automation', 'search.js')
    output_path = os.path.join('ResonantiA', 'browser_automation', 'final_results.json')
    
    try:
        subprocess.run(
            [
                'node', 
                search_script_path, 
                '--engine=duckduckgo', 
                f'--query={user_query}', 
                f'--output={output_path}'
            ], 
            check=True,
            capture_output=True,
            text=True
        )
        print("Search script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: The search script failed with exit code {e.returncode}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)

    # 2. Read the search results
    print("\\n--- Reading Search Results ---")
    try:
        with open(output_path, 'r') as f:
            search_results = json.load(f)
        print(f"Successfully loaded {len(search_results)} results.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Could not read or parse the results file: {e}")
        sys.exit(1)

    # 3. Synthesize the results using Google's Generative AI
    print("\\n--- Synthesizing Results with Google AI ---")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set.")
        sys.exit(1)
    
    genai.configure(api_key=google_api_key)

    workflow_path = 'workflows/agentic_research.json'
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Workflow file not found at {workflow_path}")
        sys.exit(1)

    synthesis_task = workflow['tasks']['synthesize_results']
    prompt_template = synthesis_task['inputs']['prompt']
    prompt = prompt_template.replace('{{ initial_context.user_query }}', user_query)
    prompt = prompt.replace('{{ execute_searches.results | to_json }}', json.dumps(search_results))

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        final_answer = response.text
        
        # 4. Print the final answer
        print("\\n--- Final Synthesized Answer ---")
        print(final_answer)

    except Exception as e:
        print(f"An error occurred during the Google AI API call: {e}")
        sys.exit(1)
    finally:
        # 5. Clean up the results file
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"\\nCleaned up temporary file: {output_path}")

if __name__ == "__main__":
    run_final_standalone_workflow() 