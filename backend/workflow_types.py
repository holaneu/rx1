from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

class WorkflowStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"

class WorkflowAction(str, Enum):
    WORKFLOW_FINISHED = "workflow_finished"
    WORKFLOW_FAILED = "workflow_failed"
    INTERACTION_REQUEST = "interaction_request"
    DATA_UPDATED = "data_updated"

@dataclass
class WorkflowMessage:
    title: str
    body: str

@dataclass
class WorkflowResult:
    status: WorkflowStatus
    action: WorkflowAction
    message: WorkflowMessage
    data: Optional[Any] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "action": self.action.value,
            "message": {
                "title": self.message.title,
                "body": self.message.body
            },
            "data": self.data,
            "metadata": self.metadata
        }
