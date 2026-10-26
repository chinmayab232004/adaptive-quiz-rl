"""
Reinforcement Learning Simulation and Multi-Model Evaluation View Module.
Empirically benchmarks three educational assessment paradigms:
1. Fixed-Difficulty Quiz (Static Baseline)
2. Rule-Based Adaptive Quiz (Heuristic State Machine)
3. Q-Learning-Based Adaptive Quiz with Mandatory Transition Rule
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reinforcement_learning.simulator import run_comparative_experiment

def render_simulation_view():
    """Renders the comprehensive 3-way evaluation benchmark portal."""
    st.markdown("## 🔬 Empirical Model Evaluation & Simulation Lab")
    st.markdown(
        """
        <div style="background: rgba(0, 180, 216, 0.1); border-left: 4px solid #00B4D8; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 1.5rem;">
            <strong>Controlled Evaluation Notice:</strong> This laboratory benchmarks three testing paradigms using
            <strong>simulated learner archetypes</strong> with parameterized response probabilities:
            <ol style="margin-top: 0.5rem; margin-bottom: 0;">
                <li><strong>Fixed-Difficulty Quiz:</strong> Serves non-adaptive fixed Medium questions.</li>
                <li><strong>Rule-Based Adaptive Quiz:</strong> Applies deterministic Easy &harr; Medium &harr; Hard transitions without RL value updates.</li>
                <li><strong>Q-Learning Adaptive Quiz:</strong> Evaluates state-action pairs, applies Bellman updates, and optimizes rewards while strictly enforcing the mandatory difficulty transition.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Simulation Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
    with ctrl_col1:
        archetype = st.selectbox(
            "Student Archetype Profile",
            options=["Novice", "Average", "Advanced"],
            index=0,
            help="Novice struggles on Medium/Hard; Average achieves moderate scores; Advanced excels across all difficulties."
        )
    with ctrl_col2:
        num_q = st.slider("Questions per Quiz Session", min_value=10, max_value=25, value=15, step=5)
    with ctrl_col3:
        episodes = st.slider("Simulation Episodes (Sessions)", min_value=1, max_value=5, value=3)

    if st.button("🚀 Run 3-Way Comparative Experiment", type="primary", use_container_width=True):
        with st.spinner("Executing simulation episodes across all three models..."):
            sim_res = run_comparative_experiment(
                ability_level=archetype,
                num_questions=num_q,
                episodes=episodes
            )
            st.session_state["comparative_results"] = sim_res

    if "comparative_results" in st.session_state:
        res = st.session_state["comparative_results"]
        st.markdown("---")
        st.markdown(f"### 📊 Benchmark Results for **{res['ability_level']}** Learner")

        # Top 3 Comparison Metric Cards
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">1. Fixed-Difficulty Model</div>
                    <div class="metric-value">{res['fixed_accuracy']}%</div>
                    <div class="metric-sub">Reward: {res['fixed_total_reward']} | Static Medium</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with sc2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">2. Rule-Based Adaptive</div>
                    <div class="metric-value" style="color: #F59E0B;">{res['rule_accuracy']}%</div>
                    <div class="metric-sub">Reward: {res['rule_total_reward']} | Deterministic Only</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with sc3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">3. Q-Learning + Mandatory Rule</div>
                    <div class="metric-value" style="color: #10B981;">{res['q_accuracy']}%</div>
                    <div class="metric-sub">Reward: {res['q_total_reward']} | RL Bellman Updates</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Chart 1: Cumulative Reward Comparison (All 3 Models)
        st.markdown("#### 1. Cumulative Reward Accumulation Over Questions")
        df_fixed = pd.DataFrame(res["fixed_logs"])
        df_rule = pd.DataFrame(res["rule_logs"])
        df_q = pd.DataFrame(res["q_logs"])

        fig_rew = go.Figure()
        fig_rew.add_trace(go.Scatter(
            x=df_fixed["question_num"],
            y=df_fixed["cumulative_reward"],
            mode="lines+markers",
            name="Fixed-Difficulty (Static Medium)",
            line=dict(color="#EF4444", width=2, dash="dot")
        ))
        fig_rew.add_trace(go.Scatter(
            x=df_rule["question_num"],
            y=df_rule["cumulative_reward"],
            mode="lines+markers",
            name="Rule-Based Adaptive Only",
            line=dict(color="#F59E0B", width=2, dash="dash")
        ))
        fig_rew.add_trace(go.Scatter(
            x=df_q["question_num"],
            y=df_q["cumulative_reward"],
            mode="lines+markers",
            name="Q-Learning Adaptive System",
            line=dict(color="#10B981", width=3)
        ))
        fig_rew.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1C2541",
            plot_bgcolor="#0B132B",
            xaxis_title="Question Number",
            yaxis_title="Cumulative Reward (R)",
            margin=dict(l=40, r=40, t=30, b=40)
        )
        st.plotly_chart(fig_rew, use_container_width=True)

        # Chart 2: Question Difficulty Progression Comparison
        st.markdown("#### 2. Question Difficulty Progression Trajectory")
        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(
            x=df_fixed["question_num"],
            y=df_fixed["difficulty"],
            mode="lines+markers",
            name="Fixed (Always Medium)",
            line=dict(color="#EF4444", width=2, dash="dot")
        ))
        fig_traj.add_trace(go.Scatter(
            x=df_rule["question_num"],
            y=df_rule["difficulty"],
            mode="lines+markers",
            name="Rule-Based Progression",
            line=dict(color="#F59E0B", width=2, dash="dash")
        ))
        fig_traj.add_trace(go.Scatter(
            x=df_q["question_num"],
            y=df_q["difficulty"],
            mode="lines+markers",
            name="Q-Learning Guided Progression",
            line=dict(color="#00B4D8", width=3)
        ))
        fig_traj.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1C2541",
            plot_bgcolor="#0B132B",
            yaxis=dict(categoryorder="array", categoryarray=["EASY", "MEDIUM", "HARD"], title="Difficulty"),
            xaxis=dict(title="Question Number", dtick=1),
            margin=dict(l=40, r=40, t=30, b=40)
        )
        st.plotly_chart(fig_traj, use_container_width=True)

        # Chart 3: Difficulty Distribution Across Models
        st.markdown("#### 3. Difficulty Level Distribution Comparison")
        dist_data = []
        for d in ["EASY", "MEDIUM", "HARD"]:
            dist_data.append({"Model": "Fixed", "Difficulty": d, "Count": res["fixed_diff_dist"].get(d, 0)})
            dist_data.append({"Model": "Rule-Based", "Difficulty": d, "Count": res["rule_diff_dist"].get(d, 0)})
            dist_data.append({"Model": "Q-Learning", "Difficulty": d, "Count": res["q_diff_dist"].get(d, 0)})

        df_dist = pd.DataFrame(dist_data)
        fig_dist = px.bar(
            df_dist,
            x="Model",
            y="Count",
            color="Difficulty",
            barmode="group",
            title="Questions Served by Difficulty Across Models",
            color_discrete_map={"EASY": "#10B981", "MEDIUM": "#F59E0B", "HARD": "#EF4444"}
        )
        fig_dist.update_layout(template="plotly_dark", paper_bgcolor="#1C2541", plot_bgcolor="#0B132B")
        st.plotly_chart(fig_dist, use_container_width=True)

        # Academic Viva Explanation
        st.markdown("### 🎓 Academic Evaluation & Defense Explanation")
        st.markdown(
            f"""
            <div class="metric-card">
                <h5 style="color:#00B4D8;">Distinction Between Rule-Based Transition & Learned Q-Values</h5>
                <p style="color:#CBD5E1; font-size:0.9rem; line-height:1.6;">
                    <strong>1. Deterministic Transition Rule:</strong> Dictates the immediate difficulty change after every response (Easy &rarr; Medium &rarr; Hard for correct; Hard &rarr; Medium &rarr; Easy for incorrect). This guarantees that difficulty bounds are never violated and student progress is consistent.<br>
                    <strong>2. Q-Learning Policy Evaluation:</strong> Operates at the state-action level, mapping discretized student states to expected cumulative returns. As questions are answered, the Bellman update converges to quantify which difficulty states yield optimal reinforcement rewards.<br>
                    <strong>3. Scientific Integrity:</strong> The simulation demonstrates that adaptive systems avoid chronic frustration for struggling students and boredom for advanced students, creating an optimal cognitive challenge.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
