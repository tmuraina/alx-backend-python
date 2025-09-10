import time
import sqlite3 
import functools

def with_db_connection(func):
    """Decorator that automatically handles database connection opening and closing."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection
            conn.close()
    
    return wrapper

query_cache = {}

def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    Subsequent calls with the same query will return cached results.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        query = None
        
        # Check if query is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if query is in positional arguments (usually second argument after conn)
        elif len(args) > 1:
            query = args[1]
        
        # If we have a query, check the cache
        if query:
            # Check if this query result is already cached
            if query in query_cache:
                print(f"Cache hit! Returning cached result for query: {query}")
                return query_cache[query]
            
            # If not in cache, execute the function
            print(f"Cache miss! Executing query: {query}")
            result = func(*args, **kwargs)
            
            # Store the result in cache
            query_cache[query] = result
            return result
        else:
            # If no query found, just execute the function without caching
            return func(*args, **kwargs)
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")
print(f"First call result: {len(users) if users else 0} users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Second call result: {len(users_again) if users_again else 0} users")
