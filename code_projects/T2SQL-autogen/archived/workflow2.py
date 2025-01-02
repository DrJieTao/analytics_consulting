#### QUERY GENERATION, VALIDATION, and EXECUTION
# workflow2.py
import autogen
import argparse
from get_schema import get_database_schema

# Define LLM configurations (assuming these are the same as in workflow1.py)
llm_configs = {
    "planner": {
        "config_list": [
            {
                "model": "marco-o1",
                "client_host": "http://127.0.0.1:12345",
                "api_type": "ollama",
                "stream": False,
            },
        ]
    },
    "db_engineer": {
        "config_list": [
            {
                "model": "qwen2.5-coder:14b",
                "client_host": "http://127.0.0.1:12345",
                "api_type": "ollama",
                "stream": False,
                "temperature":0
            },
        ]
    },
    "db_admin_reporter": {
        "config_list": [
            {
                "model": "llama3.2:latest",
                "client_host": "http://127.0.0.1:12345",
                "api_type": "ollama",
                "api_base": "http://127.0.0.1:12345",
                "timeout": 60
            },
        ]
    }
}

llm_config_db_engineer = llm_configs["db_engineer"]
llm_config_db_admin_reporter = llm_configs["db_admin_reporter"]

### GET PROMPT TEMPLATE
PROMPT_PATH = "./prompts/prompts.txt"

