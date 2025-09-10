#!/usr/bin/python3

import mysql.connector
from mysql.connector import Error

def stream_users():
    """
    Generator function that streams rows from the user_data table one by one.
    
    Yields:
        dict: Dictionary containing user data with keys: user_id, name, email, age
    
    The function uses a single loop and yields each row as a dictionary.
    """
    connection = None
    cursor = None
    
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host='localhost',
            database='ALX_prodev',
            user='root',  # Change this to your MySQL username
            password='root'  # Change this to your MySQL password
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for easy dict conversion
            
            # Execute query to fetch all users
            cursor.execute("SELECT user_id, name, email, age FROM user_data")
            
            # Single loop to yield rows one by one
            for row in cursor:
                yield row
                
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return
    
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
