"""
RISE Execution Phase - Tool-Based Plan Execution
Implements the execution layer where RISE plans are actually executed using ArchE's cognitive tools.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RISEExecutionPhase:
    """
    Executes RISE-generated plans using ArchE's cognitive tools.
    
    Flow:
    1. Receives execution plan from RISE
    2. Executes tools in the plan (web_search, code_execution, etc.)
    3. Collects results and feeds them into next iteration
    4. Iteratively refines until comprehensive answer is achieved
    """
    
    def __init__(self, workflow_engine, action_registry, spr_manager=None):
        self.workflow_engine = workflow_engine
        self.action_registry = action_registry
        self.spr_manager = spr_manager
        
    def qualify_query_for_execution(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Determine if query qualifies for RISE execution-based answering.
        
        Returns:
            {
                'qualifies': bool,
                'reason': str,
                'execution_complexity': 'simple' | 'moderate' | 'complex',
                'recommended_tools': List[str]
            }
        """
        # Simple heuristics - can be enhanced with LLM-based classification
        query_lower = query.lower()
        
        # Questions that need research/execution
        research_indicators = ['what are', 'how does', 'analyze', 'compare', 'explain', 'why', 'when', 'where']
        # Questions that need computation
        computation_indicators = ['calculate', 'predict', 'forecast', 'simulate', 'model']
        # Questions that need data gathering
        data_indicators = ['find', 'search', 'gather', 'collect', 'research']
        
        qualifies = any(indicator in query_lower for indicator in research_indicators + computation_indicators + data_indicators)
        
        recommended_tools = []
        if any(indicator in query_lower for indicator in research_indicators + data_indicators):
            recommended_tools.append('web_search')
        if any(indicator in query_lower for indicator in computation_indicators):
            recommended_tools.append('execute_code')
            recommended_tools.append('run_prediction')
        
        complexity = 'complex' if len(recommended_tools) > 2 else 'moderate' if len(recommended_tools) > 0 else 'simple'
        
        return {
            'qualifies': qualifies,
            'reason': 'Query requires research, computation, or data gathering' if qualifies else 'Query can be answered directly',
            'execution_complexity': complexity,
            'recommended_tools': recommended_tools
        }
    
    def generate_execution_plan(self, query: str, strategy: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate an execution plan from RISE strategy.
        
        Uses LLM to break down the strategy into concrete tool execution steps.
        
        Returns:
            {
                'execution_steps': List[Dict],
                'expected_outputs': Dict[str, str],
                'iteration_plan': Dict
            }
        """
        from .llm_providers import get_llm_provider
        
        # Get LLM provider
        provider_name = context.get('provider', 'groq') if context else 'groq'
        model = context.get('model', 'llama-3.3-70b-versatile') if context else 'llama-3.3-70b-versatile'
        
        try:
            llm_provider = get_llm_provider(provider_name)
        except:
            logger.warning("Could not get LLM provider for execution planning")
            return {'execution_steps': [], 'error': 'LLM provider unavailable'}
        
        # Format strategy for planning
        strategy_text = str(strategy) if isinstance(strategy, dict) else strategy
        
        planning_prompt = f"""You are an execution planner for ArchE. Your task is to break down the following strategy into concrete, executable steps using ArchE's tools.

QUERY: {query}

STRATEGY:
{strategy_text[:2000]}

AVAILABLE TOOLS:
- web_search: Search the web for information
- execute_code: Run Python code for calculations/analysis
- generate_text_llm: Generate text/analysis
- run_prediction: Run predictive models
- perform_abm: Run agent-based simulations
- perform_causal_inference: Analyze causal relationships
- run_cfp: Compare scenarios using Comparative Fluxual Processing

Generate an execution plan as JSON with this structure:
{{
    "execution_steps": [
        {{
            "step_id": "step_1",
            "tool": "web_search",
            "description": "What to do",
            "inputs": {{"query": "..."}},
            "expected_output": "What we expect to get"
        }},
        ...
    ],
    "iteration_plan": {{
        "max_iterations": 3,
        "convergence_criteria": "When to stop",
        "refinement_strategy": "How to use results for next steps"
    }}
}}

Focus on steps that will actually ANSWER the query: "{query}"
"""
        
        try:
            response = llm_provider.generate(
                prompt=planning_prompt,
                model=model,
                temperature=0.3,
                max_tokens=4096
            )
            
            # Parse JSON from response
            import json
            import re
            
            # Extract JSON from markdown if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                plan_json = json.loads(json_match.group(1))
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    plan_json = json.loads(json_match.group(0))
                else:
                    raise ValueError("No JSON found in response")
            
            return plan_json
            
        except Exception as e:
            logger.error(f"Failed to generate execution plan: {e}")
            return {
                'execution_steps': [],
                'error': str(e),
                'fallback_plan': self._generate_fallback_plan(query, strategy)
            }
    
    def _generate_fallback_plan(self, query: str, strategy: Any) -> Dict[str, Any]:
        """Generate a simple fallback plan if LLM planning fails"""
        return {
            'execution_steps': [
                {
                    'step_id': 'step_1',
                    'tool': 'web_search',
                    'description': f'Search for information about: {query}',
                    'inputs': {'query': query},
                    'expected_output': 'Relevant information to answer the query'
                }
            ],
            'iteration_plan': {
                'max_iterations': 1,
                'convergence_criteria': 'Information gathered',
                'refinement_strategy': 'Use search results directly'
            }
        }
    
    def execute_plan(self, execution_plan: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the plan using ArchE's tools.
        
        Returns:
            {
                'execution_results': Dict[str, Any],
                'iteration_results': List[Dict],
                'final_answer': str,
                'execution_metrics': Dict
            }
        """
        execution_steps = execution_plan.get('execution_steps', [])
        iteration_plan = execution_plan.get('iteration_plan', {})
        max_iterations = iteration_plan.get('max_iterations', 3)
        
        all_results = {}
        iteration_results = []
        accumulated_context = context.copy() if context else {}
        
        logger.info(f"🔧 Executing plan with {len(execution_steps)} steps, max {max_iterations} iterations")
        
        for iteration in range(max_iterations):
            logger.info(f"🔄 Execution Iteration {iteration + 1}/{max_iterations}")
            iteration_result = {
                'iteration': iteration + 1,
                'step_results': {},
                'accumulated_data': {}
            }
            
            # Execute each step
            for step in execution_steps:
                step_id = step.get('step_id', 'unknown')
                tool = step.get('tool', '')
                inputs = step.get('inputs', {})
                description = step.get('description', '')
                
                logger.info(f"  Executing {step_id}: {tool} - {description}")
                
                try:
                    # Get the action function from registry
                    if tool in self.action_registry:
                        action_func = self.action_registry[tool]
                        
                        # Merge inputs with accumulated context
                        merged_inputs = {**accumulated_context, **inputs}
                        
                        # Execute the action
                        result = action_func(**merged_inputs)
                        
                        # Store result
                        iteration_result['step_results'][step_id] = result
                        all_results[step_id] = result
                        
                        # Extract useful data for next steps
                        if isinstance(result, dict):
                            # Try to extract the actual output
                            output = result.get('result', result.get('output', result.get('generated_text', result)))
                            if output:
                                accumulated_context[f'{step_id}_result'] = output
                                accumulated_context['latest_result'] = output
                        
                        logger.info(f"    ✅ {step_id} completed")
                        
                    else:
                        logger.warning(f"    ⚠️ Tool '{tool}' not found in action registry")
                        iteration_result['step_results'][step_id] = {
                            'error': f"Tool '{tool}' not available",
                            'status': 'failed'
                        }
                        
                except Exception as e:
                    logger.error(f"    ❌ {step_id} failed: {e}")
                    iteration_result['step_results'][step_id] = {
                        'error': str(e),
                        'status': 'failed'
                    }
            
            iteration_result['accumulated_data'] = accumulated_context.copy()
            iteration_results.append(iteration_result)
            
            # Check convergence criteria
            if self._check_convergence(iteration_result, iteration_plan, accumulated_context):
                logger.info(f"✅ Convergence criteria met at iteration {iteration + 1}")
                break
        
        # Generate final answer from accumulated results
        final_answer = self._synthesize_final_answer(
            query=context.get('original_query', '') if context else '',
            all_results=all_results,
            iteration_results=iteration_results,
            context=context
        )
        
        return {
            'execution_results': all_results,
            'iteration_results': iteration_results,
            'final_answer': final_answer,
            'execution_metrics': {
                'total_iterations': len(iteration_results),
                'total_steps_executed': sum(len(ir['step_results']) for ir in iteration_results),
                'successful_steps': sum(
                    sum(1 for r in ir['step_results'].values() if isinstance(r, dict) and r.get('status') != 'failed')
                    for ir in iteration_results
                )
            }
        }
    
    def _check_convergence(self, iteration_result: Dict, iteration_plan: Dict, accumulated_context: Dict) -> bool:
        """Check if execution has converged (met criteria to stop)"""
        convergence_criteria = iteration_plan.get('convergence_criteria', '')
        
        # Simple heuristics
        if 'sufficient information' in convergence_criteria.lower():
            # Check if we have substantial results
            total_results = sum(len(ir.get('step_results', {})) for ir in [iteration_result])
            return total_results >= 2
        
        # Default: stop after first iteration unless explicitly told to continue
        return len(iteration_result.get('step_results', {})) > 0
    
    def _synthesize_final_answer(self, query: str, all_results: Dict, iteration_results: List[Dict], context: Dict = None) -> str:
        """
        Synthesize a comprehensive final answer from execution results.
        
        Uses LLM to combine all tool results into a coherent answer to the original query.
        """
        from .llm_providers import get_llm_provider
        
        # Get LLM provider
        provider_name = context.get('provider', 'groq') if context else 'groq'
        model = context.get('model', 'llama-3.3-70b-versatile') if context else 'llama-3.3-70b-versatile'
        
        try:
            llm_provider = get_llm_provider(provider_name)
        except:
            logger.warning("Could not get LLM provider for answer synthesis")
            # Fallback: just concatenate results
            return "\n\n".join([str(r) for r in all_results.values() if r])
        
        # Format results for synthesis
        results_summary = []
        for step_id, result in all_results.items():
            if isinstance(result, dict):
                output = result.get('result', result.get('output', result.get('generated_text', '')))
                if output:
                    results_summary.append(f"{step_id}: {str(output)[:500]}")
        
        synthesis_prompt = f"""You are ArchE. Your task is to synthesize a comprehensive answer to the user's query based on the execution results from various tools.

ORIGINAL QUERY: {query}

EXECUTION RESULTS:
{chr(10).join(results_summary[:10])}

Synthesize a clear, comprehensive answer that:
1. Directly addresses the query: "{query}"
2. Incorporates information from the execution results
3. Is well-structured and easy to understand
4. Provides actionable insights if applicable

Answer:"""
        
        try:
            final_answer = llm_provider.generate(
                prompt=synthesis_prompt,
                model=model,
                temperature=0.4,
                max_tokens=4096
            )
            return final_answer
        except Exception as e:
            logger.error(f"Failed to synthesize final answer: {e}")
            # Fallback: return formatted results
            return f"Based on execution results:\n\n{chr(10).join(results_summary)}"

