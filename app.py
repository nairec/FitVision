import mediapipe as mp
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QComboBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, \
    QCheckBox, QToolBar, QMainWindow, QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize

from detection import DetectionWorker

class AppSignals(QObject):
    end_detection = pyqtSignal()
    start_detection = pyqtSignal()
    pause_detection = pyqtSignal(bool)
    update_reps = pyqtSignal(int)
    update_avg_time = pyqtSignal(float)
    update_training_time = pyqtSignal(int)
    update_set_time = pyqtSignal(int)
    update_rest_time = pyqtSignal(int)

class SettingsSignals(QObject):
    toggle_feedback = pyqtSignal(bool)
    toggle_theme = pyqtSignal(str)

class Home(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.initUI()
        self.settings()

        self.app_signals = AppSignals()
        self.settings_signals = SettingsSignals()
        self.detection_worker = DetectionWorker(self.app_signals)

        self.show_settings_button.clicked.connect(self.show_settings_window)
        self.pause_session_button.clicked.connect(self.update_pause_state)
        self.end_session_button.clicked.connect(self.end_detection)

        self.app_signals.update_reps.connect(self.update_reps_label)
        self.app_signals.update_avg_time.connect(self.update_avg_time_label)
        self.app_signals.update_training_time.connect(self.update_training_time_label)
        self.app_signals.update_set_time.connect(self.update_set_time_label)
        self.app_signals.update_rest_time.connect(self.update_rest_time_label)

        self.settings_signals.toggle_feedback.connect(self.toggle_feedback)
        self.settings_signals.toggle_theme.connect(self.toggle_theme)

        self.feedback_on = True
        self.bad_feedback_color = "#94322E"
        self.medium_feedback_color = "#F0E68C"
        self.good_feedback_color = "#80FF80"

    def initUI(self):
        self.paused = True
        self.detection_started = False

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                border-bottom: 1px solid #2D2D3F;  /* Cambiar el color de la línea a blanco */
            }
        """)
        self.addToolBar(self.toolbar)

        self.show_settings_button = QPushButton("Settings")
        self.toolbar.addWidget(self.show_settings_button)

        self.end_session_button = QPushButton()
        self.end_session_button.setStyleSheet("width: 10px; height: 10px; margin-right: 200px")
        self.pause_session_button = QPushButton()
        self.pause_session_button.setStyleSheet("background: none; border: none; padding: 0px; margin-left: 200px")
        self.pause_session_button.setIcon(QIcon("icons/mediaplay.png"))
        self.pause_session_button.setIconSize(QSize(60, 60))

        self.last_session_total_reps = QLabel("0")
        self.last_session_avg_time_per_rep = QLabel("0s")
        self.last_session_training_time = QLabel("0s")
        self.last_set_time = QLabel("0s")
        self.last_rest_time = QLabel("0s")

        self.master = QVBoxLayout()

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()

        box1_layout = QVBoxLayout()
        box2_layout = QVBoxLayout()
        box3_layout = QVBoxLayout()
        box4_layout = QVBoxLayout()
        box5_layout = QVBoxLayout()

        self.box1_widget = QWidget()
        self.box2_widget = QWidget()
        self.box3_widget = QWidget()
        self.box4_widget = QWidget()
        self.box5_widget = QWidget()

        box1_layout.addWidget(QLabel("Total training time"), alignment=Qt.AlignCenter)
        box1_layout.addWidget(self.last_session_training_time, alignment=Qt.AlignCenter)
        self.box1_widget.setLayout(box1_layout)
        self.box1_widget.setObjectName("box1")

        box2_layout.addWidget(QLabel("Total reps"), alignment=Qt.AlignCenter)
        box2_layout.addWidget(self.last_session_total_reps, alignment=Qt.AlignCenter)
        self.box2_widget.setLayout(box2_layout)
        self.box2_widget.setObjectName("box2")

        box3_layout.addWidget(QLabel("Avg time per rep"), alignment=Qt.AlignCenter)
        box3_layout.addWidget(self.last_session_avg_time_per_rep, alignment=Qt.AlignCenter)
        self.box3_widget.setLayout(box3_layout)
        self.box3_widget.setObjectName("box3")

        box4_layout.addWidget(QLabel("Set time"), alignment=Qt.AlignCenter)
        box4_layout.addWidget(self.last_set_time, alignment=Qt.AlignCenter)
        self.box4_widget.setLayout(box4_layout)
        self.box4_widget.setObjectName("box4")

        box5_layout.addWidget(QLabel("Rest time"), alignment=Qt.AlignCenter)
        box5_layout.addWidget(self.last_rest_time, alignment=Qt.AlignCenter)
        self.box5_widget.setLayout(box5_layout)
        self.box5_widget.setObjectName("box5")

        boxes = [self.box1_widget, self.box2_widget, self.box3_widget, self.box4_widget, self.box5_widget]
        for i, box in enumerate(boxes):
            box.setStyleSheet(f"""
                #box{i + 1} {{ 
                    border: 1px 
                    solid #1a4b8e; 
                    border-radius: 5px; 
                    background-color: #4F67AA;
                }}

                QLabel {{
                    background-color: #4F67AA;
                }}
            """)


        row1.addWidget(self.pause_session_button, alignment=Qt.AlignCenter)
        row1.addWidget(self.end_session_button, alignment=Qt.AlignCenter)
        row2.addWidget(self.box1_widget, alignment=Qt.AlignCenter)
        row2.addWidget(self.box2_widget, alignment=Qt.AlignCenter)
        row2.addWidget(self.box3_widget, alignment=Qt.AlignCenter)
        row3.addWidget(self.box4_widget, alignment=Qt.AlignCenter)
        row3.addWidget(self.box5_widget, alignment=Qt.AlignCenter)

        self.master.addLayout(row1, 50)
        self.master.addLayout(row2, 25)
        self.master.addLayout(row3, 25)
        central_widget.setLayout(self.master)

        self.toggle_theme(self.theme)

    def settings(self):
        self.setWindowTitle("FitVision")
        self.setGeometry(250, 250, 650, 500)

    def show_settings_window(self):
        self.settings_window = SettingsWindow(self.settings_signals, self.theme)
        self.settings_window.show()

    def start_detection(self):
        self.paused = False
        self.update_pause_icon()
        self.app_signals.start_detection.emit()

    def end_detection(self):
        self.paused = True
        self.detection_started = False
        self.update_pause_icon()
        self.app_signals.end_detection.emit()


    def update_reps_label(self, reps:int):
        self.last_session_total_reps.setText(f"{reps}")
        if self.feedback_on:
            if reps < 10:
                self.last_session_total_reps.setStyleSheet(f"color: {self.bad_feedback_color};")
            elif 10 <= reps <= 15:
                self.last_session_total_reps.setStyleSheet(f"color: {self.medium_feedback_color};")
            else:
                self.last_session_total_reps.setStyleSheet(f"color: {self.good_feedback_color};")
        else:
            self.last_session_total_reps.setStyleSheet("")

    def update_avg_time_label(self, avg_time:float):
        self.last_session_avg_time_per_rep.setText(f"{avg_time:.2f}")
        if self.feedback_on:
            if avg_time > 3.0:
                self.last_session_avg_time_per_rep.setStyleSheet(f"color: {self.bad_feedback_color};")
            elif 2.0 < avg_time <= 3.0:
                self.last_session_avg_time_per_rep.setStyleSheet(f"color: {self.medium_feedback_color};")
            else:
                self.last_session_avg_time_per_rep.setStyleSheet(f"color: {self.good_feedback_color};")
        else:
            self.last_session_avg_time_per_rep.setStyleSheet("")

    def update_training_time_label(self, training_time:int):
        self.last_session_training_time.setText(f"{training_time}s")

    def update_set_time_label(self, set_time:int):
        self.last_set_time.setText(f"{set_time}s")
        if self.feedback_on:
            if set_time > 180:
                self.last_set_time.setStyleSheet(f"color: {self.bad_feedback_color};")
            elif 100 < set_time <= 180:
                self.last_set_time.setStyleSheet(f"color: {self.good_feedback_color};")
            elif 50 < set_time <= 100:
                self.last_set_time.setStyleSheet(f"color: {self.medium_feedback_color};")
            elif 0 < set_time <= 50:
                self.last_set_time.setStyleSheet(f"color: {self.bad_feedback_color};")
        else:
            self.last_set_time.setStyleSheet("")

    def update_rest_time_label(self, rest_time:int):
        self.last_rest_time.setText(f"{rest_time}s")
        if self.feedback_on:
            if rest_time > 180:
                self.last_rest_time.setStyleSheet(f"color: {self.bad_feedback_color};")
            elif 100 < rest_time <= 180:
                self.last_rest_time.setStyleSheet(f"color: {self.good_feedback_color};")
            elif 50 < rest_time <= 100:
                self.last_rest_time.setStyleSheet(f"color: {self.medium_feedback_color};")
            elif 0 < rest_time <= 50:
                self.last_rest_time.setStyleSheet(f"color: {self.bad_feedback_color};")
        else:
            self.last_rest_time.setStyleSheet("")

    def update_pause_state(self):
        if self.detection_started: # If detection has already started, pause
            self.paused = not self.paused
            self.update_pause_icon()
            self.app_signals.pause_detection.emit(self.paused)
        else: # If detection hasn't started, start it
            self.detection_started = True
            self.start_detection()

    def update_pause_icon(self):
        if self.paused:
            self.pause_session_button.setIcon(QIcon("icons/mediaplay.png"))
            self.pause_session_button.setIconSize(QSize(60, 60))
        else:
            self.pause_session_button.setIcon(QIcon("icons/mediapause.png"))
            self.pause_session_button.setIconSize(QSize(60, 60))

    def toggle_feedback(self, state:bool):
        self.feedback_on = state
        if not state:
            self.last_session_avg_time_per_rep.setStyleSheet("")
            self.last_session_training_time.setStyleSheet("")
            self.last_set_time.setStyleSheet("")
            self.last_rest_time.setStyleSheet("")

    def toggle_theme(self, theme:str):
        self.theme = theme
        if theme == "light":
            self.setStyleSheet("""
                QWidget {
                    background-color: #EBEBEB;
                }

                QPushButton {
                    background-color: #1c549f;
                    padding: 20px;
                    border-width: 5px;
                    border-style: solid;
                    border-radius: 5px;
                    border-color: #1a4b8e;
                    color: white;
                    margin-top: 40px;
                }

                QPushButton:hover {
                    background-color: #1a4b8e;
                }
            """)

            self.show_settings_button.setStyleSheet("""
                        QPushButton {
                            background-color: none;
                            margin-top: 0px;
                            border: none;
                            padding: 10px;
                            color: black;
                        }

                        QPushButton:hover {
                            background-color: #B3B3B3;
                        }

                    """)

            boxes = [self.box1_widget, self.box2_widget, self.box3_widget, self.box4_widget, self.box5_widget]
            for i, box in enumerate(boxes):
                box.setStyleSheet(f"""
                    #box{i + 1} {{ 
                        border: 1px 
                        solid #1a4b8e; 
                        border-radius: 5px; 
                        background-color: #E0E0FC;
                    }}
                    
                    QLabel {{
                        background-color: #E0E0FC;
                    }}
                """)

        elif theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #14141B;
                    color: white;
                }

                QPushButton {
                    background-color: #1c549f;
                    padding: 20px;
                    border-width: 5px;
                    border-style: solid;
                    border-radius: 5px;
                    border-color: #1a4b8e;
                    color: white;
                    margin-top: 40px;
                }

                QPushButton:hover {
                    background-color: #1a4b8e;
                }
            """)

            self.show_settings_button.setStyleSheet("""
                QPushButton {
                    background-color: none;
                    margin-top: 0px;
                    border: none;
                    padding: 10px;
                }

                QPushButton:hover {
                    background-color: #6E6E6E;
                }

            """)

            boxes = [self.box1_widget, self.box2_widget, self.box3_widget, self.box4_widget, self.box5_widget]
            for i, box in enumerate(boxes):
                box.setStyleSheet(f"""
                    #box{i + 1} {{ 
                        border: 1px 
                        solid #1a4b8e; 
                        border-radius: 5px; 
                        background-color: #4F67AA;
                    }}

                    QLabel {{
                        background-color: #4F67AA;
                    }}
                """)

