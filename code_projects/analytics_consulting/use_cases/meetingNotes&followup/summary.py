import subprocess
import os
from datetime import datetime
import sys
import argparse

def generate_summary(
    prompt_path: str,
    transcript_path: str,
    example_path: str = "",
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
        with open(transcript_path, "r") as transcript_file:
            transcript = transcript_file.read()
        if example_path:
            with open(example_path, "r") as example_file:
                example = example_file.read()
        else:
            example = ""
    except FileNotFoundError:
        return "Error: required data file cannot be found."

    prompt = prompt_template.format(transcript=transcript, example=example)
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
    parser = argparse.ArgumentParser(description="Generate summary from transcript.")
    parser.add_argument(
        "--prompt_filename", type=str, help="Filename of the prompt.",
        default="prompt.txt",
    )
    parser.add_argument(
        "--transcript_filename", type=str, help="Filename of the transcript.",
        default="transcript1.md",
    )
    parser.add_argument(
        "--example_filename",
        type=str,
        default="",
        help="Filename of the example summary.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-exp-1206",
        help="The name of the language model to use.",
    )
    args = parser.parse_args()

    # prompt_filename = "prompt.txt"
    summary_filename = (
        args.transcript_filename.replace(".md", "_summary.md")
        if args.transcript_filename.endswith(".md")
        else f"{args.transcript_filename}_summary.md"
    )

    summary = generate_summary(
        args.prompt_filename, args.transcript_filename, args.example_filename, args.model
    )

    with open(summary_filename, "w") as summary_file:
        summary_file.write(summary)

    print(f"Summary saved to {summary_filename}")
