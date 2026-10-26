"""
Mandatory Adaptive Difficulty Transition Module.
Implements the exact deterministic difficulty state machine rules for the quiz:

If the student answers correctly:
    EASY   -> MEDIUM
    MEDIUM -> HARD
    HARD   -> HARD

If the student answers incorrectly:
    HARD   -> MEDIUM
    MEDIUM -> EASY
    EASY   -> EASY

Difficulty never exceeds HARD or drops below EASY.
"""

from typing import Dict, Any
import config

def get_next_difficulty(current_difficulty: str, is_correct: bool) -> str:
    """
    Computes the mandatory next difficulty level based on current difficulty and answer correctness.
    
    Rules:
    - Correct:
        EASY   -> MEDIUM
        MEDIUM -> HARD
        HARD   -> HARD
    - Incorrect:
        HARD   -> MEDIUM
        MEDIUM -> EASY
        EASY   -> EASY
    """
    cur = current_difficulty.strip().upper()

    if is_correct:
        if cur == config.DIFFICULTY_EASY:
            return config.DIFFICULTY_MEDIUM
        elif cur == config.DIFFICULTY_MEDIUM:
            return config.DIFFICULTY_HARD
        else:
            # HARD stays HARD
            return config.DIFFICULTY_HARD
    else:
        if cur == config.DIFFICULTY_HARD:
            return config.DIFFICULTY_MEDIUM
        elif cur == config.DIFFICULTY_MEDIUM:
            return config.DIFFICULTY_EASY
        else:
            # EASY stays EASY
            return config.DIFFICULTY_EASY

def get_difficulty_transition_details(current_difficulty: str, is_correct: bool, reward: float) -> Dict[str, Any]:
    """
    Returns structured explanation of the difficulty shift for logging and UI display.
    Example:
        CURRENT QUESTION: MEDIUM
        ANSWER: INCORRECT
        REWARD: -1
        NEXT DIFFICULTY: EASY
    """
    next_diff = get_next_difficulty(current_difficulty, is_correct)
    return {
        "current_difficulty": current_difficulty.upper(),
        "is_correct": is_correct,
        "reward": reward,
        "next_difficulty": next_diff.upper(),
        "transition_str": f"{current_difficulty.upper()} -> {next_diff.upper()}"
    }
