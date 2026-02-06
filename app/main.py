from fastapi import FastAPI
from app.api import email_routers
from app.database import engine, Base
from app.models import email_models  # registers models

app = FastAPI(title="Email Auto-Reply Agent")

# ⚠️ TEMPORARY: reset DB for demo
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app.include_router(email_routers.router, prefix="/api/emails")

@app.get("/")
def home():
    return {"message": "Email Agent Running"}
