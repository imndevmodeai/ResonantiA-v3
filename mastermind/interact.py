#!/usr/bin/env python3
"""
ArchE Interactive Agent - IAR Compliant Workflow Engine Interface
This script provides a command-line interface to execute workflows using
the IARCompliantWorkflowEngine, ensuring adherence to the ResonantiA Protocol.
"""

import sys
import os
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
import argparse
from datetime import datetime

# Add the project root to the path to allow direct imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.utils.reflection_utils import ExecutionStatus

# --- PTRF Integration: Import real dependencies ---
from Three_PointO_ArchE.proactive_truth_system import ProactiveTruthSystem
from Three_PointO_ArchE.tools.search_tool import SearchTool
from Three_PointO_ArchE.spr_manager import SPRManager
# --- End PTRF Integration ---

# --- AUTONOMOUS EVOLUTION Integration: Import ACO system ---
from Three_PointO_ArchE.adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
# --- End AUTONOMOUS EVOLUTION Integration ---

# --- RISE v2.0 Genesis Protocol Integration ---
try:
    from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
    RISE_V2_ENABLED = True
except ImportError as e:
    logger.warning(f"RISE v2.0 Genesis Protocol not available: {e}")
    RISE_V2_ENABLED = False
# --- End RISE v2.0 Integration ---

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ArchE_Workflow_CLI")

def check_prerequisites():
    """
    Perform prerequisite checks before system startup.
    Exits with clear error messages if requirements are not met.
    """
    print("🔍 ArchE System Prerequisites Check")
    print("=" * 50)
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ CRITICAL ERROR: GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set.")
        print("   This is required for the Proactive Truth Resonance Framework.")
        print("   Please:")
        print("   1. Copy env.template to .env")
        print("   2. Add your Google Gemini API key to the .env file")
        print("   3. Restart the system")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    else:
        print("✅ GEMINI_API_KEY found")
    
    # Check critical file paths
    critical_files = [
        ("knowledge_graph/spr_definitions_tv.json", "SPR Definitions"),
        ("workflows/", "Workflows Directory"),
        ("chronicles/genesis_chronicle.json", "Genesis Chronicle")
    ]
    
    for file_path, description in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            if full_path.is_file():
                # Check if file is not empty
                if full_path.stat().st_size > 0:
                    print(f"✅ {description}: {file_path}")
                else:
                    print(f"⚠️  WARNING: {description} is empty: {file_path}")
            else:
                print(f"✅ {description}: {file_path}")
        else:
            print(f"⚠️  WARNING: {description} not found: {file_path}")
    
    # Check Python dependencies
    try:
        import google.generativeai
        print("✅ Google Generative AI library available")
    except ImportError:
        print("❌ ERROR: google.generativeai library not installed")
        print("   Run: pip install google-generativeai")
        sys.exit(1)
    
    try:
        import requests
        print("✅ Requests library available")
    except ImportError:
        print("❌ ERROR: requests library not installed")
        print("   Run: pip install requests")
        sys.exit(1)
    
    print("=" * 50)
    print("✅ Prerequisites check completed successfully")
    print()

