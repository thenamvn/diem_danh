import cv2
from ultralytics import YOLO

cap = cv2.VideoCapture(0)  # 0 là camera mặc định

# Kiểm tra camera có mở thành công hay không
if not cap.isOpened():
    print("Lỗi: Không thể mở camera!")
    exit()

# load yolov8 model
model = YOLO('best.pt')
ret = True
while ret:
    ret, frame = cap.read()

    if ret:
        results = model(frame)
        boxes = results[0].boxes
        for box in boxes:
            top_left_x= int(box.xyxy.tolist()[0][0]) 
            top_left_y= int(box.xyxy.tolist()[0][1]) 
            bottom_right_x= int(box.xyxy.tolist() [0] [2])
            bottom_right_y= int(box.xyxy.tolist() [0] [3])
            cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (50,200,129), 2)

        # visualize
        cv2.imshow('frame', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()