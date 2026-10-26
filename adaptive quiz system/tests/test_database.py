"""
Unit Tests for Database, Authentication, and Question Management.
"""

import unittest
import uuid
from database.db import init_db, execute_query_one
from auth.authentication import (
    register_user,
    authenticate_user,
    verify_password,
    hash_password,
    get_user_by_id
)
from quiz.question_manager import (
    add_question,
    get_question_by_id,
    update_question,
    delete_question,
    get_all_questions,
    get_question_stats
)

class TestDatabaseAndAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_password_hashing_and_verification(self):
        """Tests that password hashing generates secure salted hashes."""
        pwd = "SecretPassword123!"
        hashed, salt = hash_password(pwd)
        self.assertTrue(verify_password(pwd, hashed, salt))
        self.assertFalse(verify_password("WrongPassword", hashed, salt))

    def test_user_registration_and_auth(self):
        """Tests student registration, uniqueness constraints, and login."""
        unique_suffix = uuid.uuid4().hex[:8]
        email = f"student_{unique_suffix}@student.edu"
        password = "studentpassword123"

        ok, msg, uid = register_user("Test Student", email, password, role="student")
        self.assertTrue(ok)
        self.assertIsNotNone(uid)

        # Duplicate email should fail
        dup_ok, dup_msg, _ = register_user("Another Student", email, password)
        self.assertFalse(dup_ok)

        # Successful auth
        auth_ok, auth_msg, udict = authenticate_user(email, password)
        self.assertTrue(auth_ok)
        self.assertEqual(udict["email"], email)

        # Failed auth
        bad_ok, _, _ = authenticate_user(email, "WrongPassword")
        self.assertFalse(bad_ok)

    def test_question_crud(self):
        """Tests question creation, update, and deletion in SQLite."""
        ok, msg, qid = add_question(
            subject="Python Programming",
            topic="Style Guidelines",
            question="What is PEP 8 in Python?",
            option_a="A game engine",
            option_b="The official Python Style Guide",
            option_c="A database connector",
            option_d="A compiler flag",
            correct_answer="B",
            difficulty="EASY",
            explanation="PEP 8 provides coding conventions for Python code."
        )
        self.assertTrue(ok)
        self.assertIsNotNone(qid)

        # Read
        q = get_question_by_id(qid)
        self.assertIsNotNone(q)
        self.assertEqual(q["correct_answer"], "B")

        # Update
        up_ok, up_msg = update_question(
            question_id=qid,
            subject="Python Programming",
            topic="Style Guidelines",
            question="What is PEP 8 in Python? (Updated)",
            option_a="A game engine",
            option_b="The official Python Style Guide",
            option_c="A database connector",
            option_d="A compiler flag",
            correct_answer="B",
            difficulty="MEDIUM",
            explanation="PEP 8 is Python's style guide."
        )
        self.assertTrue(up_ok)
        q_updated = get_question_by_id(qid)
        self.assertEqual(q_updated["difficulty"], "MEDIUM")

        # Delete
        del_ok, _ = delete_question(qid)
        self.assertTrue(del_ok)
        self.assertIsNone(get_question_by_id(qid))

    def test_question_bank_size(self):
        """Verifies the question bank has at least 100 sample questions."""
        stats = get_question_stats()
        self.assertGreaterEqual(stats["total_questions"], 100)
        self.assertIn("Python Programming", stats["by_subject"])
        self.assertIn("EASY", stats["by_difficulty"])
        self.assertIn("MEDIUM", stats["by_difficulty"])
        self.assertIn("HARD", stats["by_difficulty"])

if __name__ == "__main__":
    unittest.main()
