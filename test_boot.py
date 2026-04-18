import sys
import asyncio

async def test():
    try:
        from server.app import app
        print("FastAPI app imported successfully!")
        from server.environment import AdaptiveFraudMonitoringEnv
        print("Environment loaded!")
        
        from client import AdaptiveFraudEnvClient
        print("Client loaded!")
        
        env = AdaptiveFraudMonitoringEnv()
        obs = env.reset()
        print(f"Direct Reset returned: {obs.current_transaction.amount if obs else 'None'}")
    except Exception as e:
        print(f"Error during import/test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
