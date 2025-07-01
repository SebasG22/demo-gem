from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture()
def session():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop the tables in the test database
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(session):
    # Dependency override
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def test_create_user(client):
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "test@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data


def test_read_users(client):
    client.post("/users/", json={"name": "Test User 1", "email": "test1@example.com"})
    client.post("/users/", json={"name": "Test User 2", "email": "test2@example.com"})

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_read_user(client):
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "test@example.com"},
    )
    user_id = response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert data["id"] == user_id


def test_read_user_not_found(client):
    response = client.get("/users/999")  # Assuming user ID 999 does not exist
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_user_invalid_email(client):
    invalid_emails = ["test.com", "test@", "@test.com", "plainaddress"]
    for email in invalid_emails:
        response = client.post(
            "/users/",
            json={"name": "Test User", "email": email},
        )
        assert response.status_code == 422
