import cv2
import numpy as np

def detect_spoofing(video_source=0):
    cap = cv2.VideoCapture(video_source)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    lk_params = dict(winSize=(15, 15), maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    
    prev_gray = None
    prev_points = None
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Nếu phát hiện khuôn mặt
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_center = np.array([[x + w // 2, y + h // 2]], dtype=np.float32)
            
            # Optical Flow để theo dõi chuyển động
            if prev_gray is not None and prev_points is not None:
                next_points, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_points, None, **lk_params)
                
                # Tính toán vector chuyển động
                motion_vectors = next_points - prev_points
                avg_motion = np.mean(motion_vectors, axis=0)
                
                # Xác định nếu cả khuôn mặt và khung di chuyển đồng bộ
                if np.linalg.norm(avg_motion) > 2:  # Ngưỡng di chuyển
                    print("Phát hiện điện thoại di chuyển! Kiểm tra xem có gian lận không...")
                    
                prev_points = next_points
            else:
                prev_points = face_center
            
            prev_gray = gray.copy()
            
            # Vẽ khung khuôn mặt
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        cv2.imshow('Face Spoof Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

detect_spoofing()
