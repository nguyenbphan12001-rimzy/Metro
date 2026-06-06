from UI.admin.price import Ui_PricingWindow


class price_EX(Ui_PricingWindow):
    def setupUI(self, MainWindow):
        super().setupUi(self, MainWindow)
        self.MainWindow = MainWindow

