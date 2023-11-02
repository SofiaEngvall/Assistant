import pyttsx3

# This is an example from the pyttsx3 dosc with a few updates - Doesn't work


def onStart(name):
    print(f"starting: {name}")


def onWord(name, location, length):
    print(f"word: {name} loc: {location} len: {length}")
    if location > 10:
        engine.stop()
    # Apparently stopped working in 2019


def onEnd(name, completed):
    print(f"finishing: {name} done: {completed}")
    if name == 'fox':
        engine.say('What a lazy dog!', 'dog')
    elif name == 'dog':
        engine.endLoop()
    # Apparently stopped working in 2019


engine = pyttsx3.init()
engine.connect('started-utterance', onStart)
engine.connect('started-word', onWord)
engine.connect('finished-utterance', onEnd)
engine.say('The quick brown fox jumped over the lazy dog.')
engine.say('Some more text.', 'more')
engine.runAndWait()
