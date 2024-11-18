import matplotlib.pyplot as plt

# Define the main parts of the program
parts = [
    {
        "name": "Phần Đăng ký Khuôn Mặt",
        "details": [
            "Hiển thị giao diện sử dụng PyQt5 để mở camera.",
            "Tạo các ô input để nhập tên và ID của học sinh.",
            "Cài đặt sự kiện cho nút đăng ký để:",
            "  i. Chụp ảnh khuôn mặt người dùng từ camera sử dụng OpenCV.",
            "  ii. Lưu ảnh khuôn mặt, tên và ID vào cơ sở dữ liệu."
        ]
    },
    {
        "name": "Phần Nhận Diện Khuôn Mặt",
        "details": [
            "Đồng bộ hoá dữ liệu từ cơ sở dữ liệu về máy tính.",
            "Sử dụng camera để lấy hình ảnh khuôn mặt.",
            "Sử dụng thư viện face_recognition để nhận diện khuôn mặt:",
            "  i. So sánh khuôn mặt với các ảnh trong cơ sở dữ liệu.",
            "  ii. Nếu nhận diện thành công, hiển thị thông tin của học sinh và ảnh trên giao diện.",
            "  iii. Thực hiện điểm danh bằng cách ghi thông tin vào Google Sheet.",
            "Nếu không nhận diện được, tiếp tục quét khuôn mặt khác."
        ]
    },
    {
        "name": "Xử lý Điểm Danh vào Google Sheet",
        "details": [
            "Sử dụng thư viện gspread để kết nối với Google Sheet.",
            "Ghi thông tin điểm danh (tên, ID, thời gian) vào Google Sheet."
        ]
    }
]

# Plot the affinity diagram
plt.figure(figsize=(10, 6))
for idx, part in enumerate(parts):
    plt.text(-0.5, idx, part['name'], fontsize=12, ha='right', va='center', fontweight='bold')
    for detail_idx, detail in enumerate(part['details']):
        plt.text(0.5, idx - detail_idx * 0.3, detail, fontsize=10, ha='left', va='center')

plt.title("Affinity Diagram - Chương Trình Điểm Danh Học Sinh bằng Nhận Diện Khuôn Mặt", fontsize=14, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.show()
