import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox
# Import hàm kết nối SQL Server của nhóm bạn
from App.DB_Connection import get_connection


class QuenMatKhau_EX(QtWidgets.QMainWindow):
    def __init__(self, login_controller=None):
        super().__init__()
        self.login_controller = login_controller
        self.initUi()

    def initUi(self):
        self.setObjectName("ForgotWindow")
        self.resize(430, 600)
        self.setStyleSheet("QMainWindow { background-color: #E8F6FD; }")

        self.centralwidget = QtWidgets.QWidget(self)
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(25, 20, 25, 20)

        self.central_panel = QtWidgets.QFrame(self.centralwidget)
        self.central_panel.setStyleSheet("background-color: #FFFFFF; border: 1px solid #BEE3F8; border-radius: 16px;")
        self.panel_layout = QtWidgets.QVBoxLayout(self.central_panel)
        self.panel_layout.setContentsMargins(25, 25, 25, 25)
        self.panel_layout.setSpacing(12)

        self.lbl_logo_icon = QtWidgets.QLabel("🔑", self.central_panel)
        self.lbl_logo_icon.setMinimumSize(QtCore.QSize(70, 70))
        self.lbl_logo_icon.setMaximumSize(QtCore.QSize(70, 70))
        self.lbl_logo_icon.setStyleSheet(
            "background-color: #0288D1; border-radius: 35px; font-size: 30px; color: white; border: none;")
        self.lbl_logo_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        icon_layout = QtWidgets.QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(self.lbl_logo_icon)
        icon_layout.addStretch()
        self.panel_layout.addLayout(icon_layout)

        self.lbl_title = QtWidgets.QLabel("Khôi Phục Mật Khẩu", self.central_panel)
        self.lbl_title.setStyleSheet("color: #0A4D7A; font-weight: bold; font-size: 20px; border: none;")
        self.lbl_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.panel_layout.addWidget(self.lbl_title)

        style_label = "color: #0D6FA6; font-weight: bold; font-size: 13px; border: none; margin-top: 5px;"
        style_input = "QLineEdit { border: 1px solid #CBD5E0; border-radius: 8px; padding: 8px 12px; background-color: #F7FAFC; color: #2D3748; font-size: 14px; } QLineEdit:focus { border: 1px solid #3182CE; background-color: #FFFFFF; }"

        self.lbl_user = QtWidgets.QLabel("Username tài khoản", self.central_panel)
        self.lbl_user.setStyleSheet(style_label)
        self.panel_layout.addWidget(self.lbl_user)

        self.txt_username = QtWidgets.QLineEdit(self.central_panel)
        self.txt_username.setPlaceholderText("Nhập tên tài khoản cần lấy lại...")
        self.txt_username.setStyleSheet(style_input)
        self.panel_layout.addWidget(self.txt_username)

        self.lbl_phone = QtWidgets.QLabel("Số điện thoại đăng ký", self.central_panel)
        self.lbl_phone.setStyleSheet(style_label)
        self.panel_layout.addWidget(self.lbl_phone)

        self.txt_phone = QtWidgets.QLineEdit(self.central_panel)
        self.txt_phone.setPlaceholderText("Nhập số điện thoại đã đăng ký...")
        self.txt_phone.setStyleSheet(style_input)
        self.panel_layout.addWidget(self.txt_phone)

        self.lbl_new_pass = QtWidgets.QLabel("Mật khẩu mới", self.central_panel)
        self.lbl_new_pass.setStyleSheet(style_label)
        self.txt_new_pass = QtWidgets.QLineEdit(self.central_panel)
        self.txt_new_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txt_new_pass.setPlaceholderText("Nhập mật khẩu mới...")
        self.txt_new_pass.setStyleSheet(style_input)

        self.panel_layout.addWidget(self.lbl_new_pass)
        self.panel_layout.addWidget(self.txt_new_pass)

        self.lbl_new_pass.hide()
        self.txt_new_pass.hide()

        self.panel_layout.addSpacing(10)

        self.btn_action = QtWidgets.QPushButton("Xác thực thông tin 🔍", self.central_panel)
        self.btn_action.setMinimumSize(QtCore.QSize(0, 45))
        self.btn_action.setStyleSheet(
            "QPushButton { background-color: #1098F7; color: white; border-radius: 8px; font-weight: bold; font-size: 14px; border: none; } QPushButton:pressed { background-color: #0d84d1; }")
        self.panel_layout.addWidget(self.btn_action)

        self.btn_back = QtWidgets.QPushButton("← Quay lại Đăng nhập", self.central_panel)
        self.btn_back.setStyleSheet(
            "QPushButton { color: #A0AEC0; background: none; border: none; font-size: 13px; } QPushButton:hover { color: #718096; text-decoration: underline; }")
        self.btn_back.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.panel_layout.addWidget(self.btn_back)

        self.main_layout.addWidget(self.central_panel)
        self.setCentralWidget(self.centralwidget)

        self.btn_action.clicked.connect(self.handle_action)
        self.btn_back.clicked.connect(self.back_to_login)

        self.is_verified = False

    def handle_action(self):
        username = self.txt_username.text().strip()
        phone = self.txt_phone.text().strip()

        if not username or not phone:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ Username và Số điện thoại!")
            return

        if not self.is_verified:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM [USER] WHERE user_name = ? AND phone = ?", (username, phone))
                user = cursor.fetchone()
                conn.close()

                if user is not None:
                    QMessageBox.information(self, "Thành công",
                                            "Xác thực thành công! Vui lòng nhập mật khẩu mới bên dưới.")
                    self.txt_username.setEnabled(False)
                    self.txt_phone.setEnabled(False)

                    self.lbl_new_pass.show()
                    self.txt_new_pass.show()

                    self.btn_action.setText("Cập nhật mật khẩu mới 💾")
                    self.btn_action.setStyleSheet(
                        "QPushButton { background-color: #48BB78; color: white; border-radius: 8px; font-weight: bold; font-size: 14px; border: none; } QPushButton:pressed { background-color: #38A169; }")
                    self.is_verified = True
                else:
                    QMessageBox.critical(self, "Thất bại", "Username hoặc Số điện thoại không khớp với hệ thống!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi kết nối", f"Không thể kết nối SQL Server:\n{str(e)}")

        else:
            new_password = self.txt_new_pass.text().strip()
            if not new_password:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập mật khẩu mới!")
                return

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE [USER] SET password = ? WHERE user_name = ?", (new_password, username))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "Thành công", "Mật khẩu của bạn đã được cập nhật thành công!")
                self.back_to_login()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi cập nhật", f"Không thể lưu mật khẩu mới:\n{str(e)}")

    def back_to_login(self):
        if self.login_controller and hasattr(self.login_controller, 'MainWindow'):
            self.login_controller.MainWindow.show()
        self.close()