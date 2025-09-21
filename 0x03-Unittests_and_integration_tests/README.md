# 0x03-Unittests_and_integration_tests

This project focuses on understanding and implementing unit tests and integration tests in Python using the `unittest` framework and various testing patterns.

## Learning Objectives

By the end of this project, you should be able to explain:

- The difference between unit and integration tests
- Common testing patterns such as mocking, parametrizations and fixtures
- How to test functions that make external calls (HTTP requests, database calls, etc.)
- How to mock dependencies to isolate unit tests
- How to write parameterized tests for multiple input scenarios

## Project Requirements

### General
- All files will be interpreted/compiled on Ubuntu 18.04 LTS using python3 (version 3.7)
- All files should end with a new line
- The first line of all files should be exactly `#!/usr/bin/env python3`
- Your code should use the pycodestyle style (version 2.5)
- All files must be executable
- All modules should have documentation
- All classes should have documentation  
- All functions (inside and outside a class) should have documentation
- All functions and coroutines must be type-annotated

### Testing
- Execute tests with: `$ python -m unittest path/to/test_file.py`
- Use `unittest.mock` for mocking external dependencies
- Use `parameterized` for parameterized testing
- Focus on testing logic within functions, not external dependencies

## Key Concepts

### Unit Testing
Unit testing focuses on testing individual functions in isolation. External dependencies should be mocked to ensure tests only validate the logic within the function being tested.

### Integration Testing
Integration tests validate that different parts of your application work together correctly. They test complete workflows and typically only mock low-level external services.

### Mocking
Mocking allows you to replace dependencies with fake objects that return predictable values, enabling you to test your code in isolation.

## Files

- `utils.py` - Generic utilities for GitHub org client
- `client.py` - GitHub organization client implementation  
- `fixtures.py` - Test fixtures and sample data
- `test_utils.py` - Unit tests for utils module
- `test_client.py` - Unit and integration tests for client module

## Resources

- [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- [unittest.mock — mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [How to mock a readonly property with mock?](https://stackoverflow.com/questions/11836436/how-to-mock-a-readonly-property-with-mock)
- [parameterized](https://pypi.org/project/parameterized/)
- [Memoization](https://en.wikipedia.org/wiki/Memoization)
