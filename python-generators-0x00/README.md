# Python Generators - Advanced Usage Project

## About the Project

This project introduces advanced usage of Python generators to efficiently handle large datasets, process data in batches, and simulate real-world scenarios involving live updates and memory-efficient computations. The tasks focus on leveraging Python's `yield` keyword to implement generators that provide iterative access to data, promoting optimal resource utilization, and improving performance in data-driven applications.

## Learning Objectives

By completing this project, you will:

1. **Master Python Generators**: Learn to create and utilize generators for iterative data processing, enabling memory-efficient operations.
2. **Handle Large Datasets**: Implement batch processing and lazy loading to work with extensive datasets without overloading memory.
3. **Simulate Real-world Scenarios**: Develop solutions to simulate live data updates and apply them to streaming contexts.
4. **Optimize Performance**: Use generators to calculate aggregate functions like averages on large datasets, minimizing memory consumption.
5. **Apply SQL Knowledge**: Use SQL queries to fetch data dynamically, integrating Python with databases for robust data management.

## Project Structure

```
python-generators-0x00/
├── seed.py                 # Database setup and data population script
├── user_data.csv          # Sample data file (to be provided)
├── README.md              # Project documentation
└── 0-main.py              # Test script for seed.py
```

## Task 0: Getting Started with Python Generators

### Objective
Create a generator that streams rows from an SQL database one by one.

### Requirements

#### Database Setup
- **Database Name**: `ALX_prodev`
- **Table Name**: `user_data`

#### Table Schema
- `user_id` (Primary Key, UUID, Indexed)
- `name` (VARCHAR, NOT NULL)
- `email` (VARCHAR, NOT NULL)
- `age` (DECIMAL, NOT NULL)

#### Required Functions

1. **`connect_db()`** - Connects to the MySQL database server
2. **`create_database(connection)`** - Creates the database `ALX_prodev` if it does not exist
3. **`connect_to_prodev()`** - Connects to the ALX_prodev database in MySQL
4. **`create_table(connection)`** - Creates table `user_data` if it doesn't exist with required fields
5. **`insert_data(connection, data)`** - Inserts data in the database if it doesn't exist

### Prerequisites

#### System Requirements
- Python 3.x
- MySQL Server
- Required Python packages:
  ```bash
  pip install mysql-connector-python
  ```

#### MySQL Setup
1. Install MySQL server on your system
2. Start MySQL service
3. Create a user account or use existing credentials
4. Update the connection parameters in `seed.py`:
   ```python
   # Update these with your MySQL credentials
   user='your_mysql_username'
   password='your_mysql_password'
   ```

### Usage

#### Basic Usage
```bash
# Make the script executable
chmod +x seed.py

# Run the seed script
python3 seed.py

# Or run the test script
python3 0-main.py
```

#### Expected Output
```
connection successful
Table user_data created successfully
Database ALX_prodev is present 
[('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67), ...]
```

### Features

- **Error Handling**: Comprehensive error handling for database operations
- **Data Validation**: Validates CSV data before insertion
- **Duplicate Prevention**: Checks if data already exists before insertion
- **UUID Generation**: Automatically generates UUIDs for user_id if not provided
- **Flexible CSV Reading**: Handles various CSV formats and encodings

### File Structure Details

#### seed.py
The main database setup script containing all required functions for database initialization and data population.

#### user_data.csv
Sample data file containing user information. Should include columns for name, email, and age (user_id will be auto-generated if not provided).

### Troubleshooting

#### Common Issues

1. **MySQL Connection Error**
   - Verify MySQL server is running
   - Check username and password in the script
   - Ensure MySQL server is accessible on localhost

2. **Permission Denied**
   - Make sure your MySQL user has CREATE DATABASE privileges
   - Grant necessary permissions: `GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost';`

3. **CSV File Not Found**
   - Ensure `user_data.csv` exists in the same directory
   - Check file permissions and encoding

4. **Import Errors**
   - Install required packages: `pip install mysql-connector-python`
   - Verify Python version compatibility

### Next Steps

This is the foundation for the advanced Python generators project. Future tasks will build upon this database setup to implement:
- Memory-efficient data streaming with generators
- Batch processing for large datasets
- Real-time data simulation
- Advanced aggregation functions using generators

## Repository Information

- **GitHub repository**: `alx-backend-python`
- **Directory**: `python-generators-0x00`
- **Files**: `seed.py`, `README.md`
