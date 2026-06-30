# UI/Customer/ErrorToast.py
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QFont


class ErrorToast(QWidget):
    def __init__(self, parent, message="Đã xảy ra lỗi"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._radius = 16
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 22, 0)
        layout.setSpacing(10)

        # Icon X
        icon = QLabel("✕")
        icon.setFixedSize(28, 28)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("""
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 800;
            background-color: rgba(255,255,255,0.22);
            border-radius: 14px;
        """)
        layout.addWidget(icon)

        # Message
        lbl = QLabel(message)
        lbl.setStyleSheet("""
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 600;
            background: transparent;
        """)
        font = QFont("Segoe UI", 10)
        font.setWeight(QFont.Weight.DemiBold)
        lbl.setFont(font)
        layout.addWidget(lbl)
        layout.addStretch()

        # Tính width theo text
        fm = lbl.fontMetrics()
        text_w = fm.horizontalAdvance(message)
        self.setFixedWidth(text_w + 110)

        # Đổ bóng nổi khối
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(220, 38, 38, 130))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self._radius, self._radius)

        # Gradient đỏ sang cam đậm
        from PyQt6.QtGui import QLinearGradient
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor(220, 38, 38))    # đỏ đậm
        grad.setColorAt(1.0, QColor(239, 68, 68))    # đỏ nhạt hơn

        from PyQt6.QtGui import QBrush
        painter.fillPath(path, QBrush(grad))

        # Viền mỏng trắng mờ để tăng độ nổi
        from PyQt6.QtGui import QPen
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawPath(path)

    def show_animated(self):
        parent_rect = self.parent().geometry()
        x = (parent_rect.width() - self.width()) // 2
        y_end = parent_rect.height() - self.height() - 28
        y_start = y_end + 20

        self.move(x, y_start)
        self.setWindowOpacity(0)
        self.show()
        self.raise_()

        self.anim_in = QPropertyAnimation(self, b"pos")
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(QPoint(x, y_start))
        self.anim_in.setEndValue(QPoint(x, y_end))
        self.anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(300)
        self.anim_opacity.setStartValue(0.0)
        self.anim_opacity.setEndValue(1.0)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_in.start()
        self.anim_opacity.start()

        # Tự fade out sau 2.5s
        QTimer.singleShot(2500, self._fade_out)

    def _fade_out(self):
        self.anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out.setDuration(350)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim_out.finished.connect(self.deleteLater)
        self.anim_out.start()