import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# --- PATH LOGIC ---
# This looks 2 levels up from app/providers/ to reach the root 'email_agent' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CRED_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')


class EmailClient:
    def __init__(self):
        self.service = self.authenticate()

    def authenticate(self):
        creds = None
        # Check for token.json in the root folder
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                # Check for credentials.json in the root folder
                if not os.path.exists(CRED_FILE):
                    raise FileNotFoundError(f"🚨 CRITICAL: {CRED_FILE} not found in root!")

                flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def fetch_unread_emails(self):
        """Fetch unread emails from Gmail inbox."""
        try:
            results = self.service.users().messages().list(userId='me', q="is:unread").execute()
            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                message = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = message['payload']['headers']

                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")

                # IMPORTANT: Extract threadId and rfc_id for Vidya scenario
                thread_id = message['threadId']
                rfc_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), None)

                body = self._get_body(message['payload'])

                emails.append({
                    "message_id": msg['id'],
                    "thread_id": thread_id,
                    "rfc_id": rfc_id,
                    "subject": subject,
                    "sender": sender,
                    "body": body
                })

            return emails
        except HttpError as error:
            print(f'❌ Gmail API Error: {error}')
            return []

    def _get_body(self, payload):
        """Extract body from Gmail message payload."""
        parts = payload.get('parts')
        data = None
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    break
        else:
            data = payload['body'].get('data')

        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
        return ""

    def send_reply(self, to: str, subject: str, body: str, thread_id: str = None, message_id: str = None):
        """Send threaded reply using Gmail API."""
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject if subject.lower().startswith("re:") else f"Re: {subject}"

        # Threading Headers
        if message_id:
            message['In-Reply-To'] = message_id
            message['References'] = message_id

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body_obj = {'raw': raw}
        if thread_id:
            body_obj['threadId'] = thread_id

        try:
            self.service.users().messages().send(userId='me', body=body_obj).execute()
            return True
        except HttpError as error:
            print(f'❌ Send Error: {error}')
            return False