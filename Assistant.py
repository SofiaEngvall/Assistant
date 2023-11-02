import os.path
import datetime as dt
import pytz

import pyttsx3
import speech_recognition as sr
from pynput.keyboard import Key, Controller

from pypdf import PdfReader
from webbrowser import open_new_tab
from yr.libyr import Yr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError


SPEAKING_SPEED = 200


class Assistant():

    def __init__(self):
        self.keyb = Controller()

        self.file = self.File(self)
        self.speaker = self.Speaker(self)
        self.listener = self.Listener(self)
        self.note = self.Note(self)
        self.calendar = self.Calendar(self)

    class File():
        def __init__(self, parent):
            self.parent = parent
            self.logfile = os.path.join(
                os.path.dirname(__file__), "logfile.txt")

        def log(self, text):
            with open(self.logfile, "a") as file:
                try:
                    file.write(text+"\n")
                except UnicodeEncodeError as error:
                    print("Removing unprintable characters!")
                    text = text.encode('utf8')
                    file.write(f"{text}\n")

    class Speaker():
        def __init__(self, parent):
            self.parent = parent
            self.tts = pyttsx3.init()

            # self.print_voices()
            self.set_voice(2)
            self.set_speed(SPEAKING_SPEED)
            # self.tell_speed(SPEAKING_SPEED)

        def set_voice(self, voice_number):
            voices = self.tts.getProperty('voices')
            self.tts.setProperty('voice', voices[voice_number].id)

        def print_voices(self):
            voices = self.tts.getProperty('voices')
            for voice in voices:
                print(voice.name)
            print(f"Current voice: {self.tts.getProperty('voice')}")

        def set_speed(self, speed):
            self.tts.setProperty("rate", speed)

        def tell_speed(self, speed):
            self.speak(f"I'm speaking {speed} words per minute.")

        def speak(self, text):
            self.tts.say(text)
            self.tts.runAndWait()
            self.parent.file.log(f"A: {text}")

    class Listener():
        def __init__(self, parent):
            self.parent = parent
            self.sr = sr.Recognizer()
            self.mic = sr.Microphone()
            print("Getting background noice level")
            with self.mic as source:
                self.sr.adjust_for_ambient_noise(source, 2)

        def listen(self):
            text = ""
            with self.mic as source:
                source.pause_threshold = 1
                print("Listening...")
                audio = self.sr.listen(source)
            if audio != None:
                print("Speech recognition in progress...")
                try:
                    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                    text = self.sr.recognize_google(audio)
                except LookupError:
                    self.parent.speaker.speak("Could you repeat that please.")
                except sr.UnknownValueError:
                    self.parent.speaker.speak("hmm...")
                except sr.RequestError as error:
                    self.parent.speaker.speak(
                        f"I couldn't reach google (error {error}).")
            return text

        def record(self):
            with self.mic as source:
                source.pause_threshold = 1
                return self.sr.listen(source, phrase_time_limit=None, timeout=None)

        def get_name(self):
            name = ""
            while name == "":
                name = self.parent.listener.listen()
                if name == "":
                    self.parent.speaker.speak(
                        "Could you repeat that, please?")
            return name

    class Note():
        def __init__(self, parent):
            self.parent = parent
            self.note_path = os.path.join(os.path.dirname(__file__), "notes")
            if not os.path.exists(self.note_path):
                os.mkdir(self.note_path)

        def save_audio_note(self, name, note):
            filename = os.path.join(self.note_path, name+".wav")
            with open(filename, "wb") as f:
                f.write(note.get_wav_data())

        def save_note(self, name, note):
            filename = os.path.join(self.note_path, name+".txt")
            with open(filename, "w") as f:
                f.write(note)

    class Calendar():
        def __init__(self, parent):
            self.parent = parent
            self.tz_UTC = pytz.timezone('UTC')
            self.SCOPES = ['https://www.googleapis.com/auth/calendar',
                           'https://www.googleapis.com/auth/tasks']
            self.creds_path = os.path.join(
                os.path.dirname(__file__), 'creds.json')
            self.token_path = os.path.join(
                os.path.dirname(__file__), 'token.json')
            self.calendar_id = "primary"

            self.creds = self.auth()
            self.calendar = build('calendar', 'v3', credentials=self.creds)
            self.tasks = build('tasks', 'v1', credentials=self.creds)

        def auth(self):
            creds = None
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except RefreshError as error:
                        self.parent.speaker.speak(
                            "I failed to refresh my permissions to your calendar and your tasks. A browser window will pop up so that you can renew these. Thank you!")
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.creds_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                else:
                    self.parent.speaker.speak(
                        "For me to be able to help you access your calendar and your tasks you need to approve me accessing these. A browser window will pop up so you can give me access. Thank you!")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.creds_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            try:
                return creds
            except Exception as error:
                print("An error occurred: %s" % error)
                print("Could not authenticate with google calendar!")
                return None

        def day_suffix(self, day):
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][day % 10 - 1]
            return str(day)+suffix

        def format_dateTime(self, event):
            # today = dt.datetime.today()
            # 9tomorrow = today + dt.timedelta(days=+1)

            if event['start'].get('date'):
                dtStart = dt.datetime.fromisoformat(event['start'].get('date'))
                startTime = ""
            if event['start'].get('dateTime'):
                dtStart = dt.datetime.fromisoformat(
                    event['start'].get('dateTime'))
                if dtStart.time().minute == 0:
                    startTime = f"{dtStart.time().hour}"
                else:
                    startTime = f"{dtStart.time().hour}:{dtStart.time().minute}"

                # if dtStart.date() == today.date():
                #    print("TODAY!")
                # if dtStart.date() == tomorrow.date():
                #    print("TOMORROW!")

            return dtStart.strftime('%A %B ')+self.day_suffix(dtStart.date().day)+", "+startTime

        def todays_events(self, service):
            todays_events = ""
            try:
                today = dt.datetime.today()
                # today = today + dt.timedelta(days=+1)  # for testing

                start = (dt.datetime(today.year, today.month, today.day, 00, 00, 00)
                         ).astimezone(self.tz_UTC).isoformat().removesuffix("+00:00")+'Z'
                end = (dt.datetime(today.year, today.month, today.day, 23, 59, 59)
                       ).astimezone(self.tz_UTC).isoformat().removesuffix("+00:00")+'Z'

                events_result = service.events().list(calendarId='primary', timeMin=start,
                                                      timeMax=end, singleEvents=True, orderBy='startTime').execute()
                events = events_result.get('items', [])
                if not events:
                    return "You have nothing in your calendar today."

                for event in events:
                    start = self.format_dateTime(event)
                    todays_events = todays_events + \
                        f"You have {event['summary']} at {start}\n"

            except HttpError as error:
                print('An http error occurred: %s' % error)
            except Exception as error:
                print('An error occurred: %s' % error)
            # add httplib2.error.ServerNotFoundError
            return todays_events

    def typing_mode(self):
        self.speaker.speak("Entering typing mode!")
        while True:
            text = self.listener.listen()
            if text != "":
                if ("stop" in text and "typing" in text) or "stop stop" in text:
                    break
                text = text.replace("space bar", " ")
                text = text.replace("enter", "\n")
                text = text.replace("new line", "\n")
                text = text.replace("period", ".")
                text = text.replace("comma", ",")
                text = text.replace("backspace", "\b")
                print(text)
                self.keyb.type(text)
        self.speaker.speak("Exiting typing mode!")

    def reading_mode(self):
        book_title = ""
        self.speaker.speak("What do you want me to read?")
        book = self.listener.get_name()
        book = book.lower()
        print(book)
        if "black" in book and "python" in book:
            book_title = "Black Hat Python.pdf"
        if "python" in book and "tutorial" in book:
            book_title = "Tutorial.pdf"
        if book_title != "":
            # "Do you want me to continue where we left off?""
            #  else:
            self.speaker.speak("What page should I start at?")
            page = int(self.listener.get_name())
            self.read_pdf(book_title, page)

    def read_pdf(self, book_name, page=0):
        # Replace later with better checks for if it's reading code or actual text
        book_path = os.path.join(os.path.dirname(__file__), book_name)
        reader = PdfReader(book_path)

        for page_no in range(page, len(reader.pages)):
            page = reader.pages[page_no]
            print(f"Page {page.page_number}")
            page_text = page.extract_text()
            page_text = page_text.replace(' -\n', '')
            page_text = page_text.replace(' \n', ' ').replace(
                '\n', ' ').replace('\r', '')
            for sentence in str(page_text).split(". "):
                sentence = sentence.strip()+"."
                print(sentence)
                self.speaker.speak(sentence)


