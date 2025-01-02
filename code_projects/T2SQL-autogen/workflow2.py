# workflow2.py
#### GENERATE QUERY

import os
from typing import Annotated, Dict

import autogen
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
# PROMPT_PATH = "./prompts/prompts.txt"

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

# context_path = "./example_results/q1_final_answer.txt"
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

def create_sql_writer_agent(prompt_path: str, context_path: str, name: str = "db_engineer") -> autogen.AssistantAgent:
    user_question, final_answer, db_path = get_question_and_context(context_path)
    database_schema = {} # Placeholder: You might want to fetch the schema here if needed for SQLWriter
    if not database_schema:
        print(f"Warning: Could not retrieve database schema for {name}. ")

    system_message = read_prompt_section(prompt_path, name).format(final_answer=final_answer,
                                                                   user_question=user_question,
                                                                   database_schema=database_schema)
    if system_message:
        return autogen.AssistantAgent(
            name=name, llm_config=llm_config_db_engineer, system_message=system_message,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        )
    else:
        return None
 

def extract_query(query_text:str) -> str:

        query = ""
        if query_text.startswith("```sql"):
            query = query_text[6:-3]
        elif query_text.startswith("```"):
            query = query_text[3:-3]
        else:
            query = query_text
        return query

user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
        llm_config=llm_config_db_admin_reporter,)

if __name__ == "__main__":
    # Instantiate the agents
    # sql_writer = create_sql_writer_agent()
   
   

    parser = argparse.ArgumentParser(description="Run workflow2 test with configurable prompt and context paths.")
    parser.add_argument("--prompt_path", type=str, default="./prompts/prompts.txt", help="Path to the prompts file.")
    parser.add_argument("--context_path", type=str, default="./example_results/q1_final_answer.txt", help="Path to the context file.")
    args = parser.parse_args()
    

    # Instantiate the agents
    sql_writer = create_sql_writer_agent(prompt_path = args.prompt_path, context_path = args.context_path)
    gen_query_chat = user_proxy.initiate_chat(  # The combined agent initiates the chat
        sql_writer,
        message="""Write an SQL query to answer the user question. Do not use '```sql' """,
        recipient_reply_mode="TERMINATE",
        summary_method="reflection_with_llm",
    )
    # print(gen_query_chat.chat_history[-1]['content'])
    
    # print(extract_query(gen_query_chat.chat_history[-1]['content']))

    # user_proxy.initiate_chat(  # The combined agent initiates the chat
    #     executor,
    #     message=f"""execute this query {extract_query(gen_query_chat.chat_history[-1]['content'])}""",
    #     recipient_reply_mode="TERMINATE",
    #     # summary_method="reflection_with_llm",
    # )