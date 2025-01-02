import sqlite3

def create_airline_database_from_file(sql_file_path):
    """
    Creates an SQLite database from the SQL script in the given file.

    Args:
        sql_file_path (str): The path to the SQL file.
    """
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
    except FileNotFoundError:
        print(f"Error: SQL file not found at {sql_file_path}")
        return

    conn = sqlite3.connect('airline.db')
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()

# Example usage with the provided file path
if __name__ == "__main__":
    create_airline_database_from_file('airline_example.sql')