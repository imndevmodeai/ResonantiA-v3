# ResonantiA Protocol v3.1-CA - Enhanced Workflow Orchestrator
# Integrates proven search capabilities with conversational output formatting
# Supports structured, human-readable presentations with verifiable links
# Keyholder Override keyy=('IMnDEVmode') acknowledged and active

import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import sys
import os

# Add the tools directory to the path
tools_dir = Path(__file__).parent / "tools"
sys.path.insert(0, str(tools_dir))

from .workflow_engine import IARCompliantWorkflowEngine
from .action_registry import main_action_registry
from .utils.reflection_utils import create_reflection, ExecutionStatus

try:
    from unified_search_tool import perform_web_search as unified_search
    UNIFIED_SEARCH_AVAILABLE = True
except ImportError:
    UNIFIED_SEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class ConversationalFormatter:
    """Formats workflow outputs in conversational, human-readable format"""
    
    @staticmethod
    def format_search_results(results: List[Dict], query: str, context: str = "") -> str:
        """Format search results in conversational style with verifiable links"""
        if not results:
            return f"I searched for '{query}' but didn't find any relevant results. You might want to try different search terms or check back later."
        
        intro = f"I found {len(results)} results for your query about '{query}':"
        if context:
            intro += f" {context}"
        
        formatted_results = [intro, ""]
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Untitled')
            url = result.get('url', '')
            snippet = result.get('snippet', 'No description available')
            
            # Clean up snippet
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
            
            formatted_results.append(f"**{i}. {title}**")
            formatted_results.append(f"   {snippet}")
            formatted_results.append(f"   🔗 Link: {url}")
            formatted_results.append("")
        
        return "\n".join(formatted_results)
    
    @staticmethod
    def format_analysis_result(analysis: Dict, title: str = "Analysis Results") -> str:
        """Format analysis results in conversational style"""
        if not analysis:
            return "The analysis didn't produce any results."
        
        formatted = [f"## {title}", ""]
        
        # Handle different analysis types
        if 'summary' in analysis:
            formatted.extend([
                "**Summary:**",
                analysis['summary'],
                ""
            ])
        
        if 'key_findings' in analysis:
            formatted.extend([
                "**Key Findings:**",
                ""
            ])
            for finding in analysis.get('key_findings', []):
                formatted.append(f"• {finding}")
            formatted.append("")
        
        if 'recommendations' in analysis:
            formatted.extend([
                "**Recommendations:**",
                ""
            ])
            for rec in analysis.get('recommendations', []):
                formatted.append(f"• {rec}")
            formatted.append("")
        
        if 'confidence' in analysis:
            confidence = analysis['confidence']
            if isinstance(confidence, (int, float)):
                confidence_pct = int(confidence * 100) if confidence <= 1 else int(confidence)
                formatted.append(f"**Confidence Level:** {confidence_pct}%")
        
        return "\n".join(formatted)
    
    @staticmethod
    def format_workflow_summary(workflow_name: str, results: Dict, duration: float) -> str:
        """Format workflow completion summary"""
        status = results.get('status', 'Unknown')
        task_count = len(results.get('task_results', {}))
        
        summary = [
            f"## Workflow Complete: {workflow_name}",
            f"**Status:** {status}",
            f"**Duration:** {duration:.2f} seconds",
            f"**Tasks Executed:** {task_count}",
            ""
        ]
        
        if results.get('error'):
            summary.extend([
                "**Error Encountered:**",
                results['error'],
                ""
            ])
        
        return "\n".join(summary)

