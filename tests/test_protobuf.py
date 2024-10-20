#!/usr/bin/env python3
import os
import sys

def setup_protocol_path():
    """
    Adds the protocol directory to the Python module search path.
    """
    # Get the absolute path to the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")

    # Construct the path to the protocol directory
    protocol_dir = os.path.abspath(os.path.join(current_dir, '..', 'src', 'zimbot', 'livekit', 'livekit_protocol', 'protocol'))
    print(f"Protocol directory: {protocol_dir}")

    # Add the protocol directory to the Python module search path if not already present
    if protocol_dir not in sys.path:
        sys.path.append(protocol_dir)
        print(f"Added {protocol_dir} to sys.path")
    else:
        print(f"{protocol_dir} is already in sys.path")
    
    return protocol_dir

def import_protobuf_modules():
    """
    Imports the compiled protobuf modules.
    """
    try:
        import livekit_agent_pb2
        import livekit_models_pb2
        print("Successfully imported protobuf modules.")
        return livekit_agent_pb2, livekit_models_pb2
    except ImportError as e:
        print(f"Error importing protobuf modules: {e}")
        sys.exit(1)

def test_job_message(livekit_agent_pb2, livekit_models_pb2):
    """
    Tests the serialization and deserialization of a Job message.
    """
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
    print("Serialized Job message.")

    # Deserialize the binary string back into a Job message
    parsed_message = livekit_agent_pb2.Job()
    parsed_message.ParseFromString(serialized_message)
    print("Deserialized Job message.")

    # Print out the original and parsed messages
    print("Original Job message:")
    print(job_message)
    print("\nParsed Job message from serialized data:")
    print(parsed_message)

if __name__ == "__main__":
    setup_protocol_path()
    livekit_agent_pb2, livekit_models_pb2 = import_protobuf_modules()
    test_job_message(livekit_agent_pb2, livekit_models_pb2)
