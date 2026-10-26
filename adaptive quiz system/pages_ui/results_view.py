"""
Quiz Results View Module.
Presents detailed post-quiz performance analytics, difficulty distribution,
comparisons with previous attempts, and targeted learning recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from quiz.quiz_engine import get_session_by_id, get_session_responses, get_previous_subject_attempt

def render_results_view():
    """Renders comprehensive post-quiz evaluation."""
    session_id = st.session_state.get("last_completed_session_id")
    user_id = st.session_state.get("user_id")

    if not session_id:
        st.warning("No completed quiz results found to display.")
        if st.button("Start a New Quiz"):
            st.session_state["current_page"] = "Subject Selection"
            st.rerun()
        return

    session_data = get_session_by_id(session_id)
    if not session_data:
        st.error("Quiz session data could not be retrieved.")
        return

    responses = get_session_responses(session_id)
    subject = session_data["subject"]
    score = session_data["score"]
    total = session_data["total_questions"]
    accuracy = round((score / float(total) * 100.0), 1) if total > 0 else 0.0
    incorrect = total - score

    st.markdown(f"## 🏆 Quiz Results: {subject}")
    st.markdown("Here is your performance breakdown and reinforcement learning trajectory.")

    # 4 Performance Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Final Score</div>
                <div class="metric-value">{score} / {total}</div>
                <div class="metric-sub">{incorrect} Incorrect Answers</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Accuracy Rate</div>
                <div class="metric-value">{accuracy}%</div>
                <div class="metric-sub">Session Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        # Comparison with previous attempt
        prev_attempt = get_previous_subject_attempt(user_id, subject, exclude_session_id=session_id)
        if prev_attempt:
            delta = accuracy - prev_attempt["accuracy"]
            delta_symbol = "▲" if delta >= 0 else "▼"
            delta_color = "#10B981" if delta >= 0 else "#EF4444"
            comparison_text = f"<span style='color:{delta_color}; font-weight:bold;'>{delta_symbol} {abs(delta):.1f}%</span> vs Prior"
            sub_text = f"Previous: {prev_attempt['accuracy']:.1f}%"
        else:
            comparison_text = "Baseline Set"
            sub_text = "First attempt in this subject"

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Attempt Comparison</div>
                <div class="metric-value" style="font-size: 1.5rem; padding-top: 0.25rem;">{comparison_text}</div>
                <div class="metric-sub">{sub_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c4:
        if accuracy >= 80:
            status_text = "Mastery"
            status_badge = "badge-easy"
            status_sub = "Ready for advanced topics"
        elif accuracy >= 50:
            status_text = "Proficient"
            status_badge = "badge-medium"
            status_sub = "Solid understanding shown"
        else:
            status_text = "Needs Practice"
            status_badge = "badge-hard"
            status_sub = "Strengthen core fundamentals"

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Competency Status</div>
                <div class="metric-value" style="font-size: 1.5rem; padding-top: 0.25rem;">
                    <span class="{status_badge}">{status_text}</span>
                </div>
                <div class="metric-sub">{status_sub}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Visualizations Row: Difficulty Served & Question Timeline
    v_col1, v_col2 = st.columns([1, 1.4])

    with v_col1:
        st.markdown("#### 🎯 Questions Served by Difficulty")
        diff_counts = {"EASY": 0, "MEDIUM": 0, "HARD": 0}
        for r in responses:
            d = r.get("current_difficulty", "MEDIUM").upper()
            diff_counts[d] = diff_counts.get(d, 0) + 1

        df_pie = pd.DataFrame([{"Difficulty": k, "Count": v} for k, v in diff_counts.items() if v > 0])
        if not df_pie.empty:
            fig_pie = px.pie(
                df_pie,
                names="Difficulty",
                values="Count",
                hole=0.4,
                color="Difficulty",
                color_discrete_map={"EASY": "#10B981", "MEDIUM": "#F59E0B", "HARD": "#EF4444"}
            )
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="#1C2541",
                plot_bgcolor="#0B132B",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with v_col2:
        st.markdown("#### 📈 Difficulty Trajectory Over Session")
        if responses:
            df_resp = pd.DataFrame(responses)
            df_resp["q_num"] = range(1, len(df_resp) + 1)
            df_resp["Result"] = df_resp["is_correct"].apply(lambda c: "Correct" if c else "Incorrect")

            fig_step = px.scatter(
                df_resp,
                x="q_num",
                y="current_difficulty",
                color="Result",
                size=[14] * len(df_resp),
                category_orders={"current_difficulty": ["EASY", "MEDIUM", "HARD"]},
                color_discrete_map={"Correct": "#10B981", "Incorrect": "#EF4444"},
                hover_data=["reward", "next_difficulty"]
            )
            fig_step.update_layout(
                template="plotly_dark",
                paper_bgcolor="#1C2541",
                plot_bgcolor="#0B132B",
                yaxis=dict(title="Difficulty Level"),
                xaxis=dict(title="Question Sequence", dtick=1),
                margin=dict(l=40, r=40, t=30, b=40)
            )
            st.plotly_chart(fig_step, use_container_width=True)

    # Detailed Question Review
    st.markdown("### 📝 Detailed Question Breakdown")
    with st.expander("Click to expand itemized response review", expanded=True):
        for idx, r in enumerate(responses):
            is_c = r["is_correct"]
            icon = "✅" if is_c else "❌"
            badge = {"EASY": "badge-easy", "MEDIUM": "badge-medium", "HARD": "badge-hard"}.get(r["current_difficulty"].upper(), "")
            
            st.markdown(
                f"""
                <div style="border-bottom: 1px solid #3A506B; padding: 0.75rem 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>{icon} Q{idx + 1}: {r['question']}</strong>
                        <span class="{badge}">{r['current_difficulty']} &rarr; {r['next_difficulty']}</span>
                    </div>
                    <div style="color:#CBD5E1; font-size:0.9rem; margin-top:0.25rem;">
                        Your answer: <strong>Option {r['submitted_answer']}</strong> | Correct: <strong>Option {r['correct_answer']}</strong> | Reward: <strong>{r['reward']:+.1f}</strong>
                    </div>
                    <div style="color:#94A3B8; font-size:0.85rem; margin-top:0.25rem;">
                        <em>Topic: {r.get('topic', 'General')} | Explanation:</em> {r['explanation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Recommendations
    st.markdown("### 💡 Recommended Practice Plan")
    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h5 style="color: #00B4D8; margin-bottom: 0.5rem;">Targeted Study Focus</h5>
                <p style="color: #CBD5E1; font-size: 0.9rem;">
                    {"Focus on mastering complex scenarios and internal architecture." if accuracy >= 70 else "Review the conceptual foundations and trace code examples carefully."}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with rec_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h5 style="color: #5BC0BE; margin-bottom: 0.5rem;">RL Agent Adaptation</h5>
                <p style="color: #CBD5E1; font-size: 0.9rem;">
                    The Q-learning agent has evaluated the state-action transitions from this quiz and saved updated Q-values into SQLite for continuous evaluation.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    cta1, cta2 = st.columns(2)
    with cta1:
        if st.button("📝 Take Another Quiz", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Subject Selection"
            st.rerun()
    with cta2:
        if st.button("📈 Return to Student Dashboard", use_container_width=True):
            st.session_state["current_page"] = "Student Dashboard"
            st.rerun()
