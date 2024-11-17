from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class AssistantStatus(Enum):
    """Status of an assistant"""

    READY = "ready"
    DELETED = "deleted"
    FAILED = "failed"


class RunStatus(Enum):
    """Status of a run"""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    REQUIRES_ACTION = "requires_action"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class MessageRole(Enum):
    """Role of a message"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ToolType(Enum):
    """Type of tool available to an assistant"""

    CODE_INTERPRETER = "code_interpreter"
    FILE_SEARCH = "file_search"  # Updated from retrieval to file_search
    FUNCTION = "function"


class ResponseFormat(Enum):
    """Response format for the assistant"""

    TEXT = "text"
    JSON_OBJECT = "json_object"


@dataclass
class FunctionDefinition:
    """Definition of a function tool"""

    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class Tool:
    """Tool configuration for an assistant"""

    type: ToolType
    function: Optional[FunctionDefinition] = None


@dataclass
class AssistantConfiguration:
    """Configuration for creating or updating an assistant"""

    model: str = "gpt-4o"  # Default to latest GPT-4o model
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[Tool]] = None
    file_ids: Optional[List[str]] = None
    metadata: Optional[Dict[str, str]] = None
    response_format: Optional[Dict[str, str]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_completion_tokens: Optional[int] = None  # New field for token limit control


@dataclass
class MessageContent:
    """Content of a message"""

    type: str  # text, image_url, etc.
    text: Optional[Dict[str, Any]] = None
    image_url: Optional[Dict[str, Any]] = None


@dataclass
class Message:
    """Message in a thread"""

    id: str
    object: str
    created_at: int
    thread_id: str
    role: MessageRole
    content: List[MessageContent]
    assistant_id: Optional[str] = None
    run_id: Optional[str] = None
    file_ids: List[str] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class RunToolCall:
    """Tool call made during a run"""

    id: str
    type: ToolType
    function: Dict[str, Any]


@dataclass
class RequiredAction:
    """Action required to continue a run"""

    type: str
    submit_tool_outputs: Dict[str, Any]


@dataclass
class Run:
    """Execution run on a thread"""

    id: str
    object: str
    created_at: int
    thread_id: str
    assistant_id: str
    status: RunStatus
    required_action: Optional[RequiredAction] = None
    last_error: Optional[Dict[str, str]] = None
    expires_at: Optional[int] = None
    started_at: Optional[int] = None
    cancelled_at: Optional[int] = None
    failed_at: Optional[int] = None
    completed_at: Optional[int] = None
    model: str = None
    instructions: Optional[str] = None
    tools: List[Tool] = None
    file_ids: List[str] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class Thread:
    """Thread containing messages"""

    id: str
    object: str
    created_at: int
    metadata: Optional[Dict[str, str]] = None


@dataclass
class Assistant:
    """Assistant instance"""

    id: str
    object: str
    created_at: int
    name: Optional[str]
    description: Optional[str]
    model: str
    instructions: Optional[str]
    tools: List[Tool]
    file_ids: List[str]
    metadata: Optional[Dict[str, str]]
