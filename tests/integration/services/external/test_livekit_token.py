# test_livekit_token.py
"""
import pytest
from zimbot.core.config.config import generate_livekit_token, settings

def test_generate_livekit_token_host():
    identity = "host_user"
    role = "host"
    token = generate_livekit_token(identity, role)
    decoded = jwt.decode(token, settings.livekit.secret_key.get_secret_value(), algorithms=["HS256"])

    assert decoded["iss"] == settings.livekit.api_key.get_secret_value()
    assert decoded["sub"] == identity
    assert decoded["room"] == settings.livekit.default_room_name
    assert decoded["permissions"] == settings.livekit.participant_roles[role]
    assert decoded["exp"] > time.time()

def test_generate_livekit_token_guest():
    identity = "guest_user"
    role = "guest"
    token = generate_livekit_token(identity, role)
    decoded = jwt.decode(token, settings.livekit.secret_key.get_secret_value(), algorithms=["HS256"])

    assert decoded["iss"] == settings.livekit.api_key.get_secret_value()
    assert decoded["sub"] == identity
    assert decoded["room"] == settings.livekit.default_room_name
    assert decoded["permissions"] == settings.livekit.participant_roles[role]
    assert decoded["exp"] > time.time()
"""
