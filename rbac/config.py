import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Load .env from project root explicitly
env_path = find_dotenv()
if not env_path:
    # try one directory up from this file
    env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=str(env_path))

DB_HOST = os.getenv("DB_HOST", "57.159.27.239")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "customer_support")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

