#from dataclasses import dataclass
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

class ResponseKey(str, Enum):
    STATUS = "status"
    TASK_ID = "task_id"
    TIMESTAMP = "timestamp"
    MESSAGE = "message"
    ACTION = "action"
    DATA = "data"
    ERROR = "error"
    TITLE = "title"
    BODY = "body"
    CATEGORY = "category"
    COLLECTED_MESSAGES = "collected_messages" # REMOVE
    FUNC_LOG = "func_log" 
    FORM_ELEMENTS = "form_elements"



# Helper functions to format responses - these can be used in workflows or other parts of the application
# Remove if not needed in the final implementation
def response_output(response: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to format the response output."""
    payload = {
        **response,
        ResponseKey.TIMESTAMP: response.get(ResponseKey.TIMESTAMP, datetime.now().timestamp())        
    }
    return payload

def response_output_error(response: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to format the error response output."""
    payload = {
        **response,
        ResponseKey.STATUS: ResponseStatus.ERROR,
        ResponseKey.TIMESTAMP: response.get(ResponseKey.TIMESTAMP, datetime.now().timestamp()),
        ResponseKey.ERROR: response.get(ResponseKey.ERROR, "An error occurred.")
    }
    if response.get(ResponseKey.MESSAGE) is None:
        payload[ResponseKey.MESSAGE] = {
            ResponseKey.TITLE: "Error",
            ResponseKey.BODY: response.get(ResponseKey.ERROR, "An error occurred.")
        }
    return payload

def response_output_success(response: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to format the success response output."""
    payload = {
        **response,
        ResponseKey.STATUS: ResponseStatus.SUCCESS,
        ResponseKey.TIMESTAMP: response.get(ResponseKey.TIMESTAMP, datetime.now().timestamp())
    }
    if response.get(ResponseKey.MESSAGE) is None:
        payload[ResponseKey.MESSAGE] = {
            ResponseKey.TITLE: "Success",
            ResponseKey.BODY: response.get(ResponseKey.DATA, "Operation done.")
        }
    return payload

def response_output_interaction_request(response: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to format the interaction request response output."""
    payload = {
        **response,
        ResponseKey.STATUS: ResponseStatus.PENDING,
        ResponseKey.TIMESTAMP: response.get(ResponseKey.TIMESTAMP, datetime.now().timestamp()),
        ResponseKey.ACTION: ResponseAction.INTERACTION_REQUEST
    }
    if response.get(ResponseKey.MESSAGE) is None:
        payload[ResponseKey.MESSAGE] = {
            ResponseKey.TITLE: "User Input Required",
            ResponseKey.BODY: "Please provide input."
        }
    return payload

