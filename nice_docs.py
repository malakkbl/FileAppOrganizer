import string
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# File to text :
import os
import shutil
from docx import Document
import PyPDF2
import docx2txt

# Video and audio to text :
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr

# Image to text :
import pytesseract
from PIL import Image

from my_dict import theme_keywords

def file_to_text( filepath) -> str:
        
        # Initialize doc as an empty string
        doc = ""

        # Obtenir l'extension du fichier :
        _, file_extension = os.path.splitext(filepath)

        # TEXT FILES :
        if file_extension == ".txt":
            with open(filepath, "r", encoding="utf-8") as file:
                doc = file.read()

        elif file_extension == ".docx":
            doc = docx2txt.process(filepath)

        elif file_extension == ".doc":
            doc = docx2txt.process(filepath)

        elif file_extension == ".pdf":
            with open(filepath, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                doc = text

        # IMAGE FILES (JPEG) using Tesseract OCR:
        elif (
            file_extension == ".jpg"
            or file_extension == ".jpeg"
            or file_extension == ".webp"
        ):
            # Set the path to Tesseract executable (replace with your actual path)
            pytesseract.pytesseract.tesseract_cmd = (
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )
            try:
                # Load the image
                img = Image.open(filepath)

                # Use Tesseract to perform OCR on the image

                doc = pytesseract.image_to_string(img)

            except FileNotFoundError as e:
                print(f"File not found error: {e}")
            except Exception as ex:
                print(f"Error occurred: {ex}")

        # VIDEO FILES:
        elif file_extension == ".mp4":
            # Convert MP4 to WAV audio file
            audio_path = "output_audio.wav"
            video_clip = VideoFileClip(filepath)
            video_clip.audio.write_audiofile(audio_path)
            doc = audio_to_text(audio_path)

        # AUDIO FILES:
        elif file_extension == ".mp3":
            doc = audio_to_text(filepath)

        # Check if doc is not None before calling lower()
        if doc:
            doc = doc.lower()

        return doc

def audio_to_text(audio_path):
        try:
            # Convert MP3 to WAV using pydub
            wav_audio_path = "output_audio.wav"
            audio = AudioSegment.from_mp3(audio_path)
            audio.export(wav_audio_path, format="wav")

            # Recognize text from the WAV file
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_audio_path) as source:
                audio_data = recognizer.record(source)

            # Perform speech-to-text
            text = recognizer.recognize_google(audio_data)

            return text

        except FileNotFoundError as e:
            return f"File not found error: {e}"

        except Exception as ex:
            return f"Error occurred: {ex}"

        finally:
            # Remove the temporary WAV file
            if os.path.exists(wav_audio_path):
                os.remove(wav_audio_path)

def preprocess_text(document: str):
        # Remove punctuation
        text = document.translate(str.maketrans("", "", string.punctuation))

        # Remove common stop words
        stop_words = set(stopwords.words("english"))
        words = text.split()
        meaningful_words = [word for word in words if word.lower() not in stop_words]

        # Join meaningful words back into a string
        preprocessed_text = " ".join(meaningful_words)

        return preprocessed_text

def calculate_score( document: str, keywords: list) -> float:
        # Preprocess text
        preprocessed_text = preprocess_text(document)

        # Combine preprocessed text and keywords into a list
        text_and_keywords = [preprocessed_text] + keywords

        # Create a TF-IDF vectorizer
        vectorizer = TfidfVectorizer()

        # Fit and transform the text and keywords
        tfidf_matrix = vectorizer.fit_transform(text_and_keywords)

        # Calculate cosine similarity between the preprocessed text and keywords
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # The similarity score is the value at (0, 1) since 0 is the preprocessed text and 1 is the keywords
        similarity_score = similarity_matrix[0, 1]

        return similarity_score


# TEST :

my_filepath="Section2-WhyPeopleTravel.pdf"
my_doc= file_to_text(my_filepath)
print(my_doc)
print(calculate_score( my_doc, theme_keywords['travel']))