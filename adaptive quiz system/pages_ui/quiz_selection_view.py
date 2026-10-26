"""
Subject and Quiz Selection View Module.
Allows students to select a subject, configure test length, set question countdown timer,
and review the mandatory difficulty transition rules.
"""

import streamlit as st
import config
from quiz.quiz_engine import start_quiz_session
from database.db import execute_query_one

def render_quiz_selection_view():
    """Renders the quiz configuration and subject selection screen."""
    user_id = st.session_state.get("user_id")

    st.markdown("## 🎯 Launch Adaptive Quiz Session")
    st.markdown("Select an academic domain to evaluate your knowledge with real-time Q-learning difficulty adaptation.")

    col_config, col_rules = st.columns([1.2, 1])

    with col_config:
        st.markdown("### ⚙️ Quiz Parameters")
        selected_subject = st.selectbox(
            "Select Academic Subject",
            options=config.SUBJECTS,
            index=0
        )

        q_col1, q_col2 = st.columns(2)
        with q_col1:
            quiz_length = st.select_slider(
                "Number of Questions",
                options=[5, 10, 15, 20],
                value=10,
                help="Select the number of questions for this evaluation."
            )
        with q_col2:
            timer_choice = st.selectbox(
                "Countdown Timer",
                options=[
                    "30 Seconds (Fast)",
                    "60 Seconds (Standard)",
                    "90 Seconds (Relaxed)",
                    "Untimed (No Timer)"
                ],
                index=1,
                help="Countdown timer limit per question."
            )
            timer_map = {
                "30 Seconds (Fast)": 30,
                "60 Seconds (Standard)": 60,
                "90 Seconds (Relaxed)": 90,
                "Untimed (No Timer)": 0
            }
            st.session_state["quiz_timer_seconds"] = timer_map[timer_choice]

        # Subject historical insight
        prev_progress = execute_query_one(
            "SELECT estimated_skill, total_correct, total_incorrect FROM student_progress WHERE user_id = ? AND subject = ?",
            (user_id, selected_subject)
        )
        if prev_progress:
            tot = prev_progress["total_correct"] + prev_progress["total_incorrect"]
            acc = round((prev_progress["total_correct"] / float(tot) * 100.0), 1) if tot > 0 else 0.0
            st.info(f"📊 **Subject Profile:** {tot} past questions answered. Overall Accuracy: **{acc}%** (Skill: **{prev_progress['estimated_skill']}**).")
        else:
            st.info("🆕 **First Attempt:** You have not attempted this subject yet. Initial question starts at **EASY** by default.")

        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button("🚀 Begin Adaptive Quiz Session", type="primary", use_container_width=True)

        if start_btn:
            session = start_quiz_session(user_id=user_id, subject=selected_subject, total_questions=quiz_length)
            st.session_state["active_session"] = session
            st.session_state["current_question_data"] = None
            st.session_state["question_feedback"] = None
            st.session_state["question_start_time"] = None
            st.session_state["timeout_triggered"] = False
            st.session_state["current_page"] = "Active Quiz"
            st.rerun()

    with col_rules:
        st.markdown("### 📐 Mandatory Difficulty Rules")
        st.markdown(
            """
            <div class="metric-card" style="margin-top: 0.5rem;">
                <h5 style="color: #00B4D8; margin-bottom: 0.5rem;">Deterministic Transition Matrix</h5>
                <p style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.6;">
                    <strong>If your answer is CORRECT:</strong><br>
                    &bull; <code>EASY &rarr; MEDIUM</code><br>
                    &bull; <code>MEDIUM &rarr; HARD</code><br>
                    &bull; <code>HARD &rarr; HARD</code> (upper boundary)<br><br>
                    <strong>If your answer is INCORRECT:</strong><br>
                    &bull; <code>HARD &rarr; MEDIUM</code><br>
                    &bull; <code>MEDIUM &rarr; EASY</code><br>
                    &bull; <code>EASY &rarr; EASY</code> (lower boundary)
                </p>
                <div style="border-top: 1px solid #3A506B; padding-top: 0.5rem; font-size: 0.82rem; color: #94A3B8;">
                    ⏱️ <em>If the countdown timer reaches 0s, the question is automatically timed out, counted as incorrect (-1 reward), and difficulty decreases.</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
