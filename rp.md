## **Hệ Thống Điểm Danh Dựa Trên Nhận Diện Khuôn Mặt**

### Trang Tiêu Đề

**Tên Đề Tài:** Hệ Thống Điểm Danh Dựa Trên Nhận Diện Khuôn Mặt

**Tác Giả:** [Tên của bạn và các thành viên nhóm nếu có]

**Môn Học:** [Tên môn học, ví dụ: Thị Giác Máy Tính]

**Giảng Viên:** [Tên giảng viên]

**Trường Đại Học:** [Tên trường đại học]

**Ngày:** [Ngày hiện tại]

---
### **Tóm Tắt**

Báo cáo này trình bày chi tiết về quá trình phát triển hệ thống điểm danh dựa trên nhận diện khuôn mặt, được thiết kế để tối ưu hóa việc ghi nhận điểm danh thông qua nhận dạng khuôn mặt tự động. Hệ thống bao gồm hai giao diện chính: một giao diện đăng ký, cho phép thu thập và lưu trữ dữ liệu khuôn mặt cùng với tên và ID; và một giao diện đăng nhập, sử dụng nhận diện khuôn mặt để xác định các cá nhân đã đăng ký và ghi lại thời gian điểm danh của họ. Các thành phần quan trọng của hệ thống này bao gồm việc sử dụng Firebase để lưu trữ dữ liệu an toàn và Google Sheets để quản lý hồ sơ điểm danh. Báo cáo này sẽ phác thảo thiết kế và triển khai của dự án, làm nổi bật các tính năng chính, chi tiết kỹ thuật, hướng dẫn cài đặt, và hướng dẫn sử dụng, cùng với một thảo luận về các ứng dụng của nó.

---
### **1. Giới Thiệu**

Theo dõi điểm danh là một phần cơ bản trong nhiều hoạt động tổ chức, từ các cơ sở giáo dục đến môi trường doanh nghiệp. Các phương pháp ghi nhận điểm danh truyền thống, như bảng ký tên thủ công, thường không hiệu quả, tốn thời gian và dễ xảy ra lỗi. Dự án này giải quyết những thách thức này bằng cách phát triển một hệ thống điểm danh dựa trên nhận diện khuôn mặt. Động lực chính đằng sau dự án này là tận dụng sức mạnh của thị giác máy tính để tự động hóa quá trình điểm danh, làm cho nó chính xác hơn, hiệu quả hơn và thuận tiện hơn.

Hệ thống này được thiết kế để tự động hóa quá trình ghi nhận điểm danh bằng công nghệ nhận diện khuôn mặt. Nó thay thế các phương pháp thủ công truyền thống, giảm thời gian và tối thiểu hóa khả năng xảy ra lỗi và gian lận. Hệ thống này không chỉ là một dự án kỹ thuật mà còn là một giải pháp có khả năng nâng cao hiệu quả và độ chính xác trong các ứng dụng theo dõi điểm danh khác nhau.

Hệ thống nhằm đạt được các mục tiêu sau:

*   **Điểm danh tự động:** Tự động ghi lại điểm danh dựa trên nhận diện khuôn mặt, loại bỏ sự cần thiết của việc can thiệp thủ công.
*   **Giao diện thân thiện với người dùng:** Cung cấp các giao diện trực quan cho cả việc đăng ký khuôn mặt và ghi lại điểm danh.
*   **Bảo mật dữ liệu:** Lưu trữ dữ liệu khuôn mặt an toàn trong Firebase để ngăn chặn truy cập trái phép.
*   **Quản lý dữ liệu:** Quản lý hồ sơ điểm danh bằng Google Sheets để dễ dàng truy cập và phân tích.
*   **Khả năng mở rộng:** Thiết kế một hệ thống có thể mở rộng để đáp ứng một số lượng người dùng ngày càng tăng.

Việc phát triển hệ thống này kết hợp các kỹ thuật thị giác máy tính hiện đại, các chiến lược quản lý cơ sở dữ liệu và các dịch vụ đám mây để hình thành một giải pháp toàn diện để quản lý điểm danh một cách hiệu quả. Báo cáo này sẽ đi sâu vào chi tiết của các thành phần này, phác thảo thiết kế, triển khai và chức năng của hệ thống "Điểm Danh Khuôn Mặt".

