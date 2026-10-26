"""
Learning Analytics View Module.
Provides in-depth psychometric and performance analytics for students,
including cumulative rewards, difficulty progression curves, and competency radars.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import execute_query
from dashboards.student_dashboard import get_student_metrics

def render_analytics_view():
    """Renders comprehensive psychometric learning analytics."""
    user_id = st.session_state.get("user_id")
    full_name = st.session_state.get("name", "Student")

    st.markdown(f"## 📈 Advanced Learning Analytics: {full_name}")
    st.markdown("Detailed breakdown of your reinforcement learning rewards, difficulty adaptations, and topic mastery.")

    metrics = get_student_metrics(user_id)
    if metrics["total_quizzes"] == 0:
        st.info("You haven't completed any quizzes yet. Take a quiz to generate learning analytics!")
        if st.button("Start Adaptive Quiz"):
            st.session_state["current_page"] = "Subject Selection"
            st.rerun()
        return

    # Top KPI summary
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Rewards</div>
                <div class="metric-value">{metrics['total_rewards']}</div>
                <div class="metric-sub">Sum of Reinforcement Signals</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Accuracy Rate</div>
                <div class="metric-value">{metrics['overall_accuracy']}%</div>
                <div class="metric-sub">{metrics['total_correct']} of {metrics['total_answered']} Questions</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Current Difficulty</div>
                <div class="metric-value">{metrics['current_difficulty']}</div>
                <div class="metric-sub">Active State Level</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Estimated Skill</div>
                <div class="metric-value">{metrics['overall_skill']}</div>
                <div class="metric-sub">Cognitive Tier</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Detailed response logs across all sessions
    resp_rows = execute_query(
        """
        SELECT sr.id, sr.session_id, sr.current_difficulty, sr.next_difficulty, sr.is_correct, sr.reward, sr.answered_at, qs.subject
        FROM student_responses sr
        JOIN quiz_sessions qs ON sr.session_id = qs.id
        WHERE qs.user_id = ?
        ORDER BY sr.id ASC
        """,
        (user_id,)
    )

    if resp_rows:
        df_resp = pd.DataFrame([dict(r) for r in resp_rows])
        df_resp["question_seq"] = range(1, len(df_resp) + 1)
        df_resp["cum_reward"] = df_resp["reward"].cumsum()
        df_resp["Outcome"] = df_resp["is_correct"].apply(lambda c: "Correct (+1)" if c else "Incorrect (-1)")

        st.markdown("### 1. Cumulative Reward Accumulation Trajectory")
        fig_rew = px.line(
            df_resp,
            x="question_seq",
            y="cum_reward",
            markers=True,
            title="Cumulative Reward Over All Answered Questions",
            labels={"question_seq": "Total Questions Answered", "cum_reward": "Cumulative RL Reward"}
        )
        fig_rew.update_traces(line=dict(color="#10B981", width=3))
        fig_rew.update_layout(template="plotly_dark", paper_bgcolor="#1C2541", plot_bgcolor="#0B132B")
        st.plotly_chart(fig_rew, use_container_width=True)

        st.markdown("### 2. Difficulty Progression Timeline")
        fig_diff = px.scatter(
            df_resp,
            x="question_seq",
            y="current_difficulty",
            color="Outcome",
            title="Question Difficulty Progression Across Sessions",
            category_orders={"current_difficulty": ["EASY", "MEDIUM", "HARD"]},
            color_discrete_map={"Correct (+1)": "#10B981", "Incorrect (-1)": "#EF4444"},
            size=[10] * len(df_resp)
        )
        fig_diff.update_layout(template="plotly_dark", paper_bgcolor="#1C2541", plot_bgcolor="#0B132B")
        st.plotly_chart(fig_diff, use_container_width=True)
