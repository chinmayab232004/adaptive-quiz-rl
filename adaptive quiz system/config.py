"""
Configuration module for Adaptive Quiz System Using Reinforcement Learning.
Defines application constants, database settings, RL parameters, and UI themes.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "adaptive_quiz.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
SAMPLE_QUESTIONS_PATH = BASE_DIR / "data" / "sample_questions.json"
CSS_PATH = BASE_DIR / "assets" / "style.css"

# Authentication Settings
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "adminpassword123"
DEFAULT_ADMIN_EMAIL = "admin@quizsystem.edu"

# Reinforcement Learning (Q-learning) Hyperparameters
RL_ALPHA = 0.1         # Learning rate (alpha)
RL_GAMMA = 0.9         # Discount factor (gamma)
RL_EPSILON = 0.2       # Exploration rate (epsilon-greedy)
RL_EPSILON_MIN = 0.05  # Minimum exploration rate
RL_EPSILON_DECAY = 0.98

# Reward Scheme (Configurable)
REWARD_CORRECT = 1.0
REWARD_INCORRECT = -1.0

# Difficulty Levels (Strict 3 tiers)
DIFFICULTY_EASY = "EASY"
DIFFICULTY_MEDIUM = "MEDIUM"
DIFFICULTY_HARD = "HARD"

DIFFICULTY_LEVELS = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]
ACTION_TO_DIFFICULTY = {0: DIFFICULTY_EASY, 1: DIFFICULTY_MEDIUM, 2: DIFFICULTY_HARD}
DIFFICULTY_TO_ACTION = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: 1, DIFFICULTY_HARD: 2}

# Initial Default Difficulty for new quizzes
INITIAL_QUIZ_DIFFICULTY = DIFFICULTY_EASY

# Subjects
SUBJECTS = [
    "Python Programming",
    "Data Structures and Algorithms",
    "Database Management Systems",
    "Computer Networks",
    "Cybersecurity"
]

# Quiz Session Defaults
DEFAULT_QUIZ_LENGTH = 10
QUESTION_TIMER_SECONDS = 60  # Optional countdown timer per question

# Skill Levels
SKILL_BEGINNER = "Beginner"
SKILL_INTERMEDIATE = "Intermediate"
SKILL_ADVANCED = "Advanced"

# Theme Colors (Deep Navy, Modern Blue & Violet Accents)
THEME = {
    "bg_dark": "#0B132B",
    "card_bg": "#1C2541",
    "card_border": "#3A506B",
    "accent_primary": "#00B4D8",
    "accent_secondary": "#5BC0BE",
    "accent_purple": "#7209B7",
    "text_primary": "#FFFFFF",
    "text_muted": "#CBD5E1",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
}
