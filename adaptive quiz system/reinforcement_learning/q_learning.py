"""
Tabular Q-Learning Agent Module for Adaptive Question Difficulty Evaluation.
Implements the Bellman optimality equation, epsilon-greedy action selection,
and SQLite persistence for both global and student-specific policies.
"""

import random
from typing import Dict, List, Optional, Tuple, Any
import config
from database.db import execute_query, execute_insert, execute_update

class QLearningAgent:
    """
    Tabular Q-learning agent evaluating question difficulty actions:
        Action 0: EASY
        Action 1: MEDIUM
        Action 2: HARD
    Formula:
        Q(s, a) = Q(s, a) + alpha * [reward + gamma * max_a' Q(next_state, a') - Q(s, a)]
    """
    def __init__(
        self,
        user_id: int = 0,
        alpha: float = config.RL_ALPHA,
        gamma: float = config.RL_GAMMA,
        epsilon: float = config.RL_EPSILON
    ):
        self.user_id = user_id
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.num_actions = len(config.ACTION_TO_DIFFICULTY)
        # Q-table mapping: state_key -> list of 3 float Q-values [Q(s, EASY), Q(s, MEDIUM), Q(s, HARD)]
        self.q_table: Dict[str, List[float]] = {}
        self.load_q_table()

    def get_q_values(self, state_key: str) -> List[float]:
        """Returns Q-values for a state, initializing to [0.0, 0.0, 0.0] if unseen."""
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0, 0.0, 0.0]
        return self.q_table[state_key]

    def choose_action(
        self,
        state_key: str,
        available_actions: Optional[List[int]] = None
    ) -> int:
        """
        Selects an action using the epsilon-greedy policy.
        """
        if available_actions is None or len(available_actions) == 0:
            available_actions = [0, 1, 2]

        # Exploration: pick a random action with probability epsilon
        if random.random() < self.epsilon:
            return random.choice(available_actions)

        # Exploitation: pick greedy action with highest Q-value (break ties randomly)
        q_vals = self.get_q_values(state_key)
        best_val = -float("inf")
        best_actions = []

        for a in available_actions:
            val = q_vals[a]
            if val > best_val:
                best_val = val
                best_actions = [a]
            elif abs(val - best_val) < 1e-6:
                best_actions.append(a)

        return random.choice(best_actions)

    def update(
        self,
        state: str,
        action: int,
        reward: float,
        next_state: str,
        done: bool = False
    ) -> Dict[str, Any]:
        """
        Applies the Bellman update:
            Q(s, a) = Q(s, a) + alpha * [reward + gamma * max_a' Q(s', a') - Q(s, a)]
        Returns detailed transition analytics:
            {
                "q_before": float,
                "q_after": float,
                "td_error": float,
                "td_target": float,
                "max_next_q": float
            }
        """
        current_q = self.get_q_values(state)[action]

        if done:
            max_next_q = 0.0
        else:
            next_q_vals = self.get_q_values(next_state)
            max_next_q = max(next_q_vals)

        # Target and TD error calculation
        td_target = reward + self.gamma * max_next_q
        td_error = td_target - current_q

        # Q-value update
        new_q = current_q + self.alpha * td_error
        self.q_table[state][action] = round(new_q, 4)

        # Persist single state-action update to SQLite database
        self.persist_q_value(state, action, new_q)

        return {
            "q_before": round(current_q, 4),
            "q_after": round(new_q, 4),
            "td_error": round(td_error, 4),
            "td_target": round(td_target, 4),
            "max_next_q": round(max_next_q, 4)
        }

    def persist_q_value(self, state: str, action: int, q_value: float) -> None:
        """Saves a single Q-value update into the SQLite q_values table."""
        try:
            execute_update(
                """
                INSERT INTO q_values (user_id, state_key, action, q_value, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, state_key, action)
                DO UPDATE SET q_value = excluded.q_value, updated_at = CURRENT_TIMESTAMP
                """,
                (self.user_id, state, action, q_value)
            )
        except Exception:
            pass

    def load_q_table(self) -> None:
        """Loads Q-values from SQLite for this user (with global fallback)."""
        self.q_table = {}

        # 1. Load global baseline if user agent
        if self.user_id != 0:
            global_rows = execute_query(
                "SELECT state_key, action, q_value FROM q_values WHERE user_id = 0"
            )
            for row in global_rows:
                state = row["state_key"]
                action = row["action"]
                val = row["q_value"]
                if state not in self.q_table:
                    self.q_table[state] = [0.0, 0.0, 0.0]
                self.q_table[state][action] = val

        # 2. Load user-specific rows
        user_rows = execute_query(
            "SELECT state_key, action, q_value FROM q_values WHERE user_id = ?",
            (self.user_id,)
        )
        for row in user_rows:
            state = row["state_key"]
            action = row["action"]
            val = row["q_value"]
            if state not in self.q_table:
                self.q_table[state] = [0.0, 0.0, 0.0]
            self.q_table[state][action] = val

    def get_policy_summary(self) -> List[Dict[str, Any]]:
        """Returns structured Q-table entries for visualization and inspection."""
        summary = []
        for state, q_vals in sorted(self.q_table.items()):
            best_action = int(max(range(len(q_vals)), key=lambda i: q_vals[i]))
            summary.append({
                "State": state,
                "Q(EASY)": round(q_vals[0], 4),
                "Q(MEDIUM)": round(q_vals[1], 4),
                "Q(HARD)": round(q_vals[2], 4),
                "Highest Q Difficulty": config.ACTION_TO_DIFFICULTY[best_action]
            })
        return summary
