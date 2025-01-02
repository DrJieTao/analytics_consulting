### use `google.generativeai` instead of `llm`
### for TOOL USE

import google.generativeai as genai
import os
import json
import time
import traceback


# Configure API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise Exception("Please set the GOOGLE_API_KEY as an environment variable")
genai.configure(api_key=GOOGLE_API_KEY)

# Define the model
model = genai.GenerativeModel('gemini-pro')


# Define the tool (function) for executing python code safely
def execute_python_code(code: str) -> str:
    """Executes python code and returns output.
    The execution has a time limit of 3 seconds
    """
    try:
        # Implement the safe execution with a timeout
        start_time = time.time()
        import subprocess
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


tools = [
    {
        'name': 'execute_python_code',
        'description': 'Executes python code and returns output. The execution has a time limit of 3 seconds.',
        'parameters': {
            'properties': {
                'code': {
                    'type': 'string',
                    'description': 'The python code to be executed'
                }
            },
            'required': ['code']
        }
    }
]


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


def analyze_code(student_code: str) -> str:
    """Analyzes student code, and returns the suggestions.
        The function uses tool_use to safely execute the student code
    Args:
        student_code (str): Code uploaded by the student.
    Returns:
        str: Markdown output.
    """
    
    prompt = create_debugger_prompt(prompt_template, student_code)

    # Generate response using the prompt and the functions
    model = genai.GenerativeModel('gemini-exp-1206')
    chat = model.start_chat(enable_automatic_function_calling=True)

    response = chat.send_message(prompt, tools=tools)

    if response.text:
        return response.text
    elif response.prompt_feedback:
        return "The response was blocked due to safety reasons. Please check your content and try again."
    else:
        return "No response received."

    # Handle Tool calls
    if response.candidates[0].content.parts[0].function_call:
        # Retrieve function call details
        function_call = response.candidates[0].content.parts[0].function_call
        function_name = function_call.name
        function_args = function_call.args

        if function_name == 'execute_python_code':
            # Execute the python code safely
            code_to_execute = function_args['code']
            function_response = execute_python_code(code_to_execute)

            # Feed the results back into the model for the next response.
            response = model.generate_content(
                prompt,
                tools=[
                    genai.types.Tool.from_dict(function_declarations[0])
                ],
            )

            if not response.text and response.prompt_feedback:
              return "The response was blocked due to safety reasons. Please check your content and try again."
            return response.text

        else:
            return "Tool name not found."
    else:
        return response.text


# Example usage
student_code_1 = """
def add(a b):
    return a+b

print(add(1,2))
"""

student_code_2 = """
def add(a, b):
    return a+b

print(add(1,"2"))
"""

student_code_3 = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n* factorial(n-1)

print(factorial(1000))
"""
student_code_4 = """
import time

def run_forever():
    while True:
        time.sleep(1)
        print ("I'm still here")

run_forever()
"""
def main():
    print ("Student Code 1 Result")
    print (analyze_code(student_code_1))
    print ("\nStudent Code 2 Result")
    print (analyze_code(student_code_2))
    print ("\nStudent Code 3 Result")
    print (analyze_code(student_code_3))
    print ("\nStudent Code 4 Result")
    print (analyze_code(student_code_4))

if __name__ == "__main__":
    main()