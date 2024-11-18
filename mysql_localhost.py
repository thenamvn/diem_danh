import sys
import pymysql
from PySide2.QtWidgets import QMenu, QApplication, QMainWindow, QWidget, QVBoxLayout, QAbstractItemView, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog,QShortcut
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence

class MainWindow(QMainWindow):
    def __init__(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS sinhvien_info (name TEXT, ma_sinhvien TEXT, dia_chi TEXT, quoc_tich TEXT)")
        conn.commit()
        conn.close()
        super().__init__()
        self.setWindowTitle("Show Data")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # Tạo bảng dữ liệu
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Sinh viên","Mã sinh viên","Địa chỉ","Quốc tịch"])
        layout.addWidget(self.table)

        # Tạo nút thêm dữ liệu mới
        self.add_button = QPushButton("Thêm")
        self.add_button.clicked.connect(self.add_database)
        layout.addWidget(self.add_button)

        # Tạo nút xoá dữ liệu được chọn
        self.delete_button = QPushButton("Xoá")
        self.delete_button.clicked.connect(self.delete_data)
        layout.addWidget(self.delete_button)

        # Tạo phím tắt Ctrl+F
        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut.activated.connect(self.search_data)

        # Thiết lập chế độ chọn hàng cho bảng
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.show_data()

    def connect(self):
        return pymysql.connect(host='localhost', user='ntnhacker1', password='Nam@2182004', db='quanli_hocphan')
    
    def search(self):
        text, ok = QInputDialog.getText(self, 'Search', 'Enter text:')
        if ok:
            # Thực hiện tìm kiếm với 'text'
            pass
    def show_data(self):
        # Kết nối đến cơ sở dữ liệu MySQL và hiển thị dữ liệu trong bảng
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT * FROM sinhvien_info")
        data = c.fetchall()
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)  # Căn giữa nội dung ô
                self.table.setItem(i, j, item)
        conn.close()
    # Các hàm khác giữ nguyên, chỉ thay đổi cách kết nối đến cơ sở dữ liệu
    def add_database(self):
        # Hiển thị hộp thoại nhập dữ liệu mới và thêm vào cơ sở dữ liệu
        conn = self.connect()
        c = conn.cursor()
        sinhvien_name, ok = QInputDialog.getText(self, "Nhập tên sinh viên:", "Sinh viên")
        if ok and sinhvien_name:
            msv, _ = QInputDialog.getText(self, "Nhập mã sinh viên:", "Mã sinh viên")
            address, _ = QInputDialog.getText(self, "Nhập địa chỉ:", "Địa chỉ")
            country, _ = QInputDialog.getText(self, "Nhập quốc tịch:", "Quốc tịch")
            c.execute("INSERT INTO sinhvien_info VALUES (%s, %s, %s, %s)",
                    (sinhvien_name, msv, address,country))
            conn.commit()
            self.show_data()
        conn.close()


    def delete_data(self,customer_id):
        # Xoá dữ liệu của các hàng được chọn trong bảng
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        if selected_rows:
            reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn xoá dữ liệu được chọn?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                conn = self.connect()
                c = conn.cursor()
                for row in sorted(selected_rows, reverse=True):
                    customer_id = self.table.item(row, 0).text()
                    c.execute("DELETE FROM sinhvien_info WHERE ma_sinhvien=%s", (customer_id,))
                    self.table.removeRow(row)
                conn.commit()
                conn.close()


    def search_data(self):
        # Tìm kiếm dữ liệu dựa trên giá trị nhập vào trong trường tìm kiếm
        keyword, ok = QInputDialog.getText(self, 'Search', 'Enter text:')
        if ok:  # Kiểm tra xem người dùng đã nhập dữ liệu và OK được nhấn hay không
            conn = self.connect()
            c = conn.cursor()
            if keyword:
                c.execute("SELECT * FROM sinhvien_info WHERE name LIKE %s OR ma_sinhvien LIKE %s OR dia_chỉ LIKE %s OR quoc_tich LIKE %s",
                        ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'))
                pass
            data = c.fetchall()
            self.table.setRowCount(len(data))
            for i, row in enumerate(data):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
            conn.close()

    def contextMenuEvent(self, event):
        # Kiểm tra xem có hàng nào được chọn không
        if self.table.selectedItems():
            context_menu = QMenu(self)
            delete_action = context_menu.addAction("Xoá")
            delete_action.triggered.connect(self.delete_selected_rows)

            # Hiển thị context menu
            context_menu.exec_(event.globalPos())

    def delete_selected_rows(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        customer_ids_to_delete = []
        for row in sorted(selected_rows, reverse=True):
            # Lưu customer_id vào danh sách
            customer_id = self.table.item(row, 0).text()  # Giả sử cột 0 chứa ID khách hàng
            customer_ids_to_delete.append((customer_id, row))

        # Xóa từ cơ sở dữ liệu và giao diện
        for customer_id, row in customer_ids_to_delete:
            self.delete_data(customer_id)
            self.table.removeRow(row)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 400)  # Đặt kích thước cửa sổ
    window.show()
    sys.exit(app.exec_())
