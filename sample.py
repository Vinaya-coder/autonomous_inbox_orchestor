import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# --- CONFIG ---
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]
# Look for credentials right in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_FILE = os.path.join(BASE_DIR, 'credentials.json')
GMAIL_TOKEN = os.path.join(BASE_DIR, 'token.json')
CAL_TOKEN = os.path.join(BASE_DIR, 'token_calendar.json')


def authenticate_everything():
    if not os.path.exists(CRED_FILE):
        print(f"❌ STOP! I can't find credentials.json in: {BASE_DIR}")
        return

    print("🔐 Opening Browser for Gmail & Calendar Auth...")

    # This will trigger the browser login
    flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the token for GMAIL
    with open(GMAIL_TOKEN, 'w') as token:
        token.write(creds.to_json())
    print("✅ token.json created!")

    # Save the token for CALENDAR (same creds, different filename for your app)
    with open(CAL_TOKEN, 'w') as token:
        token.write(creds.to_json())
    print("✅ token_calendar.json created!")


if __name__ == "__main__":
    try:
        authenticate_everything()
        print("\n✨ SUCCESS! Both tokens are refreshed. Now run your main agent!")
    except Exception as e:
        print(f"💥 CRASHED: {e}")