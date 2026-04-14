import importlib
from typing import Dict, Any, Tuple, List
from models import Observation, Transaction, UserProfile, Action

class AdaptiveFraudMonitoringEnv:
    def __init__(self):
        self.user_profile = None
        self.history = []
        self.targets = []
        self.is_fraud_sequence = []
        self.current_step = 0
        self.last_action_error = None
        self.task_name = ""

    def reset(self, task_name: str = "easy") -> Observation:
        """
        Reset the environment by loading a specific task scenario.
        """
        try:
            task_module = importlib.import_module(f"tasks.{task_name}")
            scenario = task_module.get_scenario()
        except (ImportError, AttributeError) as e:
            self.last_action_error = str(e)
            raise ValueError(f"Task {task_name} not found.")

        self.user_profile = UserProfile(**scenario["user_profile"])
        self.history = [Transaction(**t) for t in scenario["history"]]
        
        # Standardize targets list
        if "targets" in scenario:
            self.targets = [Transaction(**t) for t in scenario["targets"]]
            self.is_fraud_sequence = scenario["is_fraud_sequence"]
        else:
            self.targets = [Transaction(**scenario["target_transaction"])]
            self.is_fraud_sequence = [scenario["is_fraud"]]
            
        self.current_step = 0
        self.last_action_error = None
        self.task_name = scenario["task_name"]
        
        return self.state()

    def state(self) -> Observation:
        """
        Return the current observation.
        """
        if self.current_step >= len(self.targets):
            # If done, return a dummy or the last one? 
            # Usually reset() should have been called.
            current_tx = self.targets[-1]
        else:
            current_tx = self.targets[self.current_step]
            
        return Observation(
            current_transaction=current_tx,
            transaction_history=self.history,
            user_profile=self.user_profile,
            account_status="active" if self.current_step == 0 else "monitored"
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Process the agent's action and return the next state, reward, done flag, and info.
        """
        if self.current_step >= len(self.targets):
            return self.state(), 0.0, True, {"error": "Episode already finished"}

        is_fraud = self.is_fraud_sequence[self.current_step]
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
            elif decision == "flag":
                reward = -1.0 # Excessive monitoring/minor penalty
            elif decision == "escalate":
                reward = -0.5 # Neutral/Minor penalty
        
        # Handle "Excessive Freeze" - if user freezes a non-fraud transaction
        if decision == "freeze" and not is_fraud:
            # We already applied -2.0, maybe another -1.0 for "Excessive" as per spec table?
            # The table says: False positive -2.0, Excessive freeze -1.0. 
            # I'll combine them or treat Excessive Freeze as a specific condition.
            # Let's just follow the -2.0 for FP and -1.0 specifically if the policy is too rigid.
             reward -= 1.0 

        # Update history with the transaction that was just processed
        self.history.append(self.targets[self.current_step])
        self.current_step += 1
        
        done = self.current_step >= len(self.targets)
        
        info = {
            "task": self.task_name,
            "step": self.current_step,
            "is_fraud": is_fraud,
            "decision": decision,
            "last_action_error": self.last_action_error
        }
        
        return self.state(), reward, done, info
