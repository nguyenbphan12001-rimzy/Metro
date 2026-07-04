from datetime import datetime

from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtWidgets import (
    QLabel, QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QGraphicsDropShadowEffect
)

from UI.Customer.Thanhtoan import Ui_MetroBookingForm
from UI.Customer.StyledDialogs import StatusDialog, TicketSuccessDialog  # SỬA: thay QMessageBox


class ConfirmPaymentDialog(QDialog):
    def __init__(self, parent, type_name, detail_text, amount_text, balance_text):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(360)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setObjectName("confirmCard")
        card.setStyleSheet("""
            QFrame#confirmCard {
                background-color: #FFFFFF;
                border-radius: 18px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(45)
        shadow.setColor(QColor(2, 132, 199, 90))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(14)

        icon = QLabel("🎫")
        icon.setStyleSheet("font-size: 34px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Xác nhận thanh toán")
        title.setStyleSheet("font-size: 17px; font-weight: 700; color: #0C4A6E;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info_box = QFrame()
        info_box.setStyleSheet("background-color: #F0F9FF; border-radius: 12px;")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setSpacing(8)

        info_layout.addLayout(self._make_row("Loại vé", type_name))
        if detail_text:
            info_layout.addLayout(self._make_row("Hành trình", detail_text))
        info_layout.addLayout(self._make_row("Số dư hiện tại", balance_text))
        layout.addWidget(info_box)

        amount_label = QLabel(amount_text)
        amount_label.setStyleSheet("font-size: 26px; font-weight: 800; color: #0EA5E9;")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(amount_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setMinimumHeight(42)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton { background-color:#F1F5F9; color:#475569;
                border-radius:10px; font-weight:600; font-size:13px; }
            QPushButton:hover { background-color:#E2E8F0; }
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_confirm = QPushButton("Xác nhận")
        self.btn_confirm.setMinimumHeight(42)
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setStyleSheet("""
            QPushButton { background-color:#0EA5E9; color:white;
                border-radius:10px; font-weight:700; font-size:13px; }
            QPushButton:hover { background-color:#0284C7; }
        """)
        self.btn_confirm.clicked.connect(self.accept)

        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_confirm)
        layout.addLayout(btn_row)

    def _make_row(self, label_text, value_text):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color:#0284C7; font-size:12px;")
        val = QLabel(value_text)
        val.setStyleSheet("color:#0369A1; font-size:12px; font-weight:700;")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        return row

    def showEvent(self, event):
        super().showEvent(event)
        parent_rect = self.parent().geometry() if self.parent() else self.screen().geometry()
        self.adjustSize()
        x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
        y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
        start_y = y + 30

        self.move(x, start_y)
        self.setWindowOpacity(0)

        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(220)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_pos = QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(220)
        self.anim_pos.setStartValue(QPoint(x, start_y))
        self.anim_pos.setEndValue(QPoint(x, y))
        self.anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_opacity.start()
        self.anim_pos.start()


class ThanhToan_EX(Ui_MetroBookingForm):
    def setupUi(self, MetroBookingForm, conn=None, user_id=None, parent_window=None):
        super().setupUi(MetroBookingForm)
        self.conn = conn
        self.user_id = user_id
        self._window = MetroBookingForm
        self.parent_window = parent_window  # SỬA: lưu lại dashboard cha để nút Back biết quay về đâu

        self.ticket_frames = {
            self.frameTicket1: 1,  # Vé lượt
            self.frameTicket2: 2,  # Vé ngày
            self.frameTicket3: 3,  # Vé 1 tháng
            self.frameTicket4: 4,  # Vé 3 tháng
        }
        self.selected_type_id = 1

        # Gắn trực tiếp mousePressEvent, không cần installEventFilter
        for frame, type_id in self.ticket_frames.items():
            frame.mousePressEvent = lambda event, t=type_id: self.select_ticket_type(t)
            for label in frame.findChildren(QLabel):
                label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.load_wallet_balance()

        self.load_routes()
        self.comboLine.currentIndexChanged.connect(self.load_stations_by_route)
        self.comboFrom.currentIndexChanged.connect(self.update_disabled_stations)
        self.comboTo.currentIndexChanged.connect(self.update_disabled_stations)
        self.load_stations_by_route()
        self.update_ticket_selection_ui()
        self.update_stepper_ui(active_step=1)
        self.update_summary()
        self.btnPay.clicked.connect(self.on_pay_clicked)
        self.btnBack.clicked.connect(self.go_back_to_dashboard)  # SỬA: nút back mới thêm

    def go_back_to_dashboard(self):
        # SỬA: đồng bộ animation với VeCuaToi_EX._go_back —
        # chỉ animate cửa sổ CHA trượt lên + fade in, đóng cửa sổ con ngay (không animate),
        # tránh hiện tượng khựng do animate 2 cửa sổ nối tiếp nhau
        if self.parent_window is not None:
            self._show_parent_with_animation(self.parent_window)
        else:
            # SỬA: nếu không có parent_window được truyền vào, in cảnh báo để dễ debug
            print("[CẢNH BÁO] parent_window=None -> không có dashboard nào để quay lại. "
                  "Kiểm tra lại nơi gọi setupUi() của Thanhtoan, phải truyền parent_window=...")
        self._window.close()

    def _show_parent_with_animation(self, window):
        # SỬA: y hệt show_with_animation bên VeCuaToi_EX/KhachHang_Ver2_EX —
        # trượt lên 60px + fade in trong 420ms, easing OutCubic
        end_pos = window.pos()
        start_pos = QPoint(end_pos.x(), end_pos.y() + 60)

        window.move(start_pos)
        window.setWindowOpacity(0)
        window.show()
        window.raise_()
        window.activateWindow()

        self.anim_back_pos = QPropertyAnimation(window, b"pos")
        self.anim_back_pos.setDuration(420)
        self.anim_back_pos.setStartValue(start_pos)
        self.anim_back_pos.setEndValue(end_pos)
        self.anim_back_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_back_opacity = QPropertyAnimation(window, b"windowOpacity")
        self.anim_back_opacity.setDuration(420)
        self.anim_back_opacity.setStartValue(0.0)
        self.anim_back_opacity.setEndValue(1.0)
        self.anim_back_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_back_pos.start()
        self.anim_back_opacity.start()

    def load_routes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT route_id, route_name FROM ROUTE")
        self.comboLine.clear()
        for route_id, route_name in cursor.fetchall():
            self.comboLine.addItem(route_name, userData=route_id)

    def load_wallet_balance(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM WALLET WHERE user_id = ?", self.user_id)
        balance = cursor.fetchone()[0]
        self.lblBalance.setText(f"💳  Số dư: {balance:,.0f} VNĐ".replace(",", "."))

    def load_stations_by_route(self):
        route_id = self.comboLine.currentData()
        if route_id is None:
            return
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.station_id, s.station_name
            FROM ROUTESTATION rs
            JOIN STATION s ON rs.station_id = s.station_id
            WHERE rs.route_id = ?
            ORDER BY rs.position
        """, route_id)
        stations = cursor.fetchall()

        self._build_station_model(self.comboFrom, stations)
        self._build_station_model(self.comboTo, stations)

        if len(stations) > 1:
            self.comboTo.setCurrentIndex(1)

        self.update_disabled_stations()

    def _build_station_model(self, combo, stations):
        model = QStandardItemModel()
        for station_id, station_name in stations:
            item = QStandardItem(station_name)
            item.setData(station_id, Qt.ItemDataRole.UserRole)
            model.appendRow(item)
        combo.setModel(model)

    def update_disabled_stations(self):
        from_id = self.comboFrom.currentData()
        to_id = self.comboTo.currentData()

        self._disable_matching(self.comboTo, from_id)
        self._disable_matching(self.comboFrom, to_id)

        if from_id == to_id:
            self._select_first_enabled(self.comboTo, exclude_id=from_id)
        self.update_summary()

    def _disable_matching(self, combo, disabled_id):
        model = combo.model()
        for row in range(model.rowCount()):
            item = model.item(row)
            flags = item.flags()
            if item.data(Qt.ItemDataRole.UserRole) == disabled_id:
                item.setFlags(flags & ~Qt.ItemFlag.ItemIsEnabled)
            else:
                item.setFlags(flags | Qt.ItemFlag.ItemIsEnabled)

    def _select_first_enabled(self, combo, exclude_id):
        for row in range(combo.model().rowCount()):
            item = combo.model().item(row)
            if item.data(Qt.ItemDataRole.UserRole) != exclude_id:
                combo.blockSignals(True)
                combo.setCurrentIndex(row)
                combo.blockSignals(False)
                break

    def update_ticket_selection_ui(self):
        for frame, type_id in self.ticket_frames.items():
            is_selected = (type_id == self.selected_type_id)

            if is_selected:
                frame.setStyleSheet(
                    f"QFrame#{frame.objectName()} {{"
                    f"  border: 2px solid #0EA5E9;"
                    f"  background-color: #E0F2FE;"  # nền xanh nhạt khi được chọn
                    f"  border-radius: 8px;"
                    f"}}"
                )
            else:
                frame.setStyleSheet(
                    f"QFrame#{frame.objectName()} {{"
                    f"  border: 1px solid #CBD5E1;"  # viền xám nhạt khi KHÔNG chọn
                    f"  background-color: #FFFFFF;"
                    f"  border-radius: 8px;"
                    f"}}"
                )

            # Ép Qt vẽ lại style ngay, không chờ event hover/leave mới refresh
            frame.style().unpolish(frame)
            frame.style().polish(frame)
            frame.update()

        is_luot = (self.selected_type_id == 1)
        self.comboFrom.setEnabled(is_luot)
        self.comboTo.setEnabled(is_luot)

    def select_ticket_type(self, type_id):
        self.selected_type_id = type_id
        self.update_ticket_selection_ui()
        self.update_stepper_ui(active_step=2)  # vừa chọn vé -> bước 2 active
        self.update_summary()

    def update_stepper_ui(self, active_step):
        steps = [
            (self.step1Num, self.step1Label, 1),
            (self.step2Num, self.step2Label, 2),
            (self.step3Num, self.label, 3),  # "label" là tên gốc Designer đặt cho step3Label
        ]
        for num_widget, label_widget, step_no in steps:
            if step_no == active_step:
                num_widget.setStyleSheet(
                    "background:#0EA5E9; color:#fff; border-radius:14px; font-weight:bold; font-size:13px;"
                )
                label_widget.setStyleSheet("color:#0369A1; font-weight:600; font-size:12px;")
            else:
                num_widget.setStyleSheet(
                    "background:#fff; border:1.5px solid #BAE6FD; color:#7DD3FC; border-radius:14px; font-size:13px;"
                )
                label_widget.setStyleSheet("color:#7DD3FC; font-size:12px;")

            num_widget.style().unpolish(num_widget)
            num_widget.style().polish(num_widget)

    def get_next_available_train(self, route_id, reference_datetime=None):
        """
        Chọn chuyến tàu gần nhất còn chỗ trống cho vé lượt.
        - reference_datetime: cho phép truyền giờ giả lập để TEST (không có thì lấy giờ thật).
        - Chỉ đếm số vé lượt (type_id=1) đã phát hành TRONG NGÀY cho từng train_id,
          vì capacity là sức chứa của MỘT chuyến chạy trong MỘT ngày, không phải tổng all-time.
        Trả về: (train_id, departure_time_str, reason)
            reason = None nếu tìm được chuyến, hoặc "no_more_trains_today" / "all_full"
        """
        if reference_datetime is None:
            reference_datetime = datetime.now()

        ref_time = reference_datetime.time()
        ref_date = reference_datetime.date()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT train_id, departure_time, capacity
            FROM TRAIN
            WHERE route_id = ? AND departure_time >= ?
            ORDER BY departure_time ASC
        """, route_id, ref_time)
        candidates = cursor.fetchall()

        # SỬA: phân biệt rõ 2 nguyên nhân để debug dễ hơn
        if not candidates:
            # Đã qua giờ chạy của TẤT CẢ chuyến trong ngày (VD: sau 22:00)
            return None, None, "no_more_trains_today"

        for train_id, departure_time, capacity in candidates:
            cursor.execute("""
                SELECT COUNT(*) FROM TICKET
                WHERE train_id = ?
                  AND type_id = 1
                  AND status IN ('UNUSED', 'USED')
                  AND CAST(issued_at AS DATE) = ?
            """, train_id, ref_date)
            sold_count = cursor.fetchone()[0]

            if sold_count < capacity:
                dep_str = departure_time.strftime("%H:%M") if hasattr(departure_time, "strftime") else str(departure_time)
                return train_id, dep_str, None

        # Có chuyến trong khung giờ còn lại, nhưng chuyến nào cũng đã đầy 300/300
        return None, None, "all_full"

    def update_summary(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT type_name, price FROM TICKET_TYPE WHERE type_id = ?",
            self.selected_type_id
        )
        row = cursor.fetchone()
        if not row:
            return
        type_name, fixed_price = row

        route_id = self.comboLine.currentData()
        from_id = self.comboFrom.currentData()
        to_id = self.comboTo.currentData()

        if None in (route_id, from_id, to_id):
            luot_price = 0
        else:
            cursor.execute("""
                SELECT price FROM PRICE_TABLE
                WHERE route_id = ?
                  AND (
                        (from_station_id = ? AND to_station_id = ?)
                     OR (from_station_id = ? AND to_station_id = ?)
                  )
            """, route_id, from_id, to_id, to_id, from_id)
            price_row = cursor.fetchone()
            luot_price = price_row[0] if price_row else 0

        self.t1_b.setText(f"{luot_price:,.0f} VNĐ".replace(",", "."))

        price = luot_price if self.selected_type_id == 1 else fixed_price
        self.sumType.setText(type_name)
        self.sumTotal.setText(f"{price:,.0f} VNĐ".replace(",", "."))

    def on_pay_clicked(self):
        self.update_stepper_ui(active_step=3)  # thêm dòng này lên đầu
        self._window.repaint()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT type_name, price FROM TICKET_TYPE WHERE type_id = ?",
            self.selected_type_id
        )
        type_name, fixed_price = cursor.fetchone()

        route_id = self.comboLine.currentData()
        from_id = self.comboFrom.currentData()
        to_id = self.comboTo.currentData()

        if self.selected_type_id == 1:
            cursor.execute("""
                SELECT price FROM PRICE_TABLE
                WHERE route_id = ?
                  AND ((from_station_id = ? AND to_station_id = ?)
                    OR (from_station_id = ? AND to_station_id = ?))
            """, route_id, from_id, to_id, to_id, from_id)
            row = cursor.fetchone()
            price = row[0] if row else 0
        else:
            price = fixed_price
            from_id, to_id = None, None  # vé ngày/tháng không gắn ga

        cursor.execute("SELECT balance FROM WALLET WHERE user_id = ?", self.user_id)
        balance = cursor.fetchone()[0]
        balance_text = f"{balance:,.0f} VNĐ".replace(",", ".")
        amount_text = f"{price:,.0f} VNĐ".replace(",", ".")

        detail_text = ""
        if self.selected_type_id == 1:
            detail_text = f"{self.comboFrom.currentText()} → {self.comboTo.currentText()}"

        # Lưu lại để dùng khi user bấm "Xác nhận" trong dialog
        # SỬA: lưu thêm type_name, amount_text, detail_text để dùng cho TicketSuccessDialog sau này
        self._pending_payment = {
            "type_id": self.selected_type_id,
            "type_name": type_name,
            "price": price,
            "from_id": from_id,
            "to_id": to_id,
            "amount_text": amount_text,
            "detail_text": detail_text,
        }

        dialog = ConfirmPaymentDialog(self._window, type_name, detail_text, amount_text, balance_text)
        dialog.finished.connect(self.handle_payment_result)
        dialog.open()

    def handle_payment_result(self, result):
        if result == QDialog.DialogCode.Accepted:
            self.update_stepper_ui(active_step=3)
            self._window.repaint()
            QTimer.singleShot(200, self.process_payment)

        # nếu Hủy thì không làm gì, _pending_payment bỏ qua luôn

    def process_payment(self):
        info = self._pending_payment
        price = info["price"]

        if price <= 0:
            # SỬA: thay QMessageBox.warning bằng StatusDialog kiểu "error"
            dlg = StatusDialog(
                self._window,
                "Lỗi giá vé",
                "Chưa có giá hợp lệ cho chặng này. Vui lòng kiểm tra lại ga đi/ga đến.",
                kind="error",
            )
            dlg.exec()
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT wallet_id, balance FROM WALLET WHERE user_id = ?", self.user_id)
        wallet_id, balance = cursor.fetchone()

        if balance < price:
            # SỬA: thay QMessageBox.warning bằng StatusDialog kiểu "warning"
            dlg = StatusDialog(
                self._window,
                "Không đủ tiền",
                "Số dư trong ví không đủ để thanh toán vé này. Vui lòng nạp thêm tiền vào ví.",
                kind="warning",
            )
            dlg.exec()
            return

        cursor.execute("SELECT ISNULL(MAX(ticket_id), 0) FROM TICKET")
        ticket_id = cursor.fetchone()[0] + 1
        cursor.execute("SELECT ISNULL(MAX(transaction_id), 0) FROM [TRANSACTION]")
        transaction_id = cursor.fetchone()[0] + 1

        now = datetime.now()
        qr_code = f"QR_{ticket_id}_{int(now.timestamp())}"

        # SỬA: chỉ vé lượt (type_id=1) mới cần gắn chuyến tàu cụ thể.
        # Vé ngày/tháng dùng được nhiều chuyến trong ngày/tháng nên không gắn train_id.
        train_id = None
        departure_str = None
        if info["type_id"] == 1:
            route_id = self.comboLine.currentData()
            train_id, departure_str, reason = self.get_next_available_train(route_id, reference_datetime=now)

            if train_id is None:
                if reason == "no_more_trains_today":
                    title = "Đã hết giờ chạy trong ngày"
                    message = ("Chuyến cuối cùng trong ngày hôm nay đã khởi hành. "
                               "Vui lòng quay lại vào ngày mai (chuyến sớm nhất 05:00).")
                else:  # all_full
                    title = "Hết chỗ trong ngày"
                    message = ("Tất cả các chuyến còn lại trong hôm nay đã đầy chỗ (300/300). "
                               "Vui lòng quay lại vào ngày mai.")

                dlg = StatusDialog(self._window, title, message, kind="warning")
                dlg.exec()
                return

        try:
            cursor.execute("""
                INSERT INTO TICKET (ticket_id, user_id, train_id, type_id,
                    from_station_id, to_station_id, price, qr_code, status, issued_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'UNUSED', ?)
            """, ticket_id, self.user_id, train_id, info["type_id"], info["from_id"], info["to_id"], price, qr_code, now)

            cursor.execute("""
                INSERT INTO [TRANSACTION] (transaction_id, user_id, wallet_id, ticket_id, amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, transaction_id, self.user_id, wallet_id, ticket_id, price, now)
            # trigger trg_after_transaction sẽ tự trừ balance trong WALLET

            self.conn.commit()

            # Cập nhật lại số dư hiển thị trên màn hình ngay, không cần load lại cả form
            cursor.execute("SELECT balance FROM WALLET WHERE user_id = ?", self.user_id)
            new_balance = cursor.fetchone()[0]
            self.lblBalance.setText(f"💳  Số dư: {new_balance:,.0f} VNĐ".replace(",", "."))

            # SỬA: gắn giờ chuyến tàu vào detail_text khi là vé lượt, để khách biết
            # mình được xếp vào chuyến nào ngay trên dialog thành công.
            display_detail = info["detail_text"]
            if info["type_id"] == 1 and departure_str:
                display_detail = f"{display_detail} · Tàu {departure_str}"

            # SỬA: thay QMessageBox.information bằng TicketSuccessDialog có QR thật
            dlg = TicketSuccessDialog(
                self._window,
                qr_code,
                info["type_name"],
                display_detail,
                info["amount_text"],
            )
            dlg.exec()

        except Exception as e:
            self.conn.rollback()
            # SỬA: thay QMessageBox.critical bằng StatusDialog kiểu "error"
            dlg = StatusDialog(
                self._window,
                "Thanh toán thất bại",
                f"Đã xảy ra lỗi trong quá trình thanh toán:\n{e}",
                kind="error",
            )
            dlg.exec()