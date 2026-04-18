from openenv.core.env_server import create_fastapi_app
from server.environment import AdaptiveFraudMonitoringEnv

app = create_fastapi_app(AdaptiveFraudMonitoringEnv)