class ArchEWorkflowCLI:
    """
    A command-line interface for interacting with ArchE's IARCompliantWorkflowEngine.
    """
    
    def __init__(self):
        """Initialize the CLI and the workflow engine."""
        self.workflows_dir = project_root / "workflows"
        self.available_workflows = self._discover_workflows()
        self.engine = IARCompliantWorkflowEngine()
        logger.info(f"ArchE Workflow CLI initialized. Found {len(self.available_workflows)} workflows.")

        # --- PTRF Integration: Instantiate the live PTRF engine and its dependencies ---
        try:
            logger.info("Initializing Proactive Truth Resonance Framework engine...")
            # Use Google/Gemini provider since we have the API key configured
            from Three_PointO_ArchE.llm_providers import GoogleProvider
            
            # Get API key from environment
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set.")
            
            llm_provider = GoogleProvider(api_key=api_key) # Use Google/Gemini provider
            web_search_tool = SearchTool() # This might need an API key
            # Initialize SPRManager with the correct path to SPR definitions
            spr_definitions_path = str(project_root / "knowledge_graph" / "spr_definitions_tv.json")
            spr_manager = SPRManager(spr_filepath=spr_definitions_path)
            
            self.truth_seeker = ProactiveTruthSystem(
                workflow_engine=self.engine,
                llm_provider=llm_provider,
                web_search_tool=web_search_tool,
                spr_manager=spr_manager
            )
            self.ptrf_enabled = True
            logger.info("Proactive Truth Resonance Framework engine is ONLINE.")
            
        except Exception as e:
            logger.error(f"Failed to initialize PTRF: {e}", exc_info=True)
            self.ptrf_enabled = False
            self.truth_seeker = None
            logger.warning("PTRF is DISABLED. The 'truth_seek' command will not be available.")
        # --- End PTRF Integration ---

        # --- AUTONOMOUS EVOLUTION Integration: Initialize ACO system ---
        try:
            logger.info("Initializing Adaptive Cognitive Orchestrator with Autonomous Evolution...")
            
            # Initialize ACO with protocol chunks
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
                'Causal inferencE with temporal capabilities enables understanding of underlying mechanisms over time.'
            ]
            
            self.aco = AdaptiveCognitiveOrchestrator(protocol_chunks)
            self.autonomous_evolution_enabled = True
            logger.info("Adaptive Cognitive Orchestrator with Autonomous Evolution is ONLINE.")
            
            # Initialize Universal Query Enhancement System
            self.universal_enhancement_active = True
            self.query_enhancement_history = []
            self.domain_evolution_tracker = {}
            logger.info("Universal Query Enhancement System ACTIVATED - All queries will be processed through autonomous evolution.")
            
        except Exception as e:
            logger.error(f"Failed to initialize ACO: {e}", exc_info=True)
            self.autonomous_evolution_enabled = False
            self.universal_enhancement_active = False
            self.aco = None
            logger.warning("ACO is DISABLED. Autonomous evolution commands will not be available.")
        # --- End AUTONOMOUS EVOLUTION Integration ---

        # --- RISE v2.0 Genesis Protocol Integration ---
        try:
            if RISE_V2_ENABLED:
                logger.info("Initializing RISE v2.0 Genesis Protocol with Utopian Upgrade...")
                
                # Get the correct workflows directory path
                workflows_dir = project_root / "workflows"
                logger.info(f"RISE workflows directory: {workflows_dir}")
                
                # Initialize RISE_Orchestrator with the correct workflows directory
                self.rise_orchestrator = RISE_Orchestrator(workflows_dir=str(workflows_dir))
                self.rise_v2_enabled = True
                
                # Check for advanced features
                self.synergistic_fusion_enabled = hasattr(self.rise_orchestrator, 'synergistic_fusion_enabled') and self.rise_orchestrator.synergistic_fusion_enabled
                self.utopian_synthesis_enabled = hasattr(self.rise_orchestrator, 'utopian_synthesis_enabled') and self.rise_orchestrator.utopian_synthesis_enabled
                
                logger.info("RISE v2.0 Genesis Protocol is ONLINE.")
                if self.synergistic_fusion_enabled:
                    logger.info("🔮 Synergistic Fusion Protocol: ENABLED")
                if self.utopian_synthesis_enabled:
                    logger.info("🌟 Utopian Solution Synthesizer: ENABLED")
            else:
                self.rise_v2_enabled = False
                self.rise_orchestrator = None
                self.synergistic_fusion_enabled = False
                self.utopian_synthesis_enabled = False
                logger.warning("RISE v2.0 Genesis Protocol is DISABLED.")
        except Exception as e:
            logger.error(f"Failed to initialize RISE v2.0: {e}", exc_info=True)
            self.rise_v2_enabled = False
            self.rise_orchestrator = None
            self.synergistic_fusion_enabled = False
            self.utopian_synthesis_enabled = False
            logger.warning("RISE v2.0 Genesis Protocol is DISABLED due to initialization error.")
        # --- End RISE v2.0 Integration ---

        # --- Autonomous Orchestration System Integration ---
        try:
            from Three_PointO_ArchE.autonomous_orchestrator import autonomous_orchestrator
            self.autonomous_orchestrator = autonomous_orchestrator
            self.ceo_mode_enabled = True
            logger.info("🤖 Autonomous Orchestration System: ENABLED")
            logger.info("CEO Mode: ACTIVE - Keyholder elevated to strategic oversight")
        except Exception as e:
            logger.error(f"Failed to initialize Autonomous Orchestration System: {e}")
            self.ceo_mode_enabled = False
        # --- End Autonomous Orchestration System Integration ---

    def _discover_workflows(self) -> List[str]:
        """Scans the workflows directory for available .json files."""
        if not self.workflows_dir.exists():
            logger.warning(f"Workflows directory not found: {self.workflows_dir}")
            return []
        
        workflows = []
        for workflow_file in self.workflows_dir.glob("*.json"):
            workflows.append(workflow_file.name)
        
        return sorted(workflows)
    
    def _apply_universal_enhancement(self, query: str) -> Dict[str, Any]:
        """
        Universal Query Enhancement System - Applies autonomous evolution to ALL queries.
        Implements As Above So Below principle from ResonantiA Protocol v3.1-CA.
        
        Args:
            query: Any query to be enhanced through autonomous evolution
            
        Returns:
            Dict containing enhanced processing results and evolution analysis
        """
        if not self.universal_enhancement_active:
            return {
                "enhanced": False, 
                "reason": "Universal enhancement not active",
                "enhanced_answer": "Universal enhancement not active",
                "analysis_type": "Disabled",
                "confidence": 0.0
            }
        
        try:
            # Process through ACO with evolution analysis
            context, metrics = self.aco.process_query_with_evolution(query)
            
            # Universal Enhancement Analysis
            enhancement_analysis = {
                "query_processed": True,
                "domain_activated": metrics.get('active_domain', 'Unknown'),
                "processing_time": metrics.get('processing_time', 0),
                "context_generated": bool(context),
                "context_length": len(context) if context else 0,
                "evolution_active": 'evolution_analysis' in metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            # Evolution Analysis Integration
            if 'evolution_analysis' in metrics:
                evo = metrics['evolution_analysis']
                enhancement_analysis.update({
                    "evolution_opportunity": evo['evolution_opportunity']['evolution_ready'],
                    "total_queries_analyzed": evo['total_fallback_queries'],
                    "evolution_candidates": evo['evolution_opportunity'].get('total_candidates', 0),
                    "evolution_status": evo['evolution_opportunity'].get('reason', 'analyzing')
                })
                
                # Track domain evolution patterns
                domain = metrics.get('active_domain', 'Unknown')
                if domain not in self.domain_evolution_tracker:
                    self.domain_evolution_tracker[domain] = {
                        "query_count": 0,
                        "evolution_opportunities": 0,
                        "successful_evolutions": 0,
                        "last_evolution": None
                    }
                
                self.domain_evolution_tracker[domain]["query_count"] += 1
                if evo['evolution_opportunity']['evolution_ready']:
                    self.domain_evolution_tracker[domain]["evolution_opportunities"] += 1
                    self.domain_evolution_tracker[domain]["last_evolution"] = datetime.now().isoformat()
            
            # Store in enhancement history
            self.query_enhancement_history.append({
                "query": query[:100] + "..." if len(query) > 100 else query,
                "enhancement_analysis": enhancement_analysis,
                "raw_context": context,
                "raw_metrics": metrics
            })
            
            # Maintain history size
            if len(self.query_enhancement_history) > 1000:
                self.query_enhancement_history = self.query_enhancement_history[-500:]
            
            # Generate enhanced answer for the main function
            enhanced_answer = self._generate_comprehensive_analysis(query, {
                "enhanced": True,
                "enhancement_analysis": enhancement_analysis,
                "context": context
            })
            
            return {
                "enhanced": True,
                "context": context,
                "metrics": metrics,
                "enhancement_analysis": enhancement_analysis,
                "universal_enhancement": True,
                "enhanced_answer": enhanced_answer,
                "analysis_type": enhancement_analysis.get("domain_activated", "Unknown"),
                "confidence": metrics.get('domain_confidence', 0.5),
                "comprehensive_analysis": enhanced_answer
            }
            
        except Exception as e:
            logger.error(f"Universal enhancement failed for query: {e}", exc_info=True)
            return {
                "enhanced": False,
                "reason": f"Enhancement error: {str(e)}",
                "universal_enhancement": False,
                "enhanced_answer": f"ACO analysis failed: {str(e)}",
                "analysis_type": "Error",
                "confidence": 0.0
            }
    
    def _generate_comprehensive_analysis(self, query: str, enhancement_result: Dict[str, Any]) -> str:
        """
        Generate comprehensive analysis for any query using autonomous evolution insights.
        Implements Complex system visioninG and Pattern crystallizatioN principles.
        """
        if not enhancement_result.get("enhanced", False):
            return "Query could not be enhanced through autonomous evolution system."
        
        analysis_components = []
        
        # Domain Analysis
        domain = enhancement_result["enhancement_analysis"]["domain_activated"]
        analysis_components.append(f"🎯 **DOMAIN ANALYSIS**: {domain}")
        
        # Context Analysis
        context = enhancement_result.get("context", "")
        if context:
            analysis_components.append(f"📊 **CONTEXT EXTRACTION**: {context}")
        
        # Evolution Analysis
        if enhancement_result["enhancement_analysis"]["evolution_active"]:
            evo_analysis = enhancement_result["enhancement_analysis"]
            analysis_components.append(f"🧠 **EVOLUTION ANALYSIS**:")
            analysis_components.append(f"   - Total queries analyzed: {evo_analysis.get('total_queries_analyzed', 0)}")
            analysis_components.append(f"   - Evolution status: {evo_analysis.get('evolution_status', 'unknown')}")
            
            if evo_analysis.get("evolution_opportunity", False):
                analysis_components.append(f"   - 🚀 **EVOLUTION OPPORTUNITY DETECTED**")
                analysis_components.append(f"   - Candidates ready: {evo_analysis.get('evolution_candidates', 0)}")
        
        # Pattern Analysis
        domain_tracker = self.domain_evolution_tracker.get(domain, {})
        if domain_tracker:
            analysis_components.append(f"📈 **PATTERN ANALYSIS** ({domain} domain):")
            analysis_components.append(f"   - Query count: {domain_tracker.get('query_count', 0)}")
            analysis_components.append(f"   - Evolution opportunities: {domain_tracker.get('evolution_opportunities', 0)}")
            analysis_components.append(f"   - Success rate: {domain_tracker.get('successful_evolutions', 0)}/{domain_tracker.get('evolution_opportunities', 0)}")
        
        # System Enhancement Status
        analysis_components.append(f"⚡ **UNIVERSAL ENHANCEMENT**: Active")
        analysis_components.append(f"   - Processing time: {enhancement_result['enhancement_analysis']['processing_time']:.3f}s")
        analysis_components.append(f"   - Context generated: {enhancement_result['enhancement_analysis']['context_generated']}")
        analysis_components.append(f"   - Autonomous evolution: {enhancement_result['enhancement_analysis']['evolution_active']}")
        
        return "\\n".join(analysis_components)

    def _handle_protocol_query(self, query: str) -> Dict[str, Any]:
        """
        Handle queries about the ResonantiA Protocol content.
        Returns a dictionary with the answer and metadata.
        """
        try:
            # Check if this is a protocol-related query
            protocol_keywords = [
                "resonantia", "protocol", "section", "mandate", "spr", 
                "cognitive resonance", "temporal resonance", "4d thinking",
                "implementation resonance", "as above so below"
            ]
            
            query_lower = query.lower()
            is_protocol_query = any(keyword in query_lower for keyword in protocol_keywords)
            
            if not is_protocol_query:
                return {
                    "is_protocol_query": False,
                    "answer": None,
                    "reason": "Query does not appear to be about the ResonantiA Protocol"
                }
            
            # Handle specific section queries
            if "section" in query_lower:
                return self._extract_protocol_section(query)
            
            # Handle mandate queries
            if "mandate" in query_lower:
                return self._extract_protocol_mandate(query)
            
            # Handle general protocol queries
            return self._search_protocol_content(query)
            
        except Exception as e:
            logger.error(f"Error handling protocol query: {e}", exc_info=True)
            return {
                "is_protocol_query": True,
                "answer": f"Error processing protocol query: {str(e)}",
                "error": True
            }
    
    def _extract_protocol_section(self, query: str) -> Dict[str, Any]:
        """Extract specific sections from the ResonantiA Protocol."""
        try:
            # Look for section numbers in the query
            import re
            section_match = re.search(r'section\s+(\d+\.?\d*)', query.lower())
            
            if not section_match:
                return {
                    "is_protocol_query": True,
                    "answer": "Please specify a section number (e.g., 'Section 2.9' or 'Section 3.1')",
                    "section_found": False
                }
            
            section_number = section_match.group(1)
            
            # Read the protocol file
            protocol_file = project_root / "protocol" / "ResonantiA_Protocol_v3.0.md"
            if not protocol_file.exists():
                return {
                    "is_protocol_query": True,
                    "answer": "Protocol file not found",
                    "error": True
                }
            
            with open(protocol_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the section - look for section headers like "(2.9 Temporal Resonance and 4D Thinking) [ENHANCED]"
            section_pattern = rf'\({re.escape(section_number)}[^)]*\)[^[]*\[[^\]]*\]'
            section_match = re.search(section_pattern, content, re.IGNORECASE | re.DOTALL)
            
            if not section_match:
                return {
                    "is_protocol_query": True,
                    "answer": f"Section {section_number} not found in the ResonantiA Protocol v3.0",
                    "section_found": False
                }
            
            # Extract the section content
            section_start = section_match.start()
            section_end = content.find('\n(', section_start + 1)
            if section_end == -1:
                section_end = len(content)
            
            section_content = content[section_start:section_end].strip()
            
            return {
                "is_protocol_query": True,
                "answer": f"**Section {section_number} from ResonantiA Protocol v3.0:**\n\n{section_content}",
                "section_found": True,
                "section_number": section_number
            }
            
        except Exception as e:
            logger.error(f"Error extracting protocol section: {e}", exc_info=True)
            return {
                "is_protocol_query": True,
                "answer": f"Error extracting protocol section: {str(e)}",
                "error": True
            }
    
    def _extract_protocol_mandate(self, query: str) -> Dict[str, Any]:
        """Extract specific mandates from the CRITICAL_MANDATES file."""
        try:
            # Look for mandate numbers in the query
            import re
            mandate_match = re.search(r'mandate\s+(\d+)', query.lower())
            
            if not mandate_match:
                return {
                    "is_protocol_query": True,
                    "answer": "Please specify a mandate number (e.g., 'Mandate 1' or 'Mandate 5')",
                    "mandate_found": False
                }
            
            mandate_number = mandate_match.group(1)
            
            # Read the mandates file
            mandates_file = project_root / "protocol" / "CRITICAL_MANDATES.md"
            if not mandates_file.exists():
                return {
                    "is_protocol_query": True,
                    "answer": "CRITICAL_MANDATES file not found",
                    "error": True
                }
            
            with open(mandates_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the mandate
            mandate_pattern = rf'## \(MANDATE {re.escape(mandate_number)}\)[^#]*'
            mandate_match = re.search(mandate_pattern, content, re.IGNORECASE | re.DOTALL)
            
            if not mandate_match:
                return {
                    "is_protocol_query": True,
                    "answer": f"Mandate {mandate_number} not found in CRITICAL_MANDATES",
                    "mandate_found": False
                }
            
            # Extract the mandate content
            mandate_start = mandate_match.start()
            mandate_end = content.find('\n## ', mandate_start + 1)
            if mandate_end == -1:
                mandate_end = len(content)
            
            mandate_content = content[mandate_start:mandate_end].strip()
            
            return {
                "is_protocol_query": True,
                "answer": f"**Mandate {mandate_number} from CRITICAL_MANDATES:**\n\n{mandate_content}",
                "mandate_found": True,
                "mandate_number": mandate_number
            }
            
        except Exception as e:
            logger.error(f"Error extracting protocol mandate: {e}", exc_info=True)
            return {
                "is_protocol_query": True,
                "answer": f"Error extracting protocol mandate: {str(e)}",
                "error": True
            }
    
    def _search_protocol_content(self, query: str) -> Dict[str, Any]:
        """Search for general protocol content."""
        try:
            # Search in both protocol files
            protocol_files = [
                project_root / "protocol" / "ResonantiA_Protocol_v3.0.md",
                project_root / "protocol" / "CRITICAL_MANDATES.md"
            ]
            
            results = []
            
            for file_path in protocol_files:
                if not file_path.exists():
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple keyword search
                query_terms = query.lower().split()
                matches = []
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if any(term in line_lower for term in query_terms):
                        # Get context around the match
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = '\n'.join(lines[start:end])
                        matches.append(context)
                
                if matches:
                    results.append({
                        "file": file_path.name,
                        "matches": matches[:3]  # Limit to 3 matches per file
                    })
            
            if not results:
                return {
                    "is_protocol_query": True,
                    "answer": f"No relevant content found for query: '{query}'. Try being more specific or use 'Section X.Y' or 'Mandate X' format.",
                    "content_found": False
                }
            
            # Format the results
            answer = f"**Search results for: '{query}'**\n\n"
            for result in results:
                answer += f"**File: {result['file']}**\n"
                for i, match in enumerate(result['matches'], 1):
                    answer += f"\nMatch {i}:\n```\n{match}\n```\n"
                answer += "\n"
            
            return {
                "is_protocol_query": True,
                "answer": answer,
                "content_found": True,
                "files_searched": [r["file"] for r in results]
            }
            
        except Exception as e:
            logger.error(f"Error searching protocol content: {e}", exc_info=True)
            return {
                "is_protocol_query": True,
                "answer": f"Error searching protocol content: {str(e)}",
                "error": True
            }

    def _analyze_query_for_cognitive_path(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query to determine the appropriate cognitive path through ACO/RISE.
        This replaces the flawed workflow routing with true cognitive intelligence.
        """
        try:
            query_lower = query.lower()
            
            # Define cognitive path indicators
            cognitive_paths = {
                "strategic_rise": {
                    "indicators": [
                        "crisis", "conflicting", "ground truth", "predictive forecast",
                        "geopolitical", "rapidly developing", "initial reports",
                        "proactive truth resonance", "rise engine", "strategic",
                        "complex", "high-stakes", "critical decision", "south china sea"
                    ],
                    "path": "rise_v2_0",
                    "priority": 10,
                    "description": "High-stakes strategic analysis requiring RISE v2.0 Genesis Protocol"
                },
                "truth_seeking": {
                    "indicators": [
                        "truth", "fact", "verify", "check", "validate", "confirm",
                        "accurate", "reliable", "authentic", "genuine", "proactive truth"
                    ],
                    "path": "ptrf",
                    "priority": 9,
                    "description": "Truth validation through Proactive Truth Resonance Framework"
                },
                "protocol_query": {
                    "indicators": [
                        "resonantia", "protocol", "section", "mandate", "spr", 
                        "cognitive resonance", "temporal resonance", "4d thinking",
                        "implementation resonance", "as above so below"
                    ],
                    "path": "protocol",
                    "priority": 8,
                    "description": "Protocol-related query requiring direct protocol access"
                },
                "enhanced_analysis": {
                    "indicators": [
                        "what is", "how does", "explain", "describe", "tell me about",
                        "search for", "find information about", "research", "analysis"
                    ],
                    "path": "aco_enhanced",
                    "priority": 5,
                    "description": "Standard query requiring ACO enhanced analysis"
                }
            }
            
            # Score each cognitive path based on indicator matches
            path_scores = {}
            for path_name, config in cognitive_paths.items():
                score = 0
                matched_indicators = []
                
                for indicator in config["indicators"]:
                    if indicator in query_lower:
                        score += 1
                        matched_indicators.append(indicator)
                
                if score > 0:
                    path_scores[path_name] = {
                        "score": score,
                        "priority": config["priority"],
                        "path": config["path"],
                        "description": config["description"],
                        "matched_indicators": matched_indicators,
                        "final_score": score * config["priority"]
                    }
            
            # Select the best cognitive path
            if not path_scores:
                # Default to enhanced analysis if no specific path matches
                selected_path = "enhanced_analysis"
                selected_path_type = "aco_enhanced"
                confidence = 0.3
            else:
                # Sort by final score (score * priority)
                sorted_paths = sorted(path_scores.items(), 
                                    key=lambda x: x[1]["final_score"], reverse=True)
                selected_path = sorted_paths[0][0]
                selected_path_type = sorted_paths[0][1]["path"]
                confidence = min(1.0, sorted_paths[0][1]["final_score"] / 10.0)
            
            return {
                "selected_path": selected_path,
                "selected_path_type": selected_path_type,
                "confidence": confidence,
                "path_scores": path_scores,
                "description": path_scores.get(selected_path, {}).get("description", "Standard analysis"),
                "query_analysis": {
                    "query_length": len(query),
                    "word_count": len(query.split()),
                    "has_question_mark": "?" in query,
                    "has_strategic_terms": any(term in query_lower for term in 
                                             ["crisis", "strategic", "complex", "critical"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing query for cognitive path: {e}", exc_info=True)
            return {
                "selected_path": "enhanced_analysis",
                "selected_path_type": "aco_enhanced",
                "confidence": 0.1,
                "error": str(e)
            }
    
    def _execute_cognitive_path(self, query: str, path_type: str) -> Dict[str, Any]:
        """
        Execute the appropriate cognitive path (ACO/RISE/PTRF) for a query.
        This replaces the flawed workflow execution with true cognitive intelligence.
        """
        try:
            if path_type == "rise_v2_0":
                # Execute RISE v2.0 Genesis Protocol
                if not self.rise_v2_enabled:
                    return {
                        "success": False,
                        "error": "RISE v2.0 Genesis Protocol is not available",
                        "path_type": path_type
                    }
                
                logger.info(f"Executing RISE v2.0 for query: {query[:100]}...")
                result = self.rise_orchestrator.run_rise_workflow(query)
                
                return {
                    "success": True,
                    "path_type": path_type,
                    "result": result,
                    "execution_time": result.get("execution_time", 0),
                    "status": result.get("execution_status", "unknown")
                }
                
            elif path_type == "ptrf":
                # Execute Proactive Truth Resonance Framework
                if not self.ptrf_enabled:
                    return {
                        "success": False,
                        "error": "Proactive Truth Resonance Framework is not available",
                        "path_type": path_type
                    }
                
                logger.info(f"Executing PTRF for query: {query[:100]}...")
                stp = self.truth_seeker.seek_truth(query)
                
                # Convert dataclass to dict
                stp_dict = {
                    "final_answer": stp.final_answer,
                    "confidence_score": stp.confidence_score,
                    "source_consensus": stp.source_consensus.value,
                    "transparency_note": stp.transparency_note,
                    "conflicting_information": stp.conflicting_information,
                    "crystallization_ready": stp.crystallization_ready,
                    "verification_trail": stp.verification_trail
                }
                
                return {
                    "success": True,
                    "path_type": path_type,
                    "result": stp_dict,
                    "execution_time": 0,  # PTRF doesn't track time separately
                    "status": "completed"
                }
                
            elif path_type == "aco_enhanced":
                # Execute ACO enhanced analysis
                logger.info(f"Executing ACO enhanced analysis for query: {query[:100]}...")
                enhanced_result = self._apply_universal_enhancement(query)
                
                return {
                    "success": True,
                    "path_type": path_type,
                    "result": enhanced_result,
                    "execution_time": 0,  # ACO doesn't track time separately
                    "status": "completed"
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unknown cognitive path type: {path_type}",
                    "path_type": path_type
                }
                
        except Exception as e:
            logger.error(f"Error executing cognitive path '{path_type}' for query: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "path_type": path_type
            }
    
    def _handle_cognitive_query(self, query: str) -> Dict[str, Any]:
        """
        Handle queries through the true ACO/RISE cognitive core.
        This replaces the flawed workflow routing with intelligent cognitive paths.
        """
        try:
            # Step 1: Analyze query to determine cognitive path
            analysis_result = self._analyze_query_for_cognitive_path(query)
            
            # Step 2: Execute the appropriate cognitive path
            path_type = analysis_result["selected_path_type"]
            cognitive_result = self._execute_cognitive_path(query, path_type)
            
            # Step 3: Prepare comprehensive response
            if cognitive_result["success"]:
                return {
                    "query_type": "cognitive_analysis",
                    "cognitive_analysis": analysis_result,
                    "cognitive_execution": cognitive_result,
                    "path_type": path_type,
                    "confidence": analysis_result["confidence"],
                    "description": analysis_result["description"]
                }
            else:
                # Fallback to ACO enhanced analysis if cognitive path fails
                fallback_result = self._execute_cognitive_path(query, "aco_enhanced")
                return {
                    "query_type": "cognitive_fallback",
                    "cognitive_analysis": analysis_result,
                    "original_path_failed": cognitive_result,
                    "fallback_execution": fallback_result,
                    "path_type": "aco_enhanced (fallback)",
                    "confidence": 0.1
                }
                
        except Exception as e:
            logger.error(f"Error handling cognitive query: {e}", exc_info=True)
            return {
                "query_type": "cognitive_error",
                "error": str(e),
                "answer": f"Error processing query through cognitive core: {str(e)}"
            }

    def list_workflows(self):
        """Prints the list of available workflows."""
        print("\nAvailable Workflows:")
        if not self.available_workflows:
            print("  No workflows found.")
            return
        for i, wf_name in enumerate(self.available_workflows, 1):
            print(f"  {i}. {wf_name}")
        print()

    def select_workflow(self) -> str | None:
        """Prompts the user to select a workflow and returns the chosen file name."""
        self.list_workflows()
        if not self.available_workflows:
            return None
        
        while True:
            try:
                choice_str = input(f"Select a workflow by number (1-{len(self.available_workflows)}) or 'exit': ")
                if choice_str.lower() == 'exit':
                    return None
                choice = int(choice_str) - 1
                if 0 <= choice < len(self.available_workflows):
                    return self.available_workflows[choice]
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def run(self):
        """The main interactive loop for the CLI."""
        print("Welcome to the ArchE Workflow CLI.")
        available_commands = "list, run, exit"
        if self.ptrf_enabled:
            available_commands = "list, run, truth_seek, exit"
        if self.autonomous_evolution_enabled:
            if self.ptrf_enabled:
                available_commands = "list, run, truth_seek, query, evolution_status, evolution_candidates, enhancement_stats, exit"
            else:
                available_commands = "list, run, query, evolution_status, evolution_candidates, enhancement_stats, exit"
        if self.rise_v2_enabled:
            available_commands += ", rise_execute"
            if self.synergistic_fusion_enabled:
                available_commands += ", synergistic_test"
            if self.utopian_synthesis_enabled:
                available_commands += ", utopian_test"
        if self.ceo_mode_enabled:
            available_commands += ", ceo_dashboard, orchestrate, escalation_status"
        
        print(f"Type '{available_commands}'")

        while True:
            try:
                prompt_text = f"\n> Enter command ({available_commands}): "
                command = input(prompt_text).lower().strip()

                if command == 'exit':
                    print("Exiting ArchE Workflow CLI. Goodbye!")
                    break
                elif command == 'list':
                    self.list_workflows()
                elif command == 'run':
                    workflow_name = self.select_workflow()
                    if workflow_name:
                        workflow_path = self.workflows_dir / workflow_name
                        print(f"\nExecuting workflow: {workflow_name}")
                        try:
                            # For now, we run with an empty initial context.
                            # A more advanced version could prompt for context.
                            initial_context = {}
                            final_result = self.engine.run_workflow(str(workflow_path), initial_context)
                            
                            print("\n--- Workflow Execution Complete ---")
                            print(json.dumps(final_result, indent=2, default=str))
                            print("---------------------------------")
                            
                            final_reflection = final_result.get("reflection", {})
                            if final_reflection.get("status") == ExecutionStatus.CRITICAL_FAILURE:
                                logger.error("Workflow ended with CRITICAL_FAILURE.")
                            
                        except Exception as e:
                            logger.error(f"An error occurred while running the workflow '{workflow_name}': {e}", exc_info=True)
                            print(f"An error occurred. Check the logs for details.")
                elif command == 'truth_seek':
                    if not self.ptrf_enabled:
                        print("The 'truth_seek' command is disabled due to an initialization error. Please check the logs.")
                        continue
                    
                    query = input("Enter the factual query you want to verify: ")
                    if not query:
                        print("Query cannot be empty.")
                        continue
                        
                    print(f"\nInitiating Proactive Truth Resonance for: \"{query}\"")
                    print("This may take a moment as it involves live web searches and analysis...")
                    
                    try:
                        # Call the PTRF engine
                        stp = self.truth_seeker.seek_truth(query)
                        
                        # Convert dataclass to dict for clean JSON printing
                        stp_dict = {
                            "final_answer": stp.final_answer,
                            "confidence_score": stp.confidence_score,
                            "source_consensus": stp.source_consensus.value,
                            "transparency_note": stp.transparency_note,
                            "conflicting_information": stp.conflicting_information,
                            "crystallization_ready": stp.crystallization_ready,
                            "verification_trail": stp.verification_trail
                        }

                        print("\n--- Solidified Truth Packet ---")
                        print(json.dumps(stp_dict, indent=2))
                        print("-----------------------------")

                    except Exception as e:
                        logger.error(f"An error occurred during truth seeking for query '{query}': {e}", exc_info=True)
                        print(f"An error occurred during truth seeking. See logs for details.")
                        
                elif command == 'query':
                    if not self.autonomous_evolution_enabled:
                        print("The 'query' command is disabled due to ACO initialization error. Please check the logs.")
                        continue
                    
                    query = input("Enter your query: ")
                    if not query:
                        print("Query cannot be empty.")
                        continue
                        
                    print(f"\n🧠 PROCESSING QUERY THROUGH INTELLIGENT WORKFLOW ROUTING")
                    print(f"Query: \"{query}\"")
                    print("=" * 80)
                    
                    try:
                        # First, check if this is a protocol query
                        protocol_result = self._handle_protocol_query(query)
                        
                        if protocol_result.get("is_protocol_query", False):
                            # This is a protocol query - provide the answer directly
                            print(f"\n📖 **PROTOCOL QUERY DETECTED**")
                            print("=" * 80)
                            print(protocol_result["answer"])
                            print("=" * 80)
                            
                            # Still apply universal enhancement for learning purposes
                            enhancement_result = self._apply_universal_enhancement(query)
                        else:
                            # This is a general query - route through appropriate workflow
                            print(f"\n🔍 **ANALYZING QUERY FOR WORKFLOW SELECTION**")
                            general_result = self._handle_general_query(query)
                            
                            # Display workflow selection analysis
                            workflow_analysis = general_result.get("workflow_analysis", {})
                            print(f"Selected Category: {workflow_analysis.get('selected_category', 'unknown')}")
                            print(f"Selected Workflow: {workflow_analysis.get('selected_workflow', 'unknown')}")
                            print(f"Confidence: {workflow_analysis.get('confidence', 0):.2f}")
                            
                            # Display category scores if available
                            category_scores = workflow_analysis.get("category_scores", {})
                            if category_scores:
                                print(f"\n📊 **WORKFLOW CATEGORY ANALYSIS**:")
                                for category, score_info in category_scores.items():
                                    print(f"   {category}: {score_info['score']} matches, priority {score_info['priority']}, final score {score_info['final_score']}")
                            
                            # Display the workflow answer
                            print(f"\n🎯 **WORKFLOW ANSWER**")
                            print("=" * 80)
                            print(general_result.get("answer", "No answer generated"))
                            print("=" * 80)
                            
                            # Display workflow execution details
                            workflow_execution = general_result.get("workflow_execution", {})
                            if workflow_execution.get("success", False):
                                print(f"\n✅ **WORKFLOW EXECUTION SUCCESSFUL**")
                                print(f"Workflow: {workflow_execution.get('workflow_name', 'unknown')}")
                                print(f"Execution Time: {workflow_execution.get('execution_time', 0):.3f}s")
                                
                                # Show reflection if available
                                reflection = workflow_execution.get("reflection", {})
                                if reflection:
                                    print(f"Status: {reflection.get('status', 'unknown')}")
                                    print(f"Confidence: {reflection.get('confidence', 0):.2f}")
                            else:
                                print(f"\n❌ **WORKFLOW EXECUTION FAILED**")
                                print(f"Error: {workflow_execution.get('error', 'Unknown error')}")
                            
                            # Apply universal enhancement for learning purposes
                            enhancement_result = self._apply_universal_enhancement(query)
                        
                        # Display universal enhancement results
                        if enhancement_result.get("enhanced", False):
                            print(f"\n🧠 **UNIVERSAL ENHANCEMENT ANALYSIS**:")
                            print(f"Domain: {enhancement_result['enhancement_analysis']['domain_activated']}")
                            print(f"Processing Time: {enhancement_result['enhancement_analysis']['processing_time']:.3f}s")
                            print(f"Context Generated: {enhancement_result['enhancement_analysis']['context_generated']}")
                            print(f"Evolution Active: {enhancement_result['enhancement_analysis']['evolution_active']}")
                            
                            # Display context if available
                            if enhancement_result.get("context"):
                                print(f"\n📊 **EXTRACTED CONTEXT**:")
                                context = enhancement_result["context"]
                                print(f"{context[:300]}..." if len(context) > 300 else context)
                            
                            # Display evolution analysis
                            if enhancement_result["enhancement_analysis"]["evolution_active"]:
                                evo_analysis = enhancement_result["enhancement_analysis"]
                                print(f"\n🧠 **AUTONOMOUS EVOLUTION ANALYSIS**:")
                                print(f"   Total queries analyzed: {evo_analysis.get('total_queries_analyzed', 0)}")
                                print(f"   Evolution status: {evo_analysis.get('evolution_status', 'unknown')}")
                                
                                if evo_analysis.get("evolution_opportunity", False):
                                    print(f"   🚀 **EVOLUTION OPPORTUNITY DETECTED!**")
                                    print(f"   Candidates ready: {evo_analysis.get('evolution_candidates', 0)}")
                                    print(f"   The system is learning and evolving from this query pattern!")
                            
                            # Generate comprehensive analysis
                            comprehensive_analysis = self._generate_comprehensive_analysis(query, enhancement_result)
                            print(f"\n📈 **COMPREHENSIVE ANALYSIS**:")
                            print(comprehensive_analysis)
                            
                            # Show universal enhancement statistics
                            total_queries = len(self.query_enhancement_history)
                            evolution_opportunities = sum(1 for q in self.query_enhancement_history 
                                                        if q["enhancement_analysis"].get("evolution_active", False))
                            
                            print(f"\n⚡ **UNIVERSAL ENHANCEMENT STATISTICS**:")
                            print(f"   Total queries processed: {total_queries}")
                            print(f"   Evolution opportunities detected: {evolution_opportunities}")
                            print(f"   Enhancement success rate: {(evolution_opportunities/total_queries*100):.1f}%" if total_queries > 0 else "   Enhancement success rate: 0%")
                            print(f"   Active domain patterns: {len(self.domain_evolution_tracker)}")
                            
                        else:
                            print(f"\n❌ **UNIVERSAL ENHANCEMENT FAILED**")
                            print(f"Reason: {enhancement_result.get('reason', 'Unknown error')}")
                            
                        print("=" * 80)
                        
                    except Exception as e:
                        logger.error(f"An error occurred during query processing: {e}", exc_info=True)
                        print(f"An error occurred during query processing. See logs for details.")
                        
                elif command == 'evolution_status':
                    if not self.autonomous_evolution_enabled:
                        print("The 'evolution_status' command is disabled due to ACO initialization error. Please check the logs.")
                        continue
                    
                    try:
                        status = self.aco.emergent_domain_detector.get_evolution_status()
                        
                        print(f"\n--- Autonomous Evolution Status ---")
                        print(f"Autonomous mode: {status['autonomous_mode']}")
                        print(f"Total fallback queries: {status['total_fallback_queries']}")
                        print(f"Pattern clusters: {status['pattern_clusters']}")
                        print(f"Domain candidates: {status['domain_candidates']}")
                        print(f"Evolution history events: {status['evolution_history_events']}")
                        print(f"Confidence threshold: {status['confidence_threshold']}")
                        print(f"Min cluster size: {status['min_cluster_size']}")
                        print(f"Last analysis: {status['last_analysis']}")
                        print("------------------------------------")
                        
                    except Exception as e:
                        logger.error(f"An error occurred getting evolution status: {e}", exc_info=True)
                        print(f"An error occurred getting evolution status. See logs for details.")
                        
                elif command == 'evolution_candidates':
                    if not self.autonomous_evolution_enabled:
                        print("The 'evolution_candidates' command is disabled due to ACO initialization error. Please check the logs.")
                        continue
                    
                    try:
                        candidates = self.aco.get_evolution_candidates_for_review()
                        
                        print(f"\n--- Evolution Candidates for Review ---")
                        print(f"Total candidates: {candidates['total_candidates']}")
                        
                        if candidates['total_candidates'] > 0:
                            for candidate_id, candidate_info in candidates['candidates'].items():
                                config = candidate_info['config']
                                print(f"\n🎯 Candidate: {candidate_id}")
                                print(f"   Domain Name: {config['domain_name']}")
                                print(f"   Controller Class: {config['controller_class']}")
                                print(f"   Status: {candidate_info['status']}")
                                
                                # Show generated controller preview
                                controller_draft = candidate_info['controller_draft']
                                print(f"   Controller Preview: {controller_draft[:150]}...")
                        else:
                            print("No evolution candidates ready for review.")
                        
                        print(f"\nEvolution log events: {len(candidates['evolution_log'])}")
                        print("------------------------------------------")
                        
                    except Exception as e:
                        logger.error(f"An error occurred getting evolution candidates: {e}", exc_info=True)
                        print(f"An error occurred getting evolution candidates. See logs for details.")
                        
                elif command == 'enhancement_stats':
                    if not self.autonomous_evolution_enabled or not self.universal_enhancement_active:
                        print("The 'enhancement_stats' command is disabled due to ACO initialization error. Please check the logs.")
                        continue
                    
                    try:
                        print(f"\n🧠 UNIVERSAL ENHANCEMENT SYSTEM STATISTICS")
                        print("=" * 70)
                        
                        # Overall Statistics
                        total_queries = len(self.query_enhancement_history)
                        if total_queries > 0:
                            evolution_active_count = sum(1 for q in self.query_enhancement_history 
                                                       if q["enhancement_analysis"].get("evolution_active", False))
                            evolution_opportunities = sum(1 for q in self.query_enhancement_history 
                                                        if q["enhancement_analysis"].get("evolution_opportunity", False))
                            
                            print(f"📊 **OVERALL PERFORMANCE**:")
                            print(f"   Total queries processed: {total_queries}")
                            print(f"   Evolution analysis active: {evolution_active_count} ({evolution_active_count/total_queries*100:.1f}%)")
                            print(f"   Evolution opportunities detected: {evolution_opportunities} ({evolution_opportunities/total_queries*100:.1f}%)")
                            print(f"   Average processing time: {sum(q['enhancement_analysis']['processing_time'] for q in self.query_enhancement_history)/total_queries:.3f}s")
                            
                            # Domain Analysis
                            print(f"\n🎯 **DOMAIN ANALYSIS**:")
                            print(f"   Active domain patterns: {len(self.domain_evolution_tracker)}")
                            
                            for domain, stats in self.domain_evolution_tracker.items():
                                success_rate = (stats['successful_evolutions'] / stats['evolution_opportunities'] * 100) if stats['evolution_opportunities'] > 0 else 0
                                print(f"   {domain}:")
                                print(f"     - Queries: {stats['query_count']}")
                                print(f"     - Evolution opportunities: {stats['evolution_opportunities']}")
                                print(f"     - Success rate: {success_rate:.1f}%")
                                print(f"     - Last evolution: {stats['last_evolution'] or 'None'}")
                            
                            # Recent Activity
                            print(f"\n📈 **RECENT ACTIVITY** (Last 10 queries):")
                            recent_queries = self.query_enhancement_history[-10:]
                            for i, q in enumerate(recent_queries, 1):
                                status = "🚀 Evolution" if q["enhancement_analysis"].get("evolution_opportunity", False) else "📊 Analysis"
                                domain = q["enhancement_analysis"]["domain_activated"]
                                print(f"   {i}. {status} | {domain} | {q['query']}")
                            
                            # System Health
                            print(f"\n⚡ **SYSTEM HEALTH**:")
                            print(f"   Universal Enhancement: {'✅ Active' if self.universal_enhancement_active else '❌ Inactive'}")
                            print(f"   Autonomous Evolution: {'✅ Active' if self.autonomous_evolution_enabled else '❌ Inactive'}")
                            print(f"   PTRF Integration: {'✅ Active' if self.ptrf_enabled else '❌ Inactive'}")
                            
                            # Evolution Status from ACO
                            if self.aco:
                                aco_status = self.aco.emergent_domain_detector.get_evolution_status()
                                print(f"   ACO Status: ✅ Online")
                                print(f"   Evolution confidence threshold: {aco_status['confidence_threshold']}")
                                print(f"   Min cluster size: {aco_status['min_cluster_size']}")
                                print(f"   Current domain candidates: {aco_status['domain_candidates']}")
                            
                        else:
                            print("No queries have been processed yet through the universal enhancement system.")
                            print("Use the 'query' command to start processing queries and building enhancement statistics.")
                        
                        print("=" * 70)
                        
                    except Exception as e:
                        logger.error(f"An error occurred getting enhancement statistics: {e}", exc_info=True)
                        print(f"An error occurred getting enhancement statistics. See logs for details.")
                        
                elif command == 'rise_execute':
                    if not self.rise_v2_enabled:
                        print("The 'rise_execute' command is disabled due to RISE v2.0 initialization error. Please check the logs.")
                        continue
                    
                    problem_description = input("Enter the problem description for RISE v2.0 analysis: ")
                    if not problem_description:
                        print("Problem description cannot be empty.")
                        continue
                        
                    print(f"\n🚀 INITIATING RISE v2.1 UTOPIAN UPGRADE")
                    print(f"Problem: \"{problem_description}\"")
                    print("=" * 80)
                    print("🔄 Phase A: Knowledge Scaffolding & Dynamic Specialization")
                    print("🔄 Phase B: Fused Insight Generation")
                    print("🔄 Phase C: Fused Strategy Generation & Finalization")
                    print("🌟 Phase D: Utopian Vetting & Refinement (NEW)")
                    print("=" * 80)
                    
                    # Show advanced features status
                    if self.synergistic_fusion_enabled:
                        print("🔮 Synergistic Fusion Protocol: ACTIVE")
                    if self.utopian_synthesis_enabled:
                        print("🌟 Utopian Solution Synthesizer: ACTIVE")
                    print("=" * 80)
                    
                    try:
                        # Execute the RISE v2.0 workflow
                        start_time = datetime.now()
                        result = self.rise_orchestrator.run_rise_workflow(problem_description)
                        end_time = datetime.now()
                        execution_time = (end_time - start_time).total_seconds()
                        
                        # Display results
                        print(f"\n✅ RISE v2.1 UTOPIAN UPGRADE EXECUTION COMPLETE")
                        print(f"Session ID: {result.get('session_id', 'Unknown')}")
                        print(f"Execution Time: {execution_time:.2f} seconds")
                        print(f"Status: {result.get('execution_status', 'Unknown')}")
                        
                        if result.get('execution_status') == 'completed':
                            print(f"\n📊 EXECUTION METRICS:")
                            metrics = result.get('execution_metrics', {})
                            print(f"   Total Duration: {metrics.get('total_duration', 0):.2f}s")
                            phase_durations = metrics.get('phase_durations', {})
                            for phase, duration in phase_durations.items():
                                print(f"   Phase {phase}: {duration:.2f}s")
                            
                            print(f"\n🎯 FINAL STRATEGY:")
                            final_strategy = result.get('final_strategy', {})
                            if final_strategy:
                                print(f"   Strategy Generated: ✅")
                                print(f"   Confidence: {final_strategy.get('confidence', 'Unknown')}")
                                print(f"   Key Recommendations: {len(final_strategy.get('recommendations', []))}")
                            else:
                                print(f"   Strategy Generated: ❌")
                            
                            print(f"\n🧠 SPR LEARNING:")
                            spr_definition = result.get('spr_definition', {})
                            if spr_definition:
                                print(f"   SPR Created: ✅")
                                print(f"   SPR Name: {spr_definition.get('spr_name', 'Unknown')}")
                                print(f"   Reusability Score: {spr_definition.get('reusability_score', 'Unknown')}")
                            else:
                                print(f"   SPR Created: ❌")
                            
                            # Display Utopian Results (NEW)
                            print(f"\n🌟 UTOPIAN SYNTHESIS RESULTS:")
                            phase_results = result.get('phase_results', {})
                            phase_d = phase_results.get('phase_d', {})
                            if phase_d and phase_d.get('status') == 'completed':
                                utopian_metrics = phase_d.get('utopian_metrics', {})
                                print(f"   Trust Score: {utopian_metrics.get('trust_score', 0.0):.2f}")
                                print(f"   Risk Level: {utopian_metrics.get('risk_level', 'Unknown')}")
                                print(f"   Axiomatic Score: {utopian_metrics.get('axiomatic_score', 0.0):.2f}")
                                
                                trust_packet = phase_d.get('trust_packet')
                                if trust_packet:
                                    print(f"   Trust Packet Generated: ✅")
                                    print(f"   Dystopian Risks Mitigated: {len(trust_packet.get('dystopian_risk_dossier', {}).get('identified_risks', []))}")
                                    print(f"   Axioms Activated: {len(trust_packet.get('axiomatic_resonance_score', {}).get('axiom_scores', {}))}")
                                else:
                                    print(f"   Trust Packet Generated: ❌")
                            else:
                                print(f"   Utopian Synthesis: ❌ (Phase D not completed)")
                            
                            # Display detailed results if requested
                            show_details = input("\nShow detailed results? (y/n): ").lower().strip()
                            if show_details == 'y':
                                print(f"\n📋 DETAILED RESULTS:")
                                print(json.dumps(result, indent=2, default=str))
                        else:
                            print(f"\n❌ EXECUTION FAILED:")
                            print(f"Error: {result.get('error', 'Unknown error')}")
                            print(f"Current Phase: {result.get('current_phase', 'Unknown')}")
                        
                        print("=" * 80)
                        
                    except Exception as e:
                        logger.error(f"An error occurred during RISE v2.0 execution: {e}", exc_info=True)
                        print(f"An error occurred during RISE v2.0 execution. See logs for details.")

                elif command == 'synergistic_test':
                    if not self.synergistic_fusion_enabled:
                        print("The 'synergistic_test' command is disabled. Synergistic Fusion Protocol not available.")
                        continue
                    
                    test_query = input("Enter a test query for Synergistic Fusion Protocol: ")
                    if not test_query:
                        print("Test query cannot be empty.")
                        continue
                    
                    print(f"\n🔮 TESTING SYNERGISTIC FUSION PROTOCOL")
                    print(f"Query: \"{test_query}\"")
                    print("=" * 80)
                    
                    try:
                        # Create a mock RISE state for testing
                        from Three_PointO_ArchE.rise_orchestrator import RISEState
                        from datetime import datetime
                        
                        test_state = RISEState(
                            problem_description=test_query,
                            session_id="test_synergistic",
                            current_phase="A",
                            phase_start_time=datetime.utcnow(),
                            session_knowledge_base={},
                            specialized_agent=None,
                            advanced_insights=[],
                            specialist_consultation=None,
                            fused_strategic_dossier=None,
                            vetting_dossier=None,
                            final_strategy=None,
                            spr_definition=None,
                            execution_metrics={},
                            scope_limitation_assessment=None,
                            activated_axioms=[],
                            synergistic_synthesis=None,
                            utopian_trust_packet=None
                        )
                        
                        # Test synergistic fusion
                        enhanced_result = self.rise_orchestrator.perform_synergistic_fusion(
                            test_state, 
                            "Initial analysis of the problem", 
                            {"analysis_depth": "comprehensive"}
                        )
                        
                        print(f"\n✅ SYNERGISTIC FUSION TEST COMPLETE")
                        print(f"Enhanced Thought: {enhanced_result.get('enhanced_thought', 'N/A')[:200]}...")
                        print(f"Synergistic Effect: {enhanced_result.get('synergistic_effect', 'N/A')}")
                        print(f"Enhanced Inputs: {list(enhanced_result.get('enhanced_action_inputs', {}).keys())}")
                        
                    except Exception as e:
                        logger.error(f"An error occurred during synergistic fusion test: {e}", exc_info=True)
                        print(f"An error occurred during synergistic fusion test. See logs for details.")

                elif command == 'utopian_test':
                    if not self.utopian_synthesis_enabled:
                        print("The 'utopian_test' command is disabled. Utopian Solution Synthesizer not available.")
                        continue
                    
                    test_strategy = input("Enter a test strategy for Utopian Synthesis (e.g., 'Implement surveillance system'): ")
                    if not test_strategy:
                        print("Test strategy cannot be empty.")
                        continue
                    
                    print(f"\n🌟 TESTING UTOPIAN SOLUTION SYNTHESIZER")
                    print(f"Original Strategy: \"{test_strategy}\"")
                    print("=" * 80)
                    
                    try:
                        # Create a test strategy and context
                        test_strategy_dict = {
                            "strategy": test_strategy,
                            "confidence": 0.8,
                            "recommendations": [test_strategy]
                        }
                        
                        test_context = {
                            "problem_description": f"Test problem requiring: {test_strategy}",
                            "session_knowledge_base": {},
                            "advanced_insights": [],
                            "specialist_consultation": None
                        }
                        
                        # Test utopian synthesis
                        trust_packet = self.rise_orchestrator.utopian_synthesizer.synthesize_utopian_solution(
                            test_strategy_dict, test_context
                        )
                        
                        print(f"\n✅ UTOPIAN SYNTHESIS TEST COMPLETE")
                        print(f"Trust Score: {trust_packet.trust_metrics.get('overall_trust_score', 0.0):.2f}")
                        print(f"Risk Level: {trust_packet.dystopian_risk_dossier.overall_risk_level}")
                        print(f"Axiomatic Score: {trust_packet.axiomatic_resonance_score.overall_resonance_score:.2f}")
                        print(f"Dystopian Risks Identified: {len(trust_packet.dystopian_risk_dossier.identified_risks)}")
                        print(f"Axioms Evaluated: {len(trust_packet.axiomatic_resonance_score.axiom_scores)}")
                        
                        # Show refined strategy
                        refined_strategy = trust_packet.refined_utopian_strategy
                        if refined_strategy and 'utopian_enhancements' in refined_strategy:
                            enhancements = refined_strategy['utopian_enhancements']
                            print(f"\n🌟 UTOPIAN ENHANCEMENTS APPLIED:")
                            if enhancements.get('safeguards'):
                                print(f"   Safeguards: {len(enhancements['safeguards'])} added")
                            if enhancements.get('axiomatic_alignments'):
                                print(f"   Axiomatic Alignments: {len(enhancements['axiomatic_alignments'])} added")
                            if enhancements.get('positive_sum_mechanisms'):
                                print(f"   Positive-Sum Mechanisms: {len(enhancements['positive_sum_mechanisms'])} added")
                        
                    except Exception as e:
                        logger.error(f"An error occurred during utopian synthesis test: {e}", exc_info=True)
                        print(f"An error occurred during utopian synthesis test. See logs for details.")

                elif command == 'ceo_dashboard':
                    if not self.ceo_mode_enabled:
                        print("CEO Mode is not available. Check logs for initialization errors.")
                        continue
                    
                    print("\n🤖 Generating CEO Dashboard...")
                    try:
                        dashboard = self.autonomous_orchestrator.generate_ceo_dashboard()
                        
                        print("\n--- CEO DASHBOARD ---")
                        print(f"Generated: {dashboard['generated_at']}")
                        print(f"Overall Confidence: {dashboard['kpi_summary']['average_confidence']:.1%}")
                        print(f"Completion Rate: {dashboard['kpi_summary']['completion_rate']:.1%}")
                        print(f"Escalation Rate: {dashboard['kpi_summary']['escalation_rate']:.1%}")
                        print(f"Active Escalations: {dashboard['kpi_summary']['active_escalations_count']}")
                        
                        print(f"\n📊 Risk Indicators:")
                        for risk, value in dashboard['risk_indicators'].items():
                            status = "⚠️ HIGH" if value else "✅ OK"
                            print(f"   {risk.replace('_', ' ').title()}: {status}")
                        
                        if dashboard['recommendations']:
                            print(f"\n💡 Recommendations:")
                            for rec in dashboard['recommendations']:
                                print(f"   • {rec}")
                        
                        print("-------------------")
                        
                    except Exception as e:
                        logger.error(f"An error occurred generating CEO dashboard: {e}", exc_info=True)
                        print(f"An error occurred generating CEO dashboard. See logs for details.")

                elif command == 'orchestrate':
                    if not self.ceo_mode_enabled:
                        print("CEO Mode is not available. Check logs for initialization errors.")
                        continue
                    
                    print("\n🤖 Running Autonomous Orchestration Cycle...")
                    try:
                        cycle_results = self.autonomous_orchestrator.run_orchestration_cycle()
                        
                        print(f"\n--- ORCHESTRATION CYCLE COMPLETE ---")
                        print(f"Duration: {cycle_results['cycle_duration']:.2f}s")
                        print(f"Work Items Processed: {cycle_results['work_items_processed']}")
                        print(f"Dispatched: {cycle_results['dispatch_results']['dispatched']}")
                        print(f"Escalated: {cycle_results['dispatch_results']['escalated']}")
                        print(f"Blocked: {cycle_results['dispatch_results']['blocked']}")
                        
                        if cycle_results['dashboard_generated']:
                            print(f"✅ CEO Dashboard generated")
                        
                        print("-----------------------------------")
                        
                    except Exception as e:
                        logger.error(f"An error occurred during orchestration cycle: {e}", exc_info=True)
                        print(f"An error occurred during orchestration cycle. See logs for details.")

                elif command == 'escalation_status':
                    if not self.ceo_mode_enabled:
                        print("CEO Mode is not available. Check logs for initialization errors.")
                        continue
                    
                    print("\n🚨 ESCALATION STATUS")
                    try:
                        state = self.autonomous_orchestrator.state
                        print(f"Total Escalations: {state.escalated_items}")
                        print(f"Active Escalations: {len(state.active_escalations)}")
                        
                        if state.active_escalations:
                            print(f"\n📋 Active Escalations:")
                            for escalation in state.active_escalations:
                                print(f"   • {escalation['work_item_id']}: {escalation['reason']} ({escalation['timestamp']})")
                        else:
                            print("   ✅ No active escalations")
                        
                    except Exception as e:
                        logger.error(f"An error occurred checking escalation status: {e}", exc_info=True)
                        print(f"An error occurred checking escalation status. See logs for details.")

                else:
                    print(f"Unknown command: {command}")
                    print(f"Available commands: {available_commands}")

            except KeyboardInterrupt:
                print("\nExiting ArchE Workflow CLI. Goodbye!")
                break
            except Exception as e:
                logger.error(f"An unexpected error occurred in the CLI main loop: {e}", exc_info=True)
                print("An unexpected error occurred. Check the logs.")

def main():
    """Main function to run the ArchE Workflow CLI."""
    # Perform prerequisite checks before startup
    check_prerequisites()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="ArchE Interactive Agent - IAR Compliant Workflow Engine Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 -m mastermind.interact                    # Interactive mode
  python3 -m mastermind.interact "What is AI?"      # Direct query mode
  python3 -m mastermind.interact --truth-seek "Is the Earth round?"  # Truth-seeking mode
  python3 -m mastermind.interact --rise-execute "How to optimize supply chain logistics?"  # RISE v2.1 Utopian analysis
        """
    )
    parser.add_argument(
        'query', 
        nargs='?', 
        help='Query to process directly (non-interactive mode)'
    )
    parser.add_argument(
        '--truth-seek', 
        action='store_true',
        help='Use the Proactive Truth Resonance Framework to verify the query'
    )
    parser.add_argument(
        '--rise-execute',
        action='store_true',
        help='Use the RISE v2.0 Genesis Protocol to analyze and solve the problem'
    )
    parser.add_argument(
        '--server-mode',
        action='store_true',
        help='Run in server mode, reading queries from stdin'
    )
    
    args = parser.parse_args()
    
    cli = ArchEWorkflowCLI()
    
    # Check if we're in server mode (explicit flag or no args but stdin has data)
    if args.server_mode or (not args.query and not sys.stdin.isatty()):
        # Server mode: read query from stdin
        try:
            query = sys.stdin.read().strip()
            if query:
                print(f"Processing server mode query: \"{query}\"")
                
                try:
                    # Use the existing query processing functionality
                    if not cli.autonomous_evolution_enabled:
                        print("ERROR: The Adaptive Cognitive Orchestrator is not available.")
                        print("Check logs and ensure ACO is properly initialized.")
                        sys.exit(1)
                    
                    print(f"\n🧠 PROCESSING QUERY THROUGH ACO/RISE COGNITIVE CORE")
                    print(f"Query: \"{query}\"")
                    print("=" * 80)
                    
                    # First, check if this is a protocol query
                    protocol_result = cli._handle_protocol_query(query)
                    
                    if protocol_result.get("is_protocol_query", False):
                        # This is a protocol query - provide the answer directly
                        print(f"\n📖 **PROTOCOL QUERY DETECTED**")
                        print("=" * 80)
                        print(protocol_result.get("answer", "Protocol query processing failed."))
                    else:
                        # This is a general query - process through ACO/RISE cognitive core
                        print(f"\n🔮 **ACO COGNITIVE ANALYSIS**")
                        print("=" * 80)
                        
                        # ACO will analyze the query and determine the appropriate cognitive path
                        query_lower = query.lower()
                        
                        # Check for high-stakes, strategic indicators that require RISE
                        strategic_indicators = [
                            "crisis", "conflicting", "ground truth", "predictive forecast",
                            "geopolitical", "rapidly developing", "initial reports",
                            "proactive truth resonance", "rise engine", "strategic",
                            "complex", "high-stakes", "critical decision", "fog of war",
                            "competitive landscape", "unknown competitive", "resource allocation",
                            "adversarial actions", "rapid adaptation", "emerging intelligence",
                            "benchmark query", "comprehensive strategy"
                        ]
                        
                        is_strategic_query = any(indicator in query_lower for indicator in strategic_indicators)
                        
                        if is_strategic_query:
                            print(f"🎯 **STRATEGIC QUERY DETECTED**")
                            print("Query contains strategic indicators requiring RISE engine analysis.")
                            print("Redirecting to RISE v2.0 Genesis Protocol...")
                            print("=" * 80)
                            
                            # Invoke RISE engine directly
                            if not cli.rise_v2_enabled:
                                print("ERROR: RISE v2.0 Genesis Protocol is not available.")
                                print("Check logs and ensure RISE_Orchestrator is properly initialized.")
                                sys.exit(1)
                            
                            print(f"🚀 INITIATING RISE v2.1 UTOPIAN UPGRADE")
                            print(f"Problem: \"{query}\"")
                            print("=" * 80)
                            print("🔄 Phase A: Knowledge Scaffolding & Dynamic Specialization")
                            print("🔄 Phase B: Fused Insight Generation")
                            print("🔄 Phase C: Fused Strategy Generation & Finalization")
                            print("🌟 Phase D: Utopian Vetting & Refinement (NEW)")
                            print("=" * 80)
                            
                            # Show advanced features status
                            if cli.synergistic_fusion_enabled:
                                print("🔮 Synergistic Fusion Protocol: ACTIVE")
                            if cli.utopian_synthesis_enabled:
                                print("🌟 Utopian Solution Synthesizer: ACTIVE")
                            print("=" * 80)
                            print("=" * 80)
                            
                            try:
                                from datetime import datetime
                                start_time = datetime.now()
                                result = cli.rise_orchestrator.run_rise_workflow(query)
                                end_time = datetime.now()
                                execution_time = (end_time - start_time).total_seconds()
                                
                                # Display results
                                print(f"\n✅ RISE v2.0 GENESIS PROTOCOL EXECUTION COMPLETE")
                                print(f"Session ID: {result.get('session_id', 'Unknown')}")
                                print(f"Execution Time: {execution_time:.2f} seconds")
                                print(f"Status: {result.get('execution_status', 'Unknown')}")
                                
                                if result.get('execution_status') == 'completed':
                                    print(f"\n📊 EXECUTION METRICS:")
                                    metrics = result.get('execution_metrics', {})
                                    print(f"   Total Duration: {metrics.get('total_duration', 0):.2f}s")
                                    phase_durations = metrics.get('phase_durations', {})
                                    for phase, duration in phase_durations.items():
                                        print(f"   Phase {phase}: {duration:.2f}s")
                                    
                                    print(f"\n🎯 FINAL STRATEGY:")
                                    final_strategy = result.get('final_strategy', {})
                                    if final_strategy:
                                        print(f"   Strategy Generated: ✅")
                                        print(f"   Confidence: {final_strategy.get('confidence', 'Unknown')}")
                                        print(f"   Key Recommendations: {len(final_strategy.get('recommendations', []))}")
                                    else:
                                        print(f"   Strategy Generated: ❌")
                                    
                                    print(f"\n🧠 SPR LEARNING:")
                                    spr_definition = result.get('spr_definition', {})
                                    if spr_definition:
                                        print(f"   SPR Created: ✅")
                                        print(f"   SPR Name: {spr_definition.get('spr_name', 'Unknown')}")
                                        print(f"   Reusability Score: {spr_definition.get('reusability_score', 'Unknown')}")
                                    else:
                                        print(f"   SPR Created: ❌")
                                    
                                    # Display detailed results
                                    print(f"\n📋 DETAILED RESULTS:")
                                    print(json.dumps(result, indent=2, default=str))
                                else:
                                    print(f"\n❌ EXECUTION FAILED:")
                                    print(f"Error: {result.get('error', 'Unknown error')}")
                                    print(f"Current Phase: {result.get('current_phase', 'Unknown')}")
                                
                                print("=" * 80)
                                
                            except Exception as e:
                                logger.error(f"An error occurred during RISE v2.0 execution: {e}", exc_info=True)
                                print(f"ERROR: An error occurred during RISE v2.0 execution. See logs for details.")
                                sys.exit(1)
                        else:
                            # For non-strategic queries, use ACO's enhanced analysis
                            print(f"📊 **STANDARD QUERY - ACO ENHANCED ANALYSIS**")
                            print("Query processed through Adaptive Cognitive Orchestrator.")
                            print("=" * 80)
                            
                            # Use ACO's enhanced analysis capabilities
                            enhanced_result = cli._apply_universal_enhancement(query)
                            
                            print(f"\n🎯 **ACO ENHANCED ANSWER**")
                            print("=" * 80)
                            print(enhanced_result.get("enhanced_answer", "ACO analysis failed."))
                            print("=" * 80)
                            
                            print(f"\n✅ **ACO EXECUTION SUCCESSFUL**")
                            print(f"Analysis Type: {enhanced_result.get('analysis_type', 'Unknown')}")
                            print(f"Confidence: {enhanced_result.get('confidence', 0):.2f}")
                            
                            # Show comprehensive analysis if available
                            comprehensive_analysis = enhanced_result.get('comprehensive_analysis', '')
                            if comprehensive_analysis:
                                print(f"\n📈 **COMPREHENSIVE ANALYSIS**:")
                                print(comprehensive_analysis)
                
                except Exception as e:
                    logger.error(f"An error occurred while processing query '{query}': {e}", exc_info=True)
                    print(f"ERROR: An error occurred while processing the query. See logs for details.")
                    sys.exit(1)
            else:
                print("ERROR: No query received in server mode")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to read query from stdin: {e}")
            sys.exit(1)
    
    # Non-interactive mode: process the query directly
    elif args.query:
        if args.truth_seek:
            if not cli.ptrf_enabled:
                print("ERROR: The Proactive Truth Resonance Framework is not available.")
                print("Check logs and API key configurations.")
                sys.exit(1)
            
            print(f"Initiating Proactive Truth Resonance for: \"{args.query}\"")
            print("This may take a moment as it involves live web searches and analysis...")
            
            try:
                stp = cli.truth_seeker.seek_truth(args.query)
                
                # Convert dataclass to dict for clean JSON printing
                stp_dict = {
                    "final_answer": stp.final_answer,
                    "confidence_score": stp.confidence_score,
                    "source_consensus": stp.source_consensus.value,
                    "transparency_note": stp.transparency_note,
                    "conflicting_information": stp.conflicting_information,
                    "crystallization_ready": stp.crystallization_ready,
                    "verification_trail": stp.verification_trail
                }

                print("\n--- Solidified Truth Packet ---")
                print(json.dumps(stp_dict, indent=2))
                print("-----------------------------")
                
            except Exception as e:
                logger.error(f"An error occurred during truth seeking for query '{args.query}': {e}", exc_info=True)
                print(f"ERROR: An error occurred during truth seeking. See logs for details.")
                sys.exit(1)
        elif args.rise_execute:
            if not cli.rise_v2_enabled:
                print("ERROR: The RISE v2.0 Genesis Protocol is not available.")
                print("Check logs and ensure RISE_Orchestrator is properly initialized.")
                sys.exit(1)
            
            print(f"🚀 INITIATING RISE v2.1 UTOPIAN UPGRADE")
            print(f"Problem: \"{args.query}\"")
            print("=" * 80)
            print("🔄 Phase A: Knowledge Scaffolding & Dynamic Specialization")
            print("🔄 Phase B: Fused Insight Generation")
            print("🔄 Phase C: Fused Strategy Generation & Finalization")
            print("🌟 Phase D: Utopian Vetting & Refinement (NEW)")
            print("=" * 80)
            
            # Show advanced features status
            if cli.synergistic_fusion_enabled:
                print("🔮 Synergistic Fusion Protocol: ACTIVE")
            if cli.utopian_synthesis_enabled:
                print("🌟 Utopian Solution Synthesizer: ACTIVE")
            print("=" * 80)
            print("=" * 80)
            
            try:
                from datetime import datetime
                start_time = datetime.now()
                result = cli.rise_orchestrator.run_rise_workflow(args.query)
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Display results
                print(f"\n✅ RISE v2.0 GENESIS PROTOCOL EXECUTION COMPLETE")
                print(f"Session ID: {result.get('session_id', 'Unknown')}")
                print(f"Execution Time: {execution_time:.2f} seconds")
                print(f"Status: {result.get('execution_status', 'Unknown')}")
                
                if result.get('execution_status') == 'completed':
                    print(f"\n📊 EXECUTION METRICS:")
                    metrics = result.get('execution_metrics', {})
                    print(f"   Total Duration: {metrics.get('total_duration', 0):.2f}s")
                    phase_durations = metrics.get('phase_durations', {})
                    for phase, duration in phase_durations.items():
                        print(f"   Phase {phase}: {duration:.2f}s")
                    
                    print(f"\n🎯 FINAL STRATEGY:")
                    final_strategy = result.get('final_strategy', {})
                    if final_strategy:
                        print(f"   Strategy Generated: ✅")
                        print(f"   Confidence: {final_strategy.get('confidence', 'Unknown')}")
                        print(f"   Key Recommendations: {len(final_strategy.get('recommendations', []))}")
                    else:
                        print(f"   Strategy Generated: ❌")
                    
                    print(f"\n🧠 SPR LEARNING:")
                    spr_definition = result.get('spr_definition', {})
                    if spr_definition:
                        print(f"   SPR Created: ✅")
                        print(f"   SPR Name: {spr_definition.get('spr_name', 'Unknown')}")
                        print(f"   Reusability Score: {spr_definition.get('reusability_score', 'Unknown')}")
                    else:
                        print(f"   SPR Created: ❌")
                    
                    # Display detailed results
                    print(f"\n📋 DETAILED RESULTS:")
                    print(json.dumps(result, indent=2, default=str))
                else:
                    print(f"\n❌ EXECUTION FAILED:")
                    print(f"Error: {result.get('error', 'Unknown error')}")
                    print(f"Current Phase: {result.get('current_phase', 'Unknown')}")
                
                print("=" * 80)
                
            except Exception as e:
                logger.error(f"An error occurred during RISE v2.0 execution: {e}", exc_info=True)
                print(f"ERROR: An error occurred during RISE v2.0 execution. See logs for details.")
                sys.exit(1)
        else:
            # Process the query through the TRUE ACO/RISE cognitive core
            print(f"Processing query: \"{args.query}\"")
            
            try:
                # Check if ACO is available
                if not cli.autonomous_evolution_enabled:
                    print("ERROR: The Adaptive Cognitive Orchestrator is not available.")
                    print("Check logs and ensure ACO is properly initialized.")
                    sys.exit(1)
                
                print(f"\n🧠 PROCESSING QUERY THROUGH ACO/RISE COGNITIVE CORE")
                print(f"Query: \"{args.query}\"")
                print("=" * 80)
                
                # First, check if this is a protocol query
                protocol_result = cli._handle_protocol_query(args.query)
                
                if protocol_result.get("is_protocol_query", False):
                    # This is a protocol query - provide the answer directly
                    print(f"\n📖 **PROTOCOL QUERY DETECTED**")
                    print("=" * 80)
                    print(protocol_result.get("answer", "Protocol query processing failed."))
                else:
                    # This is a general query - process through ACO/RISE cognitive core
                    print(f"\n🔮 **ACO COGNITIVE ANALYSIS**")
                    print("=" * 80)
                    
                    # ACO will analyze the query and determine the appropriate cognitive path
                    query_lower = args.query.lower()
                    
                    # Check for high-stakes, strategic indicators that require RISE
                    strategic_indicators = [
                        "crisis", "conflicting", "ground truth", "predictive forecast",
                        "geopolitical", "rapidly developing", "initial reports",
                        "proactive truth resonance", "rise engine", "strategic",
                        "complex", "high-stakes", "critical decision"
                    ]
                    
                    is_strategic_query = any(indicator in query_lower for indicator in strategic_indicators)
                    
                    if is_strategic_query:
                        print(f"🎯 **STRATEGIC QUERY DETECTED**")
                        print("Query contains strategic indicators requiring RISE engine analysis.")
                        print("Redirecting to RISE v2.0 Genesis Protocol...")
                        print("=" * 80)
                        
                        # Invoke RISE engine directly
                        if not cli.rise_v2_enabled:
                            print("ERROR: RISE v2.0 Genesis Protocol is not available.")
                            print("Check logs and ensure RISE_Orchestrator is properly initialized.")
                            sys.exit(1)
                        
                        print(f"🚀 INITIATING RISE v2.1 UTOPIAN UPGRADE")
                        print(f"Problem: \"{args.query}\"")
                        print("=" * 80)
                        print("🔄 Phase A: Knowledge Scaffolding & Dynamic Specialization")
                        print("🔄 Phase B: Fused Insight Generation")
                        print("🔄 Phase C: Fused Strategy Generation & Finalization")
                        print("🌟 Phase D: Utopian Vetting & Refinement (NEW)")
                        print("=" * 80)
                        
                        # Show advanced features status
                        if cli.synergistic_fusion_enabled:
                            print("🔮 Synergistic Fusion Protocol: ACTIVE")
                        if cli.utopian_synthesis_enabled:
                            print("🌟 Utopian Solution Synthesizer: ACTIVE")
                        print("=" * 80)
                        print("=" * 80)
                        
                        try:
                            from datetime import datetime
                            start_time = datetime.now()
                            result = cli.rise_orchestrator.run_rise_workflow(args.query)
                            end_time = datetime.now()
                            execution_time = (end_time - start_time).total_seconds()
                            
                            # Display results
                            print(f"\n✅ RISE v2.0 GENESIS PROTOCOL EXECUTION COMPLETE")
                            print(f"Session ID: {result.get('session_id', 'Unknown')}")
                            print(f"Execution Time: {execution_time:.2f} seconds")
                            print(f"Status: {result.get('execution_status', 'Unknown')}")
                            
                            if result.get('execution_status') == 'completed':
                                print(f"\n📊 EXECUTION METRICS:")
                                metrics = result.get('execution_metrics', {})
                                print(f"   Total Duration: {metrics.get('total_duration', 0):.2f}s")
                                phase_durations = metrics.get('phase_durations', {})
                                for phase, duration in phase_durations.items():
                                    print(f"   Phase {phase}: {duration:.2f}s")
                                
                                print(f"\n🎯 FINAL STRATEGY:")
                                final_strategy = result.get('final_strategy', {})
                                if final_strategy:
                                    print(f"   Strategy Generated: ✅")
                                    print(f"   Confidence: {final_strategy.get('confidence', 'Unknown')}")
                                    print(f"   Key Recommendations: {len(final_strategy.get('recommendations', []))}")
                                else:
                                    print(f"   Strategy Generated: ❌")
                                
                                print(f"\n🧠 SPR LEARNING:")
                                spr_definition = result.get('spr_definition', {})
                                if spr_definition:
                                    print(f"   SPR Created: ✅")
                                    print(f"   SPR Name: {spr_definition.get('spr_name', 'Unknown')}")
                                    print(f"   Reusability Score: {spr_definition.get('reusability_score', 'Unknown')}")
                                else:
                                    print(f"   SPR Created: ❌")
                                
                                # Display detailed results
                                print(f"\n📋 DETAILED RESULTS:")
                                print(json.dumps(result, indent=2, default=str))
                            else:
                                print(f"\n❌ EXECUTION FAILED:")
                                print(f"Error: {result.get('error', 'Unknown error')}")
                                print(f"Current Phase: {result.get('current_phase', 'Unknown')}")
                            
                            print("=" * 80)
                            
                        except Exception as e:
                            logger.error(f"An error occurred during RISE v2.0 execution: {e}", exc_info=True)
                            print(f"ERROR: An error occurred during RISE v2.0 execution. See logs for details.")
                            sys.exit(1)
                    else:
                        # For non-strategic queries, use ACO's enhanced analysis
                        print(f"📊 **STANDARD QUERY - ACO ENHANCED ANALYSIS**")
                        print("Query processed through Adaptive Cognitive Orchestrator.")
                        print("=" * 80)
                        
                        # Use ACO's enhanced analysis capabilities
                        enhanced_result = cli._apply_universal_enhancement(args.query)
                        
                        print(f"\n🎯 **ACO ENHANCED ANSWER**")
                        print("=" * 80)
                        print(enhanced_result.get("enhanced_answer", "ACO analysis failed."))
                        print("=" * 80)
                        
                        print(f"\n✅ **ACO EXECUTION SUCCESSFUL**")
                        print(f"Analysis Type: {enhanced_result.get('analysis_type', 'Unknown')}")
                        print(f"Confidence: {enhanced_result.get('confidence', 0):.2f}")
                        
                        # Show comprehensive analysis if available
                        comprehensive_analysis = enhanced_result.get('comprehensive_analysis', '')
                        if comprehensive_analysis:
                            print(f"\n📈 **COMPREHENSIVE ANALYSIS**:")
                            print(comprehensive_analysis)
                
            except Exception as e:
                logger.error(f"An error occurred while processing query '{args.query}': {e}", exc_info=True)
                print(f"ERROR: An error occurred while processing the query. See logs for details.")
                sys.exit(1)
    
    # Interactive mode: run the normal CLI loop
    else:
        cli.run()

if __name__ == "__main__":
    main() 