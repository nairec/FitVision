import cv2
import mediapipe as mp
import numpy as np
import time
from PyQt5.QtCore import QThread, QTimer

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class DetectionWorker(QThread):
    def __init__(self, app_signals):
        super().__init__()
        self.app_signals = app_signals
        self.paused = False
        self.running = False
        self.last_rep_time = 0 # keeps track of the last rep time for detecting rest or mid-set time
        self.status = "resting" # resting by default until the first rep

        # Total training session timer
        self.total_training_time = 0
        self.training_timer = QTimer()
        self.training_timer.timeout.connect(self.update_total_training_time)

        # Set and rest times
        self.set_training_time = 0
        self.rest_training_time = 0

        self.app_signals.end_detection.connect(self.end_detection)
        self.app_signals.start_detection.connect(self.start_detection)
        self.app_signals.pause_detection.connect(self.pause_detection)

    def capture_and_detect_video(self):
        # VIDEO FEED
        cap = cv2.VideoCapture(0)  # Camera code may be changed depending on the device
        counter = 0

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            stage = "down"
            times_hist = []
            rep_start_time = None
            while cap.isOpened() and self.running and not self.paused:
                ret, frame = cap.read()

                # Recolor image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = pose.process(image)

                # Recolor back
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark

                    # Get limbs
                    l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    # Calculate angles
                    angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)

                    # Visualize angles
                    cv2.putText(image, str(angle), tuple(np.multiply(l_elbow, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    # Curl count
                    if angle > 160:
                        stage = "down"
                        rep_start_time = time.time() if rep_start_time is None else rep_start_time
                    elif angle < 30 and stage == "down":
                        stage = "up"
                        counter += 1
                        end_time = time.time()
                        self.last_rep_time = end_time
                        rep_time = end_time - rep_start_time
                        rep_start_time = None
                        times_hist.append(rep_time)



                    average_time = sum(times_hist) / len(times_hist)
                    self.app_signals.update_reps.emit(counter)
                    self.app_signals.update_avg_time.emit(average_time)

                except:
                    pass

                #Render detection
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(255,255,255), thickness=2, circle_radius=2),
                                        mp_drawing.DrawingSpec(color=(255,255,255), thickness=2, circle_radius=2))
                cv2.imshow('frame', image)


                if cv2.waitKey(10) & 0xFF == ord('\n') or not self.running:
                    self.end_detection()

            if not self.paused: # Kills the process if it stops and is not paused
                cap.release()
                cv2.destroyAllWindows()

    def start_detection(self):
        self.total_training_time = 0
        self.set_training_time = 0
        self.rest_training_time = 0
        self.training_timer.start(1000)
        self.running = True
        self.paused = False
        self.capture_and_detect_video()

    def end_detection(self):
        self.training_timer.stop()
        self.running = False

    def pause_detection(self, paused:bool):
        self.paused = paused
        if paused:
            self.training_timer.stop()
        else:
            self.training_timer.start(1000)
            self.capture_and_detect_video()


    def update_total_training_time(self):
        self.total_training_time += 1
        self.app_signals.update_training_time.emit(self.total_training_time)

        # Detect if user is resting or mid-set
        if np.abs(self.last_rep_time - time.time()) > 5:
            self.status = "resting"
            self.set_training_time = 0
            self.rest_training_time += 1
            self.app_signals.update_rest_time.emit(self.rest_training_time)
        else:
            self.status = "mid-set"
            self.rest_training_time = 0
            self.set_training_time += 1
            self.app_signals.update_set_time.emit(self.set_training_time)

    # Function for calculating angles
    def calculate_angle(self, a: list, b: list, c: list) -> float:
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle