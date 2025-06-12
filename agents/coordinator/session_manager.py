"""Session coordination and management"""

import time
import uuid
from typing import Any, Dict, Optional

from google.adk.sessions import InMemorySessionService

# Import existing state schema
from agents.base.state_schema import ProjectStatus, StateKeys, WorkflowPhase


class SessionCoordinator:
    """Coordinate session lifecycle and state management"""

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

    async def get_session(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get existing project session"""

        if project_id not in self.active_sessions:
            return None

        session_info = self.active_sessions[project_id]
        session = await self.session_service.get_session(
            app_name="branding_assistant",
            user_id=session_info["client_id"],
            session_id=session_info["session_id"],
        )

        # Update last activity
        self.active_sessions[project_id]["last_activity"] = time.time()

        return session

    async def update_session_state(
        self, project_id: str, state_updates: Dict[str, Any]
    ) -> bool:
        """Update session state"""

        if project_id not in self.active_sessions:
            return False

        session_info = self.active_sessions[project_id]

        # Get current session
        session = await self.session_service.get_session(
            app_name="branding_assistant",
            user_id=session_info["client_id"],
            session_id=session_info["session_id"],
        )

        if not session:
            return False

        # Update state
        session.state.update(state_updates)
        session.state["last_updated"] = time.time()

        # Update session
        await self.session_service.update_session(session)

        # Update activity tracking
        self.active_sessions[project_id]["last_activity"] = time.time()

        return True

    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions"""
        return self.active_sessions.copy()

    async def cleanup_inactive_sessions(self, timeout_hours: int = 24) -> int:
        """Clean up inactive sessions"""

        current_time = time.time()
        timeout_seconds = timeout_hours * 3600
        inactive_sessions = []

        for project_id, session_info in self.active_sessions.items():
            if current_time - session_info["last_activity"] > timeout_seconds:
                inactive_sessions.append(project_id)

        # Remove inactive sessions
        for project_id in inactive_sessions:
            del self.active_sessions[project_id]

        return len(inactive_sessions)
