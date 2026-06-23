from PyQt6.QtWidgets import QMessageBox

# Import chính xác class giao diện từ file thiết kế Dangky.py của bạn
from .Dangky import Ui_RegisterWindow

# Import hàm kết nối SQL Server chuẩn của nhóm bạn
from App.DB_Connection import get_connection


class Dangky_EX(Ui_RegisterWindow):
    def setupUi(self, MainWindow, login_controller=None):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.login_controller = login_controller  # Giữ liên kết với màn hình đăng nhập

        # KẾT NỐI SỰ KIỆN NÚT BẤM (Đã đổi sang btn_dangky theo đúng giao diện của bạn)
        self.btn_dangky.clicked.connect(self.handle_registration)
        self.btn_back_login.clicked.connect(self.back_to_login)  # Chữ Đăng nhập ngay

    def handle_registration(self):
        """Đọc dữ liệu từ giao diện và thực hiện ghi vào SQL Server của nhóm"""
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        phone = self.txt_phone.text().strip()
        role = self.combo_role.currentText()

        # 1. Bắt lỗi bỏ trống thông tin nhập liệu
        if not username or not password or not phone:
            QMessageBox.warning(self.MainWindow, "Lỗi nhập liệu", "Vui lòng điền đầy đủ tất cả các trường thông tin!")
            return

        try:
            # 2. Kết nối tới SQL Server của nhóm
            conn = get_connection()
            cursor = conn.cursor()

            # 3. Kiểm tra xem tên tài khoản này đã có ai đăng ký trước đó chưa
            cursor.execute("SELECT user_id FROM [USER] WHERE user_name = ?", (username,))
            if cursor.fetchone() is not None:
                QMessageBox.warning(self.MainWindow, "Trùng tên đăng nhập",
                                    f"Tài khoản '{username}' đã tồn tại. Vui lòng chọn tên khác!")
                conn.close()
                return

            # 4. TỰ ĐỘNG TÍNH TOÁN USER_ID TIẾP THEO (Do bảng không tự tăng)
            cursor.execute("SELECT MAX(user_id) FROM [USER]")
            max_id = cursor.fetchone()[0]
            next_id = (max_id + 1) if max_id is not None else 1

            # 5. Lưu thông tin tài khoản kèm theo next_id vừa tính được
            cursor.execute(
                "INSERT INTO [USER] (user_id, user_name, password, role, phone) VALUES (?, ?, ?, ?, ?)",
                (next_id, username, password, role, phone)
            )
            conn.commit()
            conn.close()

            # 6. Hiển thị thông báo đăng ký thành công
            QMessageBox.information(
                self.MainWindow,
                "Thành công",
                f"Đăng ký tài khoản '{username}' thành công!\nUser ID cấp phát: {next_id}"
            )

            # Đăng ký xong xuôi, tự động quay trở lại màn hình đăng nhập
            self.back_to_login()

        except Exception as e:
            QMessageBox.critical(
                self.MainWindow,
                "Lỗi kết nối",
                f"Không thể ghi dữ liệu vào SQL Server:\n{str(e)}"
            )

    def back_to_login(self):
        """Ẩn màn hình đăng ký hiện tại và lôi màn hình đăng nhập cũ lên lại"""
        if self.login_controller and hasattr(self.login_controller, 'MainWindow'):
            self.login_controller.MainWindow.show()  # Hiện form Đăng nhập cũ
            self.MainWindow.close()  # Đóng hẳn form Đăng ký này