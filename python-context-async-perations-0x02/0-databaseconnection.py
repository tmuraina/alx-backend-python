#!/usr/bin/env python3
"""
Custom class-based context manager for database connections.

This module demonstrates advanced Python techniques for managing database
connections using context managers. The DatabaseConnection class ensures
proper resource acquisition and cleanup using __enter__ and __exit__ methods.
"""

import sqlite3
import os


class DatabaseConnection:
    """
    A custom context manager class for handling SQLite database connections.
    
    This class implements the context manager protocol using __enter__ and __exit__
    methods to ensure proper database connection management. The connection is
    automatically opened when entering the context and closed when exiting,
    even if an exception occurs.
    
    Attributes:
        db_name (str): The name/path of the SQLite database file
        connection (sqlite3.Connection): The database connection object
        cursor (sqlite3.Cursor): The database cursor for executing queries
    """
    
    def __init__(self, db_name):
        """
        Initialize the DatabaseConnection context manager.
        
        Args:
            db_name (str): The name/path of the SQLite database file
        """
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """
        Enter the context manager - establish database connection.
        
        This method is called when entering the 'with' statement. It creates
        a connection to the SQLite database and returns a cursor for executing
        queries.
        
        Returns:
            sqlite3.Cursor: Database cursor for executing SQL queries
        """
        try:
            # Establish connection to the SQLite database
            self.connection = sqlite3.connect(self.db_name)
            # Create a cursor for executing queries
            self.cursor = self.connection.cursor()
            print(f"Successfully connected to database: {self.db_name}")
            return self.cursor
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
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
                print("Database connection closed")
                
        except sqlite3.Error as e:
            print(f"Error during database cleanup: {e}")
        
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
        
        # Insert sample data
        sample_users = [
            ('Alice Johnson', 'alice@example.com', 28),
            ('Bob Smith', 'bob@example.com', 35),
            ('Charlie Brown', 'charlie@example.com', 22),
            ('Diana Prince', 'diana@example.com', 30),
            ('Edward Norton', 'edward@example.com', 42)
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO users (name, email, age) VALUES (?, ?, ?)',
            sample_users
        )
        
        conn.commit()
        conn.close()
        print(f"Sample database '{db_name}' created with users table")
        
    except sqlite3.Error as e:
        print(f"Error setting up sample database: {e}")


def main():
    """
    Demonstrate the DatabaseConnection context manager usage.
    """
    db_name = "sample_database.db"
    
    # Setup sample database with users table
    setup_sample_database(db_name)
    
    print("\n" + "="*50)
    print("DEMONSTRATING DATABASE CONNECTION CONTEXT MANAGER")
    print("="*50)
    
    # Use the custom context manager to query the database
    try:
        with DatabaseConnection(db_name) as cursor:
            print("\nExecuting query: SELECT * FROM users")
            print("-" * 30)
            
            # Execute the query
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            
            # Print results with proper formatting
            if results:
                print("Query Results:")
                print(f"{'ID':<5} {'Name':<15} {'Email':<25} {'Age':<5}")
                print("-" * 55)
                for row in results:
                    print(f"{row[0]:<5} {row[1]:<15} {row[2]:<25} {row[3] or 'N/A':<5}")
            else:
                print("No users found in the database.")
                
    except Exception as e:
        print(f"An error occurred: {e}")
    
    print("\n" + "="*50)
    print("CONTEXT MANAGER DEMONSTRATION COMPLETE")
    print("="*50)
    
    # Cleanup: Remove the sample database file
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Sample database '{db_name}' removed")


if __name__ == "__main__":
    main()
