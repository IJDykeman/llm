#!/usr/bin/env python3

import re
import os
import sys
import subprocess

def get_git_root(path):
    print ("path ", path)
    try:
        git_root = subprocess.check_output(["git", "-C", path, "rev-parse", "--show-toplevel"])
        return git_root.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        raise Exception("Not a git repository")

def process_includes(content, git_root):
    include_pattern = re.compile(r'{include\s+(.+?)}')

    def replace_include(match):
        file_path = match.group(1)
        print("processing include ", file_path)
        if not os.path.isabs(file_path):
            file_path = os.path.join(git_root, file_path)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                file_content = f.read()
            return process_includes(file_content, git_root)
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

    return include_pattern.sub(replace_include, content)

def include_files(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    git_root = get_git_root(os.path.dirname(os.path.abspath(input_file)))
    print("git root ", git_root)
    content = process_includes(content, git_root)

    with open(output_file, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py input.md [output.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print("Input file does not exist")
        sys.exit(1)
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.md"

    include_files(input_file, output_file)
