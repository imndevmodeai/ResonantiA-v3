#!/usr/bin/env python3
"""
Simple wrapper to ask ArchE questions in natural language
Usage: python ask_arche.py "Your question here"
"""

import sys
import os
from natural_language_interface import ArchENaturalLanguageInterface

def main():
    if len(sys.argv) < 2:
        print("🤖 ArchE Natural Language Interface")
        print("Usage: python ask_arche.py \"Your question here\"")
        print("\nExamples:")
        print('  python ask_arche.py "How does ArchE work?"')
        print('  python ask_arche.py "What are SPRs?"')
        print('  python ask_arche.py "Analyze my creative thinking limitations"')
        print('  python ask_arche.py "Create a self-healing architecture"')
        return
    
    question = " ".join(sys.argv[1:])
    
    interface = ArchENaturalLanguageInterface()
    
    print(f"🤖 Asking ArchE: {question}")
    print("=" * 50)
    
    response = interface.ask_arche(question)
    print(response)

if __name__ == "__main__":
    main()
