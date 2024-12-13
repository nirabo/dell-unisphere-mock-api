# Dell Unity™ Unisphere® Management REST API Mock

This is a mock implementation of the Dell Unity Unisphere Management REST API using FastAPI.

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Start the API server:
```bash
cd app
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## Authentication

The mock API implements token-based authentication. Default credentials:
- Username: `admin`
- Password: `admin`

## Available Endpoints

1. **Login**
   - POST `/api/types/loginSessionInfo/action/login`
   - Authenticates user and returns access token

2. **System Information**
   - GET `/api/types/system/instances`
   - Returns basic system information

3. **System Details**
   - GET `/api/instances/system/0`
   - Returns detailed system information

## Security Note

This is a mock implementation for development and testing purposes. The security implementations (secret keys, passwords) are not suitable for production use.
