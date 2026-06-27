from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_NapTienWindow(object):
    def setupUi(self, NapTienWindow):
        NapTienWindow.setObjectName("NapTienWindow")
        NapTienWindow.resize(450, 620)
        NapTienWindow.setStyleSheet("""
            QMainWindow { background-color: #E8F6FD; }
            QWidget#centralwidget { background-color: #E8F6FD; }
        """)

        self.centralwidget = QtWidgets.QWidget(parent=NapTienWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(0)
        self.main_layout.setObjectName("main_layout")

        # ── Central panel ──
        self.central_panel = QtWidgets.QFrame(parent=self.centralwidget)
        self.central_panel.setStyleSheet(
            "QFrame { background-color: #FFFFFF; border: 1px solid #BEE3F8; border-radius: 16px; }"
        )
        self.central_panel.setObjectName("central_panel")

        self.panel_layout = QtWidgets.QVBoxLayout(self.central_panel)
        self.panel_layout.setContentsMargins(25, 28, 25, 25)
        self.panel_layout.setSpacing(14)
        self.panel_layout.setObjectName("panel_layout")

        # ── Header ──
        self.header_layout = QtWidgets.QVBoxLayout()
        self.header_layout.setSpacing(4)

        self.logo_row = QtWidgets.QHBoxLayout()
        self.logo_row.addStretch()
        self.lbl_logo_icon = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_logo_icon.setMinimumSize(QtCore.QSize(76, 76))
        self.lbl_logo_icon.setMaximumSize(QtCore.QSize(76, 76))
        self.lbl_logo_icon.setStyleSheet(
            "background-color: #0677C2; border-radius: 38px; font-size: 30px; border: none;"
        )
        self.lbl_logo_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo_icon.setObjectName("lbl_logo_icon")
        self.logo_row.addWidget(self.lbl_logo_icon)
        self.logo_row.addStretch()
        self.header_layout.addLayout(self.logo_row)

        self.header_layout.addSpacing(6)

        self.lbl_logo = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_logo.setStyleSheet(
            "color: #0A4D7A; font-weight: bold; font-size: 22px; border: none;"
        )
        self.lbl_logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo.setObjectName("lbl_logo")
        self.header_layout.addWidget(self.lbl_logo)

        self.lbl_subtitle = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_subtitle.setStyleSheet("color: #3A9EC9; font-size: 13px; border: none;")
        self.lbl_subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_subtitle.setObjectName("lbl_subtitle")
        self.header_layout.addWidget(self.lbl_subtitle)

        self.panel_layout.addLayout(self.header_layout)
        self.panel_layout.addSpacing(4)

        # ── Divider ──
        self.divider = QtWidgets.QFrame(parent=self.central_panel)
        self.divider.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.divider.setStyleSheet("border: none; border-top: 1px solid #E2E8F0;")
        self.panel_layout.addWidget(self.divider)

        # ── Số dư hiện tại ──
        self.lbl_balance_tag = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_balance_tag.setStyleSheet(
            "color: #0D6FA6; font-weight: bold; font-size: 13px; border: none;"
        )
        self.lbl_balance_tag.setObjectName("lbl_balance_tag")
        self.panel_layout.addWidget(self.lbl_balance_tag)

        self.lbl_balance_value = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_balance_value.setStyleSheet(
            "background-color: #F0FAFF; border: 1.5px solid #B3E0F5; border-radius: 12px;"
            "padding: 11px 14px; font-size: 16px; font-weight: bold; color: #0677C2;"
        )
        self.lbl_balance_value.setObjectName("lbl_balance_value")
        self.panel_layout.addWidget(self.lbl_balance_value)

        # ── Số tiền nạp ──
        self.lbl_amount_tag = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_amount_tag.setStyleSheet(
            "color: #0D6FA6; font-weight: bold; font-size: 13px; border: none;"
        )
        self.lbl_amount_tag.setObjectName("lbl_amount_tag")
        self.panel_layout.addWidget(self.lbl_amount_tag)

        self.txt_amount = QtWidgets.QLineEdit(parent=self.central_panel)
        self.txt_amount.setStyleSheet(
            "background-color: #F0FAFF; border: 1.5px solid #B3E0F5; border-radius: 12px;"
            "padding: 11px 14px; font-size: 14px; color: #0A3D5C; selection-background-color: #29B6F6;"
        )
        self.txt_amount.setObjectName("txt_amount")
        self.panel_layout.addWidget(self.txt_amount)

        # ── Quick amount buttons ──
        self.lbl_quick_tag = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_quick_tag.setStyleSheet(
            "color: #0D6FA6; font-weight: bold; font-size: 13px; border: none;"
        )
        self.lbl_quick_tag.setObjectName("lbl_quick_tag")
        self.panel_layout.addWidget(self.lbl_quick_tag)

        self.quick_row = QtWidgets.QHBoxLayout()
        self.quick_row.setSpacing(8)
        btn_style = (
            "QPushButton { background-color: #E1F5FE; border: 1.5px solid #B3E0F5; border-radius: 10px;"
            "color: #0677C2; font-size: 13px; font-weight: bold; padding: 8px 6px; }"
            "QPushButton:hover { background-color: #B3E0F5; }"
            "QPushButton:pressed { background-color: #81D4FA; }"
        )
        for amount_text in ["50,000", "100,000", "200,000", "500,000"]:
            btn = QtWidgets.QPushButton(parent=self.central_panel)
            btn.setText(amount_text)
            btn.setStyleSheet(btn_style)
            btn.setObjectName(f"btn_quick_{amount_text.replace(',','')}")
            self.quick_row.addWidget(btn)

        # Lưu reference để dùng trong EX
        self.btn_quick_50000 = self.quick_row.itemAt(0).widget()
        self.btn_quick_100000 = self.quick_row.itemAt(1).widget()
        self.btn_quick_200000 = self.quick_row.itemAt(2).widget()
        self.btn_quick_500000 = self.quick_row.itemAt(3).widget()

        self.panel_layout.addLayout(self.quick_row)

        # ── Phương thức thanh toán ──
        self.lbl_method_tag = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_method_tag.setStyleSheet(
            "color: #0D6FA6; font-weight: bold; font-size: 13px; border: none;"
        )
        self.lbl_method_tag.setObjectName("lbl_method_tag")
        self.panel_layout.addWidget(self.lbl_method_tag)

        self.combo_method = QtWidgets.QComboBox(parent=self.central_panel)
        self.combo_method.setStyleSheet(
            "QComboBox { background-color: #F0FAFF; border: 1.5px solid #B3E0F5; border-radius: 12px;"
            "padding: 11px 14px; font-size: 14px; color: #0A3D5C; }"
            "QComboBox::drop-down { border: none; width: 30px; }"
            "QComboBox QAbstractItemView { background-color: #FFFFFF; border: 1px solid #B3E0F5;"
            "border-radius: 8px; selection-background-color: #E1F5FE; color: #0A3D5C; }"
        )
        self.combo_method.setObjectName("combo_method")
        self.panel_layout.addWidget(self.combo_method)

        self.panel_layout.addStretch()

        # ── Nút xác nhận ──
        self.btn_naptien = QtWidgets.QPushButton(parent=self.central_panel)
        self.btn_naptien.setMinimumSize(QtCore.QSize(0, 48))
        self.btn_naptien.setStyleSheet(
            "QPushButton { background-color: #0677C2; border: none; border-radius: 12px;"
            "font-size: 15px; font-weight: bold; color: #FFFFFF; padding: 11px 14px; }"
            "QPushButton:hover { background-color: #0288D1; }"
            "QPushButton:pressed { background-color: #0569AD; }"
        )
        self.btn_naptien.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btn_naptien.setObjectName("btn_naptien")
        self.panel_layout.addWidget(self.btn_naptien)

        # ── Footer ──
        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.addStretch()
        self.lbl_hint = QtWidgets.QLabel(parent=self.central_panel)
        self.lbl_hint.setStyleSheet("color: #718096; font-size: 13px; border: none;")
        self.lbl_hint.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.lbl_hint.setObjectName("lbl_hint")
        self.footer_layout.addWidget(self.lbl_hint)
        self.btn_back = QtWidgets.QPushButton(parent=self.central_panel)
        font = QtGui.QFont()
        font.setBold(True)
        self.btn_back.setFont(font)
        self.btn_back.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btn_back.setStyleSheet(
            "QPushButton { color: #0077C2; font-weight: bold; background: none; border: none; font-size: 13px; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        self.btn_back.setObjectName("btn_back")
        self.footer_layout.addWidget(self.btn_back)
        self.footer_layout.addStretch()
        self.panel_layout.addLayout(self.footer_layout)

        self.main_layout.addWidget(self.central_panel)
        NapTienWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(NapTienWindow)
        QtCore.QMetaObject.connectSlotsByName(NapTienWindow)

    def retranslateUi(self, NapTienWindow):
        _translate = QtCore.QCoreApplication.translate
        NapTienWindow.setWindowTitle(_translate("NapTienWindow", "Metro Ticket System – Nạp tiền"))
        self.lbl_logo_icon.setText(_translate("NapTienWindow", "💳"))
        self.lbl_logo.setText(_translate("NapTienWindow", "Metro Ticket System"))
        self.lbl_subtitle.setText(_translate("NapTienWindow", "Nạp tiền vào ví điện tử"))
        self.lbl_balance_tag.setText(_translate("NapTienWindow", "Số dư hiện tại"))
        self.lbl_balance_value.setText(_translate("NapTienWindow", "Đang tải..."))
        self.lbl_amount_tag.setText(_translate("NapTienWindow", "Số tiền nạp (VNĐ)"))
        self.txt_amount.setPlaceholderText(_translate("NapTienWindow", "Nhập số tiền muốn nạp..."))
        self.lbl_quick_tag.setText(_translate("NapTienWindow", "Chọn nhanh"))
        self.lbl_method_tag.setText(_translate("NapTienWindow", "Phương thức thanh toán"))
        self.btn_naptien.setText(_translate("NapTienWindow", "Xác nhận nạp tiền  ↗"))
        self.lbl_hint.setText(_translate("NapTienWindow", "Quay lại?"))
        self.btn_back.setText(_translate("NapTienWindow", "Trang chủ"))