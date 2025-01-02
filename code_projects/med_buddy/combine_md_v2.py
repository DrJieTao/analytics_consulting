import os
import sys
import shutil

def combine_markdown_content(folder_path):
    """
    Combines content from markdown files within a folder, organizing it by headings.
    It also moves the processed markdown files to an 'archived' subfolder.

    Args:
        folder_path (str): The path to the folder containing markdown files.

    Returns:
        dict: A dictionary where keys are headings (extracted from lines starting and ending with **)
              and values are lists of content lines under each heading.
              Returns an empty dictionary if no markdown files are found.
    """
    combined_content = {} # Initialize an empty dictionary to store combined content
    found_md_files = False # Flag to check if any markdown files were found
    # Create the 'archived' subfolder if it doesn't exist
    archive_path = os.path.join(folder_path, "archived")
    os.makedirs(archive_path, exist_ok=True) # Create the directory, no error if it exists

    for filename in os.listdir(folder_path): # Iterate through each file in the folder
        if filename.endswith(".md"): # Check if the file is a markdown file
            found_md_files = True # Set the flag to True since a markdown file was found
            filepath = os.path.join(folder_path, filename) # Create the full file path
            # print(f"Processing file: {filepath}") # Print which file is being processed
            with open(filepath, 'r', encoding='utf-8') as f: # Open the file for reading
                current_heading = None # Initialize the current heading to None
                for line in f: # Iterate through each line in the file
                    line = line.strip() # Remove leading/trailing whitespace
                    if line.startswith("**") and line.endswith("**"): # Check if the line is a heading
                        current_heading = line.strip("*").strip() # Extract the heading text
                        # print(f"  Found heading: {current_heading}") # Print the heading found
                        if current_heading not in combined_content: # Check if the heading is already in the dictionary
                            combined_content[current_heading] = [] # If not, create a new list for the heading
                    elif current_heading: # If a heading has been found
                        combined_content[current_heading].append(line) # Append the line to the current heading's list
            # Move the processed file to the 'archived' folder
            shutil.move(filepath, os.path.join(archive_path, filename))
            # print(f"Moved '{filename}' to '{archive_path}'") # Print that the file was moved
    
    if not found_md_files: # If no markdown files were found
        print(f"No .md files found in: {folder_path}") # Print a message
    return combined_content # Return the dictionary containing the combined content

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
            print(f"## {heading}")  # Still using ## for output formatting
            for line in content_lines:
                print(line)
            print()