import os
from typing import List, Dict, Union
from dotenv import load_dotenv
from chain import MinimalChainable#, FusionChain
import llm
import json
import logging

problem = """Write a function (remove_val(val, lst)) that removes all occurrences of a specific value (val) 
in a given list (lst). Also, print out the indices of the items being removed, if any. """
tutor_path = "../prompts/tutor.txt"
reflect_path = "../prompts/reflect.txt"

def read_prompt_from_file(filepath: str) -> str:
    """
    Reads the content of a prompt file.

    Args:
        filepath (str): The path to the prompt file.

    Returns:
        str: The content of the file as a string.
    """
    try:
        with open(filepath, "r") as f:
            prompt_content = f.read()
        return prompt_content
    except FileNotFoundError:
        logging.error(f"Prompt file not found: {filepath}")
        return ""
    except Exception as e:
        logging.error(f"Error reading prompt file: {filepath}\n{e}")
        return ""


def build_models() -> List[llm.Model]:
    """Initializes and returns a list of Gemini language models."""
    load_dotenv()
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    gemini_exp_model: llm.Model = llm.get_model("gemini-exp-1206")
    gemini_exp_model.key = gemini_api_key
    # Add more Gemini models here if needed
    gemini_flash_model: llm.Model = llm.get_model("gemini-2.0-flash-exp")
    gemini_flash_model.key = gemini_api_key
    return [gemini_exp_model, gemini_flash_model]

def prompt(model: llm.Model, prompt: str):
    res = model.prompt(
        prompt,
        temperature=0.5,
    )
    return res.text()

def prompt_chainable_poc():

    gemini_exp_model, _ = build_models()

    result, context_filled_prompts = MinimalChainable.run(
        context={"problem": problem},
        model=gemini_exp_model,
        callable=prompt,
        prompts=[
            # prompt #1
            read_prompt_from_file(tutor_path),
            # prompt #2
            """Convert the PROBLEM and THOUGHT_PROCESS from JSON to proper Markdown format
            PROBLEM:
            {{output[-1].problem}}
            THOUGHT_PROCESS:
            {{output[-1].thought_process}}
            """,
            # prompt #3
            read_prompt_from_file(reflect_path),
            # prompt #4
            # """Extract the OUTPUT from previous result  
            # OUTPUT:
            # {{output[-1].optimized_thought_process}}
            # """,
        ],
    )
    # print(context_filled_prompts)

    chained_prompts = MinimalChainable.to_delim_text_file(
        "remove_val_prompts", context_filled_prompts
    )
    # print(chained_prompts)
    # print(result[-2])
    chainable_result = MinimalChainable.to_delim_text_file("remove_val", result)

    print(f"\n\n📖 Prompts~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n\n{chained_prompts}")
    print(f"\n\n📊 Results~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n\n{chainable_result}")

    pass

def main():
    # gemini_exp_model, _ = build_models()
    # print(prompt(gemini_exp_model, "What is AI?"))
    # print(read_prompt_from_file(tutor_path).format(problem=problem))
    # print(read_prompt_from_file(reflect_path))
    prompt_chainable_poc()

    # fusion_chain_poc()


if __name__ == "__main__":
    main()