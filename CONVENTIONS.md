# Coding Conventions for Aider

This document outlines the coding conventions to be followed when using Aider for code generation and editing.

## General Guidelines
- **Language**: Python
- **Code Style**: Follow PEP 8 guidelines for Python code.
- **Type Hints**: Use type hints for all function definitions.

## Libraries and Packages
- **HTTP Requests**: Prefer using `httpx` over `requests` for making HTTP requests.
- **Logging**: Utilize the built-in `logging` module instead of print statements.

## Function Definitions
- All functions should have a docstring explaining their purpose, parameters, and return values.
- Use descriptive names for functions and variables.

## Testing Conventions
- Write unit tests for all new features.
- Use `pytest` as the testing framework.
- Each test function should start with the prefix `test_`.

## Error Handling
- Use exceptions to handle errors gracefully.
- Avoid using bare `except:` clauses; specify the exception type.

## Code Organization
- Structure code into modules with a clear separation of concerns.
- Group related functions into classes where applicable.

## Example Code Snippet
