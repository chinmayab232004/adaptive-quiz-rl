"""
Active Quiz Session View Module.
Implements the live question countdown timer, real-time second-by-second ticking,
automatic timeout evaluation, visible difficulty progression banner, instant feedback,
and Q-learning Bellman update display.
"""

import time
import streamlit as st
import config

# Live real-time countdown timer fragment (ticks down second by second in the browser)
@st.fragment(run_every="1s")
def render_live_countdown_timer(start_time: float, total_sec: int):
    """
    Renders live real-time countdown timer.
    Ticks every 1s, animates progress bar, and triggers auto-timeout when remaining <= 0.
    """
    elapsed = int(time.time() - start_time)
    remaining = max(0, total_sec - elapsed)
    pct = max(0.0, min(1.0, remaining / float(total_sec)))

    # Detect timeout
    if remaining <= 0:
        st.session_state["timeout_triggered"] = True
        st.rerun()

    # Dynamic color gradient
    color = "#10B981" if remaining > (total_sec * 0.4) else ("#F59E0B" if remaining > (total_sec * 0.2) else "#EF4444")
    mins = remaining // 60
    secs = remaining % 60
    time_str = f"{mins:02d}:{secs:02d}"

    st.markdown(
        f"""
        <div style="background: #111827; border: 1.5px solid {color}; border-radius: 8px; padding: 0.45rem 0.75rem; text-align: right; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Time Remaining</span>
                <span style="font-size: 1.2rem; font-weight: 800; color: {color}; font-family: monospace;">⏱️ {time_str}</span>
            </div>
            <div style="background: #374151; width: 100%; height: 6px; border-radius: 3px; overflow: hidden; margin-top: 0.35rem;">
                <div style="background: {color}; width: {pct * 100:.1f}%; height: 100%; transition: width 1s linear;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_active_quiz_view():
    """Renders the interactive question answering experience with live countdown."""
    session = st.session_state.get("active_session")
    if not session:
        st.warning("No active quiz session found. Please select a subject to begin.")
        if st.button("Go to Subject Selection", type="primary"):
            st.session_state["current_page"] = "Subject Selection"
            st.rerun()
        return

    # Check timer duration setting (default 60s, or customized in selection)
    timer_duration = st.session_state.get("quiz_timer_seconds", config.QUESTION_TIMER_SECONDS)

    # Check if we need to fetch the next question
    if st.session_state.get("current_question_data") is None:
        q_data = session.fetch_next_question()
        if q_data is None:
            # Session finished
            session.complete_quiz()
            st.session_state["last_completed_session_id"] = session.session_id
            st.session_state["active_session"] = None
            st.session_state["current_question_data"] = None
            st.session_state["question_feedback"] = None
            st.session_state["timeout_triggered"] = False
            st.session_state["current_page"] = "Quiz Results"
            st.rerun()
            return

        st.session_state["current_question_data"] = q_data
        st.session_state["question_start_time"] = time.time()
        st.session_state["question_feedback"] = None
        st.session_state["timeout_triggered"] = False

    q_data = st.session_state["current_question_data"]
    feedback = st.session_state.get("question_feedback")

    # Handle automatic timeout if time ran out
    if st.session_state.get("timeout_triggered") and not feedback:
        st.session_state["timeout_triggered"] = False
        # Submit as timed out / unanswered
        res = session.submit_answer("UNANSWERED")
        res["is_timeout"] = True
        st.session_state["question_feedback"] = res
        st.rerun()

    # Current Difficulty Badge
    diff = q_data["difficulty"].upper()
    diff_badge_class = {
        "EASY": "badge-easy",
        "MEDIUM": "badge-medium",
        "HARD": "badge-hard"
    }.get(diff, "badge-medium")

    q_index = q_data["question_index"]
    total_q = q_data["total_questions"]
    progress_val = float(q_index - 1) / float(total_q)

    # Top Header & Timer Row
    hdr_col1, hdr_col2, hdr_col3 = st.columns([2.5, 1.3, 1.2])
    with hdr_col1:
        st.markdown(f"#### 📖 {session.subject} — <span style='color:#94A3B8; font-size:1rem;'>Topic: {q_data.get('topic', 'General')}</span>", unsafe_allow_html=True)
    with hdr_col2:
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 0.35rem;">
                <span class="{diff_badge_class}">DIFFICULTY: {diff}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with hdr_col3:
        if not feedback:
            if timer_duration > 0:
                start_t = st.session_state.get("question_start_time", time.time())
                render_live_countdown_timer(start_t, timer_duration)
            else:
                st.markdown(
                    """
                    <div style="background:#111827; border: 1px solid #374151; border-radius: 8px; padding: 0.4rem 0.75rem; text-align: right;">
                        <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase;">Mode</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #5BC0BE;">Untimed</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div style="background:#111827; border: 1px solid #374151; border-radius: 8px; padding: 0.4rem 0.75rem; text-align: right;">
                    <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase;">Timer</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #00B4D8;">Paused ⏸️</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.progress(progress_val)
    st.caption(f"Question {q_index} of {total_q} | Current Score: {session.responses and sum(1 for r in session.responses if r['is_correct']) or 0}")

    # Question Prompt Card
    st.markdown(
        f"""
        <div class="question-box">
            <div class="question-text">{q_data['question']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Options Display
    options = q_data["options"]
    option_labels = [
        f"A) {options['A']}",
        f"B) {options['B']}",
        f"C) {options['C']}",
        f"D) {options['D']}"
    ]

    # Pre-submission form
    if not feedback:
        selected_label = st.radio(
            "Choose your answer:",
            options=option_labels,
            index=None,
            key=f"q_radio_{q_data['id']}_{q_index}"
        )

        sub_btn = st.button("Submit Answer", type="primary", use_container_width=True)

        if sub_btn:
            if not selected_label:
                st.error("Please select an answer option before submitting.")
            else:
                selected_opt = selected_label[0]  # 'A', 'B', 'C', or 'D'
                res = session.submit_answer(selected_opt)
                st.session_state["question_feedback"] = res
                st.rerun()

    else:
        # VISIBLE DIFFICULTY PROGRESSION & FEEDBACK BANNER
        is_corr = feedback["is_correct"]
        cur_d = feedback["current_difficulty"]
        next_d = feedback["next_difficulty"]
        rew = feedback["reward"]
        user_opt = feedback["submitted_answer"]
        corr_opt = feedback["correct_answer"]
        is_timeout = feedback.get("is_timeout", False)

        rew_color = "#10B981" if rew > 0 else "#EF4444"
        ans_color = "#10B981" if is_corr else "#EF4444"
        ans_text = "CORRECT" if is_corr else ("TIMEOUT" if is_timeout else "INCORRECT")

        # Notification message
        if is_corr:
            banner_msg = "✅ <strong>Great job!</strong> Your correct response advances the difficulty level."
        elif is_timeout:
            banner_msg = f"⏰ <strong>Time Expired!</strong> The question was not answered in time. The correct answer was <strong>Option {corr_opt}: {options.get(corr_opt, '')}</strong>."
        else:
            banner_msg = f"❌ <strong>Incorrect.</strong> You selected Option <strong>{user_opt}</strong>. The correct answer was <strong>Option {corr_opt}: {options.get(corr_opt, '')}</strong>."

        st.markdown(
            f"""
            <div style="background: #111827; border: 2px solid #3A506B; border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #374151; padding-bottom: 0.75rem; margin-bottom: 0.75rem;">
                    <div><span style="color:#94A3B8; font-size:0.85rem;">CURRENT QUESTION:</span> <strong style="color:#FFFFFF;">{cur_d}</strong></div>
                    <div><span style="color:#94A3B8; font-size:0.85rem;">ANSWER:</span> <strong style="color:{ans_color};">{ans_text}</strong></div>
                    <div><span style="color:#94A3B8; font-size:0.85rem;">REWARD:</span> <strong style="color:{rew_color};">{rew:+.1f}</strong></div>
                    <div><span style="color:#94A3B8; font-size:0.85rem;">NEXT DIFFICULTY:</span> <strong style="color:#00B4D8;">{next_d}</strong></div>
                </div>
                <div style="font-size: 0.95rem; color: #FFFFFF; line-height: 1.6;">
                    {banner_msg}
                </div>
                <div style="margin-top: 0.75rem; padding: 0.75rem; background: rgba(28, 37, 65, 0.6); border-radius: 6px; font-size: 0.88rem; color: #CBD5E1;">
                    <strong>📖 Educational Explanation:</strong> {feedback['explanation']}
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #94A3B8;">
                    🤖 <em>Q-Learning Bellman Update:</em> State: <code>{feedback['state']}</code> | Q-before: <code>{feedback['q_before']}</code> &rarr; Q-after: <code>{feedback['q_after']}</code> (TD error: <code>{feedback['td_error']}</code>)
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        is_last = (q_index >= total_q) or feedback.get("is_quiz_done", False)

        btn_label = "🏁 Finish Quiz & View Scorecard" if is_last else f"➡️ Proceed to Next Question ({next_d})"
        if st.button(btn_label, type="primary", use_container_width=True):
            if is_last:
                session.complete_quiz()
                st.session_state["last_completed_session_id"] = session.session_id
                st.session_state["active_session"] = None
                st.session_state["current_question_data"] = None
                st.session_state["question_feedback"] = None
                st.session_state["timeout_triggered"] = False
                st.session_state["current_page"] = "Quiz Results"
            else:
                st.session_state["current_question_data"] = None
                st.session_state["question_feedback"] = None
                st.session_state["timeout_triggered"] = False
            st.rerun()
