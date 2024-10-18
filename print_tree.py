import os

def print_directory_tree(root_dir, output_file, indent="", max_depth=None, current_depth=0):
    # Check if we have reached the max depth
    if max_depth is not None and current_depth >= max_depth:
        return
    
    try:
        # List directories and files in the current directory
        items = os.listdir(root_dir)
    except FileNotFoundError as e:
        output_file.write(f"Error: {e}\n")
        return
    
    for i, item in enumerate(items):
        # Construct the full path of the item
        item_path = os.path.join(root_dir, item)
        
        # Write the item to the output file with appropriate indent
        if i == len(items) - 1:  # Last item in the directory
            output_file.write(f"{indent}└── {item}\n")
            next_indent = indent + "    "
        else:
            output_file.write(f"{indent}├── {item}\n")
            next_indent = indent + "│   "
        
        # If the item is a directory, recursively write its contents
        if os.path.isdir(item_path):
            print_directory_tree(item_path, output_file, next_indent, max_depth, current_depth + 1)

# Specify the root directory in Unix-style path for WSL
project_directory = "/mnt/c/ZimbeeCoin/Zimbot"  # Adjust to your correct path if needed

# Create the output file in the root directory
output_file_path = os.path.join(project_directory, "directory_tree.txt")

# Ensure the directory for the output file exists
if not os.path.exists(project_directory):
    os.makedirs(project_directory)

# Set the maximum depth (None for no limit)
max_depth = 3  # Adjust this value as needed

# Open the file in write mode
with open(output_file_path, "w", encoding="utf-8") as output_file:
    # Call the function to write the directory tree into the file
    print_directory_tree(project_directory, output_file, max_depth=max_depth)

print(f"Directory structure saved to: {output_file_path}")
