import autogen
import os
import argparse
import sqlite3

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
        query = content.split(sep=sep)[-1].strip()
        return query
# print(query)
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

# Create an AssistantAgent for generating SQL queries
engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=engineer_config,
)

executor = autogen.UserProxyAgent(
    name="Executor",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    function_map={
        "execute_sql": execute_sql,  # Map the string "add_numbers" to the function
    }
)
def main():
   test_path = "./example_results/q1_query.txt"
   sql_query = get_query(test_path)
   executor.initiate_chat(
    engineer,
    message=f"execute the SQL query {sql_query}",
)

if __name__ == "__main__":
    main()