"""Standard tool patterns for branding agents"""

import time
from pathlib import Path
from typing import Any, Dict, List

from google.adk.tools import ToolContext

from agents.base.state_schema import StateKeys

# Core Agent Functions (replaces BrandingToolBase and derived classes)


def validate_required_state(
    required_keys: List[str], tool_context: ToolContext
) -> Dict[str, Any]:
    """Validate that required state keys exist before proceeding"""
    state = tool_context.state
    missing_keys = []
    present_keys = []

    for key in required_keys:
        if key in state and state[key] is not None:
            present_keys.append(key)
        else:
            missing_keys.append(key)

    is_valid = len(missing_keys) == 0

    return {
        "validation_passed": is_valid,
        "required_keys": required_keys,
        "present_keys": present_keys,
        "missing_keys": missing_keys,
        "completion_rate": (
            len(present_keys) / len(required_keys) if required_keys else 1.0
        ),
        "tool_metadata": {
            "tool_name": "validate_required_state",
            "execution_timestamp": time.time(),
            "success": True,
        },
    }


def upload_file(
    file_path: str, tool_context: ToolContext, file_type: str = "auto"
) -> Dict[str, Any]:
    """Upload and process client files (images, documents, references)"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Categorize file
        file_ext = file_path.suffix.lower()
        category = _categorize_file(file_ext)

        # Create file metadata
        file_metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_type": file_ext,
            "category": category,
            "upload_timestamp": time.time(),
        }

        # Add to state
        tool_context.state.setdefault(StateKeys.UPLOADED_FILES, []).append(
            file_metadata
        )

        return {
            "file_metadata": file_metadata,
            "category": category,
            "total_uploaded_files": len(tool_context.state[StateKeys.UPLOADED_FILES]),
            "tool_metadata": {
                "tool_name": "upload_file",
                "execution_timestamp": time.time(),
                "success": True,
            },
        }
    except Exception as e:
        return {
            "error": str(e),
            "tool_metadata": {
                "tool_name": "upload_file",
                "execution_timestamp": time.time(),
                "success": False,
            },
        }


def _categorize_file(file_ext: str) -> str:
    """Categorize file by extension"""
    categories = {
        "reference_image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "existing_logo": [".svg", ".ai", ".eps"],
        "document": [".pdf", ".doc", ".docx"],
        "spreadsheet": [".xls", ".xlsx", ".csv"],
    }

    for category, extensions in categories.items():
        if file_ext in extensions:
            return category

    return "unknown"


def record_quality_score(
    score_name: str, score_value: float, tool_context: ToolContext
) -> Dict[str, Any]:
    """Record quality score for current phase or deliverable"""
    if not 0.0 <= score_value <= 1.0:
        return {
            "error": "Quality score must be between 0.0 and 1.0",
            "tool_metadata": {
                "tool_name": "record_quality_score",
                "execution_timestamp": time.time(),
                "success": False,
            },
        }

    # Update quality scores
    tool_context.state.setdefault(StateKeys.QUALITY_SCORES, {})[
        score_name
    ] = score_value

    # Record in history
    score_record = {
        "score_name": score_name,
        "score_value": score_value,
        "timestamp": time.time(),
        "phase": tool_context.state.get(StateKeys.CURRENT_PHASE),
    }

    tool_context.state.setdefault("quality_score_history", []).append(score_record)

    return {
        "score_recorded": score_record,
        "total_scores": len(tool_context.state[StateKeys.QUALITY_SCORES]),
        "average_score": sum(tool_context.state[StateKeys.QUALITY_SCORES].values())
        / len(tool_context.state[StateKeys.QUALITY_SCORES]),
        "tool_metadata": {
            "tool_name": "record_quality_score",
            "execution_timestamp": time.time(),
            "success": True,
        },
    }


def update_progress(
    progress_percentage: float, status_message: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Update progress tracking for current phase"""
    if not 0.0 <= progress_percentage <= 100.0:
        return {
            "error": "Progress percentage must be between 0.0 and 100.0",
            "tool_metadata": {
                "tool_name": "update_progress",
                "execution_timestamp": time.time(),
                "success": False,
            },
        }

    current_phase = tool_context.state.get(StateKeys.CURRENT_PHASE)

    progress_update = {
        "phase": current_phase,
        "progress_percentage": progress_percentage,
        "status_message": status_message,
        "timestamp": time.time(),
    }

    # Update current progress
    tool_context.state.setdefault("progress_tracking", {})[
        current_phase
    ] = progress_update

    # Add to progress history
    tool_context.state.setdefault("progress_history", []).append(progress_update)

    return {
        "progress_update": progress_update,
        "phase_progress": tool_context.state["progress_tracking"],
        "overall_completion": _calculate_overall_progress(tool_context.state),
        "tool_metadata": {
            "tool_name": "update_progress",
            "execution_timestamp": time.time(),
            "success": True,
        },
    }


def _calculate_overall_progress(state: Dict[str, Any]) -> float:
    """Calculate overall workflow progress"""
    from config.agent_configs.workflow_config import WorkflowTransition

    progress_tracking = state.get("progress_tracking", {})
    total_phases = len(WorkflowTransition.WORKFLOW_SEQUENCE)

    if not progress_tracking:
        return 0.0

    # Weight each phase equally
    phase_weight = 100.0 / total_phases
    total_progress = 0.0

    for phase in WorkflowTransition.WORKFLOW_SEQUENCE:
        phase_progress = progress_tracking.get(phase.value, {}).get(
            "progress_percentage", 0.0
        )
        total_progress += (phase_progress * phase_weight) / 100.0

    return min(total_progress, 100.0)


# Agent Registration Helper Functions (replaces AgentRegistry class methods)
def validate_agent_setup(agent_name: str, tools: List) -> Dict[str, Any]:
    """Validate agent has required tools and setup"""
    from config.agent_configs.responsibilities import AgentRegistry

    if agent_name not in AgentRegistry.AGENT_RESPONSIBILITIES:
        return {"valid": False, "error": f"Unknown agent: {agent_name}"}

    config = AgentRegistry.AGENT_RESPONSIBILITIES[agent_name]
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
