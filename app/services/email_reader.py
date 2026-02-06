import imaplib
import email
from app.config import settings
from app.models.email_models import EmailLog
from datetime import datetime, date


def safe_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value

class EmailReader:
    def __init__(self, db):
        self.db = db
        self.IMAP_HOST = "imap.gmail.com"

    def fetch_and_save_emails(self, gmail_db_id=None):
        print("⏳ Checking inbox for emails...")

        mail = imaplib.IMAP4_SSL(self.IMAP_HOST)
        mail.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        mail.select("inbox")

        status, data = mail.search(None, "UNSEEN")

        emails = []

        for num in data[0].split():

            status, g_data = mail.fetch(num, "(X-GM-MSGID X-GM-THRID RFC822)")
            header_info = g_data[0][0].decode()

            import re
            msg_id_match = re.search(r'X-GM-MSGID (\d+)', header_info)
            thread_id_match = re.search(r'X-GM-THRID (\d+)', header_info)

            gmail_msg_id = msg_id_match.group(1) if msg_id_match else num.decode()
            thread_id = thread_id_match.group(1) if thread_id_match else gmail_msg_id

            # Skip if already logged using the PERMANENT Gmail ID
            exists = self.db.query(EmailLog).filter_by(message_id=gmail_db_id).first()
            if exists:
                continue

            msg = email.message_from_bytes(g_data[0][1])
            rfc_message_id = msg.get("Message-ID")
            sender = msg.get("From", "unknown")
            subject = msg.get("Subject", "No Subject")
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and "attachment" not in str(
                            part.get("Content-Disposition")):
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            emails.append({
                "db_id": gmail_db_id,
                "thread_id": thread_id,
                "message_id": rfc_message_id,
                "sender": safe_value(sender),
                "subject": safe_value(subject),
                "body": safe_value(body)
            })

        mail.logout()
        return emails
