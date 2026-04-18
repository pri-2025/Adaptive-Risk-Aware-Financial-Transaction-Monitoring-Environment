import importlib
import uuid
import sys
import os
from typing import Optional

# Ensure that the root directory is on the path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openenv.core.env_server import Environment
from models import FraudObservation, FraudAction, FraudState, Transaction, UserProfile

class AdaptiveFraudMonitoringEnv(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self._state = FraudState()

    def reset(self, seed=None, episode_id=None, task_name: str = "easy", **kwargs) -> FraudObservation:
        """
        Reset the environment by loading a specific task scenario.
        """
        try:
            task_module = importlib.import_module(f"tasks.{task_name}")
            scenario = task_module.get_scenario()
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Task {task_name} not found.")

        # Standardize targets list
        if "targets" in scenario:
            targets = [Transaction(**t) for t in scenario["targets"]]
            is_fraud_sequence = scenario["is_fraud_sequence"]
        else:
            targets = [Transaction(**scenario["target_transaction"])]
            is_fraud_sequence = [scenario["is_fraud"]]

        self._state = FraudState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            user_profile=UserProfile(**scenario["user_profile"]),
            history=[Transaction(**t) for t in scenario["history"]],
            targets=targets,
            is_fraud_sequence=is_fraud_sequence,
            last_action_error=None,
            task_name=scenario.get("task_name", task_name)
        )
        
        return self._current_observation(done=False, reward=None)

    def step(self, action: FraudAction, timeout_s=None, **kwargs) -> FraudObservation:
        """
        Process the agent's action and return the next state, reward, done flag, and info.
        """
        if self._state.step_count >= len(self._state.targets):
            self._state.last_action_error = "Episode already finished"
            return self._current_observation(done=True, reward=0.0)

        is_fraud = self._state.is_fraud_sequence[self._state.step_count]
        decision = action.decision
        reward = 0.0
        
        # Reward Logic based on OpenEnv Blueprint
        if is_fraud:
            if decision in ["flag", "freeze", "escalate"]:
                reward = 4.0
            else: # approve
                reward = -5.0
        else:
            if decision == "approve":
                reward = 1.0
            elif decision == "freeze":
                reward = -2.0 # False Positive
                reward -= 1.0 # Excessive Freeze penalty
            elif decision == "flag":
                reward = -1.0 # Minor penalty
            elif decision == "escalate":
                reward = -0.5 # Neutral/Minor penalty

        # Update history with the transaction that was just processed
        processed_tx = self._state.targets[self._state.step_count]
        self._state.history.append(processed_tx)
        
        # We store the previous info so we can return it inside the observation
        self._last_is_fraud = is_fraud
        self._state.step_count += 1
        
        done = self._state.step_count >= len(self._state.targets)
        
        return self._current_observation(done=done, reward=reward, is_fraud=is_fraud)

    def _current_observation(self, done: bool, reward: Optional[float], is_fraud: Optional[bool] = None) -> FraudObservation:
        if self._state.step_count >= len(self._state.targets):
            current_tx = self._state.targets[-1] if self._state.targets else None
        else:
            current_tx = self._state.targets[self._state.step_count]
            
        return FraudObservation(
            done=done,
            reward=reward,
            current_transaction=current_tx,
            transaction_history=self._state.history,
            user_profile=self._state.user_profile,
            account_status="active" if self._state.step_count == 0 else "monitored",
            last_action_error=self._state.last_action_error,
            info_is_fraud=is_fraud,
            info_task=self._state.task_name,
            info_step=self._state.step_count
        )

    @property
    def state(self) -> FraudState:
        return self._state
