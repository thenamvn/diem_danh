# -*- coding: utf-8 -*-

import sys
from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QThread, Signal, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGroupBox, QLabel, QLineEdit, QFrame
import cv2
import face_recognition
import os
import numpy as np
import firebase_admin
from firebase_admin import credentials, db, storage
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate('firebase/credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://facerecorgnite-default-rtdb.firebaseio.com',
    'storageBucket': 'facerecorgnite.appspot.com'
})
# Reference to your database and storage
db_ref = db.reference('faces')
bucket = storage.bucket()
STYLESHEET = """
QLineEdit {
    font: 75 italic 12pt "Segoe UI";
    border-radius: 10px;
    border: 2px solid black;
}

QGroupBox {
    border: 2px solid black;
}
"""
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setFixedSize(752, 463) # increase height
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(530, 30, 211, 391)) # increase height
        self.groupBox.setStyleSheet(STYLESHEET)
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(40, 30, 131, 141))
        self.label.setStyleSheet(u"QLabel {\n"
                                  "    border: 2px solid black;\n"
                                  "}")
        self.label.setFrameShape(QFrame.Panel)
        self.label.setPixmap(QPixmap(u"faces/avatar.png"))
        self.label.setScaledContents(True)
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(20, 199, 171, 31))
        self.lineEdit.setStyleSheet(STYLESHEET)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setAlignment(Qt.AlignCenter)
        self.lineEdit.setFocusPolicy(Qt.NoFocus)

        self.lineEdit_2 = QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(20, 259, 171,31))
        self.lineEdit_2.setAlignment(Qt.AlignCenter)
        self.lineEdit_2.setFocusPolicy(Qt.NoFocus)
        self.lineEdit_2.setStyleSheet(STYLESHEET)
        self.lineEdit_2.setReadOnly(True)
        
        self.label_spoofing = QLabel(self.groupBox)  # Added spoofing label
        self.label_spoofing.setObjectName("label_spoofing")
        self.label_spoofing.setGeometry(QRect(20, 319, 171, 51))  # Adjust position and size
        self.label_spoofing.setStyleSheet("QLabel { border: 2px solid black; padding: 5px;}")
        self.label_spoofing.setAlignment(Qt.AlignCenter)
        
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(16, 32, 471, 391)) # increase height
        self.label_2.setStyleSheet(u"QLabel {\n"
                                    "    border: 2px solid black;\n"
                                    "}")
        self.label_2.setAlignment(Qt.AlignCenter)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Face Recognition", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"ID", None))
        self.label.setText("")
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Họ và tên", None))
        self.lineEdit_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Mã sinh viên", None))
        self.label_spoofing.setText(QCoreApplication.translate("MainWindow", "Spoof Status", None))
        self.label_2.setText("Webcam Feed")
    # retranslateUi

class VideoProcessingThread(QThread):
    new_frame_signal = Signal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv2.VideoCapture(0)
        self.running = True
         # use a timer to emit the signal periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.frame_rate = 30  # Target frame rate
        self.delay = int(1000 / self.frame_rate)

    def start_capture(self):
        self.timer.start(self.delay)

    def stop(self):
        self.running = False
        self.timer.stop()
        self.wait()
        if self.cap.isOpened():
            self.cap.release()
    def process_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.new_frame_signal.emit(pixmap)
            else:
                print("Failed to capture frame.")

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

