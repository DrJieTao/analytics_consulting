import sqlite3
import os
import autogen

# sql_query = """
# SELECT COUNT(DISTINCT T1.TicketID) 
# FROM Tickets AS T1 
# JOIN Passengers AS T2 ON T1.PassengerID = T2.PassengerID 
# WHERE T2.FirstName = 'Bob';
# """

sql_query = """SELECT T3.FirstName, T3.LastName FROM Tickets AS T1 JOIN Flights AS T2 ON T1.FlightID = T2.FlightID JOIN Passengers AS T3 ON T1.PassengerID = T3.PassengerID WHERE T2.FlightID = 'SA101';"""

project_path = "/Users/jtao/code_projects/T2SQL/"
db_path = "example_db/airline.db"


def get_query(query_path: str) -> str:
    """
    Extracts the SQL query from a file.

    The file is expected to contain the query after a separator line of 80 dashes.

    Args:
        query_path (str): The path to the file containing the SQL query.

    Returns:
        str: The extracted SQL query, or an empty string if not found.
    """
    with open(query_path, "r") as test_file:
        content = test_file.read()
        sep = "-"*80
        query = content.split(sep=sep)[-2].strip()
    return query
# test_path = "example_results/q1_query.txt"
# query_path = os.path.join(project_path, test_path)
# sql_query = get_query(query_path)

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
        return str(results[0][0])
    except Exception as e:
        return f"Error executing SQL: {e}"

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
engineer_config = llm_configs["db_engineer"]
reporter_config = llm_configs["db_admin_reporter"]

engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=engineer_config,
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
)
# import os
# import argparse
# from get_schema import get_database_schema
# from workflow3 import get_query

# parser = argparse.ArgumentParser(description="Run SQL query.")
# parser.add_argument('--project_path', type=str, required=True, help='Path to the project directory')
# parser.add_argument('--db_path', type=str, required=True, help='Path to the database file')
# args = parser.parse_args()

db_path = os.path.join(project_path, db_path)


executor = autogen.UserProxyAgent(
    name="Executor",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=5,
    function_map={
        "execute_sql": lambda sql_query_str: execute_sql(sql_query_str, db_path),
    },
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
)


# print(sql_query)

# Message template for the executor
query_exe_chat = executor.initiate_chat(engineer, message=f"execute the SQL query `{sql_query}` on `{db_path}`.")

# print(query_exe_chat.chat_history[-2]['content'])
# question = "How many tickets did Bob book?"
question = "Which passenger(s) booked flight with ID 'SA101'?"
answer = query_exe_chat.chat_history[-2]['content']

reporter = autogen.AssistantAgent(
    name="reporter",
    llm_config=reporter_config,
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
    system_message = "write a natural response using the answer provided for the given question. If you answered the question then you should reply exactly 'TERMINATE'"
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config=False, 
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
)

answer_chat = user_proxy.initiate_chat(reporter, message=f"answer this question {question} using this answer {answer}")

print(f"""
    User Question: {question} \n
    AI Answer: {answer_chat.chat_history[-3]['content']}

""")
