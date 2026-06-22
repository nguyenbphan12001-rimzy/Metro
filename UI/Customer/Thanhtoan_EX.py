from UI.Customer.Thanhtoan import Ui_MetroBookingForm


class ThanhToan_EX(Ui_MetroBookingForm):
    def setupUi(self, MainWindow, user_id):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.user_id = user_id