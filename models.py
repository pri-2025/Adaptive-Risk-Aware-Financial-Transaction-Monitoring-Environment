from pydantic import BaseModel, Field, validator
from typing import List, Literal

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

class Observation(BaseModel):
    current_transaction: Transaction
    transaction_history: List[Transaction]
    user_profile: UserProfile
    account_status: str

class Action(BaseModel):
    decision: Literal["approve", "flag", "escalate", "freeze"]
