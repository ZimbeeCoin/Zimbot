# src/core/integrations/openai/types.py

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class AssistantRole(str, Enum):
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


class AssistantStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    REQUIRES_ACTION = "requires_action"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ToolType(str, Enum):
    CODE_INTERPRETER = "code_interpreter"
    RETRIEVAL = "retrieval"
    FUNCTION = "function"


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI API access"""

    api_key: str = Field(..., env="OPENAI_API_KEY")
    organization_id: Optional[str] = Field(None, env="OPENAI_ORG_ID")
    api_base_url: str = "https://api.openai.com/v1"
    max_retries: int = 3
    timeout: int = 60
    default_model: str = "gpt-4o"

    class Config:
        env_file = ".env"


class MessageContent(BaseModel):
    """Content of a message in a thread"""

    type: str  # Consider using Literal["text", "image", "file"] for stricter validation
    text: Optional[str] = None
    image_url: Optional[str] = None
    file_id: Optional[str] = None

    @validator("type")
    def validate_type(cls, v):
        if v not in {"text", "image", "file"}:
            raise ValueError('type must be one of "text", "image", "file"')
        return v


class Message(BaseModel):
    """A message in a thread"""

    id: str
    role: AssistantRole
    content: List[MessageContent]
    file_ids: List[str] = []
    assistant_id: Optional[str] = None
    thread_id: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class Thread(BaseModel):
    """A conversation thread"""

    id: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class Tool(BaseModel):
    """A tool available to an assistant"""

    type: ToolType
    function: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class Assistant(BaseModel):
    """An OpenAI assistant"""

    id: str
    name: str
    model: str
    instructions: Optional[str] = None
    tools: List[Tool] = []
    file_ids: List[str] = []
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class RunStep(BaseModel):
    """A step in an assistant's run"""

    id: str
    type: str
    status: AssistantStatus
    step_details: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class Run(BaseModel):
    """An execution run of an assistant"""

    id: str
    assistant_id: str
    thread_id: str
    status: AssistantStatus
    started_at: datetime
    model: str
    instructions: Optional[str] = None
    tools: List[Tool] = []
    file_ids: List[str] = []
    completed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    steps: List[RunStep] = Field(default_factory=list)


class Usage(BaseModel):
    """API usage information"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class StreamEvent(BaseModel):
    """Represents a streaming event from the API"""

    type: str
    data: Dict[str, Any]
    id: Optional[str] = None
    created_at: Optional[datetime] = None


class TokenUsage(BaseModel):
    """Detailed token usage information"""

    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    cached_tokens: Optional[int] = None


class OpenAIError(Exception):
    """Base exception for OpenAI related errors"""

    pass


class RateLimitError(OpenAIError):
    """Raised when API rate limit is exceeded"""

    pass


class AuthenticationError(OpenAIError):
    """Raised when authentication fails"""

    pass


class APIError(OpenAIError):
    """Raised when API returns an error"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
