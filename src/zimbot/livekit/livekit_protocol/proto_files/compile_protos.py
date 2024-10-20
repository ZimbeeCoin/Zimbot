import os
from grpc_tools import protoc

def compile_protos():
    # Get the absolute path to the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the directories
    PROJECT_PROTO_DIR = current_dir
    OUTPUT_DIR = os.path.abspath(os.path.join(current_dir, '..', 'protocol'))

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # List of .proto files to compile
    proto_files = [f for f in os.listdir(PROJECT_PROTO_DIR) if f.endswith('.proto')]

    # Compile each .proto file
    for proto in proto_files:
        proto_file_path = os.path.join(PROJECT_PROTO_DIR, proto)

        command = [
            'protoc',
            f'-I{PROJECT_PROTO_DIR}',  # Include the proto files directory
            f'--python_out={OUTPUT_DIR}',  # Python protobuf files output
            f'--grpc_python_out={OUTPUT_DIR}',  # gRPC Python files output
            proto_file_path
        ]

        print(f"Compiling {proto}...")
        result = protoc.main(command)

        if result != 0:
            print(f"Error: {proto} failed to compile.")
        else:
            print(f"Successfully compiled {proto}.")

if __name__ == "__main__":
    compile_protos()
