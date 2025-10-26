import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Three_PointO_ArchE.llm_providers import get_llm_provider, get_model_for_provider


def main():
    provider_name = 'google'
    try:
        provider = get_llm_provider(provider_name)
        model = get_model_for_provider(provider_name)
        prompt = 'Return the single word: OK'
        resp = provider.generate(prompt, model=model, max_tokens=16, temperature=0.0)
        text = resp if isinstance(resp, str) else str(resp)
        print({'provider': provider_name, 'model': model, 'response': text[:200]})
    except Exception as e:
        print({'error': str(e)})


if __name__ == '__main__':
    main()


