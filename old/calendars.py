import os.path
import datetime as dt
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/tasks']

creds_path = os.path.join(os.path.dirname(__file__), 'creds.json')
token_path = os.path.join(os.path.dirname(__file__), 'token.json')

calendar_id = "primary"

tz_UTC = pytz.timezone('UTC')


def auth():
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    try:
        return creds
    except Exception as error:
        print("An error occurred: %s" % error)
        print("Could not authenticate with google calendar!")
        return None


def day_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day)+suffix


def format_dateTime(event):
    if event['start'].get('date'):
        dtStart = dt.datetime.fromisoformat(event['start'].get('date'))
        startTime = ""
    if event['start'].get('dateTime'):
        dtStart = dt.datetime.fromisoformat(event['start'].get('dateTime'))
        if dtStart.time().minute == 0:
            startTime = f"{dtStart.time().hour}"
        else:
            startTime = f"{dtStart.time().hour}:{dtStart.time().minute}"
    return dtStart.strftime('%A %B ')+day_suffix(dtStart.date().day)+", "+startTime


def todays_events(service):
    todays_events = ""
    try:
        today = dt.datetime.today()
        # today = today + dt.timedelta(days=-2)  # for testing

        start = (dt.datetime(today.year, today.month, today.day, 00, 00, 00)
                 ).astimezone(tz_UTC).isoformat().removesuffix("+00:00")+'Z'
        end = (dt.datetime(today.year, today.month, today.day, 23, 59, 59)
               ).astimezone(tz_UTC).isoformat().removesuffix("+00:00")+'Z'

        events_result = service.events().list(calendarId='primary', timeMin=start,
                                              timeMax=end, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            print('No events found for today.')
            return

        for event in events:
            start = format_dateTime(event)
            todays_events = todays_events + \
                f"You have {event['summary']} at {start}\n"

    except HttpError as error:
        print('An http error occurred: %s' % error)
    except Exception as error:
        print('An error occurred: %s' % error)
    # add httplib2.error.ServerNotFoundError
    return todays_events
