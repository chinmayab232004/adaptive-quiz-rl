"""
Main Application Entry Point for Adaptive Quiz System Using Reinforcement Learning.
Handles routing, session management, sidebar navigation, and CSS injection.
"""

import streamlit as st
import config
from database.db import init_db

# Initialize database tables and seed sample questions on startup
init_db()

# Page configuration
st.set_page_config(
    page_title="Adaptive Quiz System - Reinforcement Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS styles
def load_css():
    if config.CSS_PATH.exists():
        with open(config.CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None
if "email" not in st.session_state:
    st.session_state["email"] = None
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

# Import page views
from pages_ui.welcome_view import render_welcome_view
from pages_ui.auth_view import render_auth_view
from pages_ui.student_dashboard_view import render_student_dashboard_view
from pages_ui.quiz_selection_view import render_quiz_selection_view
from pages_ui.active_quiz_view import render_active_quiz_view
from pages_ui.results_view import render_results_view
from pages_ui.history_view import render_history_view
from pages_ui.analytics_view import render_analytics_view
from pages_ui.admin_dashboard_view import render_admin_dashboard_view
from pages_ui.question_admin_view import render_question_admin_view
from pages_ui.rl_visualization_view import render_rl_visualization_view
from pages_ui.simulation_view import render_simulation_view

# Sidebar Navigation
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1rem 0;">
            <h2 style="color: #FFFFFF; margin: 0; font-size: 1.4rem;">🎓 Adaptive Quiz</h2>
            <div style="color: #00B4D8; font-size: 0.85rem; font-weight: 600;">Reinforcement Learning (Q-Learning)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # User Profile / Status in Sidebar
    if st.session_state["authenticated"]:
        role_badge = "badge-hard" if st.session_state["user_role"] == "admin" else "badge-easy"
        st.markdown(
            f"""
            <div style="background: #1C2541; border: 1px solid #3A506B; border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem;">
                <div style="font-size: 0.8rem; color: #94A3B8;">AUTHENTICATED ACCOUNT</div>
                <div style="font-size: 1.05rem; font-weight: bold; color: #FFFFFF;">{st.session_state['name']}</div>
                <div style="margin-top: 0.35rem;">
                    <span class="{role_badge}">{st.session_state['user_role'].upper()}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background: rgba(28, 37, 65, 0.6); border: 1px dashed #3A506B; border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem; font-size: 0.85rem; color: #94A3B8;">
                Guest Mode — Please sign in or register to track your learning progression.
            </div>
            """,
            unsafe_allow_html=True
        )

    # Navigation Links
    st.markdown("### 🧭 Navigation")
    
    nav_options = ["🏠 Home"]
    
    if st.session_state["authenticated"]:
        if st.session_state["user_role"] == "student":
            nav_options.extend([
                "📊 Student Dashboard",
                "🎯 Take Adaptive Quiz",
                "📜 Quiz History",
                "📈 Learning Analytics"
            ])
        elif st.session_state["user_role"] == "admin":
            nav_options.extend([
                "🛡️ Admin Dashboard",
                "🛠️ Question Bank CRUD",
                "🎯 Take Adaptive Quiz",
                "📊 Student Dashboard",
                "📈 Learning Analytics"
            ])
    
    nav_options.extend([
        "🧠 Q-Learning Visualization",
        "🔬 Evaluation & Simulation"
    ])

    if not st.session_state["authenticated"]:
        nav_options.append("🔑 Login / Register")

    # Map current_page to sidebar radio selection
    page_to_radio = {
        "Home": "🏠 Home",
        "Student Dashboard": "📊 Student Dashboard",
        "Subject Selection": "🎯 Take Adaptive Quiz",
        "Quiz Selection": "🎯 Take Adaptive Quiz",
        "Active Quiz": "🎯 Take Adaptive Quiz",
        "Quiz Results": "🎯 Take Adaptive Quiz",
        "Quiz History": "📜 Quiz History",
        "Learning Analytics": "📈 Learning Analytics",
        "Admin Dashboard": "🛡️ Admin Dashboard",
        "Question Management": "🛠️ Question Bank CRUD",
        "RL Visualization": "🧠 Q-Learning Visualization",
        "RL Simulation": "🔬 Evaluation & Simulation",
        "Login / Register": "🔑 Login / Register"
    }

    current_radio = page_to_radio.get(st.session_state["current_page"], "🏠 Home")
    if current_radio not in nav_options:
        current_radio = nav_options[0]

    selected_nav = st.radio(
        "Navigation Menu",
        options=nav_options,
        index=nav_options.index(current_radio),
        label_visibility="collapsed"
    )

    # Convert radio selection to page name
    radio_to_page = {
        "🏠 Home": "Home",
        "📊 Student Dashboard": "Student Dashboard",
        "🎯 Take Adaptive Quiz": "Subject Selection",
        "📜 Quiz History": "Quiz History",
        "📈 Learning Analytics": "Learning Analytics",
        "🛡️ Admin Dashboard": "Admin Dashboard",
        "🛠️ Question Bank CRUD": "Question Management",
        "🧠 Q-Learning Visualization": "RL Visualization",
        "🔬 Evaluation & Simulation": "RL Simulation",
        "🔑 Login / Register": "Login / Register"
    }

    new_page = radio_to_page.get(selected_nav)
    # Only update if user explicitly changed the radio and we are not in an active quiz
    if new_page != st.session_state["current_page"]:
        if st.session_state["current_page"] in ["Active Quiz", "Quiz Results"] and new_page == "Subject Selection":
            pass
        else:
            st.session_state["current_page"] = new_page
            st.rerun()

    st.markdown("---")
    if st.session_state["authenticated"]:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user_id"] = None
            st.session_state["name"] = None
            st.session_state["email"] = None
            st.session_state["user_role"] = None
            st.session_state["active_session"] = None
            st.session_state["current_page"] = "Home"
            st.rerun()
    else:
        if st.button("🔑 Sign In / Register", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Login / Register"
            st.rerun()

    # Academic Project Footer
    st.markdown(
        """
        <div style="font-size: 0.75rem; color: #64748B; margin-top: 2rem;">
            MCA Academic Project<br>
            <strong>Adaptive Quiz RL</strong><br>
            Python 3 • Streamlit • SQLite • Tabular Q-Learning
        </div>
        """,
        unsafe_allow_html=True
    )

# Page Routing Execution
page = st.session_state.get("current_page", "Home")

if page == "Home":
    render_welcome_view()
elif page == "Login / Register":
    render_auth_view()
elif page == "Student Dashboard":
    if not st.session_state["authenticated"]:
        st.session_state["current_page"] = "Login / Register"
        st.rerun()
    render_student_dashboard_view()
elif page in ["Subject Selection", "Quiz Selection"]:
    if not st.session_state["authenticated"]:
        st.session_state["current_page"] = "Login / Register"
        st.rerun()
    render_quiz_selection_view()
elif page == "Active Quiz":
    if not st.session_state["authenticated"]:
        st.session_state["current_page"] = "Login / Register"
        st.rerun()
    render_active_quiz_view()
elif page == "Quiz Results":
    if not st.session_state["authenticated"]:
        st.session_state["current_page"] = "Login / Register"
        st.rerun()
    render_results_view()
elif page == "Quiz History":
    if not st.session_state["authenticated"]:
        st.session_state["current_page"] = "Login / Register"
        st.rerun()
    render_history_view()
elif page == "Learning Analytics":
    if not st.session_state["authenticated"]:
        st.session_state["current_page"] = "Login / Register"
        st.rerun()
    render_analytics_view()
elif page == "Admin Dashboard":
    if not st.session_state["authenticated"]:
        st.session_state["current_page"] = "Login / Register"
        st.rerun()
    render_admin_dashboard_view()
elif page == "Question Management":
    if not st.session_state["authenticated"]:
        st.session_state["current_page"] = "Login / Register"
        st.rerun()
    render_question_admin_view()
elif page == "RL Visualization":
    render_rl_visualization_view()
elif page == "RL Simulation":
    render_simulation_view()
else:
    render_welcome_view()
