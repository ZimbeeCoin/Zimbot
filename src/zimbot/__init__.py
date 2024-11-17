# src/zimbot/__init__.py

# Expose submodules
from .api import auth, consult, health, market, subscriptions
from .assistants import client as assistant_clients
from .assistants import types as assistant_types
from .bots import assistant as bot_assistant
from .bots import bot
from .core import config, integrations, utils
from .finance import client as finance_client
from .rooms import client as room_client

# Package metadata (optional but useful)
__version__ = "0.1.0"
__all__ = [
    "api",
    "assistants",
    "bots",
    "core",
    "finance",
    "rooms",
]
