#!/usr/bin/python3

import mysql.connector
import csv
import uuid
import os
from mysql.connector import Error

def connect_db():
    """
    Connects to the MySQL database server.
    
    Returns:
        connection: MySQL connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change this to your MySQL username
            password='root'  # Change this to your MySQL password
        )
        if connection.is_connected():
            return connection
        else:
            print("Failed to connect to MySQL server")
            return None
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
        print("Database ALX_prodev created successfully or already exists")
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    
    Returns:
        connection: MySQL connection object to ALX_prodev database or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ALX_prodev',
            user='root',  # Change this to your MySQL username
            password='root'  # Change this to your MySQL password
        )
        if connection.is_connected():
            return connection
        else:
            print("Failed to connect to ALX_prodev database")
            return None
    except Error as e:
        print(f"Error while connecting to ALX_prodev database: {e}")
        return None

def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,0) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        
        cursor.execute(create_table_query)
        cursor.close()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, csv_file_path):
    """
    Inserts data from CSV file into the database if it does not exist.
    
    Args:
        connection: MySQL connection object
        csv_file_path: Path to the CSV file containing user data
    """
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Data already exists in user_data table ({count} records)")
            cursor.close()
            return
        
        # Check if CSV file exists
        if not os.path.exists(csv_file_path):
            print(f"CSV file {csv_file_path} not found")
            cursor.close()
            return
        
        # Read and insert data from CSV
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            
            insert_query = """
            INSERT INTO user_data (user_id, name, email, age) 
            VALUES (%s, %s, %s, %s)
            """
            
            data_inserted = 0
            for row in csv_reader:
                try:
                    # Generate UUID for user_id if not present in CSV
                    user_id = row.get('user_id') or str(uuid.uuid4())
                    name = row.get('name', '').strip()
                    email = row.get('email', '').strip()
                    age = int(float(row.get('age', 0)))
                    
                    # Skip rows with missing essential data
                    if not name or not email or age <= 0:
                        continue
                    
                    cursor.execute(insert_query, (user_id, name, email, age))
                    data_inserted += 1
                    
                except (ValueError, KeyError) as e:
                    print(f"Skipping invalid row: {e}")
                    continue
            
            connection.commit()
            cursor.close()
            print(f"Successfully inserted {data_inserted} records into user_data table")
            
    except Error as e:
        print(f"Error inserting data: {e}")
        if connection:
            connection.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
        if connection:
            connection.rollback()

if __name__ == "__main__":
    # Test the functions
    connection = connect_db()
    if connection:
        create_database(connection)
        connection.close()
        
        connection = connect_to_prodev()
        if connection:
            create_table(connection)
            insert_data(connection, 'user_data.csv')
            connection.close()
