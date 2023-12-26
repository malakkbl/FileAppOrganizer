# File to text :
import os
from docx import Document
import PyPDF2
import docx2txt
# Video and audio to text :
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr
from pydub.playback import play

def file_to_text(filepath) -> str:
    # Obtenir l'extension du fichier :
    _, file_extension = os.path.splitext(filepath)

    # TEXT FILES :

    if file_extension == ".txt":
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    elif file_extension == ".docx":
        doc = Document(filepath)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    elif file_extension == ".doc":
        return docx2txt.process(filepath)

    elif file_extension == ".pdf":
        with open(filepath, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()  # Use extract_text instead of extractText
            return text

print(file_to_text("texte_les_miserables.pdf"))
print("***************************************************")



def audio_to_text(audio_path):
    recognizer = sr.Recognizer()

    # Convert audio to WAV using pydub
    audio = AudioSegment.from_file(audio_path)
    audio.export("temp.wav", format="wav")

    # Perform speech recognition on the converted WAV file
    with sr.AudioFile("temp.wav") as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Google Web Speech API could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Web Speech API; {e}"
    finally:
        # Clean up the temporary WAV file
        os.remove("temp.wav")

# Example usage
audio_path = r"LibiancaPeople.mp3"
result = audio_to_text(audio_path)

print("Text from audio:", result)


