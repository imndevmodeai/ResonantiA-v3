import logging
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Callable

# Assuming other ArchE components are available for type hinting
# from .vetting_agent import VettingAgent, VettingResult
# from .workflow_engine import IARCompliantWorkflowEngine

# Placeholder for VettingAgent if not available
class VettingAgent:
    def perform_vetting(self, *args, **kwargs) -> 'VettingResult':
        # Return a default approved result for standalone testing
        return VettingResult(status=VettingStatus.APPROVED, confidence=0.9, reasoning="Simulated Vetting OK")

class VettingStatus(Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

@dataclass
class VettingResult:
    status: VettingStatus
    confidence: float
    reasoning: str

logger = logging.getLogger(__name__)

class CfpStatus(Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    CLOSED = "CLOSED"
    COMPLETED = "COMPLETED"

@dataclass
class Proposal:
    """Represents a proposed solution to a Call for Proposals."""
    proposal_id: str = field(default_factory=lambda: f"prop-{uuid.uuid4()}")
    cfp_id: str
    proposer_id: str # Identifier for the agent/component submitting the proposal
    workflow_definition: Dict[str, Any] # An executable workflow
    summary: str
    confidence_score: float # Proposer's confidence in the solution (0.0 to 1.0)
    submission_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    vetting_result: Optional[VettingResult] = None
    status: str = "PENDING"

@dataclass
class CallForProposals:
    """Defines a problem that requires a novel solution."""
    cfp_id: str = field(default_factory=lambda: f"cfp-{uuid.uuid4()}")
    title: str
    problem_description: str
    success_criteria: List[str] # List of measurable criteria for a successful solution
    constraints: Dict[str, Any] = field(default_factory=dict)
    created_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: CfpStatus = CfpStatus.OPEN
    proposals: List[Proposal] = field(default_factory=list)
    selected_proposal_id: Optional[str] = None

class CfpFramework:
    """
    The Master Coordinator of the Marketplace of Ideas. This framework implements the
    'Call for Proposals' (CFP) mechanism, enabling ArchE to broadcast complex problems
    and solicit, vet, and select executable workflows as solutions. It fosters emergent,
    creative problem-solving by allowing different system components to compete in
    generating the most effective strategies.
    """

    def __init__(self, vetting_agent: VettingAgent, storage_path: str = "outputs/cfps/"):
        """
        Initializes the CFP Framework.

        Args:
            vetting_agent (VettingAgent): The agent responsible for validating proposals.
            storage_path (str): Directory to persist CFP data (for future implementation).
        """
        self.vetting_agent = vetting_agent
        self.active_cfps: Dict[str, CallForProposals] = {}
        logger.info("[CfpFramework] Initialized.")

    def issue_cfp(self, title: str, problem_description: str, success_criteria: List[str], constraints: Dict[str, Any] = None) -> CallForProposals:
        """
        Creates and broadcasts a new Call for Proposals.

        Returns:
            The newly created CallForProposals object.
        """
        cfp = CallForProposals(
            title=title,
            problem_description=problem_description,
            success_criteria=success_criteria,
            constraints=constraints or {}
        )
        self.active_cfps[cfp.cfp_id] = cfp
        logger.info(f"New CFP issued: '{title}' (ID: {cfp.cfp_id})")
        # In a real system, this would emit an event that other agents could listen to.
        return cfp

    def submit_proposal(self, cfp_id: str, proposer_id: str, workflow_definition: Dict[str, Any], summary: str, confidence_score: float) -> Proposal:
        """
        Submits a proposal for a given CFP. The proposal is immediately vetted.

        Raises:
            ValueError: If the CFP ID is invalid or the CFP is not open.
        """
        if cfp_id not in self.active_cfps:
            raise ValueError(f"CFP with ID '{cfp_id}' not found.")
        
        cfp = self.active_cfps[cfp_id]
        if cfp.status != CfpStatus.OPEN:
            raise ValueError(f"CFP '{cfp.title}' is not open for proposals.")

        proposal = Proposal(
            cfp_id=cfp_id,
            proposer_id=proposer_id,
            workflow_definition=workflow_definition,
            summary=summary,
            confidence_score=confidence_score
        )
        
        # Vet the proposal upon submission
        vetting_context = {"cfp_title": cfp.title, "proposer": proposer_id} # Simplified context
        proposal.vetting_result = self.vetting_agent.perform_vetting(
            proposed_action="workflow_proposal",
            action_inputs=workflow_definition,
            context=vetting_context
        )
        
        if proposal.vetting_result.status == VettingStatus.APPROVED:
            proposal.status = "VETTED_APPROVED"
            cfp.proposals.append(proposal)
            logger.info(f"New valid proposal {proposal.proposal_id} submitted for CFP {cfp_id} by {proposer_id}.")
        else:
            proposal.status = "VETTED_REJECTED"
            logger.warning(f"Proposal {proposal.proposal_id} for CFP {cfp_id} was rejected by vetting agent: {proposal.vetting_result.reasoning}")

        return proposal

    def review_and_select_proposal(self, cfp_id: str, selection_strategy: Callable[[List[Proposal]], Optional[Proposal]]) -> Optional[Proposal]:
        """
        Reviews all vetted proposals for a CFP and selects the best one based on a strategy.

        Args:
            cfp_id (str): The ID of the CFP to review.
            selection_strategy (Callable): A function that takes a list of proposals
                                          and returns the selected one.

        Returns:
            The selected Proposal, or None if no suitable proposal was found.
        """
        if cfp_id not in self.active_cfps:
            raise ValueError(f"CFP with ID '{cfp_id}' not found.")
        
        cfp = self.active_cfps[cfp_id]
        cfp.status = CfpStatus.UNDER_REVIEW
        
        approved_proposals = [p for p in cfp.proposals if p.status == "VETTED_APPROVED"]
        if not approved_proposals:
            logger.warning(f"No approved proposals to review for CFP '{cfp.title}'.")
            cfp.status = CfpStatus.CLOSED # No valid proposals, so close it.
            return None

        selected = selection_strategy(approved_proposals)
        
        if selected:
            cfp.selected_proposal_id = selected.proposal_id
            selected.status = "SELECTED"
            cfp.status = CfpStatus.COMPLETED
            logger.info(f"Proposal {selected.proposal_id} has been selected for CFP '{cfp.title}'.")
            return selected
        else:
            logger.info(f"No proposal was selected for CFP '{cfp.title}' based on the strategy.")
            cfp.status = CfpStatus.CLOSED
            return None

# --- Example Selection Strategy ---
def select_highest_confidence(proposals: List[Proposal]) -> Optional[Proposal]:
    """A simple selection strategy that picks the proposal with the highest confidence score."""
    if not proposals:
        return None
    return max(proposals, key=lambda p: p.confidence_score)


# --- Test Harness ---
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 1. Initialize dependencies
    mock_vetting_agent = VettingAgent()
    cfp_framework = CfpFramework(vetting_agent=mock_vetting_agent)

    # 2. Issue a new CFP
    print("\n--- [1] Issuing a new Call for Proposals ---")
    cfp = cfp_framework.issue_cfp(
        title="Automated Code Refactoring",
        problem_description="Refactor a legacy Python codebase to improve performance and readability.",
        success_criteria=["Achieve a 20% reduction in execution time.", "Increase code coverage by 30%."],
        constraints={"language": "python", "max_runtime_hours": 2}
    )
    print(f"Issued CFP: {cfp.title} (ID: {cfp.cfp_id})")

    # 3. Submit a few proposals
    print("\n--- [2] Submitting proposals from different agents ---")
    
    # Proposal A from 'CodeOptimizerAgent'
    workflow_a = {"name": "RefactorWorkflow_A", "tasks": {"start": {"action": "static_analysis"}}}
    prop_a = cfp_framework.submit_proposal(cfp.cfp_id, "CodeOptimizerAgent", workflow_a, "Uses static analysis and AST transformation.", 0.85)
    print(f"  - Proposal A submitted. Status: {prop_a.status}")

    # Proposal B from 'SimpleRefactorAgent'
    workflow_b = {"name": "RefactorWorkflow_B", "tasks": {"start": {"action": "regex_replace"}}}
    prop_b = cfp_framework.submit_proposal(cfp.cfp_id, "SimpleRefactorAgent", workflow_b, "Simple regex-based refactoring.", 0.92)
    print(f"  - Proposal B submitted. Status: {prop_b.status}")
    
    # Proposal C (will be rejected by mock vetting)
    # To test rejection, we'd need a more complex mock or a real VettingAgent.
    # For now, we assume all valid submissions are approved.

    # 4. Review and select the best proposal
    print("\n--- [3] Reviewing and selecting the best proposal ---")
    selected_proposal = cfp_framework.review_and_select_proposal(cfp.cfp_id, select_highest_confidence)
    
    if selected_proposal:
        print(f"Selected Proposal ID: {selected_proposal.proposal_id} from {selected_proposal.proposer_id}")
        print(f"Summary: {selected_proposal.summary}")
        print(f"CFP Status: {cfp.status}")
    else:
        print("No proposal was selected.")

if __name__ == "__main__":
    main()
