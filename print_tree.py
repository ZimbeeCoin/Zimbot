import os

def print_directory_tree(root_dir, output_file, indent=""):
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
            print_directory_tree(item_path, output_file, next_indent)

# Specify the root directory of your project in Windows-style path
project_directory = r"C:\ZimbeeCoin\Zimbot"  # Adjust to your correct path if needed

# Create the output file in the root directory
output_file_path = os.path.join(project_directory, "directory_tree.txt")

# Open the file in write mode
with open(output_file_path, "w", encoding="utf-8") as output_file:
    # Call the function to write the directory tree into the file
    print_directory_tree(project_directory, output_file)

print(f"Directory structure saved to: {output_file_path}")
