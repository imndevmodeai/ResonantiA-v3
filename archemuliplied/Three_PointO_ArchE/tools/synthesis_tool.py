import json
import os
from ..llm_providers.openai_provider import OpenAIProvider

def synthesize_search_results(user_query: str, search_results: list) -> str:
    """
    Synthesizes search results into a final answer using an LLM.
    """
    # This path will need to be adjusted to be relative to the project root
    workflow_path = os.path.join(os.path.dirname(__file__), '../../../workflows/agentic_research.json')

    with open(workflow_path, 'r') as f:
        workflow = json.load(f)

    synthesis_task = workflow['tasks']['synthesize_results']
    prompt_template = synthesis_task['inputs']['prompt']

    prompt = prompt_template.replace('{{ initial_context.user_query }}', user_query)
    prompt = prompt.replace('{{ execute_searches.results | to_json }}', json.dumps(search_results))

    if not os.getenv("OPENAI_API_KEY"):
        return "Please set the OPENAI_API_KEY environment variable."

    provider = OpenAIProvider()
    final_answer = provider.generate_text(prompt, "gpt-4o", 2048)
    return final_answer 