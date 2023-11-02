from win32com.client import Dispatch
import win32com.client


class ContextEvents():
    def onWord():
        print("the word event occured")

        # Work with Result


s = Dispatch('SAPI.Spvoice')
e = win32com.client.WithEvents(s, ContextEvents)
s.Speak('The quick brown fox jumped over the lazy dog.')
