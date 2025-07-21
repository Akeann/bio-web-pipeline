from ..services.password import get_password_hash
from ..config import UsersDB

fake_users_db: UsersDB = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "hashed_password": get_password_hash("testpass")
    }
}