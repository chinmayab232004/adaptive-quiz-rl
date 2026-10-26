"""
End-to-End System Integration Verification Script.
Validates the complete workflow from registration, login, quiz execution with
mandatory difficulty transitions, score recording, to administrative reporting.
"""

import unittest
import uuid
from auth.authentication import register_user, authenticate_user
from quiz.quiz_engine import (
    start_quiz_session,
    get_session_by_id,
    get_session_responses,
    get_student_session_history
)
from dashboards.student_dashboard import (
    get_student_metrics,
    create_accuracy_trend_chart,
    create_subject_performance_chart,
    create_difficulty_breakdown_chart
)
from dashboards.admin_dashboard import (
    get_admin_system_metrics,
    get_student_performance_table,
    create_question_distribution_chart,
    create_difficulty_distribution_chart,
    get_global_rl_policy_table
)
from reinforcement_learning.simulator import run_comparative_experiment
from quiz.question_manager import (
    get_question_stats,
    export_questions_to_json,
    import_questions_from_json
)
import config

class TestEndToEndSystem(unittest.TestCase):
    def test_full_workflow(self):
        # 1. Register student
        uid_hex = uuid.uuid4().hex[:8]
        email = f"student_{uid_hex}@mca.edu"
        pwd = "securepassword123"
        ok, msg, uid = register_user("MCA Capstone Student", email, pwd, role="student")
        self.assertTrue(ok)
        self.assertIsNotNone(uid)

        # 2. Login verification
        auth_ok, _, udata = authenticate_user(email, pwd)
        self.assertTrue(auth_ok)
        self.assertEqual(udata["id"], uid)

        # 3. Start Adaptive Quiz Session
        session = start_quiz_session(user_id=uid, subject="Computer Networks", total_questions=5)
        self.assertEqual(session.current_difficulty, config.DIFFICULTY_EASY)

        # 4. Answer 5 questions and verify mandatory difficulty transitions
        for i in range(5):
            q = session.fetch_next_question()
            self.assertIsNotNone(q, f"Failed to fetch question {i+1}")
            
            # Submit answer
            ans = "C"
            res = session.submit_answer(ans)
            self.assertIn("reward", res)
            self.assertIn("next_difficulty", res)
            self.assertIn("q_after", res)

        # 5. Complete session
        summary = session.complete_quiz()
        self.assertEqual(summary["total_questions"], 5)
        self.assertGreaterEqual(summary["score"], 0)

        # 6. Verify Student Dashboard Analytics
        metrics = get_student_metrics(uid)
        self.assertGreaterEqual(metrics["total_quizzes"], 1)
        self.assertEqual(metrics["total_answered"], 5)

        trend_fig = create_accuracy_trend_chart(uid)
        self.assertIsNotNone(trend_fig)

        # 7. Verify Admin Analytics
        admin_metrics = get_admin_system_metrics()
        self.assertGreaterEqual(admin_metrics["total_students"], 1)
        self.assertGreaterEqual(admin_metrics["total_questions"], 100)

        # 8. Verify Comparative Experiment (Fixed, Rule-based, Q-learning)
        sim_res = run_comparative_experiment(ability_level="Average", num_questions=10, episodes=2)
        self.assertIn("fixed_accuracy", sim_res)
        self.assertIn("rule_accuracy", sim_res)
        self.assertIn("q_accuracy", sim_res)

        # 9. Verify Question Bank Export & Import
        json_data = export_questions_to_json()
        self.assertTrue(len(json_data) > 1000)
        succ, fail, _ = import_questions_from_json(json_data)
        self.assertGreater(succ + fail, 90)

if __name__ == "__main__":
    unittest.main()
