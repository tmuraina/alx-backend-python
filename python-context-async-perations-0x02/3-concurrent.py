#!/usr/bin/env python3
"""
Concurrent Asynchronous Database Queries with aiosqlite.

This module demonstrates advanced Python techniques for executing multiple
database queries concurrently using asyncio and aiosqlite. It showcases
how to improve performance by running independent queries simultaneously
rather than sequentially.
"""

import asyncio
import aiosqlite
import sqlite3
import os
import time
from typing import List, Tuple


async def async_fetch_users() -> List[Tuple]:
    """
    Asynchronously fetch all users from the database.
    
    This function opens an asynchronous connection to the SQLite database,
    executes a query to fetch all users, and returns the results.
    
    Returns:
        List[Tuple]: A list of tuples containing user data (id, name, email, age)
    """
    db_name = "sample_database.db"
    
    try:
        print("🔍 Starting async_fetch_users...")
        start_time = time.time()
        
        # Open asynchronous database connection
        async with aiosqlite.connect(db_name) as db:
            # Execute query to fetch all users
            async with db.execute("SELECT * FROM users ORDER BY name") as cursor:
                users = await cursor.fetchall()
                
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ async_fetch_users completed in {execution_time:.4f} seconds")
        print(f"   Retrieved {len(users)} users")
        
        return users
        
    except Exception as e:
        print(f"❌ Error in async_fetch_users: {e}")
        return []


async def async_fetch_older_users() -> List[Tuple]:
    """
    Asynchronously fetch users older than 40 from the database.
    
    This function opens an asynchronous connection to the SQLite database,
    executes a parameterized query to fetch users older than 40, and
    returns the results.
    
    Returns:
        List[Tuple]: A list of tuples containing user data for users older than 40
    """
    db_name = "sample_database.db"
    age_threshold = 40
    
    try:
        print("🔍 Starting async_fetch_older_users...")
        start_time = time.time()
        
        # Open asynchronous database connection
        async with aiosqlite.connect(db_name) as db:
            # Execute parameterized query to fetch users older than 40
            async with db.execute(
                "SELECT * FROM users WHERE age > ? ORDER BY age DESC", 
                (age_threshold,)
            ) as cursor:
                older_users = await cursor.fetchall()
                
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ async_fetch_older_users completed in {execution_time:.4f} seconds")
        print(f"   Retrieved {len(older_users)} users older than {age_threshold}")
        
        return older_users
        
    except Exception as e:
        print(f"❌ Error in async_fetch_older_users: {e}")
        return []


async def fetch_concurrently():
    """
    Execute multiple database queries concurrently using asyncio.gather().
    
    This function demonstrates concurrent execution of multiple asynchronous
    database queries. It uses asyncio.gather() to run both queries simultaneously,
    significantly reducing total execution time compared to sequential execution.
    
    Returns:
        Tuple[List[Tuple], List[Tuple]]: A tuple containing results from both queries
    """
    print("\n" + "="*70)
    print("🚀 STARTING CONCURRENT ASYNCHRONOUS DATABASE QUERIES")
    print("="*70)
    
    overall_start_time = time.time()
    
    try:
        # Execute both queries concurrently using asyncio.gather()
        print("\n📊 Executing queries concurrently...")
        print("-" * 50)
        
        # asyncio.gather() runs both coroutines concurrently
        all_users, older_users = await asyncio.gather(
            async_fetch_users(),
            async_fetch_older_users()
        )
        
        overall_end_time = time.time()
        total_execution_time = overall_end_time - overall_start_time
        
        print(f"\n🎉 All concurrent queries completed!")
        print(f"⏱️  Total execution time: {total_execution_time:.4f} seconds")
        
        return all_users, older_users
        
    except Exception as e:
        print(f"❌ Error during concurrent execution: {e}")
        return [], []


