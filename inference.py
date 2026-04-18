import os
import sys
import json
import time
from typing import List
from openai import OpenAI
from client import AdaptiveFraudEnvClient
from models import FraudAction
from graders import get_grader

# 9️⃣ Environment Variables (STRICT)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required.")

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

def get_model_action(obs_dict: dict) -> FraudAction:
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
        return FraudAction(decision=data.get("decision", "flag"))
    except Exception as e:
        # Fallback to a safe action if API fails
        return FraudAction(decision="escalate")

def run_benchmark():
    tasks = ["easy", "medium", "hard"]
    benchmark_name = "openenv-fraud-v1"
    
    with AdaptiveFraudEnvClient(base_url="http://localhost:8000").sync() as env:
        for task_name in tasks:
            success = False
            step_count = 0
            rewards = []
            episode_history = []
            
            # 8️⃣ [START] Log
            print(f"[START] task={task_name} env={benchmark_name} model={MODEL_NAME}")
            
            try:
                result = env.reset(task_name=task_name)
                obs = result.observation
                done = result.done
                
                while not done:
                    step_count += 1
                    obs_dict = obs.dict()
                    
                    # Get action from model
                    action = get_model_action(obs_dict)
                    action_str = action.decision
                    
                    # Step environment
                    result = env.step(action)
                    obs = result.observation
                    done = result.done
                    reward = result.reward
                    
                    rewards.append(reward)
                    episode_history.append({
                        "is_fraud": obs.info_is_fraud,
                        "decision": action_str
                    })
                    
                    error = obs.last_action_error
                    
                    # [STEP] Log
                    print(
                        f"[STEP] step={step_count} "
                        f"action={action_str} "
                        f"reward={reward:.2f} "
                        f"done={str(done).lower()} "
                        f"error={error or 'null'}"
                    )
                    
                # Grade the episode
                grader_fn = get_grader(obs.info_task or task_name)
                score = grader_fn(episode_history)
                success = score >= 0.8
                
            except Exception as e:
                # Silence error but ensure [END] is printed
                print(f"Error during episode: {e}")
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
