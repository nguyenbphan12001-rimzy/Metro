from PyQt6.QtWidgets import QMessageBox
from UI.Customer.Naptien import Ui_NapTienWindow
from App.DB_Connection import get_connection


class NapTien_EX(Ui_NapTienWindow):

    def setupUi(self, MainWindow, user_id, parent_dashboard=None):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.user_id = user_id
        self.parent_dashboard = parent_dashboard

        self.load_balance()
        self.load_payment_methods()

        self.btn_quick_50000.clicked.connect(lambda: self.txt_amount.setText("50000"))
        self.btn_quick_100000.clicked.connect(lambda: self.txt_amount.setText("100000"))
        self.btn_quick_200000.clicked.connect(lambda: self.txt_amount.setText("200000"))
        self.btn_quick_500000.clicked.connect(lambda: self.txt_amount.setText("500000"))

        self.btn_naptien.clicked.connect(self.handle_topup)
        self.btn_back.clicked.connect(self.go_back)

    def load_balance(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM [WALLET] WHERE user_id = ?", (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.lbl_balance_value.setText(f"{row[0]:,.0f} VNĐ")
            else:
                self.lbl_balance_value.setText("Không tìm thấy ví")
        except Exception as e:
            self.lbl_balance_value.setText("Lỗi kết nối")
            print(f"load_balance error: {e}")

    def load_payment_methods(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT method_id, method_name FROM [PAYMENT_METHODS]")
            methods = cursor.fetchall()
            conn.close()

            self.combo_method.clear()
            for method_id, method_name in methods:
                self.combo_method.addItem(method_name, userData=method_id)

            if self.combo_method.count() == 0:
                for name, mid in [("Tiền mặt", 1), ("MoMo", 2), ("Thẻ ngân hàng", 3)]:
                    self.combo_method.addItem(name, userData=mid)
        except Exception as e:
            print(f"load_payment_methods error: {e}")
            for name, mid in [("Tiền mặt", 1), ("MoMo", 2), ("Thẻ ngân hàng", 3)]:
                self.combo_method.addItem(name, userData=mid)

    def handle_topup(self):
        amount_str = self.txt_amount.text().strip().replace(",", "").replace(".", "")
        method_id = self.combo_method.currentData()

        if not amount_str:
            QMessageBox.warning(self.MainWindow, "Thiếu thông tin", "Vui lòng nhập số tiền cần nạp!")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            QMessageBox.warning(self.MainWindow, "Sai định dạng", "Số tiền không hợp lệ. Chỉ nhập số!")
            return

        if amount <= 0:
            QMessageBox.warning(self.MainWindow, "Số tiền không hợp lệ", "Số tiền nạp phải lớn hơn 0!")
            return

        if amount < 10_000:
            QMessageBox.warning(self.MainWindow, "Số tiền quá nhỏ", "Số tiền nạp tối thiểu là 10,000 VNĐ!")
            return

        if amount > 50_000_000:
            QMessageBox.warning(self.MainWindow, "Số tiền quá lớn", "Số tiền nạp tối đa là 50,000,000 VNĐ/lần!")
            return

        if method_id is None:
            QMessageBox.warning(self.MainWindow, "Thiếu thông tin", "Vui lòng chọn phương thức thanh toán!")
            return

        confirm = QMessageBox.question(
            self.MainWindow,
            "Xác nhận nạp tiền",
            f"Bạn xác nhận nạp {amount:,.0f} VNĐ\nPhương thức: {self.combo_method.currentText()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT wallet_id FROM [WALLET] WHERE user_id = ?", (self.user_id,))
            wallet_row = cursor.fetchone()
            if wallet_row is None:
                QMessageBox.critical(self.MainWindow, "Lỗi hệ thống", "Không tìm thấy ví của tài khoản này!")
                conn.close()
                return
            wallet_id = wallet_row[0]

            cursor.execute("SELECT MAX(deposit_id) FROM [DEPOSIT_HISTORY]")
            max_id = cursor.fetchone()[0]
            next_deposit_id = (max_id + 1) if max_id is not None else 1

            cursor.execute(
                """INSERT INTO [DEPOSIT_HISTORY]
                   (deposit_id, wallet_id, user_id, method_id, amount, created_at)
                   VALUES (?, ?, ?, ?, ?, GETDATE())""",
                (next_deposit_id, wallet_id, self.user_id, method_id, amount)
            )

            cursor.execute(
                """UPDATE [WALLET]
                   SET balance = balance + ?, last_updated = GETDATE()
                   WHERE wallet_id = ?""",
                (amount, wallet_id)
            )

            conn.commit()
            conn.close()

            QMessageBox.information(
                self.MainWindow,
                "Nạp tiền thành công!",
                f"Đã nạp {amount:,.0f} VNĐ vào ví thành công!\nMã giao dịch: #{next_deposit_id}"
            )

            self.load_balance()

            if self.parent_dashboard and hasattr(self.parent_dashboard, 'load_wallet_info'):
                self.parent_dashboard.load_wallet_info()

        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Lỗi hệ thống", f"Không thể thực hiện nạp tiền:\n{str(e)}")

    def go_back(self):
        try:
            from UI.Customer.KhachHang_EX import KhachHang_EX
            from PyQt6.QtWidgets import QMainWindow

            self.home_window = QMainWindow()
            self.home_ui = KhachHang_EX()
            self.home_ui.setupUi(self.home_window, self.user_id)
            self.home_window.show()
            self.MainWindow.close()
        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Lỗi điều hướng", str(e))