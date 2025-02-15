#conftest.py

import pytest
import mongomock

from app.main import create_user

@pytest.fixture()
def mongo_mock(monkeypatch):
    client = mongomock.MongoClient()
    db = client.get_database("mydatabase_new")
    col = db.get_collection("Users")
    emp_data: create_user = {
        "username": "test_user",
        "email": "test_user@gmail.com"
    }

    col.insert_one(emp_data)

    def fake_db():
        return db

    monkeypatch.setattr("app.main.get_db", fake_db)
