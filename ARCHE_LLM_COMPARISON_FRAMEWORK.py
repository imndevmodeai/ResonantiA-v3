#!/usr/bin/env python3
"""
ArchE vs LLM Comparison Framework
Runs novel queries through ArchE's best flows and compares with direct LLM calls

REQUIREMENT: Must be run with arche_env virtual environment activated
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Verify virtual environment
if not os.environ.get('VIRTUAL_ENV') or 'arche_env' not in os.environ.get('VIRTUAL_ENV', ''):
    print("⚠️  WARNING: arche_env virtual environment not detected!")
    print("   Please activate with: source arche_env/bin/activate")
    print("   Current VIRTUAL_ENV:", os.environ.get('VIRTUAL_ENV', 'Not set'))
    print("   Continuing anyway, but errors may occur...\n")

# Add project root to path (same pattern as main.py)
project_root = Path(__file__).resolve().parent
package_dir = project_root / "Three_PointO_ArchE"
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))

# Initialize logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import with error handling - dependencies ARE installed, handle gracefully
RISE_AVAILABLE = False
RISE_Orchestrator = None
IARCompliantWorkflowEngine = None

try:
    from Three_PointO_ArchE.spr_manager import SPRManager
    from Three_PointO_ArchE.llm_providers.groq_provider import GroqProvider
    from Three_PointO_ArchE.llm_providers.multi_key_groq_provider import MultiKeyGroqProvider
    from Three_PointO_ArchE.llm_providers import get_llm_provider
    from Three_PointO_ArchE import config
    
    # Try to import RISE components (may have optional dependencies)
    try:
        from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
        from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
        RISE_AVAILABLE = True
        logger.info("RISE components loaded successfully")
    except (ImportError, ModuleNotFoundError) as e:
        logger.warning(f"RISE components not available (optional dependencies missing): {e}")
        logger.warning("Will use direct Groq comparison only - this is fine for basic testing")
        RISE_AVAILABLE = False
        
except (ImportError, ModuleNotFoundError) as e:
    logger.error(f"Failed to import core components: {e}")
    logger.error(f"Python path: {sys.path[:5]}")
    logger.error(f"Virtual env: {os.environ.get('VIRTUAL_ENV', 'Not set')}")
    # Don't raise - allow framework to work with just direct Groq
    SPRManager = None
    GroqProvider = None
    MultiKeyGroqProvider = None
    config = None

class ArchELLMComparisonFramework:
    """
    Framework for comparing ArchE's cognitive architecture against direct LLM calls
    """
    
    def __init__(self, output_dir: str = "outputs/comparisons"):
        """Initialize the comparison framework"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ArchE components (with fallback if RISE not available)
        logger.info("Initializing ArchE components...")
        
        if SPRManager is None:
            raise RuntimeError("SPRManager not available - core dependencies missing")
        
        spr_file = getattr(config, 'SPR_JSON_FILE', 'knowledge_graph/spr_definitions_tv.json') if config else 'knowledge_graph/spr_definitions_tv.json'
        self.spr_manager = SPRManager(spr_file)
        
        if RISE_AVAILABLE:
            workflows_dir = getattr(config, 'WORKFLOW_DIR', 'workflows')
            self.workflow_engine = IARCompliantWorkflowEngine(
                workflows_dir=workflows_dir,
                spr_manager=self.spr_manager
            )
            
            self.rise_orchestrator = RISE_Orchestrator(
                workflow_engine=self.workflow_engine,
                spr_manager=self.spr_manager
            )
        else:
            self.workflow_engine = None
            self.rise_orchestrator = None
            logger.warning("RISE components not available - will use direct Groq comparison only")
        
        # Initialize direct LLM provider (Groq) - support multiple keys
        try:
            # Try MultiKeyGroqProvider first (supports multiple keys)
            multi_key_provider = MultiKeyGroqProvider()
            if len(multi_key_provider.api_keys) > 0:
                self.llm_provider = multi_key_provider
                logger.info(f"Multi-key Groq provider initialized with {len(multi_key_provider.api_keys)} keys")
            else:
                # Fallback to single key
                api_key = os.environ.get("GROQ_API_KEY")
                if api_key:
                    self.llm_provider = GroqProvider(api_key=api_key)
                    logger.info("Single-key Groq provider initialized")
                else:
                    logger.warning("No GROQ_API_KEY found. Direct LLM comparison will be limited.")
                    self.llm_provider = None
        except Exception as e:
            logger.warning(f"Failed to initialize multi-key Groq provider: {e}. Trying single key...")
            try:
                api_key = os.environ.get("GROQ_API_KEY")
                if api_key:
                    self.llm_provider = GroqProvider(api_key=api_key)
                    logger.info("Single-key Groq provider initialized (fallback)")
                else:
                    logger.warning("No GROQ_API_KEY found. Direct LLM comparison will be limited.")
                    self.llm_provider = None
            except Exception as e2:
                logger.error(f"Failed to initialize Groq provider: {e2}")
                self.llm_provider = None
        
        logger.info("Comparison framework initialized")
    
    def run_direct_llm_query(self, query: str, model: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
        """
        Run query directly through LLM without ArchE architecture
        """
        if not self.llm_provider:
            return {
                "status": "error",
                "error": "No LLM provider available",
                "response": None,
                "time_ms": 0
            }
        
        start_time = time.time()
        
        try:
            # Simple direct prompt
            prompt = f"""You are an expert analyst. Please provide a comprehensive analysis of the following query:

{query}

Provide:
1. A clear, structured analysis
2. Key insights and findings
3. Actionable recommendations
4. Any relevant considerations or limitations

Be thorough, accurate, and insightful."""
            
            # GroqProvider uses generate() method, not generate_text()
            response = self.llm_provider.generate(
                prompt=prompt,
                model=model,
                temperature=0.7,
                max_tokens=8192
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return {
                "status": "success",
                "response": response,
                "model": model,
                "time_ms": elapsed_ms,
                "method": "direct_llm"
            }
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Direct LLM query failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "response": None,
                "time_ms": elapsed_ms,
                "method": "direct_llm"
            }
    
    def run_arche_rise_query(self, query: str, model: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
        """
        Run query through ArchE's RISE orchestrator (full cognitive architecture)
        """
        if not self.rise_orchestrator:
            return {
                "status": "error",
                "error": "RISE orchestrator not available (dependencies issue)",
                "response": None,
                "time_ms": 0,
                "method": "arche_rise"
            }
        
        start_time = time.time()
        
        try:
            context = {
                "model": model,
                "provider": "groq"
            }
            
            result = self.rise_orchestrator.process_query(
                problem_description=query,
                context=context,
                model=model
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # NEW: Prefer execution answer if available (from Phase E - tool execution)
            execution_phase = result.get("execution_phase", {})
            execution_answer = execution_phase.get("execution_answer")
            
            if execution_answer:
                # Use execution-based answer (from actual tool execution)
                final_response = execution_answer
                response_source = "execution_phase"
                logger.info("✅ Using execution-based answer from Phase E")
            else:
                # Fallback to final strategy (from planning phases)
                final_strategy = result.get("final_strategy", result.get("final_answer", ""))
                if not final_strategy and isinstance(result, dict):
                    # Try to find any strategy text in the result
                    for key in ["strategy", "analysis", "response", "output"]:
                        if key in result:
                            final_strategy = result[key]
                            break
                final_response = final_strategy or str(result)
                response_source = "final_strategy"
                logger.info("ℹ️ Using final strategy (no execution answer available)")
            
            return {
                "status": "success",
                "response": final_response,
                "response_source": response_source,  # NEW: Track where response came from
                "full_result": result,
                "time_ms": elapsed_ms,
                "method": "arche_rise",
                "phases_completed": result.get("phases_completed", []),
                "session_id": result.get("session_id", "unknown"),
                "execution_phase_used": bool(execution_answer)  # NEW: Indicate if execution phase was used
            }
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"ArchE RISE query failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "response": None,
                "time_ms": elapsed_ms,
                "method": "arche_rise"
            }
    
    def run_arche_workflow_query(self, query: str, workflow_name: str = "knowledge_scaffolding.json") -> Dict[str, Any]:
        """
        Run query through a specific ArchE workflow
        """
        start_time = time.time()
        
        try:
            initial_context = {
                "problem_description": query,
                "user_query": query
            }
            
            result = self.workflow_engine.run_workflow(
                workflow_name=workflow_name,
                initial_context=initial_context
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Extract response from workflow result
            response = result.get("final_result", result.get("output", str(result)))
            
            return {
                "status": "success",
                "response": response,
                "full_result": result,
                "time_ms": elapsed_ms,
                "method": f"arche_workflow_{workflow_name}",
                "workflow": workflow_name
            }
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"ArchE workflow query failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "response": None,
                "time_ms": elapsed_ms,
                "method": f"arche_workflow_{workflow_name}"
            }
    
    def compare_results(self, query: str, direct_llm_result: Dict, arche_result: Dict) -> Dict[str, Any]:
        """
        Compare results from direct LLM vs ArchE
        """
        comparison = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "direct_llm": {
                "status": direct_llm_result.get("status"),
                "time_ms": direct_llm_result.get("time_ms", 0),
                "response_length": len(str(direct_llm_result.get("response", ""))) if direct_llm_result.get("response") else 0,
                "has_error": direct_llm_result.get("status") == "error",
                "error": direct_llm_result.get("error")
            },
            "arche": {
                "status": arche_result.get("status"),
                "time_ms": arche_result.get("time_ms", 0),
                "response_length": len(str(arche_result.get("response", ""))) if arche_result.get("response") else 0,
                "has_error": arche_result.get("status") == "error",
                "error": arche_result.get("error"),
                "method": arche_result.get("method", "unknown")
            },
            "metrics": {
                "time_difference_ms": arche_result.get("time_ms", 0) - direct_llm_result.get("time_ms", 0),
                "time_ratio": (arche_result.get("time_ms", 0) / direct_llm_result.get("time_ms", 1)) if direct_llm_result.get("time_ms", 0) > 0 else 0,
                "response_length_ratio": (arche_result.get("response_length", 0) / direct_llm_result.get("response_length", 1)) if direct_llm_result.get("response_length", 0) > 0 else 0
            }
        }
        
        return comparison
    
    def run_comparison(self, query: str, arche_method: str = "rise", model: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
        """
        Run a complete comparison: direct LLM vs ArchE
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Running comparison for query: {query[:100]}...")
        logger.info(f"{'='*80}\n")
        
        # Run direct LLM
        logger.info(f"Running direct Groq LLM query (model: {model})...")
        direct_result = self.run_direct_llm_query(query, model=model)
        logger.info(f"Direct LLM completed in {direct_result.get('time_ms', 0):.2f}ms")
        
        # Run ArchE
        logger.info(f"Running ArchE query (method: {arche_method}, model: {model})...")
        if arche_method == "rise":
            arche_result = self.run_arche_rise_query(query, model=model)
        elif arche_method.startswith("workflow:"):
            workflow_name = arche_method.split(":", 1)[1]
            arche_result = self.run_arche_workflow_query(query, workflow_name)
        else:
            arche_result = self.run_arche_rise_query(query, model=model)
        
        logger.info(f"ArchE completed in {arche_result.get('time_ms', 0):.2f}ms")
        
        # Compare results
        comparison = self.compare_results(query, direct_result, arche_result)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c for c in query[:50] if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        filename = f"comparison_{timestamp}_{safe_query}.json"
        filepath = self.output_dir / filename
        
        full_results = {
            "comparison": comparison,
            "direct_llm_full": direct_result,
            "arche_full": arche_result
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(full_results, f, indent=2, default=str)
        
        logger.info(f"\nResults saved to: {filepath}")
        logger.info(f"\nComparison Summary:")
        logger.info(f"  Direct LLM: {comparison['direct_llm']['time_ms']:.2f}ms, Status: {comparison['direct_llm']['status']}")
        logger.info(f"  ArchE: {comparison['arche']['time_ms']:.2f}ms, Status: {comparison['arche']['status']}")
        logger.info(f"  Time difference: {comparison['metrics']['time_difference_ms']:.2f}ms")
        logger.info(f"  Time ratio: {comparison['metrics']['time_ratio']:.2f}x")
        
        return full_results
    
    def run_batch_comparison(self, queries: List[str], arche_method: str = "rise", model: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
        """
        Run comparisons for multiple queries
        """
        results = []
        
        for i, query in enumerate(queries, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Query {i}/{len(queries)}")
            logger.info(f"{'='*80}")
            
            try:
                result = self.run_comparison(query, arche_method, model=model)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to run comparison for query {i}: {e}")
                results.append({
                    "query": query,
                    "error": str(e)
                })
        
        # Save batch summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_dir / f"batch_comparison_summary_{timestamp}.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(queries),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Batch comparison complete!")
        logger.info(f"  Total queries: {len(queries)}")
        logger.info(f"  Successful: {summary['successful']}")
        logger.info(f"  Failed: {summary['failed']}")
        logger.info(f"  Summary saved to: {summary_file}")
        logger.info(f"{'='*80}\n")
        
        return summary


def main():
    """Main entry point for comparison framework"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ArchE vs LLM Comparison Framework")
    parser.add_argument("--query", type=str, help="Single query to compare")
    parser.add_argument("--queries-file", type=str, help="JSON file with list of queries")
    parser.add_argument("--arche-method", type=str, default="rise", 
                       help="ArchE method: 'rise' or 'workflow:workflow_name.json'")
    parser.add_argument("--model", type=str, default="llama-3.3-70b-versatile",
                       help="LLM model to use (default: llama-3.3-70b-versatile). Note: Some models may be blocked - try llama-3.3-70b-versatile or llama-3.1-70b-versatile")
    parser.add_argument("--output-dir", type=str, default="outputs/comparisons",
                       help="Output directory for results")
    
    args = parser.parse_args()
    
    framework = ArchELLMComparisonFramework(output_dir=args.output_dir)
    
    if args.queries_file:
        # Batch mode
        with open(args.queries_file, 'r') as f:
            queries = json.load(f)
        framework.run_batch_comparison(queries, args.arche_method, model=args.model)
    elif args.query:
        # Single query mode
        framework.run_comparison(args.query, args.arche_method, model=args.model)
    else:
        # Interactive mode with sample queries
        print("\n" + "="*80)
        print("ArchE vs LLM Comparison Framework")
        print("="*80)
        print("\nSample novel queries for testing:")
        print("1. 'How would you design a sustainable city for 10 million people?'")
        print("2. 'What are the ethical implications of AI consciousness?'")
        print("3. 'Analyze the potential impact of quantum computing on cryptography'")
        print("4. 'Design a strategy for reducing global carbon emissions by 50% in 10 years'")
        print("5. 'What would happen if we discovered intelligent life on Mars?'")
        print("\nEnter a query to compare, or 'quit' to exit:")
        
        while True:
            query = input("\nQuery: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if query:
                framework.run_comparison(query, args.arche_method, model=args.model)


if __name__ == "__main__":
    main()

