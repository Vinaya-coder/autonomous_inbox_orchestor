import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


class EmailSender:
    def __init__(self):
        # Using 465 for SMTP_SSL
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 465
        self.email_address = settings.EMAIL_ADDRESS
        self.email_password = settings.EMAIL_PASSWORD

    def send_reply(self, to, subject, body, thread_id=None, message_id=None):
        """
        'to' is the recipient email.
        'message_id' is the ID of the email you are replying to.
        """
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = to

        # Standardize Subject
        msg['Subject'] = subject if subject.lower().startswith("re:") else f"Re: {subject}"

        # 🧠 THREAD POOLING (Vara Scenario)
        if message_id:
            msg['In-Reply-To'] = message_id
            msg['References'] = message_id

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            print(f"📨 Reply sent to {to} in thread {thread_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False