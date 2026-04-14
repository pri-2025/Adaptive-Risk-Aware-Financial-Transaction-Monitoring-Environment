from typing import List, Dict, Any

def get_scenario() -> Dict[str, Any]:
    """
    Medium Task: Behavioral Drift
    Scenario: A user starts increasing their spending patterns and visits a 
    neighboring country (CA) for a new category (luxury_goods). 
    This is suspicious but might be legitimate drift or escalation.
    """
    user_profile = {
        "avg_transaction_amount": 100.0,
        "home_country": "US",
        "account_age_days": 800,
        "risk_score": 0.2
    }
    
    # History showing gradual increase
    history = [
        {"amount": 100.0, "country": "US", "timestamp": 1712000000, "merchant_category": "groceries"},
        {"amount": 150.0, "country": "US", "timestamp": 1712100000, "merchant_category": "travel"},
        {"amount": 250.0, "country": "US", "timestamp": 1712200000, "merchant_category": "retail"}
    ]
    
    # The drift
    current_transaction = {
        "amount": 800.0, 
        "country": "CA", 
        "timestamp": 1712300000, 
        "merchant_category": "luxury_goods"
    }
    
    return {
        "user_profile": user_profile,
        "history": history,
        "target_transaction": current_transaction,
        "is_fraud": False, # This is a "grey area" - let's say it's not fraud but requires 'escalate' or 'flag'
        "task_name": "Medium - Behavioral Drift"
    }
