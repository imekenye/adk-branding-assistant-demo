"""Session service configuration for ADK v1.2.1"""

import os
import time
import uuid
from typing import Any, Dict, Optional

from google.adk.sessions import InMemorySessionService, Session

from agents.base.state_schema import (
    ProjectStatus,
    SessionState,
    StateKeys,
    WorkflowPhase,
)


class BrandingSessionConfig:
    """Configuration for branding assistant sessions"""

    # Session settings
    APP_NAME = "adk_branding_assistant"
    DEFAULT_SESSION_TIMEOUT = 3600 * 24  # 24 hours
    MAX_RETRY_COUNT = 3

    # State backup settings
    BACKUP_INTERVAL = 300  # 5 minutes
    MAX_BACKUPS = 10

    @classmethod
    def get_session_service(cls) -> InMemorySessionService:
        """Get configured session service for development"""
        return InMemorySessionService()

    @classmethod
    def create_initial_state(
        cls, client_id: str, project_name: str = None
    ) -> Dict[str, Any]:
        """Create initial session state for new project"""
        project_id = f"proj_{uuid.uuid4().hex[:8]}"

        return {
            StateKeys.PROJECT_STATUS: ProjectStatus.ACTIVE.value,
            StateKeys.CURRENT_PHASE: WorkflowPhase.DISCOVERY.value,
            StateKeys.CLIENT_ID: client_id,
            StateKeys.PROJECT_ID: project_id,
            "created_timestamp": time.time(),
            "project_name": project_name or f"Project {project_id}",
            # Initialize empty phase data
            StateKeys.CLIENT_BRIEF: None,
            StateKeys.MARKET_RESEARCH: None,
            StateKeys.VISUAL_DIRECTION: None,
            StateKeys.GENERATED_LOGOS: None,
            StateKeys.SELECTED_LOGO: None,
            StateKeys.BRAND_SYSTEM: None,
            StateKeys.FINAL_ASSETS: None,
            # Initialize collections
            StateKeys.UPLOADED_FILES: [],
            "generated_files": [],
            "temp_files": [],
            # Initialize quality control
            StateKeys.APPROVAL_CHECKPOINTS: {},
            StateKeys.QUALITY_SCORES: {},
            "revision_history": [],
            # Initialize error handling
            StateKeys.LAST_ERROR: None,
            StateKeys.RETRY_COUNT: 0,
            StateKeys.ESCALATION_TRIGGERED: False,
        }
