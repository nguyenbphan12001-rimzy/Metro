import traceback

from UI.Customer.NapTien_Ver2 import Ui_TopUpWindow
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
from UI.Customer.SuccessToast import SuccessToast   # SỬA: thay QMessageBox.information
from UI.Customer.ErrorToast import ErrorToast       # SỬA: thay QMessageBox.warning/critical

# method_id tương ứng theo thứ tự insert trong Nhom1.sql:
# 1 = Tiền mặt, 2 = Thẻ tín dụng, 3 = MoMo, 4 = VNPay
PAYMENT_METHOD_MAP = {
    "Tiền mặt": 1,
    "Thẻ tín dụng": 2,
    "MoMo": 3,
    "VNPay": 4,
}


class Naptien_Ver2_EX(Ui_TopUpWindow):

    def setupUi(self, Window, conn=None, user_id=None, parent_window=None):
        super().setupUi(Window)

        self.conn = conn
        self.user_id = user_id
        self.parent_window = parent_window
        self.wallet_id = None
        self._window = Window

        if self.conn is None or self.user_id is None:
            print("[WARNING] Thiếu conn hoặc user_id khi setupUi NapTien — bỏ qua load balance.")
        else:
            self._load_wallet_balance()

        self.btn_quick_1.clicked.connect(lambda: self._on_quick_amount(50000))
        self.btn_quick_2.clicked.connect(lambda: self._on_quick_amount(100000))
        self.btn_quick_3.clicked.connect(lambda: self._on_quick_amount(200000))
        self.btn_quick_4.clicked.connect(lambda: self._on_quick_amount(500000))

        self.btn_confirm_topup.clicked.connect(self._safe(self._on_confirm_topup))
        self.btn_back.clicked.connect(self._safe(self._on_back))

    def _safe(self, fn):
        def wrapper():
            try:
                fn()
            except Exception:
                traceback.print_exc()
        return wrapper

    # SỬA: helper toast dùng chung, đồng bộ pattern với Dangky_Ver2_EX
    def _show_error(self, message):
        self._error_toast = ErrorToast(self._window, message)
        self._error_toast.show_animated()

    def _show_success(self, message):
        self._success_toast = SuccessToast(self._window, message)
        self._success_toast.show_animated()

    def _load_wallet_balance(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT wallet_id, balance FROM WALLET WHERE user_id = ?", self.user_id
        )
        row = cursor.fetchone()
        if row:
            self.wallet_id, balance = row
            self.lbl_balance_value.setText(f"{balance:,.0f} VNĐ")
        cursor.close()

    def _on_quick_amount(self, amount: int):
        self.inp_amount.setText(str(amount))

    def _on_confirm_topup(self):
        raw = self.inp_amount.text().strip().replace(",", "")
        if not raw.isdigit() or int(raw) <= 0:
            self._show_error("Vui lòng nhập số tiền hợp lệ (> 0).")  # SỬA
            return

        amount = int(raw)
        method_name = self.cbo_payment_method.currentText()
        method_id = PAYMENT_METHOD_MAP.get(method_name)

        if not self.wallet_id or not method_id:
            self._show_error("Không xác định được ví hoặc phương thức thanh toán.")  # SỬA
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO DEPOSIT_HISTORY (deposit_id, wallet_id, user_id, method_id, amount)
                VALUES (
                    (SELECT ISNULL(MAX(deposit_id), 0) + 1 FROM DEPOSIT_HISTORY),
                    ?, ?, ?, ?
                )
                """,
                self.wallet_id, self.user_id, method_id, amount,
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            traceback.print_exc()
            self._show_error("Nạp tiền thất bại, vui lòng thử lại.")  # SỬA
            cursor.close()
            return

        cursor.close()
        self._load_wallet_balance()
        self._show_success(f"Nạp {amount:,} VNĐ vào ví thành công!")  # SỬA
        self.inp_amount.clear()

    def _on_back(self):
        if self.parent_window:
            if hasattr(self.parent_window, "dashboard_gui"):
                dash = self.parent_window.dashboard_gui
                dash.load_wallet_info()  # refresh số dư trước khi hiện lại
                dash.show_with_animation(self.parent_window)  # SỬA: dùng animation slide-up+fade thay vì .show() trơn
            else:
                self.parent_window.show()  # fallback nếu không có dashboard_gui (vd. khi test riêng màn này)
            self._window.hide()