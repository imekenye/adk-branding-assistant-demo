"""Quality standards and thresholds configuration"""

from typing import Any, Dict

from agents.base.state_schema import WorkflowPhase


class QualityStandards:
    """Central quality standards configuration"""

    # Global quality thresholds
    GLOBAL_THRESHOLDS = {
        "minimum_acceptable_score": 0.7,
        "good_quality_score": 0.8,
        "excellent_quality_score": 0.9,
        "client_satisfaction_minimum": 0.8,
    }

    # Phase-specific requirements
    PHASE_REQUIREMENTS = {
        WorkflowPhase.DISCOVERY: {
            "required_fields": ["company_info", "target_audience", "style_preferences"],
            "minimum_uploaded_files": 0,
            "quality_gates": ["completeness", "clarity"],
        },
        WorkflowPhase.RESEARCH: {
            "required_sections": ["competitors", "industry_trends", "swot_analysis"],
            "minimum_competitors": 3,
            "quality_gates": ["depth", "relevance", "strategic_value"],
        },
        WorkflowPhase.VISUAL: {
            "required_components": [
                "color_palette",
                "typography_direction",
                "mood_board",
            ],
            "minimum_colors": 2,
            "quality_gates": ["coherence", "strategic_alignment", "executability"],
        },
        WorkflowPhase.LOGO: {
            "minimum_concepts": 3,
            "minimum_variations": 6,
            "required_formats": ["png"],
            "quality_gates": ["professional_quality", "scalability", "brand_alignment"],
        },
        WorkflowPhase.BRAND: {
            "required_documents": ["brand_guidelines"],
            "required_specifications": ["color_system", "typography_system"],
            "quality_gates": ["completeness", "professional_standards"],
        },
        WorkflowPhase.ASSETS: {
            "minimum_formats": ["png", "pdf"],
            "required_assets": ["logo_files", "delivery_package"],
            "quality_gates": ["format_compliance", "quality_consistency"],
        },
    }

    # Escalation triggers
    ESCALATION_TRIGGERS = {
        "consecutive_quality_failures": 3,
        "overall_score_below": 0.6,
        "client_satisfaction_below": 0.7,
        "critical_error_count": 1,
        "workflow_stuck_minutes": 30,
    }

    @classmethod
    def get_phase_standards(cls, phase: WorkflowPhase) -> Dict[str, Any]:
        """Get quality standards for specific phase"""
        return cls.PHASE_REQUIREMENTS.get(phase, {})

    @classmethod
    def should_escalate(cls, quality_metrics: Dict[str, Any]) -> bool:
        """Determine if quality issues should trigger escalation"""
        triggers = cls.ESCALATION_TRIGGERS

        # Check various escalation conditions
        if (
            quality_metrics.get("consecutive_failures", 0)
            >= triggers["consecutive_quality_failures"]
        ):
            return True

        if quality_metrics.get("overall_score", 1.0) < triggers["overall_score_below"]:
            return True

        if (
            quality_metrics.get("client_satisfaction", 1.0)
            < triggers["client_satisfaction_below"]
        ):
            return True

        return False
