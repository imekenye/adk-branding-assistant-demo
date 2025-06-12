"""Base agent classes for standardized branding agent development"""

from typing import List

from google.adk.agents import LlmAgent
from google.adk.tools import Tool

from agents.base.state_schema import StateKeys, WorkflowPhase
from config.agent_configs.workflow_config import WorkflowTransition


class BrandingAgentBase(LlmAgent):
    """Base class for all branding workflow agents"""

    def __init__(
        self,
        name: str,
        phase: WorkflowPhase,
        output_key: str,
        instruction: str,
        description: str = None,
        tools: List[Tool] = None,
        **kwargs,
    ):
        # Standard branding agent configuration
        super().__init__(
            name=name,
            model="gemini-2.0-flash",  # Standard model for all agents
            instruction=self._build_instruction(instruction, phase),
            description=description or f"Branding agent for {phase.value} phase",
            output_key=output_key,  # Automatic state persistence
            tools=tools or [],
            **kwargs,
        )

        self.phase = phase
        self.output_state_key = output_key
        self.required_input_keys = self._get_required_inputs()

    def _build_instruction(self, base_instruction: str, phase: WorkflowPhase) -> str:
        """Build standardized instruction with phase context"""
        phase_context = f"""
You are working in the {phase.value.upper()} phase of a professional branding workflow.

WORKFLOW CONTEXT:
- Current Phase: {phase.value}
- Your Output Key: {self.output_state_key}
- Next Phase: {WorkflowTransition.get_next_phase(phase)}

QUALITY STANDARDS:
- Always provide professional, actionable outputs
- Ensure outputs align with previous workflow phases
- Validate all inputs before processing
- Flag any quality issues or missing requirements

STATE MANAGEMENT:
- Your output will be automatically saved to state['{self.output_state_key}']
- Access previous phase data from session state
- Maintain consistency with established brand direction

{base_instruction}
"""
        return phase_context

    def _get_required_inputs(self) -> List[str]:
        """Get required state keys for this agent's phase"""
        phase_index = WorkflowTransition.WORKFLOW_SEQUENCE.index(self.phase)
        if phase_index == 0:
            return []  # Discovery agent needs no prior inputs

        # Return output keys of all previous phases
        previous_phases = WorkflowTransition.WORKFLOW_SEQUENCE[:phase_index]
        return [self._phase_to_output_key(phase) for phase in previous_phases]

    def _phase_to_output_key(self, phase: WorkflowPhase) -> str:
        """Map phase to expected output key"""
        mapping = {
            WorkflowPhase.DISCOVERY: StateKeys.CLIENT_BRIEF,
            WorkflowPhase.RESEARCH: StateKeys.MARKET_RESEARCH,
            WorkflowPhase.VISUAL: StateKeys.VISUAL_DIRECTION,
            WorkflowPhase.LOGO: StateKeys.GENERATED_LOGOS,
            WorkflowPhase.BRAND: StateKeys.BRAND_SYSTEM,
            WorkflowPhase.ASSETS: StateKeys.FINAL_ASSETS,
        }
        return mapping.get(phase, f"{phase.value}_output")


class DiscoveryAgentBase(BrandingAgentBase):
    """Base class for Discovery phase agents"""

    def __init__(self, **kwargs):
        super().__init__(
            phase=WorkflowPhase.DISCOVERY, output_key=StateKeys.CLIENT_BRIEF, **kwargs
        )


class ResearchAgentBase(BrandingAgentBase):
    """Base class for Research phase agents"""

    def __init__(self, **kwargs):
        super().__init__(
            phase=WorkflowPhase.RESEARCH, output_key=StateKeys.MARKET_RESEARCH, **kwargs
        )


class VisualDirectionAgentBase(BrandingAgentBase):
    """Base class for Visual Direction phase agents"""

    def __init__(self, **kwargs):
        super().__init__(
            phase=WorkflowPhase.VISUAL, output_key=StateKeys.VISUAL_DIRECTION, **kwargs
        )


class LogoGenerationAgentBase(BrandingAgentBase):
    """Base class for Logo Generation phase agents"""

    def __init__(self, **kwargs):
        super().__init__(
            phase=WorkflowPhase.LOGO, output_key=StateKeys.GENERATED_LOGOS, **kwargs
        )


class BrandSystemAgentBase(BrandingAgentBase):
    """Base class for Brand System phase agents"""

    def __init__(self, **kwargs):
        super().__init__(
            phase=WorkflowPhase.BRAND, output_key=StateKeys.BRAND_SYSTEM, **kwargs
        )


class AssetGenerationAgentBase(BrandingAgentBase):
    """Base class for Asset Generation phase agents"""

    def __init__(self, **kwargs):
        super().__init__(
            phase=WorkflowPhase.ASSETS, output_key=StateKeys.FINAL_ASSETS, **kwargs
        )
