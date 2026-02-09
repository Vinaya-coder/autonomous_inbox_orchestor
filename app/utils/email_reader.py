import imaplib
import email
import re
from app.config import settings
from app.models.email_models import EmailLog


class EmailReader:
    def __init__(self, db):
        self.db = db
        self.IMAP_HOST = "imap.gmail.com"

    def fetch_and_save_emails(self):
        print("⏳ Checking inbox for new emails...")
        mail = imaplib.IMAP4_SSL(self.IMAP_HOST)
        try:
            mail.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
            mail.select("inbox")

            # Search for UNSEEN emails
            status, data = mail.search(None, "UNSEEN")
            emails = []

            for num in data[0].split():
                # We fetch X-GM-MSGID (Permanent ID) and X-GM-THRID (Thread ID)
                status, g_data = mail.fetch(num, "(X-GM-MSGID X-GM-THRID RFC822)")
                header_info = g_data[0][0].decode()
                raw_email = g_data[0][1]

                # Extract the Permanent Gmail IDs using Regex
                msg_id_match = re.search(r'X-GM-MSGID (\d+)', header_info)
                thread_id_match = re.search(r'X-GM-THRID (\d+)', header_info)

                gmail_msg_id = msg_id_match.group(1) if msg_id_match else num.decode()
                thread_id = thread_id_match.group(1) if thread_id_match else gmail_msg_id

                # 🛑 ANTI-LOOP: Check DB using the Permanent Gmail Message ID
                exists = self.db.query(EmailLog).filter_by(message_id=gmail_msg_id).first()
                if exists:
                    continue

                msg = email.message_from_bytes(raw_email)

                # RFC Message-ID is needed for 'In-Reply-To' headers
                rfc_id = msg.get("Message-ID")
                sender = msg.get("From", "unknown")
                subject = msg.get("Subject", "No Subject")

                # Extract Body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                emails.append({
                    "message_id": gmail_msg_id,  # Permanent ID for DB
                    "rfc_id": rfc_id,  # Reference ID for Sending
                    "thread_id": thread_id,  # ID for grouping conversation
                    "sender": sender,
                    "subject": subject,
                    "body": body
                })

            return emails
        finally:
            mail.logout()