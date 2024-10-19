from livekit import LiveKitClient, RoomOptions, Room
import os
import logging

LIVEKIT_URL = os.getenv('LIVEKIT_WEBSOCKET_URL')
LIVEKIT_API_KEY = os.getenv('LIVEKIT_API_KEY')
LIVEKIT_API_SECRET = os.getenv('LIVEKIT_API_SECRET')

try:
    client = LiveKitClient(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    logging.info("LiveKit client initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize LiveKit client: {e}")
    client = None

def create_livekit_room(room_name: str) -> Room:
    if not client:
        logging.error("LiveKit client is not initialized.")
        return None
    try:
        room = client.create_room(
            room_name,
            RoomOptions(
                empty_timeout=300,  # seconds before room is deleted if empty
                max_participants=10
            )
        )
        logging.info(f"LiveKit room '{room_name}' created successfully.")
        return room
    except Exception as e:
        logging.error(f"Error creating LiveKit room '{room_name}': {e}")
        return None

def generate_livekit_token(room_name: str, identity: str) -> str:
    if not client:
        logging.error("LiveKit client is not initialized.")
        return ""
    try:
        token = client.generate_token(room_name, identity, join=True)
        logging.info(f"Generated token for user '{identity}' in room '{room_name}'.")
        return token
    except Exception as e:
        logging.error(f"Error generating LiveKit token for user '{identity}': {e}")
        return ""
