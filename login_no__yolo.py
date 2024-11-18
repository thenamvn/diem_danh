# -*- coding: utf-8 -*-
import sys
from PySide2.QtCore import QCoreApplication, QMetaObject, QRect, QThread, Signal, Qt
from PySide2.QtGui import QIcon, QPixmap, QImage
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QGroupBox, QLabel, QLineEdit, QFrame
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
    border-radius: 10px;
    border: 2px solid black;
}
"""

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setFixedSize(752, 433)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(530, 30, 211, 361))
        self.groupBox.setStyleSheet(STYLESHEET)
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(40, 30, 131, 141))
        self.label.setStyleSheet(u"QLabel {\n"
                                  "    border-radius: 10px;\n"
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
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(16, 32, 471, 361))
        self.label_2.setStyleSheet(u"QLabel {\n"
                                    "    border-radius: 10px;\n"
                                    "    border: 2px solid black;\n"
                                    "}")
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
        self.label_2.setText("")
    # retranslateUi

class VideoProcessingThread(QThread):
    new_frame_signal = Signal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv2.VideoCapture(0)
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.new_frame_signal.emit(pixmap)
            else:
                print("Failed to capture frame.")
            self.msleep(10)  # Chờ 10 mili giây trước khi xử lý khung hình tiếp theo

    def stop(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()

class FaceRecognitionThread(QThread):
    face_recognized_signal = Signal(str, str)
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
        self.detected_persons = False
        self.detected_cellphones = False
        self.object_counter = 1
        self.attendance_list = []
    def run(self):
        while self.running:
            ret, frame = self.parent().video_player.cap.read()
            if ret:
                self.counter += 1
                if self.counter == 3:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    frame_rgb = small_frame[:, :, ::-1]
                    face_locations = face_recognition.face_locations(frame_rgb)
                    if face_locations:
                        frame_center = (frame.shape[1] // 2, frame.shape[0] // 2)
                        min_distance = float('inf')
                        best_match_index = None
                        for face_location in face_locations:
                            face_center = ((face_location[1] + face_location[3]) // 2, (face_location[0] + face_location[2]) // 2)
                            distance = np.sqrt((face_center[0] - frame_center[0]) ** 2 + (face_center[1] - frame_center[1]) ** 2)
                            if distance < min_distance:
                                min_distance = distance
                                best_match_index = face_locations.index(face_location)
                        if best_match_index is not None:
                            face_encoding = face_recognition.face_encodings(frame_rgb, [face_locations[best_match_index]])[0]
                            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                            best_match_index = np.argmin(face_distances)
                            if best_match_index is not None and face_distances[best_match_index] < 0.6:
                                name = self.known_face_names[best_match_index]
                                id = self.known_face_ids[best_match_index]
                                if (name, id) != self.previous_face_info:
                                    self.face_recognized_signal.emit(name, id)
                                    self.previous_face_info = (name, id)
                                    self.attendance(name, id)
                    else:
                        self.no_face_frames_count += 1
                        if self.no_face_frames_count >= self.no_face_frames_threshold:
                            self.face_not_recognized_signal.emit()
                            self.previous_face_info = (None, None)
                            self.no_face_frames_count = 0
                    self.counter = 0         
            else:
                print("Failed to capture frame.")
            self.msleep(50)  # Chờ 100 mili giây trước khi xử lý khung hình tiếp theo

    def stop(self):
        self.running = False

    def attendance(self, name, id):
        current_time_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        current_month_year = datetime.now().strftime("%m/%Y")
        current_month = datetime.now().strftime("t%m")

        if (name, id) not in self.attendance_list:
            self.attendance_list.append((name, id))
            # Sử dụng creds để tạo một client để tương tác với Google Drive API
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
            client = gspread.authorize(creds)

            # Kiểm tra xem sheet cho tháng hiện tại có tồn tại không
            try:
                sheet = client.open("attendance").worksheet(current_month)
            except gspread.exceptions.WorksheetNotFound:
                # Nếu không tồn tại, tạo sheet mới
                sheet = client.open("attendance").add_worksheet(title=current_month, rows="100", cols="20")

            # Thêm dòng mới với name, id, thời gian hiện tại và tháng/năm
            row = [name, id, current_time_date, current_month_year]
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
        self.load_known_faces_firebase()
        # Set icon
        self.setWindowIcon(QIcon('faces/avatar.png'))

        # Add video player to the label
        self.video_player = VideoProcessingThread(self)
        self.video_player.new_frame_signal.connect(self.update_video_frame)
        self.video_player.start()

        # Start face recognition thread
        self.face_recognition_thread = FaceRecognitionThread(self)
        self.face_recognition_thread.face_recognized_signal.connect(self.update_face_info)
        self.face_recognition_thread.face_not_recognized_signal.connect(self.clear_face_info)
        self.face_recognition_thread.start()

    def update_video_frame(self, pixmap):
        self.ui.label_2.setPixmap(pixmap)
        self.ui.label_2.setScaledContents(True)

    def update_face_info(self, name, id):
            self.ui.lineEdit.setText(name)
            self.ui.lineEdit_2.setText(id)
            self.ui.lineEdit_2.setAlignment(Qt.AlignCenter)
            self.ui.lineEdit.setAlignment(Qt.AlignCenter)

            image_path = f"faces/{id}_extended.jpg"
            if os.path.isfile(image_path):
                pixmap = QPixmap(image_path)
                self.ui.label.setPixmap(pixmap)
                self.ui.label.setScaledContents(True)
            else:
                print(f"Error: File {image_path} could not be opened")

    def clear_face_info(self):
        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()
        self.ui.lineEdit.clearFocus()
        pixmap = QPixmap(f'faces/avatar.png')
        self.ui.label.setPixmap(pixmap)
        self.ui.label.setScaledContents(True)
    
    def load_known_faces_firebase(self):
            # Load known faces from Firebase
        known_faces = db_ref.get()
        if known_faces is not None:
            for face in known_faces:
                face_data = known_faces[face]
                image_path = f"faces/{face_data['id']}_face.jpg"
                extended_image_path = f"faces/{face_data['id']}_extended.jpg"
                if not os.path.exists(image_path):
                    try:
                        blob = bucket.blob(f"faces_data/{face_data['id']}_face.jpg")
                        blob.download_to_filename(image_path)
                        # Tải ảnh mở rộng bao quanh khuôn mặt
                        extended_blob = bucket.blob(f"faces_data/{face_data['id']}_extended.jpg")
                        extended_blob.download_to_filename(extended_image_path)
                    except Exception as e:
                        print(f"Không thể tải ảnh: {str(e)}")
                image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(image)
                if face_encoding:
                    self.known_face_encodings.append(face_encoding[0])
                    self.known_face_names.append(face_data['name'])
                    self.known_face_ids.append(face_data['id'])
        print("Loaded known faces from Firebase successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = FaceRecognitionApp()
    MainWindow.show()
    sys.exit(app.exec_())