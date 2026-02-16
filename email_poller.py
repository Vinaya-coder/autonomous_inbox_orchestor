import os
import time
import logging
from imap_tools import MailBox,AND
from dotenv import load_dotenv
from celery_app import process_email_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(".env.dev")


class EmailPoller:
    def __init__(self):
        self.user = os.getenv("EMAIL_ADDRESS")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.imap_server = 'imap.gmail.com'
        self.temp_dir = "temp_attachments"
        os.makedirs(self.temp_dir, exist_ok=True)

    def _dispatch_to_celery(self, msg):
        attachment_paths = []

        for att in msg.attachments:
            file_path = os.path.join(self.temp_dir, att.filename)
            with open(file_path, 'wb') as f:
                f.write(att.payload)
            attachment_paths.append(file_path)
        gmail_thread_id = msg.headers.get('x-gm-thrid', [None])[0]
        if not gmail_thread_id:
            gmail_thread_id = msg.uid
        payload = {
            "subject": msg.subject,
            "sender": msg.from_,
            "body": msg.text or msg.html,
            "attachments": attachment_paths,
            "thread_id": str(gmail_thread_id)
        }

        process_email_task.delay(payload)
        logger.info(f"!!! Dispatched task for email: {msg.subject}")

    def run(self):
        if not self.user or not self.password:
            logger.error("❌ Email credentials missing! Check your .env.dev file.")
            return

        logger.info(f"Starting EmailPoller service for {self.user}...")

        while True:
            try:
                with MailBox(self.imap_server).login(self.user, self.password, 'INBOX') as mailbox:
                    for msg in mailbox.fetch(AND(seen=False), mark_seen=True):
                        self._dispatch_to_celery(msg)

                    logger.info("IDLE mode active. Waiting for new messages...")
                    while True:
                        responses = mailbox.idle.wait(timeout=1740)
                        if responses:
                            # Fetch new messages that triggered the IDLE response
                            for msg in mailbox.fetch(AND(seen=False), mark_seen=True):
                                self._dispatch_to_celery(msg)

            except Exception as e:
                logger.error(f"⚠ Connection error: {e}. Retrying in 10s...")
                time.sleep(10)


if __name__ == "__main__":
    poller = EmailPoller()
    poller.run()