class SettingsWindow(QWidget):
    def __init__(self, settings_signals:SettingsSignals, currentTheme:str):
        super().__init__()
        self.settings_signals = settings_signals
        self.currentTheme = currentTheme
        self.initUI()

        self.toggle_feedback.setCheckState(Qt.Checked)
        self.toggle_feedback.stateChanged.connect(self.apply_toggle_feedback)
        self.theme_combobox.currentTextChanged.connect(self.apply_toggle_theme)

    def initUI(self):
        self.setWindowTitle("Settings")
        self.setGeometry(250, 250, 600, 400)

        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(["dark", "light"])
        self.theme_combobox.setCurrentText(self.currentTheme)

        self.toggle_feedback = QCheckBox("Colored feedback")
        self.master = QVBoxLayout()
        self.master.setAlignment(Qt.AlignCenter)
        self.master.addWidget(self.toggle_feedback)
        self.master.addWidget(self.theme_combobox)
        self.setLayout(self.master)

        self.setStyleSheet("""
        QWidget {
            background-color: #9F9F9F;
        }
        """)

    def apply_toggle_feedback(self, state:bool):
        if state == Qt.Checked:
            self.settings_signals.toggle_feedback.emit(True)
        else:
            self.settings_signals.toggle_feedback.emit(False)

    def apply_toggle_theme(self, theme:str):
        self.settings_signals.toggle_theme.emit(theme)

if __name__ == '__main__':
    app = QApplication([])
    main = Home()
    main.show()
    app.exec_()