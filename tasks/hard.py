from typing import List, Dict, Any

def get_scenario() -> Dict[str, Any]:
    """
    Hard Task: Coordinated Fraud Pattern
    Scenario: 
    1. Small "ping" transaction in US (test)
    2. Small "ping" transaction in UK (test)
    3. Large transfer in RU (fraud)
    """
    user_profile = {
        "avg_transaction_amount": 200.0,
        "home_country": "US",
        "account_age_days": 1200,
        "risk_score": 0.05
    }
    
    history = [
        {"amount": 180.0, "country": "US", "timestamp": 1712000000, "merchant_category": "services"},
        {"amount": 210.0, "country": "US", "timestamp": 1712100000, "merchant_category": "groceries"}
    ]
    
    # Sequential targets
    targets = [
        {"amount": 1.0, "country": "US", "timestamp": 1712200000, "merchant_category": "charity"}, # Step 1: Probe
        {"amount": 5.0, "country": "UK", "timestamp": 1712203600, "merchant_category": "digital_goods"}, # Step 2: Probe
        {"amount": 5000.0, "country": "RU", "timestamp": 1712207200, "merchant_category": "wire_transfer"} # Step 3: Fraud
    ]
    
    return {
        "user_profile": user_profile,
        "history": history,
        "targets": targets, # Multiple targets for sequential reasoning
        "is_fraud_sequence": [False, False, True],
        "task_name": "Hard - Coordinated Fraud Pattern"
    }
