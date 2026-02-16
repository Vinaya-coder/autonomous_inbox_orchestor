import sys

from celery import Celery
import os
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
load_dotenv(".env.dev")

app = Celery('email_agent',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

@app.task(bind=True, max_retries=5)
def process_email_task(self,payload):
    from app.core.email_agent import EmailAgent
    from app.database import SessionLocal
    from google.api_core import exceptions

    db = SessionLocal()
    try:
        agent = EmailAgent(db=db)
        result = agent.process_single_email(payload)
        return result
    except exceptions.ResourceExhausted as e:
        print(f"Gemini is tired. Retrying in 60s... (Attempt {self.request.retries})")
        raise self.retry(exc=e, countdown=60)
    except Exception as e:
        print(f"❌ Permanent Failure: {str(e)}")
        return {"error": str(e)}
    finally:
        db.close()