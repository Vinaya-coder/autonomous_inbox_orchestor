import imaplib
import email
import re
import os
import time
from app.config import settings
from app.models.email_models import EmailLog


class EmailReader:
    def __init__(self, db):
        self.db = db
        self.IMAP_HOST = "imap.gmail.com"
        self.temp_dir = "temp_attachments"
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        self.ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.pdf', '.txt', '.csv'}

    def cleanup_old_attachments(self, max_age_seconds=3600):
        if not os.path.exists(self.temp_dir):
            return
        now = time.time()
        for f in os.listdir(self.temp_dir):
            path = os.path.join(self.temp_dir, f)
            if os.stat(path).st_mtime < now - max_age_seconds:
                try:
                    os.remove(path)
                    print(f"Cleaned up expired file: {f}")
                except Exception as e:
                    print(f" Cleanup error: {e}")

    def fetch_and_save_emails(self):
        self.cleanup_old_attachments()

        print("⏳ Checking inbox for new emails...")
        mail = imaplib.IMAP4_SSL(self.IMAP_HOST)

        try:
            mail.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
            mail.select("inbox")

            status, data = mail.search(None, "UNSEEN")
            if not data[0].split():
                print("No new unseen emails found. AI is staying asleep.")
                return []

            emails = []
            for num in data[0].split():
                status, g_data = mail.fetch(num, "(X-GM-MSGID X-GM-THRID RFC822)")
                header_info = g_data[0][0].decode()
                raw_email_bytes = g_data[0][1]

                msg_id_match = re.search(r'X-GM-MSGID (\d+)', header_info)
                thread_id_match = re.search(r'X-GM-THRID (\d+)', header_info)
                gmail_msg_id = msg_id_match.group(1) if msg_id_match else num.decode()
                gmail_thread_id = thread_id_match.group(1) if thread_id_match else "unknown"

                exists = self.db.query(EmailLog).filter_by(message_id=gmail_msg_id).first()
                if exists:
                    continue

                msg = email.message_from_bytes(raw_email_bytes)
                raw_sender = msg.get("From", "unknown")
                subject = msg.get("Subject", "No Subject")
                rfc_id = msg.get("Message-ID")
                email_match = re.search(r'<([^>]+)>', raw_sender)
                clean_sender_email = email_match.group(1) if email_match else raw_sender
                body = ""
                attachments = []

                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode(errors="ignore")

                    elif "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            ext = os.path.splitext(filename)[1].lower()
                            payload = part.get_payload(decode=True)

                            if ext in self.ALLOWED_EXTENSIONS and len(payload) <= self.MAX_FILE_SIZE:
                                os.makedirs(self.temp_dir, exist_ok=True)
                                filepath = os.path.join(self.temp_dir, f"{gmail_msg_id}_{filename}")
                                with open(filepath, "wb") as f:
                                    f.write(payload)
                                attachments.append(filepath)
                            else:
                                print(f"⏩ Skipping {filename} (Invalid type or too large)")


                emails.append({
                    "message_id": gmail_msg_id,
                    "sender": clean_sender_email,  # Now it's just the email address
                    "subject": subject,
                    "body": body,
                    "rfc_id": rfc_id,
                    "thread_id": gmail_thread_id,  # This is the numeric ID (194f...)
                    "attachments": attachments
                })
            return emails
        finally:
            mail.logout()