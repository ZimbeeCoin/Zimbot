import os
import sys

# Get the absolute path to the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the protocol directory
protocol_dir = os.path.abspath(os.path.join(current_dir, '..', 'src', 'zimbot', 'livekit', 'livekit_protocol', 'protocol'))

# Add the protocol directory to the Python module search path
if protocol_dir not in sys.path:
    sys.path.append(protocol_dir)

# Now import the compiled protobuf modules
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
