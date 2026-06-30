from PyQt6.QtGui import QColor

from UI.Customer.QuenMatKhau_Ver3 import Ui_ForgotPasswordWindow
from UI.Customer.StyledDialogs import StatusDialog
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup


class QuenMatKhau_Ver3_EX(Ui_ForgotPasswordWindow):
    def setupUi(self, Window, conn=None, parent_window=None):
        super().setupUi(Window)

        self.conn = conn
        self.parent_window = parent_window
        self._window = Window
        self._center_on_screen()

        # Trạng thái bước: False = bước 1 (xác thực), True = bước 2 (đổi mật khẩu)
        self._is_verified = False
        self._verified_username = None

        # Bước 1: ẩn field mật khẩu mới
        self._set_step(1)

        # Kết nối nút
        self.btn_action.clicked.connect(self._handle_action)
        self.btn_back.clicked.connect(self._back_to_login)

    # ──────────────────────────────────────────────
    # UI STATE
    # ──────────────────────────────────────────────
    def _center_on_screen(self):
        screen = self._window.screen().availableGeometry()
        w, h = self._window.width(), self._window.height()
        self._window.move(
            screen.x() + (screen.width() - w) // 2,
            screen.y() + (screen.height() - h) // 2
        )

    def _set_step(self, step: int):
        """Cập nhật toàn bộ UI theo bước hiện tại (1 hoặc 2)."""
        if step == 1:
            # Hiện / ẩn field
            self.lbl_field_newpass.hide()
            self.txt_new_pass.hide()

            # Mở khoá input xác thực
            self.txt_username.setEnabled(True)
            self.txt_phone.setEnabled(True)
            self.txt_username.clear()
            self.txt_phone.clear()
            self.txt_new_pass.clear()

            # Nút hành động: màu xanh xác thực
            self.btn_action.setText("Xác thực thông tin  🔍")
            self.btn_action.setStyleSheet("""
                QPushButton#btn_action {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0284C7, stop:0.5 #0EA5E9, stop:1 #38BDF8);
                    color: #FFFFFF; border: none; border-radius: 13px;
                    font-size: 14px; font-weight: 700;
                    border-top: 1px solid rgba(255,255,255,0.20);
                }
                QPushButton#btn_action:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0369A1, stop:0.5 #0284C7, stop:1 #0EA5E9);
                }
                QPushButton#btn_action:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #075985, stop:1 #0284C7);
                }
            """)

            # Step indicator: dot 1 sáng, dot 2 mờ
            self._update_step_indicator(active=1)

        elif step == 2:
            # Hiện field mật khẩu mới
            self.lbl_field_newpass.show()
            self.txt_new_pass.show()
            self.txt_new_pass.setFocus()

            # Khoá 2 field xác thực
            self.txt_username.setEnabled(False)
            self.txt_phone.setEnabled(False)

            # Nút hành động: đổi sang màu xanh lá
            self.btn_action.setText("Cập nhật mật khẩu  💾")
            self.btn_action.setStyleSheet("""
                QPushButton#btn_action {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #059669, stop:0.5 #10B981, stop:1 #34D399);
                    color: #FFFFFF; border: none; border-radius: 13px;
                    font-size: 14px; font-weight: 700;
                    border-top: 1px solid rgba(255,255,255,0.20);
                }
                QPushButton#btn_action:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #047857, stop:0.5 #059669, stop:1 #10B981);
                }
                QPushButton#btn_action:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #065F46, stop:1 #047857);
                }
            """)

            # Step indicator: dot 2 sáng
            self._update_step_indicator(active=2)

    def _update_step_indicator(self, active: int):
        """Đổi màu dot step indicator theo bước đang active."""
        if active == 1:
            self.step_dot_1.setStyleSheet("""
                QFrame#step_dot_1 {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 #38BDF8, stop:1 #0284C7);
                    border-radius: 11px;
                    border: 2px solid rgba(255,255,255,0.35);
                }
            """)
            self.lbl_step_num_1.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: 700;")
            self.step_dot_2.setStyleSheet("""
                QFrame#step_dot_2 {
                    background: rgba(255,255,255,0.15);
                    border-radius: 11px;
                    border: 2px solid rgba(148,213,252,0.35);
                }
            """)
            self.lbl_step_num_2.setStyleSheet("color: rgba(148,213,252,0.60); font-size: 11px; font-weight: 600;")
            self.lbl_step_label_1.setStyleSheet("color: #7DD3FC; font-size: 10px; font-weight: 600;")
            self.lbl_step_label_2.setStyleSheet("color: rgba(148,213,252,0.45); font-size: 10px;")

        elif active == 2:
            # Dot 1: tick xanh lá (đã xong)
            self.step_dot_1.setStyleSheet("""
                QFrame#step_dot_1 {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 #34D399, stop:1 #059669);
                    border-radius: 11px;
                    border: 2px solid rgba(255,255,255,0.35);
                }
            """)
            self.lbl_step_num_1.setText("✓")
            self.lbl_step_num_1.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: 700;")
            self.lbl_step_label_1.setStyleSheet("color: #6EE7B7; font-size: 10px; font-weight: 600;")

            # Dot 2: xanh dương active
            self.step_dot_2.setStyleSheet("""
                QFrame#step_dot_2 {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 #38BDF8, stop:1 #0284C7);
                    border-radius: 11px;
                    border: 2px solid rgba(255,255,255,0.35);
                }
            """)
            self.lbl_step_num_2.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: 700;")
            self.lbl_step_label_2.setStyleSheet("color: #7DD3FC; font-size: 10px; font-weight: 600;")

    # ──────────────────────────────────────────────
    # HELPER: hiển thị dialog đẹp thay cho QMessageBox  (SỬA)
    # ──────────────────────────────────────────────

    def _show_dialog(self, title, message, kind="warning"):
        """kind: 'warning' | 'error' | 'success' — đồng bộ với _IconBadge trong StyledDialogs."""
        dlg = StatusDialog(self._window, title, message, kind=kind)
        dlg.exec()

    # ──────────────────────────────────────────────
    # LOGIC XỬ LÝ
    # ──────────────────────────────────────────────

    def _handle_action(self):
        """Điểm vào duy nhất của nút — tự phân nhánh theo bước."""
        if not self._is_verified:
            self._verify_identity()
        else:
            self._update_password()

    def _verify_identity(self):
        """Bước 1: xác thực username + SĐT với DB."""
        username = self.txt_username.text().strip()
        phone = self.txt_phone.text().strip()

        if not username or not phone:
            self._show_dialog(  # SỬA
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ Tên tài khoản và Số điện thoại!",
                kind="warning"
            )
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT user_id FROM [USER] WHERE user_name = ? AND phone = ?",
                username, phone
            )
            row = cursor.fetchone()

            if row:
                self._verified_username = username
                self._is_verified = True
                self._set_step(2)
                self._show_dialog(  # SỬA
                    "Xác thực thành công",
                    "Thông tin hợp lệ!\nVui lòng nhập mật khẩu mới bên dưới.",
                    kind="success"
                )
            else:
                self._show_dialog(  # SỬA
                    "Xác thực thất bại",
                    "Tên tài khoản hoặc Số điện thoại không khớp với hệ thống.",
                    kind="error"
                )

        except Exception as e:
            self._show_dialog(  # SỬA
                "Lỗi kết nối",
                f"Không thể truy vấn cơ sở dữ liệu:\n{e}",
                kind="error"
            )

    def _update_password(self):
        """Bước 2: cập nhật mật khẩu mới vào DB."""
        new_password = self.txt_new_pass.text().strip()

        if not new_password:
            self._show_dialog(  # SỬA
                "Thiếu thông tin",
                "Vui lòng nhập mật khẩu mới!",
                kind="warning"
            )
            return

        if len(new_password) < 6:
            self._show_dialog(  # SỬA
                "Mật khẩu quá ngắn",
                "Mật khẩu phải có ít nhất 6 ký tự!",
                kind="warning"
            )
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE [USER] SET password = ? WHERE user_name = ?",
                new_password, self._verified_username
            )
            self.conn.commit()

            self._show_dialog(  # SỬA
                "Thành công",
                "Mật khẩu đã được cập nhật!\nVui lòng đăng nhập lại.",
                kind="success"
            )
            self._back_to_login()

        except Exception as e:
            self.conn.rollback()
            self._show_dialog(  # SỬA
                "Lỗi cập nhật",
                f"Không thể lưu mật khẩu mới:\n{e}",
                kind="error"
            )

    def _back_to_login(self):
        """Trượt xuống + fade out rồi mới đóng, sau đó show lại màn login."""
        self._fade_out_then_close(self._window, on_finished=self._show_parent_window)

    def _show_parent_window(self):
        if self.parent_window and hasattr(self.parent_window, 'show'):
            self.parent_window.show()

    def _fade_out_then_close(self, window, on_finished):
        end_pos = QPoint(window.pos().x(), window.pos().y() + 40)

        self._exit_anim_pos = QPropertyAnimation(window, b"pos")
        self._exit_anim_pos.setDuration(280)
        self._exit_anim_pos.setStartValue(window.pos())
        self._exit_anim_pos.setEndValue(end_pos)
        self._exit_anim_pos.setEasingCurve(QEasingCurve.Type.InCubic)

        self._exit_anim_opacity = QPropertyAnimation(window, b"windowOpacity")
        self._exit_anim_opacity.setDuration(280)
        self._exit_anim_opacity.setStartValue(1.0)
        self._exit_anim_opacity.setEndValue(0.0)
        self._exit_anim_opacity.setEasingCurve(QEasingCurve.Type.InCubic)

        def _finish():
            on_finished()
            window.close()

        self._exit_anim_group = QParallelAnimationGroup()
        self._exit_anim_group.addAnimation(self._exit_anim_pos)
        self._exit_anim_group.addAnimation(self._exit_anim_opacity)
        self._exit_anim_group.finished.connect(_finish)
        self._exit_anim_group.start()
    def show_with_animation(self, window):
        """Trượt lên 60px + fade in khi mở cửa sổ — đồng bộ với các màn khác."""
        end_pos = window.pos()
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