"""Quality gate definitions for phase transitions"""

from typing import Any, Callable, Dict

from agents.base.state_schema import StateKeys, WorkflowPhase


class QualityGate:
    """Individual quality gate definition"""

    def __init__(self, name: str, validator: Callable, threshold: float = 0.8):
        self.name = name
        self.validator = validator
        self.threshold = threshold

    def validate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run validation and return result"""
        try:
            score = self.validator(state)
            return {
                "gate_name": self.name,
                "score": score,
                "passed": score >= self.threshold,
                "threshold": self.threshold,
            }
        except Exception as e:
            return {
                "gate_name": self.name,
                "score": 0.0,
                "passed": False,
                "error": str(e),
                "threshold": self.threshold,
            }


class QualityGateConfig:
    """Quality gate configuration for each phase"""

    @staticmethod
    def validate_client_brief_completeness(state: Dict[str, Any]) -> float:
        """Validate client brief completeness"""
        brief = state.get(StateKeys.CLIENT_BRIEF, {})
        if not brief:
            return 0.0

        required_fields = ["company_info", "target_audience", "style_preferences"]
        completed = sum(1 for field in required_fields if brief.get(field))
        return completed / len(required_fields)

    @staticmethod
    def validate_research_depth(state: Dict[str, Any]) -> float:
        """Validate research completeness"""
        research = state.get(StateKeys.MARKET_RESEARCH, {})
        if not research:
            return 0.0

        required_sections = ["competitors", "industry_trends", "swot_analysis"]
        completed = sum(1 for section in required_sections if research.get(section))
        return completed / len(required_sections)

    @staticmethod
    def validate_visual_coherence(state: Dict[str, Any]) -> float:
        """Validate visual direction coherence"""
        visual = state.get(StateKeys.VISUAL_DIRECTION, {})
        if not visual:
            return 0.0

        # Check if color palette and mood board align
        has_colors = bool(visual.get("color_palette"))
        has_mood = bool(visual.get("mood_board_concept"))
        has_typography = bool(visual.get("typography_direction"))

        return (has_colors + has_mood + has_typography) / 3

    @staticmethod
    def validate_logo_quality(state: Dict[str, Any]) -> float:
        """Validate logo quality scores"""
        logos = state.get(StateKeys.GENERATED_LOGOS, {})
        if not logos:
            return 0.0

        quality_scores = logos.get("quality_scores", [])
        if not quality_scores:
            return 0.0

        return max(quality_scores)  # Best logo quality

    # Quality gates for each phase
    PHASE_GATES = {
        WorkflowPhase.DISCOVERY: [
            QualityGate("brief_completeness", validate_client_brief_completeness, 0.8),
        ],
        WorkflowPhase.RESEARCH: [
            QualityGate("research_depth", validate_research_depth, 0.7),
        ],
        WorkflowPhase.VISUAL: [
            QualityGate("visual_coherence", validate_visual_coherence, 0.8),
        ],
        WorkflowPhase.LOGO: [
            QualityGate("logo_quality", validate_logo_quality, 0.7),
        ],
        WorkflowPhase.BRAND: [
            # Brand system gates would go here
        ],
        WorkflowPhase.ASSETS: [
            # Asset generation gates would go here
        ],
    }

    @classmethod
    def validate_phase(
        cls, phase: WorkflowPhase, state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run all quality gates for a phase"""
        gates = cls.PHASE_GATES.get(phase, [])
        results = []
        overall_passed = True

        for gate in gates:
            result = gate.validate(state)
            results.append(result)
            if not result["passed"]:
                overall_passed = False

        return {
            "phase": phase.value,
            "gates": results,
            "overall_passed": overall_passed,
            "total_gates": len(gates),
            "passed_gates": sum(1 for r in results if r["passed"]),
        }
