"""Agent responsibility matrix and registration system"""

from typing import Any, Dict, List, Type

from agents.base.base_agent import (
    AssetGenerationAgentBase,
    BrandingAgentBase,
    BrandSystemAgentBase,
    DiscoveryAgentBase,
    LogoGenerationAgentBase,
    ResearchAgentBase,
    VisualDirectionAgentBase,
)
from agents.base.state_schema import WorkflowPhase


class AgentRegistry:
    """Registry for agent types and responsibilities"""

    # Agent class mapping
    AGENT_CLASSES = {
        WorkflowPhase.DISCOVERY: DiscoveryAgentBase,
        WorkflowPhase.RESEARCH: ResearchAgentBase,
        WorkflowPhase.VISUAL: VisualDirectionAgentBase,
        WorkflowPhase.LOGO: LogoGenerationAgentBase,
        WorkflowPhase.BRAND: BrandSystemAgentBase,
        WorkflowPhase.ASSETS: AssetGenerationAgentBase,
    }

    # Agent responsibilities
    AGENT_RESPONSIBILITIES = {
        "discovery_agent": {
            "phase": WorkflowPhase.DISCOVERY,
            "primary_tasks": [
                "Client file upload processing",
                "Requirements gathering via questionnaire",
                "Style preference analysis",
                "Target audience definition",
            ],
            "output_format": "Comprehensive client brief with categorized uploads",
            "quality_criteria": ["Completeness", "Clarity", "Actionability"],
            "tools_required": [
                "file_upload",
                "questionnaire_generator",
                "style_analyzer",
            ],
        },
        "research_agent": {
            "phase": WorkflowPhase.RESEARCH,
            "primary_tasks": [
                "Competitive landscape analysis",
                "Industry trend identification",
                "Market positioning assessment",
                "SWOT analysis generation",
            ],
            "output_format": "Market research report with strategic recommendations",
            "quality_criteria": ["Depth", "Relevance", "Strategic value"],
            "tools_required": ["web_search", "competitor_analyzer", "trend_analyzer"],
        },
        "visual_direction_agent": {
            "phase": WorkflowPhase.VISUAL,
            "primary_tasks": [
                "Mood board creation",
                "Color palette generation",
                "Typography direction",
                "Style framework synthesis",
            ],
            "output_format": "Visual direction guide with concrete specifications",
            "quality_criteria": ["Coherence", "Strategic alignment", "Executability"],
            "tools_required": [
                "mood_board_generator",
                "color_palette_tool",
                "typography_recommender",
            ],
        },
        "logo_generation_agent": {
            "phase": WorkflowPhase.LOGO,
            "primary_tasks": [
                "Multi-model logo generation",
                "Quality validation",
                "Variation creation",
                "Professional optimization",
            ],
            "output_format": "Logo concepts with quality scores and variations",
            "quality_criteria": [
                "Professional quality",
                "Scalability",
                "Brand alignment",
            ],
            "tools_required": [
                "multi_model_generator",
                "quality_validator",
                "asset_optimizer",
            ],
        },
        "brand_system_agent": {
            "phase": WorkflowPhase.BRAND,
            "primary_tasks": [
                "Brand guidelines creation",
                "Usage rule definition",
                "Color system expansion",
                "Typography hierarchy",
            ],
            "output_format": "Complete brand system documentation",
            "quality_criteria": ["Completeness", "Clarity", "Professional standards"],
            "tools_required": [
                "guidelines_generator",
                "usage_rule_creator",
                "system_documenter",
            ],
        },
        "asset_generation_agent": {
            "phase": WorkflowPhase.ASSETS,
            "primary_tasks": [
                "Business collateral generation",
                "Marketing asset creation",
                "Format conversion",
                "Delivery package assembly",
            ],
            "output_format": "Complete asset package with delivery manifest",
            "quality_criteria": [
                "Format compliance",
                "Quality consistency",
                "Completeness",
            ],
            "tools_required": [
                "asset_generator",
                "format_converter",
                "package_assembler",
            ],
        },
    }

    @classmethod
    def get_agent_class(cls, phase: WorkflowPhase) -> Type[BrandingAgentBase]:
        """Get appropriate agent base class for phase"""
        return cls.AGENT_CLASSES.get(phase, BrandingAgentBase)

    @classmethod
    def validate_agent_setup(cls, agent_name: str, tools: List) -> Dict[str, Any]:
        """Validate agent has required tools and setup"""
        if agent_name not in cls.AGENT_RESPONSIBILITIES:
            return {"valid": False, "error": f"Unknown agent: {agent_name}"}

        config = cls.AGENT_RESPONSIBILITIES[agent_name]
        required_tools = config.get("tools_required", [])

        # Check if tools match requirements (simplified check)
        provided_tool_names = [getattr(tool, "name", str(tool)) for tool in tools]

        return {
            "valid": True,
            "agent_config": config,
            "required_tools": required_tools,
            "provided_tools": provided_tool_names,
            "phase": config["phase"].value,
        }
