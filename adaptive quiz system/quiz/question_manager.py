"""
Question Bank Management Module.
Provides CRUD operations, subject/difficulty filtering, search, and bulk JSON/CSV import/export.
"""

import json
import csv
import io
from typing import Dict, List, Optional, Any, Tuple
from database.db import execute_query, execute_query_one, execute_insert, execute_update
import config

def get_all_questions(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves questions with optional filtering by subject, difficulty, and search text."""
    query = "SELECT * FROM questions WHERE 1=1"
    params = []

    if subject and subject != "All":
        query += " AND subject = ?"
        params.append(subject)
    if difficulty and difficulty != "All":
        query += " AND difficulty = ?"
        params.append(difficulty.upper())
    if search_query:
        query += " AND (question LIKE ? OR topic LIKE ? OR explanation LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term, term])

    query += " ORDER BY id ASC"
    rows = execute_query(query, tuple(params))
    return [dict(r) for r in rows]

def get_question_by_id(question_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a single question by ID."""
    row = execute_query_one("SELECT * FROM questions WHERE id = ?", (question_id,))
    return dict(row) if row else None

def add_question(
    subject: str,
    topic: str,
    question: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_answer: str,
    difficulty: str,
    explanation: str
) -> Tuple[bool, str, Optional[int]]:
    """Validates and inserts a new question into the database."""
    subject = subject.strip()
    topic = topic.strip() if topic else "General"
    question = question.strip()
    correct_answer = correct_answer.strip().upper()
    difficulty = difficulty.strip().upper()
    explanation = explanation.strip()

    if not subject or not question:
        return False, "Subject and Question prompt are required.", None
    if not (option_a and option_b and option_c and option_d):
        return False, "All four options (A, B, C, D) are required.", None
    if correct_answer not in ["A", "B", "C", "D"]:
        return False, "Correct answer must be one of: A, B, C, or D.", None
    if difficulty not in config.DIFFICULTY_LEVELS:
        return False, f"Difficulty must be one of {config.DIFFICULTY_LEVELS}.", None

    # Check for duplicate question text in the same subject
    existing = execute_query_one(
        "SELECT id FROM questions WHERE subject = ? AND LOWER(TRIM(question)) = LOWER(TRIM(?))",
        (subject, question)
    )
    if existing:
        return False, "A question with the exact same text already exists for this subject.", existing["id"]

    try:
        new_id = execute_insert(
            """
            INSERT INTO questions (subject, topic, question, option_a, option_b, option_c, option_d, correct_answer, difficulty, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (subject, topic, question, option_a, option_b, option_c, option_d, correct_answer, difficulty, explanation)
        )
        return True, "Question created successfully.", new_id
    except Exception as e:
        return False, f"Database error inserting question: {str(e)}", None

def update_question(
    question_id: int,
    subject: str,
    topic: str,
    question: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_answer: str,
    difficulty: str,
    explanation: str
) -> Tuple[bool, str]:
    """Updates an existing question."""
    correct_answer = correct_answer.strip().upper()
    difficulty = difficulty.strip().upper()

    if correct_answer not in ["A", "B", "C", "D"]:
        return False, "Correct answer must be A, B, C, or D."
    if difficulty not in config.DIFFICULTY_LEVELS:
        return False, f"Difficulty must be one of {config.DIFFICULTY_LEVELS}."

    rows_affected = execute_update(
        """
        UPDATE questions
        SET subject = ?, topic = ?, question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?,
            correct_answer = ?, difficulty = ?, explanation = ?
        WHERE id = ?
        """,
        (subject, topic, question, option_a, option_b, option_c, option_d, correct_answer, difficulty, explanation, question_id)
    )
    if rows_affected > 0:
        return True, "Question updated successfully."
    return False, "Question not found or no changes made."

def delete_question(question_id: int) -> Tuple[bool, str]:
    """Deletes a question by ID."""
    rows_affected = execute_update("DELETE FROM questions WHERE id = ?", (question_id,))
    if rows_affected > 0:
        return True, "Question deleted successfully."
    return False, "Question not found."

def import_questions_from_json(json_content: str) -> Tuple[int, int, List[str]]:
    """Imports multiple questions from a JSON string."""
    try:
        data = json.loads(json_content)
    except Exception as e:
        return 0, 0, [f"Invalid JSON: {str(e)}"]

    if not isinstance(data, list):
        return 0, 0, ["JSON root element must be a list of question objects."]

    success_count = 0
    errors = []

    for idx, item in enumerate(data):
        try:
            ok, msg, _ = add_question(
                subject=item.get("subject", "Python Programming"),
                topic=item.get("topic", "General"),
                question=item.get("question", item.get("question_text", "")),
                option_a=item["option_a"],
                option_b=item["option_b"],
                option_c=item["option_c"],
                option_d=item["option_d"],
                correct_answer=item.get("correct_answer", item.get("correct_option", "A")),
                difficulty=item.get("difficulty", "MEDIUM"),
                explanation=item.get("explanation", "")
            )
            if ok:
                success_count += 1
            else:
                errors.append(f"Item {idx + 1}: {msg}")
        except KeyError as ke:
            errors.append(f"Item {idx + 1}: Missing key {str(ke)}")

    return success_count, len(data) - success_count, errors

def import_questions_from_csv(csv_content: str) -> Tuple[int, int, List[str]]:
    """Imports questions from CSV text."""
    success_count = 0
    errors = []
    
    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
    except Exception as e:
        return 0, 0, [f"CSV parsing error: {str(e)}"]

    for idx, row in enumerate(rows):
        try:
            ok, msg, _ = add_question(
                subject=row.get("subject", "Python Programming"),
                topic=row.get("topic", "General"),
                question=row.get("question", row.get("question_text", "")),
                option_a=row["option_a"],
                option_b=row["option_b"],
                option_c=row["option_c"],
                option_d=row["option_d"],
                correct_answer=row.get("correct_answer", row.get("correct_option", "A")),
                difficulty=row.get("difficulty", "MEDIUM"),
                explanation=row.get("explanation", "")
            )
            if ok:
                success_count += 1
            else:
                errors.append(f"Row {idx + 2}: {msg}")
        except KeyError as ke:
            errors.append(f"Row {idx + 2}: Missing column {str(ke)}")

    return success_count, len(rows) - success_count, errors

def export_questions_to_json() -> str:
    """Exports all questions to a formatted JSON string."""
    questions = get_all_questions()
    return json.dumps(questions, indent=2)

def get_question_stats() -> Dict[str, Any]:
    """Returns aggregated question bank statistics."""
    total_q = execute_query_one("SELECT COUNT(*) as c FROM questions")["c"]
    
    subj_rows = execute_query("SELECT subject, COUNT(*) as c FROM questions GROUP BY subject")
    by_subject = {r["subject"]: r["c"] for r in subj_rows}

    diff_rows = execute_query("SELECT difficulty, COUNT(*) as c FROM questions GROUP BY difficulty")
    by_difficulty = {r["difficulty"].upper(): r["c"] for r in diff_rows}

    return {
        "total_questions": total_q,
        "by_subject": by_subject,
        "by_difficulty": by_difficulty
    }
