import os
from dotenv import load_dotenv

load_dotenv()

SERVER_NAME = os.getenv("SERVER_NAME", "my-mcp-server")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
