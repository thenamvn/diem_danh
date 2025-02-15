import cv2
# Import Fasnet class (giả sử bạn đã lưu code trước đó vào file 'fasnet.py')
from Fasnet import Fasnet  # Hoặc thay bằng tên file bạn đã lưu

# Khởi tạo đối tượng Fasnet
fasnet = Fasnet()

# Khởi tạo đối tượng VideoCapture (0 thường là webcam)
cap = cv2.VideoCapture(0)

# Kiểm tra xem camera có mở được không
if not cap.isOpened():
    print("Không thể mở camera")
    exit()

# Load bộ phát hiện khuôn mặt của OpenCV (Haar cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


while True:
    # Đọc frame từ camera
    ret, frame = cap.read()
    if not ret:
        print("Không thể nhận frame (kết thúc stream?). Thoát.")
        break

    # Chuyển frame sang ảnh xám
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Phát hiện khuôn mặt
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Duyệt qua các khuôn mặt phát hiện được
    for (x, y, w, h) in faces:
        # Phát hiện giả mạo
        is_real, score = fasnet.analyze(frame, (x, y, w, h))

        # Vẽ hình chữ nhật quanh khuôn mặt
        if is_real:
            color = (0, 255, 0)  # Xanh lá cây cho khuôn mặt thật
            label = f"Real: {score:.2f}"
        else:
            color = (0, 0, 255)  # Đỏ cho khuôn mặt giả mạo
            label = f"Fake: {score:.2f}"

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)


    # Hiển thị kết quả
    cv2.imshow('Face Anti-Spoofing', frame)

    # Thoát nếu nhấn phím 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()