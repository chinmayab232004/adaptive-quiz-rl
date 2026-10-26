"""
Reinforcement Learning Visualization Page.
Provides an interactive mathematical demonstration of the Q-learning algorithm,
Q-table inspector, Bellman update breakdown, and viva presentation notes for MCA examiners.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import config
from reinforcement_learning.q_learning import QLearningAgent
from database.db import execute_query

def render_rl_visualization_view():
    """Renders the comprehensive Q-learning visualization and theory portal."""
    st.markdown("## 🧠 Reinforcement Learning & Q-Table Visualization")
    st.markdown("Examine the underlying tabular Q-learning algorithm, Bellman updates, and learned policy weights.")

    # Mathematical Formula Explainer Card
    st.markdown(
        """
        <div class="metric-card" style="margin-bottom: 1.5rem;">
            <h4 style="color: #00B4D8; margin-bottom: 0.5rem;">The Bellman Optimality Equation in This Project</h4>
            <div style="font-size: 1.15rem; background: #0B132B; padding: 1rem; border-radius: 8px; border: 1px solid #3A506B; margin-bottom: 0.75rem; text-align: center;">
                <code>Q(s, a) &larr; Q(s, a) + &alpha; [ r + &gamma; max<sub>a'</sub> Q(s', a') - Q(s, a) ]</code>
            </div>
            <div style="font-size: 0.9rem; color: #CBD5E1; line-height: 1.6;">
                <ul>
                    <li><strong>s (State):</strong> Student's current performance state tuple: <code>DIFF|ACC|PERF|ANS</code></li>
                    <li><strong>a (Action):</strong> Question difficulty evaluated: <code>EASY (0)</code>, <code>MEDIUM (1)</code>, <code>HARD (2)</code></li>
                    <li><strong>r (Reward):</strong> Immediate feedback signal (<code>+1.0</code> for correct, <code>-1.0</code> for incorrect)</li>
                    <li><strong>s' (Next State):</strong> Resulting state after answering and mandatory difficulty shift</li>
                    <li><strong>&alpha; (Learning Rate = 0.1):</strong> Determines how aggressively new rewards overwrite previous estimates</li>
                    <li><strong>&gamma; (Discount Factor = 0.9):</strong> Weights the value of future learning progression</li>
                    <li><strong>&epsilon; (Exploration Rate = 0.2):</strong> &epsilon;-greedy mechanism balancing exploration vs exploitation</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3 Hyperparameter Metric Cards
    hp1, hp2, hp3 = st.columns(3)
    with hp1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Learning Rate (&alpha;)</div>
                <div class="metric-value">{config.RL_ALPHA}</div>
                <div class="metric-sub">Step size for temporal difference</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with hp2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Discount Factor (&gamma;)</div>
                <div class="metric-value">{config.RL_GAMMA}</div>
                <div class="metric-sub">Future reward discount multiplier</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with hp3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Exploration Rate (&epsilon;)</div>
                <div class="metric-value">{config.RL_EPSILON}</div>
                <div class="metric-sub">&epsilon;-greedy action choice</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Interactive Step-by-Step Simulator for Examiner Demonstration
    st.markdown("### 🧪 Interactive Single-Step Bellman Calculator")
    st.markdown("Simulate a live Q-value update to observe how the mathematics function under examination:")

    calc_c1, calc_c2, calc_c3, calc_c4 = st.columns(4)
    with calc_c1:
        demo_state = st.selectbox(
            "State (s)",
            [
                "DIFF:EASY|ACC:HIGH|PERF:BEG|ANS:FEW",
                "DIFF:MEDIUM|ACC:MID|PERF:INT|ANS:SOME",
                "DIFF:HARD|ACC:HIGH|PERF:ADV|ANS:MANY"
            ]
        )
    with calc_c2:
        demo_action_name = st.selectbox("Action (a)", ["EASY", "MEDIUM", "HARD"], index=1)
        demo_action = config.DIFFICULTY_TO_ACTION[demo_action_name]
    with calc_c3:
        demo_result = st.radio("Student Answer", ["Correct (+1.0)", "Incorrect (-1.0)"], index=0)
        demo_reward = 1.0 if "Correct" in demo_result else -1.0
    with calc_c4:
        demo_next_state = st.selectbox(
            "Next State (s')",
            [
                "DIFF:MEDIUM|ACC:HIGH|PERF:INT|ANS:SOME",
                "DIFF:HARD|ACC:HIGH|PERF:ADV|ANS:SOME",
                "DIFF:EASY|ACC:LOW|PERF:BEG|ANS:SOME"
            ]
        )

    # Compute live calculation
    agent = QLearningAgent(user_id=st.session_state.get("user_id") or 0)
    q_vals_curr = agent.get_q_values(demo_state)
    q_before = q_vals_curr[demo_action]
    next_q_vals = agent.get_q_values(demo_next_state)
    max_next_q = max(next_q_vals)
    td_target = demo_reward + config.RL_GAMMA * max_next_q
    td_error = td_target - q_before
    q_after = q_before + config.RL_ALPHA * td_error

    st.markdown(
        f"""
        <div style="background:#1C2541; border: 1px solid #3A506B; border-radius: 8px; padding: 1.25rem; margin-top: 1rem;">
            <h5 style="color:#00B4D8; margin-bottom: 0.5rem;">Calculated Update Results:</h5>
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; color:#FFFFFF;">
                <div><span style="color:#94A3B8;">Q(s, a) Before:</span> <strong>{q_before:.4f}</strong></div>
                <div><span style="color:#94A3B8;">Max Q(s', a'):</span> <strong>{max_next_q:.4f}</strong></div>
                <div><span style="color:#94A3B8;">TD Error (&delta;):</span> <strong>{td_error:.4f}</strong></div>
                <div><span style="color:#94A3B8;">Q(s, a) After:</span> <strong style="color:#10B981;">{q_after:.4f}</strong></div>
            </div>
            <div style="margin-top: 0.75rem; font-size: 0.85rem; color: #CBD5E1;">
                <code>Q_new = {q_before:.4f} + 0.1 * [{demo_reward:+.1f} + 0.9 * {max_next_q:.4f} - {q_before:.4f}] = {q_after:.4f}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Persistent Q-Table Inspection
    st.markdown("### 📊 Persistent SQLite Q-Table Inspector")
    st.markdown("All Q-values learned by students and the global agent are persisted in the `q_values` table:")

    policy_data = agent.get_policy_summary()
    if policy_data:
        df_policy = pd.DataFrame(policy_data)
        st.dataframe(df_policy, use_container_width=True, hide_index=True)

        # Plot Q-Value Distribution
        st.markdown("#### Q-Value Heatmap Across Difficulty Actions")
        df_melt = df_policy.melt(id_vars=["State", "Highest Q Difficulty"], value_vars=["Q(EASY)", "Q(MEDIUM)", "Q(HARD)"], var_name="Action", value_name="Q-Value")
        fig_heat = px.bar(
            df_melt.head(30),
            x="State",
            y="Q-Value",
            color="Action",
            barmode="group",
            title="Q-Values for Learned State-Action Pairs (First 10 States)",
            color_discrete_map={"Q(EASY)": "#10B981", "Q(MEDIUM)": "#F59E0B", "Q(HARD)": "#EF4444"}
        )
        fig_heat.update_layout(template="plotly_dark", paper_bgcolor="#1C2541", plot_bgcolor="#0B132B")
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("The Q-table will populate with entries as you answer questions in quiz sessions.")
