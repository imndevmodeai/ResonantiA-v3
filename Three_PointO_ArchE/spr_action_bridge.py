# --- START OF FILE Three_PointO_ArchE/spr_action_bridge.py ---
# ResonantiA Protocol v3.1-CA - SPR Action Bridge
# Critical infrastructure component that bridges SPR definitions with their implementations
# Enables dynamic invocation of cognitive tools through SPR identifiers

import json
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional
import traceback
from datetime import datetime

class SPRBridgeLoader:
    """
    Handles loading and caching of the Knowledge Tapestry.
    Prevents re-reading the large JSON file for every action invocation.
    """
    
    def __init__(self, tapestry_path: str):
        """
        Initialize the bridge loader with the path to spr_definitions_tv.json
        
        Args:
            tapestry_path: Path to the SPR definitions JSON file
        """
        self.tapestry_path = Path(tapestry_path)
        self.tapestry_cache = None
        self.cache_timestamp = None
        
    def load_tapestry(self) -> Dict[str, Any]:
        """
        Reads the JSON file into a dictionary, keyed by spr_id for O(1) lookup.
        Implements caching to avoid repeated file reads.
        
        Returns:
            Dictionary of SPR definitions keyed by spr_id
        """
        try:
            # Check if file exists
            if not self.tapestry_path.exists():
                raise FileNotFoundError(f"SPR definitions file not found: {self.tapestry_path}")
            
            # Get file modification time
            file_mtime = self.tapestry_path.stat().st_mtime
            
            # Load from cache if available and file hasn't changed
            if self.tapestry_cache is not None and self.cache_timestamp == file_mtime:
                return self.tapestry_cache
            
            # Load from file
            with open(self.tapestry_path, 'r', encoding='utf-8') as f:
                tapestry_list = json.load(f)
            
            # Convert list to dictionary keyed by spr_id for efficient lookup
            tapestry_dict = {}
            for spr_def in tapestry_list:
                if 'spr_id' in spr_def:
                    tapestry_dict[spr_def['spr_id']] = spr_def
                else:
                    print(f"Warning: SPR definition missing 'spr_id': {spr_def}")
            
            # Update cache
            self.tapestry_cache = tapestry_dict
            self.cache_timestamp = file_mtime
            
            return tapestry_dict
            
        except Exception as e:
            raise Exception(f"Failed to load SPR tapestry from {self.tapestry_path}: {str(e)}")
    
    def get_spr_definition(self, spr_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single, validated SPR definition from the loaded dictionary.
        
        Args:
            spr_id: The SPR identifier to look up
            
        Returns:
            SPR definition dictionary or None if not found
        """
        tapestry = self.load_tapestry()
        return tapestry.get(spr_id)


def invoke_spr(spr_id: str, parameters: Dict[str, Any], bridge_loader: SPRBridgeLoader) -> Dict[str, Any]:
    """
    Main entry point for the SPR bridge. Dynamically invokes the implementation
    corresponding to the given SPR identifier.
    
    Args:
        spr_id: The SPR identifier to invoke
        parameters: Dictionary of parameters to pass to the implementation
        bridge_loader: Initialized SPRBridgeLoader instance
        
    Returns:
        IAR-compliant dictionary with execution results
    """
    execution_start = datetime.now()
    
    try:
        # Step 1: Get SPR Definition
        spr_definition = bridge_loader.get_spr_definition(spr_id)
        if spr_definition is None:
            return {
                "status": "error",
                "confidence": 0.0,
                "potential_issues": [f"SPR '{spr_id}' not found in Knowledge Tapestry"],
                "alignment_check": "failed",
                "tactical_resonance": 0.0,
                "crystallization_potential": 0.0,
                "error_type": "SPR_NOT_FOUND",
                "execution_time": (datetime.now() - execution_start).total_seconds()
            }
        
        # Step 2: Identify Target Implementation
        # Check for blueprint_details in metadata first, then at top level
        blueprint_details = spr_definition.get('metadata', {}).get('blueprint_details', '')
        if not blueprint_details:
            blueprint_details = spr_definition.get('blueprint_details', '')
        
        if not blueprint_details or '/' not in blueprint_details:
            return {
                "status": "error",
                "confidence": 0.0,
                "potential_issues": [f"SPR '{spr_id}' has invalid blueprint_details: {blueprint_details}"],
                "alignment_check": "failed",
                "tactical_resonance": 0.0,
                "crystallization_potential": 0.0,
                "error_type": "INVALID_BLUEPRINT",
                "execution_time": (datetime.now() - execution_start).total_seconds()
            }
        
        # Parse blueprint_details to extract module and target
        # Expected format examples:
        # "causal_inference_tool.py/CausalInferenceTool"
        # "predictive_modeling_tool.py/PredictiveModelingTool.forecast"
        # "knowledge_crystallization_system.py/crystallize_pattern"
        # "causal_inference_tool.py/perform_causal_inference:estimate_effect"
        
        module_path, target_spec = blueprint_details.split('/', 1)
        
        # Step 3: Dynamic Import
        try:
            # Handle different path formats
            if module_path.startswith('../'):
                # Relative path going up from Three_PointO_ArchE
                relative_path = module_path[3:]  # Remove '../'
                if relative_path.endswith('.py'):
                    module_name = relative_path[:-3]  # Remove .py extension
                else:
                    module_name = relative_path
                
                # For relative imports, we need to add the parent directory to sys.path temporarily
                import sys
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                    path_added = True
                else:
                    path_added = False
                
                try:
                    module = importlib.import_module(module_name)
                finally:
                    # Clean up sys.path if we added to it
                    if path_added and parent_dir in sys.path:
                        sys.path.remove(parent_dir)
                        
            elif not module_path.startswith('.') and not module_path.startswith('/'):
                # Assume it's relative to Three_PointO_ArchE
                if module_path.endswith('.py'):
                    module_name = f"Three_PointO_ArchE.{module_path[:-3]}"
                else:
                    module_name = f"Three_PointO_ArchE.{module_path}"
                
                module = importlib.import_module(module_name)
            else:
                module_name = module_path
                module = importlib.import_module(module_name)
            
        except ImportError as e:
            return {
                "status": "error",
                "confidence": 0.0,
                "potential_issues": [f"Failed to import module '{module_name}': {str(e)}"],
                "alignment_check": "failed",
                "tactical_resonance": 0.0,
                "crystallization_potential": 0.0,
                "error_type": "MODULE_IMPORT_ERROR",
                "module_path": module_path,
                "module_name": module_name,
                "import_error": str(e),
                "execution_time": (datetime.now() - execution_start).total_seconds()
            }
        
        # Step 4: Get Handle to Target Entity
        try:
            # Parse target_spec for function:operation, class.method or just function/class
            if ':' in target_spec:
                # Function with operation parameter (e.g., perform_causal_inference:estimate_effect)
                function_name, operation = target_spec.split(':', 1)
                target_entity = getattr(module, function_name)
                is_class_method = False
                # Add operation to parameters
                parameters['operation'] = operation
            elif '.' in target_spec:
                class_name, method_name = target_spec.split('.', 1)
                target_class = getattr(module, class_name)
                target_entity = getattr(target_class, method_name)
                is_class_method = True
            else:
                target_entity = getattr(module, target_spec)
                is_class_method = hasattr(target_entity, '__self__') or (
                    hasattr(target_entity, '__name__') and 
                    hasattr(module, target_spec) and 
                    callable(getattr(module, target_spec))
                )
                
        except AttributeError as e:
            return {
                "status": "error",
                "confidence": 0.0,
                "potential_issues": [f"Target entity '{target_spec}' not found in module '{module_name}': {str(e)}"],
                "alignment_check": "failed",
                "tactical_resonance": 0.0,
                "crystallization_potential": 0.0,
                "error_type": "TARGET_NOT_FOUND",
                "target_spec": target_spec,
                "module_name": module_name,
                "attribute_error": str(e),
                "execution_time": (datetime.now() - execution_start).total_seconds()
            }
        
        # Step 5: Instantiate/Execute
        try:
            if ':' in target_spec:
                # Function with operation parameter - direct call
                result_dict = target_entity(**parameters)
            elif '.' in target_spec:
                # Class method - instantiate class first with parameters
                class_name, method_name = target_spec.split('.', 1)
                target_class = getattr(module, class_name)
                tool_instance = target_class(**parameters)
                result_dict = getattr(tool_instance, method_name)()
            elif callable(target_entity):
                # Direct function call or class instantiation + execution
                if hasattr(target_entity, '__call__'):
                    # Try to determine if it's a class or function
                    try:
                        # If it's a class, try to instantiate and call execute
                        if hasattr(target_entity, '__init__') and hasattr(target_entity, 'execute'):
                            tool_instance = target_entity()
                            result_dict = tool_instance.execute(**parameters)
                        else:
                            # Direct function call
                            result_dict = target_entity(**parameters)
                    except Exception as class_error:
                        # Fallback to direct call
                        result_dict = target_entity(**parameters)
                else:
                    return {
                        "status": "error",
                        "confidence": 0.0,
                        "potential_issues": [f"Target entity '{target_spec}' is not callable"],
                        "alignment_check": "failed",
                        "tactical_resonance": 0.0,
                        "crystallization_potential": 0.0,
                        "error_type": "TARGET_NOT_CALLABLE",
                        "target_spec": target_spec,
                        "execution_time": (datetime.now() - execution_start).total_seconds()
                    }
            else:
                return {
                    "status": "error",
                    "confidence": 0.0,
                    "potential_issues": [f"Unable to determine execution strategy for target '{target_spec}'"],
                    "alignment_check": "failed",
                    "tactical_resonance": 0.0,
                    "crystallization_potential": 0.0,
                    "error_type": "EXECUTION_STRATEGY_UNKNOWN",
                    "target_spec": target_spec,
                    "execution_time": (datetime.now() - execution_start).total_seconds()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "confidence": 0.0,
                "potential_issues": [f"Execution failed for SPR '{spr_id}': {str(e)}"],
                "alignment_check": "failed",
                "tactical_resonance": 0.0,
                "crystallization_potential": 0.0,
                "error_type": "EXECUTION_ERROR",
                "execution_exception": str(e),
                "traceback": traceback.format_exc(),
                "parameters_provided": parameters,
                "execution_time": (datetime.now() - execution_start).total_seconds()
            }
        
        # Step 6: IAR Validation
        if not isinstance(result_dict, dict):
            return {
                "status": "error",
                "confidence": 0.0,
                "potential_issues": [f"Implementation for SPR '{spr_id}' returned non-dict result: {type(result_dict)}"],
                "alignment_check": "failed",
                "tactical_resonance": 0.0,
                "crystallization_potential": 0.0,
                "error_type": "NON_IAR_COMPLIANT_RESULT",
                "raw_result": str(result_dict),
                "execution_time": (datetime.now() - execution_start).total_seconds()
            }
        
        # Check for required IAR fields
        required_iar_fields = ["status", "confidence", "potential_issues", "alignment_check"]
        missing_fields = [field for field in required_iar_fields if field not in result_dict]
        
        if missing_fields:
            # Wrap non-compliant result in IAR structure
            return {
                "status": "partial_success",
                "confidence": 0.5,
                "potential_issues": [f"Implementation for SPR '{spr_id}' returned incomplete IAR, missing: {missing_fields}"],
                "alignment_check": "degraded",
                "tactical_resonance": 0.5,
                "crystallization_potential": 0.3,
                "error_type": "INCOMPLETE_IAR",
                "raw_result": result_dict,
                "missing_iar_fields": missing_fields,
                "execution_time": (datetime.now() - execution_start).total_seconds()
            }
        
        # Step 7: Return Validated IAR
        # Add bridge execution metadata
        result_dict["bridge_execution_time"] = (datetime.now() - execution_start).total_seconds()
        result_dict["spr_id_invoked"] = spr_id
        result_dict["bridge_status"] = "success"
        
        return result_dict
        
    except Exception as e:
        # Catch-all error handler
        return {
            "status": "error",
            "confidence": 0.0,
            "potential_issues": [f"Unexpected error in SPR bridge for '{spr_id}': {str(e)}"],
            "alignment_check": "failed",
            "tactical_resonance": 0.0,
            "crystallization_potential": 0.0,
            "error_type": "BRIDGE_INTERNAL_ERROR",
            "exception": str(e),
            "traceback": traceback.format_exc(),
            "execution_time": (datetime.now() - execution_start).total_seconds()
        }

# --- END OF FILE Three_PointO_ArchE/spr_action_bridge.py --- 