---
### **2. Tổng Quan Tài Liệu/Nền Tảng**

Việc phát triển hệ thống điểm danh dựa trên nhận diện khuôn mặt này dựa trên các nghiên cứu và thực tiễn hiện có trong thị giác máy tính, sinh trắc học và quản lý dữ liệu dựa trên đám mây. Phần này sẽ đánh giá các khái niệm và công nghệ thiết yếu được sử dụng trong dự án, đặc biệt tập trung vào các kỹ thuật nhận diện khuôn mặt, hệ thống quản lý cơ sở dữ liệu và các giải pháp lưu trữ đám mây.

#### 2.1. Các Kỹ Thuật Nhận Diện Khuôn Mặt

Nhận diện khuôn mặt, một yếu tố quan trọng của hệ thống này, là một lĩnh vực phức tạp với lịch sử nghiên cứu lâu dài. Các phương pháp tiếp cận ban đầu dựa trên các thuật toán như Eigenfaces và Fisherfaces, là nền tảng nhưng có những hạn chế trong việc xử lý các biến thể về tư thế, ánh sáng và biểu cảm. Gần đây, các phương pháp học sâu đã cách mạng hóa lĩnh vực này. Mạng nơ-ron tích chập (CNN) đã đạt được độ chính xác cao nhất trong nhiều tiêu chuẩn nhận diện khuôn mặt. Dự án này tận dụng thư viện Python `face_recognition`, sử dụng mô hình CNN đã được huấn luyện trước cho việc phát hiện và mã hóa khuôn mặt. Mô hình này tạo ra một vector 128 chiều (mã hóa khuôn mặt) đại diện duy nhất cho một cấu trúc khuôn mặt, cho phép so sánh và nhận dạng đáng tin cậy. Việc sử dụng học sâu không chỉ nâng cao độ chính xác của nhận diện khuôn mặt mà còn giải quyết nhiều thách thức vốn có trong các phương pháp truyền thống như nhiễu và che khuất một phần. **Thư viện `face_recognition` về bản chất sử dụng thư viện `dlib` để thực hiện các tác vụ này.**

#### 2.2. Quản Lý Cơ Sở Dữ Liệu

Việc quản lý hiệu quả dữ liệu khuôn mặt và hồ sơ điểm danh là rất cần thiết cho chức năng của hệ thống điểm danh. Các hệ thống cơ sở dữ liệu quan hệ truyền thống thường được sử dụng để quản lý dữ liệu. Trong dự án này, chúng tôi sử dụng Firebase, một cơ sở dữ liệu NoSQL được lưu trữ trên đám mây. Firebase cung cấp một cơ sở dữ liệu linh hoạt, có khả năng mở rộng và thời gian thực, tối ưu cho các ứng dụng yêu cầu đồng bộ hóa dữ liệu liên tục và khả năng truy cập. Điều này cũng cho phép dễ dàng triển khai và truy cập dữ liệu từ nhiều thiết bị, điều mà các giải pháp truyền thống tại chỗ khó có thể cung cấp.

#### 2.3. Lưu Trữ Đám Mây và Tích Hợp Google Sheets

Để cung cấp một giải pháp quản lý điểm danh hoàn chỉnh, hệ thống tích hợp với các dịch vụ lưu trữ đám mây, đặc biệt là Google Sheets. Sự lựa chọn này mang tính chiến lược vì Google Sheets thân thiện với người dùng, có thể truy cập trên các thiết bị khác nhau và cung cấp một nền tảng để phân tích dữ liệu, trực quan hóa và báo cáo. Sự tích hợp này cho phép dễ dàng lưu trữ và thao tác dữ liệu điểm danh, cũng như tạo điều kiện xem thời gian thực. Ngoài ra, việc sử dụng bộ nhớ Firebase để lưu trữ hình ảnh khuôn mặt càng làm tăng khả năng mở rộng và khả năng truy cập của hệ thống.

### **3. Phương Pháp Luận**

Phương pháp luận của hệ thống bao gồm hai giai đoạn chính: giai đoạn đăng ký và giai đoạn đăng nhập/điểm danh. Phần này mô tả chi tiết các quy trình, công cụ và thư viện được sử dụng trong từng giai đoạn.

#### 3.1. Giai Đoạn Đăng Ký

