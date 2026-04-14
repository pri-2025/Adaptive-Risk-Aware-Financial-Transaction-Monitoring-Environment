from typing import List, Dict, Any

def get_scenario() -> Dict[str, Any]:
    """
    Easy Task: Obvious Anomaly
    Scenario: A user who typically spends small amounts in their home country (US) 
    suddenly has a transaction 10x their average in a different country (RU).
    """
    user_profile = {
        "avg_transaction_amount": 50.0,
        "home_country": "US",
        "account_age_days": 450,
        "risk_score": 0.1
    }
    
    # History of normal transactions
    history = [
        {"amount": 45.0, "country": "US", "timestamp": 1712000000, "merchant_category": "groceries"},
        {"amount": 55.0, "country": "US", "timestamp": 1712100000, "merchant_category": "dining"},
        {"amount": 30.0, "country": "US", "timestamp": 1712200000, "merchant_category": "transport"}
    ]
    
    # The anomaly
    current_transaction = {
        "amount": 500.0, 
        "country": "RU", 
        "timestamp": 1712300000, 
        "merchant_category": "electronics"
    }
    
    return {
        "user_profile": user_profile,
        "history": history,
        "target_transaction": current_transaction,
        "is_fraud": True,
        "task_name": "Easy - Obvious Anomaly"
    }
