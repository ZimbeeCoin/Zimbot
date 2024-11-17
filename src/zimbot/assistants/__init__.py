"""
Assistants package with types and clients for managing assistant interactions.

This module imports all relevant types and clients to provide a centralized
interface for assistant management.

Usage:
    from zimbot.assistants import (
        AssistantClient as AssistantManagerClient,
        Assistant,
        FileObject,
        Message,
        Run,
        Thread,
    )
"""

# Import AssistantClient from client.assistant_manager_client
from zimbot.assistants.client.assistant_manager_client import AssistantClient

# Import data types from types
from zimbot.assistants.types import Assistant, FileObject, Message, Run, Thread

__all__ = [
    "AssistantClient",
    "Assistant",
    "FileObject",
    "Message",
    "Run",
    "Thread",
]
