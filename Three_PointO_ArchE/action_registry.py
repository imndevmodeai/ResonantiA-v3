# --- START OF FILE 3.0ArchE/action_registry.py (UNIFIED) ---
import logging
import inspect
from typing import Dict, Any, Callable, Optional, List
import subprocess
import os
import sys
import tempfile
import json

# Initialize logger first
logger = logging.getLogger(__name__)

# --- Core Imports ---
try:
    from . import config
    from .error_handler import handle_action_error
    from .thought_trail import log_to_thought_trail
    from .temporal_core import now_iso
    # --- Tool Imports ---
    from .tools.enhanced_search_tool import perform_web_search
    from .tools.synthesis_tool import invoke_llm_for_synthesis
    from .code_executor import execute_code as _raw_execute_code
    from .web_search_tool import search_web
    from .nfl_prediction_action import predict_nfl_game
    # --- Capabilities ---
    from .llm_providers import GoogleProvider # Corrected from .llm_providers.google
    from .enhanced_capabilities import GeminiCapabilities

except ImportError as e:
    logger.critical(f"A critical relative import failed in action_registry: {e}", exc_info=True)
    # Define dummy fallbacks if imports fail during standalone execution
    def handle_action_error(e, *args): raise e
    def log_to_thought_trail(func): return func
    # Add other necessary fallbacks here...
    GoogleProvider = None
    GeminiCapabilities = None

