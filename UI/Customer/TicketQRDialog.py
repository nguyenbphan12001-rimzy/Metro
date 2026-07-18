import os
import json
import smtplib
import tempfile
from email.message import EmailMessage

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QParallelAnimationGroup
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QGraphicsDropShadowEffect, QMessageBox, QApplication
)
from UI.Customer.StyledDialogs import StatusDialog
from App.DB_Connection import get_connection  # SỬA: cần để xử lý nghiệp vụ hoàn vé

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# EmailInputDialog — Dialog nhập email thay cho QInputDialog mặc định, đồng bộ
# theme xanh dương + có animation pop-up/đóng giống TicketQRDialog.
# ══════════════════════════════════════════════════════════════════════════════
class EmailInputDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self._closing = False
        self._already_animated_in = False
        self.email_result = None  # SỬA: nơi lưu email sau khi người dùng bấm Gửi

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(320)

        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border-radius: 18px; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(13, 31, 60, 90))
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(0)

        # ── Icon tròn + tiêu đề ──
        icon_wrap = QLabel("✉")
        icon_wrap.setFixedSize(48, 48)
        icon_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_wrap.setStyleSheet("""
            background-color: #E0F2FE; color: #0284C7;
            border-radius: 24px; font-size: 20px;
        """)
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_wrap)
        icon_row.addStretch()
        layout.addLayout(icon_row)

        lbl_title = QLabel("Gửi vé qua Email")
        lbl_title.setStyleSheet("color:#0C4A6E; font-size:16px; font-weight:800; margin-top:14px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Vé sẽ được gửi đến địa chỉ email của bạn")
        lbl_sub.setStyleSheet("color:#94A3B8; font-size:12px; margin-top:4px; margin-bottom:18px;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        # ── Ô nhập email ──
        self.inputEmail = QLineEdit()
        self.inputEmail.setPlaceholderText("vidu@gmail.com")
        self.inputEmail.setFixedHeight(44)
        self.inputEmail.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 13px;
                color: #0C4A6E;
            }
            QLineEdit:focus {
                border: 1.5px solid #0EA5E9;
                background-color: #FFFFFF;
            }
        """)
        self.inputEmail.returnPressed.connect(self._on_confirm)
        layout.addWidget(self.inputEmail)

        self.lblError = QLabel("")
        self.lblError.setStyleSheet("color:#EF4444; font-size:11px; margin-top:6px;")
        self.lblError.setVisible(False)
        layout.addWidget(self.lblError)

        # ── Nút hành động ──
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 18, 0, 0)
        btn_row.setSpacing(10)

        self.btnCancel = QPushButton("Hủy")
        self.btnCancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnCancel.setFixedHeight(42)
        self.btnCancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9; color: #64748B;
                border-radius: 10px; font-size: 13px; font-weight: 700;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        self.btnCancel.clicked.connect(self._animate_close)
        btn_row.addWidget(self.btnCancel)

        self.btnConfirm = QPushButton("Gửi  ↗")
        self.btnConfirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnConfirm.setFixedHeight(42)
        self.btnConfirm.setStyleSheet("""
            QPushButton {
                background-color: #0284C7; color: white;
                border-radius: 10px; font-size: 13px; font-weight: 700;
            }
            QPushButton:hover { background-color: #0369A1; }
        """)
        self.btnConfirm.clicked.connect(self._on_confirm)
        btn_row.addWidget(self.btnConfirm)

        layout.addLayout(btn_row)

        self.inputEmail.setFocus()

    def _on_confirm(self):
        email = self.inputEmail.text().strip()
        if "@" not in email or "." not in email.split("@")[-1]:
            self.lblError.setText("Email không hợp lệ, vui lòng kiểm tra lại.")
            self.lblError.setVisible(True)
            self.inputEmail.setStyleSheet(self.inputEmail.styleSheet().replace("#E2E8F0", "#FCA5A5"))
            return
        self.email_result = email
        self._animate_close()

    # ── Animation pop-up / đóng — dùng chung pattern với TicketQRDialog ────
    def showEvent(self, event):
        super().showEvent(event)
        if self._already_animated_in:
            return
        self._already_animated_in = True

        final_rect = self.geometry()
        cx, cy = final_rect.center().x(), final_rect.center().y()
        shrink_w, shrink_h = int(final_rect.width() * 0.9), int(final_rect.height() * 0.9)
        start_rect = QRect(cx - shrink_w // 2, cy - shrink_h // 2, shrink_w, shrink_h)

        self.setWindowOpacity(0.0)
        self.setGeometry(start_rect)

        self._anim_in_geo = QPropertyAnimation(self, b"geometry")
        self._anim_in_geo.setDuration(240)
        self._anim_in_geo.setStartValue(start_rect)
        self._anim_in_geo.setEndValue(final_rect)
        self._anim_in_geo.setEasingCurve(QEasingCurve.Type.OutBack)

        self._anim_in_opacity = QPropertyAnimation(self, b"windowOpacity")
        self._anim_in_opacity.setDuration(180)
        self._anim_in_opacity.setStartValue(0.0)
        self._anim_in_opacity.setEndValue(1.0)
        self._anim_in_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_in_group = QParallelAnimationGroup()
        self._anim_in_group.addAnimation(self._anim_in_geo)
        self._anim_in_group.addAnimation(self._anim_in_opacity)
        self._anim_in_group.start()

    def _animate_close(self):
        if self._closing:
            return
        self._closing = True

        current_rect = self.geometry()
        cx, cy = current_rect.center().x(), current_rect.center().y()
        shrink_w, shrink_h = int(current_rect.width() * 0.9), int(current_rect.height() * 0.9)
        end_rect = QRect(cx - shrink_w // 2, cy - shrink_h // 2, shrink_w, shrink_h)

        self._anim_out_geo = QPropertyAnimation(self, b"geometry")
        self._anim_out_geo.setDuration(160)
        self._anim_out_geo.setStartValue(current_rect)
        self._anim_out_geo.setEndValue(end_rect)
        self._anim_out_geo.setEasingCurve(QEasingCurve.Type.InCubic)

        self._anim_out_opacity = QPropertyAnimation(self, b"windowOpacity")
        self._anim_out_opacity.setDuration(160)
        self._anim_out_opacity.setStartValue(1.0)
        self._anim_out_opacity.setEndValue(0.0)
        self._anim_out_opacity.setEasingCurve(QEasingCurve.Type.InCubic)

        self._anim_out_group = QParallelAnimationGroup()
        self._anim_out_group.addAnimation(self._anim_out_geo)
        self._anim_out_group.addAnimation(self._anim_out_opacity)
        self._anim_out_group.finished.connect(self.accept)
        self._anim_out_group.start()



# thành công" bên Thanhtoan_EX — dialog này theme xanh dương, không có icon ✓
# màu xanh lá để tránh nhầm lẫn là vừa thanh toán xong).
# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# ConfirmRefundDialog — SỬA: dialog xác nhận hoàn vé (2 nút Hủy / Xác nhận),
# dùng pattern animation giống EmailInputDialog, theme cam (cảnh báo nhẹ).
# ══════════════════════════════════════════════════════════════════════════════
class ConfirmRefundDialog(QDialog):
    def __init__(self, parent, amount_text):
        super().__init__(parent)
        self._closing = False
        self._already_animated_in = False
        self.confirmed = False

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(320)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 18px; }")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(13, 31, 60, 90))
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(0)

        icon_wrap = QLabel("↩")
        icon_wrap.setFixedSize(48, 48)
        icon_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_wrap.setStyleSheet("""
            background-color: #FFEDD5; color: #EA580C;
            border-radius: 24px; font-size: 20px; font-weight: 800;
        """)
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_wrap)
        icon_row.addStretch()
        layout.addLayout(icon_row)

        lbl_title = QLabel("Xác nhận hoàn vé?")
        lbl_title.setStyleSheet("color:#0C4A6E; font-size:16px; font-weight:800; margin-top:14px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel(f"Vé sẽ bị hủy và {amount_text} sẽ được hoàn lại vào ví của bạn.")
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet("color:#94A3B8; font-size:12px; margin-top:6px;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 18, 0, 0)
        btn_row.setSpacing(10)

        self.btnCancel = QPushButton("Để sau")
        self.btnCancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnCancel.setFixedHeight(42)
        self.btnCancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9; color: #64748B;
                border-radius: 10px; font-size: 13px; font-weight: 700;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        self.btnCancel.clicked.connect(self._animate_close)
        btn_row.addWidget(self.btnCancel)

        self.btnConfirm = QPushButton("Hoàn vé")
        self.btnConfirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnConfirm.setFixedHeight(42)
        self.btnConfirm.setStyleSheet("""
            QPushButton {
                background-color: #EA580C; color: white;
                border-radius: 10px; font-size: 13px; font-weight: 700;
            }
            QPushButton:hover { background-color: #C2410C; }
        """)
        self.btnConfirm.clicked.connect(self._on_confirm)
        btn_row.addWidget(self.btnConfirm)

        layout.addLayout(btn_row)

    def _on_confirm(self):
        self.confirmed = True
        self._animate_close()

    def showEvent(self, event):
        super().showEvent(event)
        if self._already_animated_in:
            return
        self._already_animated_in = True

        final_rect = self.geometry()
        cx, cy = final_rect.center().x(), final_rect.center().y()
        shrink_w, shrink_h = int(final_rect.width() * 0.9), int(final_rect.height() * 0.9)
        start_rect = QRect(cx - shrink_w // 2, cy - shrink_h // 2, shrink_w, shrink_h)

        self.setWindowOpacity(0.0)
        self.setGeometry(start_rect)

        self._anim_in_geo = QPropertyAnimation(self, b"geometry")
        self._anim_in_geo.setDuration(240)
        self._anim_in_geo.setStartValue(start_rect)
        self._anim_in_geo.setEndValue(final_rect)
        self._anim_in_geo.setEasingCurve(QEasingCurve.Type.OutBack)

        self._anim_in_opacity = QPropertyAnimation(self, b"windowOpacity")
        self._anim_in_opacity.setDuration(180)
        self._anim_in_opacity.setStartValue(0.0)
        self._anim_in_opacity.setEndValue(1.0)
        self._anim_in_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_in_group = QParallelAnimationGroup()
        self._anim_in_group.addAnimation(self._anim_in_geo)
        self._anim_in_group.addAnimation(self._anim_in_opacity)
        self._anim_in_group.start()

    def _animate_close(self):
        if self._closing:
            return
        self._closing = True

        current_rect = self.geometry()
        cx, cy = current_rect.center().x(), current_rect.center().y()
        shrink_w, shrink_h = int(current_rect.width() * 0.9), int(current_rect.height() * 0.9)
        end_rect = QRect(cx - shrink_w // 2, cy - shrink_h // 2, shrink_w, shrink_h)

        self._anim_out_geo = QPropertyAnimation(self, b"geometry")
        self._anim_out_geo.setDuration(160)
        self._anim_out_geo.setStartValue(current_rect)
        self._anim_out_geo.setEndValue(end_rect)
        self._anim_out_geo.setEasingCurve(QEasingCurve.Type.InCubic)

        self._anim_out_opacity = QPropertyAnimation(self, b"windowOpacity")
        self._anim_out_opacity.setDuration(160)
        self._anim_out_opacity.setStartValue(1.0)
        self._anim_out_opacity.setEndValue(0.0)
        self._anim_out_opacity.setEasingCurve(QEasingCurve.Type.InCubic)

        self._anim_out_group = QParallelAnimationGroup()
        self._anim_out_group.addAnimation(self._anim_out_geo)
        self._anim_out_group.addAnimation(self._anim_out_opacity)
        self._anim_out_group.finished.connect(self.accept)
        self._anim_out_group.start()


class TicketQRDialog(QDialog):
    def __init__(self, parent, ticket: dict, on_refunded=None):
        super().__init__(parent)
        self.ticket = ticket
        self._qr_temp_path = None
        self._closing = False  # SỬA: cờ tránh bấm Đóng nhiều lần khi đang animate
        self.on_refunded = on_refunded  # SỬA: callback để VeCuaToi_EX refresh lại list sau khi hoàn vé thành công

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(360)

        self._build_ui()
        self._generate_qr()

    # ── Xây UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(13, 31, 60, 90))
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(0)

        # ── Header xanh dương (KHÁC màu xanh lá "thành công") ──
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet("""
            background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #0D1F3C, stop:1 #0284C7
            );
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
        """)
        header_layout = QVBoxLayout(header)

        # SỬA: hàng trên cùng chứa nút X để đóng dialog mà không cần hoàn vé
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.addStretch()
        self.btnCloseX = QPushButton("✕")
        self.btnCloseX.setFixedSize(28, 28)
        self.btnCloseX.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnCloseX.setStyleSheet("""
            QPushButton {
                color: #FFFFFF; font-size: 13px; font-weight: 800;
                background-color: rgba(255,255,255,0.18); border-radius: 14px;
                border: none;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.32); }
        """)
        self.btnCloseX.clicked.connect(self._animate_close)
        top_row.addWidget(self.btnCloseX)
        header_layout.addLayout(top_row)

        lbl_icon = QLabel("🎫")
        lbl_icon.setStyleSheet("font-size: 30px; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(lbl_icon)
        layout.addWidget(header)

        lbl_title = QLabel("Mã QR vé của bạn")
        lbl_title.setStyleSheet("color:#0C4A6E; font-size:17px; font-weight:800; margin-top:14px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Xuất trình mã này tại cổng soát vé")
        lbl_sub.setStyleSheet("color:#7DD3FC; font-size:12px; margin-bottom:14px;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        # ── Khung QR ──
        qr_box = QFrame()
        qr_box.setStyleSheet("""
            background-color: #F0F9FF;
            border: 1.5px dashed #7DD3FC;
            border-radius: 14px;
        """)
        qr_layout = QVBoxLayout(qr_box)
        qr_layout.setContentsMargins(16, 16, 16, 12)

        self.qrLabel = QLabel("Đang tạo mã QR...")
        self.qrLabel.setFixedSize(200, 200)
        self.qrLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qrLabel.setStyleSheet("color:#0284C7; font-size:12px; background: transparent;")
        qr_layout.addWidget(self.qrLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        lbl_code = QLabel(self.ticket.get("qr_code", ""))
        lbl_code.setStyleSheet("color:#0369A1; font-size:11px; font-weight:600; background: transparent;")
        lbl_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_layout.addWidget(lbl_code)

        wrap = QHBoxLayout()
        wrap.setContentsMargins(20, 16, 20, 0)
        wrap.addWidget(qr_box)
        layout.addLayout(wrap)

        # ── Thông tin vé ──
        info_box = QFrame()
        info_box.setStyleSheet("background: transparent;")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(24, 16, 24, 0)
        info_layout.setSpacing(8)

        info_layout.addLayout(self._make_row("Loại vé", self.ticket.get("type_name", "")))

        from_s = self.ticket.get("from_station")
        to_s = self.ticket.get("to_station")
        route_text = f"{from_s} → {to_s}" if from_s and to_s else "Không giới hạn ga"
        info_layout.addLayout(self._make_row("Hành trình", route_text))

        price = self.ticket.get("price", 0)
        price_text = f"{price:,.0f} VNĐ".replace(",", ".")
        info_layout.addLayout(self._make_row("Số tiền", price_text, value_color="#0284C7"))

        layout.addWidget(info_box)

        # ── Nút hành động ──
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(24, 18, 24, 0)
        btn_row.setSpacing(10)

        self.btnEmail = QPushButton("✉  Gửi Email")
        self.btnEmail.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnEmail.setFixedHeight(42)
        self.btnEmail.setStyleSheet("""
            QPushButton {
                background-color: #E0F2FE; color: #0284C7;
                border-radius: 10px; font-size: 13px; font-weight: 700;
            }
            QPushButton:hover { background-color: #BAE6FD; }
        """)
        self.btnEmail.clicked.connect(self.on_send_gmail)
        btn_row.addWidget(self.btnEmail)

        self.btnClose = QPushButton()
        self.btnClose.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnClose.setFixedHeight(42)

        # SỬA: chỉ cho hoàn vé khi vé còn hiệu lực (UNUSED). Vé đã quét (USED)
        # hoặc đã hết hạn (EXPIRED) thì nút chỉ còn tác dụng đóng dialog.
        status = (self.ticket.get("status") or "").upper()
        if status == "UNUSED":
            self.btnClose.setText("↩  Hoàn vé")
            self.btnClose.setStyleSheet("""
                QPushButton {
                    background-color: #FFEDD5; color: #C2410C;
                    border-radius: 10px; font-size: 13px; font-weight: 700;
                }
                QPushButton:hover { background-color: #FED7AA; }
            """)
            self.btnClose.clicked.connect(self.handle_refund)
        else:
            self.btnClose.setText("Đóng")
            self.btnClose.setStyleSheet("""
                QPushButton {
                    background-color: #0284C7; color: white;
                    border-radius: 10px; font-size: 13px; font-weight: 700;
                }
                QPushButton:hover { background-color: #0369A1; }
            """)
            self.btnClose.clicked.connect(self._animate_close)
        btn_row.addWidget(self.btnClose)

        layout.addLayout(btn_row)

    def _make_row(self, label_text, value_text, value_color="#0C4A6E"):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color:#94A3B8; font-size:12px; background: transparent;")
        row.addWidget(lbl)
        row.addStretch()
        val = QLabel(value_text)
        val.setStyleSheet(f"color:{value_color}; font-size:13px; font-weight:700; background: transparent;")
        row.addWidget(val)
        return row

    # ── Hiệu ứng pop-up khi dialog xuất hiện (fade + scale từ 92% → 100%) ────
    def showEvent(self, event):
        super().showEvent(event)
        if getattr(self, "_already_animated_in", False):
            return
        self._already_animated_in = True

        final_rect = self.geometry()
        cx, cy = final_rect.center().x(), final_rect.center().y()
        shrink_w, shrink_h = int(final_rect.width() * 0.92), int(final_rect.height() * 0.92)
        start_rect = QRect(
            cx - shrink_w // 2, cy - shrink_h // 2, shrink_w, shrink_h
        )

        self.setWindowOpacity(0.0)
        self.setGeometry(start_rect)

        self._anim_in_geo = QPropertyAnimation(self, b"geometry")
        self._anim_in_geo.setDuration(260)
        self._anim_in_geo.setStartValue(start_rect)
        self._anim_in_geo.setEndValue(final_rect)
        self._anim_in_geo.setEasingCurve(QEasingCurve.Type.OutBack)

        self._anim_in_opacity = QPropertyAnimation(self, b"windowOpacity")
        self._anim_in_opacity.setDuration(200)
        self._anim_in_opacity.setStartValue(0.0)
        self._anim_in_opacity.setEndValue(1.0)
        self._anim_in_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_in_group = QParallelAnimationGroup()
        self._anim_in_group.addAnimation(self._anim_in_geo)
        self._anim_in_group.addAnimation(self._anim_in_opacity)
        self._anim_in_group.start()

    # ── Hiệu ứng đóng (fade + scale xuống 92%) trước khi accept() thật ───────
    def _animate_close(self):
        if self._closing:
            return  # SỬA: chặn double-click bấm Đóng liên tục khi đang animate
        self._closing = True

        current_rect = self.geometry()
        cx, cy = current_rect.center().x(), current_rect.center().y()
        shrink_w, shrink_h = int(current_rect.width() * 0.92), int(current_rect.height() * 0.92)
        end_rect = QRect(
            cx - shrink_w // 2, cy - shrink_h // 2, shrink_w, shrink_h
        )

        self._anim_out_geo = QPropertyAnimation(self, b"geometry")
        self._anim_out_geo.setDuration(180)
        self._anim_out_geo.setStartValue(current_rect)
        self._anim_out_geo.setEndValue(end_rect)
        self._anim_out_geo.setEasingCurve(QEasingCurve.Type.InCubic)

        self._anim_out_opacity = QPropertyAnimation(self, b"windowOpacity")
        self._anim_out_opacity.setDuration(180)
        self._anim_out_opacity.setStartValue(1.0)
        self._anim_out_opacity.setEndValue(0.0)
        self._anim_out_opacity.setEasingCurve(QEasingCurve.Type.InCubic)

        self._anim_out_group = QParallelAnimationGroup()
        self._anim_out_group.addAnimation(self._anim_out_geo)
        self._anim_out_group.addAnimation(self._anim_out_opacity)
        self._anim_out_group.finished.connect(self.accept)  # SỬA: animate xong mới thật sự đóng dialog
        self._anim_out_group.start()
    # ── Hoàn vé — SỬA: nghiệp vụ mới thay cho nút Đóng khi vé còn UNUSED ────
    def handle_refund(self):
        price = self.ticket.get("price", 0)
        price_text = f"{price:,.0f} VNĐ".replace(",", ".")

        confirm_dlg = ConfirmRefundDialog(self, price_text)
        confirm_dlg.exec()
        if not confirm_dlg.confirmed:
            return

        ticket_id = self.ticket.get("ticket_id")
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # SỬA: lock + re-check trạng thái mới nhất ngay trước khi hoàn,
            # tránh trường hợp vé vừa bị quét (USED) trong lúc dialog đang mở
            # SỬA: lấy thêm type_id vì cần biết đây có phải vé lượt hay không
            cursor.execute("SELECT status, user_id, price, type_id FROM TICKET WHERE ticket_id = ?", (ticket_id,))
            row = cursor.fetchone()
            if not row or row[0] != "UNUSED":
                conn.close()
                self._show_status("error", "Không thể hoàn vé", "Vé đã được sử dụng hoặc không còn tồn tại.")
                return

            _, user_id, real_price, type_id = row

            # SỬA: vé ngày/tháng (type_id != 1) không đổi status khi quét qua cổng
            # (status vẫn UNUSED dù đã scan), nên phải check riêng SCANNING_HISTORY.
            # Chỉ cần có 1 lượt quét (IN) là khóa hoàn vé, bất kể status vẫn hiện UNUSED.
            if type_id != 1:
                cursor.execute(
                    "SELECT COUNT(*) FROM SCANNING_HISTORY WHERE ticket_id = ?", (ticket_id,)
                )
                scan_count = cursor.fetchone()[0]
                if scan_count > 0:
                    conn.close()
                    self._show_status(
                        "error", "Không thể hoàn vé",
                        "Vé này đã được sử dụng (đã quét qua cổng soát vé), không thể hoàn tiền."
                    )
                    return

            cursor.execute("SELECT wallet_id FROM WALLET WHERE user_id = ?", (user_id,))
            wallet_row = cursor.fetchone()
            if not wallet_row:
                conn.close()
                self._show_status("error", "Không thể hoàn vé", "Không tìm thấy ví điện tử của khách hàng.")
                return
            wallet_id = wallet_row[0]

            # PK thủ công (không có IDENTITY) — theo đúng pattern toàn dự án
            cursor.execute("SELECT ISNULL(MAX(refund_id), 0) + 1 FROM REFUNDS")
            next_refund_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO REFUNDS (refund_id, ticket_id, wallet_id, amount) VALUES (?, ?, ?, ?)",
                (next_refund_id, ticket_id, wallet_id, real_price)
            )
            # SỬA: KHÔNG tự UPDATE WALLET.balance ở đây — để trigger trg_after_refund
            # (AFTER INSERT trên REFUNDS) tự cộng tiền lại vào ví, đúng pattern của dự án.
            # Lưu ý: nếu DB hiện tại chưa có trigger này thì cần tạo thêm, xem ghi chú bên dưới.

            # SỬA: schema TICKET.status hiện chỉ CHECK IN ('UNUSED','USED','EXPIRED'),
            # chưa có 'CANCELLED' nên tạm dùng 'EXPIRED' để đánh dấu vé không còn dùng được.
            # Nếu muốn phân biệt rõ "hết hạn tự nhiên" và "bị hủy hoàn tiền", nên ALTER
            # CHECK constraint để thêm 'CANCELLED' rồi đổi dòng dưới thành 'CANCELLED'.
            cursor.execute("UPDATE TICKET SET status = 'EXPIRED' WHERE ticket_id = ?", (ticket_id,))

            conn.commit()
            conn.close()

            self.ticket["status"] = "EXPIRED"

            if callable(self.on_refunded):
                self.on_refunded(ticket_id)

            self._show_status("success", "Hoàn vé thành công!", f"Đã hoàn {price_text} vào ví của bạn.")
            self._animate_close()

        except Exception as e:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            self._show_status("error", "Lỗi hoàn vé", f"Không thể xử lý hoàn vé:\n{str(e)}")

    def _show_status(self, kind, title, message):
        dlg = StatusDialog(self, title=title, message=message, kind=kind, ok_text="Đã hiểu")
        dlg.exec()

    def _generate_qr(self):
        if not QR_AVAILABLE:
            self.qrLabel.setText("⚠ Cần cài:\npip install qrcode[pil]")
            return

        t = self.ticket
        payload = json.dumps({
            "ticket_id": t.get("ticket_id"),
            "qr_code": t.get("qr_code"),
            "type_name": t.get("type_name"),
            "from_station": t.get("from_station"),
            "to_station": t.get("to_station"),
            "price": t.get("price"),
        }, ensure_ascii=False, separators=(",", ":"))

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(payload)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0284C7", back_color="white")

            safe_id = str(t.get("qr_code", "ticket")).replace("-", "").replace("/", "").replace(" ", "")
            self._qr_temp_path = os.path.join(tempfile.gettempdir(), f"metro_qr_view_{safe_id}.png")
            img.save(self._qr_temp_path)

            pixmap = QPixmap(self._qr_temp_path)
            scaled = pixmap.scaled(
                200, 200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.qrLabel.setPixmap(scaled)
            self.qrLabel.setText("")
        except Exception as e:
            self.qrLabel.setText(f"Lỗi tạo QR:\n{e}")

    # ── Gửi email — logic lấy lại từ QR_EX.on_send_gmail ───────────────────
    def on_send_gmail(self):
        email_dlg = EmailInputDialog(self)
        email_dlg.exec()
        email_nhan = email_dlg.email_result

        if not email_nhan:
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            EMAIL_GUI = "metro.hcmc.project@gmail.com"
            MAT_KHAU_APP = "guqsgnvweftsxwbf"

            t = self.ticket
            from_s = t.get("from_station")
            to_s = t.get("to_station")
            route_text = f"{from_s} → {to_s}" if from_s and to_s else "Không giới hạn ga"
            price_text = f"{t.get('price', 0):,.0f} VNĐ".replace(",", ".")

            msg = EmailMessage()
            msg["Subject"] = f"[Metro HCMC] Thông tin vé #{t.get('qr_code')}"
            msg["From"] = EMAIL_GUI
            msg["To"] = email_nhan.strip()

            body = f"""THÔNG TIN VÉ TÀU METRO HỒ CHÍ MINH
    ==========================================

    Mã vé       :  {t.get('qr_code')}
    Loại vé     :  {t.get('type_name')}
    Hành trình  :  {route_text}
    Giá vé      :  {price_text}
    Trạng thái  :  {t.get('status')}

    ==========================================
    Vui lòng xuất trình vé khi lên/xuống tàu.
    Metro TP.HCM
    """
            msg.set_content(body)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_GUI, MAT_KHAU_APP)
            server.send_message(msg)
            server.quit()

            QApplication.restoreOverrideCursor()

            # SỬA: thay QMessageBox.information bằng StatusDialog đồng bộ theme
            dlg = StatusDialog(
                self,
                title="Gửi vé thành công!",
                message=f"Đã gửi vé thành công tới:\n{email_nhan}",
                kind="success",
                ok_text="Xác nhận"
            )
            dlg.exec()

        except Exception as e:
            QApplication.restoreOverrideCursor()

            # SỬA: thay QMessageBox.critical bằng StatusDialog đồng bộ theme
            dlg = StatusDialog(
                self,
                title="Lỗi gửi Email",
                message=f"Không thể gửi email.\nChi tiết: {str(e)}",
                kind="error",
                ok_text="Đã hiểu"
            )
            dlg.exec()