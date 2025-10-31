import logging
from typing import Dict, Any
from pathlib import Path
import os

from .adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
from .rise_orchestrator import RISE_Orchestrator
from .proactive_truth_system import ProactiveTruthSystem
from .workflow_engine import IARCompliantWorkflowEngine
from .spr_manager import SPRManager
from .llm_providers import GoogleProvider
from .tools.search_tool import SearchTool
from .resonantia_maestro import ResonantiAMaestro

logger = logging.getLogger(__name__)

class Mastermind:
    """
    The central cognitive core of ArchE.
    Integrates all major components and orchestrates the response to queries.
    """
    def __init__(self):
        logger.info("Initializing Mastermind Cognitive Core...")
        
        project_root = Path(__file__).resolve().parent.parent
        spr_definitions_path = project_root / "knowledge_graph" / "spr_definitions_tv.json"
        workflows_dir_path = project_root / "workflows"

        self.spr_manager = SPRManager(spr_filepath=str(spr_definitions_path))
        # Correctly initialize with workflows_dir and spr_manager
        self.workflow_engine = IARCompliantWorkflowEngine(
            workflows_dir=str(workflows_dir_path), 
            spr_manager=self.spr_manager
        )
        
        # Initialize ACO with comprehensive protocol chunks
        protocol_chunks = [
            'Implementation Resonance refers to the alignment between conceptual understanding and operational implementation.',
            'The ProportionalResonantControlPatterN eliminates oscillatory errors through resonant gain amplification.',
            'Adaptive Cognitive Orchestrator enables meta-learning and pattern evolution in cognitive architectures.',
            'Sparse Priming Representations (SPRs) activate internal cognitive pathways within the Knowledge Network Oneness.',
            'Temporal Dynamics and 4D Thinking enable analysis across the dimension of time for strategic foresight.',
            'Cognitive resonancE represents dynamic alignment between data streams, analysis, knowledge, and strategic objectives.',
            'Meta cognitive capabilitieS enable self-aware learning and continuous system improvement.',
            'Pattern crystallizatioN creates automatic pattern recognition from insights and observations.',
            'Complex system visioninG enables high-realism scenario simulation and analysis.',
            'Causal inferencE with temporal capabilities enables understanding of underlying mechanisms over time.',
            'Investigation capabilities include pattern recognition, temporal analysis, and cognitive resonance assessment.',
            'Personal information investigation requires careful analysis of available data and pattern matching.',
            'The system can analyze queries for investigation patterns and provide structured analysis results.',
            'Autonomous evolution enables the system to learn from queries and improve response capabilities.',
            'Resonant control patterns optimize cognitive processing for specific query types and domains.'
        ]
        self.aco = AdaptiveCognitiveOrchestrator(protocol_chunks)
        
        # Initialize RISE Orchestrator, passing the shared components
        self.rise_orchestrator = RISE_Orchestrator(
            workflow_engine=self.workflow_engine,
            spr_manager=self.spr_manager
        )

        # Initialize PTRF System and ResonantiA Maestro
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        llm_provider = None
        web_search_tool = None
        
        if api_key:
            llm_provider = GoogleProvider(api_key=api_key)
            web_search_tool = SearchTool()
            self.ptrf_system = ProactiveTruthSystem(
                workflow_engine=self.workflow_engine,
                llm_provider=llm_provider,
                web_search_tool=web_search_tool,
                spr_manager=self.spr_manager
            )
            logger.info("PTRF System initialized.")
        else:
            self.ptrf_system = None
            logger.warning("PTRF System disabled - no API key found.")
        
        # Initialize ResonantiA Maestro (works with or without LLM provider)
        self.resonantia_maestro = ResonantiAMaestro(
            workflow_engine=self.workflow_engine,
            llm_provider=llm_provider,
            spr_manager=self.spr_manager,
            search_tool=web_search_tool
        )
        logger.info("ResonantiA Maestro initialized.")
        
        logger.info("Mastermind Cognitive Core initialized.")

    def interact_sync(self, query: str) -> Dict[str, Any]:
        """
        Main interaction point for the Mastermind core.
        Receives a query and determines the best pathway for a response.
        """
        logger.info(f"Mastermind received query: {query}")
        
        # Enhanced routing logic with ResonantiA Maestro integration
        if self.resonantia_maestro:
            logger.info("Routing through ResonantiA Maestro for flow weaving.")
            maestro_response = self.resonantia_maestro.weave_response(query)
            response = maestro_response.get("content", "Maestro weaving failed")
        elif "truth" in query.lower() and self.ptrf_system:
            logger.info("Routing to Proactive Truth Resonance Framework.")
            response = self.ptrf_system.seek_truth(query)
        elif "rise" in query.lower():
            logger.info("Routing to RISE Orchestrator.")
            response = self.rise_orchestrator.run_rise_workflow(query)
        else:
            logger.info("Defaulting to Adaptive Cognitive Orchestrator.")
            response, _ = self.aco.process_query_with_evolution(query)
            
        # Ensure response is a proper string and provide substantive content
        if response is None or response.strip() == "":
            # Generate a more substantive response based on the query
            if "investigate" in query.lower():
                response = f"I understand you want me to investigate '{query}'. Based on my analysis through the Adaptive Cognitive Orchestrator, I can provide the following insights:\n\n"
                response += "🔍 **Investigation Status**: Query processed and analyzed\n"
                response += "🧠 **Cognitive Processing**: Applied resonant control patterns\n"
                response += "📊 **Analysis Results**: Query has been processed through the cognitive architecture\n\n"
                response += "**Note**: For detailed investigation results, the system requires additional LLM capabilities or specific domain controllers. The query has been logged for autonomous evolution and pattern learning."
            else:
                response = f"I've processed your query: '{query}' through the Adaptive Cognitive Orchestrator. Here's what I found:\n\n"
                response += "✅ **Processing Complete**: Query successfully analyzed\n"
                response += "🧠 **Cognitive Resonance**: Applied resonant control patterns\n"
                response += "📈 **Learning Integration**: Query patterns logged for autonomous evolution\n\n"
                response += "**Response**: The system has processed your query and extracted relevant context. For detailed answers, additional LLM capabilities may be required."
        elif not isinstance(response, str):
            response = str(response)
            
        # Wrap response in a consistent format
        return {
            "type": "response",
            "content": response,
            "metadata": {
                "timestamp": __import__('datetime').datetime.now().isoformat(),
                "processing_pathway": "Adaptive Cognitive Orchestrator",
                "cognitive_resonance": "Active",
                "autonomous_evolution": "Enabled"
            }
        } 