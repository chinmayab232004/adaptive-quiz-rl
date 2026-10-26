"""
Authentication and User Management Module.
Handles registration, secure salted password hashing, authentication, and session state.
"""

import hashlib
import os
import re
from typing import Dict, Optional, Tuple, Any
from database.db import execute_insert, execute_query_one, execute_update
import config

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hashes a password with SHA-256 and a random cryptographic salt.
    Returns: (password_hash, salt)
    """
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return hashed, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies a plain-text password against stored hash and salt."""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == stored_hash

def register_user(name: str, email: str, password: str, role: str = "student") -> Tuple[bool, str, Optional[int]]:
    """
    Registers a new student or administrator.
    Returns: (success: bool, message: str, user_id: Optional[int])
    """
    name = name.strip()
    email = email.strip().lower()

    # Validation
    if not name or len(name) < 2:
        return False, "Name must be at least 2 characters long.", None
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Please provide a valid email address.", None
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    # Check for existing email or duplicate name if relevant
    existing = execute_query_one(
        "SELECT id, email FROM users WHERE email = ?",
        (email,)
    )
    if existing:
        return False, "Email address is already registered. Please sign in.", None

    # Hash and insert
    pwd_hash, salt = hash_password(password)
    user_id = execute_insert(
        """
        INSERT INTO users (name, email, password_hash, salt, role)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, email, pwd_hash, salt, role)
    )

    return True, "Registration successful! You can now log in.", user_id

def authenticate_user(login_identifier: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticates a user by email or name.
    Supports default admin username 'admin' as well as email.
    Returns: (success: bool, message: str, user_dict: Optional[dict])
    """
    ident = login_identifier.strip().lower()
    if not ident or not password:
        return False, "Please enter both credentials.", None

    # Support admin username shorthand
    if ident == "admin":
        user = execute_query_one(
            "SELECT id, name, email, password_hash, salt, role FROM users WHERE email = ? OR role = 'admin'",
            (config.DEFAULT_ADMIN_EMAIL,)
        )
    else:
        user = execute_query_one(
            "SELECT id, name, email, password_hash, salt, role FROM users WHERE LOWER(email) = ? OR LOWER(name) = ?",
            (ident, ident)
        )

    if not user:
        return False, "Invalid email/username or password.", None

    if not verify_password(password, user["password_hash"], user["salt"]):
        return False, "Invalid email/username or password.", None

    user_info = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }
    return True, "Login successful!", user_info

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves user profile details by ID."""
    user = execute_query_one(
        "SELECT id, name, email, role, created_at FROM users WHERE id = ?",
        (user_id,)
    )
    if user:
        return dict(user)
    return None

def update_user_profile(user_id: int, name: str, email: str, new_password: Optional[str] = None) -> Tuple[bool, str]:
    """Updates user profile information and optionally password."""
    name = name.strip()
    email = email.strip().lower()

    if not name or not email:
        return False, "Name and email cannot be blank."

    conflict = execute_query_one(
        "SELECT id FROM users WHERE email = ? AND id != ?",
        (email, user_id)
    )
    if conflict:
        return False, "Email address is already in use by another account."

    if new_password:
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters."
        pwd_hash, salt = hash_password(new_password)
        execute_update(
            "UPDATE users SET name = ?, email = ?, password_hash = ?, salt = ? WHERE id = ?",
            (name, email, pwd_hash, salt, user_id)
        )
    else:
        execute_update(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, user_id)
        )

    return True, "Profile updated successfully."
