import sys
from celery import Celery
import os
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
load_dotenv(".env.dev")

app = Celery('email_agent',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

@app.task
def process_email_task():
    from app.core.email_agent import EmailAgent
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        agent = EmailAgent(db=db)
        result = agent.run()
        return result
    finally:
        db.close()