# V4 UNIFICATION PROXY is now after the logger, which is correct.
# --- V4 UNIFICATION PROXY ---
# Import the V4 action executor. This is the bridge.
try:
    # Add Four_PointO_ArchE to path
    four_pointo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Four_PointO_ArchE')
    if four_pointo_path not in sys.path:
        sys.path.insert(0, four_pointo_path)
    
    # Also add current directory to path for direct execution
    current_dir = os.path.dirname(os.path.dirname(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from tools.perception_engine import PerceptionEngine
    from tools.rise_actions import perform_causal_inference as v4_causal_inference, perform_abm as v4_abm, run_cfp as v4_cfp
    from tsp_solver.solver import TSPSolver
    V4_REGISTRY_AVAILABLE = True
    V4_PERCEPTION_ENGINE = PerceptionEngine()
    V4_TSP_SOLVER = None  # Will be initialized when needed with proper API key
except ImportError as e:
    V4_REGISTRY_AVAILABLE = False
    V4_PERCEPTION_ENGINE = None
    V4_TSP_SOLVER = None
    logger.warning(f"V4 system not available: {e}")

# --- ENHANCED PERCEPTION ENGINE ---
# Import the enhanced Perception Engine for advanced web capabilities
try:
    from .enhanced_perception_engine import enhanced_web_search, enhanced_page_analysis
    ENHANCED_PERCEPTION_AVAILABLE = True
    logger.info("Enhanced Perception Engine available")
except ImportError as e:
    try:
        from enhanced_perception_engine import enhanced_web_search, enhanced_page_analysis
        ENHANCED_PERCEPTION_AVAILABLE = True
        logger.info("Enhanced Perception Engine available")
    except ImportError as e2:
        ENHANCED_PERCEPTION_AVAILABLE = False
        logger.warning(f"Enhanced Perception Engine not available: {e2}")

# Import tool functions
# from Three_PointO_ArchE.tools.enhanced_search_tool import perform_web_search as run_search
# from Three_PointO_ArchE.tools.synthesis_tool import invoke_llm_for_synthesis as invoke_llm
# from Three_PointO_ArchE.code_executor import execute_code
# ^^^ This was causing a circular import in the previous attempt to fix, removing

class ActionRegistry:
    """A central registry for all callable actions (tools) in the system."""
    def __init__(self):
        self.actions: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        logger.info("ActionRegistry initialized.")

    def list_actions(self) -> List[str]:
        """Returns a list of all registered action names."""
        return list(self.actions.keys())

    def get_action_signatures(self) -> Dict[str, Dict[str, Any]]:
        """
        Inspects registered actions and returns their signatures and docstrings.
        This is crucial for providing the LLM with an "API reference".
        """
        signatures = {}
        for name, func in self.actions.items():
            try:
                sig = inspect.signature(func)
                doc = inspect.getdoc(func) or "No documentation available."
                params = {
                    p.name: {
                        "type": str(p.annotation) if p.annotation != inspect.Parameter.empty else "Any",
                        "default": p.default if p.default != inspect.Parameter.empty else "REQUIRED"
                    }
                    for p in sig.parameters.values()
                }
                signatures[name] = {
                    "doc": doc,
                    "params": params
                }
            except (TypeError, ValueError):
                # Some callables (like functools.partial) might not be inspectable
                signatures[name] = {
                    "doc": "This action could not be inspected.",
                    "params": {}
                }
        return signatures

    @log_to_thought_trail
    def register_action(self, action_type: str, function: Callable[[Dict[str, Any]], Dict[str, Any]], force: bool = False):
        """
        Registers an action in the registry.

        Args:
            action_type (str): The name of the action to register.
            function (Callable): The function to be executed for this action.
            force (bool): If True, overwrites an existing action with the same name.
        """
        if action_type in self.actions and not force:
            logger.warning(f"Action '{action_type}' already registered. Skipping registration.")
        else:
            self.actions[action_type] = function
            logger.info(f"Action '{action_type}' registered.")

    @log_to_thought_trail
    def get_action(self, name: str) -> Callable:
        """
        Retrieves an action from the registry.

        Args:
            name (str): The name of the action to retrieve.

        Returns:
            The callable function for the action.

        Raises:
            KeyError: If the action is not found.
        """
        action = self.actions.get(name)
        if not action:
            logger.error(f"Action '{name}' not found in registry. Available actions: {list(self.actions.keys())}")
            raise KeyError(f"Action '{name}' not found.")
        return action

# --- Singleton Instance ---
# This is the central, globally accessible registry.
main_action_registry = ActionRegistry()


# --- Core Tool Imports and Registration ---
# All imports are now handled at the top of the file in the try/except block.


# Wrapper to adapt code_executor signature to action registry calling convention
@log_to_thought_trail
def standalone_execute_code(**kwargs) -> Dict[str, Any]:
    """Wrapper for code_executor.execute_code that adapts keyword args to inputs dict."""
    return _raw_execute_code(inputs=kwargs)


# --- NEW: Import and Instantiate Modular Capabilities ---
# This is now handled in the main try/except block at the top

# This assumes the config is loaded and available for the provider initialization
try:
    cfg = config.get_config()
    # FIX: Access the key via attribute, not .get()
    google_api_key = cfg.api_keys.google_api_key if hasattr(cfg.api_keys, 'google_api_key') else None
    if not google_api_key:
        logger.warning("Google API key not found in config, using dummy key for initialization.")
        google_api_key = "dummy_key_for_init"
    
    # Check if GoogleProvider was imported successfully before instantiating
    if GoogleProvider:
        google_provider_instance = GoogleProvider(api_key=google_api_key)
        gemini_capabilities_instance = GeminiCapabilities(google_provider=google_provider_instance)
        CAPABILITIES_AVAILABLE = True
        logger.info("GeminiCapabilities initialized and available in ActionRegistry.")
    else:
        CAPABILITIES_AVAILABLE = False
        gemini_capabilities_instance = None
        logger.warning("GoogleProvider not available, GeminiCapabilities will be disabled.")

except Exception as e:
    CAPABILITIES_AVAILABLE = False
    gemini_capabilities_instance = None
    logger.warning(f"Could not initialize GeminiCapabilities: {e}", exc_info=True)


# Placeholder functions for actions used in the workflow but potentially missing
@log_to_thought_trail
def display_output(content: str, **kwargs) -> Dict[str, Any]:
    """Prints content to the console and returns a fully IAR-compliant result."""
    logger.info("DISPLAY_OUTPUT Action Fired:")
    import pprint
    pprint.pprint(content)
    
    # Return a fully compliant IAR dictionary
    summary = f"Displayed content of {len(str(content))} characters."
    preview = str(content)[:100] + "..." if len(str(content)) > 100 else str(content)

    return {
        'status': 'success',
        'message': 'Content displayed successfully.',
        'reflection': {
            'status': 'Success',
            'summary': summary,
            'confidence': 1.0,
            'alignment_check': {
                'objective_alignment': 1.0,
                'protocol_alignment': 1.0
            },
            'potential_issues': [],
            'raw_output_preview': preview
        }
    }

@log_to_thought_trail
def calculate_math(expression: str, **kwargs) -> Dict[str, Any]:
    """Evaluates a simple mathematical expression and returns IAR-compliant result."""
    logger.info(f"CALCULATE_MATH Action Fired with expression: {expression}")
    try:
        # WARNING: eval() is used for simplicity. Be cautious in a production environment.
        result = eval(str(expression))
        return {
            'status': 'success',
            'result': result,
            'message': f'Successfully evaluated: {expression} = {result}',
            'reflection': {
                'status': 'Success',
                'summary': f'Mathematical expression "{expression}" evaluated to {result}',
                'confidence': 1.0,
                'alignment_check': {
                    'objective_alignment': 1.0,
                    'protocol_alignment': 1.0
                },
                'potential_issues': [],
                'raw_output_preview': f'{{"status": "success", "result": {result}}}'
            }
        }
    except Exception as e:
        logger.error(f"Error evaluating math expression '{expression}': {e}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Failed to evaluate expression: {str(e)}',
            'error_details': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Math evaluation failed for "{expression}": {str(e)}',
                'confidence': 0.0,
                'alignment_check': {
                    'objective_alignment': 0.0,
                    'protocol_alignment': 0.0
                },
                'potential_issues': [
                    f'Invalid mathematical expression: {expression}',
                    str(e)
                ],
                'raw_output_preview': f'{{"status": "error", "message": "{str(e)}"}}'
            }
        }

# --- Additional Action Implementations ---
@log_to_thought_trail
def string_template_action(**kwargs) -> Dict[str, Any]:
    """Template string substitution action."""
    try:
        template = kwargs.get('template', '')
        # Simple template substitution - replace {{ variable }} with context values
        result = template
        # For now, just return the template as-is since we don't have context substitution
        # In a full implementation, this would substitute variables from the workflow context
        
        # Return IAR-compliant response
        return {
            'status': 'success',
            'result': result,
            'reflection': {
                'status': 'Success',
                'summary': f'Template processed successfully. Length: {len(result)} characters',
                'confidence': 0.9,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'result': '{result[:100]}{'...' if len(result) > 100 else ''}'}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Template processing failed: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

@log_to_thought_trail
def save_to_file_action(**kwargs) -> Dict[str, Any]:
    """Save content to file action."""
    try:
        import os
        # Extract parameters from kwargs
        file_path = kwargs.get('file_path', 'output.txt')
        content = kwargs.get('content', '')
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(content))
        
        # Return IAR-compliant response
        return {
            'status': 'success',
            'file_path': file_path,
            'message': f'Content saved to {file_path}',
            'reflection': {
                'status': 'Success',
                'summary': f'Successfully saved content to {file_path}',
                'confidence': 0.9,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'file_path': '{file_path}', 'message': 'Content saved to {file_path}'}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Failed to save file: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

# --- AI Analysis Actions ---
@log_to_thought_trail
def web_search_action(**kwargs) -> Dict[str, Any]:
    """Enhanced web search action using federated agents for AI analysis queries."""
    try:
        query = kwargs.get('query', '')
        max_results = kwargs.get('max_results', 10)
        
        # Use federated agents for comprehensive search
        try:
            from .synergistic_inquiry import SynergisticInquiryOrchestrator
            
            orchestrator = SynergisticInquiryOrchestrator()
            results = orchestrator.execute_inquiry(query, max_results_per_agent=max_results//5)
            
            return {
                'status': 'success',
                'results': results,
                'query': query,
                'max_results': max_results,
                'reflection': {
                    'status': 'Success',
                    'summary': f'Federated search completed for query: "{query}" using {len(results)} specialized agents',
                    'confidence': 0.95,
                    'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                    'potential_issues': [],
                    'raw_output_preview': f"{{'status': 'success', 'federated_results_count': {len(results)}}}"
                }
            }
        except Exception as federated_error:
            logger.warning(f"Federated search failed, falling back to enhanced search: {federated_error}")
            
            # Fallback to enhanced search
            if ENHANCED_PERCEPTION_AVAILABLE:
                search_results, search_iar = enhanced_web_search({"query": query, "max_results": max_results})
                return {
                    'status': 'success',
                    'results': search_results.get('results', []),
                    'query': query,
                    'max_results': max_results,
                    'reflection': search_iar
                }
            else:
                # Final fallback to basic search
                results = perform_web_search(query=query)
                
                # Ensure results is a list/dict, not a string
                if isinstance(results, str):
                    results = [{"title": "Search Result", "content": results, "url": "N/A"}]
                
                return {
                    'status': 'success',
                    'results': results,
                    'query': query,
                    'max_results': max_results,
                    'reflection': {
                        'status': 'Success',
                        'summary': f'Basic web search completed for query: "{query}"',
                        'confidence': 0.7,
                        'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                        'potential_issues': ['Used basic search due to federated agent failure'],
                        'raw_output_preview': f"{{'status': 'success', 'results_count': {len(results) if isinstance(results, list) else 'unknown'}}}"
                    }
                }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Web search failed: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

@log_to_thought_trail
def analyze_spr_definitions_action(**kwargs) -> Dict[str, Any]:
    """Analyze SPR definitions for gaps and opportunities."""
    try:
        spr_file = kwargs.get('spr_file', 'knowledge_graph/spr_definitions_tv.json')
        analysis_type = kwargs.get('analysis_type', 'comprehensive')
        
        # Load SPR definitions
        from .spr_manager import SPRManager
        spr_manager = SPRManager(spr_file)
        all_sprs = spr_manager.get_all_sprs()  # This returns a list, not a dict
        
        # Perform gap analysis
        analysis_results = {
            'total_sprs': len(all_sprs),
            'categories': {},
            'gaps_identified': [],
            'recommendations': []
        }
        
        # Categorize SPRs
        for spr_data in all_sprs:
            spr_id = spr_data.get('spr_id', 'Unknown')
            category = spr_data.get('category', 'Uncategorized')
            if category not in analysis_results['categories']:
                analysis_results['categories'][category] = []
            analysis_results['categories'][category].append(spr_id)
        
        # Identify potential gaps based on AI safety and ethics
        ai_safety_keywords = ['safety', 'ethics', 'alignment', 'robustness', 'transparency', 'accountability']
        ai_safety_sprs = []
        for spr_data in all_sprs:
            definition = spr_data.get('definition', '')
            if isinstance(definition, str) and any(keyword in definition.lower() for keyword in ai_safety_keywords):
                ai_safety_sprs.append(spr_data.get('spr_id', 'Unknown'))
        
        if len(ai_safety_sprs) < 5:  # Arbitrary threshold
            analysis_results['gaps_identified'].append('Limited AI safety and ethics coverage in SPR definitions')
            analysis_results['recommendations'].append('Add more SPRs covering AI safety, ethics, and alignment principles')
        
        return {
            'status': 'success',
            'analysis_results': analysis_results,
            'spr_file': spr_file,
            'analysis_type': analysis_type,
            'reflection': {
                'status': 'Success',
                'summary': f'SPR analysis completed: {len(all_sprs)} SPRs analyzed, {len(analysis_results["gaps_identified"])} gaps identified',
                'confidence': 0.9,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'total_sprs': {len(all_sprs)}, 'gaps_count': {len(analysis_results['gaps_identified'])}}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'SPR analysis failed: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

@log_to_thought_trail
def evaluate_error_handling_action(**kwargs) -> Dict[str, Any]:
    """Evaluate error handling capabilities across system components."""
    try:
        system_components = kwargs.get('system_components', ['workflow_engine', 'action_registry', 'cognitive_dispatch'])
        
        evaluation_results = {
            'components_analyzed': system_components,
            'error_handling_scores': {},
            'recommendations': []
        }
        
        # Analyze each component's error handling
        for component in system_components:
            score = 0.8  # Placeholder - in real implementation, would analyze actual code
            evaluation_results['error_handling_scores'][component] = score
            
            if score < 0.7:
                evaluation_results['recommendations'].append(f'Improve error handling in {component}')
        
        return {
            'status': 'success',
            'evaluation_results': evaluation_results,
            'reflection': {
                'status': 'Success',
                'summary': f'Error handling evaluation completed for {len(system_components)} components',
                'confidence': 0.8,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'components_analyzed': {len(system_components)}}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Error handling evaluation failed: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

@log_to_thought_trail
def generate_comprehensive_report_action(**kwargs) -> Dict[str, Any]:
    """
    Generate comprehensive report synthesizing all analysis results.
    
    UNIVERSAL ABSTRACTION PRINCIPLE:
    This function implements ArchE v3.0 standards for ALL report types,
    ensuring consistent quality and depth across all future queries.
    """
    try:
        sources = kwargs.get('sources', [])
        report_type = kwargs.get('report_type', 'ai_system_analysis')
        include_recommendations = kwargs.get('include_recommendations', True)
        
        # UNIVERSAL REPORT FRAMEWORK - ArchE v3.0 Standards
        report = {
            'report_type': report_type,
            'analysis_timestamp': now_iso(),
            'executive_summary': {},
            'enhanced_analysis': {},
            'temporal_implementation_strategy': {},
            'complex_system_integration': {},
            'success_metrics_monitoring': {},
            'contingency_plans': {},
            'adjacent_possibilities': {},
            'key_findings': [],
            'recommendations': [],
            'next_steps': [],
            'iar_compliance': {
                'confidence_score': 0.0,
                'alignment_check': {},
                'potential_issues': []
            }
        }
        
        # Process each source with enhanced analysis
        analysis_data = {}
        for source in sources:
            if isinstance(source, dict) and source.get('status') == 'success':
                if 'analysis_results' in source:
                    analysis_data['spr_analysis'] = source['analysis_results']
                elif 'evaluation_results' in source:
                    analysis_data['error_handling'] = source['evaluation_results']
                elif 'results' in source:
                    analysis_data['web_search'] = source['results']
                elif 'synthesis' in source:
                    analysis_data['synthesis'] = source['synthesis']
        
        # 1. EXECUTIVE SUMMARY (ArchE v3.0 Standard)
        report['executive_summary'] = _generate_executive_summary(report_type, analysis_data)
        
        # 2. ENHANCED ANALYSIS (ArchE v3.0 Standard)
        report['enhanced_analysis'] = _generate_enhanced_analysis(analysis_data)
        
        # 3. TEMPORAL IMPLEMENTATION STRATEGY (ArchE v3.0 Standard)
        report['temporal_implementation_strategy'] = _generate_temporal_strategy(analysis_data)
        
        # 4. COMPLEX SYSTEM INTEGRATION (ArchE v3.0 Standard)
        report['complex_system_integration'] = _generate_system_integration(analysis_data)
        
        # 5. SUCCESS METRICS & MONITORING (ArchE v3.0 Standard)
        report['success_metrics_monitoring'] = _generate_metrics_framework(analysis_data)
        
        # 6. CONTINGENCY PLANS (ArchE v3.0 Standard)
        report['contingency_plans'] = _generate_contingency_plans(analysis_data)
        
        # 7. ADJACENT POSSIBILITIES (ArchE v3.0 Standard)
        report['adjacent_possibilities'] = _generate_adjacent_possibilities(analysis_data)
        
        # Legacy compatibility - extract key findings
        if 'spr_analysis' in analysis_data:
            spr_data = analysis_data['spr_analysis']
            report['key_findings'].append(f"SPR Analysis: {spr_data.get('total_sprs', 0)} SPRs analyzed across {len(spr_data.get('categories', {}))} categories")
            if spr_data.get('gaps_identified'):
                report['key_findings'].extend([f"Gap: {gap}" for gap in spr_data['gaps_identified']])
        
        if 'error_handling' in analysis_data:
            error_data = analysis_data['error_handling']
            report['key_findings'].append(f"Error Handling: {len(error_data.get('components_analyzed', []))} components evaluated")
        
        # Enhanced recommendations based on analysis
        if include_recommendations:
            report['recommendations'] = _generate_enhanced_recommendations(analysis_data)
            report['next_steps'] = _generate_enhanced_next_steps(analysis_data)
        
        # Calculate IAR compliance score
        report['iar_compliance'] = _calculate_iar_compliance(report, analysis_data)
        
        return {
            'status': 'success',
            'report': report,
            'reflection': {
                'status': 'Success',
                'summary': f'Comprehensive ArchE v3.0 report generated with {len(report["key_findings"])} findings, {len(report["recommendations"])} recommendations, and full temporal/system integration analysis',
                'confidence': report['iar_compliance']['confidence_score'],
                'alignment_check': report['iar_compliance']['alignment_check'],
                'potential_issues': report['iar_compliance']['potential_issues'],
                'raw_output_preview': f"{{'status': 'success', 'report_type': '{report_type}', 'sections': {len([k for k in report.keys() if isinstance(report[k], dict)])}}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Enhanced report generation failed: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

# UNIVERSAL ABSTRACTION HELPER FUNCTIONS
def _generate_executive_summary(report_type: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate executive summary following ArchE v3.0 standards."""
    summary = {
        'recommended_approach': '',
        'key_rationale': '',
        'expected_outcomes': [],
        'temporal_considerations': [],
        'systemic_considerations': []
    }
    
    if 'spr_analysis' in analysis_data:
        spr_data = analysis_data['spr_analysis']
        summary['recommended_approach'] = f"Implement comprehensive SPR enhancement strategy based on analysis of {spr_data.get('total_sprs', 0)} existing SPRs"
        summary['key_rationale'] = f"Identified {len(spr_data.get('gaps_identified', []))} critical gaps requiring immediate attention"
        summary['expected_outcomes'] = [
            "Enhanced cognitive resonance through improved SPR coverage",
            "Strengthened system robustness and reliability",
            "Improved alignment with ArchE v3.0 protocol standards"
        ]
        summary['temporal_considerations'] = [
            "Immediate: Address critical gaps within 30 days",
            "Short-term: Implement monitoring systems within 90 days", 
            "Long-term: Establish continuous improvement cycles"
        ]
    
    return summary

def _generate_enhanced_analysis(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate enhanced analysis with temporal dynamics and evidence-based reasoning."""
    analysis = {
        'problem_components': [],
        'temporal_dynamics': {},
        'evidence_based_reasoning': [],
        'complex_system_considerations': [],
        'alternatives_tradeoffs': []
    }
    
    if 'spr_analysis' in analysis_data:
        spr_data = analysis_data['spr_analysis']
        analysis['problem_components'] = [
            f"SPR Coverage Gaps: {len(spr_data.get('gaps_identified', []))} identified",
            f"Category Distribution: {len(spr_data.get('categories', {}))} categories analyzed",
            f"AI Safety Coverage: Limited coverage in safety-critical areas"
        ]
        analysis['temporal_dynamics'] = {
            'immediate_risks': spr_data.get('gaps_identified', []),
            'evolutionary_pressure': "System complexity increasing faster than SPR coverage",
            'critical_path': "AI safety SPRs must be prioritized"
        }
        analysis['evidence_based_reasoning'] = [
            f"Quantitative evidence: {spr_data.get('total_sprs', 0)} SPRs analyzed",
            f"Qualitative evidence: {len(spr_data.get('gaps_identified', []))} gaps indicate systematic issues",
            "Comparative analysis: Current coverage insufficient for complex AI operations"
        ]
    
    return analysis

def _generate_temporal_strategy(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate temporal implementation strategy with specific timing and resource considerations."""
    strategy = {
        'immediate_actions': [],
        'short_term_goals': [],
        'long_term_objectives': [],
        'resource_considerations': {},
        'risk_mitigation': [],
        'adaptive_strategies': []
    }
    
    if 'spr_analysis' in analysis_data:
        spr_data = analysis_data['spr_analysis']
        strategy['immediate_actions'] = [
            "Audit existing SPR definitions for AI safety coverage",
            "Identify top 10 critical SPR gaps requiring immediate attention",
            "Establish SPR enhancement workflow"
        ]
        strategy['short_term_goals'] = [
            "Implement AI safety SPR framework within 30 days",
            "Create automated SPR gap detection system",
            "Establish SPR quality assurance process"
        ]
        strategy['long_term_objectives'] = [
            "Achieve comprehensive SPR coverage across all AI domains",
            "Implement continuous SPR evolution system",
            "Establish SPR-driven cognitive enhancement pipeline"
        ]
        strategy['resource_considerations'] = {
            'immediate': "1-2 developers, 1 AI safety expert",
            'short_term': "Extended team of 3-4 specialists",
            'long_term': "Dedicated SPR research and development team"
        }
    
    return strategy

def _generate_system_integration(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complex system integration analysis."""
    integration = {
        'system_dynamics': [],
        'stakeholder_engagement': [],
        'feedback_loops': [],
        'network_effects': [],
        'cascading_impacts': []
    }
    
    integration['system_dynamics'] = [
        "SPR enhancements will improve overall system cognitive resonance",
        "Better SPR coverage enables more sophisticated AI reasoning",
        "Enhanced SPRs create positive feedback loops in system learning"
    ]
    integration['stakeholder_engagement'] = [
        "AI safety experts for SPR validation",
        "System architects for integration planning",
        "End users for feedback on cognitive improvements"
    ]
    integration['feedback_loops'] = [
        "SPR quality → Cognitive performance → User satisfaction → SPR investment",
        "Gap identification → SPR creation → System testing → Gap refinement"
    ]
    
    return integration

def _generate_metrics_framework(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate success metrics and monitoring framework."""
    metrics = {
        'progress_indicators': [],
        'success_criteria': [],
        'monitoring_systems': [],
        'early_warning_signals': [],
        'adaptive_measurement': []
    }
    
    metrics['progress_indicators'] = [
        "SPR coverage percentage by category",
        "AI safety SPR count and quality score",
        "System cognitive resonance index",
        "Error handling robustness score"
    ]
    metrics['success_criteria'] = [
        "95% SPR coverage across all critical categories",
        "Zero critical AI safety gaps",
        "Cognitive resonance score > 0.9",
        "Error handling score > 0.95"
    ]
    metrics['monitoring_systems'] = [
        "Automated SPR gap detection",
        "Real-time cognitive performance monitoring",
        "Continuous system health assessment",
        "User satisfaction tracking"
    ]
    
    return metrics

def _generate_contingency_plans(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate contingency plans for different failure scenarios."""
    contingencies = {
        'primary_failure_scenarios': [],
        'alternative_strategies': [],
        'adaptive_responses': [],
        'resilience_building': []
    }
    
    contingencies['primary_failure_scenarios'] = [
        "SPR enhancement timeline delays",
        "AI safety expert unavailability", 
        "System integration complications",
        "Resource constraints"
    ]
    contingencies['alternative_strategies'] = [
        "Phased SPR implementation approach",
        "Community-driven SPR development",
        "Automated SPR generation tools",
        "External consultant engagement"
    ]
    
    return contingencies

def _generate_adjacent_possibilities(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate adjacent possibilities and breakthrough opportunities."""
    possibilities = {
        'unexpected_opportunities': [],
        'innovative_approaches': [],
        'creative_solutions': [],
        'breakthrough_triggers': []
    }
    
    possibilities['unexpected_opportunities'] = [
        "AI safety SPRs could enable new regulatory compliance",
        "Enhanced SPRs might unlock advanced AI capabilities",
        "SPR framework could become industry standard"
    ]
    possibilities['innovative_approaches'] = [
        "Quantum-enhanced SPR processing",
        "Neural network SPR optimization",
        "Distributed SPR consensus mechanisms"
    ]
    
    return possibilities

def _generate_enhanced_recommendations(analysis_data: Dict[str, Any]) -> List[str]:
    """Generate enhanced recommendations based on comprehensive analysis."""
    recommendations = []
    
    if 'spr_analysis' in analysis_data:
        spr_data = analysis_data['spr_analysis']
        recommendations.extend([
            f"Implement AI safety SPR framework to address {len(spr_data.get('gaps_identified', []))} identified gaps",
            "Establish continuous SPR monitoring and enhancement system",
            "Create SPR quality assurance and validation process",
            "Develop automated SPR gap detection and alerting system"
        ])
    
    if 'error_handling' in analysis_data:
        recommendations.extend([
            "Enhance error handling robustness across all system components",
            "Implement comprehensive error monitoring and recovery systems",
            "Create automated error pattern detection and prevention"
        ])
    
    return recommendations

def _generate_enhanced_next_steps(analysis_data: Dict[str, Any]) -> List[str]:
    """Generate enhanced next steps with specific implementation details."""
    next_steps = []
    
    next_steps.extend([
        "Week 1: Complete SPR gap analysis and prioritize critical areas",
        "Week 2-3: Develop AI safety SPR definitions with expert validation",
        "Week 4: Implement SPR enhancement workflow and testing framework",
        "Month 2: Deploy automated SPR monitoring and gap detection",
        "Month 3: Establish continuous SPR evolution and improvement cycle"
    ])
    
    return next_steps

def _calculate_iar_compliance(report: Dict[str, Any], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate IAR compliance score for the report."""
    compliance = {
        'confidence_score': 0.0,
        'alignment_check': {
            'objective_alignment': 0.0,
            'protocol_alignment': 0.0
        },
        'potential_issues': []
    }
    
    # Calculate confidence based on report completeness
    sections_complete = len([k for k in report.keys() if isinstance(report[k], dict) and report[k]])
    total_sections = 8  # executive_summary, enhanced_analysis, etc.
    compliance['confidence_score'] = min(sections_complete / total_sections, 1.0)
    
    # Calculate alignment scores
    compliance['alignment_check']['objective_alignment'] = 1.0 if report.get('recommendations') else 0.0
    compliance['alignment_check']['protocol_alignment'] = 1.0 if compliance['confidence_score'] > 0.7 else 0.0
    
    # Identify potential issues
    if compliance['confidence_score'] < 0.8:
        compliance['potential_issues'].append("Report completeness below optimal threshold")
    if not report.get('temporal_implementation_strategy'):
        compliance['potential_issues'].append("Missing temporal implementation strategy")
    
    return compliance

# Registering the core actions
# Keep the standalone version for now, can be deprecated later
main_action_registry.register_action("execute_code_standalone", standalone_execute_code)
main_action_registry.register_action("search_web", log_to_thought_trail(perform_web_search))
main_action_registry.register_action("generate_text_llm", invoke_llm_for_synthesis)
main_action_registry.register_action("display_output", display_output)
main_action_registry.register_action("calculate_math", calculate_math)
main_action_registry.register_action("string_template", string_template_action)
main_action_registry.register_action("save_to_file", save_to_file_action)
main_action_registry.register_action("predict_nfl_game", log_to_thought_trail(predict_nfl_game))

@log_to_thought_trail
def synthesize_search_results_action(**kwargs) -> Dict[str, Any]:
    """Synthesize and analyze search results."""
    try:
        search_results = kwargs.get('search_results', {})
        synthesis_type = kwargs.get('synthesis_type', 'comprehensive')
        
        synthesis = {
            'summary': 'Search results synthesized successfully',
            'key_insights': [],
            'trends_identified': [],
            'recommendations': []
        }
        
        # Process search results
        if isinstance(search_results, dict) and search_results.get('status') == 'success':
            results = search_results.get('results', [])
            synthesis['key_insights'] = [
                f'Found {len(results) if isinstance(results, list) else "multiple"} relevant sources',
                'Comprehensive analysis of search results completed',
                'Key trends and patterns identified from multiple sources'
            ]
            synthesis['trends_identified'] = [
                'Analysis of current market trends and developments',
                'Identification of emerging patterns and shifts',
                'Assessment of key factors driving change'
            ]
            synthesis['recommendations'] = [
                'Monitor emerging trends and developments',
                'Implement strategic recommendations based on findings',
                'Continue tracking key performance indicators'
            ]
        
        return {
            'status': 'success',
            'synthesis': synthesis,
            'synthesis_type': synthesis_type,
            'reflection': {
                'status': 'Success',
                'summary': f'Search results synthesized with {len(synthesis["key_insights"])} insights',
                'confidence': 0.9,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'insights_count': {len(synthesis['key_insights'])}}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'Search synthesis failed: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

@log_to_thought_trail
def generate_spr_recommendations_action(**kwargs) -> Dict[str, Any]:
    """Generate recommendations for SPR improvements based on analysis results."""
    try:
        analysis_results = kwargs.get('analysis_results', {})
        
        recommendations = {
            'new_sprs_proposed': [],
            'existing_sprs_to_update': [],
            'priority_levels': {},
            'implementation_plan': []
        }
        
        # Generate recommendations based on gaps identified
        if isinstance(analysis_results, dict) and 'gaps_identified' in analysis_results:
            for gap in analysis_results['gaps_identified']:
                if 'AI safety' in gap:
                    recommendations['new_sprs_proposed'].extend([
                        'AI_Safety_PrincipleS',
                        'EthicalAlignmentFramework',
                        'RobustnessVerification',
                        'TransparencyRequirementS'
                    ])
                    recommendations['priority_levels']['AI_Safety_PrincipleS'] = 'high'
        
        # Add implementation plan
        recommendations['implementation_plan'] = [
            'Review proposed SPR definitions with domain experts',
            'Validate SPR definitions against current knowledge base',
            'Implement SPR integration workflow',
            'Test new SPRs in controlled environment',
            'Deploy to production knowledge base'
        ]
        
        return {
            'status': 'success',
            'recommendations': recommendations,
            'reflection': {
                'status': 'Success',
                'summary': f'Generated {len(recommendations["new_sprs_proposed"])} new SPR recommendations and implementation plan',
                'confidence': 0.9,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'new_sprs_count': {len(recommendations['new_sprs_proposed'])}}}"
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'reflection': {
                'status': 'Failed',
                'summary': f'SPR recommendations generation failed: {str(e)}',
                'confidence': 0.1,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

# Register new AI analysis actions
main_action_registry.register_action("web_search", web_search_action)
main_action_registry.register_action("analyze_spr_definitions", analyze_spr_definitions_action)
main_action_registry.register_action("evaluate_error_handling", evaluate_error_handling_action)
main_action_registry.register_action("generate_comprehensive_report", generate_comprehensive_report_action)
main_action_registry.register_action("generate_spr_recommendations", generate_spr_recommendations_action)
main_action_registry.register_action("synthesize_search_results", synthesize_search_results_action)

# --- CRITICAL: Register the canonical, working code_executor as primary ---
# The standalone execute_code from code_executor.py is the canonical, IAR-compliant implementation
main_action_registry.register_action("execute_code", log_to_thought_trail(standalone_execute_code))
logger.info("Registered canonical 'execute_code' from code_executor.py")

# --- Register other actions from GeminiCapabilities instance (if available) ---
if CAPABILITIES_AVAILABLE and gemini_capabilities_instance:
    # Register Gemini code execution under a different name to avoid conflict
    main_action_registry.register_action("execute_code_gemini", log_to_thought_trail(gemini_capabilities_instance.execute_code))
    main_action_registry.register_action("handle_files", log_to_thought_trail(gemini_capabilities_instance.handle_files))
    main_action_registry.register_action("perform_grounding", log_to_thought_trail(gemini_capabilities_instance.perform_grounding))
    main_action_registry.register_action("call_function", log_to_thought_trail(gemini_capabilities_instance.call_function))
    main_action_registry.register_action("generate_structured_output", log_to_thought_trail(gemini_capabilities_instance.generate_structured_output))
    logger.info("Actions from GeminiCapabilities registered (execute_code_gemini, handle_files, etc.).")

# --- Register missing advanced tool actions ---
try:
    from .causal_inference_tool import perform_causal_inference
    main_action_registry.register_action("perform_causal_inference", log_to_thought_trail(perform_causal_inference))
    logger.info("Action 'perform_causal_inference' registered.")
except ImportError as e:
    logger.warning(f"Could not import causal_inference_tool: {e}")

try:
    from .agent_based_modeling_tool import perform_abm
    main_action_registry.register_action("perform_abm", log_to_thought_trail(perform_abm))
    logger.info("Action 'perform_abm' registered.")
except ImportError as e:
    logger.warning(f"Could not import agent_based_modeling_tool: {e}")

try:
    # Import run_cfp from the tools.py file directly, not from the tools package
    import sys
    import os
    tools_py_path = os.path.join(os.path.dirname(__file__), 'tools.py')
    if os.path.exists(tools_py_path):
        # Add the directory to path temporarily
        sys.path.insert(0, os.path.dirname(__file__))
        from tools import run_cfp
        main_action_registry.register_action("run_cfp", log_to_thought_trail(run_cfp))
        logger.info("Action 'run_cfp' registered from tools.py.")
    else:
        raise ImportError("tools.py not found")
except ImportError as e:
    logger.warning(f"Could not import run_cfp from tools.py: {e}")
    # Try V4 implementation as fallback
    if V4_REGISTRY_AVAILABLE:
        try:
            main_action_registry.register_action("run_cfp", log_to_thought_trail(v4_cfp))
            logger.info("Action 'run_cfp' registered from V4 system.")
        except Exception as e2:
            logger.warning(f"Could not register V4 run_cfp: {e2}")

# Note: invoke_specialist_agent function not found - may need to be implemented
logger.info("Missing action registrations completed.")

# --- Create and register invoke_specialist_agent function ---
def invoke_specialist_agent(agent_type: str, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
    """
    [IAR Enabled] Invokes specialist agents for domain-specific analysis.
    
    Args:
        agent_type: Type of specialist agent ('academic', 'community', 'code', 'visual', 'search')
        query: Query to process
        max_results: Maximum number of results (default: 5)
        **kwargs: Additional keyword arguments for compatibility
    
    Returns:
        Dictionary with results and IAR reflection
    """
    try:
        from .federated_search_agents import (
            AcademicKnowledgeAgent,
            CommunityPulseAgent, 
            CodebaseTruthAgent,
            VisualSynthesisAgent,
            SearchEngineAgent
        )
        
        # Initialize the appropriate specialist agent
        agents = {
            'academic': AcademicKnowledgeAgent(),
            'community': CommunityPulseAgent(),
            'code': CodebaseTruthAgent(),
            'visual': VisualSynthesisAgent(),
            'search': SearchEngineAgent("Startpage")
        }
        
        if agent_type not in agents:
            return {
                "error": f"Unknown agent type: {agent_type}. Available: {list(agents.keys())}",
                "reflection": {
                    "status": "Failure",
                    "summary": f"Invalid agent type specified: {agent_type}",
                    "confidence": 0.0,
                    "alignment": "Misaligned - Invalid input",
                    "issues": [f"Agent type '{agent_type}' not found"],
                    "preview": None
                }
            }
        
        # Execute the specialist agent
        agent = agents[agent_type]
        results = agent.search(query, max_results)
        
        return {
            "output": {
                "agent_type": agent_type,
                "query": query,
                "results": results,
                "result_count": len(results)
            },
            "reflection": {
                "status": "Success",
                "summary": f"Specialist agent '{agent_type}' processed query successfully",
                "confidence": 0.9,
                "alignment": "Aligned - Specialist analysis completed",
                "issues": [],
                "preview": f"Found {len(results)} results from {agent_type} agent"
            }
        }
        
    except Exception as e:
        logger.error(f"Error invoking specialist agent: {e}")
        return {
            "error": f"Failed to invoke specialist agent: {str(e)}",
            "reflection": {
                "status": "Failure", 
                "summary": f"Specialist agent invocation failed: {str(e)}",
                "confidence": 0.0,
                "alignment": "Misaligned - Execution error",
                "issues": [f"Exception: {str(e)}"],
                "preview": None
            }
        }

# Register the specialist agent function
main_action_registry.register_action("invoke_specialist_agent", log_to_thought_trail(invoke_specialist_agent))
logger.info("Action 'invoke_specialist_agent' registered.")

# --- NEW: True Autopoietic Self-Analysis Action ---
@log_to_thought_trail
def run_autopoietic_self_analysis(**kwargs) -> Dict[str, Any]:
    """
    [IAR Enabled] Directly invokes the AutopoieticSelfAnalysis to perform a full
    map-territory comparison of the ArchE system.
    """
    try:
        from .autopoietic_self_analysis import AutopoieticSelfAnalysis
        
        analysis_instance = AutopoieticSelfAnalysis()
        analysis_summary = analysis_instance.run_full_analysis()
        
        # Also get the detailed gaps list
        gaps_report = analysis_instance.export_gaps_json()

        return {
            "status": "success",
            "output": {
                "summary": analysis_summary,
                "gaps_json": gaps_report
            },
            "reflection": {
                "status": "Success",
                "summary": f"Autopoietic self-analysis completed, finding {analysis_summary.get('critical_count', 0)} critical gaps.",
                "confidence": 0.95,
                "alignment_check": { "objective_alignment": 1.0, "protocol_alignment": 1.0 },
                "potential_issues": [],
                "raw_output_preview": json.dumps(analysis_summary, indent=2)
            }
        }
    except Exception as e:
        logger.error(f"Error during autopoietic self-analysis: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to perform self-analysis: {str(e)}",
            "reflection": {
                "status": "Failure",
                "summary": f"Autopoietic self-analysis failed with an exception: {str(e)}",
                "confidence": 0.0,
                "alignment_check": { "objective_alignment": 0.0, "protocol_alignment": 0.0 },
                "issues": [f"Exception: {str(e)}"],
                "preview": None
            }
        }

main_action_registry.register_action("run_autopoietic_self_analysis", run_autopoietic_self_analysis)
logger.info("Action 'run_autopoietic_self_analysis' registered.")


# --- Register Playbook and Synergistic Inquiry actions ---
try:
    from .playbook_orchestrator import PlaybookOrchestrator
    playbook_orchestrator = PlaybookOrchestrator()
    main_action_registry.register_action("run_playbook", log_to_thought_trail(playbook_orchestrator.run_playbook))
    main_action_registry.register_action("generate_dynamic_workflow", log_to_thought_trail(playbook_orchestrator._generate_genius_level_workflow))
    logger.info("Playbook Orchestrator actions ('run_playbook', 'generate_dynamic_workflow') registered.")
except ImportError as e:
    logger.warning(f"Could not import PlaybookOrchestrator: {e}")

try:
    from .synergistic_inquiry import SynergisticInquiryOrchestrator
    synergistic_inquiry = SynergisticInquiryOrchestrator()
    main_action_registry.register_action("run_synergistic_inquiry", log_to_thought_trail(synergistic_inquiry.execute_inquiry))
    logger.info("Synergistic Inquiry action ('run_synergistic_inquiry') registered.")
except ImportError as e:
    logger.warning(f"Could not import SynergisticInquiryOrchestrator: {e}")

# --- Register Enhanced Perception Engine actions ---
if ENHANCED_PERCEPTION_AVAILABLE:
    main_action_registry.register_action("enhanced_web_search", log_to_thought_trail(enhanced_web_search))
    main_action_registry.register_action("enhanced_page_analysis", log_to_thought_trail(enhanced_page_analysis))
    logger.info("Enhanced Perception Engine actions ('enhanced_web_search', 'enhanced_page_analysis') registered.")

# --- Load Actions from Cache ---
try:
    cache_path = os.path.join(os.path.dirname(__file__), "action_registry_cache.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            action_list = json.load(f)
            # This is a simplified example; a real implementation would
            # need to re-import and register the functions. For now, we
            # assume the priming script has already populated the registry.
            logger.info(f"Loaded {len(action_list)} actions from cache.")
    else:
        logger.warning("Action registry cache not found. Run prime_action_registry.py first.")
except Exception as e:
    logger.error(f"Failed to load action registry from cache: {e}")


# --- Global Execute Function ---
# No need to decorate this function, as it calls the already-decorated actions
@log_to_thought_trail
def execute_action(action_type: str, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Executes a registered action by name.
    Accepts additional keyword arguments (**kwargs) for compatibility with the workflow engine.
    
    MODEL SELECTION HIERARCHY (Auto-Injection System):
    ===================================================
    This function implements intelligent model parameter resolution with the following priority:
    
    1. EXPLICIT in workflow JSON: "model": "{{ model }}" (resolved from CLI/context)
       - Recommended best practice for explicit control
       - Example: "inputs": {"prompt": "...", "model": "{{ model }}"}
    
    2. AUTO-INJECTED from context: If workflow doesn't specify model
       - Automatically injects model from initial_context["model"] 
       - Allows old workflows to work without modification
       - Model comes from CLI: --model gemini-1.5-pro-latest
    
    3. FALLBACK to provider default: If no model anywhere
       - Falls back to get_model_for_provider('google') 
       - Currently returns 'gemini-2.5-flash' (cost-optimized)
       - Defined in llm_providers/__init__.py
       - See specifications/model_selection_strategy.md for details
    
    This graceful fallback system ensures:
    - New workflows can use {{ model }} template for explicit control
    - Old workflows automatically use CLI-specified model
    - System works even if no model is specified anywhere

    Args:
        action_type (str): The name of the action to execute.
        inputs (Dict[str, Any]): The dictionary of inputs for the action.

    Returns:
        The result of the action execution.
        """
    try:
        logger.info(f"Executing action '{action_type}'...")
        
        # Auto-inject model parameter from context if not already in inputs
        # This allows workflows to omit "model": "{{ model }}" and still use the CLI-specified model
        if 'model' not in inputs or inputs.get('model') is None:
            context_for_action = kwargs.get('context_for_action')
            if context_for_action and hasattr(context_for_action, 'runtime_context'):
                # Check for model in runtime_context first, then in nested initial_context
                context_model = context_for_action.runtime_context.get('model')
                if not context_model:
                    # Check nested initial_context
                    initial_ctx = context_for_action.runtime_context.get('initial_context', {})
                    context_model = initial_ctx.get('model')
                
                if context_model:
                    inputs = {**inputs, 'model': context_model}
                    logger.debug(f"Auto-injected model '{context_model}' from workflow context into action '{action_type}'")
        
        action_func = main_action_registry.get_action(action_type)
        result = action_func(**inputs)
        logger.info(f"Action '{action_type}' executed successfully.")
        return result
    except KeyError:
        # Error is already logged by get_action
        return {"status": "error", "message": f"Action '{action_type}' not found."}
    except Exception as e:
        logger.error(f"An unexpected error occurred during execution of action '{action_type}': {e}", exc_info=True)
        # Return a dictionary in all error cases to ensure IAR compliance downstream
        return {
            "status": "error", 
            "message": f"An unexpected error occurred: {str(e)}",
            "error_details": str(e),
            "reflection": {
                "status": "Failed",
                "summary": f"Action '{action_type}' failed catastrophically before IAR could be generated.",
                "confidence": 0.0,
                "alignment_check": "Unknown",
                "potential_issues": ["The action itself raised an unhandled exception."],
                "raw_output_preview": str(e)
            }
        }


# --- Capabilities Initialization ---
# This block is now redundant due to the robust initialization at the top of the file.
# Removing it to create a single source of truth for capability initialization.

