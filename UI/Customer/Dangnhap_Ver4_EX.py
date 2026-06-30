from PyQt6.QtWidgets import (
    QMessageBox, QMainWindow, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QRect, QRectF, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient

from UI.Customer.Dangky_Ver2_EX import Dangky_Ver2_EX

from MyCollection.auth import login

from UI.Customer.Dangnhap_Ver4 import Ui_LoginWindow_Ver4
from UI.Customer.KhachHang_Ver2_EX import KhachHang_Ver2_EX
from UI.Customer.QuenMatkhau_Ver3_EX import QuenMatKhau_Ver3_EX
from UI.Customer.SuccessToast import SuccessToast
from UI.Customer.ErrorToast import ErrorToast


class Dangnhap_Ver4_EX(Ui_LoginWindow_Ver4):
    def setupUi(self, MainWindow, conn):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.conn = conn

        self.btn_login.clicked.connect(self.handle_login)

        self._entrance_played = False
        self._install_watermark_background()
        self._install_entrance_animation()
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_forgot.clicked.connect(self.open_forgot_password_window)
        self.btn_register.clicked.connect(self.open_register_window)

    def handle_login(self):
        user_name = self.inp_username.text().strip()
        password = self.inp_password.text().strip()

        if not user_name or not password:
            self._error_toast = ErrorToast(self.MainWindow, "Vui lòng nhập đầy đủ thông tin!")
            self._error_toast.show_animated()
            return

        result = login(user_name, password)

        if result:
            self._toast = SuccessToast(self.MainWindow, f"Chào {result['user_name']}!")
            self._toast.show_animated()
            self._pending_user_id = result['user_id']
            self._toast.anim_in.finished.connect(self._delayed_open_wallet)
        else:
            self._error_toast = ErrorToast(self.MainWindow, "Tên đăng nhập hoặc mật khẩu không đúng!")
            self._error_toast.show_animated()


    def _delayed_open_wallet(self):
        QTimer.singleShot(900, lambda: self.open_wallet(self._pending_user_id))

    def open_register_window(self):
        self.register_window = QMainWindow()
        self.register_ui = Dangky_Ver2_EX()
        self.register_ui.setupUi(self.register_window, login_controller=self)
        self.register_window.show()
        self.MainWindow.hide()

    def open_forgot_password_window(self):
        self.forgot_window = QMainWindow()
        self.forgot_ui = QuenMatKhau_Ver3_EX()
        self.forgot_ui.setupUi(self.forgot_window, conn=self.conn, parent_window=self.MainWindow)
        self.forgot_ui.show_with_animation(self.forgot_window)
        self.MainWindow.hide()

    def open_wallet(self, user_id):
        from UI.Customer.KhachHang_Ver2_EX import KhachHang_Ver2_EX

        screen = self.MainWindow.screen().availableGeometry()
        self.wallet_window = QMainWindow()
        ui = KhachHang_Ver2_EX()
        ui.setupUi(self.wallet_window, user_id, self.conn)

        w, h = 440, min(680, screen.height() - 40)
        self.wallet_window.resize(w, h)
        self.wallet_window.move(
            screen.x() + (screen.width() - w) // 2,
            screen.y() + (screen.height() - h) // 2
        )

        # Gọi animation từ KhachHang_Ver2_EX thay vì show() thẳng
        ui.show_with_animation(self.wallet_window)
        self.MainWindow.close()



    # =========================================================
    # WATERMARK
    # =========================================================
    def _install_watermark_background(self):
        import os
        from PyQt6.QtGui import QPixmap

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(BASE_DIR, "..", "..", "image", "Metro_background0.jpg")
        self._bg_pixmap = QPixmap(image_path)

        original_paint_event = self.centralwidget.paintEvent

        def paint_event(event):
            original_paint_event(event)
            painter = QPainter(self.centralwidget)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(
                QPainter.RenderHint.SmoothPixmapTransform)  # SỬA: ép smooth khi vẽ, không chỉ khi scale

            if not self._bg_pixmap.isNull():
                rect = self.centralwidget.rect()

                # SỬA: nhân theo devicePixelRatio để scale đúng số pixel thật trên màn hình,
                # tránh việc Qt phải nội suy thêm 1 lớp nữa gây mờ trên màn hình DPI cao (125%/150%)
                dpr = self.centralwidget.devicePixelRatioF()
                target_w = int(rect.width() * dpr)
                target_h = int(rect.height() * dpr)

                scaled = self._bg_pixmap.scaled(
                    target_w, target_h,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                scaled.setDevicePixelRatio(dpr)  # SỬA: báo cho Qt biết đây là ảnh "nét" theo DPR này

                x = (scaled.width() / dpr - rect.width()) / 2
                y = (scaled.height() / dpr - rect.height()) / 2
                painter.drawPixmap(
                    QRectF(0, 0, rect.width(), rect.height()),
                    scaled,
                    QRectF(x * dpr, y * dpr, rect.width() * dpr, rect.height() * dpr)
                )

            painter.end()

        self.centralwidget.paintEvent = paint_event

    def _draw_rail_watermark(self, painter, rect):
        w, h = rect.width(), rect.height()

        glow = QRadialGradient(w * 0.5, h * 0.12, w * 0.45)
        glow.setColorAt(0.0, QColor(41, 182, 246, 70))
        glow.setColorAt(1.0, QColor(41, 182, 246, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QRectF(w * 0.05, -h * 0.05, w * 0.9, h * 0.35))

        track_color = QColor(10, 77, 122, 35)
        train_color = QColor(10, 77, 122, 45)

        rail_y = int(h * 0.78)
        painter.setPen(QPen(track_color, 3))
        painter.drawLine(0, rail_y, w, rail_y - 40)
        painter.drawLine(0, rail_y + 14, w, rail_y - 26)

        painter.setPen(QPen(track_color, 2))
        x = 0
        while x < w:
            y_top = rail_y - (x / w) * 40
            painter.drawLine(int(x), int(y_top - 6), int(x), int(y_top + 20))
            x += 36

        body = QRectF(w * 0.55, h * 0.12, w * 0.38, h * 0.16)
        painter.setBrush(QBrush(train_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(body, 18, 18)

        win_color = QColor(255, 255, 255, 60)
        painter.setBrush(QBrush(win_color))
        win_w = body.width() * 0.16
        win_h = body.height() * 0.45
        gap = body.width() * 0.05
        win_x = body.x() + gap
        win_y = body.y() + body.height() * 0.22
        for _ in range(4):
            painter.drawRoundedRect(QRectF(win_x, win_y, win_w, win_h), 4, 4)
            win_x += win_w + gap

        painter.setPen(QPen(track_color, 2))
        for i in range(3):
            yy = body.y() + body.height() * 0.3 + i * 10
            painter.drawLine(int(body.x() - 40 - i * 14), int(yy), int(body.x() - 10), int(yy))

    # =========================================================
    # ENTRANCE ANIMATION
    # =========================================================
    def _install_entrance_animation(self):
        original_show_event = self.MainWindow.showEvent

        def show_event(event):
            original_show_event(event)
            if not self._entrance_played:
                self._entrance_played = True
                self._animate_card_entrance()

        self.MainWindow.showEvent = show_event

    def _animate_card_entrance(self):
        final_geo = self.card.geometry()
        if final_geo.width() == 0 or final_geo.height() == 0:
            return

        self.root_layout.setEnabled(False)

        cx, cy = final_geo.center().x(), final_geo.center().y()
        shrink_w = int(final_geo.width() * 0.82)
        shrink_h = int(final_geo.height() * 0.82)
        start_geo = QRect(cx - shrink_w // 2, cy - shrink_h // 2, shrink_w, shrink_h)

        self._card_opacity_effect = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(self._card_opacity_effect)
        self._card_opacity_effect.setOpacity(0)
        self.card.setGeometry(start_geo)

        self.anim_fade = QPropertyAnimation(self._card_opacity_effect, b"opacity", self.MainWindow)
        self.anim_fade.setDuration(600)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        self.anim_fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_scale = QPropertyAnimation(self.card, b"geometry", self.MainWindow)
        self.anim_scale.setDuration(600)  # tăng từ 450 lên 900ms
        self.anim_scale.setStartValue(start_geo)
        self.anim_scale.setEndValue(final_geo)
        self.anim_scale.setEasingCurve(QEasingCurve.Type.OutBack)

        self.anim_scale.finished.connect(self._on_entrance_finished)
        self.anim_fade.start()
        self.anim_scale.start()

    def _on_entrance_finished(self):
        self.root_layout.setEnabled(True)
        self._apply_card_shadow()

    def _apply_card_shadow(self):
        self._card_shadow = QGraphicsDropShadowEffect(self.card)
        self._card_shadow.setBlurRadius(35)
        self._card_shadow.setOffset(0, 10)
        self._card_shadow.setColor(QColor(10, 77, 122, 80))
        self.card.setGraphicsEffect(self._card_shadow)

    def replay_entrance(self):
        """SỬA: cho phép phát lại animation entrance khi quay về từ màn khác"""
        self._entrance_played = False
