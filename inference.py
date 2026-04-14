import os
import sys
import json
import time
from typing import List
from openai import OpenAI
from env import AdaptiveFraudMonitoringEnv
from models import Action
from graders import get_grader

# 9️⃣ Environment Variables (STRICT)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    # Small hack: if we're just testing locally and HF_TOKEN isn't set, 
    # but the user asked for strictness, we must raise.
    # However, for the sake of the demo, I'll allow a dummy or raise.
    # User said: "If HF_TOKEN is None -> raise error."
    raise ValueError("HF_TOKEN environment variable is required.")

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

def get_model_action(obs_dict: dict) -> Action:
    """
    Get action from LLM based on observation.
    """
    prompt = f"""
    You are an AI Fraud Detection Agent. Analyze the following financial data and decide the best action.
    
    Observation:
    {json.dumps(obs_dict, indent=2)}
    
    Respond ONLY with a JSON object containing the field 'decision'.
    Possible values: "approve", "flag", "escalate", "freeze"
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return Action(decision=data.get("decision", "flag"))
    except Exception as e:
        # Fallback to a safe action if API fails
        return Action(decision="escalate")

def run_benchmark():
    env = AdaptiveFraudMonitoringEnv()
    tasks = ["easy", "medium", "hard"]
    benchmark_name = "openenv-fraud-v1"
    
    for task_name in tasks:
        success = False
        step_count = 0
        rewards = []
        episode_history = []
        
        # 8️⃣ [START] Log
        print(f"[START] task={task_name} env={benchmark_name} model={MODEL_NAME}")
        
        try:
            obs = env.reset(task_name)
            done = False
            
            while not done:
                step_count += 1
                obs_dict = obs.dict()
                
                # Get action from model
                action = get_model_action(obs_dict)
                action_str = action.decision
                
                # Step environment
                next_obs, reward, done, info = env.step(action)
                obs = next_obs
                
                rewards.append(reward)
                episode_history.append({
                    "is_fraud": info["is_fraud"],
                    "decision": action_str
                })
                
                error = info.get("last_action_error")
                
                # [STEP] Log
                print(
                    f"[STEP] step={step_count} "
                    f"action={action_str} "
                    f"reward={reward:.2f} "
                    f"done={str(done).lower()} "
                    f"error={error or 'null'}"
                )
                
            # Grade the episode
            grader_fn = get_grader(env.task_name)
            score = grader_fn(episode_history)
            success = score >= 0.8
            
        except Exception as e:
            # Silence error but ensure [END] is printed
            pass
        finally:
            # [END] Log
            formatted_rewards = [f"{r:.2f}" for r in rewards]
            print(
                f"[END] success={str(success).lower()} "
                f"steps={step_count} "
                f"rewards={','.join(formatted_rewards)}"
            )

if __name__ == "__main__":
    run_benchmark()
