# **Coding Conventions for Dell Unisphere Mock API**

This document outlines the coding conventions and best practices to ensure consistency and maintainability across the Dell Unisphere Mock API project.

---

## **General Guidelines**
- **Language**: Python 3.12+
- **Code Style**: Follow [PEP 8](https://peps.python.org/pep-0008/) guidelines.
- **Type Hints**: Use type hints for all function definitions and return types.
- **Imports**: Group imports in the following order:
  1. Standard library imports
  2. Third-party library imports
  3. Local application imports
  Use absolute imports for clarity.

---

## **Authentication and Security**
- **Authentication**:
  - Use `HTTPBasic` for basic authentication.
  - Always validate the `X-EMC-REST-CLIENT` header for non-Swagger requests.
  - Generate CSRF tokens for POST, PATCH, and DELETE requests.
- **Cookies**:
  - Use `httponly`, `secure`, and `samesite="lax"` for cookies.
  - Store session tokens securely.
- **Error Handling**:
  - Raise `HTTPException` with appropriate status codes for authentication failures.
  - Include detailed error messages for debugging.

---

## **Model Layer**
- **Singleton Pattern**:
  - Use the singleton pattern for models that manage shared state (e.g., `PoolModel`).
  - Initialize shared state in `__new__` to ensure thread safety.
- **CRUD Operations**:
  - Implement `create`, `read`, `update`, and `delete` methods for all models.
  - Use `Optional` for return types when an entity might not exist.
- **Validation**:
  - Use Pydantic models for input validation.
  - Validate all inputs before processing.

---

## **Controllers and Routers**
- **Async Support**:
  - Use `async/await` for I/O-bound operations.
  - Use `BackgroundTasks` for long-running tasks.
- **Endpoint Design**:
  - Use descriptive endpoint paths (e.g., `/types/pool/instances`).
  - Support pagination, filtering, and sorting for list endpoints.
  - Use `Query` parameters for optional filters (e.g., `compact`, `fields`).
- **Response Format**:
  - Return JSON responses with consistent structure (e.g., `@base`, `entries`, `links`).
  - Use `JSONResponse` for custom response formatting.

---

## **Testing**
- **Unit Tests**:
  - Write tests for all new functionality.
  - Use `pytest` as the testing framework.
  - Prefix test functions with `test_`.
- **Mocking**:
  - Use `unittest.mock` for mocking external dependencies.
  - Mock authentication and database interactions in tests.
- **Coverage**:
  - Aim for 100% test coverage for critical components.
  - Use `pytest-cov` for coverage reporting.

---

## **Configuration**
- **Environment Variables**:
  - Use `pydantic_settings` for managing configuration.
  - Prefix environment variables with `UNISPHERE_`.
  - Store sensitive data in `.env` files (excluded from version control).
- **Settings**:
  - Define settings in `core/config.py`.
  - Use `BaseSettings` for configuration models.

---

## **Error Handling**
- **HTTP Errors**:
  - Use appropriate HTTP status codes (e.g., 404 for not found, 401 for unauthorized).
  - Include detailed error messages in responses.
- **Validation Errors**:
  - Use Pydantic's built-in validation for input data.
  - Return 400 for invalid requests.

---

## **Documentation**
- **API Docs**:
  - Use FastAPI's automatic Swagger and ReDoc documentation.
  - Add detailed docstrings to all endpoints.
- **Code Comments**:
  - Use comments sparingly; prefer self-documenting code.
  - Add comments for complex logic or non-obvious decisions.
- **README**:
  - Keep the README updated with installation, usage, and contribution instructions.

---

## **Example Code Snippet**

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Item(BaseModel):
    name: str
    description: str | None = None

@router.post("/items/", response_model=Item)
async def create_item(item: Item):
    """Create a new item."""
    if item.name == "invalid":
        raise HTTPException(status_code=400, detail="Invalid item name")
    return item
```

---

## **Best Practices**
1. **Keep It Simple**: Avoid over-engineering; prefer simple, readable code.
2. **DRY Principle**: Reuse code where possible; avoid duplication.
3. **Consistency**: Follow the same patterns across the codebase.
4. **Security First**: Always validate inputs and handle errors gracefully.
5. **Test Everything**: Write tests for all new features and bug fixes.
