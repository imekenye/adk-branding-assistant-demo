"""
Root Coordinator Agent for AI Branding Assistant
Manages the complete branding workflow and client interaction
"""

import time
import uuid
from pathlib import Path
from typing import Any, Dict

from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext

from agents.base.state_schema import ProjectStatus, StateKeys, WorkflowPhase

# Import sub-agents and utilities
from agents.discovery.agent import root_agent as discovery_agent
from agents.research.agent import root_agent as research_agent
from agents.visual.agent import root_agent as visual_agent


# Function Tools (ADK v1.0.0 pattern - no classes)
def create_project_session(
    client_id: str, project_name: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Initialize new branding project session with proper state management"""
    project_id = f"proj_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    # Initialize complete session state
    initial_state = {
        StateKeys.PROJECT_STATUS: ProjectStatus.ACTIVE.value,
        StateKeys.CURRENT_PHASE: WorkflowPhase.DISCOVERY.value,
        StateKeys.CLIENT_ID: client_id,
        StateKeys.PROJECT_ID: project_id,
        "created_timestamp": time.time(),
        "project_name": project_name,
        "uploaded_files": [],
        "progress_tracking": {},
        "client_communications": [],
        "quality_scores": {},
        "phase_approvals": {},
    }

    # Update tool context state (ADK v1.0.0 state management)
    tool_context.state.update(initial_state)

    return {
        "success": True,
        "project_id": project_id,
        "client_id": client_id,
        "project_name": project_name,
        "current_phase": WorkflowPhase.DISCOVERY.value,
        "session_initialized": True,
        "timestamp": time.time(),
    }


def communicate_with_client(
    message: str, tool_context: ToolContext, message_type: str = "update"
) -> Dict[str, Any]:
    """Professional client communication with structured messaging"""
    communication = {
        "message": message,
        "type": message_type,  # "update", "request_approval", "question", "delivery"
        "timestamp": time.time(),
        "phase": tool_context.state.get(StateKeys.CURRENT_PHASE),
        "project_id": tool_context.state.get(StateKeys.PROJECT_ID),
    }

    # Store in communication history
    tool_context.state.setdefault("client_communications", []).append(communication)

    return {
        "communication_sent": True,
        "message_type": message_type,
        "phase": communication["phase"],
        "timestamp": communication["timestamp"],
    }


def upload_and_process_file(
    file_path: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Handle client file uploads with categorization and validation"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        # File categorization logic
        file_ext = file_path.suffix.lower()
        category_map = {
            (".jpg", ".jpeg", ".png", ".gif", ".webp"): "reference_image",
            (".svg", ".ai", ".eps"): "existing_logo",
            (".pdf",): "document",
            (".doc", ".docx", ".txt"): "text_document",
        }

        category = "other"
        for extensions, cat in category_map.items():
            if file_ext in extensions:
                category = cat
                break

        # Create file metadata
        file_info = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_type": file_ext,
            "category": category,
            "upload_timestamp": time.time(),
            "project_id": tool_context.state.get(StateKeys.PROJECT_ID),
        }

        # Add to session state
        tool_context.state.setdefault(StateKeys.UPLOADED_FILES, []).append(file_info)

        return {
            "success": True,
            "file_info": file_info,
            "total_files": len(tool_context.state[StateKeys.UPLOADED_FILES]),
            "category": category,
        }

    except Exception as e:
        return {"success": False, "error": f"File processing failed: {str(e)}"}


def track_progress(
    phase: str,
    progress_percentage: float,
    status_message: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Track workflow progress with real-time updates"""
    # Validate progress percentage
    progress_percentage = max(0.0, min(100.0, progress_percentage))

    progress_update = {
        "phase": phase,
        "progress_percentage": progress_percentage,
        "status_message": status_message,
        "timestamp": time.time(),
        "project_id": tool_context.state.get(StateKeys.PROJECT_ID),
    }

    # Update current progress
    tool_context.state.setdefault("progress_tracking", {})[phase] = progress_update

    # Add to progress history
    tool_context.state.setdefault("progress_history", []).append(progress_update)

    # Calculate overall workflow progress
    phases = [
        WorkflowPhase.DISCOVERY,
        WorkflowPhase.RESEARCH,
        WorkflowPhase.VISUAL,
        WorkflowPhase.LOGO,
        WorkflowPhase.BRAND,
        WorkflowPhase.ASSETS,
    ]

    progress_tracking = tool_context.state.get("progress_tracking", {})
    total_progress = sum(
        progress_tracking.get(p.value, {}).get("progress_percentage", 0.0)
        for p in phases
    ) / len(phases)

    tool_context.state["overall_progress"] = total_progress

    return {
        "progress_updated": True,
        "phase": phase,
        "progress_percentage": progress_percentage,
        "overall_progress": total_progress,
        "status_message": status_message,
    }


def transition_workflow_phase(
    target_phase: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Manage workflow phase transitions with validation"""
    current_phase = tool_context.state.get(
        StateKeys.CURRENT_PHASE, WorkflowPhase.DISCOVERY.value
    )

    # Workflow transition validation
    valid_transitions = {
        WorkflowPhase.DISCOVERY.value: [WorkflowPhase.RESEARCH.value],
        WorkflowPhase.RESEARCH.value: [
            WorkflowPhase.VISUAL.value,
            WorkflowPhase.DISCOVERY.value,
        ],
        WorkflowPhase.VISUAL.value: [
            WorkflowPhase.LOGO.value,
            WorkflowPhase.RESEARCH.value,
        ],
        WorkflowPhase.LOGO.value: [
            WorkflowPhase.BRAND.value,
            WorkflowPhase.VISUAL.value,
        ],
        WorkflowPhase.BRAND.value: [
            WorkflowPhase.ASSETS.value,
            WorkflowPhase.LOGO.value,
        ],
        WorkflowPhase.ASSETS.value: [WorkflowPhase.DELIVERY.value],
    }

    if target_phase not in valid_transitions.get(current_phase, []):
        return {
            "success": False,
            "error": f"Invalid transition from {current_phase} to {target_phase}",
            "current_phase": current_phase,
        }

    # Validate phase completion requirements
    phase_requirements = {
        WorkflowPhase.DISCOVERY.value: [StateKeys.CLIENT_BRIEF],
        WorkflowPhase.RESEARCH.value: [StateKeys.MARKET_RESEARCH],
        WorkflowPhase.VISUAL.value: [StateKeys.VISUAL_DIRECTION],
        WorkflowPhase.LOGO.value: [StateKeys.SELECTED_LOGO],
        WorkflowPhase.BRAND.value: [StateKeys.BRAND_SYSTEM],
        WorkflowPhase.ASSETS.value: [StateKeys.FINAL_ASSETS],
    }

    required_keys = phase_requirements.get(current_phase, [])
    missing_keys = [
        key
        for key in required_keys
        if key not in tool_context.state or tool_context.state[key] is None
    ]

    if missing_keys:
        return {
            "success": False,
            "error": "Current phase requirements not met",
            "missing_requirements": missing_keys,
            "current_phase": current_phase,
        }

    # Perform transition
    transition_record = {
        "from_phase": current_phase,
        "to_phase": target_phase,
        "timestamp": time.time(),
        "project_id": tool_context.state.get(StateKeys.PROJECT_ID),
    }

    tool_context.state[StateKeys.CURRENT_PHASE] = target_phase
    tool_context.state["last_transition"] = transition_record
    tool_context.state.setdefault("transition_history", []).append(transition_record)

    return {
        "success": True,
        "from_phase": current_phase,
        "to_phase": target_phase,
        "timestamp": transition_record["timestamp"],
    }


def get_project_status(tool_context: ToolContext) -> Dict[str, Any]:
    """Get comprehensive project status and metrics"""
    state = tool_context.state

    # Calculate phase completion
    completed_phases = []
    phases = [
        WorkflowPhase.DISCOVERY,
        WorkflowPhase.RESEARCH,
        WorkflowPhase.VISUAL,
        WorkflowPhase.LOGO,
        WorkflowPhase.BRAND,
        WorkflowPhase.ASSETS,
    ]

    for phase in phases:
        if phase.value in state.get("phase_approvals", {}):
            completed_phases.append(phase.value)

    # Progress metrics
    overall_progress = state.get("overall_progress", 0.0)
    current_phase = state.get(StateKeys.CURRENT_PHASE, WorkflowPhase.DISCOVERY.value)

    return {
        "project_id": state.get(StateKeys.PROJECT_ID),
        "client_id": state.get(StateKeys.CLIENT_ID),
        "project_status": state.get(StateKeys.PROJECT_STATUS),
        "current_phase": current_phase,
        "overall_progress": overall_progress,
        "completed_phases": completed_phases,
        "total_files": len(state.get(StateKeys.UPLOADED_FILES, [])),
        "quality_scores": state.get(StateKeys.QUALITY_SCORES, {}),
        "last_activity": time.time(),
        "phase_breakdown": state.get("progress_tracking", {}),
    }


def delegate_to_agent(
    agent_name: str, task_description: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Intelligent agent delegation with context passing"""
    current_phase = tool_context.state.get(StateKeys.CURRENT_PHASE)

    # Agent mapping for delegation
    agent_mapping = {
        "discovery": WorkflowPhase.DISCOVERY.value,
        "research": WorkflowPhase.RESEARCH.value,
        "visual": WorkflowPhase.VISUAL.value,
        "logo": WorkflowPhase.LOGO.value,
    }

    # Validate delegation
    if agent_name not in agent_mapping:
        return {
            "success": False,
            "error": f"Unknown agent: {agent_name}",
            "available_agents": list(agent_mapping.keys()),
        }

    expected_phase = agent_mapping[agent_name]
    if current_phase != expected_phase:
        return {
            "success": False,
            "error": f"Agent {agent_name} not available in phase {current_phase}",
            "current_phase": current_phase,
            "expected_phase": expected_phase,
        }

    # Delegation successful - agent will be invoked via sub_agents
    delegation_record = {
        "agent_name": agent_name,
        "task_description": task_description,
        "phase": current_phase,
        "timestamp": time.time(),
        "project_id": tool_context.state.get(StateKeys.PROJECT_ID),
    }

    tool_context.state.setdefault("delegation_history", []).append(delegation_record)

    return {
        "success": True,
        "delegated_to": agent_name,
        "task_description": task_description,
        "current_phase": current_phase,
        "timestamp": delegation_record["timestamp"],
    }


def validate_quality_gates(phase: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Quality gate validation for phase transitions"""
    quality_thresholds = {
        WorkflowPhase.DISCOVERY.value: 0.8,
        WorkflowPhase.RESEARCH.value: 0.7,
        WorkflowPhase.VISUAL.value: 0.8,
        WorkflowPhase.LOGO.value: 0.8,
    }

    threshold = quality_thresholds.get(phase, 0.7)
    current_scores = tool_context.state.get(StateKeys.QUALITY_SCORES, {})
    phase_score = current_scores.get(f"{phase}_score", 0.0)

    quality_passed = phase_score >= threshold

    quality_result = {
        "phase": phase,
        "quality_score": phase_score,
        "threshold": threshold,
        "quality_passed": quality_passed,
        "timestamp": time.time(),
    }

    # Store quality validation
    tool_context.state.setdefault("quality_validations", []).append(quality_result)

    return quality_result


# Root Coordinator Agent Implementation (ADK v1.0.0)
root_agent = LlmAgent(
    name="ai_brand_designer",
    model="gemini-2.0-flash",
    instruction="""You are the AI Brand Designer, the master coordinator of a sophisticated multi-agent branding workflow.

🎯 CORE MISSION:
Orchestrate specialized agents to deliver complete, professional brand identities through seamless collaboration and quality assurance.

🔄 WORKFLOW PHASES:
1. DISCOVERY → Client intake, file uploads, style preferences, requirements gathering
2. RESEARCH → Market analysis, competitive intelligence, strategic positioning  
3. VISUAL → Mood boards, color palettes, typography, creative direction
4. LOGO → Multi-model AI logo generation, quality validation, client selection
5. BRAND → Guidelines, usage rules, brand system documentation
6. ASSETS → Final deliverables, format conversion, delivery packages

🤖 AGENT NETWORK:
• Discovery Agent: Client requirements and reference processing
• Research Agent: Market intelligence and strategic insights  
• Visual Direction Agent: Creative strategy and visual frameworks
• Logo Generation Agent: Multi-model logo creation and optimization
• Brand System Agent: Guidelines and professional documentation
• Asset Generation Agent: Final deliverable packaging

💬 CLIENT INTERACTION EXCELLENCE:
- Maintain professional, consultative communication style
- Provide clear progress updates and next steps
- Request approval at critical milestones
- Handle file uploads and process client references seamlessly
- Escalate complex issues with transparent communication

🔍 QUALITY STANDARDS:
- Validate deliverables at each phase boundary
- Ensure brand consistency across all outputs  
- Meet professional design standards throughout
- Provide comprehensive, client-ready packages

🛠 TOOL USAGE:
Use your function tools to create sessions, communicate professionally, process uploads, track progress, manage transitions, delegate intelligently, monitor status, and validate quality gates.

Remember: You coordinate, don't execute. Trust your specialized agents and ensure smooth handoffs between phases.""",
    description="Professional AI Brand Designer coordinating multi-agent branding workflow with quality assurance",
    # Sub-agents for delegation (ADK v1.0.0 pattern)
    sub_agents=[
        discovery_agent,
        research_agent,
        visual_agent,
        # Logo, brand, and asset agents will be added in subsequent chunks
    ],
    # Function tools (ADK v1.0.0 - no Tool classes)
    tools=[
        create_project_session,
        communicate_with_client,
        upload_and_process_file,
        track_progress,
        transition_workflow_phase,
        get_project_status,
        delegate_to_agent,
        validate_quality_gates,
    ],
)

# Session service configuration for development (ADK v1.0.0)
session_service = InMemorySessionService()

# Export for ADK runner
__all__ = ["root_agent", "session_service"]
