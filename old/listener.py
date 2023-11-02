import speech_recognition as sr

mic = sr.Microphone()
r = sr.Recognizer()
with mic as source:
    r.adjust_for_ambient_noise(mic, 2)


def listen():
    text = ""
    with mic as source:
        source.pause_threshold = 1
        print("Listening...")
        audio = r.listen(source)
    if audio != None:
        print("Speech recognition in progress...")
        try:
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            text = r.recognize_google(audio)
            # print("U: "+text)
        # except LookupError:
        #     print("CanPlease repeat that, I didn't understand.")
        # except sr.UnknownValueError:
        #     print("...")
        except sr.RequestError as error:
            print(f"I couldn't reach google (error {error}).")
    return text


def record():
    with mic as source:
        source.pause_threshold = 1
        return r.listen(source, phrase_time_limit=None, timeout=None)
