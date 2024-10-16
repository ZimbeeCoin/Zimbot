import os
import sys

# Add the path to livekit_protocol/protocol to the Python module search path
sys.path.append(os.path.abspath("C:/ZimbeeCoin/Zimbot/livekit/livekit_protocol/protocol"))

# Import the necessary protobuf modules
import livekit_agent_pb2
import livekit_models_pb2  # Import for the Room message

def test_job_message():
    # Create a Job message with some example data
    job_message = livekit_agent_pb2.Job(
        id="12345",
        dispatch_id="dispatch123",
        type=livekit_agent_pb2.JT_ROOM,  # Use JobType enum
        room=livekit_models_pb2.Room(name="TestRoom"),  # Use Room from livekit_models_pb2
        participant=livekit_models_pb2.ParticipantInfo(identity="user123", name="John Doe")  # Also from livekit_models_pb2
    )

    # Serialize the Job message to a binary string
    serialized_message = job_message.SerializeToString()

    # Deserialize the binary string back into a Job message
    parsed_message = livekit_agent_pb2.Job()
    parsed_message.ParseFromString(serialized_message)

    # Print out the original and parsed messages
    print("Original Job message:")
    print(job_message)
    print("\nParsed Job message from serialized data:")
    print(parsed_message)

if __name__ == "__main__":
    test_job_message()
