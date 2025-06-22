import json
import re
import os

file_path = 'knowledge_graph/spr_definitions_tv.json'

def format_spr_id_strict(original_id):
    if not original_id:
        return ""

    # Split by non-alphanumeric characters, keeping alphanumeric parts
    parts = re.findall(r'[A-Za-z0-9]+', original_id)
    
    camel_cased_parts = []
    for part in parts:
        if part.isalpha():
            camel_cased_parts.append(part[0].upper() + part[1:].lower())
        else: # numerical or mixed (like '4D')
            camel_cased_parts.append(part)
    
    # Join parts without spaces
    interim_id = "".join(camel_cased_parts)

    # Ensure overall first and last alphanumeric are capitalized
    final_id_chars = list(interim_id)
    
    # Capitalize first alphanumeric
    for i in range(len(final_id_chars)):
        if final_id_chars[i].isalpha():
            final_id_chars[i] = final_id_chars[i].upper()
            break
    
    # Capitalize last alphanumeric
    for i in range(len(final_id_chars) - 1, -1, -1):
        if final_id_chars[i].isalpha():
            final_id_chars[i] = final_id_chars[i].upper()
            break
    
    return "".join(final_id_chars)

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content_raw = f.read()

    # Attempt to load, if it fails due to syntax, it will be caught.
    data = json.loads(content_raw)

    for entry in data:
        if 'spr_id' in entry:
            original_spr_id = entry['spr_id']
            entry['spr_id'] = format_spr_id_strict(original_spr_id)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully reformatted SPR IDs and re-dumped JSON to {file_path}")

except json.JSONDecodeError as e:
    print(f"ERROR: Failed to decode JSON from {file_path}. Error: {e}")
    print("Please inspect the file for syntax errors like missing commas, unescaped backslashes, etc.")
    print("Specifically, check line and column mentioned in the error message.")
except Exception as e:
    print(f"An unexpected error occurred: {e}") 