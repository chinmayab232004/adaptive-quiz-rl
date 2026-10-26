"""
Student Dashboard Analytics and Chart Generation Module.
Processes student history, computes performance metrics, and renders Plotly visualizations.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import execute_query, execute_query_one
import config

def get_student_metrics(user_id: int) -> Dict[str, Any]:
    """Computes aggregated performance metrics for a student."""
    # Aggregated session stats
    session_stats = execute_query_one(
        """
        SELECT COUNT(*) as total_quizzes,
               COALESCE(SUM(total_questions), 0) as total_questions,
               COALESCE(SUM(score), 0) as total_correct
        FROM quiz_sessions
        WHERE user_id = ? AND status = 'completed'
        """,
        (user_id,)
    )

    total_quizzes = session_stats["total_quizzes"] if session_stats else 0
    total_answered = session_stats["total_questions"] if session_stats else 0
    total_correct = session_stats["total_correct"] if session_stats else 0
    total_incorrect = total_answered - total_correct
    overall_accuracy = round((total_correct / float(total_answered) * 100.0), 1) if total_answered > 0 else 0.0

    # Total rewards earned
    reward_row = execute_query_one(
        """
        SELECT COALESCE(SUM(sr.reward), 0.0) as total_reward
        FROM student_responses sr
        JOIN quiz_sessions qs ON sr.session_id = qs.id
        WHERE qs.user_id = ?
        """,
        (user_id,)
    )
    total_rewards = round(reward_row["total_reward"], 1) if reward_row else 0.0

    # Subject-wise progress rows
    prog_rows = execute_query(
        """
        SELECT subject, estimated_skill, total_correct, total_incorrect
        FROM student_progress
        WHERE user_id = ?
        """,
        (user_id,)
    )

    # Dominant skill level
    if prog_rows:
        skills = [r["estimated_skill"] for r in prog_rows]
        avg_skill = sum(skills) / len(skills)
        if avg_skill >= 0.75:
            overall_skill = config.SKILL_ADVANCED
        elif avg_skill >= 0.45:
            overall_skill = config.SKILL_INTERMEDIATE
        else:
            overall_skill = config.SKILL_BEGINNER
    else:
        overall_skill = config.SKILL_BEGINNER

    # Latest difficulty reached
    last_resp = execute_query_one(
        """
        SELECT sr.next_difficulty
        FROM student_responses sr
        JOIN quiz_sessions qs ON sr.session_id = qs.id
        WHERE qs.user_id = ?
        ORDER BY sr.id DESC
        LIMIT 1
        """,
        (user_id,)
    )
    current_difficulty = last_resp["next_difficulty"].upper() if last_resp else config.DIFFICULTY_EASY

    # Difficulty-wise accuracy
    diff_rows = execute_query(
        """
        SELECT sr.current_difficulty as difficulty,
               COUNT(*) as total,
               SUM(sr.is_correct) as correct
        FROM student_responses sr
        JOIN quiz_sessions qs ON sr.session_id = qs.id
        WHERE qs.user_id = ?
        GROUP BY sr.current_difficulty
        """,
        (user_id,)
    )
    diff_accuracy = {}
    for r in diff_rows:
        d_name = r["difficulty"].upper()
        diff_accuracy[d_name] = {
            "total": r["total"],
            "correct": r["correct"],
            "accuracy": round((r["correct"] / r["total"] * 100.0), 1) if r["total"] > 0 else 0.0
        }

    return {
        "total_quizzes": total_quizzes,
        "total_answered": total_answered,
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "overall_accuracy": overall_accuracy,
        "overall_skill": overall_skill,
        "current_difficulty": current_difficulty,
        "total_rewards": total_rewards,
        "subject_progress": [dict(r) for r in prog_rows],
        "difficulty_accuracy": diff_accuracy
    }

def create_accuracy_trend_chart(user_id: int) -> Optional[go.Figure]:
    """Generates an interactive line chart tracking student accuracy over quiz sessions."""
    rows = execute_query(
        """
        SELECT id, subject, score, total_questions, completed_at
        FROM quiz_sessions
        WHERE user_id = ? AND status = 'completed'
        ORDER BY id ASC
        """,
        (user_id,)
    )
    if not rows:
        return None

    df = pd.DataFrame([dict(r) for r in rows])
    df["accuracy"] = df.apply(lambda r: round((r["score"] / float(r["total_questions"]) * 100.0), 1) if r["total_questions"] > 0 else 0.0, axis=1)
    df["session_num"] = range(1, len(df) + 1)

    fig = px.line(
        df,
        x="session_num",
        y="accuracy",
        markers=True,
        title="Learning Progress Over Time",
        labels={"session_num": "Quiz Session", "accuracy": "Accuracy (%)"},
        hover_data=["subject", "score", "total_questions"]
    )
    fig.update_traces(
        line=dict(color="#00B4D8", width=3),
        marker=dict(size=8, color="#5BC0BE", line=dict(width=2, color="#0B132B"))
    )
    fig.add_hline(y=75, line_dash="dash", line_color="#10B981", annotation_text="Mastery (75%)")
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1C2541",
        plot_bgcolor="#0B132B",
        margin=dict(l=40, r=40, t=50, b=40),
        yaxis=dict(range=[0, 105])
    )
    return fig

def create_subject_performance_chart(user_id: int) -> Optional[go.Figure]:
    """Generates a bar chart comparing accuracy across subjects."""
    rows = execute_query(
        """
        SELECT subject, total_correct, total_incorrect
        FROM student_progress
        WHERE user_id = ?
        """,
        (user_id,)
    )
    if not rows:
        return None

    data = []
    for r in rows:
        tot = r["total_correct"] + r["total_incorrect"]
        if tot > 0:
            acc = round((r["total_correct"] / float(tot)) * 100.0, 1)
            data.append({"Subject": r["subject"], "Accuracy": acc, "Total Answered": tot})

    if not data:
        return None

    df = pd.DataFrame(data)
    fig = px.bar(
        df,
        x="Subject",
        y="Accuracy",
        color="Accuracy",
        color_continuous_scale="Blues",
        title="Subject-Wise Accuracy (%)",
        text="Accuracy"
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1C2541",
        plot_bgcolor="#0B132B",
        margin=dict(l=40, r=40, t=50, b=40),
        yaxis=dict(range=[0, 115])
    )
    return fig

def create_difficulty_breakdown_chart(diff_accuracy: Dict[str, Any]) -> Optional[go.Figure]:
    """Generates a grouped bar chart displaying accuracy by difficulty level."""
    if not diff_accuracy:
        return None

    levels = []
    accuracies = []
    colors = []
    color_map = {"EASY": "#10B981", "MEDIUM": "#F59E0B", "HARD": "#EF4444"}

    for d in ["EASY", "MEDIUM", "HARD"]:
        if d in diff_accuracy and diff_accuracy[d]["total"] > 0:
            levels.append(d)
            accuracies.append(diff_accuracy[d]["accuracy"])
            colors.append(color_map.get(d, "#00B4D8"))

    if not levels:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=levels,
                y=accuracies,
                marker_color=colors,
                text=[f"{a}%" for a in accuracies],
                textposition="outside"
            )
        ]
    )
    fig.update_layout(
        title="Accuracy by Difficulty Level",
        template="plotly_dark",
        paper_bgcolor="#1C2541",
        plot_bgcolor="#0B132B",
        yaxis=dict(range=[0, 115], title="Accuracy (%)"),
        xaxis=dict(title="Difficulty"),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig
