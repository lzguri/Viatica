import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Font Example")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        text_browser = QTextBrowser()
        layout.addWidget(text_browser)

        # Create a QFont object
        custom_font = QFont("Arial", 16)
        custom_font.setBold(True)
        custom_font.setItalic(True)

        # Set the font for the QTextBrowser
        text_browser.setFont(custom_font)

        # Add text with the custom font
        text_browser.setPlainText("This is some text with a custom font.")

if __name__ == "__main__":
    main()
