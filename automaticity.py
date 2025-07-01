import functions
import pyperclip
import pyautogui


def remove_double(input_text):
    lines = input_text.splitlines()
    new_lines = []
    for line in lines:
        if line not in new_lines or line in ['Plan', '']:
            new_lines.append(line)
    return '\n'.join(new_lines)


def analyze_text(Text_input):
    all_diseases = []
    master = functions.MasterClass(Text_input)
    
    # Loop through the diseases list
    for i in master.PMH_abbreviations(return_diseases=True):
        all_diseases.append(master.plan_chronic(i))
    
    
    # Age, PMH, vitals, labs
    age_PMH_labs = f"""is a {master.get_age()} year-old {master.get_sex()} with PMH of {master.PMH_abbreviations()} who presents today with c/o ***

{master.get_all_vitals()}

{master.show_abnormal_labs()}"""
    next_line = "\n"
    return f"""
    {age_PMH_labs}
{next_line}
{remove_double(next_line.join(all_diseases))}
    """
import pyperclip
import pyautogui
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QProgressBar
from PyQt6.QtCore import QTimer

# Function to display a small window with a progress bar, message, and a Paste button
def show_message(message):
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()

    label = QLabel(message)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    layout.addWidget(progress_bar)

    paste_button = QPushButton("Paste")
    paste_button.setEnabled(False)
    layout.addWidget(paste_button)

    window.setLayout(layout)
    window.setWindowTitle("Text Ready")
    window.show()

    # Function to handle the paste button click event
    def paste_button_clicked():
        window.close()
        allow_paste()

    paste_button.clicked.connect(paste_button_clicked)

    # Timer to periodically update the progress bar
    timer = QTimer()
    timer.start(100)  # Update every 100 milliseconds

    # Function to update the progress bar value
    def update_progress():
        value = progress_bar.value() + 1
        progress_bar.setValue(value)

        if value >= 100:
            timer.stop()
            paste_button.setEnabled(True)

    timer.timeout.connect(update_progress)

    app.exec()

# Get the current clipboard content
current_clipboard = pyperclip.paste()

# Function to allow text pasting
def allow_paste():
    # Simulate typing the analyzed text
    pyautogui.typewrite(analyzed_text)

    # Press Enter to confirm the paste (if needed)
    pyautogui.press('enter')

    # Restore the original clipboard content
    pyperclip.copy(current_clipboard)

    # Optional: print the analyzed text
    print(analyzed_text)

# Continuously monitor the clipboard for new text
while True:
    # Wait for new text to be copied to the clipboard
    new_text = pyperclip.waitForNewPaste()

    # Apply the text analysis function to the new text
    analyzed_text = analyze_text(new_text)

    # Copy the analyzed text to the clipboard
    pyperclip.copy(analyzed_text)

    # Show a small window indicating that the text is being analyzed
    show_message("Analyzing text...")

