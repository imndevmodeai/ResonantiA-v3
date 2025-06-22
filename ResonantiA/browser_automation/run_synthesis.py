import json
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Three_PointO_ArchE.llm_providers.openai_provider import OpenAIProvider

def run_synthesis():
    # 1. Load the workflow definition
    with open('../../workflows/agentic_research.json', 'r') as f:
        workflow = json.load(f)

    # 2. Define the inputs for the synthesis task
    user_query = "tell me adrianna checks last 3 performances and give me the links to them"
    
    with open('search_results_ddg.json', 'r') as f:
        search_results = json.load(f)

    # 3. Get the prompt from the synthesize_results task
    synthesis_task = workflow['tasks']['synthesize_results']
    prompt_template = synthesis_task['inputs']['prompt']

    # 4. Substitute the context and results into the prompt
    prompt = prompt_template.replace('{{ initial_context.user_query }}', user_query)
    prompt = prompt.replace('{{ execute_searches.results | to_json }}', json.dumps(search_results))

    # 5. Execute the LLM call
    # Assuming you have a way to call the LLM provider.
    # For this example, I'll use a placeholder for the actual LLM call.
    # In a real scenario, you would import and use your LLM provider here.
    
    # This is a simplified example. In the actual system, you'd use the llm_tool
    # or a direct provider call that's properly configured.
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set the OPENAI_API_KEY environment variable.")
        return

    provider = OpenAIProvider()
    final_answer = provider.generate_text(prompt, "gpt-4o", 2048)


    # 6. Print the final answer
    print("--- Agentic Research Synthesis ---")
    print(final_answer)

if __name__ == "__main__":
    run_synthesis() 