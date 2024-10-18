# test_livekit.py

import sys
import os

# Add the protocol directory to sys.path
sys.path.append(os.path.abspath("livekit/livekit_protocol/livekit/protocol"))

try:
    from livekit.livekit_protocol.livekit.protocol.livekit_room_pb2 import RoomService, CreateRoomRequest
    from livekit.livekit_protocol.livekit.protocol.livekit_agent_dispatch_pb2 import RoomAgentDispatch
    from livekit.livekit_protocol.livekit.protocol.livekit_egress_pb2 import RoomEgress
    from livekit.livekit_protocol.livekit.protocol.livekit_models_pb2 import Room
    print("LiveKit SDK imports successful!")
except ImportError as e:
    print(f"ImportError: {e}")
