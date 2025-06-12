"""Workflow orchestration configuration for sequential agent pipeline"""

from typing import Dict, Optional

from agents.base.state_schema import StateKeys, WorkflowPhase


class WorkflowTransition:
    """Defines valid workflow transitions"""

    # Sequential workflow path
    WORKFLOW_SEQUENCE = [
        WorkflowPhase.DISCOVERY,
        WorkflowPhase.RESEARCH,
        WorkflowPhase.VISUAL,
        WorkflowPhase.LOGO,
        WorkflowPhase.BRAND,
        WorkflowPhase.ASSETS,
        WorkflowPhase.DELIVERY,
    ]

    # Valid transitions map
    VALID_TRANSITIONS = {
        WorkflowPhase.DISCOVERY: [WorkflowPhase.RESEARCH],
        WorkflowPhase.RESEARCH: [
            WorkflowPhase.VISUAL,
            WorkflowPhase.DISCOVERY,
        ],  # Can go back
        WorkflowPhase.VISUAL: [WorkflowPhase.LOGO, WorkflowPhase.RESEARCH],
        WorkflowPhase.LOGO: [WorkflowPhase.BRAND, WorkflowPhase.VISUAL],
        WorkflowPhase.BRAND: [WorkflowPhase.ASSETS, WorkflowPhase.LOGO],
        WorkflowPhase.ASSETS: [WorkflowPhase.DELIVERY, WorkflowPhase.BRAND],
        WorkflowPhase.DELIVERY: [],  # Final phase
    }

    # Agent responsible for each phase
    PHASE_AGENTS = {
        WorkflowPhase.DISCOVERY: "discovery_agent",
        WorkflowPhase.RESEARCH: "research_agent",
        WorkflowPhase.VISUAL: "visual_direction_agent",
        WorkflowPhase.LOGO: "logo_generation_agent",
        WorkflowPhase.BRAND: "brand_system_agent",
        WorkflowPhase.ASSETS: "asset_generation_agent",
        WorkflowPhase.DELIVERY: "coordinator_agent",  # Final packaging
    }

    @classmethod
    def can_transition(cls, from_phase: WorkflowPhase, to_phase: WorkflowPhase) -> bool:
        """Check if transition is valid"""
        return to_phase in cls.VALID_TRANSITIONS.get(from_phase, [])

    @classmethod
    def get_next_phase(cls, current_phase: WorkflowPhase) -> Optional[WorkflowPhase]:
        """Get next phase in sequence"""
        try:
            current_index = cls.WORKFLOW_SEQUENCE.index(current_phase)
            if current_index < len(cls.WORKFLOW_SEQUENCE) - 1:
                return cls.WORKFLOW_SEQUENCE[current_index + 1]
        except ValueError:
            pass
        return None

    @classmethod
    def get_responsible_agent(cls, phase: WorkflowPhase) -> str:
        """Get agent responsible for phase"""
        return cls.PHASE_AGENTS.get(phase, "coordinator_agent")


class WorkflowTriggers:
    """Defines triggers for agent activation"""

    # State-based triggers for each agent
    AGENT_TRIGGERS = {
        "discovery_agent": {
            "required_state": [],  # Always can start
            "trigger_conditions": [],
        },
        "research_agent": {
            "required_state": [StateKeys.CLIENT_BRIEF],
            "trigger_conditions": ["client_brief_complete"],
        },
        "visual_direction_agent": {
            "required_state": [StateKeys.CLIENT_BRIEF, StateKeys.MARKET_RESEARCH],
            "trigger_conditions": ["research_complete", "client_brief_complete"],
        },
        "logo_generation_agent": {
            "required_state": [StateKeys.VISUAL_DIRECTION],
            "trigger_conditions": ["visual_direction_approved"],
        },
        "brand_system_agent": {
            "required_state": [StateKeys.SELECTED_LOGO],
            "trigger_conditions": ["logo_selected"],
        },
        "asset_generation_agent": {
            "required_state": [StateKeys.BRAND_SYSTEM],
            "trigger_conditions": ["brand_system_complete"],
        },
    }

    @classmethod
    def can_trigger_agent(cls, agent_name: str, state: Dict) -> bool:
        """Check if agent can be triggered based on state"""
        trigger_config = cls.AGENT_TRIGGERS.get(agent_name, {})
        required_state = trigger_config.get("required_state", [])

        return all(key in state and state[key] is not None for key in required_state)
