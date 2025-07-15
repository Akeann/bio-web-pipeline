from ..models.user import User

def get_fake_user():
    return User(
        username="testuser",
        full_name="Test User",
        email="testuser@example.com"
    )