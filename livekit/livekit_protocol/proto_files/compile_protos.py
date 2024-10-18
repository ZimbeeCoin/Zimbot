import os
from grpc_tools import protoc

# Get the absolute path to the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the directories using Unix-style paths
PROJECT_PROTO_DIR = current_dir  # Assuming this script is in the proto_files directory
GOOGLE_PROTOBUF_INCLUDE = '/usr/local/include'  # Standard Protobuf include path in Linux
OUTPUT_DIR = os.path.abspath(os.path.join(current_dir, '..', 'protocol'))  # Output directory

# Debugging: Print paths to verify correctness
print(f"Project Proto Directory: {PROJECT_PROTO_DIR}")
print(f"Google Protobuf Include: {GOOGLE_PROTOBUF_INCLUDE}")
print(f"Output Directory: {OUTPUT_DIR}")

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List of .proto files to compile
proto_files = [
    "cloud_replay.proto",
    "livekit_agent_dispatch.proto",
    "livekit_agent.proto",
    "livekit_analytics.proto",
    "livekit_egress.proto",
    "livekit_ingress.proto",
    "livekit_internal.proto",
    "livekit_metrics.proto",
    "livekit_models.proto",
    "livekit_room.proto",
    "livekit_rtc.proto",
    "livekit_sip.proto",
    "livekit_webhook.proto"
]

# Change working directory to PROJECT_PROTO_DIR
os.chdir(PROJECT_PROTO_DIR)

# Compile each .proto file
for proto in proto_files:
    if not os.path.isfile(proto):
        print(f"Proto file {proto} not found in {PROJECT_PROTO_DIR}. Skipping.")
        continue

    # Command for compiling the proto files
    # protoc.main expects a list similar to sys.argv, where the first element is the program name
    command = [
        '',  # Placeholder for sys.argv[0], which is the program name
        f'-I{PROJECT_PROTO_DIR}',        # Include path for your project's proto files
        f'-I{GOOGLE_PROTOBUF_INCLUDE}',  # Include path for standard Google Protobuf files
        f'--python_out={OUTPUT_DIR}',     # Output directory for Python files
        f'--grpc_python_out={OUTPUT_DIR}',# Output directory for gRPC Python files
        proto                             # The .proto file to compile
    ]

    print(f"Compiling {proto}...")
    result = protoc.main(command)
    if result != 0:
        print(f"Error: {proto} failed to compile.")
    else:
        print(f"Successfully compiled {proto}.")

print("All .proto files have been processed.")
