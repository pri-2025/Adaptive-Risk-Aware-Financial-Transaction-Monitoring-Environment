# Adaptive Fraud Monitoring Environment (OpenEnv)

This repository contains a financial fraud detection RL environment designed for the OpenEnv RL Challenge. It simulates a transaction monitoring system where an AI agent must make real-time decisions on transactions to balance risk and customer experience.

## Project Structure

- `inference.py`: Root entry point for high-speed benchmark execution.
- `env.py`: The core Reinforcement Learning environment.
- `models.py`: Pydantic models for transactions, observations, and actions.
- `tasks/`: Scenario definitions (Easy, Medium, Hard).
- `graders.py`: Deterministic scoring logic for benchmarking.
- `openenv.yaml`: OpenEnv environment configuration.
- `Dockerfile`: Container configuration for submission.

## Environment Logic

### Actions
- `approve`: Process the transaction.
- `flag`: Mark for review but don't block.
- `escalate`: Send to a human investigator.
- `freeze`: Block the account immediately.

### Reward System
| Case | Reward |
|------|--------|
| Correct fraud detection | +4.0 |
| Correct approval | +1.0 |
| False positive | -2.0 |
| Missed fraud | -5.0 |
| Excessive freeze | -1.0 |

## Getting Started

### Prerequisites
- Python 3.10+
- OpenAI API Key (Required via `HF_TOKEN`)

### Running Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   ```bash
   # Windows
   $env:HF_TOKEN="your_api_key"
   $env:MODEL_NAME="gpt-4.1-mini"
   ```
3. Execute the benchmark:
   ```bash
   python inference.py
   ```

### Docker
```bash
docker build -t fraud-env .
docker run -e HF_TOKEN="your_key" fraud-env
```

## Compliance
- Aligned with OpenEnv RL Challenge specifications.
- Deterministic grading and stdout logging format (`[START]`, `[STEP]`, `[END]`).
- Lightweight Docker image under 8GB RAM limit.