if __name__ == "__main__":
    assistant = Assistant()
    assistant.file.log(f"\n{dt.datetime.now()}\n")
    assistant.speaker.speak("Welcome, I'm listening to your commands!")
    while True:
        text = assistant.listener.listen()
        if text != "":
            assistant.file.log("U: "+text)
            print("U: "+text)
            text = " "+text.lower()+" "

            for greeting in [" hi ", "hello", "greetings", "good morning", "good night"]:
                if greeting in text:
                    assistant.speaker.speak(f"{greeting} to you too!")
                    break

            for thanks in ["thank you", "thanks"]:
                if thanks in text:
                    assistant.speaker.speak(f"You're welcome!")
                    break

            if "i'm" in text and "impressed" in text:
                assistant.speaker.speak("Thank you!")

            if "commands" in text or ("what" in text and "you" in text and " do " in text):
                assistant.speaker.speak("""
                    I can tell you the time, type for you and make text and audio notes.
                    I'm just learning to help you manage your calendar and your tasks lists.
                    I hope I can be of assistance!
                    """)

            if "type" in text:
                if "me" in text or "mode" in text:
                    assistant.typing_mode()

            if "read" in text:
                if "me" in text:
                    assistant.reading_mode()

            if "note" in text:
                if "save" in text:
                    if "audio" in text:
                        assistant.speaker.speak("What should the note say?")
                        note = assistant.listener.record()
                        assistant.speaker.speak("What should it be called?")
                        name = assistant.listener.get_name()
                        assistant.speaker.speak(f"Saving audio note {name}")
                        assistant.note.save_audio_note(name, note)
                        assistant.speaker.speak("Saved!")
                    else:
                        assistant.speaker.speak("What should the note say?")
                        note = assistant.listener.listen()
                        assistant.speaker.speak("What should it be called?")
                        name = assistant.listener.get_name()
                        assistant.speaker.speak(f"Saving note {name}")
                        assistant.note.save_note(name, note)
                        assistant.speaker.speak("Saved!")
                if "read" in text:
                    assistant.speaker.speak("Reading note")

            if "time" in text and "what" in text:
                if "uk" in text:
                    assistant.speaker.speak(
                        f"It's {dt.datetime.now(pytz.timezone('Europe/London')).hour} in London.")
                elif "new york" in text:
                    assistant.speaker.speak(
                        f"It's {dt.datetime.now(pytz.timezone('America/New_York')).hour} in New  York.")
                else:
                    assistant.speaker.speak(
                        f"It's {dt.datetime.now().hour} {dt.datetime.now().minute}.")

            if "what's up" in text or ("what" in text and "today" in text):
                assistant.speaker.speak(
                    assistant.calendar.todays_events(assistant.calendar.calendar))

            if "calendar" in text:
                if "add" in text:
                    assistant.speaker.speak("Adding to calendar")

            if "open" in text:
                if "messenger" in text:
                    assistant.speaker.speak(
                        "I'm opening Messenger in your browser.")
                    open_new_tab("https://www.facebook.com/messages/")

            if "weather" in text:
                assistant.speaker.speak("For which location?")
                location = assistant.listener.get_name()
                if "home" in location:
                    weather = Yr(location_name='Norge/Telemark/Skien/Skien')
                    # assistant.speaker.speak(weather.now(as_json=True))
                    print(weather.now(as_json=True))
                    "Accept-Encoding: gzip, deflate"
                    # "acmeweathersite.com support@acmeweathersite.com" "AcmeWeatherApp/0.9 github.com/acmeweatherapp"
                    "User-Agents: Assistant.py sofia@fixitnow.se"

            if "sleep" in text:
                print("Pausing assistant")
                assistant.speaker.speak(
                    "Sleeping. Please say listen to activate me again.")
                while True:
                    text = assistant.listener.listen()
                    if "listen" in text:
                        print("Reactivating assistant")
                        assistant.speaker.speak(
                            "I'm listening to your commands!")
                        break

            # if "restart" in text:
            #    with keyb.pressed(Key.shift_r) and keyb.pressed(Key.ctrl_r):
            #        keyb.press(Key.f5)

            if "stop" in text:
                print("Stopping!")
                assistant.speaker.speak("Stopping!")
                break

            if "self" in text and "destruct" in text:
                assistant.speaker.speak(
                    "Counting down to self destruct: 10, 9, 8, 7, 6")
                assistant.speaker.speak("Just kidding!! hehe")
