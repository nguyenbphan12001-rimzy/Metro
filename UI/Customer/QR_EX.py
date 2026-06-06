from UI.Customer.QR import Ui_QRPaymentDialog


class QR_EX(Ui_QRPaymentDialog):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow= MainWindow