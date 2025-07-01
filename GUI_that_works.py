import sys  # For command-line arguments and exit
import os   # For file and directory operations
import time  # For timestamps and delays
import traceback  # For capturing stack traces on errors
import threading  # For running tasks in background threads

# PyQt6 widgets and layout classes
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFileDialog, QMessageBox, QGraphicsOpacityEffect, QSplitter,
    QToolBar, QStyle, QMainWindow, QLineEdit, QDialog, QFrame
)
# GUI elements: fonts, colors, icons, actions
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor, QColor, QIcon, QTextDocument, QAction
# For PDF export
from PyQt6.QtPrintSupport import QPrinter
# Core Qt functionality: animations, events, timing, sizing
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QEvent, QTimer, QSize
# Import drop shadow effect (not yet used)
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

import keyboard  # For global hotkeys
from pynput.keyboard import Controller as KeyboardController  # Simulate typing


class HighlightEditableTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)  # Allow editing
        self.setAcceptRichText(True)  # Support rich text formatting
        self.highlight_placeholders()  # Highlight '***' placeholders initially

    def set_theme(self, is_dark_mode):
        self.highlight_placeholders()  # Re-highlight when theme changes

    def highlight_placeholders(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)  # Start from top of document
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("yellow"))  # Yellow background
        fmt.setFontWeight(QFont.Weight.Bold)  # Bold text
        fmt.setForeground(QColor("black"))  # Black text color

        while not cursor.isNull() and not cursor.atEnd():
            cursor = self.document().find("***", cursor)  # Find next '***'
            if not cursor.isNull():
                start = cursor.selectionStart()
                cursor.setPosition(start)
                cursor.setPosition(start + 3, QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(fmt)  # Apply format to placeholder

    def focus_next_placeholder(self):
        cursor = self.textCursor()
        current_pos = cursor.selectionEnd()  # Position after current selection

        found_cursor = self.document().find("***", current_pos)
        if found_cursor.isNull():
            found_cursor = self.document().find("***", 0)  # Wrap around

        if not found_cursor.isNull():
            start = found_cursor.selectionStart()
            found_cursor.setPosition(start)
            found_cursor.setPosition(start + 3, QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(found_cursor)  # Select next placeholder


class ProcessingDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Frameless, modal dialog
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.label = QLabel("Processing....", self)  # Status text
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 12pt; padding: 0px;")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setFixedSize(200, 100)  # Fixed size dialog

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)  # Animate dots
        self.timer.start(500)  # Update every 500ms
        self.dots = 0

    def update_dots(self):
        self.dots = (self.dots + 1) % 4
        self.label.setText("Processing" + "." * self.dots)  # Cycle 'Processing.' to 'Processing...'


class TextAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Make window frameless and translucent for custom chrome
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Viatica 1.0 beta")  # Window title
        self.typing_delay = 0.01  # Delay between simulated keystrokes
        self.setWindowIcon(QIcon("v_icon.png"))  # Set application icon

        self.keyboard = KeyboardController()  # For simulate_typing
        self.interrupt_event = threading.Event()  # To stop typing on hotkey
        self.is_dark_mode = False  # Theme flag
        self.init_ui()  # Build UI components

    def init_ui(self):

        # Container widget with padding
        container = QWidget()
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(0)
        self.setCentralWidget(container)

        # Main content frame (currently unused)
        main_frame = QFrame()
        main_frame.setObjectName("main_frame")
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(5)
        # NOTE: main_frame is created but never added to any layout
        
        # Overwrites earlier central widget, removing 'container'
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Custom title bar
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(36)
        self.title_bar.setStyleSheet("background-color: #2c3e50;")

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)

        # Icon on title bar
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("v_icon.png").pixmap(24, 24))
        title_layout.addWidget(self.icon_label)

        # Title text
        self.title_label = QLabel("Viatica 1.0 beta")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()  # Push buttons to right

        # Helper to create minimize, maximize, close buttons
        def make_btn(symbol):
            btn = QPushButton(symbol)
            btn.setFixedSize(30, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    font-size: 14px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            return btn

        # Window control buttons
        self.min_btn = make_btn("–")
        self.max_btn = make_btn("❐")
        self.close_btn = make_btn("✕")
        self.min_btn.clicked.connect(self.showMinimized)
        self.max_btn.clicked.connect(self.toggle_max_restore)
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.min_btn)
        title_layout.addWidget(self.max_btn)
        title_layout.addWidget(self.close_btn)

        # Enable window drag via title bar
        self.old_pos = None
        self.title_bar.mousePressEvent = self.mouse_press_event
        self.title_bar.mouseMoveEvent = self.mouse_move_event

        # Toolbar setup
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("background-color: #ecf0f1;")
        self.toolbar.setIconSize(QSize(16, 16))

        self.add_toolbar_button("Analyze", self.analyze_text)
        self.add_toolbar_button("Copy", self.copy_text)
        self.add_toolbar_button("Sim Typing", self.simulate_typing)
        self.add_toolbar_button("Save As", self.save_as_text)
        self.add_toolbar_button("Export PDF", self.export_to_pdf)
        self.add_toolbar_button("Clear", self.clear_text)

        # Theme toggle action
        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(theme_action)

        # Main input and output text widgets
        self.text_input = QTextEdit()
        self.text_output = HighlightEditableTextEdit()
        self.text_output.installEventFilter(self)  # Capture key events

        self.text_input.setFont(QFont("Roboto", 10))
        self.text_output.setFont(QFont("Roboto", 10))

        # Splitter to resize input/output panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Input Text:"))
        left_layout.addWidget(self.text_input)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Output Text:"))
        right_layout.addWidget(self.text_output)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Search bar for output
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search output (Ctrl+F)...")
        self.search_bar.returnPressed.connect(self.search_in_output)
        self.search_bar.setVisible(False)

        # Main layout assembly
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.toolbar)
        layout.addWidget(splitter)
        layout.addWidget(self.search_bar)
        self.central_widget.setLayout(layout)

        self.setMinimumSize(1000, 600)  # Minimum window size
        self.apply_light_theme()  # Default to light theme

    def toggle_max_restore(self):
        # Toggle between maximized and normal window
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mouse_press_event(self, event):
        # Record position when mouse pressed for drag
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouse_move_event(self, event):
        # Move window based on mouse drag
        if self.old_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def add_toolbar_button(self, name, callback):
        action = QAction(name, self)
        action.triggered.connect(callback)
        self.toolbar.addAction(action)

    def toggle_theme(self):
        # Switch between dark and light themes
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        self.text_output.set_theme(self.is_dark_mode)

    def apply_light_theme(self):
        # Stylesheet for light theme
        self.setStyleSheet("""
            QWidget {
                font-family: Roboto, Arial, sans-serif;
                font-size: 10pt;
                font-weight: bold;
                background-color: #fdfdfd;
                color: #000;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-weight: normal;
                padding: 6px;
                color: #000;
            }
            QToolBar {
                background-color: #f0f0f0;
            }
        """)

    def apply_dark_theme(self):
        # Stylesheet for dark theme
        self.setStyleSheet("""
            QWidget {
                font-family: Roboto, Arial, sans-serif;
                font-size: 10pt;
                font-weight: bold;
                background-color: #2e2e2e;
                color: #2e2e2e;
            }
            QTextEdit {
                background-color: #2e2e2e;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 6px;
                font-weight: normal;
                color: #ffffff;
            }
            QToolBar {
                background-color: #f0f0f0;
            }
        """)

    def eventFilter(self, obj, event):
        # Capture Tab for placeholder navigation and Ctrl+F for search
        if obj == self.text_output:
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Tab:
                    self.text_output.focus_next_placeholder()
                    return True
                elif event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.search_bar.setVisible(True)
                    self.search_bar.setFocus()
                    return True
        return super().eventFilter(obj, event)

    def search_in_output(self):
        # Find next occurrence of search term
        term = self.search_bar.text()
        if not term:
            return
        cursor = self.text_output.textCursor()
        cursor = self.text_output.document().find(term, cursor)
        if cursor.isNull():
            cursor = self.text_output.document().find(term, 0)
        if not cursor.isNull():
            self.text_output.setTextCursor(cursor)

    def analyze_text(self):
        # Show processing dialog and call text processing
        dialog = ProcessingDialog()
        dialog.show()
        QApplication.processEvents()

        try:
            input_text = self.text_input.toPlainText()
            output_text = self.process_input_text(input_text)
            self.text_output.setPlainText(output_text)
            self.text_output.highlight_placeholders()
            self.fade_in_output()
        except Exception as e:
            self.save_error_and_input(e)
        finally:
            dialog.close()

    def fade_in_output(self):
        # Fade-in animation for output widget
        effect = QGraphicsOpacityEffect()
        self.text_output.setGraphicsEffect(effect)
        self.animation = QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

    def save_error_and_input(self, error):
        # Save input text and error traceback to a file
        error_message = traceback.format_exc()
        input_text = self.text_input.toPlainText()
        error_folder = "errors"
        os.makedirs(error_folder, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        error_file_path = os.path.join(error_folder, f"error_{timestamp}.txt")
        try:
            with open(error_file_path, "w") as file:
                file.write("Input Text:\n")
                file.write(input_text)
                file.write("\n\nError Message:\n")
                file.write(error_message)
            self.show_success_message(error_file_path)
        except Exception as e:
            # show_error_dialog not defined -> potential bug
            self.show_error_dialog("Error occurred while saving the error: " + str(e))

    def show_success_message(self, error_file_path):
        # Inform user that error log was saved
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Error Saved")
        msg.setText("The error has been saved successfully.")
        msg.setInformativeText(f"Error file path:\n{error_file_path}")
        msg.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

    def copy_text(self):
        # Copy output text to clipboard
        output_text = self.text_output.toPlainText()
        QApplication.clipboard().setText(output_text)

    def save_as_text(self):
        # Save output text to a .txt file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as file:
                output_text = self.text_output.toPlainText()
                file.write(output_text)

    def export_to_pdf(self):
        # Export output text as PDF
        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PDF", "", "PDF Files (*.pdf)")
        if file_path:
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            doc = QTextDocument()
            doc.setHtml(self.text_output.toHtml())
            doc.print(printer)

    def clear_text(self):
        # Clear both input and output fields
        self.text_input.clear()
        self.text_output.clear()

    def simulate_typing(self):
        # Simulate typing output text with delay
        output_text = self.text_output.toPlainText()
        time.sleep(2)  # Brief pause before typing
        typing_thread = threading.Thread(target=self.type_with_interrupt, args=(output_text,))
        typing_thread.start()
        keyboard.add_hotkey('ctrl+alt+c', self.interrupt_typing)  # Stop on hotkey

    def type_with_interrupt(self, text):
        # Typing loop that can be interrupted
        for char in text:
            if self.interrupt_event.is_set():
                break
            self.keyboard.type(char)
            time.sleep(self.typing_delay)

    def interrupt_typing(self):
        # Signal to stop typing
        self.interrupt_event.set()

    def process_input_text(self, input_text):
        # Dynamically import and use new_tester.process
        import new_tester
        output_text = new_tester.process(input_text)
        del new_tester
        return output_text


if __name__ == '__main__':
    # Entry point: create app and show main window
    app = QApplication(sys.argv)
    window = TextAnalyzerApp()
    window.show()
    sys.exit(app.exec())
