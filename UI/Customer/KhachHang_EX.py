from UI.Customer.KhachHang import Ui_DashboardWindow
from App.wallet import get_wallet


class KhachHang_EX(Ui_DashboardWindow):
    def setupUi(self, MainWindow, user_id):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.user_id = user_id

        self.load_wallet_info()

        # Gán hành động click trực tiếp cho card_buy
        self.card_buy.mousePressEvent = lambda event: self.open_buy_ticket()

    def open_buy_ticket(self):
        from UI.Customer.Thanhtoan_EX import ThanhToan_EX   # đổi tên đúng theo file EX màn thanh toán của mày
        from PyQt6.QtWidgets import QMainWindow

        self.buy_window = QMainWindow()
        ui = ThanhToan_EX()
        ui.setupUi(self.buy_window, self.user_id)
        self.buy_window.show()
        self.MainWindow.close()

    def load_wallet_info(self):
        wallet = get_wallet(self.user_id)
        if wallet:
            self.lbl_balance.setText(f"{wallet['balance']:,.0f} VNĐ")
        else:
            self.lbl_balance.setText("Không tìm thấy ví")