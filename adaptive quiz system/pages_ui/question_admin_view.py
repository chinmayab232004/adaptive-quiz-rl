"""
Question Management Admin View Module.
Provides full CRUD capabilities, search filters, and JSON/CSV import/export.
"""

import streamlit as st
import pandas as pd
import config
from quiz.question_manager import (
    get_all_questions,
    get_question_by_id,
    add_question,
    update_question,
    delete_question,
    import_questions_from_json,
    import_questions_from_csv,
    export_questions_to_json,
    get_question_stats
)

def render_question_admin_view():
    """Renders administrative question bank management panel."""
    if st.session_state.get("user_role") != "admin":
        st.error("⛔ Access Denied. Administrator privileges are required.")
        return

    st.markdown("## 🛠️ Question Bank Management")
    st.markdown("Add, edit, delete, search, and bulk-import curriculum evaluation items.")

    tab_list, tab_add, tab_import = st.tabs([
        "📋 Question Explorer",
        "➕ Add New Question",
        "📥 Import / Export"
    ])

    # TAB 1: Explorer, Search, Edit & Delete
    with tab_list:
        st.markdown("#### Search & Filter Questions")
        f_col1, f_col2, f_col3 = st.columns([1.5, 1, 2])
        with f_col1:
            subj_filter = st.selectbox("Subject Filter", ["All"] + config.SUBJECTS, key="qm_subj")
        with f_col2:
            diff_filter = st.selectbox("Difficulty Filter", ["All"] + config.DIFFICULTY_LEVELS, key="qm_diff")
        with f_col3:
            search_txt = st.text_input("Search Text", placeholder="Search keywords...", key="qm_search")

        questions = get_all_questions(
            subject=subj_filter if subj_filter != "All" else None,
            difficulty=diff_filter if diff_filter != "All" else None,
            search_query=search_txt if search_txt else None
        )

        st.caption(f"Displaying {len(questions)} question(s)")

        if questions:
            df_q = pd.DataFrame(questions)[["id", "subject", "topic", "difficulty", "question", "correct_answer"]]
            df_q.columns = ["ID", "Subject", "Topic", "Difficulty", "Question", "Answer"]
            st.dataframe(df_q, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### Edit or Delete Question")
            q_ids = [q["id"] for q in questions]
            selected_qid = st.selectbox("Select Question ID to Inspect/Modify", options=q_ids)

            if selected_qid:
                q_item = get_question_by_id(selected_qid)
                if q_item:
                    with st.form(f"edit_q_form_{selected_qid}"):
                        e_sub = st.selectbox("Subject", options=config.SUBJECTS, index=config.SUBJECTS.index(q_item["subject"]) if q_item["subject"] in config.SUBJECTS else 0)
                        e_topic = st.text_input("Topic", value=q_item.get("topic", "General"))
                        e_diff = st.selectbox("Difficulty", options=config.DIFFICULTY_LEVELS, index=config.DIFFICULTY_LEVELS.index(q_item["difficulty"].upper()) if q_item["difficulty"].upper() in config.DIFFICULTY_LEVELS else 1)
                        e_text = st.text_area("Question Text", value=q_item["question"], height=100)
                        
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_a = st.text_input("Option A", value=q_item["option_a"])
                            e_c = st.text_input("Option C", value=q_item["option_c"])
                        with ec2:
                            e_b = st.text_input("Option B", value=q_item["option_b"])
                            e_d = st.text_input("Option D", value=q_item["option_d"])

                        e_corr = st.selectbox("Correct Answer", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(q_item["correct_answer"]))
                        e_exp = st.text_area("Educational Explanation", value=q_item["explanation"])

                        btn_col1, btn_col2 = st.columns([1, 1])
                        with btn_col1:
                            save_btn = st.form_submit_button("💾 Save Updates", type="primary", use_container_width=True)
                        with btn_col2:
                            del_btn = st.form_submit_button("🗑️ Delete Question", use_container_width=True)

                        if save_btn:
                            ok, msg = update_question(
                                question_id=selected_qid,
                                subject=e_sub,
                                topic=e_topic,
                                question=e_text,
                                option_a=e_a,
                                option_b=e_b,
                                option_c=e_c,
                                option_d=e_d,
                                correct_answer=e_corr,
                                difficulty=e_diff,
                                explanation=e_exp
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                        if del_btn:
                            ok, msg = delete_question(selected_qid)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("No questions match the selected filters.")

    # TAB 2: Add New Question
    with tab_add:
        st.markdown("#### Create a New Evaluation Question")
        with st.form("add_question_form"):
            new_sub = st.selectbox("Domain / Subject", options=config.SUBJECTS, key="add_sub")
            new_topic = st.text_input("Topic Category", placeholder="e.g. Memory Management, Routing, Trees", key="add_topic")
            new_diff = st.selectbox("Difficulty Level", options=config.DIFFICULTY_LEVELS, index=1, key="add_diff")
            new_text = st.text_area("Question Prompt", placeholder="Enter the complete question prompt...", height=100)

            c_opt1, c_opt2 = st.columns(2)
            with c_opt1:
                opt_a = st.text_input("Option A", placeholder="Choice A")
                opt_c = st.text_input("Option C", placeholder="Choice C")
            with c_opt2:
                opt_b = st.text_input("Option B", placeholder="Choice B")
                opt_d = st.text_input("Option D", placeholder="Choice D")

            new_corr = st.selectbox("Correct Answer", ["A", "B", "C", "D"], key="add_corr")
            new_exp = st.text_area("Educational Explanation / Rationale", placeholder="Explain why the correct answer is right...")

            create_submit = st.form_submit_button("➕ Create Question in Database", type="primary", use_container_width=True)

            if create_submit:
                ok, msg, new_id = add_question(
                    subject=new_sub,
                    topic=new_topic,
                    question=new_text,
                    option_a=opt_a,
                    option_b=opt_b,
                    option_c=opt_c,
                    option_d=opt_d,
                    correct_answer=new_corr,
                    difficulty=new_diff,
                    explanation=new_exp
                )
                if ok:
                    st.success(f"{msg} (New Question ID: {new_id})")
                    st.rerun()
                else:
                    st.error(msg)

    # TAB 3: Import / Export
    with tab_import:
        st.markdown("#### Bulk Curriculum Operations")
        st.markdown("##### 📤 Export Question Bank")
        json_export = export_questions_to_json()
        st.download_button(
            label="Download All Questions (JSON)",
            data=json_export,
            file_name="adaptive_quiz_question_bank.json",
            mime="application/json",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("##### 📥 Import Questions from File")
        uploaded_file = st.file_uploader("Upload JSON or CSV question file", type=["json", "csv"])

        if uploaded_file is not None:
            content_str = uploaded_file.getvalue().decode("utf-8")
            if uploaded_file.name.endswith(".json"):
                if st.button("Process JSON Import", type="primary"):
                    succ, fail, errors = import_questions_from_json(content_str)
                    st.success(f"Successfully imported {succ} questions. (Failed: {fail})")
                    if errors:
                        st.warning("Some items had errors:")
                        for err in errors[:5]:
                            st.write(f"- {err}")
                    st.rerun()
            elif uploaded_file.name.endswith(".csv"):
                if st.button("Process CSV Import", type="primary"):
                    succ, fail, errors = import_questions_from_csv(content_str)
                    st.success(f"Successfully imported {succ} questions. (Failed: {fail})")
                    if errors:
                        st.warning("Some items had errors:")
                        for err in errors[:5]:
                            st.write(f"- {err}")
                    st.rerun()
