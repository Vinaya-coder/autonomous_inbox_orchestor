from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base
import datetime

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    replied = Column(Boolean, default=False)

class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    from_email = Column(String)
    subject = Column(String)
    body = Column(Text)
    reply_body = Column(Text)
    status = Column(String)

class ReplyContext(Base):
    __tablename__ = "reply_contexts"
    id = Column(Integer, primary_key=True, index=True)
    context_type = Column(String, index=True)
    keywords = Column(String)
    content = Column(Text)
    sender_email = Column(String, nullable=True)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'model'
    content = Column(Text)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )