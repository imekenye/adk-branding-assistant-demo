"""Workflow orchestration and agent handoff logic"""

import time
from typing import Any, Dict, List, Optional

from google.adk.tools import ToolContext

from agents.base.state_schema import StateKeys, WorkflowPhase
from config.agent_configs.quality_gates import QualityGateConfig
from config.agent_configs.workflow_config import WorkflowTransition, WorkflowTriggers


class WorkflowManager:
    """Manages workflow transitions and agent orchestration"""

    def __init__(self):
        self.transition_history = []

    def get_current_phase(self, state: Dict[str, Any]) -> WorkflowPhase:
        """Get current workflow phase"""
        phase_str = state.get(StateKeys.CURRENT_PHASE, WorkflowPhase.DISCOVERY.value)
        return WorkflowPhase(phase_str)

    def can_proceed_to_next_phase(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check if workflow can proceed to next phase"""
        current_phase = self.get_current_phase(state)
        next_phase = WorkflowTransition.get_next_phase(current_phase)

        if not next_phase:
            return {"can_proceed": False, "reason": "Already at final phase"}

        # Validate quality gates
        gate_results = QualityGateConfig.validate_phase(current_phase, state)

        # Check state requirements
        from tools.state_management.state_validators import StateValidator

        requirements_met = StateValidator.validate_phase_completion(
            state, current_phase
        )

        can_proceed = gate_results["overall_passed"] and requirements_met

        return {
            "can_proceed": can_proceed,
            "current_phase": current_phase.value,
            "next_phase": next_phase.value if next_phase else None,
            "quality_gates": gate_results,
            "requirements_met": requirements_met,
            "next_agent": (
                WorkflowTransition.get_responsible_agent(next_phase)
                if next_phase
                else None
            ),
        }

    def transition_to_phase(
        self, state: Dict[str, Any], target_phase: WorkflowPhase
    ) -> bool:
        """Perform phase transition with validation"""
        current_phase = self.get_current_phase(state)

        # Validate transition
        if not WorkflowTransition.can_transition(current_phase, target_phase):
            return False

        # Record transition
        transition = {
            "from_phase": current_phase.value,
            "to_phase": target_phase.value,
            "timestamp": time.time(),
            "agent": WorkflowTransition.get_responsible_agent(target_phase),
        }

        # Update state
        state[StateKeys.CURRENT_PHASE] = target_phase.value
        state["last_transition"] = transition
        state.setdefault("transition_history", []).append(transition)

        self.transition_history.append(transition)
        return True

    def get_next_agent(self, state: Dict[str, Any]) -> Optional[str]:
        """Determine which agent should run next"""
        current_phase = self.get_current_phase(state)

        # Check if current phase agent can be triggered
        current_agent = WorkflowTransition.get_responsible_agent(current_phase)
        if WorkflowTriggers.can_trigger_agent(current_agent, state):
            return current_agent

        # Check if we can move to next phase
        next_check = self.can_proceed_to_next_phase(state)
        if next_check["can_proceed"]:
            return next_check["next_agent"]

        return None


# ADK v1.0.0 Modern Function Tools
def transition_workflow_phase(
    target_phase: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Transition workflow to next phase with validation"""
    workflow_manager = WorkflowManager()
    target = WorkflowPhase(target_phase)
    current_phase = workflow_manager.get_current_phase(tool_context.state)

    # Check if transition is valid
    if not WorkflowTransition.can_transition(current_phase, target):
        return {
            "success": False,
            "error": f"Invalid transition from {current_phase.value} to {target_phase}",
            "current_phase": current_phase.value,
        }

    # Validate current phase completion
    can_proceed = workflow_manager.can_proceed_to_next_phase(tool_context.state)
    if not can_proceed["can_proceed"]:
        return {
            "success": False,
            "error": "Current phase requirements not met",
            "validation_details": can_proceed,
        }

    # Perform transition
    success = workflow_manager.transition_to_phase(tool_context.state, target)

    if success:
        # Update quality scores
        tool_context.state.setdefault(StateKeys.QUALITY_SCORES, {})
        tool_context.state[StateKeys.QUALITY_SCORES][
            f"{current_phase.value}_transition"
        ] = 1.0

        return {
            "success": True,
            "from_phase": current_phase.value,
            "to_phase": target_phase,
            "next_agent": WorkflowTransition.get_responsible_agent(target),
            "timestamp": time.time(),
        }

    return {
        "success": False,
        "error": "Transition failed",
        "current_phase": current_phase.value,
    }


def get_next_agent(tool_context: ToolContext) -> Dict[str, Any]:
    """Determine which agent should run next based on workflow state"""
    workflow_manager = WorkflowManager()
    current_phase = workflow_manager.get_current_phase(tool_context.state)
    next_agent = workflow_manager.get_next_agent(tool_context.state)

    # Get workflow status
    can_proceed = workflow_manager.can_proceed_to_next_phase(tool_context.state)

    return {
        "current_phase": current_phase.value,
        "recommended_agent": next_agent,
        "can_proceed_to_next": can_proceed["can_proceed"],
        "workflow_status": can_proceed,
        "available_transitions": WorkflowTransition.VALID_TRANSITIONS.get(
            current_phase, []
        ),
        "timestamp": time.time(),
    }


def validate_workflow_state(tool_context: ToolContext) -> Dict[str, Any]:
    """Comprehensive validation of current workflow state"""
    state = tool_context.state
    current_phase = WorkflowPhase(
        state.get(StateKeys.CURRENT_PHASE, WorkflowPhase.DISCOVERY.value)
    )

    # Run quality gates
    quality_results = QualityGateConfig.validate_phase(current_phase, state)

    # Check state completeness
    from tools.state_management.state_validators import StateValidator

    missing_requirements = StateValidator.get_missing_requirements(state, current_phase)

    # Check agent triggers
    available_agents = []
    for agent_name in WorkflowTriggers.AGENT_TRIGGERS.keys():
        if WorkflowTriggers.can_trigger_agent(agent_name, state):
            available_agents.append(agent_name)

    return {
        "current_phase": current_phase.value,
        "quality_validation": quality_results,
        "missing_requirements": missing_requirements,
        "available_agents": available_agents,
        "workflow_complete": current_phase == WorkflowPhase.DELIVERY,
        "validation_timestamp": time.time(),
    }
    """Tool for comprehensive workflow validation"""

    def __init__(self):
        super().__init__(
            name="validate_workflow_state",
            description="Comprehensive validation of current workflow state",
        )

    async def run(self, context: ToolContext) -> Dict[str, Any]:
        """Validate entire workflow state"""
        state = context.state
        current_phase = WorkflowPhase(
            state.get(StateKeys.CURRENT_PHASE, WorkflowPhase.DISCOVERY.value)
        )

        # Run quality gates
        quality_results = QualityGateConfig.validate_phase(current_phase, state)

        # Check state completeness
        from tools.state_management.state_validators import StateValidator

        missing_requirements = StateValidator.get_missing_requirements(
            state, current_phase
        )

        # Check agent triggers
        available_agents = []
        for agent_name in WorkflowTriggers.AGENT_TRIGGERS.keys():
            if WorkflowTriggers.can_trigger_agent(agent_name, state):
                available_agents.append(agent_name)

        return {
            "current_phase": current_phase.value,
            "quality_validation": quality_results,
            "missing_requirements": missing_requirements,
            "available_agents": available_agents,
            "workflow_complete": current_phase == WorkflowPhase.DELIVERY,
            "validation_timestamp": time.time(),
        }
