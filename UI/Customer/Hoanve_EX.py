from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QColor
from UI.Customer.Hoanve import Ui_RefundWindow


class Hoanve_EX(Ui_RefundWindow):
    def setupUi(self, window, conn=None, user_id=None,parent_window=None):
        super().setupUi(window)
        self.conn = conn
        self.user_id = user_id
        self._window = window
        self._current_ticket = None
        self._parent_window = parent_window

        self.btn_lookup.clicked.connect(self.lookup_ticket)
        self.btn_confirm_refund.clicked.connect(self.confirm_refund)
        self.btn_back.clicked.connect(lambda: self._go_back())
        print(f"[DEBUG] btn_back connected: {self.btn_back}")
        print(f"[DEBUG] btn_back isEnabled: {self.btn_back.isEnabled()}")
        print(f"[DEBUG] btn_back isVisible: {self.btn_back.isVisible()}")
        print(f"[DEBUG] btn_back geometry: {self.btn_back.geometry()}")

        self.load_balance()

    def load_balance(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM WALLET WHERE user_id = ?", self.user_id)
        row = cursor.fetchone()
        if row:
            self.lbl_balance_value.setText(f"{row[0]:,.0f} VNĐ".replace(",", "."))

    def lookup_ticket(self):
        code = self.inp_ticket_code.text().strip()
        if not code:
            QMessageBox.warning(self._window, "Thiếu thông tin", "Vui lòng nhập mã vé.")
            return

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.ticket_id, t.qr_code, t.type_id, t.price, t.status,
                   t.from_station_id, t.to_station_id, t.issued_at,
                   tt.type_name,
                   sf.station_name AS from_name,
                   st2.station_name AS to_name
            FROM TICKET t
            JOIN TICKET_TYPE tt ON t.type_id = tt.type_id
            LEFT JOIN STATION sf  ON t.from_station_id = sf.station_id
            LEFT JOIN STATION st2 ON t.to_station_id   = st2.station_id
            WHERE (t.qr_code = ? OR CAST(t.ticket_id AS VARCHAR) = ?)
              AND t.user_id = ?
        """, code, code, self.user_id)
        row = cursor.fetchone()

        if not row:
            QMessageBox.warning(self._window, "Không tìm thấy",
                                "Không tìm thấy vé hợp lệ thuộc tài khoản này.")
            self._reset_ui()
            return

        (ticket_id, qr_code, type_id, price, status,
         from_id, to_id, issued_at, type_name, from_name, to_name) = row

        self._current_ticket = {
            "ticket_id": ticket_id, "price": price, "status": status
        }

        # Hiển thị thông tin vé
        if from_name and to_name:
            self.lbl_ticket_route.setText(f"{from_name} → {to_name}")
        else:
            self.lbl_ticket_route.setText("(Không giới hạn tuyến)")

        self.lbl_ticket_type.setText(type_name)
        self.lbl_ticket_date.setText(
            f"Ngày mua: {issued_at.strftime('%d/%m/%Y %H:%M') if hasattr(issued_at, 'strftime') else str(issued_at)}"
        )
        self.lbl_ticket_price_value.setText(f"{price:,.0f} VNĐ".replace(",", "."))
        self.lbl_refund_amount.setText(f"{price:,.0f} VNĐ".replace(",", "."))

        # Badge trạng thái
        status_map = {
            "UNUSED":  ("CHƯA DÙNG", "#DCFCE7", "#166534"),
            "USED":    ("ĐÃ DÙNG",   "#FEE2E2", "#991B1B"),
            "EXPIRED": ("HẾT HẠN",   "#FEF3C7", "#92400E"),
        }
        label, bg, fg = status_map.get(status, (status, "#F1F5F9", "#475569"))
        self.badge_status.setText(label)
        self.badge_status.setStyleSheet(
            f"background-color:{bg}; color:{fg}; border-radius:8px;"
            f"font-size:11px; font-weight:700; padding:3px 10px;"
        )

        # Hiện/ẩn các card
        self.ticket_info_card.setVisible(True)
        self.refund_amount_row.setVisible(status == "UNUSED")
        self.lbl_empty_state.setVisible(False)

        # Chỉ enable nút nếu vé UNUSED
        self.btn_confirm_refund.setEnabled(status == "UNUSED")

        if status != "UNUSED":
            QMessageBox.information(self._window, "Không thể hoàn",
                                    f"Vé này có trạng thái '{label}', không thể hoàn.")

    def confirm_refund(self):
        if not self._current_ticket:
            return

        ticket_id = self._current_ticket["ticket_id"]
        price     = self._current_ticket["price"]

        cursor = self.conn.cursor()
        cursor.execute("SELECT wallet_id FROM WALLET WHERE user_id = ?", self.user_id)
        wallet_id = cursor.fetchone()[0]

        cursor.execute("SELECT ISNULL(MAX(refund_id), 0) FROM REFUNDS")
        refund_id = cursor.fetchone()[0] + 1

        try:
            # Insert vào REFUNDS
            cursor.execute("""
                INSERT INTO REFUNDS (refund_id, ticket_id, wallet_id, amount)
                VALUES (?, ?, ?, ?)
            """, refund_id, ticket_id, wallet_id, price)

            # Cộng lại tiền vào ví (REFUNDS không có trigger, phải UPDATE thủ công)
            cursor.execute("""
                UPDATE WALLET SET balance = balance + ?, last_updated = CURRENT_TIMESTAMP
                WHERE wallet_id = ?
            """, price, wallet_id)

            # Đánh dấu vé đã hoàn (dùng USED để tránh dùng lại)
            cursor.execute("""
                UPDATE TICKET SET status = 'USED' WHERE ticket_id = ?
            """, ticket_id)

            self.conn.commit()

            # Cập nhật số dư hiển thị
            self.load_balance()
            self._reset_ui()
            QMessageBox.information(self._window, "Hoàn vé thành công",
                                    f"Đã hoàn {price:,.0f} VNĐ vào ví của bạn.".replace(",", "."))
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self._window, "Lỗi", f"Hoàn vé thất bại:\n{e}")

    def _reset_ui(self):
        self.inp_ticket_code.clear()
        self.ticket_info_card.setVisible(False)
        self.refund_amount_row.setVisible(False)
        self.lbl_empty_state.setVisible(True)
        self.btn_confirm_refund.setEnabled(False)
        self._current_ticket = None

    def _go_back(self):
        self._window.close()
        if self._parent_window:
            # Refresh số dư dashboard
            if hasattr(self._parent_window, 'dashboard_gui'):
                self._parent_window.dashboard_gui.load_wallet_info()
                # Dùng animation của dashboard để show lại
                self._parent_window.dashboard_gui.show_with_animation(self._parent_window)
            else:
                self._parent_window.show()