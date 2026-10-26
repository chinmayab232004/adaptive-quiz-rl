"""
Adaptive Quiz Engine Module.
Orchestrates quiz session lifecycle, applies the mandatory deterministic difficulty transition rules:
    Correct:   EASY -> MEDIUM, MEDIUM -> HARD, HARD -> HARD
    Incorrect: HARD -> MEDIUM, MEDIUM -> EASY, EASY -> EASY
Updates the Q-learning agent, prevents in-session duplicates (with same-difficulty reset if exhausted),
and persists responses to SQLite.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from database.db import execute_query, execute_query_one, execute_insert, execute_update
import config
from reinforcement_learning.difficulty import get_next_difficulty, get_difficulty_transition_details
from reinforcement_learning.state import build_state
from reinforcement_learning.reward import calculate_reward
from reinforcement_learning.q_learning import QLearningAgent

class QuizSession:
    """Manages an active quiz session in memory and syncs with SQLite database."""
    def __init__(self, session_id: int, user_id: int, subject: str, total_questions: int = 10):
        self.session_id = session_id
        self.user_id = user_id
        self.subject = subject
        self.total_questions = total_questions
        self.agent = QLearningAgent(user_id=user_id)

        # Initial question starts at EASY by default
        self.current_difficulty: str = config.INITIAL_QUIZ_DIFFICULTY
        self.next_difficulty: str = config.INITIAL_QUIZ_DIFFICULTY

        # In-memory session tracking
        self.used_question_ids: List[int] = []
        self.used_question_texts: List[str] = []
        self.responses: List[Dict[str, Any]] = []
        self.current_question: Optional[Dict[str, Any]] = None
        self.current_state: str = ""
        self.current_action: int = config.DIFFICULTY_TO_ACTION[self.current_difficulty]
        self.estimated_skill: float = self._load_initial_skill()

    def _load_initial_skill(self) -> float:
        """Fetches student's baseline skill score from student_progress table."""
        row = execute_query_one(
            "SELECT estimated_skill FROM student_progress WHERE user_id = ? AND subject = ?",
            (self.user_id, self.subject)
        )
        if row and row["estimated_skill"] is not None:
            return float(row["estimated_skill"])
        return 0.50

    def fetch_next_question(self) -> Optional[Dict[str, Any]]:
        """
        Selects a question from the mandatory determined difficulty level.
        Enforces:
        1. Difficulty matches self.current_difficulty exactly.
        2. No duplicate question until all questions at this difficulty in this subject are exhausted.
        3. If exhausted at this difficulty, resets the used list for this difficulty (never changes difficulty).
        """
        if len(self.responses) >= self.total_questions:
            return None

        # Build current RL state
        self.current_state = build_state(
            current_difficulty=self.current_difficulty,
            session_responses=self.responses,
            estimated_performance=self.estimated_skill
        )
        self.current_action = config.DIFFICULTY_TO_ACTION[self.current_difficulty]

        # Query candidate questions of the exact current difficulty
        candidates = self._query_unused_questions(self.current_difficulty)

        # If all questions at this difficulty have been exhausted, reset used tracking for this difficulty
        if not candidates:
            rows_at_diff = execute_query(
                "SELECT id, question FROM questions WHERE subject = ? AND difficulty = ?",
                (self.subject, self.current_difficulty)
            )
            diff_ids = set(r["id"] for r in rows_at_diff)
            diff_texts = set(r["question"].strip().lower() for r in rows_at_diff)

            self.used_question_ids = [qid for qid in self.used_question_ids if qid not in diff_ids]
            self.used_question_texts = [qtxt for qtxt in self.used_question_texts if qtxt.strip().lower() not in diff_texts]

            candidates = self._query_unused_questions(self.current_difficulty)

        if not candidates:
            # Fallback to any question at this difficulty from the entire database for this subject
            rows = execute_query(
                "SELECT * FROM questions WHERE subject = ? AND difficulty = ?",
                (self.subject, self.current_difficulty)
            )
            candidates = [dict(r) for r in rows]

        if not candidates:
            return None

        # Pick one candidate randomly
        selected_q = random.choice(candidates)
        self.current_question = selected_q
        self.used_question_ids.append(selected_q["id"])
        self.used_question_texts.append(selected_q["question"])

        # Return question view (options without leaking correct answer)
        return {
            "id": selected_q["id"],
            "subject": selected_q["subject"],
            "topic": selected_q.get("topic", "General"),
            "question": selected_q["question"],
            "options": {
                "A": selected_q["option_a"],
                "B": selected_q["option_b"],
                "C": selected_q["option_c"],
                "D": selected_q["option_d"]
            },
            "difficulty": selected_q["difficulty"].upper(),
            "question_index": len(self.responses) + 1,
            "total_questions": self.total_questions
        }

    def _query_unused_questions(self, difficulty: str) -> List[Dict[str, Any]]:
        """Queries unused questions matching subject and difficulty."""
        query = "SELECT * FROM questions WHERE subject = ? AND difficulty = ?"
        params: List[Any] = [self.subject, difficulty.upper()]

        if self.used_question_ids:
            placeholders = ",".join("?" for _ in self.used_question_ids)
            query += f" AND id NOT IN ({placeholders})"
            params.extend(self.used_question_ids)

        rows = execute_query(query, tuple(params))
        used_texts_lower = {t.strip().lower() for t in self.used_question_texts}
        candidates = [dict(r) for r in rows if r["question"].strip().lower() not in used_texts_lower]
        return candidates

    def submit_answer(self, submitted_answer: str) -> Dict[str, Any]:
        """
        Evaluates student's answer, applies mandatory difficulty transition,
        calculates reward, updates Q-values, and stores records in SQLite.
        """
        if not self.current_question:
            raise ValueError("No active question to submit answer for.")

        submitted_answer = submitted_answer.strip().upper()
        correct_answer = self.current_question["correct_answer"].strip().upper()
        is_correct = (submitted_answer == correct_answer)

        # 1. Compute Reward (+1 for correct, -1 for incorrect)
        reward = calculate_reward(is_correct=is_correct, difficulty=self.current_difficulty)

        # 2. Mandatory Difficulty Transition Rule
        # Easy + Correct = Medium, Medium + Correct = Hard, Hard + Correct = Hard
        # Hard + Incorrect = Medium, Medium + Incorrect = Easy, Easy + Incorrect = Easy
        next_diff = get_next_difficulty(self.current_difficulty, is_correct)
        self.next_difficulty = next_diff

        # 3. Store in-memory response record
        response_record = {
            "question_id": self.current_question["id"],
            "topic": self.current_question.get("topic", "General"),
            "question": self.current_question["question"],
            "submitted_answer": submitted_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "current_difficulty": self.current_difficulty,
            "next_difficulty": next_diff,
            "reward": reward,
            "explanation": self.current_question["explanation"],
            "state_key": self.current_state,
            "action_taken": self.current_action
        }
        self.responses.append(response_record)

        # Update rolling skill estimate
        correct_count = sum(1 for r in self.responses if r["is_correct"])
        total_count = len(self.responses)
        self.estimated_skill = round(correct_count / float(total_count), 3)

        # 4. Construct Next State and Execute Q-Learning Bellman Update
        is_quiz_done = (total_count >= self.total_questions)
        next_state = build_state(
            current_difficulty=next_diff,
            session_responses=self.responses,
            estimated_performance=self.estimated_skill
        )

        rl_update_info = self.agent.update(
            state=self.current_state,
            action=self.current_action,
            reward=reward,
            next_state=next_state,
            done=is_quiz_done
        )

        # 5. Insert into student_responses table
        execute_insert(
            """
            INSERT INTO student_responses (
                session_id, question_id, submitted_answer, is_correct,
                current_difficulty, next_difficulty, reward
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.session_id,
                self.current_question["id"],
                submitted_answer,
                1 if is_correct else 0,
                self.current_difficulty,
                next_diff,
                reward
            )
        )

        # 6. Update quiz_sessions record
        execute_update(
            "UPDATE quiz_sessions SET score = ? WHERE id = ?",
            (correct_count, self.session_id)
        )

        # Prepare for next question
        prev_diff = self.current_difficulty
        self.current_difficulty = next_diff

        return {
            "is_correct": is_correct,
            "submitted_answer": submitted_answer,
            "correct_answer": correct_answer,
            "explanation": self.current_question["explanation"],
            "current_difficulty": prev_diff,
            "next_difficulty": next_diff,
            "reward": reward,
            "score": correct_count,
            "questions_answered": total_count,
            "total_questions": self.total_questions,
            "is_quiz_done": is_quiz_done,
            "state": self.current_state,
            "action": self.current_action,
            "next_state": next_state,
            "q_before": rl_update_info["q_before"],
            "q_after": rl_update_info["q_after"],
            "td_error": rl_update_info["td_error"],
            "alpha": self.agent.alpha,
            "gamma": self.agent.gamma,
            "epsilon": self.agent.epsilon
        }

    def complete_quiz(self) -> Dict[str, Any]:
        """Finalizes quiz session in database and updates student_progress table."""
        total_count = len(self.responses)
        correct_count = sum(1 for r in self.responses if r["is_correct"])
        incorrect_count = total_count - correct_count

        # Mark session as completed
        execute_update(
            """
            UPDATE quiz_sessions
            SET score = ?, status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (correct_count, self.session_id)
        )

        # Update cumulative student_progress
        self._update_student_progress(correct_count, incorrect_count)

        return {
            "session_id": self.session_id,
            "subject": self.subject,
            "score": correct_count,
            "total_questions": total_count,
            "accuracy": round((correct_count / float(total_count) * 100.0) if total_count > 0 else 0.0, 1),
            "responses": self.responses
        }

    def _update_student_progress(self, session_correct: int, session_incorrect: int) -> None:
        """Updates cumulative progress in student_progress table."""
        row = execute_query_one(
            "SELECT total_correct, total_incorrect FROM student_progress WHERE user_id = ? AND subject = ?",
            (self.user_id, self.subject)
        )

        if not row:
            total_corr = session_correct
            total_inc = session_incorrect
        else:
            total_corr = row["total_correct"] + session_correct
            total_inc = row["total_incorrect"] + session_incorrect

        total_ans = total_corr + total_inc
        skill = round((total_corr / float(total_ans)), 3) if total_ans > 0 else 0.50

        execute_update(
            """
            INSERT INTO student_progress (
                user_id, subject, estimated_skill, total_correct, total_incorrect, updated_at
            )
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, subject)
            DO UPDATE SET
                estimated_skill = excluded.estimated_skill,
                total_correct = excluded.total_correct,
                total_incorrect = excluded.total_incorrect,
                updated_at = CURRENT_TIMESTAMP
            """,
            (self.user_id, self.subject, skill, total_corr, total_inc)
        )

