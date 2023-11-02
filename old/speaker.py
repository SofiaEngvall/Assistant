import os
import pyttsx3

_tts = pyttsx3.init()

logfile = os.path.join(os.path.dirname(__file__), "logfile.txt")


def log_to_file(text):
    with open(logfile, "a") as file:
        file.write(text+"\n")


def speak(text):
    _tts.say(text)
    _tts.runAndWait()
    print(f"A: {text}")
    log_to_file(f"A: {text}")
