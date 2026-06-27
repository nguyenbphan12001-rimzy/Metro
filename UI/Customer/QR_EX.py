import os
import sys
import json
import shutil
import tempfile
from datetime import datetime
import smtplib
from email.message import EmailMessage
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

APP_DIR = os.path.join(PROJECT_ROOT, 'App')
if APP_DIR not in sys.path:
    sys.path.append(APP_DIR)

from UI.Customer.QR import Ui_QRPaymentDialog

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


class QR_EX(Ui_QRPaymentDialog):
    def __init__(self, user_id="1", ticket_data=None):
        super().__init__()

        # Lưu lại mã khách hàng
        self.user_id = user_id

        self.ticket_data = ticket_data or {
            "ma_ve": "MTR-2024-05-001",
            "tuyen": "Tuyến 1",
            "hanh_trinh": "Bến Thành → Văn Thánh",
            "loai_ve": "Vé lượt",
            "gia_ve": "12,000 VNĐ",
            "ngay_mua": datetime.now().strftime("%d/%m/%Y"),
            "trang_thai": "Chưa sử dụng",
        }

        self._window = None
        self._qr_temp_path = None

    def setupUi(self, window):
        super().setupUi(window)
        self._window = window

        self.populate_ticket_info()
        self.generate_qr()

        self.btnShare.setText("✉  Gửi Gmail")

        self.btnDownload.clicked.connect(self.on_download)
        self.btnShare.clicked.connect(self.on_send_gmail)
        self.btnHome.clicked.connect(self.on_go_home)

    def populate_ticket_info(self):
        d = self.ticket_data
        self.ticketCodeLabel.setText(f"Mã vé: #{d['ma_ve']}")
        self.lblTuyenVal.setText(d["tuyen"])
        self.lblHTVal.setText(d["hanh_trinh"])
        self.lblLVVal.setText(d["loai_ve"])
        self.lblGVVal.setText(d["gia_ve"])
        self.lblNMVal.setText(d["ngay_mua"])
        self.statusBadge.setText(d["trang_thai"])

    def generate_qr(self):
        if not QR_AVAILABLE:
            self.qrLabel.setText("⚠ Cần cài:\npip install qrcode[pil]")
            return

        d = self.ticket_data
        payload = json.dumps({
            "ma_ve": d["ma_ve"],
            "tuyen": d["tuyen"],
            "hanh_trinh": d["hanh_trinh"],
            "loai_ve": d["loai_ve"],
            "ngay_mua": d["ngay_mua"],
            "trang_thai": d["trang_thai"],
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
            img = qr.make_image(fill_color="#0A4D7A", back_color="white")

            safe_id = d["ma_ve"].replace("-", "").replace("/", "").replace(" ", "")
            self._qr_temp_path = os.path.join(
                tempfile.gettempdir(), f"metro_qr_{safe_id}.png"
            )
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

    def on_download(self):
        if not self._qr_temp_path or not os.path.exists(self._qr_temp_path):
            QMessageBox.warning(
                self._window, "Chưa có ảnh QR",
                "Không tìm thấy mã QR.\nHãy cài: pip install qrcode[pil]"
            )
            return

        default_name = f"Ve_Metro_{self.ticket_data['ma_ve']}.png"
        save_path, _ = QFileDialog.getSaveFileName(
            self._window, "Lưu mã QR vé tàu",
            default_name, "PNG Image (*.png);;All Files (*)"
        )

        if not save_path:
            return

        try:
            shutil.copy2(self._qr_temp_path, save_path)
            QMessageBox.information(
                self._window, "Lưu thành công",
                f"Đã lưu mã QR tại:\n{save_path}"
            )
        except Exception as e:
            QMessageBox.critical(self._window, "Lỗi lưu file", str(e))

    def on_send_gmail(self):
        # Bật hộp thoại hỏi khách hàng nhập Email
        email_nhan, ok = QInputDialog.getText(
            self._window,
            "Gửi vé qua Email",
            "Vui lòng nhập địa chỉ Email của bạn:"
        )

        if not ok or not email_nhan.strip():
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            EMAIL_GUI = "khanhpham3652007@gmail.com"
            MAT_KHAU_APP = "wmribojvuoglnkxb"

            d = self.ticket_data
            msg = EmailMessage()
            msg['Subject'] = f'[Metro HCMC] Thông tin vé #{d["ma_ve"]}'
            msg['From'] = EMAIL_GUI
            msg['To'] = email_nhan.strip()

            body = f"""THÔNG TIN VÉ TÀU METRO HỒ CHÍ MINH
==========================================

Mã vé       :  {d['ma_ve']}
Tuyến       :  {d['tuyen']}
Hành trình  :  {d['hanh_trinh']}
Loại vé     :  {d['loai_ve']}
Giá vé      :  {d['gia_ve']}
Ngày mua    :  {d['ngay_mua']}
Trạng thái  :  {d['trang_thai']}

==========================================
Vui lòng xuất trình vé khi lên/xuống tàu.
Metro TP.HCM – Tuyến 1
"""
            msg.set_content(body)

            # Bắt đầu gửi Email ngầm
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_GUI, MAT_KHAU_APP)
            server.send_message(msg)
            server.quit()

            QApplication.restoreOverrideCursor()
            QMessageBox.information(self._window, "Thành công", f"Đã gửi vé thành công tới:\n{email_nhan}")

        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self._window, "Lỗi gửi Email", f"Không thể gửi email.\nChi tiết: {str(e)}")


    def on_go_home(self):
        try:
            from UI.Customer.KhachHang_EX import KhachHang_EX

            self._home_window = QMainWindow()
            self._home_ui = KhachHang_EX()

            # Truyền user_id đã lưu ở trên vào setupUi
            self._home_ui.setupUi(self._home_window, self.user_id)

            self._home_window.show()
            self._window.close()

        except Exception as e:
            QMessageBox.critical(self._window, "Lỗi mở trang chủ", str(e))


