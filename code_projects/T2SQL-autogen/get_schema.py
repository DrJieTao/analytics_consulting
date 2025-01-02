import sqlite3

def get_database_schema(db_file_path):
    """
    Retrieves the schema of the SQLite database.

    Args:
        db_file_path (str): The path to the SQLite database file.

    Returns:
        dict: A dictionary where keys are table names and values are the CREATE TABLE statements.
    """
    try:
        conn = sqlite3.connect(db_file_path)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return {}
    
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    
    tables = cursor.fetchall()
    schema = {}
    
    for table_name, create_statement in tables:
        schema[table_name] = create_statement
    
    conn.close()
    
    return schema

# Example usage:
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get database schema.")
    parser.add_argument('--path', type=str, required=True, help='Path to the database file')
    args = parser.parse_args()
    
    # Example usage: python get_schema.py --path="airline.db"
    schema = get_database_schema(args.path)
    for table, definition in schema.items():
        print(f"Table: {table}")
        print(definition)
        print("-" * 20)