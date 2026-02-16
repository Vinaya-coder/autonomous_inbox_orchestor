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
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
        self.USER_INFO_FILE: str = "vinaya_info.txt"

    def get_instructions(self):
        instruction_path = base_dir / "instructions.txt"
        try:
            with open(instruction_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "You are a professional executive assistant."
settings = Settings()
EMAIL_ADDRESS = settings.EMAIL_ADDRESS
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
DATABASE_URL = settings.DATABASE_URL
OPENAI_API_KEY = settings.OPENAI_API_KEY
