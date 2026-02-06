import os
from app.services.email_reader import EmailReader
from app.services.reply_generator import ReplyGenerator
from app.services.email_sender import EmailSender
from app.models.email_models import EmailLog, ChatHistory  # Added ChatHistory
from app.database import SessionLocal


class EmailAgent:
    def __init__(self):
        self.db = SessionLocal()
        self.reader = EmailReader(self.db)

        gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment")

        self.generator = ReplyGenerator()
        self.sender = EmailSender()

    def run(self, cal_service=None):
        # Fetch unread emails
        unread_emails = self.reader.fetch_and_save_emails() or []
        processed = 0

        for email in unread_emails:
            # --- 1. GET THREAD CONTEXT ---
            thread_id = email.get("thread_id")  # Ensure your reader provides this

            # Fetch previous messages in this thread from ChatHistory
            raw_history = self.db.query(ChatHistory).filter(
                ChatHistory.thread_id == thread_id
            ).order_by(ChatHistory.created_at.asc()).all()

            # Format history for Gemini [{"role": "user", "parts": [...]}, ...]
            formatted_history = [
                {"role": log.role, "parts": [log.content]}
                for log in raw_history
            ]

            # --- 2. SAVE INCOMING MESSAGE TO HISTORY ---
            user_msg = ChatHistory(thread_id=thread_id, role="user", content=email["body"])
            self.db.add(user_msg)
            # We commit now so the generator can theoretically see it if needed
            self.db.commit()

            # --- 3. GENERATE REPLY WITH HISTORY ---
            # Now the AI knows if it already sent a link!
            reply_text = self.generator.generate_reply(email, self.db,thread_id,calendar_service=cal_service,thread_history=formatted_history)

            # --- 4. SAVE MODEL REPLY TO HISTORY ---
            ai_msg = ChatHistory(thread_id=thread_id, role="model", content=reply_text)
            self.db.add(ai_msg)
            self.db.commit()

            original_msg_id = email.get('message_id')  # This must be the <xyz@mail.gmail.com> format
            if reply_text:

                self.sender.send_reply(
                    to=email['sender'],
                    subject=email['subject'],
                    body=reply_text,
                    thread_id=email['thread_id'],
                    message_id=email['message_id']
                )
            else:
                print(f"⏩ Skipping email {email['message_id']} because reply is empty (likely Quota Error).")



            # Log the reply in EmailLog (for your dashboard/history)
            try:
                log = EmailLog(
                    message_id=str(email["message_id"]),
                    from_email=str(email["sender"]),
                    subject=str(email["subject"]),
                    body=str(email["body"]),
                    reply_body=str(reply_text),
                    status="SENT"
                )
                self.db.add(log)
                self.db.commit()
            except Exception as e:
                print(f"⚠ Database logging failed: {e}")
                self.db.rollback()

            processed += 1

        return {"processed": processed}