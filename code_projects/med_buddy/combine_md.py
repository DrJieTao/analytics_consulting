import os
import sys

def combine_markdown_content(folder_path):
    combined_content = {}
    found_md_files = False
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            found_md_files = True
            filepath = os.path.join(folder_path, filename)
            # print(f"Processing file: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                current_heading = None
                for line in f:
                    line = line.strip()
                    if line.startswith("**") and line.endswith("**"):
                        current_heading = line.strip("*").strip()
                        # print(f"  Found heading: {current_heading}")
                        if current_heading not in combined_content:
                            combined_content[current_heading] = []
                    elif current_heading:
                        combined_content[current_heading].append(line)
    if not found_md_files:
        print(f"No .md files found in: {folder_path}")
    return combined_content

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        sys.exit(1)

    combined_data = combine_markdown_content(folder_path)

    if not combined_data:
        print("No content found under any headings.")
    else:
        for heading, content_lines in combined_data.items():
            print(f"## {heading}") # Still using ## for output formatting
            for line in content_lines:
                print(line)
            print()