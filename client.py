from typing import Any
from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from models import FraudAction, FraudObservation, FraudState, Transaction, UserProfile

class AdaptiveFraudEnvClient(EnvClient[FraudAction, FraudObservation, FraudState]):
    def _step_payload(self, action: FraudAction) -> dict:
        return {"decision": action.decision}

    def _parse_result(self, payload: dict) -> StepResult:
        obs_data = payload.get("observation", {})
        
        return StepResult(
            observation=FraudObservation(
                done=payload.get("done", False),
                reward=payload.get("reward"),
                current_transaction=Transaction(**obs_data.get("current_transaction", {})),
                transaction_history=[Transaction(**t) for t in obs_data.get("transaction_history", [])],
                user_profile=UserProfile(**obs_data.get("user_profile", {})) if obs_data.get("user_profile") else None,
                account_status=obs_data.get("account_status", "active"),
                last_action_error=obs_data.get("last_action_error"),
                info_is_fraud=obs_data.get("info_is_fraud"),
                info_task=obs_data.get("info_task", ""),
                info_step=obs_data.get("info_step", 0)
            ),
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> FraudState:
        return FraudState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            targets=[Transaction(**t) for t in payload.get("targets", [])],
            is_fraud_sequence=payload.get("is_fraud_sequence", []),
            user_profile=UserProfile(**payload.get("user_profile", {})) if payload.get("user_profile") else None,
            history=[Transaction(**t) for t in payload.get("history", [])],
            last_action_error=payload.get("last_action_error"),
            task_name=payload.get("task_name", "")
        )
