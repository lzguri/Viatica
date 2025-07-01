import sys
import os
import time
import traceback
import threading

from PyQt6.QtWidgets import (
    QApplication, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFileDialog, QMessageBox, QGraphicsOpacityEffect, QSplitter,
    QToolBar, QMainWindow, QLineEdit, QDialog
)
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor, QColor, QIcon, QTextDocument, QAction
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QEvent, QTimer, QSize
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

import keyboard
from pynput.keyboard import Controller as KeyboardController


class HighlightEditableTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setAcceptRichText(True)
        self.highlight_placeholders()

    def set_theme(self, is_dark_mode):
        self.highlight_placeholders()

    def highlight_placeholders(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("yellow"))
        fmt.setFontWeight(QFont.Weight.Bold)
        fmt.setForeground(QColor("black"))

        while not cursor.isNull() and not cursor.atEnd():
            cursor = self.document().find("***", cursor)
            if not cursor.isNull():
                start = cursor.selectionStart()
                cursor.setPosition(start)
                cursor.setPosition(start + 3, QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(fmt)

    def focus_next_placeholder(self):
        cursor = self.textCursor()
        current_pos = cursor.selectionEnd()

        found_cursor = self.document().find("***", current_pos)
        if found_cursor.isNull():
            found_cursor = self.document().find("***", 0)

        if not found_cursor.isNull():
            start = found_cursor.selectionStart()
            found_cursor.setPosition(start)
            found_cursor.setPosition(start + 3, QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(found_cursor)


class ProcessingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.label = QLabel("Processing", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 14pt; padding: 20px;")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setFixedSize(200, 100)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)
        self.dots = 0

    def update_dots(self):
        self.dots = (self.dots + 1) % 4
        self.label.setText("Processing" + "." * self.dots)


class TextAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Preserve window type and add frameless hint for custom shadow
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setWindowTitle("Viatica 1.0 beta")
        self.typing_delay = 0.01

        # Taskbar and Alt-Tab icon
        self.setWindowIcon(QIcon("viatica.png"))  # ensure this file is in working directory

        self.keyboard = KeyboardController()
        self.interrupt_event = threading.Event()
        self.is_dark_mode = False
        self.init_ui()

    def init_ui(self):
        # Outer container with padding
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(0)
        self.setCentralWidget(container)

        # Main frame with background and rounded corners
        main_frame = QFrame()
        main_frame.setObjectName("main_frame")
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(5)

        # Title bar
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(36)
        self.title_bar.setStyleSheet("background-color: #2c3e50;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("viatica.png").pixmap(24, 24))
        title_layout.addWidget(self.icon_label)
        self.title_label = QLabel("Viatica 1.0 beta")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        def make_btn(symbol):
            btn = QPushButton(symbol)
            btn.setFixedSize(30, 28)
            btn.setStyleSheet(
                "QPushButton { background-color: transparent; color: white; font-size: 14px; border: none; }"
                "QPushButton:hover { background-color: #34495e; }"
            )
            return btn
        self.min_btn = make_btn("–")
        self.max_btn = make_btn("❐")
        self.close_btn = make_btn("✕")
        self.min_btn.clicked.connect(self.showMinimized)
        self.max_btn.clicked.connect(self.toggle_max_restore)
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.min_btn)
        title_layout.addWidget(self.max_btn)
        title_layout.addWidget(self.close_btn)
        self.old_pos = None
        self.title_bar.mousePressEvent = self.mouse_press_event
        self.title_bar.mouseMoveEvent = self.mouse_move_event
        frame_layout.addWidget(self.title_bar)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        for name, func in [
            ("Analyze", self.analyze_text), ("Copy", self.copy_text),
            ("Sim Typing", self.simulate_typing), ("Save As", self.save_as_text),
            ("Export PDF", self.export_to_pdf), ("Clear", self.clear_text)
        ]:
            action = QAction(name, self)
            action.triggered.connect(func)
            self.toolbar.addAction(action)
        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(theme_action)
        frame_layout.addWidget(self.toolbar)

        # Text areas
        self.text_input = QTextEdit()
        self.text_output = HighlightEditableTextEdit()
        self.text_output.installEventFilter(self)
        self.text_input.setFont(QFont("Roboto", 10))
        self.text_output.setFont(QFont("Roboto", 10))
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget(); left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Input Text:")); left_layout.addWidget(self.text_input)
        right_widget = QWidget(); right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Output Text:")); right_layout.addWidget(self.text_output)
        splitter.addWidget(left_widget); splitter.addWidget(right_widget)
        frame_layout.addWidget(splitter)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("search_bar")
        self.search_bar.setPlaceholderText("Search output (Ctrl+F)...")
        self.search_bar.returnPressed.connect(self.search_in_output)
        self.search_bar.setVisible(False)
        frame_layout.addWidget(self.search_bar)

        container_layout.addWidget(main_frame)

        # Initial theme
        self.apply_light_theme()

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 160))
        main_frame.setGraphicsEffect(shadow)
        self.setMinimumSize(1000, 600)

    def toggle_max_restore(self):
        if self.isMaximized(): self.showNormal()
        else: self.showMaximized()

    def mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouse_move_event(self, event):
        if self.old_pos and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x()+delta.x(), self.y()+delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        (self.apply_dark_theme if self.is_dark_mode else self.apply_light_theme)()
        self.text_output.set_theme(self.is_dark_mode)

    def apply_light_theme(self):
        self.setStyleSheet("""
            QWidget#main_frame { background-color: #fdfdfd; border-radius: 10px; }
            QWidget { font-family: Roboto, Arial, sans-serif; font-size: 10pt; color: #000; }
            QTextEdit { background-color: #fff; border:1px solid #ccc; border-radius:5px; padding:6px; color:#000; }
            QToolBar { background-color: #f0f0f0; color:#000; }
            QToolBar QToolButton { color:#000; }
            QSplitter::handle { background-color: #fdfdfd; }
            QLineEdit#search_bar { background-color: #ffffcc; border:1px solid #ccc; border-radius:5px; padding:4px; }
        """)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget#main_frame { background-color: #1e1e1e; border-radius: 10px; }
            QWidget { font-family: Roboto, Arial, sans-serif; font-size: 10pt; color: #fff; }
            QTextEdit { background-color: #2e2e2e; border:1px solid #444; border-radius:5px; padding:6px; color:#fff; }
            QToolBar { background-color: #333; color:#fff; }
            QToolBar QToolButton { color:#fff; }
            QSplitter::handle { background-color: #1e1e1e; }
            QLineEdit#search_bar { background-color: #1e1e1e; border:1px solid #555; border-radius:5px; padding:4px; color:#fff; }
                           
        """)

    def eventFilter(self, obj, event):
        if obj == self.text_output and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                self.text_output.focus_next_placeholder(); return True
            if event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.search_bar.setVisible(True); self.search_bar.setFocus(); return True
        return super().eventFilter(obj, event)

    def search_in_output(self):
        term = self.search_bar.text();
        if not term: return
        cursor = self.text_output.document().find(term, self.text_output.textCursor())
        if cursor.isNull(): cursor = self.text_output.document().find(term, 0)
        if not cursor.isNull(): self.text_output.setTextCursor(cursor)

    def analyze_text(self):
        dialog = ProcessingDialog(); dialog.show(); QApplication.processEvents()
        try:
            output_text = __import__('new_tester').process(self.text_input.toPlainText())
            self.text_output.setPlainText(output_text);
            self.text_output.highlight_placeholders(); #self.fade_in_output()
        except Exception as e: self.save_error_and_input(e)
        finally: dialog.close()

   # def fade_in_output(self):
   #     effect = QGraphicsOpacityEffect(); self.text_output.setGraphicsEffect(effect)
    #    self.animation = QPropertyAnimation(effect, b"opacity"); self.animation.setDuration(800)
    #    self.animation.setStartValue(0); self.animation.setEndValue(1)
    #    self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad); self.animation.start()

    def save_error_and_input(self, error):
        err = traceback.format_exc(); inp = self.text_input.toPlainText()
        os.makedirs("errors", exist_ok=True)
        path = f"errors/error_{time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        try:
            with open(path, 'w') as f:
                f.write("Input Text:\n"+inp+"\n\nError Message:\n"+err)
            self.show_success_message(path)
        except Exception as e: self.show_error_dialog(str(e))

    def show_success_message(self, path):
        msg=QMessageBox(); msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Error Saved"); msg.setText("Saved successfully.")
        msg.setInformativeText(path); msg.addButton("Close", QMessageBox.ButtonRole.RejectRole); msg.exec()

    def copy_text(self):
        QApplication.clipboard().setText(self.text_output.toPlainText())

    def save_as_text(self):
        fp,_=QFileDialog.getSaveFileName(self, "Save As", "", "Text Files (*.txt)")
        if fp:
            with open(fp,'w') as f: f.write(self.text_output.toPlainText())

    def export_to_pdf(self):
        fp,_=QFileDialog.getSaveFileName(self, "Export as PDF", "", "PDF Files (*.pdf)")
        if fp:
            if not fp.lower().endswith('.pdf'): fp+='.pdf'
            printer=QPrinter(); printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(fp);
            doc=QTextDocument(); doc.setHtml(self.text_output.toHtml()); doc.print(printer)

    def clear_text(self):
        self.text_input.clear(); self.text_output.clear()

    def simulate_typing(self):
        text=self.text_output.toPlainText(); time.sleep(2)
        threading.Thread(target=self.type_with_interrupt, args=(text,)).start()
        keyboard.add_hotkey('ctrl+alt+c', self.interrupt_typing)

    def type_with_interrupt(self, text):
        for c in text:
            if self.interrupt_event.is_set(): break
            self.keyboard.type(c); time.sleep(self.typing_delay)

    def interrupt_typing(self):
        self.interrupt_event.set()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("viatica.png"))
    window = TextAnalyzerApp()
    window.show()
    sys.exit(app.exec())
