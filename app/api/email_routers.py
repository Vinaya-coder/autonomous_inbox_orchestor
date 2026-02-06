from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.email_agent import EmailAgent

router = APIRouter(prefix="/agent", tags=["Email Agent"])

@router.post("/fetch-and-reply")
def run_email_agent(db: Session = Depends(get_db)):
    agent = EmailAgent( )
    return agent.run()
