from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QGraphicsDropShadowEffect, QMainWindow
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup
from PyQt6.QtGui import QColor

from UI.Customer.VeCuaToi import Ui_VeCoiToiWindow


# ══════════════════════════════════════════════════════════════════════════════
# TicketCard — QFrame có hover effect + click handler
# ══════════════════════════════════════════════════════════════════════════════
class TicketCard(QFrame):
    def __init__(self, ticket: dict, on_click=None):
        super().__init__()
        self._on_click  = on_click
        self._is_active = ticket.get("status") == "UNUSED"
        status = ticket.get("status", "USED")

        if status == "UNUSED":
            self._bg_normal     = "#FFFFFF"
            self._bg_hover      = "#F0F9FF"
            self._border_normal = "#38BDF8"
            self._border_hover  = "#0EA5E9"
        elif status == "USED":
            self._bg_normal     = "#F8FAFC"
            self._bg_hover      = "#F1F5F9"
            self._border_normal = "#E2E8F0"
            self._border_hover  = "#CBD5E1"
        else:  # EXPIRED
            self._bg_normal     = "#FFF8F8"
            self._bg_hover      = "#FEF2F2"
            self._border_normal = "#FEE2E2"
            self._border_hover  = "#FECACA"

        self._apply_style(hovered=False)

        if self._is_active:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _apply_style(self, hovered: bool):
        bg     = self._bg_hover     if hovered else self._bg_normal
        border = self._border_hover if hovered else self._border_normal
        self.setStyleSheet(f"""
            QFrame#{self.objectName()} {{
                background-color: {bg};
                border: 1.5px solid {border};
                border-radius: 14px;
            }}
        """)
        if self._is_active:
            if hovered:
                fx = QGraphicsDropShadowEffect()
                fx.setBlurRadius(20)
                fx.setOffset(0, 4)
                fx.setColor(QColor(14, 165, 233, 60))
                self.setGraphicsEffect(fx)
            else:
                self.setGraphicsEffect(None)

    def enterEvent(self, event):
        self._apply_style(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_style(hovered=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._is_active and self._on_click:
            self._on_click()
        super().mousePressEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
# Helper: tạo nội dung bên trong card vé
# ══════════════════════════════════════════════════════════════════════════════
def make_ticket_card(ticket: dict, on_click=None) -> TicketCard:
    """
    ticket = {
        'ticket_id', 'qr_code', 'status',   # 'UNUSED' | 'USED' | 'EXPIRED'
        'price', 'issued_at',
        'type_name',
        'from_station', 'to_station'         # có thể None nếu vé tháng
    }
    """
    status    = ticket.get("status", "USED")
    is_active = status == "UNUSED"

    # ── Màu sắc theo trạng thái ──
    if is_active:
        badge_bg    = "#E0F2FE"
        badge_color = "#0284C7"
        badge_text  = "✓  Còn hiệu lực"
        price_color = "#0EA5E9"
        title_color = "#0C4A6E"
        sub_color   = "#0369A1"
        accent_left = "#0EA5E9"
    elif status == "USED":
        badge_bg    = "#F1F5F9"
        badge_color = "#64748B"
        badge_text  = "✓  Đã sử dụng"
        price_color = "#94A3B8"
        title_color = "#94A3B8"
        sub_color   = "#CBD5E1"
        accent_left = "#CBD5E1"
    else:  # EXPIRED
        badge_bg    = "#FEE2E2"
        badge_color = "#EF4444"
        badge_text  = "✕  Hết hạn"
        price_color = "#FCA5A5"
        title_color = "#94A3B8"
        sub_color   = "#CBD5E1"
        accent_left = "#FCA5A5"

    # ── Outer card (TicketCard thay cho QFrame thường) ──
    outer = TicketCard(ticket, on_click=on_click)
    outer.setObjectName(f"ticketCard_{ticket.get('ticket_id', 0)}")
    outer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    h_layout = QHBoxLayout(outer)
    h_layout.setContentsMargins(0, 0, 12, 0)
    h_layout.setSpacing(0)

    # ── Dải màu bên trái (accent strip) ──
    strip = QFrame()
    strip.setFixedWidth(6)
    strip.setStyleSheet(f"""
        background-color: {accent_left};
        border-top-left-radius: 14px;
        border-bottom-left-radius: 14px;
    """)
    strip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    h_layout.addWidget(strip)

    # ── Nội dung chính ──
    content = QVBoxLayout()
    content.setContentsMargins(14, 12, 0, 12)
    content.setSpacing(6)

    # Dòng 1: loại vé + badge trạng thái
    row1 = QHBoxLayout()
    row1.setSpacing(8)

    lbl_type = QLabel(ticket.get("type_name", "Vé"))
    lbl_type.setStyleSheet(f"color:{title_color}; font-size:14px; font-weight:700;")
    lbl_type.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    row1.addWidget(lbl_type)

    row1.addStretch()

    badge = QLabel(badge_text)
    badge.setStyleSheet(f"""
        background-color:{badge_bg}; color:{badge_color};
        border-radius:8px; font-size:11px; font-weight:600;
        padding: 2px 8px;
    """)
    badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    row1.addWidget(badge)
    content.addLayout(row1)

    # Dòng 2: hành trình (nếu có)
    from_s = ticket.get("from_station")
    to_s   = ticket.get("to_station")
    if from_s and to_s:
        lbl_route = QLabel(f"📍 {from_s}  →  {to_s}")
    else:
        lbl_route = QLabel("🗓  Không giới hạn ga")
    lbl_route.setStyleSheet(f"color:{sub_color}; font-size:12px;")
    lbl_route.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    content.addWidget(lbl_route)

    # Dòng 3: ngày mua + giá
    row3 = QHBoxLayout()
    issued = ticket.get("issued_at")
    if issued:
        date_str = issued.strftime("%d/%m/%Y  %H:%M") if hasattr(issued, "strftime") else str(issued)[:16]
    else:
        date_str = ""
    lbl_date = QLabel(f"🕐 {date_str}")
    lbl_date.setStyleSheet(f"color:{sub_color}; font-size:11px;")
    lbl_date.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    row3.addWidget(lbl_date)

    row3.addStretch()

    price = ticket.get("price", 0)
    lbl_price = QLabel(f"{price:,.0f} VNĐ".replace(",", "."))
    lbl_price.setStyleSheet(f"color:{price_color}; font-size:15px; font-weight:800;")
    lbl_price.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    row3.addWidget(lbl_price)
    content.addLayout(row3)

    # Dòng 4: QR code nhỏ (chỉ hiện nếu UNUSED)
    if is_active:
        lbl_qr = QLabel(f"QR: {ticket.get('qr_code', '')}   •   Nhấn để xem mã QR ↗")
        lbl_qr.setStyleSheet("color:#BAE6FD; font-size:10px;")
        lbl_qr.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        content.addWidget(lbl_qr)

    h_layout.addLayout(content)
    return outer


# ══════════════════════════════════════════════════════════════════════════════
# VeCuaToi_EX — class logic chính
# ══════════════════════════════════════════════════════════════════════════════
class VeCuaToi_EX(Ui_VeCoiToiWindow):
    def setupUi(self, MainWindow, conn=None, user_id=None, parent_window=None):
        super().setupUi(MainWindow)
        self.conn            = conn
        self.user_id         = user_id
        self._window         = MainWindow
        self._parent_window  = parent_window
        self._current_filter = "ALL"   # ALL | UNUSED | USED | EXPIRED

        # ── Nút back ──
        self.btn_back.clicked.connect(self._go_back)
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #E0F2FE;
            }
        """)

        # ── Tab filter ──
        self.btnTabAll.clicked.connect(lambda: self.apply_filter("ALL"))
        self.btnTabUnused.clicked.connect(lambda: self.apply_filter("UNUSED"))
        self.btnTabUsed.clicked.connect(lambda: self.apply_filter("USED"))
        self.btnTabExpired.clicked.connect(lambda: self.apply_filter("EXPIRED"))

        self._update_tab_styles()
        self.load_tickets()

    # ── Load dữ liệu từ DB ──────────────────────────────────────────────────
    def load_tickets(self):
        cursor = self.conn.cursor()

        # SỬA: tự động chuyển vé UNUSED đã quá hạn sang EXPIRED trước khi load danh sách.
        # Gồm 2 trường hợp:
        #   1. Vé ngày/tháng (validity_days có giá trị): hết hạn khi issued_at + validity_days < NOW()
        #   2. Vé lượt (type_id = 1, validity_days = NULL): chỉ có giá trị trong đúng NGÀY mua,
        #      nếu chưa dùng mà đã sang ngày khác thì hết hạn luôn (so sánh theo CAST ... AS DATE
        #      để không dính giờ phút, chỉ so ngày với ngày).
        cursor.execute("""
            UPDATE TICKET
            SET status = 'EXPIRED'
            FROM TICKET t
            JOIN TICKET_TYPE tt ON t.type_id = tt.type_id
            WHERE t.user_id = ?
              AND t.status = 'UNUSED'
              AND (
                    (tt.validity_days IS NOT NULL
                        AND DATEADD(DAY, tt.validity_days, t.issued_at) < GETDATE())
                 OR (tt.validity_days IS NULL
                        AND CAST(t.issued_at AS DATE) < CAST(GETDATE() AS DATE))
                  )
        """, self.user_id)
        self.conn.commit()

        cursor.execute("""
            SELECT t.ticket_id, t.qr_code, t.status, t.price, t.issued_at,
                   tt.type_name,
                   s1.station_name AS from_station,
                   s2.station_name AS to_station
            FROM TICKET t
            JOIN TICKET_TYPE tt ON t.type_id = tt.type_id
            LEFT JOIN STATION s1 ON t.from_station_id = s1.station_id
            LEFT JOIN STATION s2 ON t.to_station_id = s2.station_id
            WHERE t.user_id = ?
            ORDER BY t.issued_at DESC
        """, self.user_id)

        rows = cursor.fetchall()
        self._all_tickets = [
            {
                "ticket_id":    r[0],
                "qr_code":      r[1],
                "status":       r[2],
                "price":        float(r[3]),
                "issued_at":    r[4],
                "type_name":    r[5],
                "from_station": r[6],
                "to_station":   r[7],
            }
            for r in rows
        ]
        self.render_tickets(self._all_tickets)

    # ── Lọc theo tab ────────────────────────────────────────────────────────
    def apply_filter(self, status_filter: str):
        self._current_filter = status_filter
        self._update_tab_styles()

        if status_filter == "ALL":
            filtered = self._all_tickets
        else:
            filtered = [t for t in self._all_tickets if t["status"] == status_filter]

        self.render_tickets(filtered)

    # ── Render danh sách card vào layout ────────────────────────────────────
    def render_tickets(self, tickets: list):
        layout = self.ticketListLayout   # QVBoxLayout trong scrollContents

        # Xóa card cũ (trừ lbl_empty và spacer cuối)
        while layout.count() > 2:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not tickets:
            self.lbl_empty.setVisible(True)
            self.lbl_count.setText("0 vé")
            return

        self.lbl_empty.setVisible(False)
        self.lbl_count.setText(f"{len(tickets)} vé")

        for i, ticket in enumerate(tickets):
            on_click = (lambda t=ticket: self._open_qr(t)) if ticket["status"] == "UNUSED" else None
            card = make_ticket_card(ticket, on_click=on_click)
            layout.insertWidget(i, card)

    # ── Mở màn QR khi click vé còn hiệu lực ────────────────────────────────
    def _open_qr(self, ticket: dict):
        # TODO: thay bằng màn QR thật sau khi có file UI
        # Ví dụ khi có QRCode_EX:
        #
        # from UI.Customer.QRCode_EX import QRCode_EX
        # qr_window = QMainWindow()
        # ui = QRCode_EX()
        # ui.setupUi(qr_window, ticket=ticket, parent_window=self._window)
        # ui.show_with_animation(qr_window)
        # self._window.hide()

        print(f"[QR] Mở vé #{ticket['ticket_id']} — mã: {ticket['qr_code']}")

    # ── Style tab active/inactive ────────────────────────────────────────────
    def _update_tab_styles(self):
        active_style = """
            background-color: #0EA5E9; color: #FFFFFF;
            border-radius: 8px; font-size: 12px; font-weight: 700;
            padding: 6px 10px;
        """
        inactive_style = """
            background-color: transparent; color: #7DD3FC;
            border-radius: 8px; font-size: 12px; font-weight: 600;
            padding: 6px 10px; border: none;
        """
        mapping = {
            "ALL":     self.btnTabAll,
            "UNUSED":  self.btnTabUnused,
            "USED":    self.btnTabUsed,
            "EXPIRED": self.btnTabExpired,
        }
        for key, btn in mapping.items():
            btn.setStyleSheet(active_style if key == self._current_filter else inactive_style)

    # ── Animation show window ────────────────────────────────────────────────
    def show_with_animation(self, window):
        end_pos   = window.pos()
        start_pos = QPoint(end_pos.x(), end_pos.y() + 60)

        window.move(start_pos)
        window.setWindowOpacity(0)
        window.show()

        self._anim_pos = QPropertyAnimation(window, b"pos")
        self._anim_pos.setDuration(420)
        self._anim_pos.setStartValue(start_pos)
        self._anim_pos.setEndValue(end_pos)
        self._anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_opacity = QPropertyAnimation(window, b"windowOpacity")
        self._anim_opacity.setDuration(420)
        self._anim_opacity.setStartValue(0.0)
        self._anim_opacity.setEndValue(1.0)
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_group = QParallelAnimationGroup()
        self._anim_group.addAnimation(self._anim_pos)
        self._anim_group.addAnimation(self._anim_opacity)
        self._anim_group.start()

    # ── Nút back về màn trước ───────────────────────────────────────────────
    def _go_back(self):
        if self._parent_window:
            self.show_with_animation(self._parent_window)
        self._window.close()

    # ── Mở màn QR khi click vé còn hiệu lực ────────────────────────────────
        # ── Mở dialog xem QR vé (KHÁC dialog "mua vé thành công") ───────────────
    def _open_qr(self, ticket: dict):
        from UI.Customer.TicketQRDialog import \
            TicketQRDialog

        dlg = TicketQRDialog(self._window, ticket)
        dlg.exec()