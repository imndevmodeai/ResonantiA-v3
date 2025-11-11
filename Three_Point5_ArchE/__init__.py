import logging
import sys
from pathlib import Path

# --- System-Wide Logging Configuration ---
# Set up a basic logger that outputs to stdout.
# A more robust implementation would use the Config object to set level, file output, etc.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("ArchE")
logger.info("ArchE System Initializing...")

# --- Add Project Root to Python Path ---
# This allows for consistent imports across the system.
sys.path.append(str(Path(__file__).parent.parent))

# --- Core Component Imports ---
# Import the primary classes and singletons from each module to make them
# accessible via the package root.
from .config import Config
from .action_context import ActionContext
from .action_registry import ActionRegistry, main_action_registry
from .spr_manager import SprManager
from .vetting_agent import VettingAgent
from .workflow_engine import IARCompliantWorkflowEngine
from .rise_orchestrator import RISE_Orchestrator
from .autonomous_orchestrator import AutonomousOrchestrator
from .adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
from .executable_spec_parser import ExecutableSpecParser
from .cfp_framework import CfpFramework
from .distributed_arche_registry import DistributedArcheRegistry
from . import phiên_dịch_so_sánh_luồng_tương_tự_được_tăng_cường_lượng_tử
from . import khai_thác_dữ_liệu_và_lập_hồ_sơ
from . import trí_tuệ_thích_ứng_cho_an_ninh_mạng_tiên_tiến
from . import tăng_cường_khả_năng_xử_lý_ngôn_ngữ_tự_nhiên_với_sự_hài_hước_và_thông_minh_nhân_tạo
from .proposal_framework import ProposalFramework

# --- Singleton Instantiation ---
# Instantiate and configure the core singleton objects that will be used
# throughout the system's lifecycle.

logger.info("Instantiating singleton services...")

# Load configuration first as other modules may depend on it.
config = Config()

# The Librarian of Alexandria: Manages all knowledge.
spr_manager = SprManager(knowledge_base_path=config.get('paths.spr_knowledge_base'))

# The Guardian: Vets all actions before execution.
vetting_agent = VettingAgent()

# The Heartbeat of ArchE: Executes workflows.
workflow_engine = IARCompliantWorkflowEngine(
    workflows_dir=config.get('paths.workflows'),
    spr_manager=spr_manager
)

# The Genesis Engine: High-level problem solving.
rise_orchestrator = RISE_Orchestrator(
    workflows_dir=config.get('paths.workflows'),
    spr_manager=spr_manager,
    workflow_engine=workflow_engine
)

# The CEO-Level Manager: Autonomous work management.
autonomous_orchestrator = AutonomousOrchestrator()

logger.info("Core components initialized.")


# --- Populate Action Registry ---
# Discover and register all available tools/actions.
# A more advanced implementation would dynamically discover actions from modules.
def _populate_actions():
    """Registers all the core system tools into the main registry."""
    from .llm_tool import generate_text_llm
    from .web_search_tool import search_web
    from .code_executor import execute_code
    from .predictive_modeling_tool import run_prediction
    from .causal_inference_tool import CausalInferenceTool
    from .agent_based_modeling_tool import perform_abm
    from .temporal_reasoning_engine import TemporalReasoningEngine
    from .quantum_utils import quantum_utils_tool

    actions_to_register = {
        "generate_text_llm": generate_text_llm,
        "search_web": search_web,
        "execute_code": execute_code,
        "run_prediction": run_prediction,
        "perform_abm": perform_abm,
        "temporal_analysis": TemporalReasoningEngine().perform_temporal_analysis,
        "discover_causal_graph": CausalInferenceTool().discover_temporal_graph,
        "quantum_operation": quantum_utils_tool
    }
    
    for name, func in actions_to_register.items():
        main_action_registry.register_action(name, func, module=func.__module__)
    
    logger.info(f"Populated main action registry with {len(actions_to_register)} actions.")

_populate_actions()

# --- System Status ---
SYSTEM_INITIALIZED = True
logger.info("ArchE System initialization complete. Ready for operation.")

# --- Public API ---
# Expose the core components that other parts of the application will interact with.
__all__ = [
    "config",
    "ActionContext",
    "main_action_registry",
    "spr_manager",
    "vetting_agent",
    "workflow_engine",
    "rise_orchestrator",
    "autonomous_orchestrator",
    "AdaptiveCognitiveOrchestrator",
    "ExecutableSpecParser",
    "CfpFramework",
    "DistributedArcheRegistry",
    "logger"
]
