import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from app.main import app, get_db, User
from bson import ObjectId
# Test data
test_user = {
    "username": "testuser",
    "email": "test@example.com"
}

test_product =  {
    "name": "Banana",
    "category": "Fruit",
    "qty": 2
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
    
    
# Test case for creating a new user
@pytest.mark.asyncio
async def test_create_product(mock_db):
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
    response = client.post("/proucts/", json=test_product)

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"id": "12345", "message": "Product created successfully"}

#Sample mock data


# Sample mock data
mock_users_data = [
    {"_id": "60f7a5f4f1d2e91f5f1a254b", "username": "testuser", "email": "test@example.com"},
    {"_id": "60f7a5f4f1d2e91f5f1a254d", "username": "anotheruser", "email": "another@example.com"},
]

# Mock database function for the users collection
@pytest.fixture
def mock_db_client():
    mock_collection = MagicMock()

    # Mocking the find() method to return an async cursor
    mock_cursor = AsyncMock()
    mock_cursor.to_list = AsyncMock(return_value=mock_users_data)
    
    # Mocking find to return our async cursor
    mock_collection.find.return_value = mock_cursor

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection  # db["Users"] should return mock_collection

    return mock_db

# Override the `get_db` dependency with our mock
@pytest.fixture
def app_with_mock_db_client(mock_db_client):
    app.dependency_overrides[get_db] = lambda: mock_db_client
    yield app
    app.dependency_overrides.clear()  # Cleanup after test

# Test for getting all users
@pytest.mark.asyncio
async def test_get_users_endpoint(app_with_mock_db_client):
    # Use TestClient for FastAPI
    client = TestClient(app_with_mock_db_client)
    
    # Call the API to get all users
    response = client.get("/users/")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "60f7a5f4f1d2e91f5f1a254b", "username": "testuser", "email": "test@example.com"},
        {"id": "60f7a5f4f1d2e91f5f1a254d", "username": "anotheruser", "email": "another@example.com"}
    ]

mock_user = {
    "_id": ObjectId("60f7a5f4f1d2e91f5f1a254b"),  # Example ObjectId
    "username": "testuser",
    "email": "test@example.com"
}

# Mock database function
@pytest.fixture
def mock_db():
    mock_collection = MagicMock()
    # Use AsyncMock to mock async methods
    mock_collection.find_one = AsyncMock(return_value=mock_user)

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection  # db["Users"] should return mock_collection

    return mock_db

# Override the `get_db` dependency with our mock
@pytest.fixture
def app_with_mock_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield app
    app.dependency_overrides.clear()  # Cleanup after test

# Test for valid user ID
@pytest.mark.asyncio
async def test_get_user_by_id(app_with_mock_db):
    # Use TestClient for FastAPI
    client = TestClient(app_with_mock_db)
    
    # Valid user ID (ObjectId format)
    valid_user_id = str(mock_user["_id"])

    # Call the API
    response = client.get(f"/user/{valid_user_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": valid_user_id,
        "username": "testuser",
        "email": "test@example.com"
    }

@pytest.mark.asyncio
async def test_get_user_by_id_invalid_format(app_with_mock_db):
    client = TestClient(app_with_mock_db)

    invalid_user_id = "invalid_id_format"

    response = client.get(f"/user/{invalid_user_id}")

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid user ID format"}

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(app_with_mock_db):
    client = TestClient(app_with_mock_db)
    non_existing_user = str(ObjectId())

    # Simulate the DB return None for a non-existing user
    mock_db = app_with_mock_db.dependency_overrides[get_db]  # Get the mock DB
    mock_db().__getitem__().find_one = AsyncMock(return_value=None)

    response = client.get(f"/user/{non_existing_user}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}