class FaceRecognitionThread(QThread):
    face_recognized_signal = Signal(str, str, bool, str)  # Add spoofing info to the signal
    face_not_recognized_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.known_face_encodings = parent.known_face_encodings
        self.known_face_names = parent.known_face_names
        self.known_face_ids = parent.known_face_ids
        self.previous_face_info = (None, None)
        self.no_face_frames_count = 0
        self.no_face_frames_threshold = 3
        self.counter = 0
        self.attendance_list = []

    def get_best_match_index(self,face_locations, frame_center):
        min_distance = float('inf')
        best_match_index = None
        for index, face_location in enumerate(face_locations):
            face_center_x = (face_location[1] + face_location[3]) // 2
            face_center_y = (face_location[0] + face_location[2]) // 2
            distance = np.sqrt((face_center_x - frame_center[0]) ** 2 + (face_center_y - frame_center[1]) ** 2)
            if distance < min_distance:
                min_distance = distance
                best_match_index = index
        return best_match_index
    
    def detect_spoofing(self, frame):
        """
        Phát hiện spoofing bằng cách kết hợp face detection và edge analysis
        """
        # Chuyển sang ảnh xám
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Bước 1: Phát hiện khuôn mặt
        face_locations = face_recognition.face_locations(frame)
        
        # Bước 2: Phát hiện cạnh với Canny
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 100, 200)
        
        is_spoof = False
        spoof_score = 0
        evidence = []
        
        for face_location in face_locations:
            top, right, bottom, left = face_location
            
            # Mở rộng vùng ROI ra xung quanh khuôn mặt để bắt được viền thiết bị
            padding = 50
            top = max(0, top - padding)
            bottom = min(frame.shape[0], bottom + padding)
            left = max(0, left - padding)
            right = min(frame.shape[1], right + padding)
            
            # Lấy vùng ROI từ ảnh cạnh
            face_roi_edges = edges[top:bottom, left:right]
            
            # Phân tích đặc điểm của cạnh trong vùng ROI
            spoof_characteristics = self.analyze_edge_patterns(face_roi_edges)
            
            if spoof_characteristics['is_spoof']:
                is_spoof = True
                spoof_score = spoof_characteristics['score']
                evidence = spoof_characteristics['evidence']
                
        return {
            'is_spoof': is_spoof,
            'spoof_score': spoof_score,
            'evidence': evidence,
            'edges': edges,
            'face_locations': face_locations
        }

    def analyze_edge_patterns(self, roi_edges):
        """
        Phân tích các đặc điểm của cạnh để phát hiện spoofing
        """
        # Tìm các đường contour
        contours, _ = cv2.findContours(roi_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        evidence = []
        total_score = 0
        
        # 1. Kiểm tra đường thẳng song song/vuông góc (đặc trưng của thiết bị)
        lines = cv2.HoughLinesP(roi_edges, 1, np.pi/180, 30, minLineLength=30, maxLineGap=10)
        if lines is not None:
            parallel_lines = 0
            perpendicular_lines = 0
            
            for i in range(len(lines)):
                for j in range(i + 1, len(lines)):
                    angle = self.calculate_angle(lines[i][0], lines[j][0])
                    if angle < 5 or angle > 175:  # Song song
                        parallel_lines += 1
                    elif 85 < angle < 95:  # Vuông góc
                        perpendicular_lines += 1
            
            if parallel_lines > 2 or perpendicular_lines > 2:
                evidence.append("Phat hien duong thang / song song / vuong goc")
                total_score += 0.4
        
        # 2. Kiểm tra mật độ cạnh đều đặn (đặc trưng của màn hình)
        edge_density = np.sum(roi_edges > 0) / roi_edges.size
        if 0.1 < edge_density < 0.3:  # Ngưỡng điều chỉnh theo thực tế
            evidence.append(f"Mat do bat thuong: {edge_density:.2f}")
            total_score += 0.3
        
        # 3. Kiểm tra chu vi và diện tích của contour
        if len(contours) > 0:
            areas = [cv2.contourArea(cnt) for cnt in contours]
            perimeters = [cv2.arcLength(cnt, True) for cnt in contours]
            
            # Tính tỷ lệ chu vi/diện tích
            for area, perimeter in zip(areas, perimeters):
                if area > 0:
                    ratio = perimeter / np.sqrt(area)
                    if ratio > 5:  # Ngưỡng điều chỉnh theo thực tế
                        evidence.append(f"Ty le chu vi, dien tich bat thuong: {ratio:.2f}")
                        total_score += 0.3
        
        return {
            'is_spoof': total_score > 0.5,  # Ngưỡng điều chỉnh theo thực tế
            'score': total_score,
            'evidence': evidence
        }

    def calculate_angle(self, line1, line2):
        """
        Tính góc giữa hai đường thẳng
        """
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2
        
        angle1 = np.arctan2(y2 - y1, x2 - x1)
        angle2 = np.arctan2(y4 - y3, x4 - x3)
        
        angle = np.abs(np.degrees(angle1 - angle2))
        if angle > 180:
            angle = 360 - angle
        return angle


    def run(self):
        while self.running:
            ret, frame = self.parent().video_player.cap.read()
            if ret:
                self.counter += 1
                if self.counter == 4:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    frame_rgb = small_frame[:, :, ::-1]
                    face_locations = face_recognition.face_locations(frame_rgb)
                    spoof_result = self.detect_spoofing(frame)
                    is_spoof = spoof_result['is_spoof']
                    evidence = spoof_result['evidence']
                    if face_locations:
                        # Tìm khuôn mặt lớn nhất
                        max_area = 0
                        best_match_index = None
                        for i, face_location in enumerate(face_locations):
                            top, right, bottom, left = face_location
                            area = (bottom - top) * (right - left)  # Diện tích của khuôn mặt
                            if area > max_area:
                                max_area = area
                                best_match_index = i
                        # Xử lý khuôn mặt lớn nhất
                        if best_match_index is not None:
                            face_encoding = face_recognition.face_encodings(frame_rgb, [face_locations[best_match_index]])[0]
                            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                            best_match_index = np.argmin(face_distances)
                            if best_match_index is not None and face_distances[best_match_index] < 0.6:
                                name = self.known_face_names[best_match_index]
                                id = self.known_face_ids[best_match_index]
                                if (name, id) != self.previous_face_info:
                                    self.face_recognized_signal.emit(name, id, is_spoof, ','.join(evidence))  # Emit with spoofing info
                                    self.previous_face_info = (name, id)
                                    self.attendance(name, id)  # Gọi hàm attendance
                    else:
                        self.no_face_frames_count += 1
                        if self.no_face_frames_count >= self.no_face_frames_threshold:
                            self.face_not_recognized_signal.emit()
                            self.previous_face_info = (None, None)
                            self.no_face_frames_count = 0
                    self.counter = 0         
            else:
                print("Failed to capture frame.")
            self.msleep(100)

    def stop(self):
        self.running = False


    def attendance(self, name, id):
        if (name, id) not in self.attendance_list:
            self.attendance_list.append((name, id))
            # Sử dụng creds để tạo một client để tương tác với Google Drive API
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
            client = gspread.authorize(creds)

            # Tìm một workbook bằng tên và mở sheet đầu tiên
            # Đảm bảo rằng bạn đã chia sẻ workbook này với client_email trong client_secret.json
            sheet = client.open("attendance").sheet1

            # Thêm dòng mới với name, id, ngày và giờ
            now = datetime.now()  # Lấy thời gian hiện tại
            date_string = now.strftime("%m/%d/%Y")  # Định dạng ngày
            time_string = now.strftime("%H:%M:%S")  # Định dạng giờ
            row = [name, id, date_string, time_string]
            index = 1  # Chèn vào dòng đầu tiên
            sheet.insert_row(row, index)

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self._load_known_faces_firebase()
        # Set icon
        self.setWindowIcon(QIcon('faces/avatar.png'))

        # Add video player to the label
        self.video_player = VideoProcessingThread(self)
        self.video_player.new_frame_signal.connect(self._update_video_frame)
        self.video_player.start_capture()

        # Start face recognition thread
        self.face_recognition_thread = FaceRecognitionThread(self)
        self.face_recognition_thread.face_recognized_signal.connect(self._update_face_info)
        self.face_recognition_thread.face_not_recognized_signal.connect(self._clear_face_info)
        self.face_recognition_thread.start()
        # Listen for changes in Firebase database
        self._setup_firebase_listener()

    def _update_video_frame(self, pixmap):
        self.ui.label_2.setPixmap(pixmap)
        self.ui.label_2.setScaledContents(True)

    def _update_face_info(self, name, id, is_spoof, evidence):
            self.ui.lineEdit.setText(name)
            self.ui.lineEdit_2.setText(id)
            self.ui.lineEdit_2.setAlignment(Qt.AlignCenter)
            self.ui.lineEdit.setAlignment(Qt.AlignCenter)
            
            spoofing_text = "Real"
            if is_spoof:
                spoofing_text = "Spoofing"
                print(f"Spoof Detected! Evidence: {evidence}")  # print to console
                self.ui.label_spoofing.setStyleSheet("QLabel { border: 2px solid black; padding: 5px; background-color: red; color: white;}")
            else:
                 self.ui.label_spoofing.setStyleSheet("QLabel { border: 2px solid black; padding: 5px; background-color: green; color: white;}")

            self.ui.label_spoofing.setText(spoofing_text)

            image_path = f"faces/{id}_extended.jpg"
            if os.path.isfile(image_path):
                pixmap = QPixmap(image_path)
                self.ui.label.setPixmap(pixmap)
                self.ui.label.setScaledContents(True)
            else:
                print(f"Error: File {image_path} could not be opened")

    def _clear_face_info(self):
        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()
        self.ui.lineEdit.clearFocus()
        self.ui.label_spoofing.setText("Spoof Status")
        self.ui.label_spoofing.setStyleSheet("QLabel { border: 2px solid black; padding: 5px;}")
        pixmap = QPixmap(f'faces/avatar.png')
        self.ui.label.setPixmap(pixmap)
        self.ui.label.setScaledContents(True)
    
    def _load_known_faces_firebase(self):
            # Load known faces from Firebase
        known_faces = db_ref.get()
        if known_faces is not None:
            for face in known_faces:
                face_data = known_faces[face]
                image_path = f"faces/{face_data['id']}_face.jpg"
                extended_image_path = f"faces/{face_data['id']}_extended.jpg"
                if not os.path.exists(image_path):
                    blob = bucket.blob(f"faces_data/{face_data['id']}_face.jpg")
                    blob.download_to_filename(image_path)
                    blob = bucket.blob(f"faces_data/{face_data['id']}_extended.jpg")
                    blob.download_to_filename(extended_image_path)
                image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(image)
                if face_encoding:
                    self.known_face_encodings.append(face_encoding[0])
                    self.known_face_names.append(face_data['name'])
                    self.known_face_ids.append(face_data['id'])
        print("Loaded known faces from Firebase successfully!")

    def _setup_firebase_listener(self):
            # Set up a listener for changes in the Firebase database
        def face_data_changed(event):
            if event.data is not None:  # Check if data exists (not a remove operation)
                self._load_known_faces_firebase()  # Reload face data
                print("Firebase data changed, updated known faces")
            else:
                print("A face entry has been removed from Firebase.")
        db_ref.listen(face_data_changed)

    def closeEvent(self, event):
        self.video_player.stop()
        self.face_recognition_thread.stop()
        event.accept()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = FaceRecognitionApp()
    MainWindow.show()
    sys.exit(app.exec())