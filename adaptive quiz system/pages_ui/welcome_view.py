"""
Welcome / Landing Page View.
Introduces the project, core MCA reinforcement learning objectives, and quick access links.
"""

import streamlit as st
import config

def render_welcome_view():
    """Renders the modern home / welcome page."""
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Adaptive Quiz System Using Reinforcement Learning</div>
            <div class="hero-subtitle">
                An intelligent educational evaluation system powered by <strong>Tabular Q-Learning</strong>.
                Dynamically calibrates question difficulty (EASY, MEDIUM, HARD) in real-time according to
                mandatory pedagogical transition rules, maximizing cognitive retention and motivation.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Core Features 3-Column Highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🤖</div>
                <h4 style="margin: 0 0 0.5rem 0; color: #00B4D8;">Tabular Q-Learning</h4>
                <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                    Utilizes discrete state representation (difficulty, accuracy, skill, question count)
                    and Bellman updates with exploration & exploitation.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎯</div>
                <h4 style="margin: 0 0 0.5rem 0; color: #5BC0BE;">Mandatory Transitions</h4>
                <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                    Enforces strict pedagogical state changes: Correct answers advance difficulty
                    (Easy &rarr; Med &rarr; Hard); incorrect answers scaffold downward.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
                <h4 style="margin: 0 0 0.5rem 0; color: #10B981;">Psychometric Analytics</h4>
                <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                    Rich interactive Plotly dashboards tracking student mastery curves,
                    cumulative reinforcement rewards, and domain competencies.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 📚 100+ Question Bank Across 5 Academic Domains")
    cols = st.columns(5)
    for idx, subj in enumerate(config.SUBJECTS):
        with cols[idx]:
            st.info(f"**{subj}**")

    st.markdown("---")

    # Quick Navigation CTA
    st.markdown("### 🚀 Quick Access")
    cta_col1, cta_col2, cta_col3, cta_col4 = st.columns(4)
    
    with cta_col1:
        if st.session_state.get("authenticated"):
            if st.button("📝 Start Adaptive Quiz", use_container_width=True, type="primary"):
                st.session_state["current_page"] = "Subject Selection"
                st.rerun()
        else:
            if st.button("🔑 Login or Register", use_container_width=True, type="primary"):
                st.session_state["current_page"] = "Login / Register"
                st.rerun()

    with cta_col2:
        if st.button("🧠 Q-Learning Visualization", use_container_width=True):
            st.session_state["current_page"] = "RL Visualization"
            st.rerun()

    with cta_col3:
        if st.button("🔬 Simulation & Benchmark Lab", use_container_width=True):
            st.session_state["current_page"] = "RL Simulation"
            st.rerun()

    with cta_col4:
        if st.session_state.get("authenticated") and st.session_state.get("user_role") == "admin":
            if st.button("⚙️ Admin Management", use_container_width=True):
                st.session_state["current_page"] = "Admin Dashboard"
                st.rerun()
        elif st.session_state.get("authenticated"):
            if st.button("📈 My Student Dashboard", use_container_width=True):
                st.session_state["current_page"] = "Student Dashboard"
                st.rerun()
        else:
            if st.button("👤 Demo Admin Login", use_container_width=True):
                st.session_state["demo_admin_fill"] = True
                st.session_state["current_page"] = "Login / Register"
                st.rerun()
