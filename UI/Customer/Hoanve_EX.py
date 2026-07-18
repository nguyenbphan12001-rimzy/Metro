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
                   tt.type_name, tt.validity_days,
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
         from_id, to_id, issued_at, type_name, validity_days, from_name, to_name) = row

        # SỬA DEBUG: in ra ngay để biết chắc type_id/status thật sự đang lấy được là gì
        print(f"[DEBUG lookup_ticket] ticket_id={ticket_id}, type_id={type_id}, status={status}")

        # SỬA: check hết hạn THEO THỜI GIAN THỰC (giống hệt logic bên Scanning_App.py).
        # Status trong DB chỉ được cập nhật thành EXPIRED khi có người quét vé đó,
        # nên nếu vé hết hạn mà chưa ai quét lại thì DB vẫn ghi UNOSED -> phải tự tính lại ở đây,
        # tránh trường hợp khách hoàn được vé đã hết hạn thực tế.
        if type_id != 1 and validity_days:
            cursor.execute("SELECT DATEDIFF(day, ?, GETDATE())", issued_at)
            days_passed = cursor.fetchone()[0]
            if days_passed > validity_days and status != 'EXPIRED':
                cursor.execute("UPDATE TICKET SET status='EXPIRED' WHERE ticket_id=?", ticket_id)
                self.conn.commit()
                status = 'EXPIRED'

        # SỬA: vé ngày/tháng (type_id != 1) không đổi status khi scan — status vẫn UNUSED
        # dù đã quét rồi, nên phải check riêng SCANNING_HISTORY xem đã từng quét chưa.
        # Đây là ràng buộc chính: chỉ cần quét 1 lần (IN) là vé ngày/1 tháng/3 tháng
        # không còn được hoàn nữa, dù status vẫn hiển thị UNUSED (khác vé lượt — vé lượt
        # bị đổi hẳn sang USED ngay khi quét IN).
        already_scanned = False
        scan_count = 0
        if type_id != 1:
            cursor.execute(
                "SELECT COUNT(*) FROM SCANNING_HISTORY WHERE ticket_id = ?", ticket_id
            )
            scan_count = cursor.fetchone()[0]
            already_scanned = scan_count > 0

        # SỬA DEBUG: đây là dòng quan trọng nhất để mày xem console —
        # nếu vừa quét xong ở điện thoại mà scan_count vẫn ra 0 ở đây,
        # nghĩa là 2 app đang KHÔNG cùng trỏ vào 1 database.
        print(f"[DEBUG lookup_ticket] type_id={type_id} -> scan_count trong SCANNING_HISTORY = {scan_count}, already_scanned={already_scanned}")

        self._current_ticket = {
            "ticket_id": ticket_id, "price": price, "status": status,
            "already_scanned": already_scanned  # SỬA
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
        # SỬA: vé chỉ hoàn được khi vừa UNUSED vừa chưa từng bị quét qua cổng
        can_refund = (status == "UNUSED") and not already_scanned

        # SỬA DEBUG: in luôn giá trị can_refund cuối cùng, để biết chắc UI có đang
        # enable nút Xác nhận đúng theo logic hay không
        print(f"[DEBUG lookup_ticket] can_refund={can_refund} (status=='UNUSED' -> {status == 'UNUSED'}, not already_scanned -> {not already_scanned})")

        self.ticket_info_card.setVisible(True)
        self.refund_amount_row.setVisible(can_refund)
        self.lbl_empty_state.setVisible(False)

        # Chỉ enable nút nếu vé chưa dùng VÀ chưa từng bị quét
        self.btn_confirm_refund.setEnabled(can_refund)

        if status != "UNUSED":
            QMessageBox.information(self._window, "Không thể hoàn",
                                    f"Vé này có trạng thái '{label}', không thể hoàn.")
        elif already_scanned:  # SỬA: case mới — status vẫn UNUSED nhưng đã bị quét rồi
            QMessageBox.information(self._window, "Không thể hoàn",
                                    "Vé này đã được sử dụng (đã quét qua cổng soát vé), không thể hoàn tiền.")

    def confirm_refund(self):
        if not self._current_ticket:
            return

        ticket_id = self._current_ticket["ticket_id"]
        price     = self._current_ticket["price"]

        cursor = self.conn.cursor()

        # SỬA: check lại lần nữa ngay trước khi hoàn, phòng vé bị quét/hết hạn ở khoảng
        # thời gian giữa lúc lookup_ticket() và lúc user bấm xác nhận (race condition)
        cursor.execute("""
            SELECT t.type_id, t.status, t.issued_at, tt.validity_days
            FROM TICKET t JOIN TICKET_TYPE tt ON t.type_id = tt.type_id
            WHERE t.ticket_id = ?
        """, ticket_id)
        type_id, cur_status, issued_at, validity_days = cursor.fetchone()

        # SỬA DEBUG: in ra ngay đầu confirm_refund, đây là bằng chứng quan trọng nhất —
        # nếu type_id ở đây không phải 2/3/4 như mày nghĩ, hoặc cur_status không phải UNUSED,
        # thì phải xem lại vé mày đang test thực ra là vé gì.
        print(f"[DEBUG confirm_refund] ticket_id={ticket_id}, type_id={type_id}, cur_status={cur_status}")

        # Check hết hạn real-time lần nữa
        if type_id != 1 and validity_days:
            cursor.execute("SELECT DATEDIFF(day, ?, GETDATE())", issued_at)
            days_passed = cursor.fetchone()[0]
            if days_passed > validity_days:
                if cur_status != 'EXPIRED':
                    cursor.execute("UPDATE TICKET SET status='EXPIRED' WHERE ticket_id=?", ticket_id)
                    self.conn.commit()
                QMessageBox.warning(self._window, "Không thể hoàn",
                                    "Vé này đã hết hạn sử dụng, không thể hoàn tiền.")
                self._reset_ui()
                return

        # SỬA: chặn hoàn nếu vé không còn ở trạng thái UNUSED (vé lượt đã USED,
        # hoặc vé bất kỳ đã CANCELLED/EXPIRED) — trước đây thiếu bước check này ở
        # confirm_refund, chỉ có ở lookup_ticket() nên có khe hở nếu code gọi thẳng
        # confirm_refund() mà bỏ qua lookup.
        if cur_status != 'UNUSED':
            print(f"[DEBUG confirm_refund] BỊ CHẶN vì cur_status='{cur_status}' khác 'UNUSED'")
            QMessageBox.warning(self._window, "Không thể hoàn",
                                f"Vé này hiện có trạng thái '{cur_status}', không thể hoàn tiền.")
            self._reset_ui()
            return

        # Check đã từng bị quét chưa (vé ngày/tháng chỉ cần quét IN 1 lần là khóa hoàn vé)
        cursor.execute("SELECT COUNT(*) FROM SCANNING_HISTORY WHERE ticket_id = ?", ticket_id)
        scan_count = cursor.fetchone()[0]

        # SỬA DEBUG: đây là dòng mấu chốt để xác định vụ vé ngày/tháng vẫn hoàn được
        # -> nếu quét xong bên điện thoại rồi mà scan_count vẫn ra 0 ở đây,
        # nghĩa là app desktop và Scanning_App.py KHÔNG cùng connect vào 1 database
        # (khác connection string/server/database name trong App/DB_Connection.py)
        print(f"[DEBUG confirm_refund] type_id={type_id} -> scan_count={scan_count}")

        if scan_count > 0 and type_id != 1:
            print(f"[DEBUG confirm_refund] BỊ CHẶN vì đã có {scan_count} lượt quét cho vé ngày/tháng này")
            QMessageBox.warning(self._window, "Không thể hoàn",
                                "Vé này đã được quét sử dụng, không thể hoàn tiền.")
            self._reset_ui()
            return

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
            print(f"[DEBUG confirm_refund] Hoàn vé THÀNH CÔNG cho ticket_id={ticket_id}, số tiền={price}")

            # Cập nhật số dư hiển thị
            self.load_balance()
            self._reset_ui()
            QMessageBox.information(self._window, "Hoàn vé thành công",
                                    f"Đã hoàn {price:,.0f} VNĐ vào ví của bạn.".replace(",", "."))
        except Exception as e:
            self.conn.rollback()
            print(f"[DEBUG confirm_refund] LỖI khi hoàn vé: {e}")
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