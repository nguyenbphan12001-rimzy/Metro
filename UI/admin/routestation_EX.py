from UI.admin.routestation import Ui_RouteStationWindow


class routestation_Ex(Ui_RouteStationWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
