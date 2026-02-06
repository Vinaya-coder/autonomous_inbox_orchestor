import os
from dotenv import load_dotenv

load_dotenv(".env.dev")

class Settings:
    def __init__(self):
        self.EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS")
        self.EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")
        self.JWT_SECRET: str = os.getenv("JWT_SECRET")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

# Create instance
settings = Settings()

# Optional: sanity check
print("Loaded DATABASE_URL:", settings.DATABASE_URL)
