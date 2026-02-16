import os
import shutil
from app.utils.email_reader import EmailReader
from app.utils.email_sender import EmailSender
from app.logic.reply_generator import ReplyGenerator
from app.models.email_models import EmailLog, ChatHistory
from app.database import SessionLocal
from datetime import datetime

class EmailAgent:
    def __init__(self, db=None):
        self.db = db if db else SessionLocal()
        self.reader = EmailReader(self.db)
        self.generator = ReplyGenerator()
        self.sender = EmailSender()

    def process_single_email(self, payload):
        email_obj = {
            "message_id": payload.get("message_id", str(hash(payload['subject']))),  # Fallback if ID missing
            "thread_id": payload.get("thread_id", payload['sender']),
            "rfc_id": payload.get("rfc_id", ""),
            "sender": payload['sender'],
            "subject": payload['subject'],
            "body": payload['body'],
            "attachments": payload.get("attachments", [])
        }

        return self._execute_core_logic(email_obj)

    def run(self, cal_service=None):
        unread_emails = self.reader.fetch_and_save_emails() or []
        processed = 0
        for email_obj in unread_emails:
            self._execute_core_logic(email_obj, cal_service)
            processed += 1
        return {"processed": processed}

    def _execute_core_logic(self, email_obj, cal_service=None):
        msg_id = str(email_obj["message_id"])
        thread_id = str(email_obj["thread_id"])
        current_attachments = email_obj.get("attachments", [])
        already_processed = self.db.query(EmailLog).filter_by(message_id=msg_id).first()
        if already_processed:
            return {"status": "already_processed"}
        raw_history = self.db.query(ChatHistory).filter(
            ChatHistory.thread_id == thread_id
        ).order_by(ChatHistory.created_at.asc()).all()
        formatted_history = [
            {"role": log.role, "parts": [log.content]}
            for log in raw_history
        ]

        user_msg = ChatHistory(thread_id=thread_id, role="user", content=email_obj["body"])
        self.db.add(user_msg)
        self.db.commit()

        reply_text = self.generator.generate_reply(
            email_obj=email_obj,
            db=self.db,
            thread_id=thread_id,
            calendar_service=cal_service,
            thread_history=formatted_history,
            attachments=current_attachments
        )

        if reply_text:
            ai_msg = ChatHistory(thread_id=thread_id, role="model", content=reply_text)
            self.db.add(ai_msg)

            self.sender.send_reply(
                to=email_obj['sender'],
                subject=email_obj['subject'],
                body=reply_text,
                thread_id=thread_id,
                message_id=email_obj.get('rfc_id', '')
            )

            try:
                log = EmailLog(
                    message_id=msg_id,
                    from_email=email_obj["sender"],
                    subject=email_obj["subject"],
                    body=email_obj["body"],
                    reply_body=reply_text,
                    status="SENT"
                )
                self.db.add(log)
                self.db.commit()
            except Exception as e:
                print(f"⚠ Database logging failed: {e}")
                self.db.rollback()

            return {"status": "success", "msg_id": msg_id}

        return {"status": "skipped"}