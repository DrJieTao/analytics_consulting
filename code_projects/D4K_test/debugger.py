import llm
import os
import json
import time
import traceback
import subprocess

# Define the tool (function) for executing python code safely
def execute_python_code(code: str) -> str:
    """Executes python code and returns output.
    The execution has a time limit of 3 seconds
    """
    try:
        # Implement the safe execution with a timeout
        start_time = time.time()
        process = subprocess.Popen(['python', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return "Timeout: The code took too long to execute. Please try again with a simpler program"
        
        output = stdout.decode('utf-8')
        error = stderr.decode('utf-8')
        if error:
            return error
        return output
    except Exception as e:
        trace = traceback.format_exc()
        return f"Error during execution: {str(e)}, Traceback:{trace}"

# Function declaration for llm
tool_schema = {
    'execute_python_code': {
        'description': 'Executes python code and returns output. The execution has a time limit of 3 seconds.',
        'parameters': {
            'code': {
                'type': 'string',
                'description': 'The python code to be executed'
                }
            },
        'required': ['code']
    }
}

PROMPT_PATH = './prompts/debugger.txt'
with open(PROMPT_PATH, "r") as f:
    prompt_template = f.read()

def create_debugger_prompt(prompt_template, student_code):
    """
    Creates a prompt for the debugger tool.

    Args:
        student_code (str): The student's code snippet.

    Returns:
        str: The formatted prompt for the debugger tool.
    """
    formatted_prompt = prompt_template.replace("{{STUDENT_CODE}}", student_code)
    return formatted_prompt

student_code_3 = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n* factorial(n-1)

print(factorial(1000))
"""

# prompt = create_debugger_prompt(prompt_template, student_code_3)

# print(prompt)

def analyze_code(student_code: str) -> str:
    """Analyzes student code, and returns the suggestions.
        The function uses tool_use to safely execute the student code
    Args:
        student_code (str): Code uploaded by the student.
    Returns:
        str: Markdown output.
    """

    prompt = create_debugger_prompt(prompt_template, student_code)


     # Calling llm with tools
    llm_instance = llm.get_model("gemini-exp-1206")
    response = llm_instance.generate_with_tools(
        prompt,
        tools=tool_schema,
        tool_callback = execute_tool
    )
    return response.text

def execute_tool(tool_call):
    """Executes the tools used in the prompt
    """
    if tool_call.tool_name == "execute_python_code":
        code_to_execute = tool_call.arguments["code"]
        return execute_python_code(code_to_execute)
    
    return "Tool name not found"

def main():
    # gemini_exp_model, _ = build_models()
    # print(prompt(gemini_exp_model, "What is AI?"))
    # print(read_prompt_from_file(tutor_path).format(problem=problem))
    # print(read_prompt_from_file(reflect_path))
    analyze_code(student_code_3)

    # fusion_chain_poc()


if __name__ == "__main__":
    main()