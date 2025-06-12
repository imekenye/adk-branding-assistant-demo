"""State validation tools for workflow transitions"""

import time
from typing import Any, Dict, List

from google.adk.tools import ToolContext

from agents.base.state_schema import SessionState, StateKeys, WorkflowPhase


class StateValidator:
    """Validates state for phase transitions"""

    # Required state keys for each phase completion
    PHASE_REQUIREMENTS = {
        WorkflowPhase.DISCOVERY: [StateKeys.CLIENT_BRIEF],
        WorkflowPhase.RESEARCH: [StateKeys.MARKET_RESEARCH],
        WorkflowPhase.VISUAL: [StateKeys.VISUAL_DIRECTION],
        WorkflowPhase.LOGO: [StateKeys.SELECTED_LOGO],
        WorkflowPhase.BRAND: [StateKeys.BRAND_SYSTEM],
        WorkflowPhase.ASSETS: [StateKeys.FINAL_ASSETS],
    }

    @classmethod
    def validate_phase_completion(
        cls, state: Dict[str, Any], phase: WorkflowPhase
    ) -> bool:
        """Check if phase has required state keys"""
        required_keys = cls.PHASE_REQUIREMENTS.get(phase, [])
        return all(key in state and state[key] is not None for key in required_keys)

    @classmethod
    def get_missing_requirements(
        cls, state: Dict[str, Any], phase: WorkflowPhase
    ) -> List[str]:
        """Get list of missing state keys for phase"""
        required_keys = cls.PHASE_REQUIREMENTS.get(phase, [])
        return [key for key in required_keys if key not in state or state[key] is None]

    @classmethod
    def validate_state_schema(cls, state: Dict[str, Any]) -> bool:
        """Validate state against SessionState schema"""
        try:
            SessionState(**state)
            return True
        except Exception:
            return False


# Modern ADK v1.0.0 Function-based Tools
def validate_phase_transition(
    current_phase: str, target_phase: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Validate state for moving to next workflow phase"""
    current = WorkflowPhase(current_phase)
    target = WorkflowPhase(target_phase)

    # Check current phase completion
    is_complete = StateValidator.validate_phase_completion(tool_context.state, current)
    missing = StateValidator.get_missing_requirements(tool_context.state, current)

    return {
        "current_phase_complete": is_complete,
        "missing_requirements": missing,
        "can_transition": is_complete,
        "target_phase": target_phase,
        "validation_timestamp": time.time(),
    }


def validate_phase_transition_helper(
    state: Dict[str, Any], from_phase: str, to_phase: str
) -> bool:
    """Helper function for phase transition validation"""
    return StateValidator.validate_phase_completion(state, WorkflowPhase(from_phase))
