# filename: run_instrumented_mastermind.py
# This is the final, corrected entry point for the ArchE system.

import argparse
import json
import sys
import os
import logging

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ArchE_Wrapper")

# --- Ensure Project Root is in Path ---
# This makes imports robust regardless of where the script is called from,
# as long as the CWD is the project root.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- Core Imports ---
# These imports will now succeed because the package is correctly installed.
from mastermind.interact import KnO
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine

class ArchEInstrumentedWrapper:
    """
    A meta-layer that wraps the KnO to provide enhanced capabilities
    like ThoughtTrail generation, as envisioned by the ResonantiA Protocol.
    """
    def __init__(self, query: str):
        logger.info(f"Initializing KnO to handle query: '{query}'")
        self.kno = KnO()
        self.query = query
        self.thought_trail = []

    def instrument_kno(self):
        """
        Performs deep logic replacement to instrument the KnO instance.
        This is a conceptual representation of meta-cognitive enhancement.
        """
        logger.info("Instrumenting KnO instance with deep logic replacement...")
        # Replace original methods with instrumented versions
        self.original_decompose = self.kno._decompose_query
        self.kno._decompose_query = self.instrumented_decompose

        self.original_retrieve = self.kno._retrieve_context
        self.kno._retrieve_context = self.instrumented_retrieve

        self.original_reason = self.kno.reasoning_engine.reason
        self.kno.reasoning_engine.reason = self.instrumented_reason
        logger.info("Instrumentation complete.")

    def instrumented_decompose(self, query):
        self.thought_trail.append({"step": "Deconstruct Query", "input": query})
        result = self.original_decompose(query)
        self.thought_trail.append({"step": "Deconstruct Query", "output": result})
        return result

    def instrumented_retrieve(self, query):
        self.thought_trail.append({"step": "Retrieve Context", "input": query})
        result = self.original_retrieve(query)
        self.thought_trail.append({"step": "Retrieve Context", "output": result})
        return result

    def instrumented_reason(self, query, context):
        self.thought_trail.append({"step": "Synthesize Response", "input": {"query": query, "context_len": len(context)}})
        result = self.original_reason(query, context)
        self.thought_trail.append({"step": "Synthesize Response", "output": result})
        return result

    def execute_query(self):
        logger.info("Executing instrumented query...")
        response = self.kno.handle_query(self.query)
        self.export_thought_trail()
        return response

    def export_thought_trail(self):
        """Exports the recorded thought process to a JSON file."""
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "mastermind_vettable_thought_trail.json")
        with open(filepath, 'w') as f:
            json.dump(self.thought_trail, f, indent=2)
        logger.info(f"ThoughtTrail has been exported to {filepath}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run the instrumented ArchE system.")
    parser.add_argument("query", type=str, help="The natural language query or directive.")
    args = parser.parse_args()

    wrapper = ArchEInstrumentedWrapper(args.query)
    wrapper.instrument_kno()
    final_response = wrapper.execute_query()

    print("\n--- Final Response ---")
    print(final_response)

if __name__ == "__main__":
    # This check ensures the script runs only when executed directly
    # and that necessary environment variables are set.
    if not os.environ.get("GOOGLE_API_KEY"):
        print("FATAL: The GOOGLE_API_KEY environment variable is not set.")
        print("Please create a .env file in the project root or export the variable.")
        sys.exit(1)
    main() 