#!/usr/bin/python3
import sqlite3

def stream_users_in_batches(batch_size):
    """
    Generator to fetch users from user_data table in batches
    """
    conn = sqlite3.connect("users.db")   # DB file
    conn.row_factory = sqlite3.Row       # dict-like rows
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_data")   # ✅ use user_data

    while True:
        rows = cur.fetchmany(batch_size)
        if not rows:
            break
        yield [dict(row) for row in rows]    # ✅ yield, not return

    conn.close()


def batch_processing(batch_size):
    """
    Process user batches: filter users over age 25
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user["age"] > 25:
                print(user)
