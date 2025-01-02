# import json
import os
from typing import Annotated, Dict
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
# import sqlite3
import autogen
# from autogen import ConversableAgent, UserProxyAgent, config_list_from_json
from get_schema import get_database_schema
import argparse

os.environ["AUTOGEN_USE_DOCKER"] = "no"

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

def construct_agent(name: str, llm_config: dict, db_path: str, final_answer: str, user_question: str, PROMPT_PATH: str) -> autogen.AssistantAgent:
    database_schema = {} # Placeholder: You might want to fetch the schema here if needed for SQLWriter
    if not database_schema:
        print(f"Warning: Could not retrieve database schema for {name}. ")

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

# Define SQL Writer Agent using the construct_agent function
# workflow2_test.py
def create_sql_writer_agent(context_path: str) -> autogen.AssistantAgent:
    user_question, final_answer, db_path = get_question_and_context(context_path)
    return construct_agent(
        "db_engineer",  # Make sure this matches the section name in your prompts.txt
        llm_config=llm_config_db_engineer,
        db_path=db_path,
        final_answer=final_answer,
        user_question=user_question,
    )


def extract_query(query_str: str) -> str:

    query = ""
    if query_str.startswith("```sql"):
        query = query_str[6:-3]
    elif query_str.startswith("```"):
        query = query_str[3:-3]
    else:
        query = query_str

    return query



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Run workflow2 test with configurable prompt and context paths.")
    parser.add_argument("--prompt_path", type=str, default="./prompts/prompts.txt", help="Path to the prompts file.")
    parser.add_argument("--context_path", type=str, default="./example_results/q1_final_answer.txt", help="Path to the context file.")
    args = parser.parse_args()

    # Instantiate the agents
    sql_writer = create_sql_writer_agent(name = "db_engineer", PROMPT_PATH = args.prompt_path)
    
    user_proxy = autogen.UserProxyAgent(name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,)

    chat_res = user_proxy.initiate_chat(
    sql_writer,
    message="""Write an SQL query to answer the user question. Do not use '```sql' """,
    summary_method="reflection_with_llm",
    )

    
    print(extract_query(chat_res.chat_history[-1]['content']))