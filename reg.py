# -*- coding: utf-8 -*-

import sys
from PySide2.QtCore import QCoreApplication, QMetaObject, QRect, QThread, Signal, Qt
from PySide2.QtGui import QIcon, QPixmap, QImage
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QGroupBox, QPushButton, QLabel, QLineEdit, QFrame
import cv2
import face_recognition
import os
import firebase_admin
from firebase_admin import credentials, db, storage
from PySide2.QtWidgets import QFileDialog

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
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(20, 199, 171, 31))
        self.lineEdit.setStyleSheet(style_sheet)
        self.lineEdit.setAlignment(Qt.AlignCenter)
        self.lineEdit.setReadOnly(False)
        self.lineEdit.setClearButtonEnabled(False)
        self.lineEdit_2 = QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(20, 259, 171,31))
        self.lineEdit_2.setStyleSheet(style_sheet)
        self.lineEdit_2.setAlignment(Qt.AlignCenter)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(16, 32, 471, 361))
        self.label_2.setStyleSheet(style_sheet)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Face Recognition", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"ID", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", "Chụp Ảnh", None))
        self.pushButton_select.setText(QCoreApplication.translate("MainWindow", "Chọn ảnh", None))
        self.label.setText("")
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"H\u1ecd v\u00e0 t\u00ean", None))
        self.lineEdit_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"M\u00e3 sinh vi\u00ean", None))
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
        self.video_player.start()

    def update_video_frame(self, pixmap):
        self.ui.label_2.setPixmap(pixmap)
        self.ui.label_2.setScaledContents(True)
    

    def select_image_from_file(self):
        # Mở hộp thoại để chọn file ảnh
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        
        if file_name:
            # Đọc và hiển thị ảnh từ file
            image = cv2.imread(file_name)
            if image is not None:
                frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(frame_rgb)
                if face_locations:
                    face_location = face_locations[0]
                    top, right, bottom, left = face_location

                    # Cắt ảnh chỉ chứa khuôn mặt
                    cropped_face = frame_rgb[top:bottom, left:right]

                    # Cắt ảnh lớn hơn một chút, với khuôn mặt là trung tâm
                    face_center = ((left + right) // 2, (top + bottom) // 2)
                    crop_width = int((right - left) * 2)
                    crop_height = int((bottom - top) * 2)
                    crop_x1 = max(0, face_center[0] - crop_width // 2)
                    crop_y1 = max(0, face_center[1] - crop_height // 2)
                    crop_x2 = min(frame_rgb.shape[1], face_center[0] + crop_width // 2)
                    crop_y2 = min(frame_rgb.shape[0], face_center[1] + crop_height // 2)
                    cropped_frame_extended = frame_rgb[crop_y1:crop_y2, crop_x1:crop_x2]
                    
                    # Hiển thị ảnh mở rộng lên QLabel
                    extended_image = cv2.cvtColor(cropped_frame_extended, cv2.COLOR_RGB2BGR)
                    q_img = QImage(extended_image.data, extended_image.shape[1], extended_image.shape[0], 
                                extended_image.strides[0], QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_img)
                    self.ui.label.setPixmap(pixmap)
                    self.ui.label.setScaledContents(True)

                    # Lưu và upload ảnh tương tự như trong hàm capture_image_firebase
                    name = self.ui.lineEdit.text()
                    id = self.ui.lineEdit_2.text()
                    if name and id:
                        face_file_path = os.path.join(os.getcwd(), 'face_only.jpg')
                        cv2.imwrite(face_file_path, cv2.cvtColor(cropped_face, cv2.COLOR_RGB2BGR))
                        face_blob = bucket.blob(f'faces_data/{id}_face.jpg')
                        face_blob.upload_from_filename(face_file_path)
                        face_blob.make_public()
                        face_image_url = face_blob.public_url

                        extended_file_path = os.path.join(os.getcwd(), 'extended_face.jpg')
                        cv2.imwrite(extended_file_path, cv2.cvtColor(cropped_frame_extended, cv2.COLOR_RGB2BGR))
                        extended_blob = bucket.blob(f'faces_data/{id}_extended.jpg')
                        extended_blob.upload_from_filename(extended_file_path)
                        extended_blob.make_public()
                        extended_image_url = extended_blob.public_url

                        db_ref.push({
                            'name': name,
                            'id': id,
                            'face_image_url': face_image_url,
                            'extended_image_url': extended_image_url
                        })
                        print("Upload to Firebase successful!")

    def capture_image_firebase(self):
        ret, frame = self.video_player.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(frame_rgb)
            if face_locations:
                face_location = face_locations[0]
                top, right, bottom, left = face_location

                # Cắt ảnh chỉ chứa khuôn mặt
                cropped_face = frame_rgb[top:bottom, left:right]

                # Cắt ảnh lớn hơn một chút, với khuôn mặt là trung tâm
                face_center = ((left + right) // 2, (top + bottom) // 2)
                # Xác định chiều rộng và chiều cao của vùng cắt mở rộng
                crop_width = int((right - left) * 2)  # Gấp đôi chiều rộng khuôn mặt
                crop_height = int((bottom - top) * 2)  # Gấp đôi chiều cao khuôn mặt
                # Tính toán tọa độ của vùng cắt mở rộng
                crop_x1 = max(0, face_center[0] - crop_width // 2)
                crop_y1 = max(0, face_center[1] - crop_height // 2)
                crop_x2 = min(frame_rgb.shape[1], face_center[0] + crop_width // 2)
                crop_y2 = min(frame_rgb.shape[0], face_center[1] + crop_height // 2)
                cropped_frame_extended = frame_rgb[crop_y1:crop_y2, crop_x1:crop_x2]
                
                name = self.ui.lineEdit.text()
                id = self.ui.lineEdit_2.text()
                if name and id:
                    # Upload ảnh chỉ có khuôn mặt lên Firebase Storage
                    face_file_path = os.path.join(os.getcwd(), 'face_only.jpg')
                    cv2.imwrite(face_file_path, cv2.cvtColor(cropped_face, cv2.COLOR_RGB2BGR))
                    face_blob = bucket.blob(f'faces_data/{id}_face.jpg')
                    face_blob.upload_from_filename(face_file_path)
                    face_blob.make_public()
                    face_image_url = face_blob.public_url

                    # Upload ảnh mở rộng lên Firebase Storage
                    extended_file_path = os.path.join(os.getcwd(), 'extended_face.jpg')
                    cv2.imwrite(extended_file_path, cv2.cvtColor(cropped_frame_extended, cv2.COLOR_RGB2BGR))
                    extended_blob = bucket.blob(f'faces_data/{id}_extended.jpg')
                    extended_blob.upload_from_filename(extended_file_path)
                    extended_blob.make_public()
                    extended_image_url = extended_blob.public_url

                    # Hiển thị ảnh mở rộng lên QLabel
                    pixmap = QPixmap(extended_file_path)
                    self.ui.label.setPixmap(pixmap)
                    self.ui.label.setScaledContents(True)
                    os.remove(face_file_path)
                    os.remove(extended_file_path)

                    # Lưu thông tin vào Firebase Realtime Database
                    db_ref.push({
                        'name': name,
                        'id': id,
                        'face_image_url': face_image_url,
                        'extended_image_url': extended_image_url
                    })
                    print("Upload to Firebase successful!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = FaceRecognitionApp()
    MainWindow.show()
    sys.exit(app.exec_())