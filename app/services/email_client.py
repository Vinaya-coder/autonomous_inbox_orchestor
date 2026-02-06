import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class EmailClient:
    def __init__(self):
        self.service = self.authenticate()

    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth2.
        """
        creds = None
        # token.json stores user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for next time
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return build('gmail', 'v1', credentials=creds)

    def fetch_unread_emails(self):
        """
        Fetch unread emails from Gmail inbox.
        """
        try:
            results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                message = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = message['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                sender = next(h['value'] for h in headers if h['name'] == 'From')
                body = self._get_body(message['payload'])
                emails.append({"id": msg['id'], "subject": subject, "sender": sender, "body": body})

            return emails
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def _get_body(self, payload):
        """
        Extract body from Gmail message payload.
        """
        parts = payload.get('parts')
        if parts:
            data = parts[0]['body'].get('data')
        else:
            data = payload['body'].get('data')
        if data:
            text = base64.urlsafe_b64decode(data).decode('utf-8')
            return text
        return ""

    def send_email(self, to: str, subject: str, body: str):
        """
        Send email using Gmail API.
        """
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        try:
            message_sent = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            print(f"Email sent to {to}, id: {message_sent['id']}")
        except HttpError as error:
            print(f'An error occurred: {error}')
