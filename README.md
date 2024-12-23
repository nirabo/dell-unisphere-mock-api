# Dell Unisphere Mock API

> **IMPORTANT DISCLAIMER**  
> This codebase is entirely generated using artificial intelligence.  
> Users shall use it at their own risk.  
> The authors make no warranties about the completeness, reliability, and accuracy of this code.  
> Any action you take upon this code is strictly at your own risk.

A FastAPI-based mock implementation of the Dell EMC Unisphere REST API for testing and development purposes.

[![Tests](https://github.com/YOUR_USERNAME/dell-unisphere-mock-api/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/dell-unisphere-mock-api/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/dell-unisphere-mock-api/branch/master/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/dell-unisphere-mock-api)

## Features

- Mock implementation of Dell EMC Unisphere REST API endpoints
- Support for basic authentication and CSRF token management
- Comprehensive test suite with high coverage
- Storage resource management (pools, LUNs, filesystems, etc.)
- Pagination and sorting support
- Based on FastAPI for modern async API development

## Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

For development:
```bash
pip install -r requirements-test.txt
```

## Running Tests

```bash
make test
```

This will:
- Create a test virtual environment
- Install test dependencies
- Run pytest with coverage reporting

## Development

### Project Structure

```
dell_unisphere_mock_api/
├── core/           # Core functionality (auth, etc.)
├── models/         # Data models
├── routers/        # API route handlers
└── schemas/        # Pydantic schemas
```

### Testing

The project uses pytest for testing and includes:
- Unit tests for all components
- Integration tests based on Dell EMC Unisphere API tutorials
- Coverage reporting
- CI/CD integration with both GitHub Actions and GitLab CI

### CI/CD

The project is configured with:

#### GitHub Actions
- Runs tests on Python 3.12
- Automated testing on pull requests and master branch
- Coverage reporting via Codecov
- Dependency caching for faster builds

#### GitLab CI
- Parallel CI pipeline configuration
- Built-in coverage reporting
- Caching of pip packages and virtualenv
- Runs on merge requests and master branch

## API Documentation

When running locally, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
