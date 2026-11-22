"""Group F - Authentication module: basic login system.

NOTE: SHA-256 is used to keep the project dependency-free. Real systems
should use a salted password hash such as bcrypt or argon2.
"""
import hashlib

LIBRARIAN = "librarian"
MEMBER = "member"


def hash_password(password):
    """Return the SHA-256 hex digest of a password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(user_db, username, password, role=MEMBER, member_id=None):
    """Create a user. Raises ValueError if the username exists or role is invalid.

    user_db format: {username: {"password": <hash>, "role": str, "member_id": str|None}}
    """
    if username in user_db:
        raise ValueError(f"User '{username}' already exists")
    if role not in (LIBRARIAN, MEMBER):
        raise ValueError("role must be 'librarian' or 'member'")
    user_db[username] = {
        "password": hash_password(password),
        "role": role,
        "member_id": member_id,
    }


def authenticate(username, password, user_db):
    """Return True if the username/password pair is valid."""
    user = user_db.get(username)
    return user is not None and user["password"] == hash_password(password)


def get_user(username, user_db):
    """Return the user record dict for a username, or None."""
    return user_db.get(username)
