from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGraphicsDropShadowEffect, QWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient

# Thư viện tạo QR thật - cần cài: pip install qrcode pillow
try:
    import qrcode
    from PyQt6.QtGui import QImage, QPixmap
    _QRCODE_AVAILABLE = True
except ImportError:
    _QRCODE_AVAILABLE = False


# ============================================================
# ICON VẼ TAY: vòng tròn gradient nổi khối + dấu hiệu (✓ / ✕ / !)
# Không dùng emoji để giữ phong cách đồng nhất, sắc nét trên mọi máy
# ============================================================
class _IconBadge(QWidget):
    COLORS = {
        "warning": QColor(245, 158, 11),   # cam đậm
        "error":   QColor(220, 38, 38),    # đỏ đậm
        "success": QColor(22, 163, 74),    # xanh đậm
    }

    def __init__(self, kind="warning", size=72, parent=None):
        super().__init__(parent)
        self.kind = kind
        self._size = size
        self.setFixedSize(size, size)

        main_color = self.COLORS.get(kind, self.COLORS["warning"])
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 7)
        shadow.setColor(QColor(main_color.red(), main_color.green(), main_color.blue(), 140))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        main_color = self.COLORS.get(self.kind, self.COLORS["warning"])
        rect = QRectF(4, 4, self._size - 8, self._size - 8)

        # Gradient chéo -> tạo cảm giác nổi khối, không phẳng dẹt
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, main_color.lighter(120))
        gradient.setColorAt(1.0, main_color.darker(115))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(rect)

        # Viền sáng mỏng phía trên-trái, giả lập ánh sáng chiếu vào (bevel nhẹ)
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect.adjusted(2, 2, -2, -2), 40 * 16, 110 * 16)

        cx, cy = rect.center().x(), rect.center().y()
        pen = QPen(QColor(255, 255, 255), 5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        if self.kind == "success":
            path = QPainterPath()
            path.moveTo(cx - 15, cy + 1)
            path.lineTo(cx - 4, cy + 13)
            path.lineTo(cx + 17, cy - 13)
            painter.drawPath(path)

        elif self.kind == "error":
            off = 11
            painter.drawLine(int(cx - off), int(cy - off), int(cx + off), int(cy + off))
            painter.drawLine(int(cx - off), int(cy + off), int(cx + off), int(cy - off))

        else:  # warning: dấu chấm than
            painter.drawLine(int(cx), int(cy - 15), int(cx), int(cy + 3))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QRectF(cx - 3, cy + 8, 6, 6))

        painter.end()


# ============================================================
# Hiệu ứng mở dialog dùng chung: fade-in + slide lên nhẹ
# (cùng phong cách với ConfirmPaymentDialog đã có)
# ============================================================
class _AnimatedDialogMixin:
    def _play_entrance_animation(self):
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


