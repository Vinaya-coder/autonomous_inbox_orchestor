import re
import os
import datetime
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CRED_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token_calendar.json')


def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def create_meeting(summary, attendee_emails, start_time_iso):
    """Clean emails, check for conflicts, and create a Google Meet session."""
    try:
        service = get_calendar_service()
        if isinstance(attendee_emails, str):
            attendee_emails = [attendee_emails]

        # 1. Clean Emails
        clean_list = []
        for raw in attendee_emails:
            found = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', str(raw))
            if found:
                clean_list.append({'email': found.group(0).lower()})

        # 2. Setup Times
        # We handle the 'Z' and ensure start_dt is defined first
        clean_start_time = start_time_iso.replace('Z', '')
        start_dt = datetime.datetime.fromisoformat(clean_start_time)
        end_dt = start_dt + datetime.timedelta(minutes=30)

        # 3. Create 'check' (Fixes Unresolved Reference)
        # We query the calendar to see if anything exists in this time slot
        check = service.events().list(
            calendarId='primary',
            timeMin=start_dt.isoformat() + 'Z',
            timeMax=end_dt.isoformat() + 'Z',
            singleEvents=True
        ).execute()

        # 4. Conflict Logic
        if check.get('items'):
            return "ALREADY_BOOKED: This slot is already taken. Suggest a different time to the user."

        # 5. Create Event with Unique ID (Prevents 409 errors)
        unique_id = f"req_{int(time.time() * 1000)}"
        event = {
            'summary': summary,
            'attendees': clean_list,
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'conferenceData': {
                'createRequest': {
                    'requestId': unique_id,
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
        }

        result = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        return f"Meeting created. Meet Link: {result.get('hangoutLink')}"

    except Exception as e:
        import traceback
        print("❌ FULL ERROR TRACEBACK:")
        print(traceback.format_exc())
        return None