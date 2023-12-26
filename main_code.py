import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QRadioButton,
    QLineEdit,
    QFileDialog,
    QPlainTextEdit,
)
import subprocess
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

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

# score + move functions :
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from my_dict import theme_keywords


class FileOrganizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_theme = ""  # To store the selected theme

        # Create layout managers
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # Create widgets
        self.info_label = QLabel("Welcome to the Advanced File Organizer!")
        self.extension_radio = QRadioButton("Organize by Extension")
        self.theme_radio = QRadioButton("Organize by Theme")
        self.folder_label = QLabel("Selected Folder:")
        self.folder_path = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.organize_button = QPushButton("Organize Files")

        # New widgets for theme input
        self.theme_input = QPlainTextEdit()
        self.theme_input.setHidden(True)
        self.add_theme_button = QPushButton("Add Theme")
        self.add_theme_button.setHidden(True)

        # Add widgets to layouts
        top_layout.addWidget(self.theme_radio)
        top_layout.addWidget(self.extension_radio)
        top_layout.addWidget(self.theme_input)
        top_layout.addWidget(self.add_theme_button)
        top_layout.addWidget(self.browse_button)

        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.folder_label)
        main_layout.addWidget(self.folder_path)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.organize_button)

        # Set main layout
        self.setLayout(main_layout)

        # Configure widgets
        self.folder_path.setReadOnly(True)
        self.theme_input.setPlaceholderText("Enter themes, separated by commas")

        # Connect signals to slots
        self.browse_button.clicked.connect(self.select_folder)
        self.organize_button.clicked.connect(self.organize_files)
        self.theme_radio.toggled.connect(self.show_theme_input)
        self.add_theme_button.clicked.connect(self.add_theme)

        # Set window properties
        self.setWindowTitle("Advanced File Organizer")
        self.setGeometry(100, 100, 400, 400)

    def show_theme_input(self, checked):
        # Show or hide theme input based on radio button state
        self.theme_input.setHidden(not checked)
        self.add_theme_button.setHidden(not checked)

    def add_theme(self):
        self.current_theme = self.theme_input.toPlainText().strip()
        self.theme_input.clear()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path.setText(folder_path)

    def remove_empty_folders(self, folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)

    def organize_files_recursive(self, folder_path, themes):
        documents_as_text = {}

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                documents_as_text[filepath] = self.file_to_text(filepath)

        document_scores = {}

        for filepath, file_text in documents_as_text.items():
            scores = {}
            for theme, keywords in theme_keywords.items():
                scores[theme] = self.calculate_score(file_text, keywords)
            document_scores[filepath] = scores

        seuil = 0.1
        for filepath, scores in document_scores.items():
            max_score_theme = max(scores, key=scores.get)
            if scores[max_score_theme] < seuil:
                self.move_file_to_folder(filepath, "autre")
            else:
                self.move_file_to_folder(filepath, max_score_theme)


    def organize_files(self):
        folder_path = self.folder_path.text()

        if not folder_path:
            return

        if self.extension_radio.isChecked():
            self.organize_by_extension(folder_path)

        if self.theme_radio.isChecked():
            user_entered_themes = [
                theme.strip() for theme in self.current_theme.split(",")
            ]
            self.organize_files_recursive(folder_path, user_entered_themes)

        # Remove empty folders after organizing files
        self.remove_empty_folders(folder_path)

        self.info_label.setText(f"Files in {folder_path} organized!")

    def list_files(self, dir_path):
        r = []
        for name in os.listdir(dir_path):
            path = os.path.join(dir_path, name)
            if os.path.isfile(path):
                r.append(path)
            else:
                r.extend(self.list_files(path))
        return r

    def organize_by_extension(self, folder_path):
        all_files = self.list_files(folder_path)

        for file_path in all_files:
            if ".git" in file_path:
                continue

            extension_start = file_path.rfind(".")
            filename_start = file_path.rfind(os.sep) + 1
            

            if extension_start != -1:
                file_extension = file_path[extension_start + 1 :].lower()
            else:
                file_extension = "no_extension"

            filename = file_path[filename_start:]
            dest_folder = os.path.join(folder_path, file_extension)

            if not os.path.exists(dest_folder):
                os.mkdir(dest_folder)

            dest_file_path = os.path.join(dest_folder, filename)
            base_filename = filename[: extension_start - filename_start]
            counter = 1
            while os.path.exists(dest_file_path):
                dest_file_path = os.path.join(
                    dest_folder, f"{base_filename}_{counter}.{file_extension}"
                )
                counter += 1

            os.rename(file_path, dest_file_path)

    def organize_by_theme(self, folder_path, themes: list):
        print("THEMES:", themes)
        # 1. Transformer chaque fichier en texte
        documents_as_text = {}
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                documents_as_text[filepath] = self.file_to_text(
                    filepath
                )  # file_to_text : Une fonction pour convertir un fichier en texte

        # 3. Scoring des documents par rapport à chaque thème
        document_scores = {}
        for filepath, file_text in documents_as_text.items():
            scores = {}
            for theme, keywords in theme_keywords.items():
                scores[theme] = self.calculate_score(file_text, keywords)
            document_scores[filepath] = scores

        print("DOCUMENT_SCORES:", document_scores)
        # 4. Organiser les fichiers basés sur le score le plus élevé et un seuil d'attribution
        seuil = 0.1
        for filepath, scores in document_scores.items():
            print("FILEPATH:", filepath)
            max_score_theme = max(scores, key=scores.get)
            if scores[max_score_theme] < seuil:
                # Déplacez le fichier dans le dossier "autre"
                self.move_file_to_folder(filepath, "autre")
            else:
                # Déplacez le fichier dans le dossier du thème correspondant
                self.move_file_to_folder(filepath, max_score_theme)

    # FONCTIONS UTILISEES :

    def file_to_text(self, filepath) -> str:
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
            doc = self.audio_to_text(audio_path)

        # AUDIO FILES:
        elif file_extension == ".mp3":
            doc = self.audio_to_text(filepath)

        # Check if doc is not None before calling lower()
        if doc:
            doc = doc.lower()

        return doc

    def audio_to_text(self, audio_path):
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

    def calculate_score(self, document: str, keywords: list) -> float:
        # Combine document text and keywords for TF-IDF calculation
        text_and_keywords = [document] + keywords

        # Create a TF-IDF vectorizer
        vectorizer = TfidfVectorizer()

        # Fit and transform the text and keywords
        tfidf_matrix = vectorizer.fit_transform(text_and_keywords)

        # Calculate cosine similarity between the document and keywords
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # The similarity score is the value at (0, 1) since 0 is the document and 1 is the keywords
        similarity_score = similarity_matrix[0, 1]

        return similarity_score

    def move_file_to_folder(self, filepath: str, folder_name: str):
        try:
            dest_folder = os.path.join(os.path.dirname(filepath), folder_name)
            os.makedirs(dest_folder, exist_ok=True)

            filename = os.path.basename(filepath)
            dest_path = os.path.join(dest_folder, filename)

            base_filename, file_extension = os.path.splitext(filename)
            counter = 1

            while os.path.exists(dest_path):
                dest_path = os.path.join(
                    dest_folder, f"{base_filename}_{counter}{file_extension}"
                )
                counter += 1

            shutil.move(filepath, dest_path)
        except Exception as e:
            print(f"Error moving file to {folder_name}: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileOrganizerApp()
    window.show()
    sys.exit(app.exec_())
