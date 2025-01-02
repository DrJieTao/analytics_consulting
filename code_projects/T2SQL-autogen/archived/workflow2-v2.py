# workflow2.py
import autogen
import argparse
from get_schema import get_database_schema
import sqlite3

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
            },
        ]
    },
    "db_admin_reporter": {
        "config_list": [
            {
                "model": "llama3.2:latest",
                "client_host": "http://127.0.0.1:12345",
                "api_type": "ollama",
            },
        ]
    }
}

llm_config_db_engineer = llm_configs["db_engineer"]
llm_config_db_admin_reporter = llm_configs["db_admin_reporter"]

### GET PROMPT TEMPLATE
PROMPT_PATH = "./prompts/prompts.txt"

def read_prompt_section(file_path: str, section_name: str) -> str:
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
        return None, None, None

def construct_agent(name: str, llm_config: dict, db_path: str, final_answer: str, user_question: str) -> autogen.AssistantAgent:
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


def execute_sql(sql_query_str: str, db_path: str) -> str:
    """Executes a SQL query against the database."""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(sql_query_str)
        results = cursor.fetchall()

        # Commit and close the connection
        conn.commit()
        conn.close()

        # Return results as a string
        return str(results)
    except Exception as e:
        return f"Error executing SQL: {e}"

def generate_and_execute_sql(db_path: str, final_answer: str, user_question: str, max_attempts: int = 3):
    """Generates and executes an SQL query iteratively using db_engineer and db_admin agents."""
    # Define the database engineer agent
    db_engineer = construct_agent(
        "db_engineer",
        llm_config=llm_config_db_engineer,
        db_path=db_path,
        final_answer=final_answer,
        user_question=user_question,
    )
    if not db_engineer:
        print("Error: Could not create the database engineer agent.")
        return None

   
    # Define the database admin agent
    db_admin = autogen.UserProxyAgent(
        name="database_admin",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"work_dir": "db_admin_workdir", "env": {"DB_PATH": db_path}, "use_docker": False},
    )

    # Register the execute_sql function with the db_admin agent
    def execute_sql_wrapper(query: str) -> str:
        query = query.strip('`').replace('```sql', '').replace('```', '').strip()
        return execute_sql(query, db_path)
    
    db_admin.register_function(
        function_map={
            "execute_sql_query": execute_sql_wrapper
        }
    )
    

    attempt = 0
    execution_result = None

    while attempt < max_attempts:
        attempt += 1
        if attempt == 1:
            # Initial message to db_engineer
            initial_message = "Write an SQL query to answer the user question. Use the `execute_sql_query` function to execute it."
            db_admin.initiate_chat(
                db_engineer,
                message=initial_message,
            )
        else:
            # Provide feedback for query correction
            db_admin.send(
                message="The previous query resulted in an error. Revise the SQL query and use the `execute_sql_query` function to execute it.",
                recipient=db_engineer,
            )

        # Retrieve the last message from the db_admin
        last_message = db_admin.last_message(db_engineer)
        if last_message and "content" in last_message:
            execution_result = last_message["content"]
            if "Error" in execution_result:
                print(f"SQL Execution Issue: {execution_result}")
            else:
                print(f"SQL Execution Result: {execution_result}")
                return execution_result
        else:
            execution_result = "Error: No response received from db_admin."
            print(execution_result)

    print(f"Reached maximum attempts ({max_attempts}). Could not execute the SQL query successfully.")
    return execution_result


def main():
    parser = argparse.ArgumentParser(description="AutoGen workflow to generate and execute SQL query.")
    parser.add_argument('--context_path', type=str, required=True, help='Path to the context file containing user_question and final_answer')
    parser.add_argument('--max_attempts', type=int, default=3, help='Maximum number of attempts for SQL query generation and execution')
    args = parser.parse_args()

    user_question, final_answer, db_path = get_question_and_context(args.context_path)
    if user_question and final_answer and db_path:
        execution_result = generate_and_execute_sql(db_path, final_answer, user_question, args.max_attempts)
        if execution_result:
            print(f"\nSQL Query Execution Result:\n{execution_result}")
        else:
            print("\nCould not generate and execute the SQL query after multiple attempts.")
    else:
        print("Error: Could not retrieve user question, final answer, and database path from the context file.")

if __name__ == "__main__":
    main()