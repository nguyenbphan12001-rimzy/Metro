from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath


class SuccessToast(QWidget):
    """
    Popup tự vẽ thay cho QMessageBox mặc định:
    - Khung bo góc, nền trắng, có bóng đổ nhẹ
    - Dấu tích xanh trong vòng tròn ở giữa
    - Chữ thông báo phía dưới
    - Hiệu ứng mờ dần -> rõ dần khi xuất hiện, tự đóng sau vài giây
    """

    def __init__(self, parent_window, message="Đăng nhập thành công!", duration_ms=1800):
        # Không dùng parent thật vì cần nó nổi độc lập, tự vẽ nền trong suốt được
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._parent_window = parent_window
        self._message = message
        self._duration_ms = duration_ms

        self._box_w, self._box_h = 280, 200
        self.resize(self._box_w, self._box_h)

        self._build_ui()
        self._center_on_parent()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        # chừa khoảng trống phía trên cho vòng tròn tích được paintEvent vẽ riêng
        layout.setContentsMargins(0, 120, 0, 20)

        self.lbl_text = QLabel(self._message)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_text.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.lbl_text.setStyleSheet("color: #1E5631; background: transparent;")
        layout.addWidget(self.lbl_text)

    def _center_on_parent(self):
        if self._parent_window is not None:
            geo = self._parent_window.geometry()
            x = geo.x() + (geo.width() - self._box_w) // 2
            y = geo.y() + (geo.height() - self._box_h) // 2
        else:
            x, y = 400, 300
        self.move(x, y)

    # ------------------------------------------------------------------
    # Vẽ nền bo góc + bóng đổ + vòng tròn dấu tích
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(8, 8, self.width() - 16, self.height() - 16)

        # Bóng đổ mềm (vẽ vài lớp viền mờ dần ra ngoài)
        for i in range(8, 0, -1):
            shadow_rect = rect.adjusted(-i, -i, i, i)
            alpha = int(6 * (8 - i))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(10, 77, 122, alpha)))
            painter.drawRoundedRect(shadow_rect, 24, 24)

        # Nền trắng bo góc chính
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(230, 230, 230), 1))
        painter.drawRoundedRect(rect, 24, 24)

        # Vòng tròn xanh + dấu tích, đặt giữa phần trên khung
        circle_d = 72
        cx = rect.center().x()
        cy = rect.y() + 30 + circle_d / 2
        circle_rect = QRectF(cx - circle_d / 2, cy - circle_d / 2, circle_d, circle_d)

        painter.setBrush(QBrush(QColor(39, 174, 96)))  # xanh lá
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(circle_rect)

        # Dấu tích vẽ bằng path, dày, đầu bo tròn
        path = QPainterPath()
        path.moveTo(cx - 18, cy + 2)
        path.lineTo(cx - 5, cy + 16)
        path.lineTo(cx + 20, cy - 16)

        pen = QPen(QColor(255, 255, 255), 6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        painter.end()

    # ------------------------------------------------------------------
    # Hiệu ứng hiển thị: mờ dần -> rõ dần, rồi tự ẩn sau duration_ms
    # ------------------------------------------------------------------
    def show_animated(self):
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.0)

        self.show()

        self.anim_in = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self.anim_in.setDuration(400)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_in.start()

        # Sau khi hiện đủ lâu thì tự mờ dần đi rồi đóng
        QTimer.singleShot(self._duration_ms, self._fade_out)

    def _fade_out(self):
        self.anim_out = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self.anim_out.setDuration(350)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim_out.finished.connect(self.close)
        self.anim_out.start()
