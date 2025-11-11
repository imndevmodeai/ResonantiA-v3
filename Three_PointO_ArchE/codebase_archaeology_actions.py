#!/usr/bin/env python3
"""
Codebase Archaeology Action Wrappers
Action registry wrappers for CodebaseArchaeologist methods
"""

import logging
from typing import Dict, Any, List
from .codebase_archaeologist import CodebaseArchaeologist, CodebasePattern
from .thought_trail import log_to_thought_trail

logger = logging.getLogger(__name__)

# Global instance (will be initialized by RISE orchestrator)
_archaeologist: CodebaseArchaeologist = None

def set_archaeologist(archaeologist: CodebaseArchaeologist):
    """Set the global CodebaseArchaeologist instance"""
    global _archaeologist
    _archaeologist = archaeologist
    logger.info("CodebaseArchaeologist instance set for action registry")

@log_to_thought_trail
def search_codebase_action(**kwargs) -> Dict[str, Any]:
    """
    Action wrapper for CodebaseArchaeologist.search_codebase_for_patterns
    
    Inputs:
        query: str - Search query/problem description
        pattern_types: List[str] - Types to search (class, function, workflow, spr, specification)
        max_results: int - Maximum results (default: 10)
        search_mode: str - Search mode: semantic, exact, fuzzy (default: semantic)
    
    Returns:
        Dict with patterns list and metadata
    """
    try:
        if _archaeologist is None:
            return {
                'status': 'error',
                'message': 'CodebaseArchaeologist not initialized',
                'patterns': [],
                'reflection': {
                    'status': 'Failed',
                    'summary': 'CodebaseArchaeologist instance not available',
                    'confidence': 0.0
                }
            }
        
        query = kwargs.get('query', '')
        pattern_types = kwargs.get('pattern_types', ['class', 'function', 'workflow', 'spr', 'specification'])
        max_results = kwargs.get('max_results', 10)
        search_mode = kwargs.get('search_mode', 'semantic')
        
        if not query:
            return {
                'status': 'error',
                'message': 'Query parameter required',
                'patterns': [],
                'reflection': {
                    'status': 'Failed',
                    'summary': 'No query provided for codebase search',
                    'confidence': 0.0
                }
            }
        
        logger.info(f"Searching codebase: '{query}' (types: {pattern_types}, mode: {search_mode})")
        
        patterns = _archaeologist.search_codebase_for_patterns(
            query=query,
            pattern_types=pattern_types,
            max_results=max_results,
            search_mode=search_mode
        )
        
        # Convert CodebasePattern objects to dicts
        patterns_dict = [p.to_dict() for p in patterns]
        
        return {
            'status': 'success',
            'patterns': patterns_dict,
            'pattern_count': len(patterns_dict),
            'query': query,
            'reflection': {
                'status': 'Success',
                'summary': f'Found {len(patterns_dict)} codebase patterns matching query',
                'confidence': 0.8 if patterns_dict else 0.3,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [] if patterns_dict else ['No patterns found - may need broader query'],
                'raw_output_preview': f"{{'status': 'success', 'pattern_count': {len(patterns_dict)}}}"
            }
        }
    except Exception as e:
        logger.error(f"Codebase search action failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
            'patterns': [],
            'reflection': {
                'status': 'Failed',
                'summary': f'Codebase search failed: {str(e)}',
                'confidence': 0.0,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

@log_to_thought_trail
def synthesize_from_patterns_action(**kwargs) -> Dict[str, Any]:
    """
    Action wrapper for CodebaseArchaeologist.synthesize_from_patterns
    
    Inputs:
        problem_description: str - The problem to solve
        external_knowledge: Dict[str, Any] - External research/knowledge
        codebase_patterns: List[Dict] - Patterns from codebase (from search_codebase_action)
        synthesis_mode: str - How to combine: codebase_led, external_led, hybrid (default: hybrid)
    
    Returns:
        Dict with synthesized solution
    """
    try:
        if _archaeologist is None:
            return {
                'status': 'error',
                'message': 'CodebaseArchaeologist not initialized',
                'synthesized_solution': {},
                'reflection': {
                    'status': 'Failed',
                    'summary': 'CodebaseArchaeologist instance not available',
                    'confidence': 0.0
                }
            }
        
        problem_description = kwargs.get('problem_description', '')
        external_knowledge = kwargs.get('external_knowledge', {})
        codebase_patterns_raw = kwargs.get('codebase_patterns', [])
        synthesis_mode = kwargs.get('synthesis_mode', 'hybrid')
        
        if not problem_description:
            return {
                'status': 'error',
                'message': 'problem_description parameter required',
                'synthesized_solution': {},
                'reflection': {
                    'status': 'Failed',
                    'summary': 'No problem description provided',
                    'confidence': 0.0
                }
            }
        
        # Convert dict patterns back to CodebasePattern objects if needed
        codebase_patterns = []
        for p in codebase_patterns_raw:
            if isinstance(p, dict):
                # Reconstruct CodebasePattern from dict
                pattern = CodebasePattern(
                    pattern_type=p.get('type', ''),
                    name=p.get('name', ''),
                    file_path=p.get('file_path', ''),
                    description=p.get('description', ''),
                    relevance_score=p.get('relevance_score', 0.0),
                    key_excerpts=p.get('key_excerpts', []),
                    relationships=p.get('relationships', []),
                    spr_references=p.get('spr_references', []),
                    implementation_details=p.get('implementation_details', {})
                )
                codebase_patterns.append(pattern)
            elif isinstance(p, CodebasePattern):
                codebase_patterns.append(p)
        
        logger.info(f"Synthesizing solution from {len(codebase_patterns)} patterns (mode: {synthesis_mode})")
        
        synthesized = _archaeologist.synthesize_from_patterns(
            problem_description=problem_description,
            external_knowledge=external_knowledge,
            codebase_patterns=codebase_patterns,
            synthesis_mode=synthesis_mode
        )
        
        return {
            'status': 'success',
            'synthesized_solution': synthesized,
            'synthesis_mode': synthesis_mode,
            'pattern_count': len(codebase_patterns),
            'reflection': {
                'status': 'Success',
                'summary': f'Synthesized solution from {len(codebase_patterns)} codebase patterns',
                'confidence': 0.85,
                'alignment_check': {'objective_alignment': 1.0, 'protocol_alignment': 1.0},
                'potential_issues': [],
                'raw_output_preview': f"{{'status': 'success', 'synthesis_mode': '{synthesis_mode}'}}"
            }
        }
    except Exception as e:
        logger.error(f"Pattern synthesis action failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
            'synthesized_solution': {},
            'reflection': {
                'status': 'Failed',
                'summary': f'Pattern synthesis failed: {str(e)}',
                'confidence': 0.0,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }

@log_to_thought_trail
def validate_against_patterns_action(**kwargs) -> Dict[str, Any]:
    """
    Action wrapper for validating strategy against codebase patterns
    
    Inputs:
        strategy: str or Dict - Strategy to validate
        required_patterns: List[str] - Required pattern types (e.g., ["IAR compliance", "SPR integration"])
        codebase_patterns: List[Dict] - Patterns to validate against (optional, will search if not provided)
    
    Returns:
        Dict with validation results and alignment scores
    """
    try:
        if _archaeologist is None:
            return {
                'status': 'error',
                'message': 'CodebaseArchaeologist not initialized',
                'validation_result': {},
                'reflection': {
                    'status': 'Failed',
                    'summary': 'CodebaseArchaeologist instance not available',
                    'confidence': 0.0
                }
            }
        
        strategy = kwargs.get('strategy', '')
        required_patterns = kwargs.get('required_patterns', ['IAR compliance', 'SPR integration', 'workflow compatibility'])
        codebase_patterns_raw = kwargs.get('codebase_patterns', [])
        
        if not strategy:
            return {
                'status': 'error',
                'message': 'strategy parameter required',
                'validation_result': {},
                'reflection': {
                    'status': 'Failed',
                    'summary': 'No strategy provided for validation',
                    'confidence': 0.0
                }
            }
        
        # Convert strategy to string if dict
        if isinstance(strategy, dict):
            strategy_str = str(strategy)
        else:
            strategy_str = str(strategy)
        
        # If patterns not provided, search for them
        if not codebase_patterns_raw:
            logger.info(f"Searching codebase for validation patterns: {required_patterns}")
            patterns = _archaeologist.search_codebase_for_patterns(
                query=' '.join(required_patterns),
                pattern_types=['class', 'function', 'workflow', 'spr'],
                max_results=20
            )
            codebase_patterns = patterns
        else:
            # Convert dict patterns to CodebasePattern objects
            codebase_patterns = []
            for p in codebase_patterns_raw:
                if isinstance(p, dict):
                    pattern = CodebasePattern(
                        pattern_type=p.get('type', ''),
                        name=p.get('name', ''),
                        file_path=p.get('file_path', ''),
                        description=p.get('description', ''),
                        relevance_score=p.get('relevance_score', 0.0)
                    )
                    codebase_patterns.append(pattern)
                elif isinstance(p, CodebasePattern):
                    codebase_patterns.append(p)
        
        # Simple validation: check if strategy mentions required patterns
        validation_scores = {}
        for pattern_name in required_patterns:
            # Check if pattern is mentioned in strategy or found in codebase
            pattern_found = any(
                pattern_name.lower() in p.name.lower() or 
                pattern_name.lower() in p.description.lower()
                for p in codebase_patterns
            )
            strategy_mentions = pattern_name.lower() in strategy_str.lower()
            validation_scores[pattern_name] = {
                'found_in_codebase': pattern_found,
                'mentioned_in_strategy': strategy_mentions,
                'alignment_score': 1.0 if (pattern_found and strategy_mentions) else 0.5 if pattern_found else 0.0
            }
        
        overall_alignment = sum(s['alignment_score'] for s in validation_scores.values()) / len(validation_scores) if validation_scores else 0.0
        
        return {
            'status': 'success',
            'validation_result': {
                'overall_alignment': overall_alignment,
                'pattern_scores': validation_scores,
                'required_patterns': required_patterns,
                'patterns_checked': len(codebase_patterns)
            },
            'reflection': {
                'status': 'Success',
                'summary': f'Validated strategy against {len(required_patterns)} required patterns (alignment: {overall_alignment:.2f})',
                'confidence': 0.8,
                'alignment_check': {'objective_alignment': overall_alignment, 'protocol_alignment': overall_alignment},
                'potential_issues': [] if overall_alignment > 0.7 else ['Low alignment with codebase patterns'],
                'raw_output_preview': f"{{'status': 'success', 'overall_alignment': {overall_alignment:.2f}}}"
            }
        }
    except Exception as e:
        logger.error(f"Pattern validation action failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
            'validation_result': {},
            'reflection': {
                'status': 'Failed',
                'summary': f'Pattern validation failed: {str(e)}',
                'confidence': 0.0,
                'alignment_check': {'objective_alignment': 0.0, 'protocol_alignment': 0.0},
                'potential_issues': [str(e)],
                'raw_output_preview': f"{{'status': 'error', 'message': '{str(e)}'}}"
            }
        }



