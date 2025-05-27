from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"

class ResponseAction(str, Enum):
    WORKFLOW_FINISHED = "workflow_finished"
    WORKFLOW_FAILED = "workflow_failed"
    INTERACTION_REQUEST = "interaction_request"
    DATA_UPDATED = "data_updated"
    STATUS_MESSAGE = "status_message"

@dataclass
class ResponseMessage:
    title: str
    body: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "body": self.body
        }

@dataclass
class ResponseResult:
    status: ResponseStatus
    action: ResponseAction
    message: ResponseMessage
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
