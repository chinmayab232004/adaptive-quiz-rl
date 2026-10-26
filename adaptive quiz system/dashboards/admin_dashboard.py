"""
Admin Dashboard Module.
Provides academic administrators with system analytics, student performance logs,
question distribution visualizers, and Q-learning policy oversight.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import execute_query, execute_query_one
import config
from reinforcement_learning.q_learning import QLearningAgent

def get_admin_system_metrics() -> Dict[str, Any]:
    """Retrieves top-level academic system metrics."""
    student_count = execute_query_one("SELECT COUNT(*) as c FROM users WHERE role = 'student'")["c"]
    question_count = execute_query_one("SELECT COUNT(*) as c FROM questions")["c"]
    total_quizzes = execute_query_one("SELECT COUNT(*) as c FROM quiz_sessions WHERE status = 'completed'")["c"]
    total_responses = execute_query_one("SELECT COUNT(*) as c FROM student_responses")["c"]
    
    avg_score_row = execute_query_one(
        """
        SELECT AVG(CAST(score AS REAL) / total_questions * 100) as a
        FROM quiz_sessions
        WHERE status = 'completed' AND total_questions > 0
        """
    )
    avg_accuracy = round(avg_score_row["a"], 1) if avg_score_row and avg_score_row["a"] else 0.0

    # RL Stats
    total_q_entries = execute_query_one("SELECT COUNT(*) as c FROM q_values")["c"]

    return {
        "total_students": student_count,
        "total_questions": question_count,
        "total_quizzes": total_quizzes,
        "total_responses": total_responses,
        "avg_system_accuracy": avg_accuracy,
        "total_q_entries": total_q_entries
    }

def get_student_performance_table() -> List[Dict[str, Any]]:
    """Retrieves summary performance list for all registered students."""
    rows = execute_query(
        """
        SELECT u.id, u.name, u.email,
               COUNT(DISTINCT qs.id) as quizzes_completed,
               COALESCE(SUM(qs.score), 0) as total_score,
               COALESCE(SUM(qs.total_questions), 0) as total_questions
        FROM users u
        LEFT JOIN quiz_sessions qs ON u.id = qs.user_id AND qs.status = 'completed'
        WHERE u.role = 'student'
        GROUP BY u.id
        ORDER BY quizzes_completed DESC
        """
    )
    result = []
    for r in rows:
        tot_q = r["total_questions"]
        tot_s = r["total_score"]
        acc = round((tot_s / float(tot_q) * 100.0), 1) if tot_q > 0 else 0.0
        result.append({
            "User ID": r["id"],
            "Student Name": r["name"],
            "Email": r["email"],
            "Quizzes Completed": r["quizzes_completed"],
            "Total Score": tot_s,
            "Questions Answered": tot_q,
            "Average Accuracy (%)": acc
        })
    return result

def create_question_distribution_chart() -> Optional[go.Figure]:
    """Generates a donut chart displaying question bank coverage across academic subjects."""
    rows = execute_query("SELECT subject, COUNT(*) as c FROM questions GROUP BY subject")
    if not rows:
        return None

    df = pd.DataFrame([dict(r) for r in rows])
    fig = px.pie(
        df,
        names="subject",
        values="c",
        title="Question Distribution by Subject",
        hole=0.45,
        color_discrete_sequence=["#00B4D8", "#5BC0BE", "#3A506B", "#10B981", "#7209B7"]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1C2541",
        plot_bgcolor="#0B132B",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def create_difficulty_distribution_chart() -> Optional[go.Figure]:
    """Generates a bar chart showing questions available at each difficulty."""
    rows = execute_query("SELECT difficulty, COUNT(*) as c FROM questions GROUP BY difficulty")
    if not rows:
        return None

    df = pd.DataFrame([dict(r) for r in rows])
    df["difficulty"] = df["difficulty"].str.upper()
    color_map = {"EASY": "#10B981", "MEDIUM": "#F59E0B", "HARD": "#EF4444"}
    fig = px.bar(
        df,
        x="difficulty",
        y="c",
        color="difficulty",
        color_discrete_map=color_map,
        title="Questions by Difficulty Level",
        labels={"difficulty": "Difficulty", "c": "Count"}
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1C2541",
        plot_bgcolor="#0B132B",
        margin=dict(l=30, r=30, t=50, b=30),
        showlegend=False
    )
    return fig

def get_challenging_questions_report() -> List[Dict[str, Any]]:
    """Identifies questions with the lowest accuracy across student attempts."""
    rows = execute_query(
        """
        SELECT q.id, q.subject, q.difficulty, q.question,
               COUNT(sr.id) as attempts,
               SUM(sr.is_correct) as correct_answers,
               ROUND((CAST(SUM(sr.is_correct) AS REAL) / COUNT(sr.id)) * 100, 1) as accuracy_rate
        FROM questions q
        JOIN student_responses sr ON q.id = sr.question_id
        GROUP BY q.id
        HAVING attempts >= 1
        ORDER BY accuracy_rate ASC
        LIMIT 10
        """
    )
    return [dict(r) for r in rows]

def get_global_rl_policy_table() -> List[Dict[str, Any]]:
    """Retrieves the global Q-learning agent policy for administrative inspection."""
    agent = QLearningAgent(user_id=0)
    return agent.get_policy_summary()
