#### USER QUESTION DECOMPOSITION
import autogen
from get_schema import get_database_schema
import argparse

# Define LLM configurations for different models
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
                "model": "qwen-2.5-coder-14b",
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

llm_config_planner = llm_configs["planner"]
llm_config_db_engineer = llm_configs["db_engineer"]
llm_config_db_admin_reporter = llm_configs["db_admin_reporter"]

### GET PROMPT TEMPLATE
PROMPT_PATH = "./prompts/prompts.txt"
planner_name = "planner"
critic_name = "critic"

### test questions
user_q1 = "How many tickets did Bob book?"
user_q2 = "How many passengers booked flight GW202?"

### USER AGENT
user_proxy = autogen.UserProxyAgent(
    name = "user_proxy",
    system_message="",
    human_input_mode = "TERMINATE",
    code_execution_config=False,  # we don't want to execute code in this case.
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    description="The user who ask questions and give tasks.",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
)

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


def construct_agent(name: str, llm_config: dict, db_path: str, user_question: str) -> autogen.AssistantAgent:
    """Constructs an AutoGen AssistantAgent using a prompt from the prompts.txt file.

    Args:
        name: The name of the agent, corresponding to the section in prompts.txt.
        llm_config: The LLM configuration for the agent.
        db_path: The path to the SQLite database file.

    Returns:
        An instance of autogen.AssistantAgent.
    """
   
    database_schema = get_database_schema(db_path)
    if not database_schema:
        print(f"Warning: Could not retrieve database schema. Please check the database path: {db_path}")
        database_schema = {}

    # print(database_schema)
    system_message = read_prompt_section(PROMPT_PATH, name).format(user_question=user_question,
                                                                   database_schema=database_schema)
    if system_message:
        return autogen.AssistantAgent(
            name=name, llm_config=llm_config, system_message=system_message,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        )
    else:
        return None



def reflection_message(recipient, messages, sender, config):
    print("Reflecting...")
    return f"Reflect and provide critique on the following plan. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"

def start_reflection_chat(db_path: str, user_question: str):
    """Starts a chat with the planner, and uses a nested chat for reflection with the critic.

    Args:
        db_path: The path to the SQLite database file.
        user_question: The initial question from the user.

    Returns:
        The final response from the planner agent.
    """
    

    # Define the planner agent
    planner = construct_agent("planner", llm_config_planner, db_path, user_question)

    # Define the critic agent (acting as reflection assistant)
    critic = construct_agent("critic", llm_config_planner, db_path, user_question)

    if not planner or not critic:
        print("Error: Could not create planner or critic agent.")
        return None

    nested_chat_queue = [
        {
            "recipient": critic,
            "message": reflection_message,
            "max_turns": 1,
        },
    ]
    user_proxy.register_nested_chats(
        nested_chat_queue,
        trigger=planner,
    )

    # Start the conversation with the planner
    user_proxy.initiate_chat(
        planner,
        message=user_question,
        max_turns=3, # Adjust as needed
    )
    
    #### TEST CODE
    # print("\nChat History:")
    # for message in user_proxy.chat_messages[planner]:
    #     print(f"{message['role']}: {message['content']}")

    # Return the last message from the planner
    for i in reversed(range(len(user_proxy.chat_messages[planner]))):
        if user_proxy.chat_messages[planner][i]["role"] == "user":
            return user_proxy.chat_messages[planner][i]["content"]
    return None



def main():
    parser = argparse.ArgumentParser(description="AutoGen workflow for T2SQL.")
    parser.add_argument('--db_path', type=str, required=True, help='Path to the SQLite database file')
    parser.add_argument('--user_question', type=str, required=True, help='Initial user question')
    args = parser.parse_args()

    final_answer = start_reflection_chat(args.db_path, args.user_question)

    if final_answer:
        print(f"""<response>\n\tFinal Answer from Planner for question: 
              <user_question>{args.user_question}</user_question>:\n 
              <final_answer> {final_answer} </final_answer>
              <db_path> {args.db_path} </db_path>
              \n</response>""")
    else:
        print("\nCould not retrieve the final answer from the planner.")

if __name__ == "__main__":
    main()

# Define the database engineer agent
# db_engineer = autogen.AssistantAgent(
#     name="database_engineer",
#     llm_config=llm_config_db_engineer,
#     system_message="You are a database engineer. Based on the identified tables and columns, write an SQL query to answer the user's question.",
# )

# # Define the database admin agent
# db_admin = autogen.UserProxyAgent(
#     name="database_admin",
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=10,
#     code_execution_config={"work_dir": "db_admin_workdir"},
#     llm_config=llm_config_db_admin_reporter, # Apply the llama3.2:3b config
# )

# # Define the reporter agent
# reporter = autogen.AssistantAgent(
#     name="reporter",
#     llm_config=llm_config_db_admin_reporter, # Apply the llama3.2:3b config
#     system_message="You are a reporter. Take the user's original question and the result from the database query and write a clear and concise answer to the user.",
# )

