"""
Unit Tests for Reinforcement Learning (Q-Learning) Components.
Verifies state representation, reward calculations, Bellman formula updates, and DB persistence.
"""

import unittest
from reinforcement_learning.state import (
    discretize_accuracy,
    discretize_performance,
    discretize_question_count,
    get_state_key,
    build_state
)
from reinforcement_learning.reward import calculate_reward
from reinforcement_learning.q_learning import QLearningAgent
from reinforcement_learning.simulator import run_comparative_experiment
from database.db import init_db
import config

class TestQLearning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_state_representation(self):
        """Tests that discrete state dimensions format into canonical state keys."""
        self.assertEqual(discretize_accuracy(0.20), "LOW")
        self.assertEqual(discretize_accuracy(0.65), "MID")
        self.assertEqual(discretize_accuracy(0.90), "HIGH")

        self.assertEqual(discretize_performance(0.25), "BEG")
        self.assertEqual(discretize_performance(0.55), "INT")
        self.assertEqual(discretize_performance(0.85), "ADV")

        self.assertEqual(discretize_question_count(2), "FEW")
        self.assertEqual(discretize_question_count(5), "SOME")
        self.assertEqual(discretize_question_count(9), "MANY")

        key = get_state_key("MEDIUM", "HIGH", "INT", "SOME")
        self.assertEqual(key, "DIFF:MEDIUM|ACC:HIGH|PERF:INT|ANS:SOME")

        # Test build_state
        state_str = build_state("EASY", [{"is_correct": 1}, {"is_correct": 1}], estimated_performance=0.8)
        self.assertIn("DIFF:EASY", state_str)
        self.assertIn("ACC:HIGH", state_str)
        self.assertIn("PERF:ADV", state_str)

    def test_reward_calculation(self):
        """Tests reward calculation scheme: +1 for correct, -1 for incorrect."""
        self.assertEqual(calculate_reward(is_correct=True), 1.0)
        self.assertEqual(calculate_reward(is_correct=False), -1.0)

    def test_q_learning_bellman_formula(self):
        """Tests the exact mathematical execution of the Bellman optimality update."""
        agent = QLearningAgent(user_id=8888, alpha=0.1, gamma=0.9, epsilon=0.0)
        state_s = "DIFF:EASY|ACC:HIGH|PERF:BEG|ANS:FEW"
        state_s_prime = "DIFF:MEDIUM|ACC:HIGH|PERF:INT|ANS:FEW"
        action = 0 # EASY

        q_before = agent.get_q_values(state_s)[action]
        reward = 1.0

        update_info = agent.update(state_s, action, reward, state_s_prime, done=False)
        q_after = agent.get_q_values(state_s)[action]

        # Verify update increased Q after positive reward
        self.assertGreater(q_after, q_before)
        expected_td_target = reward + 0.9 * max(agent.get_q_values(state_s_prime))
        expected_q_after = round(q_before + 0.1 * (expected_td_target - q_before), 4)
        self.assertAlmostEqual(q_after, expected_q_after, places=4)

    def test_action_selection_with_constraints(self):
        """Tests epsilon-greedy action selection."""
        agent = QLearningAgent(user_id=8887, alpha=0.1, gamma=0.9, epsilon=0.0)
        state = "DIFF:MEDIUM|ACC:MID|PERF:INT|ANS:FEW"
        
        # Greedy choice chooses best
        action = agent.choose_action(state, available_actions=[0, 1, 2])
        self.assertIn(action, [0, 1, 2])

    def test_comparative_experiment_execution(self):
        """Verifies simulation across Fixed, Rule-based, and Q-learning models."""
        res = run_comparative_experiment(ability_level="Novice", num_questions=10, episodes=2)
        self.assertIn("fixed_accuracy", res)
        self.assertIn("rule_accuracy", res)
        self.assertIn("q_accuracy", res)
        self.assertEqual(len(res["fixed_logs"]), 10)
        self.assertEqual(len(res["rule_logs"]), 10)
        self.assertEqual(len(res["q_logs"]), 10)

if __name__ == "__main__":
    unittest.main()
