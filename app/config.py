import os
from pathlib import Path
from dotenv import load_dotenv
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env.dev"

load_dotenv(dotenv_path=env_path)

class Settings:
    def __init__(self):
        self.EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS")
        self.EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")
        self.JWT_SECRET: str = os.getenv("JWT_SECRET")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings()

EMAIL_ADDRESS = settings.EMAIL_ADDRESS
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
DATABASE_URL = settings.DATABASE_URL
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
OPENAI_API_KEY = settings.OPENAI_API_KEY

if settings.DATABASE_URL:
    print(f"✅ Config loaded. DB Path: {settings.DATABASE_URL}")
else:
    print("❌ WARNING: DATABASE_URL not found. Check your .env.dev file location.")