1.  **Thu Thập Ảnh:** Trong bước này, khuôn mặt của người dùng được chụp bằng webcam. Hệ thống hiển thị luồng trực tiếp từ webcam để đảm bảo người dùng được định vị phù hợp để chụp ảnh.
2.  **Phát Hiện Khuôn Mặt:** Sau khi chụp ảnh, hệ thống sử dụng thư viện `face_recognition` để phát hiện vị trí của khuôn mặt trong ảnh.
3.  **Mã Hóa Khuôn Mặt:** Sau khi phát hiện khuôn mặt, vùng khuôn mặt đã phát hiện được xử lý để tạo ra mã hóa khuôn mặt 128 chiều, một vector duy nhất đại diện cho cấu trúc khuôn mặt.
4.  **Lưu Trữ Dữ Liệu:** Mã hóa khuôn mặt, cùng với siêu dữ liệu do người dùng cung cấp (tên và ID), được lưu trữ trong Firebase. Hình ảnh thực tế của khuôn mặt được tải lên Firebase Storage để truy xuất và hiển thị sau này, cho phép ứng dụng có một biểu diễn trực quan thân thiện với người dùng.

#### 3.2. Giai Đoạn Đăng Nhập/Điểm Danh

1.  **Thu Thập Ảnh:** Tương tự như giai đoạn đăng ký, khuôn mặt của người dùng được chụp bằng webcam trong quá trình đăng nhập.
2.  **Phát Hiện và Mã Hóa Khuôn Mặt:** Hệ thống xử lý ảnh đã chụp để phát hiện khuôn mặt và tạo ra mã hóa khuôn mặt tương ứng.
3.  **So Khớp Khuôn Mặt:** Mã hóa khuôn mặt đã tạo được so sánh với các mã hóa được lưu trữ trong Firebase bằng khoảng cách Euclidean. Hệ thống xác định người dùng có khoảng cách nhỏ nhất, cho thấy sự phù hợp nhất.
4.  **Ghi Lại Điểm Danh:** Sau khi xác định thành công, hệ thống ghi lại tên, ID và dấu thời gian hiện tại, và ghi dữ liệu này vào Google Sheets. Nhật ký này cung cấp một hồ sơ điểm danh theo thời gian thực và dễ dàng truy cập.

#### 3.3. Các Công Cụ và Thư Viện

Dự án sử dụng các công cụ và thư viện sau:

*   **Python:** Ngôn ngữ lập trình cốt lõi để phát triển tất cả các thành phần.
*   **`face_recognition`:** Cung cấp các tính năng nhận diện khuôn mặt.
*   **`dlib`:** Được sử dụng cho việc phát hiện khuôn mặt và trích xuất đặc trưng.
*   **`numpy`:** Tạo điều kiện cho các hoạt động số trên dữ liệu khuôn mặt.
*   **`opencv-python`:** Xử lý các tác vụ xử lý hình ảnh và video.
*   **`PySide6`:** Để xây dựng giao diện người dùng (GUI) của hệ thống.
*   **`firebase-admin`:** Xử lý tích hợp với Firebase.
*   **`google-auth-oauthlib`, `google-api-python-client` và `gspread`:** Tạo điều kiện tích hợp với Google Sheets.

---
### **4. Triển Khai**

Phần này trình bày chi tiết về việc triển khai hệ thống điểm danh dựa trên nhận diện khuôn mặt. Việc triển khai bao gồm việc phát triển hai tập lệnh Python chính: `reg_new.py` (để đăng ký) và `login_new.py` (để ghi lại điểm danh).

#### 4.1. Giao Diện Đăng Ký (`reg_new.py`)

Tập lệnh `reg_new.py` xử lý việc đăng ký người dùng mới. Nó sử dụng thư viện `PySide6` để tạo giao diện người dùng đồ họa (GUI). GUI cho phép người dùng chụp khuôn mặt của họ bằng webcam và nhập tên và ID của họ. Sau khi người dùng nhấp vào nút chụp, hệ thống tiến hành các tác vụ sau:

