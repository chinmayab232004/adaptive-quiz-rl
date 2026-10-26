"""
Student Dashboard View Module.
Displays learner metrics, skill trajectories, subject progress, and Plotly graphs.
"""

import streamlit as st
import pandas as pd
from dashboards.student_dashboard import (
    get_student_metrics,
    create_accuracy_trend_chart,
    create_subject_performance_chart,
    create_difficulty_breakdown_chart,
)
from quiz.quiz_engine import get_student_session_history

def render_student_dashboard_view():
    """Renders the comprehensive student performance dashboard."""
    user_id = st.session_state.get("user_id")
    full_name = st.session_state.get("full_name", "Student")

    st.markdown(f"## 🎓 Student Dashboard: {full_name}")
    st.markdown("Track your reinforcement learning progress, difficulty adaptations, and subject proficiencies.")

    metrics = get_student_metrics(user_id)

    # 4 Top-level Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Quizzes Attempted</div>
                <div class="metric-value">{metrics['total_quizzes']}</div>
                <div class="metric-sub">Completed Sessions</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Questions Answered</div>
                <div class="metric-value">{metrics['total_answered']}</div>
                <div class="metric-sub">{metrics['total_correct']} Correct Answers</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Overall Accuracy</div>
                <div class="metric-value">{metrics['overall_accuracy']}%</div>
                <div class="metric-sub">Across All Subjects</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        skill_badge = {
            "Beginner": "badge-easy",
            "Intermediate": "badge-medium",
            "Advanced": "badge-hard"
        }.get(metrics['overall_skill'], "badge-medium")

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Estimated Skill Level</div>
                <div class="metric-value" style="font-size: 1.5rem; padding-top: 0.25rem;">
                    <span class="{skill_badge}">{metrics['overall_skill']}</span>
                </div>
                <div class="metric-sub">Calibrated by Q-Learning</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # If new student with no completed quizzes yet
    if metrics["total_quizzes"] == 0:
        st.info("👋 You haven't taken any quizzes yet! Click below to start your first adaptive quiz session.")
        if st.button("🚀 Start Your First Adaptive Quiz", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Quiz Selection"
            st.rerun()
        return

    # Visualizations Row
    st.markdown("### 📈 Analytical Performance Charts")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        trend_fig = create_accuracy_trend_chart(user_id)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.caption("Complete more quizzes to view your learning trend.")

    with chart_col2:
        subj_fig = create_subject_performance_chart(user_id)
        if subj_fig:
            st.plotly_chart(subj_fig, use_container_width=True)
        else:
            st.caption("Subject-wise performance will populate as you test different subjects.")

    # Difficulty Breakdown Row
    diff_fig = create_difficulty_breakdown_chart(metrics["difficulty_accuracy"])
    if diff_fig:
        st.plotly_chart(diff_fig, use_container_width=True)

    # Subject Progress Table
    st.markdown("### 📚 Subject Competency Breakdown")
    if metrics["subject_progress"]:
        df_progress = pd.DataFrame(metrics["subject_progress"])
        df_progress["Accuracy (%)"] = df_progress.apply(
            lambda r: round((r["total_correct"] / float(r["total_answered"]) * 100), 1) if r["total_answered"] > 0 else 0.0,
            axis=1
        )
        df_display = df_progress[[
            "subject", "current_skill_level", "total_quizzes", "total_answered", "total_correct", "Accuracy (%)", "best_streak"
        ]].rename(columns={
            "subject": "Subject",
            "current_skill_level": "Skill Level",
            "total_quizzes": "Quizzes",
            "total_answered": "Answered",
            "total_correct": "Correct",
            "best_streak": "Best Streak"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.caption("No subject data recorded yet.")

    # Recent Quiz Sessions
    st.markdown("### 🕒 Recent Quiz Attempts")
    history = get_student_session_history(user_id, limit=5)
    if history:
        df_hist = pd.DataFrame(history)[["id", "subject", "score", "total_questions", "accuracy", "completed_at"]]
        df_hist.columns = ["Session ID", "Subject", "Score", "Total Questions", "Accuracy (%)", "Completed Date"]
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("📝 Take Another Quiz", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Quiz Selection"
            st.rerun()
    with c2:
        if st.button("📜 View Full History", use_container_width=True):
            st.session_state["current_page"] = "Quiz History"
            st.rerun()