# ============================================================
# DIALOG 1: dùng cho lỗi / cảnh báo đơn giản
# Thay cho QMessageBox.warning(...) và QMessageBox.critical(...)
# ============================================================
class StatusDialog(QDialog, _AnimatedDialogMixin):
    ACCENT = {
        "warning": "#F59E0B",
        "error": "#DC2626",
        "success": "#16A34A",
    }

    def __init__(self, parent, title, message, kind="warning", ok_text="Đã hiểu"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(340)

        accent = self.ACCENT.get(kind, self.ACCENT["warning"])

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setObjectName("statusCard")
        card.setStyleSheet(f"""
            QFrame#statusCard {{
                background-color: #FFFFFF;
                border-radius: 18px;
                border-top: 4px solid {accent};
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(42)
        shadow.setColor(QColor(15, 23, 42, 95))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 26, 26, 22)
        layout.setSpacing(12)

        badge_row = QHBoxLayout()
        badge_row.addStretch()
        badge_row.addWidget(_IconBadge(kind))
        badge_row.addStretch()
        layout.addLayout(badge_row)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size:16px; font-weight:700; color:#0F172A;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("font-size:13px; color:#475569;")
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_lbl)

        btn_ok = QPushButton(ok_text)
        btn_ok.setMinimumHeight(42)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent}; color: white;
                border-radius: 10px; font-weight: 700; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {accent}; }}
        """)
        btn_ok.clicked.connect(self.accept)
        layout.addSpacing(4)
        layout.addWidget(btn_ok)

    def showEvent(self, event):
        super().showEvent(event)
        self._play_entrance_animation()


# ============================================================
# DIALOG 2: khung vé mua thành công, có QR THẬT quét được
# Thay cho QMessageBox.information(... "Mua vé thành công" ...)
# ============================================================
class TicketSuccessDialog(QDialog, _AnimatedDialogMixin):
    def __init__(self, parent, qr_text, type_name, detail_text, amount_text, train_time=None):
        # SỬA: thêm train_time riêng, không nhét chung vào detail_text nữa
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(360)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setObjectName("ticketCard")
        card.setStyleSheet("""
            QFrame#ticketCard {
                background-color: #FFFFFF;
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(55)
        shadow.setColor(QColor(22, 163, 74, 110))
        shadow.setOffset(0, 16)
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # --- Dải header gradient, giả lập "đầu vé tàu" ---
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #16A34A, stop:1 #22C55E);
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 16, 0, 0)
        badge_row = QHBoxLayout()
        badge_row.addStretch()
        badge_row.addWidget(_IconBadge("success", size=58))
        badge_row.addStretch()
        header_layout.addLayout(badge_row)
        card_layout.addWidget(header)

        # --- Phần nội dung, có lề riêng để không phá vỡ bo góc của header ---
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 14, 24, 22)
        content_layout.setSpacing(14)

        title = QLabel("Mua vé thành công!")
        title.setStyleSheet("font-size:16px; font-weight:700; color:#14532D;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

        # Khung chứa QR, viền nét đứt giả lập đường xé vé
        qr_box = QFrame()
        qr_box.setStyleSheet("""
            background-color: #F0FDF4;
            border: 1.5px dashed #86EFAC;
            border-radius: 14px;
        """)
        qr_layout = QVBoxLayout(qr_box)
        qr_layout.setContentsMargins(18, 18, 18, 14)
        qr_layout.setSpacing(8)

        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_label.setFixedSize(180, 180)

        if _QRCODE_AVAILABLE:
            qr_label.setPixmap(self._build_qr_pixmap(qr_text, box_size=180))
        else:
            # Chưa cài thư viện qrcode -> hiện chữ thay vì lỗi crash
            qr_label.setStyleSheet("""
                background-color:#FFFFFF; border:1px solid #BBF7D0; border-radius:10px;
                font-family: Consolas; font-size:11px; color:#166534; padding:6px;
            """)
            qr_label.setWordWrap(True)
            qr_label.setText(f"[Cần cài: pip install qrcode pillow]\n\n{qr_text}")

        qr_row = QHBoxLayout()
        qr_row.addStretch()
        qr_row.addWidget(qr_label)
        qr_row.addStretch()
        qr_layout.addLayout(qr_row)

        code_lbl = QLabel(qr_text)
        code_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_lbl.setStyleSheet("font-size:11px; color:#16A34A; font-weight:600;")
        qr_layout.addWidget(code_lbl)

        content_layout.addWidget(qr_box)

        info_box = QFrame()
        info_box.setStyleSheet("background-color:#F8FAFC; border-radius:12px;")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setSpacing(8)

        info_layout.addLayout(self._make_row("Loại vé", type_name))
        if detail_text:
            info_layout.addLayout(self._make_row("Hành trình", detail_text))
        if train_time:  # SỬA: dòng riêng cho giờ chuyến tàu, chỉ hiện khi là vé lượt
            info_layout.addLayout(self._make_row("Chuyến tàu", train_time))
        info_layout.addLayout(self._make_row("Số tiền", amount_text))
        content_layout.addWidget(info_box)

        btn_close = QPushButton("Đóng")
        btn_close.setMinimumHeight(42)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color:#16A34A; color:white;
                border-radius:10px; font-weight:700; font-size:13px;
            }
            QPushButton:hover { background-color:#15803D; }
        """)
        btn_close.clicked.connect(self.accept)
        content_layout.addWidget(btn_close)

        card_layout.addWidget(content)

    def _build_qr_pixmap(self, text, box_size=180):
        qr = qrcode.QRCode(border=1, box_size=8)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#14532D", back_color="white").convert("RGB")
        img = img.resize((box_size, box_size))
        data = img.tobytes("raw", "RGB")
        qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qimg)

    def _make_row(self, label_text, value_text):
        """SỬA: bật word wrap + canh phải cho value, tránh bị cắt chữ khi text dài
        (VD: hành trình vé lượt có thêm giờ chuyến tàu)."""
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color:#16A34A; font-size:12px;")
        lbl.setFixedWidth(80)  # SỬA: cố định bề rộng nhãn để value có đủ chỗ còn lại

        val = QLabel(value_text)
        val.setStyleSheet("color:#14532D; font-size:12px; font-weight:700;")
        val.setWordWrap(True)  # SỬA: cho phép xuống dòng thay vì tràn/cắt chữ
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(lbl)
        row.addWidget(val, stretch=1)  # SỬA: value chiếm hết phần còn lại thay vì addStretch()
        return row

    def showEvent(self, event):
        super().showEvent(event)
        self._play_entrance_animation()