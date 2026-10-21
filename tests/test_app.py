
import sys
from pathlib import Path

# Add the main project folder to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import database

# Use a separate database for testing.
database.DATABASE = PROJECT_ROOT / "tests" / "test_college_lab.db"

from app import app
from database import get_db_connection, init_db


# Initialize the test database.
init_db()

app.config.update(
    TESTING=True,
    SECRET_KEY="test-secret-key"
)


def reset_database():
    connection = get_db_connection()
    try:
        connection.execute("DELETE FROM bookings")
        connection.execute("DELETE FROM users")
        connection.commit()
    finally:
        connection.close()


def setup_function():
    reset_database()


def teardown_function():
    reset_database()


def test_home_page():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200


def test_equipment_page():
    client = app.test_client()
    response = client.get("/equipment")

    assert response.status_code == 200
    assert b"Arduino Kit" in response.data


def test_dashboard_requires_login():
    client = app.test_client()
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/login" in response.location


def test_booking_requires_login():
    client = app.test_client()
    response = client.get("/book/1")

    assert response.status_code == 302
    assert "/login" in response.location


def test_student_registration():
    client = app.test_client()

    response = client.post(
        "/register",
        data={
            "name": "Test Student",
            "email": "student@example.com",
            "password": "TestPass123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    connection = get_db_connection()
    try:
        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            ("student@example.com",)
        ).fetchone()
    finally:
        connection.close()

    assert user is not None


def test_student_login():
    client = app.test_client()

    client.post(
        "/register",
        data={
            "name": "Test Student",
            "email": "student@example.com",
            "password": "TestPass123"
        }
    )

    response = client.post(
        "/login",
        data={
            "email": "student@example.com",
            "password": "TestPass123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" in session
