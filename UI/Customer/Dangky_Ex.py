from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QDate
from .Dangky import Ui_RegisterWindow
from App.DB_Connection import get_connection


class Dangky_EX(Ui_RegisterWindow):
    def setupUi(self, MainWindow, login_controller=None):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.login_controller = login_controller

        self.btn_dangky.clicked.connect(self.handle_registration)
        self.btn_back_login.clicked.connect(self.back_to_login)

    def handle_registration(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        phone = self.txt_phone.text().strip()
        role = "customer"

        try:
            if hasattr(self, 'DoB') and hasattr(self.DoB, 'date'):
                dob = self.DoB.date().toString("yyyy-MM-dd")
            elif hasattr(self, 'DoB') and hasattr(self.DoB, 'text'):
                dob = self.DoB.text().strip()
            else:
                dob = "2000-01-01"
        except Exception:
            dob = "2000-01-01"

        if not username or not password or not phone or not dob:
            QMessageBox.warning(self.MainWindow, "Lỗi nhập liệu", "Vui lòng điền đầy đủ thông tin!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT user_id FROM [USER] WHERE user_name = ?", (username,))
            if cursor.fetchone() is not None:
                QMessageBox.warning(self.MainWindow, "Trùng tên", f"Tài khoản '{username}' đã tồn tại!")
                conn.close()
                return

            cursor.execute("SELECT MAX(user_id) FROM [USER]")
            max_id = cursor.fetchone()[0]
            next_id = (max_id + 1) if max_id is not None else 1

            cursor.execute(
                "INSERT INTO [USER] (user_id, user_name, password, role, phone, DoB) VALUES (?, ?, ?, ?, ?, ?)",
                (next_id, username, password, role, phone, dob)
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self.MainWindow, "Thành công", f"Đăng ký tài khoản thành công! ID cấp phát: {next_id}")
            self.back_to_login()

        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Lỗi kết nối", f"Không thể ghi dữ liệu vào database:\n{str(e)}")

    def back_to_login(self):
        if self.login_controller and hasattr(self.login_controller, 'MainWindow'):
            self.login_controller.MainWindow.show()
            self.MainWindow.close()
        else:
            try:
                from UI.Customer.Dangnhap_EX import Dangnhap_EX
                from PyQt6.QtWidgets import QMainWindow

                self.main_window = QMainWindow()
                self.login_ui = Dangnhap_EX()
                self.login_ui.setupUi(self.main_window)
                self.main_window.show()

                self.MainWindow.close()
            except Exception as e:
                self.MainWindow.close()