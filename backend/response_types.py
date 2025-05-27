from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime

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
    data: Optional[Any] = None
    timestamp: float = datetime.now().timestamp()
    error: Optional[str] = None
    action: Optional[ResponseAction] = None
    message: Optional[ResponseMessage] = None

    def to_dict(self) -> dict:
        result = {
            "status": self.status.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "error": self.error
        }
        
        if self.action:
            result["action"] = self.action.value
            
        if self.message:
            result["message"] = self.message.to_dict()
            
        return result

def success_response(
    data: Any = None, 
    message: Optional[ResponseMessage] = None,
    action: Optional[ResponseAction] = None,
    **additional_fields: Any
) -> Dict:
    response = ResponseResult(
        status=ResponseStatus.SUCCESS,
        data=data,
        message=message,
        action=action
    ).to_dict()
    
    response.update(additional_fields)
    return response
    
def error_response(
    error: str,
    message: Optional[ResponseMessage] = None,
    action: Optional[ResponseAction] = ResponseAction.WORKFLOW_FAILED,
    **additional_fields: Any
) -> Dict:
    response = ResponseResult(
        status=ResponseStatus.ERROR,
        error=error,
        message=message or ResponseMessage(
            title="Error Occurred",
            body=error
        ),
        action=action
    ).to_dict()
    
    response.update(additional_fields)
    return response

def interaction_request(
    prompt: str,
    title: str = "User Input Required",
    **additional_fields: Any
) -> Dict:
    response = ResponseResult(
        status=ResponseStatus.PENDING,
        action=ResponseAction.INTERACTION_REQUEST,
        message=ResponseMessage(
            title=title,
            body=prompt
        )
    ).to_dict()
    
    response.update(additional_fields)
    return response
