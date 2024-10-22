import os
import sys

def print_directory_tree(root_dir, output_file, indent="", max_depth=None, current_depth=0,
                        exclude_dirs=None, exclude_files=None, comments=None):
    """
    Recursively writes the directory tree of `root_dir` to `output_file`.

    Args:
        root_dir (str): The directory path to traverse.
        output_file (file object): The file object to write the tree structure.
        indent (str): The current indentation string.
        max_depth (int, optional): Maximum depth to traverse. None for no limit.
        current_depth (int, optional): Current depth level in recursion.
        exclude_dirs (set, optional): Set of directory names to exclude from traversal.
        exclude_files (set, optional): Set of file names to exclude from the tree.
        comments (dict, optional): Dictionary mapping file/directory names to their comments.
    """
    # Check if the current depth exceeds the maximum allowed depth
    if max_depth is not None and current_depth >= max_depth:
        return

    try:
        # Retrieve and sort directory contents for consistency
        items = sorted(os.listdir(root_dir))
    except FileNotFoundError as e:
        output_file.write(f"Error: {e}\n")
        return
    except PermissionError as e:
        output_file.write(f"Permission Error: {e}\n")
        return

    for i, item in enumerate(items):
        # Skip excluded directories
        if exclude_dirs and item in exclude_dirs:
            continue

        # Skip excluded files
        if exclude_files and item in exclude_files:
            continue

        # Construct the full path of the item
        item_path = os.path.join(root_dir, item)

        # Determine the connector based on item's position
        connector = "└── " if i == len(items) - 1 else "├── "
        output_file.write(f"{indent}{connector}{item}")

        # Append comment if exists
        if comments and item in comments:
            output_file.write(f"  # {comments[item]}")

        output_file.write("\n")

        # Update indentation for child items
        next_indent = indent + ("    " if i == len(items) - 1 else "│   ")

        # Recursively process directories
        if os.path.isdir(item_path):
            print_directory_tree(
                item_path,
                output_file,
                indent=next_indent,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                exclude_dirs=exclude_dirs,
                exclude_files=exclude_files,
                comments=comments
            )

def main():
    """
    Main function to generate the directory tree and save it to a text file in the root Zimbot directory.
    """
    # Get the current working directory
    current_dir = os.getcwd()

    # Define the root Zimbot directory
    # Update this path to match your actual root Zimbot directory
    root_zimbot_dir = "/home/zimbot/ZimbeeCoin/Zimbot"  # Example path for Unix/Linux systems

    # For Windows (WSL), it might look like:
    # root_zimbot_dir = "/mnt/c/ZimbeeCoin/Zimbot"

    # Verify that the root Zimbot directory exists
    if not os.path.isdir(root_zimbot_dir):
        print(f"Error: Root Zimbot directory '{root_zimbot_dir}' does not exist.")
        sys.exit(1)

    # Define the output file path
    output_file_path = os.path.join(root_zimbot_dir, "directory_tree.txt")

    # Define the output file name to exclude it from the tree
    output_file_name = os.path.basename(output_file_path)

    # Optional: Set the maximum depth of directory traversal (None for unlimited)
    max_depth = None  # Change to an integer (e.g., 3) to limit depth

    # Define a set of directories to exclude from traversal
    exclude_dirs = {
        ".git", ".vscode", "__pycache__", "build", "dist",
        "env", "venv", "protobuf", "node_modules", "lib",
        "lib64", "third_party", "bazel", "ci", "cmake"
    }

    # Define a set of files to exclude from the tree
    exclude_files = {output_file_name, "directory_tree.txt"}

    # Define comments for specific files and directories
    comments = {
        ".env": "Environment configuration",
        ".vscode": "VSCode project settings",
        "settings.json": "VSCode specific settings",
        "dockerfile": "Docker configuration for the project",
        "LICENSE": "Licensing information",
        "README.md": "Project documentation",
        "requirements.txt": "Python dependencies",
        "bot.py": "Main bot execution logic",
        "test_imports.py": "Testing for bot imports",
        "main.py": "Main API entry point",
        "__init__.py": "Initialization files",
        "auth.py": "Handles authentication routes",
        "consult.py": "Consultation route",
        "rooms.py": "Room management routes",
        "subscriptions.py": "Handles subscriptions routes",
        "bcrypt_patch.py": "Bcrypt utility for secure password management",
        "test_livekit.py": "Tests for Livekit functionalities",
        "test_protobuf.py": "Tests for protobuf integrations",
        # Add more mappings as needed
    }

    try:
        # Open the output file in write mode
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            # Write the root of the tree (project name)
            project_name = os.path.basename(root_zimbot_dir)
            output_file.write(f"{project_name}\n")

            # Generate and write the directory tree
            print_directory_tree(
                current_dir,
                output_file,
                indent="",
                max_depth=max_depth,
                current_depth=0,
                exclude_dirs=exclude_dirs,
                exclude_files=exclude_files,
                comments=comments
            )

        print(f"Directory structure saved to: {output_file_path}")
    except Exception as e:
        print(f"Error writing to file '{output_file_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
