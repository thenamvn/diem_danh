import cv2
import numpy as np

def detect_face_and_track_edges(frame, previous_frame_data=None):
    """
    Phát hiện khuôn mặt và cạnh, lọc đường thẳng, theo dõi chuyển động của các cạnh,
    phân biệt cạnh người/vật, trả về cả 3 frame.

    Args:
        frame: Frame hình ảnh từ camera.
        previous_frame_data: Dictionary chứa thông tin từ frame trước.
    """

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    face_rects = []
    current_face_location = None
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        face_rects.append((x, y, w, h))
        current_face_location = (x, y, w, h)

    # Sobel edge detection
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    gradient_magnitude = cv2.convertScaleAbs(gradient_magnitude)

    # Áp dụng ngưỡng cao hơn
    _, thresholded = cv2.threshold(gradient_magnitude, 70, 255, cv2.THRESH_BINARY)

    # Probabilistic Hough Transform
    minLineLength = 150
    maxLineGap = 20
    lines = cv2.HoughLinesP(thresholded, 1, np.pi / 180, 100, minLineLength, maxLineGap)

    frame_with_lines = frame.copy()
    tracked_lines = []

    face_movement_x = 0
    face_movement_y = 0

    if previous_frame_data and current_face_location:
        previous_face_location = previous_frame_data["face_location"]
        # KIỂM TRA: Đảm bảo previous_face_location không phải là None trước khi truy cập
        if previous_face_location is not None:
            # Tính toán chuyển động của khuôn mặt giữa các frame
            face_movement_x = current_face_location[0] - previous_face_location[0]
            face_movement_y = current_face_location[1] - previous_face_location[1]

    # Ước tính vận tốc trung bình của khuôn mặt.
    if previous_frame_data is not None:
         vx = (face_movement_x - previous_frame_data['face_velocity'][0]) / 2
         vy = (face_movement_y - previous_frame_data['face_velocity'][1]) / 2
    else:
         vx, vy = 0, 0


    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            is_face_line = False

            for x, y, w, h in face_rects:
                # Kiểm tra kỹ hơn: nếu bất kỳ điểm nào trên đường thẳng nằm trong khuôn mặt, bỏ qua.
                for t in np.linspace(0, 1, 20):
                    point_x = int(x1 + t * (x2 - x1))
                    point_y = int(y1 + t * (y2 - y1))
                    if x < point_x < x + w and y < point_y < y + h:
                        is_face_line = True
                        break
                if is_face_line:
                    break

            # Tính khoảng cách từ đường thẳng này đến khuôn mặt.
            distance_to_face = 10000000
            if current_face_location is not None:
                distance_to_face = min(distance_to_face, np.sqrt((x1 - current_face_location[0])**2 + (y1 - current_face_location[1])**2 ))
                distance_to_face = min(distance_to_face, np.sqrt((x2 - current_face_location[0])**2 + (y2 - current_face_location[1])**2 ))

            if not is_face_line:
                cv2.line(frame_with_lines, (x1, y1), (x2, y2), (0, 0, 255), 2)
                tracked_lines.append(((x1, y1), (x2, y2), distance_to_face)) # Lưu lại thông tin đường thẳng

    # So sánh chuyển động của các cạnh với chuyển động của khuôn mặt
    # và phân biệt cạnh người/vật
    moved_with_face = 0
    total_lines = 0
    suspected_lines = 0 # Số lượng đường thẳng đáng ngờ

    if previous_frame_data is not None:
        previous_lines = previous_frame_data["lines"]
        previous_face_location = previous_frame_data["face_location"]

        for (px1, py1), (px2, py2), distance_to_face in previous_lines:
            total_lines += 1
            # Ước tính vị trí mới của đường thẳng dựa trên chuyển động của khuôn mặt
            new_x1 = px1 + face_movement_x
            new_y1 = py1 + face_movement_y
            new_x2 = px2 + face_movement_x
            new_y2 = py2 + face_movement_y

            is_suspect = False

            # Tìm các đường thẳng gần vị trí mới
            for (cx1, cy1), (cx2, cy2), distance_to_face in tracked_lines:
                if abs(cx1 - new_x1) < 20 and abs(cy1 - new_y1) < 20 and abs(cx2 - new_x2) < 20 and abs(cy2-new_y2)<20:
                    moved_with_face += 1
                    # Nếu đường thẳng di chuyển theo khuôn mặt và ở gần khuôn mặt
                    # có thể đây là đường thẳng của một vật
                    is_suspect = True
                    break

            if is_suspect == True and distance_to_face < 200:
                 suspected_lines += 1

        if total_lines > 0:
            # Tính tỷ lệ các đường thẳng di chuyển theo khuôn mặt
            movement_ratio = moved_with_face / total_lines
            suspicious_ratio = suspected_lines / total_lines
            print("Tỷ lệ đường thẳng di chuyển theo khuôn mặt:", movement_ratio)
            print("Tỷ lệ đường thẳng đáng ngờ", suspicious_ratio)

            # Nếu tỷ lệ này vượt quá một ngưỡng nhất định, và cũng gần mặt, có thể là spoofing
            if movement_ratio > 0.3 and suspicious_ratio > 0.1:
                print("Cảnh báo: Có thể là spoofing!")
                cv2.putText(frame_with_lines, "SPOOFING DETECTED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Các thông tin cần lưu giữ để tính toán ở frame tiếp theo.
    frame_data = {
        "face_location": current_face_location,
        "lines": tracked_lines,
        "face_velocity": (vx, vy),
    }

    return frame_with_lines, gradient_magnitude, thresholded, frame_data


def real_time_face_and_edge_detection():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Không thể mở camera")
        return

    previous_frame_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể nhận frame. Thoát...")
            break

        frame_with_lines, sobel_edges, thresholded_edges, frame_data = detect_face_and_track_edges(frame, previous_frame_data)

        cv2.imshow('Original with Faces and Lines', frame_with_lines)
        cv2.imshow('Sobel Edges', sobel_edges)
        cv2.imshow('Thresholded Edges', thresholded_edges)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        previous_frame_data = frame_data # Lưu lại các thông tin của frame này.

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    real_time_face_and_edge_detection()