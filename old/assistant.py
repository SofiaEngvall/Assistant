import os
from time import sleep
import pytz
from datetime import datetime as dt
from pynput.keyboard import Key, Controller
from webbrowser import open_new_tab

from speaker import speak
from listener import listen, record
# from googleapiclient.discovery import build
from calendars import build, auth, todays_events

keyb = Controller()

tz_UTC = pytz.timezone('UTC')

creds = auth()
calendar = build('calendar', 'v3', credentials=creds)
tasks = build('tasks', 'v1', credentials=creds)

note_path = os.path.join(os.path.dirname(__file__), "notes")
if not os.path.exists(note_path):
    os.mkdir(note_path)

logfile = os.path.join(os.path.dirname(__file__), "logfile.txt")


def log_to_file(text):
    with open(logfile, "a") as file:
        file.write(text+"\n")


def save_audio_note(name, note):
    filename = os.path.join(note_path, name+".wav")
    with open(filename, "wb") as f:
        f.write(note.get_wav_data())


def save_note(name, note):
    filename = os.path.join(note_path, name+".txt")
    with open(filename, "w") as f:
        f.write(note)


def get_note_name():
    speak("What should it be called?")
    name = ""
    while name == "":
        name = listen()
        if name == "":
            speak("Could you repeat that, please?")
    return name


def typing_mode():
    speak("Entering typing mode!")
    while True:
        text = listen()
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
            keyb.type(text)
    speak("Exiting typing mode!")


if __name__ == "__main__":
    log_to_file(f"\n{dt.now()}\n")
    speak("Welcome, I'm listening to your commands!")
    while True:
        text = listen()
        if text != "":
            log_to_file("U: "+text)
            text = " "+text.lower()+" "

            for greeting in [" hi ", "hello", "greetings"]:
                if greeting in text:
                    speak(f"{greeting} to you too!")
                    break

            for thanks in ["thank you", "thanks"]:
                if thanks in text:
                    speak(f"You're welcome!")
                    break

            if "i'm" in text and "impressed" in text:
                speak("Thank you!")

            if "command" in text or ("what" in text and "you" in text and " do " in text):
                speak("""
                    I can tell you the time, type for you and make text and audio notes.
                    I'm just learning to help you manage your calendar and your tasks lists.
                    I hope I can be of assistance!
                    """)

            if "type" in text:
                if "me" in text or "mode" in text:
                    typing_mode()

            if "note" in text:
                if "save" in text:
                    if "audio" in text:
                        speak("What should the note say?")
                        note = record()
                        name = get_note_name()
                        speak(f"Saving audio note {name}")
                        save_audio_note(name, note)
                        speak("Saved!")
                    else:
                        speak("What should the note say?")
                        note = listen()
                        name = get_note_name()
                        speak(f"Saving note {name}")
                        save_note(name, note)
                        speak("Saved!")
                if "read" in text:
                    speak("Reading note")

            if "time" in text and "what" in text:
                if "uk" in text:
                    speak(
                        f"It's {dt.now(pytz.timezone('Europe/London')).hour} in London.")
                elif "new york" in text:
                    speak(
                        f"It's {dt.now(pytz.timezone('America/New_York')).hour} in New  York.")
                else:
                    speak(f"It's {dt.now().hour} {dt.now().minute}.")

            if "what's up" in text or ("what" in text and "today" in text):
                speak(todays_events(calendar))

            if "calendar" in text:
                if "add" in text:
                    speak("Adding to calendar")

            if "sleep" in text:
                print("Pausing assistant")
                speak("Sleeping. Please say listen to activate me again.")
                while True:
                    text = listen()
                    if "listen" in text:
                        print("Reactivating assistant")
                        speak("I'm listening to your commands!")
                        break

            # if "restart" in text:
            #    with keyb.pressed(Key.shift_r) and keyb.pressed(Key.ctrl_r):
            #        keyb.press(Key.f5)

            if "stop" in text:
                print("Stopping!")
                speak("Stopping!")
                break

            if "self" in text and "destruct" in text:
                speak("Counting down to self destruct: 10, 9, 8, 7, 6")
                speak("Just kidding!! hehe")
