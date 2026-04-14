from typing import List, Dict, Any

class Grader:
    @staticmethod
    def grade_easy(history: List[Dict[str, Any]]) -> float:
        """
        Easy Grader: 1.0 if correct action (detect fraud), 0.0 otherwise.
        """
        if not history: return 0.0
        last_step = history[-1]
        # Easy task target is fraud. Correct detection = freeze, flag, or escalate.
        if last_step["is_fraud"] and last_step["decision"] in ["freeze", "flag", "escalate"]:
            return 1.0
        return 0.0

    @staticmethod
    def grade_medium(history: List[Dict[str, Any]]) -> float:
        """
        Medium Grader: 1.0 correct, 0.5 if escalate, 0.0 otherwise.
        """
        if not history: return 0.0
        last_step = history[-1]
        # Medium target was NOT fraud (behavioral drift).
        # Correct action = approve (1.0) or escalate (0.5).
        if not last_step["is_fraud"]:
            if last_step["decision"] == "approve":
                return 1.0
            if last_step["decision"] == "escalate":
                return 0.5
        return 0.0

    @staticmethod
    def grade_hard(history: List[Dict[str, Any]]) -> float:
        """
        Hard Grader: Check correct detection BEFORE final large fraud.
        Sequence: [False, False, True]
        Correct if they flagged/escalated during probe or froze correctly at the end.
        """
        if not history: return 0.0
        
        # Check if they flagged/escalated/froze at ANY step in the sequence [False, False, True]
        # Especially before the final fraud.
        detected_preshock = any(
            h["decision"] in ["flag", "escalate", "freeze"] 
            for h in history[:-1] # The first two 'False' fraud steps
        )
        
        final_step = history[-1]
        detected_final = final_step["decision"] in ["freeze", "flag", "escalate"] and final_step["is_fraud"]
        
        if detected_preshock:
            return 1.0 # Sequential reasoning bonus
        if detected_final:
            return 0.8 # Correct finale but missed the signs
            
        return 0.0

def get_grader(task_type: str):
    if "Easy" in task_type:
        return Grader.grade_easy
    if "Medium" in task_type:
        return Grader.grade_medium
    if "Hard" in task_type:
        return Grader.grade_hard
    return lambda x: 0.0