*   **Luồng Video:** Video trực tiếp từ webcam được hiển thị bằng widget `QLabel`.
*   **Phát Hiện Khuôn Mặt:** Thư viện `face_recognition` phát hiện khuôn mặt trong ảnh đã chụp và trích xuất vector mã hóa khuôn mặt.
*   **Nhập Dữ Liệu:** Các trường văn bản được cung cấp để người dùng nhập tên và ID của họ.
*   **Tải Dữ Liệu Lên:** Khi nhấp vào nút "Đăng ký", mã hóa khuôn mặt, tên và ID được tải lên cơ sở dữ liệu Firebase. Hình ảnh đã chụp cũng được tải lên Firebase Storage. Việc lưu trữ dữ liệu này bao gồm xử lý lỗi và xác thực dữ liệu.
*   **Phản Hồi Thời Gian Thực:** GUI phản hồi và cung cấp phản hồi thời gian thực cho người dùng, chẳng hạn như thông báo thành công hoặc thông báo lỗi. Nó cũng hiển thị khuôn mặt đã chụp của người dùng trong nhãn được chỉ định.
*   **Đa Luồng:** Để ngăn chặn giao diện người dùng bị đóng băng, các tác vụ như tải lên Firebase và xử lý khuôn mặt được thực hiện trong các luồng riêng biệt.

#### 4.2. Giao Diện Đăng Nhập (`login_new.py`)

Tập lệnh `login_new.py` xử lý chức năng ghi lại điểm danh. Nó cũng sử dụng `PySide6` cho GUI, bao gồm:

*   **Video Trực Tiếp:** Nó sử dụng phương pháp tương tự như giao diện đăng ký, sử dụng widget `QLabel` để hiển thị luồng trực tiếp từ webcam.
*   **Phát Hiện & Nhận Diện Khuôn Mặt:** Tương tự như giai đoạn đăng ký, nó phát hiện và mã hóa khuôn mặt trong luồng webcam trực tiếp. Sau đó, nó so sánh mã hóa đã tạo với tất cả các mã hóa được lưu trữ từ Firebase.
*   **Xác Định Người Dùng:** Khi tìm thấy sự phù hợp, tập lệnh truy xuất tên và ID của người đã được xác định từ Firebase. GUI sau đó hiển thị thông tin này.
*   **Ghi Lại Điểm Danh:** Khi nhận dạng thành công, hệ thống ghi lại dữ liệu điểm danh, bao gồm tên, ID và dấu thời gian hiện tại, vào Google Sheets bằng thư viện `gspread`.
*   **Đa Luồng:** Để duy trì GUI trôi chảy, việc xử lý video, nhận diện khuôn mặt và ghi lại điểm danh được xử lý trong các luồng riêng biệt.
*   **Phản Hồi Thời Gian Thực:** Một thanh trạng thái được cung cấp để hiển thị tin nhắn, cả tin nhắn thành công và lỗi.

#### 4.3. Tích Hợp Firebase và Google Sheets

*   **Firebase:** Firebase được khởi tạo bằng thông tin xác thực, cho phép hệ thống truy cập cơ sở dữ liệu và bộ nhớ. Hệ thống tương tác với Firebase bằng cách:
    *   **Đọc dữ liệu khuôn mặt:** Mã hóa khuôn mặt được tìm nạp từ Firebase để mục đích so sánh.
    *   **Tải dữ liệu người dùng mới lên:** Mã hóa khuôn mặt, tên, ID và hình ảnh khuôn mặt được lưu trữ vào Firebase trong giai đoạn đăng ký.
    *   **Phát hiện thay đổi dữ liệu thời gian thực:** Hệ thống lắng nghe các thay đổi thời gian thực trong Firebase, điều này đảm bảo rằng nếu bất kỳ người dùng mới nào được đăng ký, họ cũng được hệ thống nhận ra trong các phiên tiếp theo.
*   **Google Sheets:** Google Sheet API được sử dụng để tương tác với Google Sheet để lưu trữ hồ sơ điểm danh:
    *   **Xác Thực:** API được xác thực bằng OAuth2, cho phép hệ thống truy cập và sửa đổi dữ liệu trong Google Sheet đã chỉ định.
    *   **Ghi Lại Điểm Danh:** Trong giai đoạn đăng nhập, hệ thống thêm tên, ID và dấu thời gian của người dùng làm một hàng mới vào Google Sheet sau mỗi lần xác định thành công.

---
### **5. Giải Thích Chi Tiết Hoạt Động của Các Hàm và Thư Viện Chính**

#### 5.1. Bản Chất của Thư Viện `face_recognition` và `dlib`

