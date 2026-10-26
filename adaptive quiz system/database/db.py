"""
Database management module for SQLite.
Handles connection pooling, table initialization, and atomic transactions.
"""

import sqlite3
import hashlib
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import config

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(str(config.DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(force: bool = False) -> None:
    """Initializes the database schema if not present, and seeds default admin and questions."""
    db_exists = config.DATABASE_PATH.exists()
    
    if force and db_exists:
        try:
            config.DATABASE_PATH.unlink()
            db_exists = False
        except Exception:
            pass

    conn = get_connection()
    try:
        with open(config.SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

    # Seed default admin user and sample questions
    seed_default_admin()
    seed_sample_questions()

def seed_default_admin() -> None:
    """Seeds the default administrator account if none exists."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? OR name = ?", (config.DEFAULT_ADMIN_EMAIL, config.DEFAULT_ADMIN_USERNAME))
        row = cursor.fetchone()
        if not row:
            salt = os.urandom(16).hex()
            # SHA-256 hash with salt
            password_hash = hashlib.sha256((config.DEFAULT_ADMIN_PASSWORD + salt).encode("utf-8")).hexdigest()
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash, salt, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "System Administrator",
                    config.DEFAULT_ADMIN_EMAIL,
                    password_hash,
                    salt,
                    "admin",
                )
            )
            conn.commit()
    finally:
        conn.close()

def seed_sample_questions(force_reload: bool = False) -> None:
    """Loads sample questions from data/sample_questions.json with INSERT OR IGNORE to prevent duplicates."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM questions")
        count = cursor.fetchone()["count"]
        
        # Reseed if forced or if fewer than 150 questions exist
        if (force_reload or count < 150) and config.SAMPLE_QUESTIONS_PATH.exists():
            with open(config.SAMPLE_QUESTIONS_PATH, "r", encoding="utf-8") as f:
                questions_data = json.load(f)
            
            if force_reload:
                cursor.execute("DELETE FROM questions")

            for q in questions_data:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO questions (subject, topic, question, option_a, option_b, option_c, option_d, correct_answer, difficulty, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        q["subject"].strip(),
                        q.get("topic", "General").strip(),
                        q["question"].strip(),
                        q["option_a"].strip(),
                        q["option_b"].strip(),
                        q["option_c"].strip(),
                        q["option_d"].strip(),
                        q["correct_answer"].strip().upper(),
                        q["difficulty"].strip().upper(),
                        q.get("explanation", "No explanation available.").strip()
                    )
                )
            conn.commit()
    finally:
        conn.close()

def execute_query(query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
    """Executes a SELECT query and returns all matching rows."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()

def execute_query_one(query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
    """Executes a SELECT query and returns a single row."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        conn.close()

def execute_insert(query: str, params: Tuple[Any, ...] = ()) -> int:
    """Executes an INSERT query and returns the newly inserted row ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def execute_update(query: str, params: Tuple[Any, ...] = ()) -> int:
    """Executes an UPDATE or DELETE query and returns the count of affected rows."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
