import subprocess
import os
from datetime import datetime
import sys
import argparse

def get_example(example_path: str = "example1.txt") -> str:
    """
    Extracts an example from a file based on specified start and end tags.

    Args:
        example_path (str): Path to the example file.

    Returns:
        str: The extracted example, or an error message if the file or tags are not found.
    """
    example_tag = "output"
    example_start, example_end = f"<{example_tag}>", f"</{example_tag}>"
    try:
        with open(example_path, "r") as example_file:
            content = example_file.read()
    except FileNotFoundError:
        return "Error: example file cannot be found."

    example_start_idx = content.find(example_start)
    example_end_idx = content.find(example_end)

    if example_start_idx == -1 or example_end_idx == -1:
        return "Error: example tag cannot be found."

    example = content[example_start_idx + len(example_start) : example_end_idx]
    return example

def get_input(input_path: str) -> str:
    """
    Extracts the input section from a file based on <input> tags.

    Args:
        input_path (str): Path to the input file.

    Returns:
        str: The extracted input, or an error message if the file or tags are not found.
    """
    input_tag = "input"
    input_start, input_end = f"<{input_tag}>", f"</{input_tag}>"
    try:
        with open(input_path, "r") as input_file:
            content = input_file.read()
    except FileNotFoundError:
        return "Error: input file cannot be found."

    input_start_idx = content.find(input_start)
    input_end_idx = content.find(input_end)

    if input_start_idx == -1 or input_end_idx == -1:
        return "Error: input tag cannot be found."

    input_content = content[input_start_idx + len(input_start) : input_end_idx]
    return input_content

def generate_ticket(
    prompt_path: str,
    plan_path: str,
    example:bool = False,
    # example_path: str = "",
    model: str = "gemini-exp-1206",
) -> str:
    """
    Generates a summary using a specified language model.

    Reads prompt, transcript, and optional example files, formats the prompt,
    and then executes the LLM to generate a summary.

    Args:
        prompt_path (str): Path to the prompt template file.
        transcript_path (str): Path to the transcript file.
        example_path (str, optional): Path to the example file. Defaults to "".
        model (str, optional): The name of the language model to use.
            Defaults to "gemini-exp-1206".

    Returns:
        str: The generated summary, or an error message if a file is not found or LLM execution fails.
    """
    try:
        with open(prompt_path, "r") as prompt_file:
            prompt_template = prompt_file.read()
        plan_input = get_input(plan_path)
        if example:
            example = get_example()
        else:
            example = ""
    except FileNotFoundError:
        return "Error: required data file cannot be found."

    prompt = prompt_template.format(input=plan_input, example=example)
    # print(prompt)
    command = ["llm", "-m", model, prompt]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    if stderr:
        return f"Error during LLM execution:\n{stderr}"

    report = stdout.strip()
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Ticket Assignment based on Action plan")
    parser.add_argument(
        "--prompt_filename", type=str, help="Filename of the prompt.",
        default="prompt.txt",
    )
    parser.add_argument(
        "--input_filename", type=str, help="Filename of the input.",
        default="example2.txt",
    )
    parser.add_argument(
        "--example",
        type=str,
        default="False",
        help="Include example or not",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-exp-1206",
        help="The name of the language model to use.",
    )
    args = parser.parse_args()

    # prompt_filename = "prompt.txt"
    tickets_filename = (
        args.input_filename.replace(".txt", "_tickets.md")
        if args.input_filename.endswith(".txt")
        else f"{args.input_filename}_tickets.md"
    )

    tickets = generate_ticket(
        args.prompt_filename, args.input_filename, args.example, args.model
    )

    with open(tickets_filename, "w") as summary_file:
        summary_file.write(tickets)

    print(f"Summary saved to {tickets_filename}")
