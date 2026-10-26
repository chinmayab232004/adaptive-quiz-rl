"""
Unit Tests for Quiz Engine and Session Execution.
Verifies:
- First question starts at EASY by default
- Difficulty transitions: Easy->Medium->Hard for correct; Hard->Medium->Easy for incorrect
- In-session duplicate question prevention
- Session response recording and score calculation
"""

import unittest
from database.db import init_db
from quiz.quiz_engine import (
    start_quiz_session,
    get_session_by_id,
    get_session_responses,
    get_student_session_history
)
import config

class TestQuizEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_first_question_starts_at_easy(self):
        """Verifies Acceptance Criteria 4: The first question starts at Easy by default."""
        session = start_quiz_session(user_id=1, subject="Python Programming", total_questions=5)
        self.assertEqual(session.current_difficulty, config.DIFFICULTY_EASY)

        q1 = session.fetch_next_question()
        self.assertIsNotNone(q1)
        self.assertEqual(q1["difficulty"], config.DIFFICULTY_EASY)

    def test_mandatory_difficulty_progression(self):
        """
        Verifies exact mandatory difficulty sequence:
        Q1 (EASY) + Correct -> Q2 (MEDIUM)
        Q2 (MEDIUM) + Correct -> Q3 (HARD)
        Q3 (HARD) + Correct -> Q4 (HARD)
        Q4 (HARD) + Incorrect -> Q5 (MEDIUM)
        """
        session = start_quiz_session(user_id=1, subject="Data Structures and Algorithms", total_questions=5)

        # Q1: EASY
        q1 = session.fetch_next_question()
        self.assertEqual(q1["difficulty"], "EASY")
        corr_ans1 = session.current_question["correct_answer"]
        res1 = session.submit_answer(corr_ans1) # Correct
        self.assertTrue(res1["is_correct"])
        self.assertEqual(res1["next_difficulty"], "MEDIUM")
        self.assertEqual(session.current_difficulty, "MEDIUM")

        # Q2: MEDIUM
        q2 = session.fetch_next_question()
        self.assertEqual(q2["difficulty"], "MEDIUM")
        corr_ans2 = session.current_question["correct_answer"]
        res2 = session.submit_answer(corr_ans2) # Correct
        self.assertTrue(res2["is_correct"])
        self.assertEqual(res2["next_difficulty"], "HARD")
        self.assertEqual(session.current_difficulty, "HARD")

        # Q3: HARD
        q3 = session.fetch_next_question()
        self.assertEqual(q3["difficulty"], "HARD")
        corr_ans3 = session.current_question["correct_answer"]
        res3 = session.submit_answer(corr_ans3) # Correct
        self.assertTrue(res3["is_correct"])
        self.assertEqual(res3["next_difficulty"], "HARD") # Stays HARD

        # Q4: HARD
        q4 = session.fetch_next_question()
        self.assertEqual(q4["difficulty"], "HARD")
        # Submit deliberately wrong answer
        wrong_ans = "A" if session.current_question["correct_answer"] != "A" else "B"
        res4 = session.submit_answer(wrong_ans) # Incorrect
        self.assertFalse(res4["is_correct"])
        self.assertEqual(res4["next_difficulty"], "MEDIUM") # Drops to MEDIUM

        # Q5: MEDIUM
        q5 = session.fetch_next_question()
        self.assertEqual(q5["difficulty"], "MEDIUM")

    def test_duplicate_question_prevention(self):
        """Verifies that neither question ID nor question text is repeated within a quiz session."""
        session = start_quiz_session(user_id=1, subject="Database Management Systems", total_questions=10)
        served_ids = []
        served_texts = []

        for _ in range(10):
            q = session.fetch_next_question()
            if q:
                self.assertNotIn(q["id"], served_ids, f"Question ID {q['id']} was duplicated!")
                self.assertNotIn(q["question"].strip(), served_texts, f"Question text '{q['question']}' was duplicated!")
                served_ids.append(q["id"])
                served_texts.append(q["question"].strip())
                # Alternate answers to trigger different difficulties
                session.submit_answer(session.current_question["correct_answer"])

        self.assertEqual(len(served_ids), 10)
        self.assertEqual(len(served_ids), len(set(served_ids)))
        self.assertEqual(len(served_texts), len(set(served_texts)))

    def test_session_completion_and_persistence(self):
        """Tests that completion sets score, status, and creates persistent database records."""
        session = start_quiz_session(user_id=1, subject="Cybersecurity", total_questions=3)
        for _ in range(3):
            q = session.fetch_next_question()
            if q:
                session.submit_answer("B")

        summary = session.complete_quiz()
        self.assertEqual(summary["total_questions"], 3)

        # Check DB record
        db_sess = get_session_by_id(session.session_id)
        self.assertEqual(db_sess["status"], "completed")
        self.assertIsNotNone(db_sess["completed_at"])

        # Check responses
        responses = get_session_responses(session.session_id)
        self.assertEqual(len(responses), 3)

if __name__ == "__main__":
    unittest.main()
