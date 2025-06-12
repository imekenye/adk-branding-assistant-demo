"""Session management utilities for ADK v1.2.1"""

import time
import uuid
from typing import Any, Dict

from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext

# Import existing state schema
from agents.base.state_schema import (
    ProjectStatus,
    SessionState,
    StateKeys,
    WorkflowPhase,
)


class SessionManager:
    """Session lifecycle and state management utility class"""

    def __init__(self):
        self.session_service = InMemorySessionService()
        self.active_sessions = {}

    async def create_project_session(
        self, client_id: str, project_name: str
    ) -> Dict[str, Any]:
        """Create new project session"""

        project_id = f"proj_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        session_id = f"session_{project_id}"

        # Initialize session state
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
        }

        # Create ADK session
        session = await self.session_service.create_session(
            app_name="branding_assistant",
            user_id=client_id,
            session_id=session_id,
            state=initial_state,
        )

        # Track active session
        self.active_sessions[project_id] = {
            "session_id": session_id,
            "client_id": client_id,
            "created_at": time.time(),
            "last_activity": time.time(),
        }

        return {
            "project_id": project_id,
            "session_id": session_id,
            "initial_state": initial_state,
            "created_at": time.time(),
        }


# ADK v1.0.0 Function Tools
def create_session(
    client_id: str, project_name: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Create new project session"""
    session_manager = SessionManager()
    # Use asyncio.run for demo - in production use proper async context
    import asyncio

    result = asyncio.run(
        session_manager.create_project_session(client_id, project_name)
    )

    # Update tool context state
    tool_context.state.update(result["initial_state"])

    return result


def update_session_state(
    state_updates: Dict[str, Any], tool_context: ToolContext
) -> Dict[str, Any]:
    """Update session state with new data"""
    tool_context.state.update(state_updates)
    tool_context.state["last_updated"] = time.time()

    return {
        "success": True,
        "updated_keys": list(state_updates.keys()),
        "timestamp": time.time(),
    }
