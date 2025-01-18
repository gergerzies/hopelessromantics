import sys
import speech_recognition as sr
from gemini_translator import translate_gemini
from PyQt5.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel
import os
# print("Current working directory:", os.getcwd())

# Get the directory where the script is located
# script_dir = os.path.dirname(os.path.realpath(__file__))

# Create the full path to the image
# otomeUI_bg_path = os.path.join(script_dir, "images", "otomeUI_bg.png")






class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Transparent Window")


        # Get screen size
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Load the background image
        self.bg_image = QPixmap('images/otomeUI_bg.png')  # Relative path  # Load the image

        # Calculate the new window size to preserve the aspect ratio of the image
        image_width = self.bg_image.width()
        image_height = self.bg_image.height()
        new_height = screen_height
        new_width = int(image_width * (new_height / image_height))

        # Set the initial window size based on the scaled image size
        self.setGeometry(0, 0, new_width, new_height)

        # Set window flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Remove window border and keep it on top

        # Set the background image
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make the window background transparent

        # Variables for resizing and dragging
        self.is_dragging = False
        self.is_resizing = False
        self.drag_position = QPoint(0, 0)
        self.resize_border_thickness = 20  # Thickness for the resize area

        # Create the exit button and add to layout
        self.exit_button = QPushButton(self)
        self.exit_button.setStyleSheet(
            f"""
            QPushButton {{
                background-image: url(images/exit_button.png); 
                background-position: center; 
                background-repeat: no-repeat;
                border: none;
                background-size: cover;
            }}
            QPushButton:hover {{
                background-image: url(images/exit_buttonpress.png); 
                background-position: center; 
                background-repeat: no-repeat;
                border: none;
                background-size: cover;
            }}"""
        )
        self.exit_button.clicked.connect(self.close)

        # Create a custom button and add to layout
        self.blush_button = QPushButton(self)
        self.blush_button.setStyleSheet(
            f"""
            QPushButton {{
                background-image: url(images/blush_button.png); 
                background-position: center; 
                background-repeat: no-repeat;
                border: none;
                background-size: cover;
            }}
            QPushButton:hover {{
                background-image: url(images/blush_buttonpress.png); 
                background-position: center; 
                background-repeat: no-repeat;
                border: none;
                background-size: cover;
            }}"""
        )
        
        # Add label for romantic speech
        self.speech_label = QLabel(self)
        self.speech_label.setStyleSheet("background-color: black; color: white; font-family: MS Gothic; font-weight: bold;")  # Customize text style





        # Initialize speech recognition state
        self.is_listening = False
        self.recognizer_thread = None
        self.recognizer_worker = None

        # Toggle button for speech recognition
        self.toggle_button = QPushButton(self)
        self.toggle_button.setStyleSheet(
            f"""
            QPushButton {{
                background-image: url(images/begin_button.png); 
                background-position: center; 
                background-repeat: no-repeat;
                border: none;
                background-size: fill;
            }}
            QPushButton:hover {{
                background-image: url(images/begin_buttonpress.png); 
                background-position: center; 
                background-repeat: no-repeat;
                border: none;
                background-size: cover;
            }}"""
        )
        self.toggle_button.clicked.connect(self.toggle_speech_recognition)

        # Timer for text animation
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_text)
        self.text_to_display = ""
        self.current_text_index = 0
        self.text_speed = 50  # Speed in milliseconds between characters


    def toggle_speech_recognition(self):
        """Start or stop the speech recognition process."""
        if not self.is_listening:
            self.is_listening = True
            self.start_speech_recognition()
        else:
            self.is_listening = False
            self.stop_speech_recognition()

    def start_speech_recognition(self):
        """Start the speech recognizer in a separate thread."""
        self.recognizer_thread = QThread()
        self.recognizer_worker = SpeechRecognizerWorker()
        self.recognizer_worker.moveToThread(self.recognizer_thread)

        # Connect signals and slots
        self.recognizer_worker.text_ready.connect(self.start_text_animation)
        self.recognizer_thread.started.connect(self.recognizer_worker.run)
        self.recognizer_thread.finished.connect(self.recognizer_worker.stop_listening)  # Ensure cleanup


        # Start the thread
        self.recognizer_thread.start()

    def stop_speech_recognition(self):
        """Stop the speech recognizer."""
        if self.recognizer_worker:
            self.recognizer_worker.stop_listening() # Signal the worker to stop
        if self.recognizer_thread:
            self.recognizer_thread.quit()
            self.recognizer_thread.wait()
        self.recognizer_worker = None
        self.recognizer_thread = None

    def start_text_animation(self, text):
        """Animate text on the speech label."""
        self.text_to_display = text
        self.current_text_index = 0
        self.speech_label.setText("")
        self.animation_timer.start(self.text_speed)

    def update_text(self):
        """Update the text on the label character by character."""
        if self.current_text_index < len(self.text_to_display):
            self.speech_label.setText(self.text_to_display[:self.current_text_index + 1])
            self.current_text_index += 1
        else:
            self.animation_timer.stop()
        




    def resizeEvent(self, event):
        # Get the new size of the window
        window_width = self.width()
        window_height = self.height()

        # Resize the exit button
        button_width = window_width // 7  # Resize based on the window size (10% of window width)
        button_height = window_height // 22  # Resize based on the window size (15% of window height)
        self.exit_button.resize(button_width, button_height)
        self.exit_button.move(button_width//8 ,
                                window_height - button_height*4)
        
        # Resize the custom button
        self.blush_button.resize(button_width, button_height*7//3)
        self.blush_button.move(button_width//8 ,
                                window_height - button_height*3)
        

        
        # Resize label
        label_width = window_width // 10*6  # Resize based on the window size (10% of window width)
        label_height = window_height // 7  # Resize based on the window size (15% of window height)
        self.speech_label.resize(label_width, label_height)

        # Move label
        self.speech_label.move((window_width - label_width)// 2 ,
                                window_height - label_height//3*4)


        # Adjust font size
        font_size_label = int(label_height * 0.13)
        self.speech_label.setWordWrap(True)
        self.speech_label.setAlignment(Qt.AlignLeft)
        self.speech_label.setStyleSheet(f"background-color: black; color: white; font-size: {font_size_label}px; font-family: MS Gothic; font-weight: bold;")


        # Resize toggle button
        self.toggle_button.resize(button_width//2*3, button_height)
        self.toggle_button.move((window_width - (button_width//2*3))// 2, window_height //3*2 + button_height//2*3)



    def paintEvent(self, event):
        # Paint the scaled background image with fixed aspect ratio
        painter = QPainter(self)
        scaled_image = self.bg_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_image)  # Draw the scaled background image
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Start dragging if the mouse is not in the resize area
            if event.pos().x() < self.resize_border_thickness or event.pos().y() < self.resize_border_thickness or \
               event.pos().x() > self.width() - self.resize_border_thickness or event.pos().y() > self.height() - self.resize_border_thickness:
                self.is_resizing = True
            else:
                self.is_dragging = True
                self.drag_position = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Move the window
            self.move(event.globalPos() - self.drag_position)
        elif self.is_resizing:
            # Resize the window from the edge
            delta = event.globalPos() - self.pos()
            new_height = max(150, delta.y())  # Minimum height of 150
            new_width = int(self.bg_image.width() * (new_height / self.bg_image.height()))  # Adjust width to keep aspect ratio
            self.resize(new_width, new_height)
            
    def mouseReleaseEvent(self, event):
        # Stop dragging or resizing
        self.is_dragging = False
        self.is_resizing = False
        # Timer for text animation
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_text)

        self.text_to_display = ""
        self.current_text_index = 0
        self.text_speed = 20  # Speed in milliseconds between characters




class SpeechRecognizerWorker(QThread):
    """Worker class for speech recognition."""
    text_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_listening = True
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.stop_event = False  # Signal for stopping the worker

    def run(self):
        """Start the speech recognition loop."""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                while self.is_listening:
                    if self.stop_event:  # Check if stop has been signaled
                        break
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        text = self.recognizer.recognize_google(audio)
                        romantic_text = translate_gemini(text)
                        self.text_ready.emit(romantic_text)
                    except sr.WaitTimeoutError:
                        continue  # No speech detected, keep listening
                    except sr.UnknownValueError:
                        self.text_ready.emit("I didn't quite catch that. Could you try again?")
                    except sr.RequestError as e:
                        self.text_ready.emit(f"Error: {e}")
        except Exception as e:
            self.text_ready.emit(f"Unexpected error: {e}")

    def stop_listening(self):
        """Stop the listening loop and release resources."""
        self.is_listening = False
        self.stop_event = True  # Signal to exit the loop
        self.mic_release()  # Explicitly release the microphone

    def mic_release(self):
        """Release the microphone resource."""
        self.microphone = None
    
def main():
    app = QApplication(sys.argv)
    window = TransparentWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
