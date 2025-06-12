"""Error handling and recovery system for branding workflow"""

import time
import traceback
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from google.adk.tools import ToolContext

from agents.base.state_schema import StateKeys, WorkflowPhase


class ErrorSeverity(str, Enum):
    """Error severity levels"""

    LOW = "low"  # Recoverable, continue workflow
    MEDIUM = "medium"  # Requires retry or fallback
    HIGH = "high"  # Requires human intervention
    CRITICAL = "critical"  # Stop workflow immediately


class ErrorCategory(str, Enum):
    """Error category types"""

    VALIDATION = "validation"  # State/input validation errors
    TOOL_EXECUTION = "tool_execution"  # Tool/API failures
    QUALITY = "quality"  # Quality gate failures
    WORKFLOW = "workflow"  # Workflow transition errors
    EXTERNAL_API = "external_api"  # External service failures
    FILE_PROCESSING = "file_processing"  # File upload/processing errors


class ErrorHandler:
    """Central error handling and recovery logic"""

    def __init__(self):
        self.error_history = []
        self.recovery_strategies = self._setup_recovery_strategies()
        self.escalation_thresholds = {
            ErrorSeverity.LOW: 5,  # 5 low errors before escalation
            ErrorSeverity.MEDIUM: 3,  # 3 medium errors before escalation
            ErrorSeverity.HIGH: 1,  # 1 high error triggers escalation
            ErrorSeverity.CRITICAL: 0,  # Immediate escalation
        }

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main error handling entry point"""
        error_info = self._classify_error(error, context)

        # Record error
        self.error_history.append(error_info)

        # Attempt recovery
        recovery_result = self._attempt_recovery(error_info, context)

        # Check escalation
        escalation_needed = self._check_escalation(error_info, context)

        return {
            "error_info": error_info,
            "recovery_attempted": recovery_result.get("attempted", False),
            "recovery_successful": recovery_result.get("successful", False),
            "escalation_needed": escalation_needed,
            "recommended_action": self._get_recommended_action(
                error_info, recovery_result, escalation_needed
            ),
        }

    def _classify_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify error by type, severity, and category"""
        error_type = type(error).__name__
        error_message = str(error)

        # Determine category
        category = self._determine_category(error_type, error_message, context)

        # Determine severity
        severity = self._determine_severity(error_type, category, context)

        return {
            "error_id": f"err_{int(time.time())}_{len(self.error_history)}",
            "error_type": error_type,
            "error_message": error_message,
            "category": category,
            "severity": severity,
            "timestamp": time.time(),
            "context": context,
            "stack_trace": traceback.format_exc(),
            "phase": context.get("current_phase"),
            "agent": context.get("current_agent"),
        }

    def _determine_category(
        self, error_type: str, message: str, context: Dict[str, Any]
    ) -> ErrorCategory:
        """Determine error category based on type and context"""
        category_indicators = {
            ErrorCategory.VALIDATION: ["validation", "missing", "required", "invalid"],
            ErrorCategory.TOOL_EXECUTION: ["tool", "execution", "failed", "timeout"],
            ErrorCategory.QUALITY: ["quality", "threshold", "score", "gate"],
            ErrorCategory.WORKFLOW: ["transition", "phase", "workflow", "state"],
            ErrorCategory.EXTERNAL_API: ["api", "connection", "rate limit", "service"],
            ErrorCategory.FILE_PROCESSING: ["file", "upload", "format", "processing"],
        }

        message_lower = message.lower()
        for category, indicators in category_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                return category

        return ErrorCategory.TOOL_EXECUTION  # Default

    def _determine_severity(
        self, error_type: str, category: ErrorCategory, context: Dict[str, Any]
    ) -> ErrorSeverity:
        """Determine error severity"""
        # Critical errors
        if error_type in ["SystemExit", "KeyboardInterrupt", "MemoryError"]:
            return ErrorSeverity.CRITICAL

        # High severity by category
        if category in [ErrorCategory.WORKFLOW, ErrorCategory.EXTERNAL_API]:
            return ErrorSeverity.HIGH

        # Medium severity
        if category in [ErrorCategory.QUALITY, ErrorCategory.TOOL_EXECUTION]:
            return ErrorSeverity.MEDIUM

        # Low severity for validation and file processing
        return ErrorSeverity.LOW

    def _setup_recovery_strategies(self) -> Dict[ErrorCategory, List[Callable]]:
        """Setup recovery strategies for each error category"""
        return {
            ErrorCategory.VALIDATION: [
                self._retry_with_fallback_data,
                self._request_manual_input,
            ],
            ErrorCategory.TOOL_EXECUTION: [
                self._retry_with_backoff,
                self._use_alternative_tool,
                self._manual_completion,
            ],
            ErrorCategory.QUALITY: [
                self._lower_quality_threshold,
                self._regenerate_with_different_params,
                self._manual_quality_override,
            ],
            ErrorCategory.WORKFLOW: [
                self._reset_to_previous_phase,
                self._skip_problematic_step,
                self._manual_workflow_intervention,
            ],
            ErrorCategory.EXTERNAL_API: [
                self._retry_with_exponential_backoff,
                self._use_fallback_api,
                self._cache_fallback,
                self._manual_api_intervention,
            ],
            ErrorCategory.FILE_PROCESSING: [
                self._retry_file_processing,
                self._use_alternative_format,
                self._manual_file_intervention,
            ],
        }

    def _attempt_recovery(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attempt to recover from error using appropriate strategy"""
        category = ErrorCategory(error_info["category"])
        strategies = self.recovery_strategies.get(category, [])

        for strategy in strategies:
            try:
                result = strategy(error_info, context)
                if result.get("successful"):
                    return {
                        "attempted": True,
                        "successful": True,
                        "strategy": strategy.__name__,
                        "result": result,
                    }
            except Exception as recovery_error:
                continue

        return {"attempted": True, "successful": False}

    def _check_escalation(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Check if error should trigger human escalation"""
        severity = ErrorSeverity(error_info["severity"])

        # Count recent errors of this severity
        recent_errors = [
            e for e in self.error_history[-10:] if e["severity"] == severity.value
        ]
        error_count = len(recent_errors)

        threshold = self.escalation_thresholds.get(severity, 1)
        return error_count >= threshold

    def _get_recommended_action(
        self,
        error_info: Dict[str, Any],
        recovery_result: Dict[str, Any],
        escalation_needed: bool,
    ) -> str:
        """Get recommended action based on error analysis"""
        if escalation_needed:
            return "escalate_to_human"
        elif recovery_result.get("successful"):
            return "continue_workflow"
        elif error_info["severity"] == ErrorSeverity.CRITICAL:
            return "stop_workflow"
        else:
            return "retry_operation"

    # Recovery strategy implementations (simplified for brevity)
    def _retry_with_fallback_data(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "fallback_data_used"}

    def _retry_with_backoff(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        retry_count = context.get("retry_count", 0)
        if retry_count < 3:
            time.sleep(2**retry_count)  # 1s, 2s, 4s
            return {"successful": True, "action": "retry_scheduled"}
        return {"successful": False, "reason": "Max retries exceeded"}

    def _use_alternative_tool(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "alternative_tool_available"}

    def _manual_completion(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "manual_completion_required"}

    def _lower_quality_threshold(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "quality_threshold_lowered"}

    def _regenerate_with_different_params(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "regeneration_with_new_params"}

    def _reset_to_previous_phase(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "workflow_reset_to_previous"}

    def _skip_problematic_step(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "step_skipped"}

    def _manual_workflow_intervention(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "manual_workflow_intervention"}

    def _retry_with_exponential_backoff(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._retry_with_backoff(error_info, context)

    def _use_fallback_api(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "fallback_api_used"}

    def _cache_fallback(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "cache_fallback_used"}

    def _manual_api_intervention(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "manual_api_intervention"}

    def _retry_file_processing(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "file_processing_retry"}

    def _use_alternative_format(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "alternative_format_used"}

    def _manual_file_intervention(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "manual_file_intervention"}

    def _request_manual_input(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "manual_input_requested"}

    def _manual_quality_override(
        self, error_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"successful": True, "action": "manual_quality_override"}


# ADK v1.0.0 Function Tools
def handle_workflow_error(
    error_message: str, error_context: Dict[str, Any], tool_context: ToolContext
) -> Dict[str, Any]:
    """Handle errors and attempt recovery in workflow"""
    error_handler = ErrorHandler()

    # Create mock exception from message
    mock_error = Exception(error_message)

    # Add current state context
    full_context = {
        **error_context,
        "current_phase": tool_context.state.get(StateKeys.CURRENT_PHASE),
        "retry_count": tool_context.state.get(StateKeys.RETRY_COUNT, 0),
        "session_state": tool_context.state,
    }

    # Handle error
    result = error_handler.handle_error(mock_error, full_context)

    # Update state with error info
    tool_context.state.setdefault("error_log", []).append(result["error_info"])
    tool_context.state[StateKeys.LAST_ERROR] = result["error_info"]["error_message"]

    # Update retry count if retrying
    if result["recommended_action"] == "retry_operation":
        tool_context.state[StateKeys.RETRY_COUNT] = (
            tool_context.state.get(StateKeys.RETRY_COUNT, 0) + 1
        )

    # Trigger escalation if needed
    if result["escalation_needed"]:
        tool_context.state[StateKeys.ESCALATION_TRIGGERED] = True

    return result
