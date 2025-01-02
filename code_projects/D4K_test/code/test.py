import os
from typing import List, Dict, Union
from dotenv import load_dotenv
from chain import MinimalChainable#, FusionChain
import llm
import json

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
        context={"topic": "AI Agents"},
        model=gemini_exp_model,
        callable=prompt,
        prompts=[
            # prompt #1
            "Generate one blog post title about: {{topic}}. Respond in strictly in JSON in this format: {'title': '<title>'}",
            # prompt #2
            "Generate one hook for the blog post title: {{output[-1].title}}",
            # prompt #3
            """Based on the BLOG_TITLE and BLOG_HOOK, generate the first paragraph of the blog post.

BLOG_TITLE:
{{output[-2].title}}

BLOG_HOOK:
{{output[-1]}}""",
        ],
    )
    print(context_filled_prompts)

    chained_prompts = MinimalChainable.to_delim_text_file(
        "poc_context_filled_prompts", context_filled_prompts
    )
    # print(chained_prompts)
    chainable_result = MinimalChainable.to_delim_text_file("poc_prompt_results", result)

    print(f"\n\n📖 Prompts~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n\n{chained_prompts}")
    print(f"\n\n📊 Results~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n\n{chainable_result}")

    pass

def main():
    # gemini_exp_model, _ = build_models()
    # print(prompt(gemini_exp_model, "What is AI?"))
    prompt_chainable_poc()

    # fusion_chain_poc()


if __name__ == "__main__":
    main()