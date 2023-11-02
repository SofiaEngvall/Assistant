import os.path
import datetime as dt
# from dateutil.parser import parse as dtparse
import time
import pytz

import pyttsx3

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pprint import pprint  # for debug output

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/tasks']

# To explore later
# holidays = "https://www.googleapis.com/calendar/v3/calendar/en.swedish#holiday@group.v.calendar.google.com"

creds_path = os.path.join(os.path.dirname(__file__), 'creds.json')
token_path = os.path.join(os.path.dirname(__file__), 'token.json')

calendar_id = "primary"  # "Sofia Engvall"
# calendar_id = "5515e0a5004847022bfaacaf9841e90e48e752d7683a2b271849833ede4f26f0@group.calendar.google.com"  # "Automated"
# calendar_id = "b47fdlbcspbial0mqf8b38oe6k@group.calendar.google.com" # "Familjekalender"

tts = pyttsx3.init()

# print(pytz.all_timezones)
# tz_Stockholm = pytz.timezone('Europe/Stockholm')
tz_UTC = pytz.timezone('UTC')


def speak(text):
    tts.say(text)
    tts.runAndWait()


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


def list_upcoming(service, no_of_events):
    try:
        now = dt.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print(f"Getting the upcoming {no_of_events} events")
        events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                              maxResults=no_of_events, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)
    except Exception as error:
        print('An error occurred: %s' % error)


def add_event(service):
    try:

        event = {
            "summary": "Automation test",
            "location": "online",
            "description":  "automated description",
            "colorId": 5,
            "start": {
                "dateTime": "2023-10-22T19:30:00+02:00",
                "timeZone": "Europe/Stockholm"
            },
            "end": {
                "dateTime": "2023-10-22T20:30:00+02:00",
                "timeZone": "Europe/Stockholm"
            },
            "recurrence": [
                "RRULE:FREQ=DAILY;COUNT=5"
            ],
            "attendees":  [
                {"email": "liza@verymuchthetopcatloverintheworld.com"},
                {"email": "andy@verymuchthetopcatloverintheworld.com"}
            ]
            # add "defaultReminders":  [{"method":"str","minutes":"str"}]
            # add "items":[resourses]
        }

        event = service.events().insert(calendarId="primary", body=event).execute()

        print(f"Event created {event}")

    except HttpError as error:
        print('An error occurred: %s' % error)
    except Exception as error:
        print('An error occurred: %s' % error)


def remind_me(service):
    pass


def todays_events(service):
    # try:
    today = dt.datetime.today()
    today = today + dt.timedelta(days=-2)  # for testing

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
        # pprint(event)
        start = format_dateTime(event)
        print(f"{event['summary']} at {start}")
        speak(f"You have {event['summary']} at {start}")

        if 'recurringEventId' in event:
            parent_event = service.events().get(
                calendarId='primary', eventId=event['recurringEventId']).execute()
            lst = parent_event['recurrence'][0].removeprefix(
                "RRULE:").replace('=', ';').split(";")
            dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
            # print(dct)

    # add httplib2.error.ServerNotFoundError
    # except HttpError as error:
    #    print('An http error occurred: %s' % error)
    # except Exception as error:
    #    print('An error occurred: %s' % error)


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


def day_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day)+suffix


def add_task(service, list, title, notes):
    task = {
        'title': title,
        'notes': notes
    }

    list_no = tasklist_name_to_id(service, list)
    if list_no:
        try:
            results = service.tasks().insert(tasklist=list_no, body=task).execute()
            speak(f"{title} was added to the {list} tasks list")
        except HttpError as error:
            if error.reason == "Invalid task list ID":
                speak(f"Couldn't find the list {list}.")
            else:
                print(error)
    else:
        speak(f"Couldn't find the list {list}.")


def list_task_lists(service):
    results = service.tasklists().list(maxResults=100).execute()
    items = results.get('items', [])
    if items:
        speak("Task lists")
        for item in items:
            speak(f"{item['title']}")
            print(f"{item['title']} ({item['id']})")


def tasklist_name_to_id(service, name):
    id = None
    results = service.tasklists().list(maxResults=100).execute()
    items = results.get('items', [])
    if items:
        for item in items:
            if item['title'].lower() == name.lower():
                id = item['id']
    return id


def main():

    creds = auth()
    calendar = build('calendar', 'v3', credentials=creds)
    tasks = build('tasks', 'v1', credentials=creds)

    # list_upcoming(calendar, 5)

    # add_task(tasks, '@default', "test 2",  "test test test")
    # add_task(tasks, 'Automated', "test 3", "testing")

    # list_task_lists(tasks)

    todays_events(calendar)

    # add_event(service)

    # while True:
    #   remind_me(calendar)
    #    time.sleep(60)  # seconds


if __name__ == '__main__':
    main()
