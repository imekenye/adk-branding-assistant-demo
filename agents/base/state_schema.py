"""Session state schema for ADK v1.2.1 multi-agent branding workflow"""

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    """Project lifecycle states"""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowPhase(str, Enum):
    """Sequential workflow phases"""

    DISCOVERY = "discovery"
    RESEARCH = "research"
    VISUAL = "visual"
    LOGO = "logo"
    BRAND = "brand"
    ASSETS = "assets"
    DELIVERY = "delivery"


class StateKeys:
    """State key constants for consistent access"""

    # Project management
    PROJECT_STATUS = "project_status"
    CURRENT_PHASE = "current_phase"
    CLIENT_ID = "client_id"
    PROJECT_ID = "project_id"

    # Agent outputs (output_key values)
    CLIENT_BRIEF = "client_brief"
    MARKET_RESEARCH = "market_research"
    VISUAL_DIRECTION = "visual_direction"
    GENERATED_LOGOS = "generated_logos"
    SELECTED_LOGO = "selected_logo"
    BRAND_SYSTEM = "brand_system"
    FINAL_ASSETS = "final_assets"

    # File management
    UPLOADED_FILES = "uploaded_files"
    GENERATED_FILES = "generated_files"

    # Quality control
    APPROVAL_CHECKPOINTS = "approval_checkpoints"
    QUALITY_SCORES = "quality_scores"

    # Error handling
    LAST_ERROR = "last_error"
    RETRY_COUNT = "retry_count"
    ESCALATION_TRIGGERED = "escalation_triggered"


class SessionState(BaseModel):
    """Complete session state structure for validation"""

    # Project management
    project_status: ProjectStatus = ProjectStatus.ACTIVE
    current_phase: WorkflowPhase = WorkflowPhase.DISCOVERY
    client_id: str
    project_id: str
    created_timestamp: float = Field(default_factory=time.time)

    # Phase data (populated by agents via output_key)
    client_brief: Optional[Dict[str, Any]] = None
    market_research: Optional[Dict[str, Any]] = None
    visual_direction: Optional[Dict[str, Any]] = None
    generated_logos: Optional[Dict[str, Any]] = None
    selected_logo: Optional[Dict[str, Any]] = None
    brand_system: Optional[Dict[str, Any]] = None
    final_assets: Optional[Dict[str, Any]] = None

    # File management
    uploaded_files: List[str] = Field(default_factory=list)
    generated_files: List[str] = Field(default_factory=list)
    temp_files: List[str] = Field(default_factory=list)

    # Quality control
    approval_checkpoints: Dict[str, bool] = Field(default_factory=dict)
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    revision_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Error handling
    last_error: Optional[str] = None
    retry_count: int = 0
    escalation_triggered: bool = False

    class Config:
        use_enum_values = True