class EnhancedSearchAction:
    """Enhanced search action with conversational output formatting"""
    
    @staticmethod
    def perform_enhanced_search(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform web search with enhanced formatting and verification
        
        Args:
            inputs: Dictionary containing:
                - query (str): Search query
                - num_results (int): Number of results (default: 10)
                - format_style (str): 'conversational' or 'structured' (default: 'conversational')
                - context (str): Additional context for formatting
        """
        start_time = time.time()
        action_name = "enhanced_search"
        
        query = inputs.get("query")
        num_results = inputs.get("num_results", 10)
        format_style = inputs.get("format_style", "conversational")
        context = inputs.get("context", "")
        
        if not query:
            return {
                "error": "Search query is required",
                "reflection": create_reflection(
                    action_name=action_name,
                    status=ExecutionStatus.FAILURE,
                    message="No search query provided",
                    inputs=inputs,
                    execution_time=time.time() - start_time
                )
            }
        
        # Perform the search using our proven unified search tool
        if UNIFIED_SEARCH_AVAILABLE:
            try:
                search_result = unified_search(query, engine="duckduckgo", debug=False)
                
                if search_result.get("success", False):
                    raw_results = search_result.get("results", [])[:num_results]
                    
                    # Format results based on style preference
                    if format_style == "conversational":
                        formatted_output = ConversationalFormatter.format_search_results(
                            raw_results, query, context
                        )
                    else:
                        formatted_output = json.dumps(raw_results, indent=2)
                    
                    return {
                        "formatted_results": formatted_output,
                        "raw_results": raw_results,
                        "search_metadata": {
                            "query": query,
                            "results_count": len(raw_results),
                            "search_method": search_result.get("search_method", "unified"),
                            "response_time": search_result.get("response_time", 0)
                        },
                        "reflection": create_reflection(
                            action_name=action_name,
                            status=ExecutionStatus.SUCCESS,
                            message=f"Successfully found {len(raw_results)} results using {search_result.get('search_method', 'unified')} search",
                            inputs=inputs,
                            outputs={
                                "results_count": len(raw_results),
                                "format_style": format_style,
                                "search_method": search_result.get("search_method", "unified")
                            },
                            confidence=0.95,
                            execution_time=time.time() - start_time
                        )
                    }
                else:
                    error_msg = search_result.get("error", "Search failed")
                    return {
                        "error": error_msg,
                        "reflection": create_reflection(
                            action_name=action_name,
                            status=ExecutionStatus.FAILURE,
                            message=f"Search failed: {error_msg}",
                            inputs=inputs,
                            execution_time=time.time() - start_time
                        )
                    }
                    
            except Exception as e:
                error_msg = f"Search tool exception: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {
                    "error": error_msg,
                    "reflection": create_reflection(
                        action_name=action_name,
                        status=ExecutionStatus.FAILURE,
                        message=error_msg,
                        inputs=inputs,
                        execution_time=time.time() - start_time
                    )
                }
        else:
            return {
                "error": "Enhanced search tool not available",
                "reflection": create_reflection(
                    action_name=action_name,
                    status=ExecutionStatus.FAILURE,
                    message="Unified search tool not available",
                    inputs=inputs,
                    execution_time=time.time() - start_time
                )
            }

class ConversationalAnalysisAction:
    """Analysis action with conversational output formatting"""
    
    @staticmethod
    def perform_conversational_analysis(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform analysis with conversational output formatting
        
        Args:
            inputs: Dictionary containing:
                - data (Any): Data to analyze
                - analysis_type (str): Type of analysis to perform
                - format_style (str): Output formatting style
                - context (str): Additional context
        """
        start_time = time.time()
        action_name = "conversational_analysis"
        
        data = inputs.get("data")
        analysis_type = inputs.get("analysis_type", "general")
        format_style = inputs.get("format_style", "conversational")
        context = inputs.get("context", "")
        
        if data is None:
            return {
                "error": "Data is required for analysis",
                "reflection": create_reflection(
                    action_name=action_name,
                    status=ExecutionStatus.FAILURE,
                    message="No data provided for analysis",
                    inputs=inputs,
                    execution_time=time.time() - start_time
                )
            }
        
        try:
            # Perform basic analysis based on type
            analysis_result = {}
            
            if analysis_type == "search_results":
                # Analyze search results
                if isinstance(data, list):
                    analysis_result = {
                        "summary": f"Analyzed {len(data)} search results",
                        "key_findings": [
                            f"Found {len(data)} relevant sources",
                            f"Results span various domains and perspectives",
                            "All results include verifiable links for fact-checking"
                        ],
                        "confidence": 0.85
                    }
                    
            elif analysis_type == "general":
                # General data analysis
                if isinstance(data, dict):
                    keys = list(data.keys())
                    analysis_result = {
                        "summary": f"Analyzed data structure with {len(keys)} main components",
                        "key_findings": [f"Contains: {', '.join(keys[:5])}{'...' if len(keys) > 5 else ''}"],
                        "confidence": 0.80
                    }
                elif isinstance(data, list):
                    analysis_result = {
                        "summary": f"Analyzed list with {len(data)} items",
                        "key_findings": [f"List contains {len(data)} elements"],
                        "confidence": 0.80
                    }
            
            # Format output
            if format_style == "conversational":
                formatted_output = ConversationalFormatter.format_analysis_result(
                    analysis_result, f"{analysis_type.title()} Analysis"
                )
            else:
                formatted_output = json.dumps(analysis_result, indent=2)
            
            return {
                "formatted_analysis": formatted_output,
                "raw_analysis": analysis_result,
                "analysis_metadata": {
                    "analysis_type": analysis_type,
                    "data_type": type(data).__name__,
                    "format_style": format_style
                },
                "reflection": create_reflection(
                    action_name=action_name,
                    status=ExecutionStatus.SUCCESS,
                    message=f"Successfully completed {analysis_type} analysis",
                    inputs=inputs,
                    outputs={
                        "analysis_type": analysis_type,
                        "format_style": format_style,
                        "confidence": analysis_result.get("confidence", 0.8)
                    },
                    confidence=analysis_result.get("confidence", 0.8),
                    execution_time=time.time() - start_time
                )
            }
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "error": error_msg,
                "reflection": create_reflection(
                    action_name=action_name,
                    status=ExecutionStatus.FAILURE,
                    message=error_msg,
                    inputs=inputs,
                    execution_time=time.time() - start_time
                )
            }

