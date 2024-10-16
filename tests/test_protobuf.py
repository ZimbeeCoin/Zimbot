import sys
import os

# Add the protocol directory to sys.path to enable imports
sys.path.append(os.path.abspath('../livekit/livekit_protocol/protocol'))

import livekit_agent_pb2

# Create a simple message and serialize it
message = livekit_agent_pb2.AgentMessage(id="12345")
serialized = message.SerializeToString()

# Deserialize
message_parsed = livekit_agent_pb2.AgentMessage()
message_parsed.ParseFromString(serialized)

print(message_parsed)