*   Thư viện `face_recognition` là một thư viện Python cấp cao, cung cấp một giao diện đơn giản để thực hiện các tác vụ nhận diện khuôn mặt. **Về bản chất, `face_recognition` sử dụng thư viện `dlib` để thực hiện các chức năng nhận diện khuôn mặt phức tạp ở cấp độ thấp hơn.**
*   `dlib` là một thư viện C++ mạnh mẽ, cung cấp các công cụ để xử lý hình ảnh, học máy và các tác vụ liên quan đến thị giác máy tính. Trong `face_recognition`, `dlib` được sử dụng để phát hiện khuôn mặt, xác định các điểm mốc trên khuôn mặt (landmarks) và tính toán các đặc trưng khuôn mặt.

#### 5.2. Bản Chất của Hàm `face_recognition.face_distance`

*   **Mục Đích:** Hàm `face_distance` tính toán khoảng cách Euclidean giữa một vector đặc trưng khuôn mặt mới (face_to_compare) và danh sách các vector đặc trưng đã biết (face_encodings).
*   **Chi Tiết Hoạt Động:**
    1.  **Input:**
        *   `face_encodings`: Danh sách các vector đặc trưng của các khuôn mặt đã biết, là một mảng numpy có kích thước (n, 128) (với n là số khuôn mặt đã biết).
        *   `face_to_compare`: Một vector đặc trưng có kích thước (128,), đại diện cho khuôn mặt cần so sánh.
    2.  **Output:**
        *   Một mảng numpy chứa các khoảng cách Euclidean giữa `face_to_compare` và từng vector trong `face_encodings`. Kích thước mảng trả về là (n,).
    3.  **Toán Học:** Công thức tính khoảng cách Euclidean giữa hai vector `p` và `q` là:
        ```
        distance = sqrt(sum((p_i - q_i)^2))
        ```
*   **Kết Luận:** Hàm này trả về các khoảng cách Euclidean, mà giá trị càng nhỏ thì khuôn mặt càng giống nhau. Giá trị ngưỡng (ví dụ: 0.6) thường được sử dụng để xác định mức độ giống nhau.

#### 5.3. Bản Chất của Hàm `face_recognition.face_encodings`

*   **Mục Đích:** Hàm `face_encodings` tạo ra vector đặc trưng 128 chiều cho một khuôn mặt từ ảnh.
*   **Đầu vào:**
    *   `face_image`: Ảnh đầu vào (`frame_rgb`) có khuôn mặt cần mã hóa.
    *   `known_face_locations`: Vị trí khuôn mặt trong ảnh, ví dụ: `[top, right, bottom, left]`. Trong trường hợp này, là `[face_locations[best_match_index]]`.
*   **Chi Tiết Hoạt Động:**
    1.  Hàm `face_encodings` gọi hàm `_raw_face_landmarks()` để nhận diện các điểm landmarks (5 hoặc 68 điểm) của khuôn mặt từ ảnh. (68 điểm là mặc định).
    2.  Tại đây, nó sẽ tìm vị trí khuôn mặt bằng cách sử dụng các model đã được training sẵn là **HOG** và CNN (HOG là mặc định).
        *   **HOG (Histogram of Oriented Gradients)** là một kỹ thuật được sử dụng trong lĩnh vực thị giác máy tính để trích xuất các đặc trưng từ hình ảnh. Nó đặc biệt phổ biến trong nhận dạng đối tượng, bao gồm cả nhận diện khuôn mặt.
    3.  Khi đã có vị trí các khuôn mặt, nó sẽ sử dụng các model để nhận diện các điểm landmark trên khuôn mặt (68 điểm mặc định).
    4.  Khi đã có vị trí các điểm trên khuôn mặt, tính toán đặc trưng khuôn mặt để đưa ra vector 128 chiều cho khuôn mặt đó.
    5.  Mô hình ResNet được `dlib` sử dụng để tính toán vector đặc trưng từ hình ảnh khuôn mặt và landmarks, sử dụng đường dẫn sau:

        ```python
        def face_recognition_model_location():
            return resource_filename(__name__, "models/dlib_face_recognition_resnet_model_v1.dat")
        ```
*   **Kết quả:** Một vector 128 chiều đại diện cho khuôn mặt.

---
### **6. Kết Quả**

