# Dell Unisphere Mock API

> **IMPORTANT DISCLAIMER**  
> This codebase is entirely generated using artificial intelligence.  
> Users shall use it at their own risk.  
> The authors make no warranties about the completeness, reliability, and accuracy of this code.  
> Any action you take upon this code is strictly at your own risk.

A FastAPI-based mock implementation of the Dell EMC Unisphere REST API for testing and development purposes.

[![Tests](https://github.com/YOUR_USERNAME/dell-unisphere-mock-api/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/dell-unisphere-mock-api/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/dell-unisphere-mock-api/branch/master/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/dell-unisphere-mock-api)
[![PyPI version](https://badge.fury.io/py/dell-unisphere-mock-api.svg)](https://badge.fury.io/py/dell-unisphere-mock-api)
[![Python Version](https://img.shields.io/pypi/pyversions/dell-unisphere-mock-api.svg)](https://pypi.org/project/dell-unisphere-mock-api/)

## Features

- Mock implementation of Dell EMC Unisphere REST API endpoints
- Support for basic authentication and CSRF token management
- Comprehensive test suite with high coverage
- Storage resource management (pools, LUNs, filesystems, etc.)
- Pagination and sorting support
- Based on FastAPI for modern async API development

## Installation

### From PyPI

```bash
pip install dell-unisphere-mock-api
```

For development features:
```bash
pip install "dell-unisphere-mock-api[test]"
```

### From Source

```bash
git clone https://github.com/YOUR_USERNAME/dell-unisphere-mock-api.git
cd dell-unisphere-mock-api
make venv  # Creates virtual environment and installs package in editable mode
```

## Usage

### Running the Server

```bash
# If installed from PyPI
python -m dell_unisphere_mock_api

# If installed from source
make run
```

The server will start at `http://localhost:8000`

## Development

### Project Structure

```
dell_unisphere_mock_api/
├── core/           # Core functionality (auth, etc.)
├── models/         # Data models
├── routers/        # API route handlers
└── schemas/        # Pydantic schemas
```

### Common Tasks

```bash
make help          # Show all available commands
make test          # Run tests with coverage
make clean         # Clean all build and test artifacts
make build         # Build source and wheel package
make release       # Upload to PyPI (maintainers only)
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
- Automated PyPI releases on tags

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
