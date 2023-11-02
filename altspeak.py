import win32com.client

SPEAKING_SPEED = 300


class Speaker():
    # def __init__(self, parent):
    #    self.parent = parent
    def __init__(self):
        self.tts = win32com.client.Dispatch('SAPI.Spvoice')

        # self.print_voices()
        self.set_voice(2)
        self.set_speed(SPEAKING_SPEED)
        self.tell_speed()

    def set_voice(self, voice_number):
        voices = self.tts.GetVoices()
        self.tts.Voice = voices.Item(voice_number)

    def print_voices(self):
        voices = self.tts.GetVoices()
        for voice in voices:
            print(voice.GetDescription())
        print(f"Current voice: {self.tts.Voice.GetDescription()}")

    def set_speed(self, speed):
        self.tts.Rate = speed

    def tell_speed(self):
        self.speak(f"I'm speaking {self.tts.Rate} words per minute.")

    def speak(self, text):
        self.tts.Speak(text)
        # self.parent.file.log(f"A: {text}")


# class ContextEvents():
#    def OnWord():
#        print("the word event occured")
#        # Work with Result


speaker = Speaker()


# event = win32com.client.WithEvents(speaker, ContextEvents)


speaker.speak("Just testing the voice")
