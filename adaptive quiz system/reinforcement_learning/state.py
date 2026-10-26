"""
Reinforcement Learning State Representation Module.
Encodes the student's learning state using the 4 required dimensions:
1. Current difficulty level (EASY, MEDIUM, HARD)
2. Recent answer accuracy (LOW, MID, HIGH)
3. Estimated performance level (BEG, INT, ADV)
4. Number of questions answered (FEW, SOME, MANY)
"""

from typing import List, Dict, Any, Optional
import config

def discretize_accuracy(accuracy: float) -> str:
    """Discretizes accuracy percentage (0.0 to 1.0) into LOW, MID, HIGH tiers."""
    if accuracy < 0.50:
        return "LOW"
    elif accuracy <= 0.75:
        return "MID"
    return "HIGH"

def discretize_performance(perf_score: float) -> str:
    """Discretizes estimated performance level into BEG, INT, ADV."""
    if perf_score < 0.40:
        return "BEG"
    elif perf_score <= 0.75:
        return "INT"
    return "ADV"

def discretize_question_count(count: int) -> str:
    """Discretizes count of questions answered into FEW, SOME, MANY."""
    if count <= 3:
        return "FEW"
    elif count <= 7:
        return "SOME"
    return "MANY"

def get_state_key(
    current_difficulty: str,
    recent_accuracy: str,
    performance_level: str,
    question_count_tier: str
) -> str:
    """Formats the discrete state components into a canonical key string."""
    diff_clean = current_difficulty.strip().upper()
    return f"DIFF:{diff_clean}|ACC:{recent_accuracy}|PERF:{performance_level}|ANS:{question_count_tier}"

def build_state(
    current_difficulty: str,
    session_responses: List[Dict[str, Any]],
    estimated_performance: float = 0.50
) -> str:
    """
    Constructs the canonical RL state representation from active session metrics.
    """
    num_answered = len(session_responses)
    if num_answered == 0:
        acc = 0.50  # Default initial accuracy prior
    else:
        acc = sum(1 for r in session_responses if r.get("is_correct", 0)) / float(num_answered)

    acc_tier = discretize_accuracy(acc)
    perf_tier = discretize_performance(estimated_performance)
    ans_tier = discretize_question_count(num_answered)

    return get_state_key(current_difficulty, acc_tier, perf_tier, ans_tier)
