import cv2
import numpy as np
import face_recognition

def detect_spoofing(frame):
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
        spoof_characteristics = analyze_edge_patterns(face_roi_edges)
        
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

def analyze_edge_patterns(roi_edges):
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
                angle = calculate_angle(lines[i][0], lines[j][0])
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

def calculate_angle(line1, line2):
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

# Hàm main để sử dụng
def main():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        result = detect_spoofing(frame)
        
        # Vẽ kết quả lên frame
        for face_location in result['face_locations']:
            top, right, bottom, left = face_location
            # Vẽ rectangle xung quanh khuôn mặt
            color = (0, 0, 255) if result['is_spoof'] else (0, 255, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Hiển thị thông tin spoofing
        if result['is_spoof']:
            text = f"SPOOF DETECTED! Score: {result['spoof_score']:.2f}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            for i, evidence in enumerate(result['evidence']):
                cv2.putText(frame, evidence, (10, 60 + i*30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Hiển thị frame và edges
        cv2.imshow('Frame', frame)
        cv2.imshow('Edges', result['edges'])
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()