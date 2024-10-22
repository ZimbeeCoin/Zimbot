# replace_jose_with_pyjwt.py

import os
import re

def replace_imports(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Replace import statements
    content_new = re.sub(r'from\s+jose\s+import\s+([^ ]+)', r'from jwt import \1', content)
    content_new = re.sub(r'import\s+jose', 'import jwt', content_new)

    # Replace 'jose.' with 'jwt.'
    content_new = content_new.replace('jose.', 'jwt.')

    # Replace JWTError with PyJWT's exceptions
    content_new = content_new.replace('JWTError', 'PyJWTError')

    # Replace 'jose.JWTError' with 'jwt.PyJWTError' if present
    content_new = re.sub(r'jose\.JWTError', 'jwt.PyJWTError', content_new)

    if content != content_new:
        with open(file_path, 'w') as file:
            file.write(content_new)
        print(f"Updated imports in {file_path}")

def find_python_files(directory):
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment directory
        if 'zimbot' in dirs:
            dirs.remove('zimbot')
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    project_dir = '.'  # Current directory
    python_files = find_python_files(project_dir)
    for file_path in python_files:
        replace_imports(file_path)

if __name__ == "__main__":
    main()
