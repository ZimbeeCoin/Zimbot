import os
from grpc_tools import protoc

# Define the directories
PROJECT_PROTO_DIR = os.path.abspath("C:/ZimbeeCoin/Zimbot/livekit/livekit_protocol/proto_files")  # Project proto files
GOOGLE_PROTO_PATH = os.path.abspath("C:/ZimbeeCoin/Zimbot/protoc/include")  # Path to google/protobuf files
OUTPUT_DIR = os.path.abspath("C:/ZimbeeCoin/Zimbot/livekit/livekit_protocol/protocol")  # Output directory for generated files

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List of .proto files to compile from the project's proto files
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

# Compile each .proto file
for proto in proto_files:
    proto_path = os.path.join(PROJECT_PROTO_DIR, proto)
    if not os.path.isfile(proto_path):
        print(f"Proto file {proto} not found in {PROJECT_PROTO_DIR}. Skipping.")
        continue

    # Command for compiling the proto files
    command = [
        'grpc_tools.protoc',
        f'--proto_path={PROJECT_PROTO_DIR}',  # Path to your project's proto files
        f'--proto_path={GOOGLE_PROTO_PATH}',  # Path to google/protobuf files
        f'--python_out={OUTPUT_DIR}',  # Output directory for Python files
        f'--grpc_python_out={OUTPUT_DIR}',  # Output directory for gRPC Python files
        proto_path,
    ]

    if protoc.main(command) != 0:
        print(f"Error: {proto} failed to compile.")
    else:
        print(f"Successfully compiled {proto}.")

print("All .proto files have been processed.")
