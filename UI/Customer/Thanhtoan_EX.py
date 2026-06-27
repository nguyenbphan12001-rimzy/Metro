from UI.Customer.Thanhtoan import Ui_MetroBookingForm


class ThanhToan_EX(Ui_MetroBookingForm):
    def setupUi(self, MetroBookingForm, conn=None, user_id=None):
        super().setupUi(MetroBookingForm)
        self.conn = conn
        self.user_id = user_id

        self.load_routes()
        self.comboLine.currentIndexChanged.connect(self.load_stations_by_route)
        self.load_stations_by_route()

    def load_routes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT route_id, route_name FROM ROUTE")
        self.comboLine.clear()
        for route_id, route_name in cursor.fetchall():
            self.comboLine.addItem(route_name, userData=route_id)

    def load_stations_by_route(self):
        route_id = self.comboLine.currentData()
        if route_id is None:
            return
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.station_id, s.station_name
            FROM ROUTESTATION rs
            JOIN STATION s ON rs.station_id = s.station_id
            WHERE rs.route_id = ?
            ORDER BY rs.position
        """, route_id)
        stations = cursor.fetchall()

        self.comboFrom.clear()
        self.comboTo.clear()
        for station_id, station_name in stations:
            self.comboFrom.addItem(station_name, userData=station_id)
            self.comboTo.addItem(station_name, userData=station_id)