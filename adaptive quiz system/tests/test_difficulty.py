"""
Unit Tests for Mandatory Adaptive Difficulty Transitions.
Verifies all 6 required state machine transitions:
- Easy + correct = Medium
- Medium + correct = Hard
- Hard + correct = Hard
- Hard + incorrect = Medium
- Medium + incorrect = Easy
- Easy + incorrect = Easy
"""

import pytest
from reinforcement_learning.difficulty import get_next_difficulty
import config

def test_easy_correct_becomes_medium():
    assert get_next_difficulty("EASY", is_correct=True) == "MEDIUM"
    assert get_next_difficulty("Easy", is_correct=True) == "MEDIUM"

def test_medium_correct_becomes_hard():
    assert get_next_difficulty("MEDIUM", is_correct=True) == "HARD"
    assert get_next_difficulty("Medium", is_correct=True) == "HARD"

def test_hard_correct_stays_hard():
    assert get_next_difficulty("HARD", is_correct=True) == "HARD"
    assert get_next_difficulty("Hard", is_correct=True) == "HARD"

def test_hard_incorrect_becomes_medium():
    assert get_next_difficulty("HARD", is_correct=False) == "MEDIUM"
    assert get_next_difficulty("Hard", is_correct=False) == "MEDIUM"

def test_medium_incorrect_becomes_easy():
    assert get_next_difficulty("MEDIUM", is_correct=False) == "EASY"
    assert get_next_difficulty("Medium", is_correct=False) == "EASY"

def test_easy_incorrect_stays_easy():
    assert get_next_difficulty("EASY", is_correct=False) == "EASY"
    assert get_next_difficulty("Easy", is_correct=False) == "EASY"
