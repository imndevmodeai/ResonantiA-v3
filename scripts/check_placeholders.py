#!/usr/bin/env python3
import sys
import re

PLACEHOLDER_REGEX = r"\[\[PLACEHOLDER\]\]"

def main():
    has_placeholders = False
    for filename in sys.argv[1:]:
        if filename.endswith('.md'):
            continue
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if re.search(PLACEHOLDER_REGEX, line):
                        print(f"Error: Placeholder found in {filename} on line {i}:")
                        print(f"  > {line.strip()}")
                        has_placeholders = True
        except Exception as e:
            print(f"Could not check {filename}: {e}")

    if has_placeholders:
        sys.exit(1)
    else:
        print("No placeholders found in staged files.")
        sys.exit(0)

if __name__ == "__main__":
    main()
