from PyQt6.QtGui import QColor
from UI.Customer.Dangky_Ver2 import Ui_RegisterWindow_Ver2
from App.DB_Connection import get_connection
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt6.QtCore import QRect, QPropertyAnimation, QEasingCurve, QTimer
from UI.Customer.SuccessToast import SuccessToast  # SỬA: thay QMessageBox bằng toast đồng bộ UI
from UI.Customer.ErrorToast import ErrorToast      # SỬA


class Dangky_Ver2_EX(Ui_RegisterWindow_Ver2):
    def setupUi(self, MainWindow, login_controller=None):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.login_controller = login_controller

        self.btn_dangky.clicked.connect(self.handle_registration)
        self.btn_back_login.clicked.connect(self.back_to_login)

        self._entrance_played = False
        self._center_on_screen()
        self._install_entrance_animation()

    def _center_on_screen(self):
        screen = self.MainWindow.screen().availableGeometry()
        w, h = self.MainWindow.width(), self.MainWindow.height()
        self.MainWindow.move(
            screen.x() + (screen.width() - w) // 2,
            screen.y() + (screen.height() - h) // 2
        )

    def replay_entrance(self):
        self._entrance_played = False

    # =========================================================
    # ENTRANCE ANIMATION (giữ nguyên, không đổi)
    # =========================================================
    def _install_entrance_animation(self):
        original_show_event = self.MainWindow.showEvent

        def show_event(event):
            original_show_event(event)
            if not self._entrance_played:
                self._entrance_played = True
                try:
                    self._animate_card_entrance()
                except Exception:
                    import traceback
                    traceback.print_exc()

        self.MainWindow.showEvent = show_event

    def _animate_card_entrance(self):
        final_geo = self.central_panel.geometry()
        if final_geo.width() == 0 or final_geo.height() == 0:
            return

        self.root_layout.setEnabled(False)

        cx, cy = final_geo.center().x(), final_geo.center().y()
        shrink_w = int(final_geo.width() * 0.82)
        shrink_h = int(final_geo.height() * 0.82)
        start_geo = QRect(cx - shrink_w // 2, cy - shrink_h // 2, shrink_w, shrink_h)

        self._card_opacity_effect = QGraphicsOpacityEffect(self.central_panel)
        self.central_panel.setGraphicsEffect(self._card_opacity_effect)
        self._card_opacity_effect.setOpacity(0)
        self.central_panel.setGeometry(start_geo)

        self.anim_fade = QPropertyAnimation(self._card_opacity_effect, b"opacity", self.MainWindow)
        self.anim_fade.setDuration(600)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        self.anim_fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_scale = QPropertyAnimation(self.central_panel, b"geometry", self.MainWindow)
        self.anim_scale.setDuration(600)
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
        self._card_shadow = QGraphicsDropShadowEffect(self.central_panel)
        self._card_shadow.setBlurRadius(35)
        self._card_shadow.setOffset(0, 10)
        self._card_shadow.setColor(QColor(10, 77, 122, 80))
        self.central_panel.setGraphicsEffect(self._card_shadow)

    # =========================================================
    # ĐĂNG KÝ — đổi toàn bộ QMessageBox sang Toast
    # =========================================================
    def handle_registration(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        phone = self.txt_phone.text().strip()
        role = "customer"

        try:
            if hasattr(self, 'DoB') and hasattr(self.DoB, 'date'):
                dob = self.DoB.date().toString("yyyy-MM-dd")
            elif hasattr(self, 'DoB') and hasattr(self.DoB, 'text'):
                dob = self.DoB.text().strip()
            else:
                dob = "2000-01-01"
        except Exception:
            dob = "2000-01-01"

        if not username or not password or not phone or not dob:
            self._show_error("Vui lòng điền đầy đủ thông tin!")  # SỬA
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT user_id FROM [USER] WHERE user_name = ?", (username,))
            if cursor.fetchone() is not None:
                self._show_error(f"Tài khoản '{username}' đã tồn tại!")  # SỬA
                conn.close()
                return

            # SỬA: check trùng số điện thoại — mỗi số điện thoại chỉ được đăng ký 1 tài khoản
            cursor.execute("SELECT user_id FROM [USER] WHERE phone = ?", (phone,))
            if cursor.fetchone() is not None:
                self._show_error(f"Số điện thoại '{phone}' đã được sử dụng để đăng ký tài khoản khác!")  # SỬA
                conn.close()
                return

            cursor.execute("SELECT MAX(user_id) FROM [USER]")
            max_id = cursor.fetchone()[0]
            next_id = (max_id + 1) if max_id is not None else 1

            cursor.execute(
                "INSERT INTO [USER] (user_id, user_name, password, role, phone, DoB) VALUES (?, ?, ?, ?, ?, ?)",
                (next_id, username, password, role, phone, dob)
            )
            # Cấp phát ví cho user mới — lấy wallet_id kế tiếp
            cursor.execute("SELECT ISNULL(MAX(wallet_id), 0) FROM WALLET")
            next_wallet_id = cursor.fetchone()[0] + 1

            cursor.execute(
                "INSERT INTO WALLET (wallet_id, user_id, balance) VALUES (?, ?, 0)",
                (next_wallet_id, next_id)
            )
            conn.commit()
            conn.close()

            self._toast = SuccessToast(self.MainWindow, f"Đăng ký thành công! ID: {next_id}")  # SỬA
            self._toast.show_animated()
            QTimer.singleShot(1200, self.back_to_login)  # SỬA: đợi toast chạy xong rồi mới chuyển màn

        except Exception as e:
            self._show_error(f"Không thể ghi dữ liệu vào database:\n{str(e)}")  # SỬA

    def _show_error(self, message):
        """SỬA: helper dùng ErrorToast đồng bộ giao diện thay cho QMessageBox."""
        self._error_toast = ErrorToast(self.MainWindow, message)
        self._error_toast.show_animated()

    def back_to_login(self):
        try:
            if self.login_controller and hasattr(self.login_controller, 'MainWindow'):
                if hasattr(self.login_controller, 'replay_entrance'):
                    self.login_controller.replay_entrance()
                self.login_controller.MainWindow.show()
                self.MainWindow.close()
                return

            from UI.Customer.Dangnhap_Ver4_EX import Dangnhap_Ver4_EX
            from PyQt6.QtWidgets import QMainWindow, QApplication

            conn = get_connection()
            main_window = QMainWindow()
            login_ui = Dangnhap_Ver4_EX()
            login_ui.setupUi(main_window, conn=conn)

            app = QApplication.instance()
            if not hasattr(app, "_kept_refs"):
                app._kept_refs = []
            app._kept_refs.append((main_window, login_ui))

            self.main_window = main_window
            self.login_ui = login_ui

            main_window.show()
            self.MainWindow.close()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._show_error(f"Không thể quay lại màn đăng nhập:\n{str(e)}")  # SỬA