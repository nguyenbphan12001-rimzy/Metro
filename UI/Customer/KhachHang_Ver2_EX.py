import traceback

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QMainWindow
from PyQt6.QtGui import QColor
from UI.Customer.KhachHang_Ver2 import Ui_DashboardWindow_Ver2
from MyCollection.wallet import get_wallet
from UI.Customer.Naptien_Ver2_EX import Naptien_Ver2_EX


class KhachHang_Ver2_EX(Ui_DashboardWindow_Ver2):
    def setupUi(self, MainWindow, user_id, conn,parent_window=None):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.user_id = user_id
        self.conn = conn
        self._window = MainWindow
        self._parent_window = parent_window

        self.load_wallet_info()
        self._install_refresh_on_show()  # SỬA: tự refresh số dư mỗi khi quay lại dashboard
        self.card_buy.mousePressEvent = lambda event: self.open_buy_ticket()
        self.card_myticket.mousePressEvent = lambda event: self.open_my_tickets()
        self.btn_topup.clicked.connect(self._safe(self.open_topup))

        self.btn_logout.clicked.connect(self._safe(self.open_logout))

    # SỬA: dashboard chỉ hide()/show() lại chứ không tạo mới mỗi lần quay về
    # (từ mua vé, vé của tôi, hoàn vé, nạp tiền...) nên lbl_balance bị đứng giá trị
    # cũ dù DB đã cập nhật ngay qua trigger. Hook showEvent để mỗi lần cửa sổ
    # này HIỆN LẠI là tự load_wallet_info() mới nhất từ DB.
    def _install_refresh_on_show(self):
        original_show_event = self.MainWindow.showEvent

        def show_event(event):
            original_show_event(event)
            self._safe(self.load_wallet_info)()

        self.MainWindow.showEvent = show_event



    def show_with_animation(self, window):
        """
        Hiệu ứng: cửa sổ trượt lên từ dưới 60px + fade in đồng thời.
        Khác với fade thông thường — tạo cảm giác 'nội dung bay vào'.
        """
        # Tính vị trí đích (đã set trước khi gọi hàm này)
        end_pos = window.pos()
        start_pos = QPoint(end_pos.x(), end_pos.y() + 60)

        window.move(start_pos)
        window.setWindowOpacity(0)
        window.show()

        # Animation vị trí: trượt lên
        self._anim_pos = QPropertyAnimation(window, b"pos")
        self._anim_pos.setDuration(420)
        self._anim_pos.setStartValue(start_pos)
        self._anim_pos.setEndValue(end_pos)
        self._anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Animation opacity: fade in
        self._anim_opacity = QPropertyAnimation(window, b"windowOpacity")
        self._anim_opacity.setDuration(420)
        self._anim_opacity.setStartValue(0.0)
        self._anim_opacity.setEndValue(1.0)
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Chạy song song
        self._anim_group = QParallelAnimationGroup()
        self._anim_group.addAnimation(self._anim_pos)
        self._anim_group.addAnimation(self._anim_opacity)
        self._anim_group.start()

    def open_buy_ticket(self):
        from UI.Customer.Thanhtoan_EX import ThanhToan_EX
        from PyQt6.QtWidgets import QMainWindow

        try:
            screen = self.MainWindow.screen().availableGeometry()
            self.buy_window = QMainWindow()
            ui = ThanhToan_EX()
            ui.setupUi(self.buy_window, conn=self.conn, user_id=self.user_id, parent_window=self.MainWindow)

            w = 436
            h = min(853, screen.height() - 20)  # SỬA: chừa 20px lề trên/dưới thay vì trừ nhiều

            self.buy_window.resize(w, h)
            self.buy_window.move(
                screen.x() + (screen.width() - w) // 2,
                screen.y() + 10  # SỬA: dán sát mép trên màn hình thay vì canh giữa theo chiều dọc
            )

            self.show_with_animation(self.buy_window)
            self.MainWindow.hide()
        except Exception as e:
            import traceback
            print("[LỖI open_buy_ticket]:", e)
            traceback.print_exc()

    def load_wallet_info(self):
        # Load số dư ví
        wallet = get_wallet(self.user_id)
        if wallet:
            self.lbl_balance.setText(f"{wallet['balance']:,.0f} VNĐ")
        else:
            self.lbl_balance.setText("Không tìm thấy ví")

        # Load tên và SĐT user từ DB
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT user_name, phone FROM [USER] WHERE user_id = ?",
                self.user_id
            )
            row = cursor.fetchone()
            if row:
                user_name, phone = row
                self.lbl_name.setText(user_name)
                self.lbl_email.setText(phone if phone else "")
                # Avatar: lấy chữ cái đầu của username
                self.lbl_avatar.setText(user_name[0].upper() if user_name else "KH")
        except Exception as e:
            print(f"[load_wallet_info] Lỗi load user info: {e}")

    def open_my_tickets(self):
        from UI.Customer.VeCuaToi_EX import VeCuaToi_EX
        from PyQt6.QtWidgets import QMainWindow

        try:
            screen = self.MainWindow.screen().availableGeometry()
            self.ticket_window = QMainWindow()
            ui = VeCuaToi_EX()
            ui.setupUi(self.ticket_window, conn=self.conn, user_id=self.user_id, parent_window=self.MainWindow)

            w, h = 440, min(780, screen.height() - 40)
            self.ticket_window.resize(w, h)
            self.ticket_window.move(
                screen.x() + (screen.width() - w) // 2,
                screen.y() + (screen.height() - h) // 2
            )

            self.show_with_animation(self.ticket_window)
            self.MainWindow.hide()
        except Exception as e:
            import traceback
            print("[LỖI open_my_tickets]:", e)
            traceback.print_exc()

    def open_topup(self):
        from PyQt6.QtWidgets import QMainWindow

        try:
            screen = self.MainWindow.screen().availableGeometry()
            self.topup_window = QMainWindow()
            self.topup_gui = Naptien_Ver2_EX()
            self.topup_gui.setupUi(
                self.topup_window,
                conn=self.conn,
                user_id=self.user_id,
                parent_window=self.MainWindow,  # SỬA: dùng self.MainWindow cho đồng bộ với các open_* khác
            )

            w, h = 440, min(680, screen.height() - 40)
            self.topup_window.resize(w, h)
            self.topup_window.move(
                screen.x() + (screen.width() - w) // 2,
                screen.y() + (screen.height() - h) // 2
            )

            # SỬA: lưu reference để màn nạp tiền refresh lại số dư dashboard khi back về
            self.MainWindow.dashboard_gui = self

            self.show_with_animation(self.topup_window)
            self.MainWindow.hide()
        except Exception as e:
            print("[LỖI open_topup]:", e)
            traceback.print_exc()



    def _safe(self, fn):
        def wrapper():
            try:
                fn()
            except Exception:
                traceback.print_exc()

        return wrapper

    def open_logout(self):
        from UI.Customer.Dangnhap_Ver4_EX import Dangnhap_Ver4_EX
        from PyQt6.QtWidgets import QMainWindow, QApplication

        try:
            login_window = QMainWindow()
            login_ui = Dangnhap_Ver4_EX()
            login_ui.setupUi(login_window, conn=self.conn)

            # SỬA: giữ reference tránh bị garbage collect mất window/controller
            app = QApplication.instance()
            if not hasattr(app, "_kept_refs"):
                app._kept_refs = []
            app._kept_refs.append((login_window, login_ui))

            # Fade-out dashboard trước khi đóng — hiệu ứng "trượt xuống" ngược với lúc mở
            self._fade_out_then_close(self.MainWindow, on_finished=login_window.show)

        except Exception as e:
            print("[LỖI open_logout]:", e)
            traceback.print_exc()

    def _fade_out_then_close(self, window, on_finished):
        """SỬA: fade out + trượt xuống 40px trước khi đóng cửa sổ, đối xứng với show_with_animation."""
        end_pos = QPoint(window.pos().x(), window.pos().y() + 40)

        self._logout_anim_pos = QPropertyAnimation(window, b"pos")
        self._logout_anim_pos.setDuration(280)
        self._logout_anim_pos.setStartValue(window.pos())
        self._logout_anim_pos.setEndValue(end_pos)
        self._logout_anim_pos.setEasingCurve(QEasingCurve.Type.InCubic)

        self._logout_anim_opacity = QPropertyAnimation(window, b"windowOpacity")
        self._logout_anim_opacity.setDuration(280)
        self._logout_anim_opacity.setStartValue(1.0)
        self._logout_anim_opacity.setEndValue(0.0)
        self._logout_anim_opacity.setEasingCurve(QEasingCurve.Type.InCubic)

        def _finish():
            on_finished()  # show màn login — entrance animation của nó tự chạy qua showEvent
            window.close()

        self._logout_anim_group = QParallelAnimationGroup()
        self._logout_anim_group.addAnimation(self._logout_anim_pos)
        self._logout_anim_group.addAnimation(self._logout_anim_opacity)
        self._logout_anim_group.finished.connect(_finish)
        self._logout_anim_group.start()

    def _go_back(self):
        self._window.close()
        if self._parent_window:
            self._parent_window.show()