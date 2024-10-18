import os
from grpc_tools import protoc

# Get the absolute path to the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the directories
PROJECT_PROTO_DIR = current_dir  # Assuming the script is in the proto_files directory
GOOGLE_PROTOBUF_INCLUDE = '/usr/local/include'  # Path where protoc includes are stored
OUTPUT_DIR = os.path.abspath(os.path.join(current_dir, '..', 'protocol'))

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List of .proto files to compile
proto_files = [f for f in os.listdir(PROJECT_PROTO_DIR) if f.endswith('.proto')]

# Compile each .proto file
for proto in proto_files:
    command = [
        '',
        f'-I{PROJECT_PROTO_DIR}',
        f'-I{GOOGLE_PROTOBUF_INCLUDE}',
        f'--python_out={OUTPUT_DIR}',
        f'--grpc_python_out={OUTPUT_DIR}',
        proto
    ]
    print(f"Compiling {proto}...")
    result = protoc.main(command)
    if result != 0:
        print(f"Error: {proto} failed to compile.")
    else:
        print(f"Successfully compiled {proto}.")
