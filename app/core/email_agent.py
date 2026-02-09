import os
from app.utils.email_reader import EmailReader
from app.utils.email_sender import EmailSender
from app.logic.reply_generator import ReplyGenerator
from app.models.email_models import EmailLog, ChatHistory
from app.database import SessionLocal


class EmailAgent:
    def __init__(self, db=None):
        self.db = db if db else SessionLocal()
        self.reader = EmailReader(self.db)
        self.generator = ReplyGenerator()
        self.sender = EmailSender()

    def run(self, cal_service=None):
        unread_emails = self.reader.fetch_and_save_emails() or []
        processed = 0

        for email in unread_emails:
            msg_id = str(email["message_id"])
            thread_id = str(email["thread_id"])

            # 🛑 ANTI-LOOP CHECK: Have we already logged this message?
            already_processed = self.db.query(EmailLog).filter_by(message_id=msg_id).first()
            if already_processed:
                continue

            # 1. GET THREAD CONTEXT (Your stable logic)
            raw_history = self.db.query(ChatHistory).filter(
                ChatHistory.thread_id == thread_id
            ).order_by(ChatHistory.created_at.asc()).all()

            formatted_history = [
                {"role": log.role, "parts": [log.content]}
                for log in raw_history
            ]

            # 2. SAVE INCOMING MESSAGE TO HISTORY
            user_msg = ChatHistory(thread_id=thread_id, role="user", content=email["body"])
            self.db.add(user_msg)
            self.db.commit()

            # 3. GENERATE REPLY (This now sees the history)
            reply_text = self.generator.generate_reply(
                email,
                self.db,
                thread_id,
                calendar_service=cal_service,
                thread_history=formatted_history
            )

            if reply_text:
                # 4. SAVE MODEL REPLY TO HISTORY
                ai_msg = ChatHistory(thread_id=thread_id, role="model", content=reply_text)
                self.db.add(ai_msg)

                # 5. SEND THE EMAIL
                self.sender.send_reply(
                    to=email['sender'],
                    subject=email['subject'],
                    body=reply_text,
                    thread_id=thread_id,
                    message_id=email['rfc_id']  # Use RFC ID for threading
                )

                # 6. LOG TO EMAIL_LOG
                try:
                    log = EmailLog(
                        message_id=msg_id,
                        from_email=email["sender"],
                        subject=email["subject"],
                        body=email["body"],
                        reply_body=reply_text,
                        status="SENT"
                    )
                    self.db.add(log)
                    self.db.commit()
                except Exception as e:
                    print(f"⚠ Database logging failed: {e}")
                    self.db.rollback()

            processed += 1
        return {"processed": processed}