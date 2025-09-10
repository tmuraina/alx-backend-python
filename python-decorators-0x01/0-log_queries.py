import sqlite3
import functools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_queries(func):
    """
    Decorator that logs SQL queries before executing the decorated function.
    
    Args:
        func: The function to be decorated (should accept a 'query' parameter)
        
    Returns:
        The decorated function that logs queries before execution
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        # Assume the query is passed as 'query' keyword argument or first positional argument
        query = None
        
        # Check if query is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if query is the first positional argument
        elif len(args) > 0:
            # Assume first argument is the query if it's a string
            if isinstance(args[0], str):
                query = args[0]
        
        # Log the query if found
        if query:
            logging.info(f"Executing SQL Query: {query}")
        else:
            logging.warning("No SQL query found in function arguments")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetch all users from the database using the provided query.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        list: Results from the database query
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage
if __name__ == "__main__":
    # Create a sample database and table for testing
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    ''')
    
    # Insert sample data if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ('John Doe', 'john@example.com', 30),
            ('Jane Smith', 'jane@example.com', 25),
            ('Bob Johnson', 'bob@example.com', 35)
        ]
        cursor.executemany("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", sample_users)
        conn.commit()
    
    conn.close()
    
    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Retrieved {len(users)} users from database")
    for user in users:
        print(f"User: {user}")