def start_quiz_session(user_id: int, subject: str, total_questions: int = config.DEFAULT_QUIZ_LENGTH) -> QuizSession:
    """Creates a new quiz session record in SQLite and returns active QuizSession manager."""
    session_id = execute_insert(
        """
        INSERT INTO quiz_sessions (user_id, subject, total_questions, score, status)
        VALUES (?, ?, ?, 0, 'in_progress')
        """,
        (user_id, subject, total_questions)
    )
    return QuizSession(session_id=session_id, user_id=user_id, subject=subject, total_questions=total_questions)

def get_session_by_id(session_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves session metadata from SQLite."""
    row = execute_query_one("SELECT * FROM quiz_sessions WHERE id = ?", (session_id,))
    return dict(row) if row else None

def get_session_responses(session_id: int) -> List[Dict[str, Any]]:
    """Retrieves all submitted question responses for a given session."""
    rows = execute_query(
        """
        SELECT sr.*, q.subject, q.topic, q.question, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_answer, q.explanation
        FROM student_responses sr
        JOIN questions q ON sr.question_id = q.id
        WHERE sr.session_id = ?
        ORDER BY sr.id ASC
        """,
        (session_id,)
    )
    return [dict(r) for r in rows]

def get_student_session_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves past completed quiz sessions for a student."""
    rows = execute_query(
        """
        SELECT id, subject, total_questions, score, started_at, completed_at, status
        FROM quiz_sessions
        WHERE user_id = ? AND status = 'completed'
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit)
    )
    res = []
    for r in rows:
        d = dict(r)
        d["accuracy"] = round((d["score"] / float(d["total_questions"]) * 100.0) if d["total_questions"] > 0 else 0.0, 1)
        res.append(d)
    return res

def get_previous_subject_attempt(user_id: int, subject: str, exclude_session_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves the previous completed quiz attempt for comparative analysis."""
    row = execute_query_one(
        """
        SELECT id, score, total_questions, completed_at
        FROM quiz_sessions
        WHERE user_id = ? AND subject = ? AND status = 'completed' AND id != ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id, subject, exclude_session_id)
    )
    if row:
        d = dict(row)
        d["accuracy"] = round((d["score"] / float(d["total_questions"]) * 100.0) if d["total_questions"] > 0 else 0.0, 1)
        return d
    return None
