"""
Admin Dashboard View Module.
Administrative control room providing institutional analytics, student reports,
question distribution graphs, and reinforcement learning policy oversight.
"""

import streamlit as st
import pandas as pd
from dashboards.admin_dashboard import (
    get_admin_system_metrics,
    get_student_performance_table,
    create_question_distribution_chart,
    create_difficulty_distribution_chart,
    get_challenging_questions_report,
    get_global_rl_policy_table,
)

def render_admin_dashboard_view():
    """Renders the administrative analytics portal."""
    if st.session_state.get("user_role") != "admin":
        st.error("⛔ Access Denied. Administrator privileges are required to view this page.")
        return

    st.markdown("## 🛡️ Academic Administration Portal")
    st.markdown("Monitor system-wide learner performance, question inventory, and reinforcement learning convergence.")

    # System Metrics Cards
    metrics = get_admin_system_metrics()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Registered Students</div>
                <div class="metric-value">{metrics['total_students']}</div>
                <div class="metric-sub">Active Accounts</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Question Bank Size</div>
                <div class="metric-value">{metrics['total_questions']}</div>
                <div class="metric-sub">Across 5 CS Domains</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Completed Quizzes</div>
                <div class="metric-value">{metrics['total_quizzes']}</div>
                <div class="metric-sub">{metrics['total_responses']} Total Responses</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Avg System Accuracy</div>
                <div class="metric-value">{metrics['avg_system_accuracy']}%</div>
                <div class="metric-sub">System-wide Average</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Question Bank Distribution Charts
    st.markdown("### 📊 Question Inventory Distribution")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        donut_fig = create_question_distribution_chart()
        if donut_fig:
            st.plotly_chart(donut_fig, use_container_width=True)
    with col_chart2:
        bar_fig = create_difficulty_distribution_chart()
        if bar_fig:
            st.plotly_chart(bar_fig, use_container_width=True)

    # Student Performance Report
    st.markdown("### 👥 Student Performance Summary")
    student_rows = get_student_performance_table()
    if student_rows:
        df_students = pd.DataFrame(student_rows)
        st.dataframe(df_students, use_container_width=True, hide_index=True)
    else:
        st.info("No registered students found.")

    # Challenging Questions Analysis
    st.markdown("### ⚠️ Challenging Questions Analysis (Low Success Rate)")
    hard_questions = get_challenging_questions_report()
    if hard_questions:
        df_hard = pd.DataFrame(hard_questions)[["id", "subject", "difficulty", "attempts", "correct_answers", "accuracy_rate", "question_text"]]
        df_hard.columns = ["QID", "Subject", "Difficulty", "Attempts", "Correct", "Success Rate (%)", "Question Snippet"]
        st.dataframe(df_hard, use_container_width=True, hide_index=True)
    else:
        st.caption("Not enough student response data to detect question anomalies yet (requires 2+ attempts per question).")

    # Global Q-Learning Policy Inspector
    st.markdown("### 🧠 Learned Q-Learning Global Policy Inspector")
    with st.expander("Inspect Learned State-Action Q-Values in SQLite", expanded=False):
        policy_data = get_global_rl_policy_table()
        if policy_data:
            df_policy = pd.DataFrame(policy_data)
            st.dataframe(df_policy, use_container_width=True, hide_index=True)
        else:
            st.caption("Q-table entries are being initialized and updated as quiz responses are submitted.")

    st.markdown("---")
    if st.button("🛠️ Manage Question Bank (CRUD & Import/Export)", type="primary", use_container_width=True):
        st.session_state["current_page"] = "Question Management"
        st.rerun()
