import sys
import os

# Add the correct protocol directory to sys.path
sys.path.append(os.path.abspath("src/zimbot/livekit/livekit_protocol/protocol"))

try:
    from livekit_room_pb2 import RoomService, CreateRoomRequest
    from livekit_agent_dispatch_pb2 import RoomAgentDispatch
    from livekit_egress_pb2 import RoomEgress
    from livekit_models_pb2 import Room
    print("LiveKit SDK imports successful!")
except ImportError as e:
    print(f"ImportError: {e}")
