# -*- coding: utf-8 -*-

import sys
from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QThread, Signal, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGroupBox, QPushButton, QLabel, QLineEdit, QFrame, QFileDialog, QMessageBox, QProgressBar
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials, db, storage
import numpy as np
# Initialize Firebase
cred = credentials.Certificate('firebase/credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://facerecorgnite-default-rtdb.firebaseio.com',
    'storageBucket': 'facerecorgnite.appspot.com'
})
# Reference to your database and storage
db_ref = db.reference('faces')
bucket = storage.bucket()

style_sheet = """
    QPushButton {
        font: 75 italic 12pt "Segoe UI";
        border-radius: 10px;
        border: 2px solid black;
        background-color: rgb(63, 88, 232);
    }
    QLineEdit {
        font: 75 italic 12pt "Segoe UI";
        border-radius: 10px;
        border: 2px solid black;
    }
    QLabel {
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
        MainWindow.resize(752, 433)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(530, 30, 211, 361))
        self.groupBox.setStyleSheet(style_sheet)

        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(10, 310, 91, 41))
        self.pushButton.setStyleSheet(style_sheet)

        self.pushButton_select = QPushButton(self.groupBox)
        self.pushButton_select.setObjectName(u"pushButton_select")
        self.pushButton_select.setGeometry(QRect(110, 310, 91, 41))
        self.pushButton_select.setStyleSheet(style_sheet)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(40, 30, 131, 141))
        self.label.setStyleSheet(style_sheet)
        self.label.setFrameShape(QFrame.Panel)
        self.label.setPixmap(QPixmap(u"faces/avatar.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignCenter)  # Center the image

        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(20, 199, 171, 31))
        self.lineEdit.setStyleSheet(style_sheet)
        self.lineEdit.setAlignment(Qt.AlignCenter)
        self.lineEdit.setClearButtonEnabled(True) # Added clear button

        self.lineEdit_2 = QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(20, 259, 171,31))
        self.lineEdit_2.setStyleSheet(style_sheet)
        self.lineEdit_2.setAlignment(Qt.AlignCenter)
        self.lineEdit_2.setClearButtonEnabled(True) # Added clear button

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(16, 32, 471, 361))
        self.label_2.setStyleSheet(style_sheet)
        self.label_2.setAlignment(Qt.AlignCenter) # Center the video feed

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(16, 400, 471, 20))
        self.progressBar.setValue(0) # Start at 0
        self.progressBar.setTextVisible(False) # Hide percentage text initially

        self.statusLabel = QLabel(self.centralwidget)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setGeometry(QRect(16, 400 - 30, 471, 20))
        self.statusLabel.setText("")
        self.statusLabel.setAlignment(Qt.AlignCenter) # Center text

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Face Recognition", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"ID", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", "Chụp Ảnh", None))
        self.pushButton_select.setText(QCoreApplication.translate("MainWindow", "Chọn ảnh", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"H\u1ecd v\u00e0 t\u00ean", None))
        self.lineEdit_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"M\u00e3 sinh vi\u00ean", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", "Webcam Feed", None)) # Informative text
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
    face_processed_signal = Signal(np.ndarray, np.ndarray, str, str)
    face_detection_failed_signal = Signal()
    progress_signal = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame_rgb = None
        self.name = None
        self.student_id = None

    def set_data(self, frame_rgb, name, student_id):
        self.frame_rgb = frame_rgb
        self.name = name
        self.student_id = student_id

    def run(self):
        if self.frame_rgb is not None:
            self.progress_signal.emit(25, "Detecting face...")
            frame_rgb_small = cv2.resize(self.frame_rgb, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(frame_rgb_small)

            if face_locations:
                face_location = face_locations[0]
                top, right, bottom, left = [coord * 4 for coord in face_location]
                # Crop face and extended face
                self.progress_signal.emit(50, "Cropping face...")
                cropped_face = self.frame_rgb[top:bottom, left:right]
                face_center = ((left + right) // 2, (top + bottom) // 2)
                crop_width = int((right - left) * 2.5)
                crop_height = int((bottom - top) * 2.5)
                crop_x1 = max(0, face_center[0] - crop_width // 2)
                crop_y1 = max(0, face_center[1] - crop_height // 2)
                crop_x2 = min(self.frame_rgb.shape[1], face_center[0] + crop_width // 2)
                crop_y2 = min(self.frame_rgb.shape[0], face_center[1] + crop_height // 2)
                cropped_frame_extended = self.frame_rgb[crop_y1:crop_y2, crop_x1:crop_x2]

                self.face_processed_signal.emit(cropped_face, cropped_frame_extended, self.name, self.student_id)
                self.progress_signal.emit(100, "Face processing complete.")
            else:
              self.face_detection_failed_signal.emit()
              self.progress_signal.emit(0, "")

class FirebaseUploadThread(QThread):
    upload_complete_signal = Signal(bool, str)
    progress_signal = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.face_image = None
        self.extended_image = None
        self.name = None
        self.student_id = None


    def set_data(self, face_image, extended_image, name, student_id):
        self.face_image = face_image
        self.extended_image = extended_image
        self.name = name
        self.student_id = student_id

    def run(self):
      try:
        if self.face_image is not None and self.extended_image is not None:
          self.progress_signal.emit(25, "Encoding images...")
          # No need to save to disk, upload directly from memory
          _, face_encoded = cv2.imencode('.jpg', cv2.cvtColor(self.face_image, cv2.COLOR_RGB2BGR))
          face_data = face_encoded.tobytes()
          face_blob = bucket.blob(f'faces_data/{self.student_id}_face.jpg')
          if face_blob.exists():
              face_blob.delete()
          self.progress_signal.emit(50, "Uploading face image...")
          face_blob.upload_from_string(face_data, content_type='image/jpeg')
          face_blob.make_public()
          face_image_url = face_blob.public_url
          
          _, extended_encoded = cv2.imencode('.jpg', cv2.cvtColor(self.extended_image, cv2.COLOR_BGR2RGB)) # Ensure RGB format
          extended_data = extended_encoded.tobytes()
          extended_blob = bucket.blob(f'faces_data/{self.student_id}_extended.jpg')
          if extended_blob.exists():
                extended_blob.delete()
          self.progress_signal.emit(75, "Uploading extended face image...")
          extended_blob.upload_from_string(extended_data, content_type='image/jpeg')
          extended_blob.make_public()
          extended_image_url = extended_blob.public_url
          self.progress_signal.emit(90, "Updating database...")
          db_ref.push({
              'name': self.name,
              'id': self.student_id,
              'face_image_url': face_image_url,
              'extended_image_url': extended_image_url
          })
          self.progress_signal.emit(100, "Upload to Firebase successful!")
          self.upload_complete_signal.emit(True, "Upload to Firebase successful!")
        else:
            self.upload_complete_signal.emit(False, "Face or extended image is missing")
            self.progress_signal.emit(0, "")
      except Exception as e:
        self.upload_complete_signal.emit(False, f"Error uploading to Firebase: {e}")
        self.progress_signal.emit(0, "")

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Set icon
        self.setWindowIcon(QIcon('faces/avatar.png'))

        # Connect button signals
        self.ui.pushButton.clicked.connect(self.capture_image_firebase)
        self.ui.pushButton_select.clicked.connect(self.select_image_from_file)

        # Add video player to the label
        self.video_player = VideoProcessingThread(self)
        self.video_player.new_frame_signal.connect(self.update_video_frame)
        self.video_player.start_capture()
        self.current_frame = None  # Store the latest frame

        self.face_recognition_thread = FaceRecognitionThread(self)
        self.face_recognition_thread.face_processed_signal.connect(self.start_upload)
        self.face_recognition_thread.face_detection_failed_signal.connect(self.handle_face_detection_failed)
        self.face_recognition_thread.progress_signal.connect(self.update_progress)

        self.firebase_upload_thread = FirebaseUploadThread(self)
        self.firebase_upload_thread.upload_complete_signal.connect(self.handle_upload_result)
        self.firebase_upload_thread.progress_signal.connect(self.update_progress)

    def update_video_frame(self, pixmap):
        self.ui.label_2.setPixmap(pixmap)
        # Store the underlying QImage for later use (avoid converting back and forth)
        self.current_frame = pixmap.toImage()


    def select_image_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")

        if file_name:
            image = cv2.imread(file_name)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self._process_face(image)

    def capture_image_firebase(self):
        if self.current_frame:
            # Đảm bảo QImage được chuyển sang định dạng RGB888
            self.current_frame = self.current_frame.convertToFormat(QImage.Format_RGB888)
            width = self.current_frame.width()
            height = self.current_frame.height()
            ptr = self.current_frame.constBits()
            frame_rgb = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 3))
            self._process_face(frame_rgb)

    def _process_face(self, frame_rgb):
      name = self.ui.lineEdit.text().strip()
      student_id = self.ui.lineEdit_2.text().strip()
      if name and student_id:
          self.ui.progressBar.setValue(0)
          self.ui.statusLabel.setText("Starting face processing...")
          self.face_recognition_thread.set_data(frame_rgb, name, student_id)
          self.face_recognition_thread.start()
      else:
          QMessageBox.warning(self, "Warning", "Please enter name and student ID.")

    def start_upload(self, cropped_face, cropped_frame_extended, name, student_id):
        h, w, ch = cropped_frame_extended.shape
        bytes_per_line = ch * w
        cropped_frame_extended_copy = cropped_frame_extended.copy()
        q_img = QImage(cropped_frame_extended_copy.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.ui.label.setPixmap(pixmap)
        self.ui.label.setScaledContents(True)
        self.ui.statusLabel.setText("Starting upload...")
        self.ui.progressBar.setValue(0)
        self.firebase_upload_thread.set_data(cropped_face, cropped_frame_extended_copy, name, student_id)
        self.firebase_upload_thread.start()


    def handle_upload_result(self, success, message):
      self.ui.statusLabel.setText(message)
      if success:
        self.ui.progressBar.setValue(100)
      else:
        self.ui.progressBar.setValue(0)
        QMessageBox.critical(self, "Error", message)

    def handle_face_detection_failed(self):
      self.ui.progressBar.setValue(0)
      self.ui.statusLabel.setText("")
      QMessageBox.warning(self, "Warning", "No face detected.")

    def update_progress(self, value, message):
        self.ui.progressBar.setValue(value)
        self.ui.statusLabel.setText(message)

    def closeEvent(self, event):
        self.video_player.stop()
        self.face_recognition_thread.quit() # Stop face processing thread
        self.face_recognition_thread.wait() # Wait for face processing thread to stop
        self.firebase_upload_thread.quit() # Stop firebase upload thread
        self.firebase_upload_thread.wait()# Wait for firebase upload thread to stop
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = FaceRecognitionApp()
    MainWindow.show()
    sys.exit(app.exec())