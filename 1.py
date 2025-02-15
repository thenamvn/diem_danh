import cv2
import numpy as np

def detect_face_and_edges(frame):
    """
    Phát hiện khuôn mặt và cạnh, lọc đường thẳng, trả về cả 3 frame.
    """

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    face_rects = []
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        face_rects.append((x, y, w, h))

    # Sobel edge detection
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    gradient_magnitude = cv2.convertScaleAbs(gradient_magnitude)

    # Áp dụng ngưỡng cao hơn
    _, thresholded = cv2.threshold(gradient_magnitude, 70, 255, cv2.THRESH_BINARY)  # Tăng ngưỡng lên 70

    # Probabilistic Hough Transform
    minLineLength = 150
    maxLineGap = 20
    lines = cv2.HoughLinesP(thresholded, 1, np.pi / 180, 100, minLineLength, maxLineGap)

    frame_with_lines = frame.copy()

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            is_face_line = False

            for x, y, w, h in face_rects:
                # Kiểm tra kỹ hơn: nếu bất kỳ điểm nào trên đường thẳng nằm trong khuôn mặt, bỏ qua.
                for t in np.linspace(0, 1, 20): # Lấy 20 điểm trên đường thẳng
                    point_x = int(x1 + t * (x2 - x1))
                    point_y = int(y1 + y2 * t)
                    if x < point_x < x + w and y < point_y < y + h:
                        is_face_line = True
                        break
                if is_face_line:
                    break

            # Lọc đường thẳng dựa trên góc
            angle = np.arctan2(abs(y2 - y1), abs(x2 - x1)) * 180 / np.pi
            if not is_face_line and (angle < 20 or angle > 70):
                cv2.line(frame_with_lines, (x1, y1), (x2, y2), (0, 0, 255), 2)

    return frame_with_lines, gradient_magnitude, thresholded

def real_time_face_and_edge_detection():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Không thể mở camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể nhận frame. Thoát...")
            break

        frame_with_lines, sobel_edges, thresholded_edges = detect_face_and_edges(frame)

        cv2.imshow('Original with Faces and Lines', frame_with_lines)
        cv2.imshow('Sobel Edges', sobel_edges)
        cv2.imshow('Thresholded Edges', thresholded_edges)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    real_time_face_and_edge_detection()