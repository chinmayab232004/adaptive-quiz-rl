"""Dashboards package initialization."""
from dashboards.student_dashboard import (
    get_student_metrics,
    create_accuracy_trend_chart,
    create_subject_performance_chart,
    create_difficulty_breakdown_chart,
)
from dashboards.admin_dashboard import (
    get_admin_system_metrics,
    get_student_performance_table,
    create_question_distribution_chart,
    create_difficulty_distribution_chart,
    get_challenging_questions_report,
    get_global_rl_policy_table,
)
