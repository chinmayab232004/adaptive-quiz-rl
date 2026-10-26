"""
Quiz History View Module.
Allows students to browse past quiz sessions and inspect question-by-question historical responses.
"""

import streamlit as st
import pandas as pd
from quiz.quiz_engine import get_student_session_history, get_session_responses

def render_history_view():
    """Renders student quiz history and previous question responses."""
    user_id = st.session_state.get("user_id")

    st.markdown("## 📜 Quiz History & Review")
    st.markdown("Inspect all your completed adaptive evaluation sessions and reviewed responses.")

    history = get_student_session_history(user_id, limit=50)
    if not history:
        st.info("You have not completed any quizzes yet.")
        if st.button("Start a Quiz Now", type="primary"):
            st.session_state["current_page"] = "Subject Selection"
            st.rerun()
        return

    # Filter by subject
    subjects = ["All"] + sorted(list(set(h["subject"] for h in history)))
    selected_sub = st.selectbox("Filter History by Subject", options=subjects)

    filtered_history = [
        h for h in history if selected_sub == "All" or h["subject"] == selected_sub
    ]

    st.markdown(f"**Found {len(filtered_history)} completed session(s)**")

    # Overview table
    df_table = pd.DataFrame(filtered_history)[["id", "subject", "score", "total_questions", "accuracy", "completed_at"]]
    df_table.columns = ["Session ID", "Subject", "Score", "Total Questions", "Accuracy (%)", "Completed At"]
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # Detailed session inspector
    st.markdown("### 🔍 Inspect Session Questions")
    session_options = [f"Session #{h['id']} - {h['subject']} ({h['score']}/{h['total_questions']} | {h['accuracy']}%)" for h in filtered_history]
    selected_sess_label = st.selectbox("Choose a session to review in detail:", options=session_options)

    if selected_sess_label:
        sess_id = int(selected_sess_label.split(" - ")[0].replace("Session #", ""))
        responses = get_session_responses(sess_id)

        st.markdown(f"#### Questions for Session #{sess_id}")
        for idx, r in enumerate(responses):
            is_c = r["is_correct"]
            icon = "✅" if is_c else "❌"
            badge = {"EASY": "badge-easy", "MEDIUM": "badge-medium", "HARD": "badge-hard"}.get(r["current_difficulty"].upper(), "")

            with st.expander(f"{icon} Q{idx + 1}: {r['question'][:80]}... [{r['current_difficulty']}]", expanded=False):
                st.markdown(f"**Full Question:** {r['question']}")
                st.markdown(
                    f"""
                    - **A:** {r['option_a']}
                    - **B:** {r['option_b']}
                    - **C:** {r['option_c']}
                    - **D:** {r['option_d']}
                    """
                )
                st.markdown(f"- **Your Answer:** Option {r['submitted_answer']}")
                st.markdown(f"- **Correct Answer:** Option {r['correct_answer']}")
                st.markdown(f"- **Difficulty Transition:** `{r['current_difficulty']}` &rarr; `{r['next_difficulty']}` (Reward: `{r['reward']:+.1f}`)")
                st.info(f"**Explanation:** {r['explanation']}")
