from repository.users_repo import (
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
)


def test_create_user_and_get_by_id(app):
    with app.app_context():
        user_id = create_user("u@example.com", "hash123", name="User One")
        assert isinstance(user_id, int) and user_id > 0, "User ID should be a positive integer"
        u = get_user_by_id(user_id)
        assert u is not None, "User should be retrievable by ID"
        assert u["email"] == "u@example.com", "User email should match"
        assert u["name"] == "User One", "User name should match"
        assert u["role"] == "user", "User role should match"


def test_get_user_by_email(app):
    with app.app_context():
        user_id = create_user("u2@example.com", "hash456", name="User Two")
        u = get_user_by_email("u2@example.com")
        assert u is not None and u["id"] == user_id, "User should be retrievable by email"


def test_update_user(app):
    with app.app_context():
        user_id = create_user("u3@example.com", "hash789", name="User Three")
        assert update_user(user_id, name="User 3", role="admin") is True, "User update should return True"
        u = get_user_by_id(user_id)
        assert u["name"] == "User 3", "User name should be updated"
        assert u["role"] == "admin", "User role should be updated"


def test_delete_user(app):
    with app.app_context():
        user_id = create_user("u4@example.com", "hash000", name="User Four")
        assert delete_user(user_id) is True, "User deletion should return True"
        assert get_user_by_id(user_id) is None, "Deleted user should not be retrievable"
