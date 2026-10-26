"""
Authentication View Module.
Provides clean login and student registration tabs with secure salted password hashing.
"""

import streamlit as st
from auth.authentication import authenticate_user, register_user
import config

def render_auth_view():
    """Renders Login and Student Registration interface."""
    st.markdown("## 🔐 Portal Authentication")
    st.markdown("Sign in with your student credentials or register a new academic account.")

    tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create New Student Account"])

    # 1. Login Tab
    with tab_login:
        st.markdown("#### Access Your Dashboard")
        
        default_user = ""
        default_pwd = ""
        if st.session_state.get("demo_admin_fill"):
            default_user = config.DEFAULT_ADMIN_USERNAME
            default_pwd = config.DEFAULT_ADMIN_PASSWORD
            st.session_state["demo_admin_fill"] = False

        with st.form("login_form"):
            login_id = st.text_input("Email or Username", value=default_user, placeholder="e.g. admin or student@univ.edu")
            password = st.text_input("Password", value=default_pwd, type="password", placeholder="Enter your password")
            submit_btn = st.form_submit_button("Sign In", use_container_width=True)

            if submit_btn:
                success, msg, user_data = authenticate_user(login_id, password)
                if success and user_data:
                    st.session_state["authenticated"] = True
                    st.session_state["user_id"] = user_data["id"]
                    st.session_state["name"] = user_data["name"]
                    st.session_state["email"] = user_data["email"]
                    st.session_state["user_role"] = user_data["role"]
                    
                    st.success(f"Welcome back, {user_data['name']}!")
                    if user_data["role"] == "admin":
                        st.session_state["current_page"] = "Admin Dashboard"
                    else:
                        st.session_state["current_page"] = "Student Dashboard"
                    st.rerun()
                else:
                    st.error(msg)

        with st.expander("ℹ️ Academic Demo Credentials"):
            st.markdown(
                f"""
                - **Administrator Account:**
                  - Username / Email: `{config.DEFAULT_ADMIN_USERNAME}` or `{config.DEFAULT_ADMIN_EMAIL}`
                  - Password: `{config.DEFAULT_ADMIN_PASSWORD}`
                - Or register a new student account using the **Create New Student Account** tab.
                """
            )

    # 2. Registration Tab
    with tab_register:
        st.markdown("#### Student Registration")
        with st.form("register_form"):
            reg_name = st.text_input("Full Name", placeholder="e.g. John Doe")
            reg_email = st.text_input("Email Address", placeholder="e.g. john@student.edu")
            reg_password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
            reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            
            reg_btn = st.form_submit_button("Register Account", use_container_width=True)

            if reg_btn:
                if reg_password != reg_confirm:
                    st.error("Passwords do not match. Please verify and try again.")
                else:
                    success, msg, new_id = register_user(
                        name=reg_name,
                        email=reg_email,
                        password=reg_password,
                        role="student"
                    )
                    if success:
                        st.success(f"{msg} Logging you in automatically...")
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = new_id
                        st.session_state["name"] = reg_name.strip()
                        st.session_state["email"] = reg_email.strip().lower()
                        st.session_state["user_role"] = "student"
                        st.session_state["current_page"] = "Student Dashboard"
                        st.rerun()
                    else:
                        st.error(msg)