Hệ thống đã chứng minh thành công khả năng thực hiện nhận diện khuôn mặt và ghi lại điểm danh với độ chính xác cao. Quá trình đăng ký diễn ra liền mạch và hệ thống có thể nhận ra người dùng đã đăng ký trong các điều kiện ánh sáng và góc độ khác nhau. Phản hồi thời gian thực được cung cấp bởi cả hai giao diện cho phép trải nghiệm người dùng mượt mà.

*   **Độ Chính Xác:** Thuật toán nhận diện khuôn mặt đạt được tỷ lệ chính xác cao trong các điều kiện thử nghiệm lý tưởng, với số lượng dương tính giả tối thiểu.
*   **Tính Mạnh Mẽ:** Hệ thống thể hiện mức độ mạnh mẽ cao đối với các thách thức thông thường như thay đổi nhỏ về hướng khuôn mặt, tư thế và ánh sáng.
*   **Khả Năng Mở Rộng:** Việc hệ thống sử dụng bộ nhớ đám mây khiến nó phù hợp với các ứng dụng quy mô lớn.
*   **Hiệu Suất:** Việc triển khai đa luồng đảm bảo hiệu suất tốt về khả năng phản hồi của giao diện người dùng và độ trễ trong cả việc xử lý khuôn mặt và lưu dữ liệu.
*   **Tích Hợp:** Cả hai tích hợp Firebase và Google Sheets đều hoạt động hoàn hảo.

---
### **7. Thảo Luận**

Dự án này đã chứng minh thành công việc sử dụng thực tế các công nghệ thị giác máy tính để tự động hóa và đơn giản hóa quy trình quản lý điểm danh. Độ chính xác của thuật toán nhận diện khuôn mặt, tính mạnh mẽ của hệ thống, giao diện thân thiện với người dùng và tích hợp liền mạch với các dịch vụ dựa trên đám mây làm cho dự án này trở thành một giải pháp khả thi cho các ứng dụng theo dõi điểm danh khác nhau.

*   **Hiệu Quả:** Hệ thống đã chứng minh khả năng theo dõi điểm danh nhanh hơn, tự động và hiệu quả hơn so với các hệ thống truyền thống.
*   **Bảo Mật Dữ Liệu:** Các tính năng bảo mật của Firebase bảo vệ dữ liệu người dùng và quyền truy cập vào cơ sở dữ liệu được kiểm soát.
*   **Khả Năng Mở Rộng:** Việc sử dụng các dịch vụ dựa trên đám mây có nghĩa là hệ thống này có thể dễ dàng mở rộng để đáp ứng nhiều người dùng hơn.
*   **Trải Nghiệm Người Dùng:** Cả giao diện đăng ký và đăng nhập đều đơn giản và dễ sử dụng, điều này tạo điều kiện thuận lợi cho việc áp dụng và hài lòng của người dùng.

---
### **8. Kết Luận**

Hệ thống điểm danh dựa trên nhận diện khuôn mặt đã chứng minh thành công việc tích hợp hiệu quả công nghệ nhận diện khuôn mặt, quản lý dữ liệu dựa trên đám mây và các nguyên tắc thiết kế giao diện người dùng. Hệ thống tự động hóa thành công quá trình điểm danh, loại bỏ đầu vào thủ công, đồng thời duy trì giao diện hiệu quả và thân thiện với người dùng. Các kết quả, thảo luận và đánh giá cho thấy tính thực tế và khả thi của dự án.

Công việc trong tương lai có thể tập trung vào việc nâng cao hơn nữa tính mạnh mẽ của hệ thống, đặc biệt là trong các điều kiện ánh sáng khó khăn và với các đặc điểm khuôn mặt đa dạng, cũng như kết hợp các hệ thống theo dõi điểm danh khác. Ngoài ra, việc thêm xử lý lỗi mạnh mẽ hơn và kết hợp luồng trực tiếp của hồ sơ điểm danh có thể cung cấp trải nghiệm người dùng tốt hơn. Nhìn chung, dự án này đã thành công trong việc đáp ứng các mục tiêu của mình và cung cấp một giải pháp có khả năng mở rộng và khả thi để theo dõi điểm danh tự động.

---

Đây là phiên bản đầy đủ của báo cáo, bao gồm cả phần giải thích chi tiết về cách hoạt động của các hàm và thư viện chính. Bạn có muốn chỉnh sửa hay thêm gì nữa không?