async def demonstrate_sequential_vs_concurrent():
    """
    Demonstrate the performance difference between sequential and concurrent execution.
    
    This function runs the same queries both sequentially and concurrently
    to showcase the performance benefits of asynchronous concurrent execution.
    """
    print("\n" + "="*70)
    print("⚡ PERFORMANCE COMPARISON: SEQUENTIAL vs CONCURRENT")
    print("="*70)
    
    # Sequential execution
    print("\n1️⃣ SEQUENTIAL EXECUTION")
    print("-" * 30)
    
    sequential_start = time.time()
    
    # Run queries one after another
    users_seq = await async_fetch_users()
    older_users_seq = await async_fetch_older_users()
    
    sequential_end = time.time()
    sequential_time = sequential_end - sequential_start
    
    print(f"⏱️  Sequential execution time: {sequential_time:.4f} seconds")
    
    # Concurrent execution
    print("\n2️⃣ CONCURRENT EXECUTION")
    print("-" * 30)
    
    concurrent_start = time.time()
    
    # Run queries concurrently
    users_conc, older_users_conc = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    concurrent_end = time.time()
    concurrent_time = concurrent_end - concurrent_start
    
    print(f"⏱️  Concurrent execution time: {concurrent_time:.4f} seconds")
    
    # Calculate performance improvement
    if concurrent_time > 0:
        speedup = sequential_time / concurrent_time
        improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
        
        print(f"\n📈 PERFORMANCE ANALYSIS")
        print("-" * 25)
        print(f"🚀 Speedup factor: {speedup:.2f}x")
        print(f"⚡ Performance improvement: {improvement:.1f}%")
    
    return (users_seq, older_users_seq), (users_conc, older_users_conc)


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
            ('Julia Kim', 'julia@example.com', 29),
            ('Kevin Brown', 'kevin@example.com', 48),
            ('Laura White', 'laura@example.com', 52),
            ('Michael Chen', 'michael@example.com', 41),
            ('Nancy Taylor', 'nancy@example.com', 38),
            ('Oliver Jones', 'oliver@example.com', 45),
            ('Patricia Wilson', 'patricia@example.com', 50),
            ('Quinn Davis', 'quinn@example.com', 27),
            ('Rachel Green', 'rachel@example.com', 43),
            ('Samuel Lee', 'samuel@example.com', 31),
            ('Tina Martinez', 'tina@example.com', 46)
        ]
        
        # Clear existing data and insert fresh sample data
        cursor.execute('DELETE FROM users')
        cursor.executemany(
            'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
            sample_users
        )
        
        conn.commit()
        conn.close()
        print(f"📊 Sample database '{db_name}' created with {len(sample_users)} users")
        
    except sqlite3.Error as e:
        print(f"❌ Error setting up sample database: {e}")


def display_results(results, title="Query Results"):
    """
    Display query results in a formatted table.
    
    Args:
        results (List[Tuple]): List of result tuples from the database query
        title (str): Title for the results display
    """
    print(f"\n📋 {title}")
    print("=" * len(f"📋 {title}"))
    
    if results:
        print(f"{'ID':<5} {'Name':<15} {'Email':<25} {'Age':<5}")
        print("-" * 55)
        for row in results:
            print(f"{row[0]:<5} {row[1]:<15} {row[2]:<25} {row[3] or 'N/A':<5}")
        print(f"\nTotal records: {len(results)}")
    else:
        print("No results found.")
    print()


async def main():
    """
    Main function to demonstrate concurrent asynchronous database queries.
    """
    db_name = "sample_database.db"
    
    # Setup sample database with users table
    setup_sample_database(db_name)
    
    try:
        # 1. Demonstrate basic concurrent execution
        all_users, older_users = await fetch_concurrently()
        
        # Display results
        display_results(all_users, "All Users (Concurrent Query)")
        display_results(older_users, "Users Older than 40 (Concurrent Query)")
        
        # 2. Demonstrate performance comparison
        await demonstrate_sequential_vs_concurrent()
        
        # 3. Additional demonstration with error handling
        print("\n" + "="*70)
        print("🛡️  DEMONSTRATING ERROR HANDLING")
        print("="*70)
        
        try:
            # This will work fine
            results = await asyncio.gather(
                async_fetch_users(),
                async_fetch_older_users(),
                return_exceptions=True  # Continue even if one query fails
            )
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"❌ Query {i+1} failed: {result}")
                else:
                    print(f"✅ Query {i+1} succeeded with {len(result)} results")
                    
        except Exception as e:
            print(f"❌ Error in error handling demonstration: {e}")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
    
    finally:
        # Cleanup: Remove the sample database file
        if os.path.exists(db_name):
            os.remove(db_name)
            print(f"\n🧹 Sample database '{db_name}' removed")


if __name__ == "__main__":
    # Run the main async function using asyncio.run()
    print("🎯 Starting Concurrent Asynchronous Database Queries Demo")
    print("📚 Using aiosqlite and asyncio.gather() for concurrent execution")
    
    # This is the required call as specified in the instructions
    asyncio.run(main())  # Note: main() calls fetch_concurrently() internally
