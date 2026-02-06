import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """Handles the identity/login part so Google knows who you are."""
    creds = None
    if os.path.exists('token_calendar.json'):
        creds = Credentials.from_authorized_user_file('token_calendar.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_calendar.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def is_slot_busy(service, start_time_iso):
    """The 'Secret Sauce' that prevents double booking."""
    try:
        # If service wasn't passed, get it now
        if not service:
            service = get_calendar_service()

        start_dt = datetime.datetime.fromisoformat(start_time_iso)
        end_dt = start_dt + datetime.timedelta(minutes=30)

        body = {
            "timeMin": start_dt.isoformat(),
            "timeMax": end_dt.isoformat(),
            "items": [{"id": "primary"}]
        }

        # This query will now WORK because it has 'service' (the identity)
        query = service.freebusy().query(body=body).execute()
        busy_slots = query.get("calendars", {}).get("primary", {}).get("busy", [])

        return len(busy_slots) > 0
    except Exception as e:
        print(f"❌ Busy Check Error: {e}")
        return False


def create_meeting(summary, attendee_email, start_time_iso):
    """Creates the actual event once the time is confirmed free."""
    try:
        service = get_calendar_service()

        start_dt = datetime.datetime.fromisoformat(start_time_iso)
        end_dt = start_dt + datetime.timedelta(minutes=30)

        event = {
            'summary': summary,
            'attendees': [{'email': attendee_email}],
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'conferenceData': {
                'createRequest': {'requestId': f"req_{int(start_dt.timestamp())}",
                                  'conferenceSolutionKey': {'type': 'hangoutsMeet'}}
            },
        }

        event_result = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        return event_result.get('hangoutLink')
    except Exception as e:
        print(f"❌ Create Meeting Error: {e}")
        return None