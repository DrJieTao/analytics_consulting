import json
import sys

def json_to_markdown(json_string: str) -> str:
    """Converts a JSON string into a Markdown representation.

    This function recursively parses the JSON structure and formats it into a
    human-readable Markdown string. It handles dictionaries, lists, and primitive
    JSON types (strings, numbers, booleans, null).

    Args:
        json_string (str): The JSON string to convert.

    Returns:
        str: The Markdown representation of the JSON data.

    Raises:
        ValueError: If the input string is not valid JSON.

    Examples:
        >>> json_to_markdown('{"name": "Alice", "age": 30}')
        '- **name**: Alice\\n- **age**: 30'
        >>> json_to_markdown('[1, 2, 3]')
        '- 1\\n- 2\\n- 3'
        >>> json_to_markdown('{"items": [ {"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"} ]}')
        '- **items**:\\n  - **id**: 1\\n  - **name**: Item 1\\n  - **id**: 2\\n  - **name**: Item 2'
    """
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string")
    
    def _convert(obj, indent_level=0):
        """Recursively converts a Python object (parsed from JSON) to Markdown."""
        indent = " " * (indent_level * 2)
        markdown_output = ""

        if isinstance(obj, dict):
            for key, value in obj.items():
                markdown_output += f"{indent}- **{key}**:\n"
                if isinstance(value, (dict, list)):
                    markdown_output += _convert(value, indent_level + 1)
                else:
                     markdown_output += f" {value}\n"
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    markdown_output += f"{indent}-\n"  # Add a dash for each nested item
                    markdown_output += _convert(item, indent_level + 1)
                else:
                    markdown_output += f"{indent}- {item}\n"
        else:
            markdown_output += f"{indent}{str(obj)}\n"
        return markdown_output
    # def _convert(obj, indent_level=0):
    #     """Recursively converts a Python object (parsed from JSON) to Markdown."""
    #     indent = " " * (indent_level * 2)
    #     markdown_output = ""

    #     if isinstance(obj, dict):
    #         for key, value in obj.items():
    #             markdown_output += f"{indent}- **{key}**:\n"
    #             if isinstance(value, (dict, list)):
    #                 markdown_output += _convert(value, indent_level + 1)
    #             else:
    #                 markdown_output += f"{' ' * ((indent_level + 1) * 2)}{value}\n"
    #     elif isinstance(obj, list):
    #         for item in obj:
    #             if isinstance(item, (dict, list)):
    #                 markdown_output += f"{indent}-\n"  # Add a dash for each nested item
    #                 markdown_output += _convert(item, indent_level + 1)
    #             else:
    #                 markdown_output += f"{indent}- {item}\n"
    #     else:
    #         markdown_output += f"{indent}{str(obj)}\n"
    #     return markdown_output






    return _convert(data).strip()

if __name__ == "__main__":
    if __name__ == "__main__":
        if len(sys.argv) > 1:
            # Read JSON from the file specified as a command-line argument
            file_path = sys.argv[1]
            try:
                with open(file_path, 'r') as f:
                    json_data = f.read()
                markdown_output = json_to_markdown(json_data)
                print(markdown_output)
            except FileNotFoundError:
                print(f"Error: File not found: {file_path}")
            except ValueError as e:
                print(f"Error: Invalid JSON in {file_path}: {e}")
        else:
            # Read JSON from standard input (when using redirection like `< example.json`)
            json_data = sys.stdin.read()
            try:
                markdown_output = json_to_markdown(json_data)
                print(markdown_output)
            except ValueError as e:
                print(f"Error: Invalid JSON input: {e}")
