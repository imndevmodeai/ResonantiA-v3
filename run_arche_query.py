#!/usr/bin/env python3
"""
Wrapper script to run ask_arche_enhanced_v2.py with proper environment setup
"""
import sys
import os

# Set up Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set environment variables for enhanced Cursor ArchE
os.environ['ARCHE_USE_ENHANCED_CURSOR'] = '1'
os.environ['ARCHE_LLM_PROVIDER'] = 'cursor'

# Import and run the main function
if __name__ == "__main__":
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Analyze the current state of AI development and provide comprehensive strategic insights."
    
    # Set sys.argv for the main script
    sys.argv = ['ask_arche_enhanced_v2.py', query]
    
    # Import and execute
    try:
        from ask_arche_enhanced_v2 import main
        main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nAttempting direct execution...")
        import subprocess
        result = subprocess.run([
            sys.executable, 
            os.path.join(project_root, 'ask_arche_enhanced_v2.py'),
            query
        ], env=os.environ.copy())
        sys.exit(result.returncode)

