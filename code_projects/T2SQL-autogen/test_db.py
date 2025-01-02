import os
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
        query = content.split(sep=sep)[-1].strip()
    return query

test_path = "example_results/q1_query.txt"
query_path = os.path.join(project_path, test_path)
sql_query = get_query(query_path)
print(sql_query)
