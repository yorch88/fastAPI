import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app, get_db, User

# Test data
test_user = {
    "username": "testuser",
    "email": "test@example.com"
}

# Mock the MongoDB client
@pytest.fixture
def mock_db():
    with patch("app.main.AsyncIOMotorClient") as mock_client:
        mock_db = AsyncMock()
        mock_client.return_value = mock_db
        yield mock_db

# Test case for creating a new user
@pytest.mark.asyncio
async def test_create_user(mock_db):
    # Mock the database collection and its methods
    mock_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_collection.find_one.return_value = None  # Simulate no existing user
    mock_collection.insert_one.return_value.inserted_id = "12345"  # Simulate inserted ID

    # Override the get_db dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Create a test client
    client = TestClient(app)

    # Make the request
    response = client.post("/users/", json=test_user)

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"id": "12345", "message": "User created successfully"}

# Test case for creating a user with an existing email
@pytest.mark.asyncio
async def test_create_user_with_existing_email(mock_db):
    # Mock the database collection and its methods
    mock_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_collection.find_one.return_value = {"username": "existinguser", "email": "test@example.com"}  # Simulate existing user

    # Override the get_db dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Create a test client
    client = TestClient(app)

    # Make the request
    response = client.post("/users/", json=test_user)

    # Assertions
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

# Test case for invalid email format
@pytest.mark.asyncio
async def test_create_user_with_invalid_email():
    # Create a test client
    client = TestClient(app)

    # Make the request with invalid email
    invalid_user = {
        "username": "testuser",
        "email": "invalid-email"
    }
    response = client.post("/users/", json=invalid_user)

    # Assertions
    assert response.status_code == 422  # 422 Unprocessable Entity

# Test case for missing required fields
@pytest.mark.asyncio
async def test_create_user_with_missing_fields():
    # Create a test client
    client = TestClient(app)

    # Make the request with missing email field
    incomplete_user = {
        "username": "testuser"
    }
    response = client.post("/users/", json=incomplete_user)

    # Assertions
    assert response.status_code == 422  # 422 Unprocessable Entity
    