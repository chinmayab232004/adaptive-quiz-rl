"""
Reinforcement Learning Evaluation and Multi-Model Experimentation Module.
Empirically compares three educational quiz paradigms:
1. Fixed-Difficulty Quiz (Traditional Static Benchmark)
2. Pure Rule-Based Adaptive Quiz (Heuristic State Machine)
3. Q-Learning-Based Adaptive Quiz with Mandatory Transition Rule
"""

import random
from typing import Dict, List, Any
import numpy as np
import config
from reinforcement_learning.difficulty import get_next_difficulty
from reinforcement_learning.state import build_state
from reinforcement_learning.reward import calculate_reward
from reinforcement_learning.q_learning import QLearningAgent

class SimulatedStudent:
    """Simulates a student with probability distributions for answering questions at each difficulty."""
    def __init__(self, name: str, ability_level: str):
        self.name = name
        self.ability_level = ability_level

        if ability_level == "Novice":
            self.prob_correct = {"EASY": 0.75, "MEDIUM": 0.35, "HARD": 0.12}
            self.baseline_skill = 0.30
        elif ability_level == "Average":
            self.prob_correct = {"EASY": 0.90, "MEDIUM": 0.65, "HARD": 0.35}
            self.baseline_skill = 0.55
        elif ability_level == "Advanced":
            self.prob_correct = {"EASY": 0.98, "MEDIUM": 0.88, "HARD": 0.72}
            self.baseline_skill = 0.85
        else:
            self.prob_correct = {"EASY": 0.85, "MEDIUM": 0.60, "HARD": 0.30}
            self.baseline_skill = 0.50

    def answer_question(self, difficulty: str) -> bool:
        p = self.prob_correct.get(difficulty.upper(), 0.5)
        return random.random() < p

def run_comparative_experiment(
    ability_level: str = "Average",
    num_questions: int = 15,
    episodes: int = 3
) -> Dict[str, Any]:
    """
    Executes benchmark comparison across:
    1. Fixed Difficulty (Fixed Medium)
    2. Rule-Based Adaptive (Deterministic transitions only)
    3. Q-Learning Adaptive (Q-learning updates + mandatory transitions)
    """
    student = SimulatedStudent(f"Student-{ability_level}", ability_level)

    # 1. FIXED-DIFFICULTY SYSTEM (Fixed Medium)
    fixed_logs = []
    fixed_cum_reward = 0.0
    for q_idx in range(1, num_questions + 1):
        diff = config.DIFFICULTY_MEDIUM
        is_corr = student.answer_question(diff)
        reward = calculate_reward(is_corr, diff)
        fixed_cum_reward += reward
        fixed_logs.append({
            "question_num": q_idx,
            "difficulty": diff,
            "is_correct": is_corr,
            "reward": reward,
            "cumulative_reward": round(fixed_cum_reward, 2)
        })

    # 2. RULE-BASED ADAPTIVE SYSTEM (Easy start, transitions without RL updates)
    rule_logs = []
    rule_cum_reward = 0.0
    cur_diff = config.INITIAL_QUIZ_DIFFICULTY # Starts at EASY
    for q_idx in range(1, num_questions + 1):
        is_corr = student.answer_question(cur_diff)
        reward = calculate_reward(is_corr, cur_diff)
        rule_cum_reward += reward
        next_diff = get_next_difficulty(cur_diff, is_corr)
        rule_logs.append({
            "question_num": q_idx,
            "difficulty": cur_diff,
            "is_correct": is_corr,
            "reward": reward,
            "next_difficulty": next_diff,
            "cumulative_reward": round(rule_cum_reward, 2)
        })
        cur_diff = next_diff

    # 3. Q-LEARNING ADAPTIVE SYSTEM WITH MANDATORY TRANSITIONS
    agent = QLearningAgent(user_id=-888, alpha=0.1, gamma=0.9, epsilon=0.2)
    q_logs = []
    q_cum_reward = 0.0
    cur_q_diff = config.INITIAL_QUIZ_DIFFICULTY # Starts at EASY
    ep_responses = []

    for ep in range(episodes):
        ep_responses = []
        cur_q_diff = config.INITIAL_QUIZ_DIFFICULTY
        for q_idx in range(1, num_questions + 1):
            state = build_state(cur_q_diff, ep_responses, student.baseline_skill)
            action = config.DIFFICULTY_TO_ACTION[cur_q_diff]

            is_corr = student.answer_question(cur_q_diff)
            reward = calculate_reward(is_corr, cur_q_diff)
            q_cum_reward += reward

            # Mandatory transition dictates next difficulty
            next_q_diff = get_next_difficulty(cur_q_diff, is_corr)
            next_state = build_state(next_q_diff, ep_responses + [{"is_correct": is_corr}], student.baseline_skill)

            # Q-learning Bellman update evaluates the state-action pair
            rl_info = agent.update(state, action, reward, next_state, done=(q_idx == num_questions))

            record = {
                "question_num": q_idx,
                "difficulty": cur_q_diff,
                "is_correct": is_corr,
                "reward": reward,
                "next_difficulty": next_q_diff,
                "cumulative_reward": round(q_cum_reward, 2),
                "q_before": rl_info["q_before"],
                "q_after": rl_info["q_after"],
                "td_error": rl_info["td_error"],
                "state": state
            }
            ep_responses.append(record)

            if ep == episodes - 1:
                q_logs.append(record)

            cur_q_diff = next_q_diff

    # Metrics computation
    fixed_corr = sum(1 for r in fixed_logs if r["is_correct"])
    rule_corr = sum(1 for r in rule_logs if r["is_correct"])
    q_corr = sum(1 for r in q_logs if r["is_correct"])

    fixed_acc = round((fixed_corr / float(num_questions) * 100.0), 1)
    rule_acc = round((rule_corr / float(num_questions) * 100.0), 1)
    q_acc = round((q_corr / float(num_questions) * 100.0), 1)

    return {
        "ability_level": ability_level,
        "num_questions": num_questions,
        "episodes": episodes,
        "fixed_logs": fixed_logs,
        "rule_logs": rule_logs,
        "q_logs": q_logs,
        "fixed_accuracy": fixed_acc,
        "rule_accuracy": rule_acc,
        "q_accuracy": q_acc,
        "fixed_total_reward": round(fixed_logs[-1]["cumulative_reward"], 2),
        "rule_total_reward": round(rule_logs[-1]["cumulative_reward"], 2),
        "q_total_reward": round(q_logs[-1]["cumulative_reward"], 2),
        "fixed_diff_dist": {
            "EASY": sum(1 for r in fixed_logs if r["difficulty"] == "EASY"),
            "MEDIUM": sum(1 for r in fixed_logs if r["difficulty"] == "MEDIUM"),
            "HARD": sum(1 for r in fixed_logs if r["difficulty"] == "HARD"),
        },
        "rule_diff_dist": {
            "EASY": sum(1 for r in rule_logs if r["difficulty"] == "EASY"),
            "MEDIUM": sum(1 for r in rule_logs if r["difficulty"] == "MEDIUM"),
            "HARD": sum(1 for r in rule_logs if r["difficulty"] == "HARD"),
        },
        "q_diff_dist": {
            "EASY": sum(1 for r in q_logs if r["difficulty"] == "EASY"),
            "MEDIUM": sum(1 for r in q_logs if r["difficulty"] == "MEDIUM"),
            "HARD": sum(1 for r in q_logs if r["difficulty"] == "HARD"),
        }
    }
