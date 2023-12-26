import sys
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
)

class AdvancedFileOrganizer(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout managers
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        radio_layout = QVBoxLayout()

        # Create widgets
        self.info_label = QLabel("Welcome to the Advanced File Organizer!")
        self.extension_radio = QRadioButton("Organize by Extension")
        self.theme_radio = QRadioButton("Organize by Theme")
        self.folder_label = QLabel("Selected Folder:")
        self.folder_path = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.organize_button = QPushButton("Organize Files")

        # Configure widgets
        self.folder_path.setReadOnly(True)

        # Add widgets to layouts
        radio_layout.addWidget(self.extension_radio)
        radio_layout.addWidget(self.theme_radio)

        top_layout.addLayout(radio_layout)
        top_layout.addWidget(self.browse_button)

        main_layout.addWidget(self.info_label)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.folder_label)
        main_layout.addWidget(self.folder_path)
        main_layout.addWidget(self.organize_button)

        # Set main layout
        self.setLayout(main_layout)

        # Connect signals to slots
        self.browse_button.clicked.connect(self.select_folder)
        self.organize_button.clicked.connect(self.organize_files)

        # Set window properties
        self.setWindowTitle("Advanced File Organizer")
        self.setGeometry(100, 100, 400, 200)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path.setText(folder_path)

    def organize_files(self):
        # Add your file organization logic here based on user's selection
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedFileOrganizer()
    window.show()
    sys.exit(app.exec_())
