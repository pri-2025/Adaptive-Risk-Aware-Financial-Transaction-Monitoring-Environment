from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from openenv.core.env_server import Action, Observation, State

class Transaction(BaseModel):
    amount: float
    country: str
    timestamp: int
    merchant_category: str

class UserProfile(BaseModel):
    avg_transaction_amount: float
    home_country: str
    account_age_days: int
    risk_score: float

class FraudAction(Action):
    decision: Literal["approve", "flag", "escalate", "freeze"]

class FraudObservation(Observation):
    current_transaction: Transaction
    transaction_history: List[Transaction]
    user_profile: UserProfile
    account_status: str
    # Making info fields explicitly available in the observation model, as OpenAI agents may need them
    last_action_error: Optional[str] = None

class FraudState(State):
    targets: List[Transaction] = Field(default_factory=list)
    is_fraud_sequence: List[bool] = Field(default_factory=list)
    user_profile: Optional[UserProfile] = None
    history: List[Transaction] = Field(default_factory=list)
    last_action_error: Optional[str] = None
    task_name: str = ""
