from PyQt6.QtWidgets import QMessageBox

from UI.Customer.Dangnhap import Ui_LoginWindow
from App.auth import login


class Dangnhap_EX(Ui_LoginWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        self.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        user_name = self.inp_username.text()
        password = self.inp_password.text()

        result = login(user_name, password)

        if result:
            QMessageBox.information(self.MainWindow, "Thành công", f"Chào {result['user_name']}!")
            self.open_wallet(result['user_id'])

    def open_wallet(self, user_id):
        from UI.Customer.KhachHang_EX import KhachHang_EX
        from PyQt6.QtWidgets import QMainWindow

        self.wallet_window = QMainWindow()
        ui = KhachHang_EX()
        ui.setupUi(self.wallet_window, user_id)
        self.wallet_window.show()
        self.MainWindow.close()