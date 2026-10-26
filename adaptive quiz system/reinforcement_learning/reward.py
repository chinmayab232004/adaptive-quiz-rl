"""
Reinforcement Learning Reward Calculation Module.
Implements configurable reward schemes for correct and incorrect answers:
- Correct answer: +1 (or configurable via config.REWARD_CORRECT)
- Incorrect answer: -1 (or configurable via config.REWARD_INCORRECT)
"""

from typing import Optional, List, Dict, Any
import config

def calculate_reward(
    is_correct: bool,
    difficulty: str = config.DIFFICULTY_MEDIUM,
    reward_correct: Optional[float] = None,
    reward_incorrect: Optional[float] = None
) -> float:
    """
    Computes scalar reward R for answering a question.
    Default scheme:
        Correct   -> +1.0
        Incorrect -> -1.0
    """
    pos = config.REWARD_CORRECT if reward_correct is None else reward_correct
    neg = config.REWARD_INCORRECT if reward_incorrect is None else reward_incorrect

    if is_correct:
        return float(pos)
    else:
        return float(neg)