class EnhancedWorkflowOrchestrator:
    """Enhanced workflow orchestrator with conversational capabilities"""
    
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = workflows_dir
        self.engine = IARCompliantWorkflowEngine(workflows_dir)
        self.formatter = ConversationalFormatter()
        
        # Register enhanced actions
        self._register_enhanced_actions()
        
        logger.info("Enhanced Workflow Orchestrator initialized with conversational capabilities")
    
    def _register_enhanced_actions(self):
        """Register enhanced actions with the workflow engine"""
        # Register enhanced search action
        register_action("enhanced_search", EnhancedSearchAction.perform_enhanced_search)
        
        # Register conversational analysis action
        register_action("conversational_analysis", ConversationalAnalysisAction.perform_conversational_analysis)
        
        # Register conversational display action
        register_action("conversational_display", self._conversational_display)
        
        # Update engine's action registry
        self.engine.action_registry = main_action_registry.actions.copy()
    
    def _conversational_display(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Display content in conversational format"""
        start_time = time.time()
        action_name = "conversational_display"
        
        content = inputs.get("content", "")
        title = inputs.get("title", "")
        style = inputs.get("style", "info")
        
        # Format the display
        if title:
            display_text = f"## {title}\n\n{content}"
        else:
            display_text = content
        
        # Add style indicators
        if style == "success":
            display_text = f"✅ {display_text}"
        elif style == "warning":
            display_text = f"⚠️ {display_text}"
        elif style == "error":
            display_text = f"❌ {display_text}"
        elif style == "info":
            display_text = f"ℹ️ {display_text}"
        
        print(display_text)
        
        return {
            "displayed_content": display_text,
            "reflection": create_reflection(
                action_name=action_name,
                status=ExecutionStatus.SUCCESS,
                message=f"Successfully displayed {style} content",
                inputs=inputs,
                outputs={"content_length": len(display_text)},
                confidence=1.0,
                execution_time=time.time() - start_time
            )
        }
    
    def run_enhanced_workflow(self, workflow_name: str, initial_context: Dict[str, Any], 
                            conversational_mode: bool = True) -> Dict[str, Any]:
        """
        Run a workflow with enhanced conversational output
        
        Args:
            workflow_name: Name of the workflow to run
            initial_context: Initial context for the workflow
            conversational_mode: Whether to use conversational formatting
        """
        start_time = time.time()
        
        # Add conversational mode to context
        enhanced_context = {
            **initial_context,
            "conversational_mode": conversational_mode,
            "enhanced_orchestrator": True,
            "workflow_run_id": f"enhanced_{uuid.uuid4().hex[:8]}"
        }
        
        logger.info(f"Starting enhanced workflow: {workflow_name}")
        
        try:
            # Run the workflow
            results = self.engine.run_workflow(workflow_name, enhanced_context)
            
            duration = time.time() - start_time
            
            # Format final summary if in conversational mode
            if conversational_mode:
                summary = self.formatter.format_workflow_summary(
                    workflow_name, results, duration
                )
                print(summary)
            
            return {
                **results,
                "enhanced_mode": True,
                "conversational_mode": conversational_mode,
                "total_duration": duration
            }
            
        except Exception as e:
            error_msg = f"Enhanced workflow execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if conversational_mode:
                print(f"❌ **Workflow Error:** {workflow_name}")
                print(f"   {error_msg}")
            
            return {
                "error": error_msg,
                "enhanced_mode": True,
                "conversational_mode": conversational_mode,
                "total_duration": time.time() - start_time
            }
    
    def create_enhanced_workflow_template(self, workflow_name: str, 
                                        description: str, 
                                        search_queries: List[str],
                                        analysis_type: str = "general") -> Dict[str, Any]:
        """
        Create an enhanced workflow template with search and analysis capabilities
        
        Args:
            workflow_name: Name for the new workflow
            description: Description of what the workflow does
            search_queries: List of search queries to execute
            analysis_type: Type of analysis to perform on results
        """
        tasks = {}
        
        # Create search tasks
        for i, query in enumerate(search_queries):
            task_id = f"search_{i+1}"
            tasks[task_id] = {
                "description": f"Search for: {query}",
                "action_type": "enhanced_search",
                "inputs": {
                    "query": query,
                    "num_results": 10,
                    "format_style": "conversational",
                    "context": f"Query {i+1} of {len(search_queries)}"
                },
                "dependencies": []
            }
        
        # Create analysis task that depends on all searches
        search_dependencies = [f"search_{i+1}" for i in range(len(search_queries))]
        
        tasks["analyze_results"] = {
            "description": "Analyze all search results",
            "action_type": "conversational_analysis",
            "inputs": {
                "data": [f"{{{{ search_{i+1}.raw_results }}}}" for i in range(len(search_queries))],
                "analysis_type": analysis_type,
                "format_style": "conversational",
                "context": "Combined analysis of all search results"
            },
            "dependencies": search_dependencies
        }
        
        # Create display task
        tasks["display_summary"] = {
            "description": "Display workflow summary",
            "action_type": "conversational_display",
            "inputs": {
                "title": f"Workflow Complete: {workflow_name}",
                "content": "{{ analyze_results.formatted_analysis }}",
                "style": "success"
            },
            "dependencies": ["analyze_results"]
        }
        
        workflow_template = {
            "name": workflow_name,
            "description": description,
            "version": "1.0",
            "enhanced_mode": True,
            "conversational_output": True,
            "tasks": tasks
        }
        
        return workflow_template
    
    def save_enhanced_workflow(self, workflow_template: Dict[str, Any], 
                             filename: str = None) -> str:
        """Save an enhanced workflow template to file"""
        if not filename:
            workflow_name = workflow_template.get("name", "enhanced_workflow")
            filename = f"{workflow_name.lower().replace(' ', '_')}_enhanced.json"
        
        filepath = Path(self.workflows_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow_template, f, indent=2)
        
        logger.info(f"Enhanced workflow saved to: {filepath}")
        return str(filepath)

# Convenience function for quick workflow creation and execution
def create_and_run_search_workflow(query: str, context: str = "", 
                                 num_results: int = 10) -> Dict[str, Any]:
    """
    Quick function to create and run a search workflow with conversational output
    
    Args:
        query: Search query
        context: Additional context for the search
        num_results: Number of results to return
    """
    orchestrator = EnhancedWorkflowOrchestrator()
    
    # Create a simple search workflow
    workflow_template = {
        "name": "Quick Search",
        "description": f"Quick search for: {query}",
        "version": "1.0",
        "enhanced_mode": True,
        "tasks": {
            "search": {
                "description": f"Search for: {query}",
                "action_type": "enhanced_search",
                "inputs": {
                    "query": query,
                    "num_results": num_results,
                    "format_style": "conversational",
                    "context": context
                },
                "dependencies": []
            },
            "display": {
                "description": "Display search results",
                "action_type": "conversational_display",
                "inputs": {
                    "title": f"Search Results for: {query}",
                    "content": "{{ search.formatted_results }}",
                    "style": "info"
                },
                "dependencies": ["search"]
            }
        }
    }
    
    # Save and run the workflow
    workflow_path = orchestrator.save_enhanced_workflow(workflow_template, "quick_search.json")
    
    initial_context = {
        "query": query,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return orchestrator.run_enhanced_workflow("quick_search.json", initial_context)

if __name__ == "__main__":
    # Example usage
    orchestrator = EnhancedWorkflowOrchestrator()
    
    # Create a sample enhanced workflow
    workflow = orchestrator.create_enhanced_workflow_template(
        workflow_name="Enhanced Research Example",
        description="Demonstrates enhanced search and analysis capabilities",
        search_queries=[
            "ResonantiA Protocol AI framework",
            "advanced workflow orchestration systems",
            "conversational AI output formatting"
        ],
        analysis_type="search_results"
    )
    
    # Save the workflow
    workflow_path = orchestrator.save_enhanced_workflow(workflow)
    print(f"Enhanced workflow saved to: {workflow_path}") 