def read_prompt_section(file_path: str, section_name: str) -> str:
    """Reads a specific section from a text file based on the section name.

    Args:
        file_path: The path to the text file.
        section_name: The name of the section to read (e.g., "planner").

    Returns:
        The content of the specified section, or None if the section is not found.
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
        start_tag = f"<{section_name}>"
        end_tag = f"</{section_name}>"
        start_index = content.find(start_tag)
        end_index = content.find(end_tag)
        if start_index != -1 and end_index != -1:
            return content[start_index + len(start_tag):end_index].strip()
        else:
            return None
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None

def get_question_and_context(context_path: str) -> tuple[str, str, str]:
    """Reads the user question and final answer from a context file.

    Args:
        context_path: The path to the context file.

    Returns:
        A tuple containing the user question and final answer, or (None, None) if not found.
    """
    try:
        with open(context_path, "r") as context_f:
            content = context_f.read()
        question_tag = "user_question"
        final_answer_tag = "final_answer"
        db_path_tag = 'db_path'
        
        question_start_tag = f"<{question_tag}>"
        question_end_tag = f"</{question_tag}>"
        final_answer_start_tag = f"<{final_answer_tag}>"
        final_answer_end_tag = f"</{final_answer_tag}>"
        db_path_start_tag = f"<{db_path_tag}>"
        db_path_end_tag = f"</{db_path_tag}>"

        question_start_index = content.find(question_start_tag)
        question_end_index = content.find(question_end_tag)
        final_answer_start_index = content.find(final_answer_start_tag)
        final_answer_end_index = content.find(final_answer_end_tag)
        db_path_start_index = content.find(db_path_start_tag)
        db_path_end_index = content.find(db_path_end_tag)

        user_question = None
        final_answer = None
        db_path = None

        if question_start_index != -1 and question_end_index != -1:
            user_question = content[question_start_index + len(question_start_tag):question_end_index].strip()
        if final_answer_start_index != -1 and final_answer_end_index != -1:
            final_answer = content[final_answer_start_index + len(final_answer_start_tag):final_answer_end_index].strip()
        if db_path_start_index != -1 and db_path_end_index != -1:
            db_path = content[db_path_start_index + len(db_path_start_tag):db_path_end_index].strip()
        
        return user_question, final_answer, db_path

    except FileNotFoundError:
        print(f"Error: File not found at {context_path}")
        return None, None


def construct_agent(name: str, llm_config: dict, db_path: str, final_answer: str, user_question: str) -> autogen.AssistantAgent:
    # ... (same as before)
    database_schema = get_database_schema(db_path)
    if not database_schema:
        print(f"Warning: Could not retrieve database schema. Please check the database path: {db_path}")
        database_schema = {}

    system_message = read_prompt_section(PROMPT_PATH, name).format(final_answer=final_answer,
                                                                   user_question=user_question,
                                                                   database_schema=database_schema)
    if system_message:
        return autogen.AssistantAgent(
            name=name, llm_config=llm_config, system_message=system_message,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        )
    else:
        return None

def generate_and_execute_sql(db_path: str, final_answer: str, user_question: str, max_attempts: int = 5):
    """Generates and executes an SQL query iteratively using the db_engineer and db_admin agents.

    Args:
        db_path: The path to the SQLite database file.
        final_answer: The final answer from the previous workflow.
        user_question: The initial user question.

    Returns:
        The result of the SQL query execution, or None if an error occurs after max attempts.
    """
    # Define the database engineer agent
    db_engineer = construct_agent("db_engineer", llm_config_db_engineer, db_path, final_answer, user_question)
    if not db_engineer:
        print("Error: Could not create the database engineer agent.")
        return None

    # Define the database admin agent
    db_admin = autogen.UserProxyAgent(
        name="database_admin",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"work_dir": "db_admin_workdir", "env": {"DB_PATH": db_path}, "use_docker": False},
        # llm_config={"timeout": 60},
        llm_config=llm_config_db_admin_reporter,
    )

    # Initial message to the db_engineer
    initial_message = "Let's write an SQL query based on the final answer."

    attempt = 0
    sql_query = None
    execution_result = None

    while attempt < max_attempts:
        attempt += 1
        if attempt == 1:
            # Initiate the chat with the db_engineer
            db_admin.initiate_chat(
                db_engineer,
                message=initial_message,
                max_turns=3,
            )
        else:
            # Continue the conversation with the db_engineer with feedback
            db_admin.send(
                message=f"The previous query resulted in an error. Please revise the SQL query.",
                recipient=db_engineer,
            )

        # Retrieve the last message from the db_engineer, which should be the SQL query
        sql_query = None
        for i in reversed(range(len(db_admin.chat_messages[db_engineer]))):
            if db_admin.chat_messages[db_engineer][i]["role"] == "assistant":
                sql_query = db_admin.chat_messages[db_engineer][i]["content"]
                break

    if sql_query:
        # Execute the SQL query using the db_admin
        db_admin.send(
            message=f"""Execute this SQL query against the database located at $DB_PATH:
                        ```
                        {sql_query}
                        """,
            recipient=db_engineer,
        )
        # Retrieve the last message from the db_admin, which should be the execution result
        for i in reversed(range(len(db_admin.chat_messages[db_engineer]))):
            if db_admin.chat_messages[db_engineer][i]["role"] == "user":
                execution_result = db_admin.chat_messages[db_engineer][i]["content"]
                if "Error" not in execution_result:
                    return execution_result
                break
    else:
        print("Error: Could not retrieve SQL query from db_engineer.")
        return None  # Or handle this case differently
    print(f"Reached maximum attempts ({max_attempts}). Could not execute the SQL query successfully.")
    return execution_result


def main():
    parser = argparse.ArgumentParser(description="AutoGen workflow to generate and execute SQL query.")
    # parser.add_argument('--db_path', type=str, required=True, help='Path to the SQLite database file')
    parser.add_argument('--context_path', type=str, required=True, help='Path to the context file containing user_question and final_answer')
    parser.add_argument('--max_attempts', type=int, default=3, help='Maximum number of attempts for SQL query generation and execution')
    args = parser.parse_args()

    user_question, final_answer, db_path = get_question_and_context(args.context_path)
    if user_question and final_answer:
        execution_result = generate_and_execute_sql(db_path, final_answer, user_question, args.max_attempts)
        if execution_result:
            print(f"\nSQL Query Execution Result:\n{execution_result}")
        else:
            print("\nCould not generate and execute the SQL query after multiple attempts.")
    else:
        print("Error: Could not retrieve user question and final answer from the context file.")

if __name__ == "__main__":
    main()
