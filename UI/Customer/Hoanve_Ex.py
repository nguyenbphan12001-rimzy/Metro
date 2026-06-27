import sys
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView


class Hoanve_EX(QtWidgets.QMainWindow):
    def __init__(self, user_id, parent_dashboard=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.parent_dashboard = parent_dashboard

        self.initUi()
        self.load_customer_info()
        self.load_purchased_tickets()

    def initUi(self):
        self.setObjectName("RefundWindow")
        self.resize(650, 600)
        self.setStyleSheet("QMainWindow { background-color: #F0F8FF; }")

        self.centralwidget = QtWidgets.QWidget(self)
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- KHUNG THÔNG TIN KHÁCH HÀNG ---
        self.info_panel = QtWidgets.QFrame(self.centralwidget)
        self.info_panel.setStyleSheet("background-color: #FFFFFF; border: 1px solid #BEE3F8; border-radius: 12px;")
        self.info_layout = QtWidgets.QVBoxLayout(self.info_panel)

        self.lbl_title = QtWidgets.QLabel("YÊU CẦU HOÀN VÉ METRO", self.info_panel)
        self.lbl_title.setStyleSheet("color: #0A4D7A; font-weight: bold; font-size: 16px; border: none;")
        self.info_layout.addWidget(self.lbl_title)

        self.lbl_cust_info = QtWidgets.QLabel("Khách hàng: Đang tải... | Số điện thoại: Đang tải...", self.info_panel)
        self.lbl_cust_info.setStyleSheet("color: #4A5568; font-size: 13px; border: none;")
        self.info_layout.addWidget(self.lbl_cust_info)

        self.main_layout.addWidget(self.info_panel)

        # --- BẢNG DANH SÁCH VÉ ĐÃ MUA ---
        self.table_tickets = QtWidgets.QTableWidget(self.centralwidget)
        self.table_tickets.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; border: 1px solid #CBD5E0; border-radius: 8px; gridline-color: #E2E8F0; }
            QHeaderView::section { background-color: #1098F7; color: white; font-weight: bold; padding: 6px; border: none; }
        """)
        self.table_tickets.setColumnCount(4)
        self.table_tickets.setHorizontalHeaderLabels(["Mã Vé", "Thông tin vé", "Số Tiền Đã Trả", "Trạng Thái"])
        self.table_tickets.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_tickets.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_tickets.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.main_layout.addWidget(self.table_tickets)

        # --- NÚT HÀNH ĐỘNG ---
        self.btn_layout = QtWidgets.QHBoxLayout()

        self.btn_back = QtWidgets.QPushButton("← Trang chủ", self.centralwidget)
        self.btn_back.setMinimumSize(QtCore.QSize(160, 40))
        self.btn_back.setStyleSheet(
            "QPushButton { background-color: #EDF2F7; color: #4A5568; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #E2E8F0; }")
        self.btn_layout.addWidget(self.btn_back)

        self.btn_layout.addStretch()

        self.btn_confirm_refund = QtWidgets.QPushButton("Xác nhận hoàn vé 💳", self.centralwidget)
        self.btn_confirm_refund.setMinimumSize(QtCore.QSize(180, 40))
        self.btn_confirm_refund.setStyleSheet(
            "QPushButton { background-color: #E53E3E; color: white; border-radius: 8px; font-weight: bold; } QPushButton:hover { background-color: #C53030; }")
        self.btn_layout.addWidget(self.btn_confirm_refund)

        self.main_layout.addLayout(self.btn_layout)
        self.setCentralWidget(self.centralwidget)

        self.btn_back.clicked.connect(self.close)
        self.btn_confirm_refund.clicked.connect(self.handle_refund)

    def load_customer_info(self):
        try:
            from App.DB_Connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_name, phone FROM [USER] WHERE user_id = ?", (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.lbl_cust_info.setText(f"Khách hàng: {row[0]}  |  Số điện thoại: {row[1]}")
        except Exception as e:
            print(f"❌ Lỗi SQL load_customer_info: {e}")

    def load_purchased_tickets(self):
        try:
            from App.DB_Connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()

            # 🎯 ĐÃ SỬA: Thay thế câu truy vấn JOIN lỗi bằng câu truy vấn chỉ quét bảng [TICKET] để an toàn tuyệt đối
            query = """
                    SELECT ticket_id, ticket_id, price, status
                    FROM [TICKET]
                    WHERE user_id = ? AND status = N'Chưa sử dụng'
                    """
            cursor.execute(query, (self.user_id,))
            rows = cursor.fetchall()
            conn.close()

            self.table_tickets.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.table_tickets.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    if col_idx == 1:
                        item = QTableWidgetItem(f"Vé tàu Metro #{value}")
                    elif col_idx == 2:
                        item = QTableWidgetItem(f"{value:,.0f} VNĐ")
                    else:
                        item = QTableWidgetItem(str(value))
                    item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                    self.table_tickets.setItem(row_idx, col_idx, item)
        except Exception as e:
            print(f"❌ Lỗi SQL load_purchased_tickets: {e}")

    def handle_refund(self):
        selected_row = self.table_tickets.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một chiếc vé từ bảng để hoàn tác!")
            return

        ticket_id = self.table_tickets.item(selected_row, 0).text()
        price_str = self.table_tickets.item(selected_row, 2).text().replace(" VNĐ", "").replace(",", "")
        refund_amount = float(price_str)

        confirm = QMessageBox.question(
            self, "Xác nhận",
            f"Bạn có chắc chắn muốn hoàn vé mã {ticket_id}?\nSố tiền {refund_amount:,.0f} VNĐ sẽ được hoàn về ví.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                from App.DB_Connection import get_connection
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("UPDATE [TICKET] SET status = N'Đã hoàn' WHERE ticket_id = ?", (ticket_id,))
                cursor.execute("UPDATE [WALLET] SET balance = balance + ? WHERE user_id = ?",
                               (refund_amount, self.user_id))

                cursor.execute("SELECT MAX(refund_id) FROM [REFUNDS]")
                max_ref_id = cursor.fetchone()[0]
                next_ref_id = (max_ref_id + 1) if max_ref_id is not None else 1

                cursor.execute(
                    "INSERT INTO [REFUNDS] (refund_id, ticket_id, refund_date, amount) VALUES (?, ?, GETDATE(), ?)",
                    (next_ref_id, ticket_id, refund_amount)
                )

                conn.commit()
                conn.close()

                QMessageBox.information(self, "Thành công",
                                        "Vé đã được hoàn thành công! Tiền đã được cộng vào ví của bạn.")
                self.load_purchased_tickets()

                if self.parent_dashboard:
                    self.parent_dashboard.load_wallet_info()

            except Exception as e:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Quá trình xử lý hoàn vé thất bại:\n{str(e)}")


# Khối chạy thử nghiệm độc lập (Đặt chuẩn lề ngoài cùng)
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Giả lập ID để test
    window = Hoanve_EX(user_id=1)
    window.show()
    sys.exit(app.exec())