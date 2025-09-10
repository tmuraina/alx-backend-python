#!/usr/bin/env python3
"""
Reusable Query Context Manager for Database Operations.

This module demonstrates advanced Python techniques for creating reusable
context managers that handle both database connections and query execution.
The ExecuteQuery class provides a clean interface for executing parameterized
queries with automatic resource management.
"""

import sqlite3
import os


class ExecuteQuery:
    """
    A reusable context manager class for executing database queries.
    
    This class implements the context manager protocol to handle both database
    connection management and query execution. It accepts a query string and
    optional parameters, executes the query, and returns the results while
    ensuring proper resource cleanup.
    
    Attributes:
        db_name (str): The name/path of the SQLite database file
        query (str): The SQL query to execute
        parameters (tuple): Optional parameters for the query
        connection (sqlite3.Connection): The database connection object
        cursor (sqlite3.Cursor): The database cursor for executing queries
        results (list): The query results
    """
    
    def __init__(self, db_name, query, parameters=None):
        """
        Initialize the ExecuteQuery context manager.
        
        Args:
            db_name (str): The name/path of the SQLite database file
            query (str): The SQL query to execute
            parameters (tuple, optional): Parameters for parameterized queries
        """
        self.db_name = db_name
        self.query = query
        self.parameters = parameters or ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - establish connection and execute query.
        
        This method is called when entering the 'with' statement. It creates
        a database connection, executes the specified query with parameters,
        and returns the query results.
        
        Returns:
            list: The results of the executed query
        """
        try:
            # Establish connection to the SQLite database
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            
            print(f"Connected to database: {self.db_name}")
            print(f"Executing query: {self.query}")
            
            if self.parameters:
                print(f"With parameters: {self.parameters}")
            
            # Execute the query with or without parameters
            if self.parameters:
                self.cursor.execute(self.query, self.parameters)
            else:
                self.cursor.execute(self.query)
            
            # Fetch all results
            self.results = self.cursor.fetchall()
            
            print(f"Query executed successfully. Retrieved {len(self.results)} rows.")
            return self.results
            
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
            # Re-raise the exception to be handled by the calling code
            raise
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager - cleanup database resources.
        
        This method is called when exiting the 'with' statement, regardless
        of whether an exception occurred. It ensures proper cleanup of database
        resources by closing the cursor and connection.
        
        Args:
            exc_type: Exception type if an exception occurred, None otherwise
            exc_value: Exception value if an exception occurred, None otherwise
            traceback: Exception traceback if an exception occurred, None otherwise
            
        Returns:
            bool: False to propagate any exceptions that occurred in the context
        """
        try:
            if self.cursor:
                self.cursor.close()
                print("Database cursor closed")
            
            if self.connection:
                # Commit any pending transactions before closing
                self.connection.commit()
                self.connection.close()
                print("Database connection closed and committed")
                
        except sqlite3.Error as e:
            print(f"Error during database cleanup: {e}")
        
        # Handle different types of exceptions
        if exc_type is not None:
            print(f"Exception occurred in context: {exc_type.__name__}: {exc_value}")
        
        # Return False to propagate any exceptions that occurred in the context
        return False


def setup_sample_database(db_name):
    """
    Create a sample database with users table for demonstration.
    
    Args:
        db_name (str): Name of the database file to create
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER
            )
        ''')
        
        # Insert sample data with varied ages for testing
        sample_users = [
            ('Alice Johnson', 'alice@example.com', 28),
            ('Bob Smith', 'bob@example.com', 35),
            ('Charlie Brown', 'charlie@example.com', 22),
            ('Diana Prince', 'diana@example.com', 30),
            ('Edward Norton', 'edward@example.com', 42),
            ('Fiona Green', 'fiona@example.com', 19),
            ('George Wilson', 'george@example.com', 55),
            ('Helen Davis', 'helen@example.com', 26),
            ('Ivan Rodriguez', 'ivan@example.com', 33),
            ('Julia Kim', 'julia@example.com', 29)
        ]
        
        # Clear existing data and insert fresh sample data
        cursor.execute('DELETE FROM users')
        cursor.executemany(
            'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
            sample_users
        )
        
        conn.commit()
        conn.close()
        print(f"Sample database '{db_name}' created with users table")
        
    except sqlite3.Error as e:
        print(f"Error setting up sample database: {e}")


def display_results(results, title="Query Results"):
    """
    Display query results in a formatted table.
    
    Args:
        results (list): List of result tuples from the database query
        title (str): Title for the results display
    """
    print(f"\n{title}")
    print("=" * len(title))
    
    if results:
        print(f"{'ID':<5} {'Name':<15} {'Email':<25} {'Age':<5}")
        print("-" * 55)
        for row in results:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<25} {row[3] or 'N/A':<5}")
    else:
        print("No results found.")
    print()


def main():
    """
    Demonstrate the ExecuteQuery context manager usage.
    """
    db_name = "sample_database.db"
    
    # Setup sample database with users table
    setup_sample_database(db_name)
    
    print("\n" + "="*60)
    print("DEMONSTRATING REUSABLE QUERY CONTEXT MANAGER")
    print("="*60)
    
    # Example 1: Execute the required query - users older than 25
    print("\n1. EXECUTING PARAMETERIZED QUERY")
    print("-" * 40)
    
    try:
        query = "SELECT * FROM users WHERE age > ?"
        parameter = (25,)  # Note: parameters must be a tuple
        
        with ExecuteQuery(db_name, query, parameter) as results:
            display_results(results, "Users older than 25")
            
    except Exception as e:
        print(f"Error executing query: {e}")
    
    # Example 2: Execute query without parameters
    print("\n2. EXECUTING SIMPLE QUERY")
    print("-" * 40)
    
    try:
        query = "SELECT * FROM users"
        
        with ExecuteQuery(db_name, query) as results:
            display_results(results, "All Users")
            
    except Exception as e:
        print(f"Error executing query: {e}")
    
    # Example 3: Execute query with multiple parameters
    print("\n3. EXECUTING COMPLEX PARAMETERIZED QUERY")
    print("-" * 40)
    
    try:
        query = "SELECT * FROM users WHERE age BETWEEN ? AND ? ORDER BY age"
        parameters = (25, 40)
        
        with ExecuteQuery(db_name, query, parameters) as results:
            display_results(results, "Users aged between 25 and 40")
            
    except Exception as e:
        print(f"Error executing query: {e}")
    
    # Example 4: Demonstrate error handling
    print("\n4. DEMONSTRATING ERROR HANDLING")
    print("-" * 40)
    
    try:
        # This query will cause an error (invalid table name)
        query = "SELECT * FROM nonexistent_table"
        
        with ExecuteQuery(db_name, query) as results:
            display_results(results, "This should not display")
            
    except sqlite3.Error as e:
        print(f"Expected database error caught: {e}")
    except Exception as e:
        print(f"Unexpected error caught: {e}")
    
    print("\n" + "="*60)
    print("REUSABLE QUERY CONTEXT MANAGER DEMONSTRATION COMPLETE")
    print("="*60)
    
    # Cleanup: Remove the sample database file
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Sample database '{db_name}' removed")


if __name__ == "__main__":
    main()
