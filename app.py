import mediapipe as mp
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QComboBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, \
    QCheckBox, QToolBar, QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from detection import DetectionWorker

class AppSignals(QObject):
    stop_detection = pyqtSignal()
    start_detection = pyqtSignal()
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
        self.start_session_button.clicked.connect(self.app_signals.start_detection.emit)
        self.end_session_button.clicked.connect(self.app_signals.stop_detection.emit)

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

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)

        self.show_settings_button = QPushButton("Settings")
        self.toolbar.addWidget(self.show_settings_button)

        self.start_session_button = QPushButton("Start Session")
        self.end_session_button = QPushButton("End Session")
        self.last_session_total_reps = QLabel("Total Reps: 0")
        self.last_session_avg_time_per_rep = QLabel("Avg Time per Rep: 0s")
        self.last_session_training_time = QLabel("Training Time: 0s")
        self.last_set_time = QLabel("Set Time: 0s")
        self.last_rest_time = QLabel("Rest Time: 0s")

        self.master = QVBoxLayout()

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()

        row1.addWidget(self.start_session_button, alignment=Qt.AlignCenter)
        row1.addWidget(self.end_session_button, alignment=Qt.AlignCenter)
        row2.addWidget(self.last_session_training_time, alignment=Qt.AlignCenter)
        row2.addWidget(self.last_session_total_reps, alignment=Qt.AlignCenter)
        row2.addWidget(self.last_session_avg_time_per_rep, alignment=Qt.AlignCenter)
        row3.addWidget(self.last_set_time, alignment=Qt.AlignCenter)
        row3.addWidget(self.last_rest_time, alignment=Qt.AlignCenter)

        self.master.addLayout(row1, 50)
        self.master.addLayout(row2, 25)
        self.master.addLayout(row3, 25)
        central_widget.setLayout(self.master)

        self.toggle_theme(self.theme)

    def settings(self):
        self.setWindowTitle("FitVision")
        self.setGeometry(250, 250, 650, 400)

    def show_settings_window(self):
        self.settings_window = SettingsWindow(self, self.settings_signals)
        self.settings_window.show()

    def update_reps_label(self, reps:int):
        self.last_session_total_reps.setText(f"Total Reps: {reps}")
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
        self.last_session_avg_time_per_rep.setText(f"Avg time per rep: {avg_time:.2f}s")
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
        self.last_session_training_time.setText(f"Total training time: {training_time}s")

    def update_set_time_label(self, set_time:int):
        self.last_set_time.setText(f"Set time: {set_time}s")
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
        self.last_rest_time.setText(f"Rest time: {rest_time}s")
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

    def toggle_feedback(self, state:bool):
        self.feedback_on = state
        if not state:
            self.last_session_avg_time_per_rep.setStyleSheet("")
            self.last_session_training_time.setStyleSheet("")
            self.last_set_time.setStyleSheet("")
            self.last_rest_time.setStyleSheet("")

    def toggle_theme(self, theme:str):
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
                            background-color: #C6C6C6;
                            margin-top: 0px;
                            border: none;
                            padding: 10px;
                            color: black;
                        }

                        QPushButton:hover {
                            background-color: #B3B3B3;
                        }

                    """)
        elif theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #565656;
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
                    background-color: #565656;
                    margin-top: 0px;
                    border: none;
                    padding: 10px;
                }

                QPushButton:hover {
                    background-color: #6E6E6E;
                }

            """)

class SettingsWindow(QWidget):
    def __init__(self, home:Home, settings_signals:SettingsSignals):
        super().__init__()
        self.initUI()
        self.home = home
        self.settings_signals = settings_signals

        self.toggle_feedback.setCheckState(Qt.Checked)
        self.toggle_feedback.stateChanged.connect(self.apply_toggle_feedback)
        self.theme_combobox.currentTextChanged.connect(self.apply_toggle_theme)

    def initUI(self):
        self.setWindowTitle("Settings")
        self.setGeometry(250, 250, 600, 400)

        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(["dark", "light"])

        self.toggle_feedback = QCheckBox("Colored feedback")
        self.master = QVBoxLayout()
        self.master.setAlignment(Qt.AlignCenter)
        self.master.addWidget(self.toggle_feedback)
        self.master.addWidget(self.theme_combobox)
        self.setLayout(self.master)

        self.setStyleSheet("""
        QWidget {
            background-color: #565656;
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