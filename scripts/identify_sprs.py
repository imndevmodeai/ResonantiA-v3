import re
import sys
import json
import os # Added for environment variable access

def identify_sprs(raw_query_text):
    identified_spr_candidates = []
    if raw_query_text and isinstance(raw_query_text, str):
        # Regex for a single SPR-like word (e.g., InnovativE, SolutioN)
        # Starts with an uppercase, ends with an uppercase, alphanumeric in between.
        single_word_spr_pattern = r'[A-Z][a-zA-Z0-9]*[A-Z]'
        words = raw_query_text.split()
        cleaned_words = [word.strip('. ,!?;:') for word in words]

        for i, clean_word in enumerate(cleaned_words):
            # Check for single-word SPRs
            if re.fullmatch(single_word_spr_pattern, clean_word):
                identified_spr_candidates.append(clean_word)
                
                # Check for two-word SPRs (e.g., InnovativE SolutioN)
                if i + 1 < len(cleaned_words):
                    clean_next_word = cleaned_words[i+1]
                    if re.fullmatch(single_word_spr_pattern, clean_next_word):
                        two_word_phrase = f'{clean_word} {clean_next_word}'
                        identified_spr_candidates.append(two_word_phrase)
                        
                        # Optional: Add quoted version if SPRs might be stored/referred to with quotes
                        # two_word_phrase_quoted = f'"{two_word_phrase}"' # Note: f'"..."' if you want quotes in string
                        # identified_spr_candidates.append(two_word_phrase_quoted)

        # Deduplicate while preserving order (Python 3.7+)
        final_candidates = list(dict.fromkeys(identified_spr_candidates))
        return final_candidates
    return []

if __name__ == "__main__":
    input_query = os.environ.get("INPUT_QUERY")
    if not input_query: # Fallback if env var is not set
        # Try reading from stdin as a last resort, though env var is preferred for this setup
        # For subprocess, stdin might be empty if not explicitly fed.
        # Consider if a direct error is better if INPUT_QUERY is missing.
        try:
            input_query = sys.stdin.read()
            if not input_query.strip(): # Check if stdin was empty or just whitespace
                # If run without env var and no stdin, this will be an issue.
                # For now, proceed with potentially empty input_query, identify_sprs handles None.
                pass 
        except Exception: # pylint: disable=broad-except
            # If stdin reading fails for some reason with no env var.
            input_query = None 
            
    spr_list = identify_sprs(input_query)
    print(json.dumps({"identified_spr_list": spr_list})) 