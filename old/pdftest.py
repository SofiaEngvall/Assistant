import pyttsx3
from pypdf import PdfReader
import os.path

speaker = pyttsx3.init()

book_name = "Black Hat Python.pdf"
book_path = os.path.join(os.path.dirname(__file__), book_name)


def speak(text):
    speaker.say(text)
    speaker.runAndWait()


reader = PdfReader(book_path)

number_of_pages = len(reader.pages)
print(f"Pages: {number_of_pages}\n")

for page_no in range(16, len(reader.pages)):
    page = reader.pages[page_no]
    print(f"Page {page.page_number}")
    page_text = page.extract_text()
    page_text = page_text.replace(' -\n', '')
    page_text = page_text.replace(' \n', ' ').replace(
        '\n', ' ').replace('\r', '')
    for sentence in str(page_text).split("."):
        sentence = sentence.strip()+"."
        print(sentence)
        speak(sentence)
