#!/usr/bin/python3
seed = __import__('seed')


def stream_user_ages():
    """
    Generator that yields user ages one by one
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")
    for row in cursor:
        yield row["age"]   # ✅ yields ages one by one
    connection.close()


def average_user_age():
    """
    Calculate average age without loading all data into memory
    """
    total = 0
    count = 0
    for age in stream_user_ages():   # ✅ one loop
        total += age
        count += 1

    if count > 0:
        avg = total / count
        print(f"Average age of users: {avg:.2f}")
    else:
        print("No users found")
