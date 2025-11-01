import sys, requests
from PyQt5.QtCore import Qt, QRectF, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QGraphicsOpacityEffect)

BASE_URL = "https://api.open-meteo.com/v1/forecast"

CITY_COORDS = {
    "algiers": (36.75, 3.06),
    "cairo": (24),
    "riyadh": (24.71, 46.67),
    "paris": (48.85, 2.35),
    "london": (51.51, -0.13),
    "new york": (40.71, -74.01),
    "tokyo": (35.68, 139.69),
    "berlin": (52.52, 13.40),
    "moscow": (55.75, 37.62),
    "sydney": (-33.87, 151.21)
}

#30.05, 31.25)

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.oldPos = self.pos()
        self.startup_animation()

    def init_ui(self):
        self.setWindowTitle("Weather App")
        self.setGeometry(450, 200, 420, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main_widget = QWidget(self)
        self.main_widget.setStyleSheet("background-color: #f5f5f5; border-radius: 20px;")
        self.main_widget.setGeometry(0, 0, 420, 500)

        title = QLabel("🌍 Weather App", self.main_widget)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.city_input = QLineEdit(self.main_widget)
        self.city_input.setPlaceholderText("Enter city (e.g., Algiers, Paris...)")
        self.city_input.setFont(QFont("Arial", 12))
        self.city_input.setStyleSheet("padding: 6px; border: 1px solid gray; border-radius: 10px;")

        self.search_btn = QPushButton("🔍 Get Weather", self.main_widget)
        self.search_btn.clicked.connect(self.get_weather)
        self.search_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 10px;")

        exit_btn = QPushButton("❌ Exit", self.main_widget)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; border-radius: 10px;")

        minimize_btn = QPushButton("➖ Minimize", self.main_widget)
        minimize_btn.clicked.connect(self.showMinimized)
        minimize_btn.setStyleSheet("background-color: #3498db; color: white; padding: 8px; border-radius: 10px;")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.search_btn)
        btn_layout.addWidget(minimize_btn)
        btn_layout.addWidget(exit_btn)

        self.weather_icon = QLabel(self.main_widget)
        self.weather_icon.setAlignment(Qt.AlignCenter)
        self.weather_icon.setFixedHeight(150)

        self.result = QLabel("", self.main_widget)
        self.result.setFont(QFont("Arial", 14))
        self.result.setAlignment(Qt.AlignCenter)
        self.result.setWordWrap(True)

        vbox = QVBoxLayout(self.main_widget)
        vbox.addWidget(title)
        vbox.addSpacing(10)
        vbox.addWidget(self.city_input)
        vbox.addLayout(btn_layout)
        vbox.addSpacing(20)
        vbox.addWidget(self.weather_icon)
        vbox.addWidget(self.result)
        vbox.setSpacing(15)
        vbox.setContentsMargins(20, 20, 20, 20)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.main_widget)

        # تأثير شفافية
        self.opacity_effect = QGraphicsOpacityEffect()
        self.result.setGraphicsEffect(self.opacity_effect)


        print("all ok")

    # -------- Animations ----------
    def startup_animation(self):
        """ نافذة تدخل بانيميشن عند البداية """
        self.resize(0, 0)
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(1000)
        anim.setStartValue(self.geometry().adjusted(210, 250, -210, -250))
        anim.setEndValue(self.geometry())
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        self.start_anim = anim

    def animate_drop_icon(self):
        """ الأيقونة تنزل من فوق مع bounce """
        start_geo = self.weather_icon.geometry()
        anim = QPropertyAnimation(self.weather_icon, b"geometry")
        anim.setDuration(800)
        anim.setStartValue(start_geo.translated(0, -200))
        anim.setEndValue(start_geo)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        self.drop_anim = anim

    def animate_slide_result(self):
        """ النص يطلع من الجنب بانزلاق """
        start_geo = self.result.geometry()
        anim = QPropertyAnimation(self.result, b"geometry")
        anim.setDuration(600)
        anim.setStartValue(start_geo.translated(-400, 0))
        anim.setEndValue(start_geo)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self.slide_anim = anim

    def animate_pulse_button(self, btn):
        """ الزر يعمل pulse صغير """
        start_geo = btn.geometry()
        anim = QPropertyAnimation(btn, b"geometry")
        anim.setDuration(500)
        anim.setKeyValueAt(0, start_geo)
        anim.setKeyValueAt(0.5, start_geo.adjusted(-5, -5, 5, 5))
        anim.setKeyValueAt(1, start_geo)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        btn.anim = anim

    def shake_window(self):
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(500)
        anim.setKeyValueAt(0, self.pos())
        anim.setKeyValueAt(0.2, self.pos() + QPoint(-15, 0))
        anim.setKeyValueAt(0.4, self.pos() + QPoint(15, 0))
        anim.setKeyValueAt(0.6, self.pos() + QPoint(-15, 0))
        anim.setKeyValueAt(0.8, self.pos() + QPoint(15, 0))
        anim.setKeyValueAt(1, self.pos())
        anim.setEasingCurve(QEasingCurve.OutElastic)
        anim.start()
        self.animation = anim


        print("beeep beeep")

    # -------- Weather ----------
    def get_weather(self):
        city = self.city_input.text().strip().lower()
        if city not in CITY_COORDS:
            self.shake_window()
            QMessageBox.warning(self, "Error", "❌ City not supported!\nTry: " + ", ".join(CITY_COORDS.keys()))
            return

        self.animate_pulse_button(self.search_btn)

        lat, lon = CITY_COORDS[city]
        params = {"latitude": lat, "longitude": lon, "current_weather": True}
        try:
            resp = requests.get(BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.result.setText(f"Error: {e}")
            return

        weather = data.get("current_weather")
        if not weather:
            self.result.setText("⚠️ No weather data.")
            return

        temp = weather["temperature"]
        wind = weather["windspeed"]
        time = weather["time"]
        code = weather["weathercode"]

        icon_url = self.get_icon(code)
        pix = QPixmap()
        pix.loadFromData(requests.get(icon_url).content)
        self.weather_icon.setPixmap(pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.result.setText(
            f"📍 {city.capitalize()}\n"
            f"🌡️ {temp} °C\n"
            f"💨 {wind} km/h\n"
            f"⏰ {time}\n"
            f"📝 {self.get_desc(code)}"
        )

        # play animations
        self.animate_drop_icon()
        self.animate_slide_result()

    def get_icon(self, code):
        if code in [0]: return "https://cdn-icons-png.flaticon.com/512/869/869869.png"
        elif code in [1, 2]: return "https://cdn-icons-png.flaticon.com/512/1163/1163624.png"
        elif code in [3]: return "https://cdn-icons-png.flaticon.com/512/414/414825.png"
        elif code in [45, 48]: return "https://cdn-icons-png.flaticon.com/512/4005/4005901.png"
        elif code in [51, 61, 80]: return "https://cdn-icons-png.flaticon.com/512/1163/1163657.png"
        elif code in [71, 85]: return "https://cdn-icons-png.flaticon.com/512/2315/2315309.png"
        else: return "https://cdn-icons-png.flaticon.com/512/1779/1779940.png"

    def get_desc(self, code):
        mapping = {
            0: "Clear sky ☀️",
            1: "Mainly clear 🌤️",
            2: "Partly cloudy ⛅",
            3: "Overcast ☁️",
            45: "Fog 🌫️",
            48: "Depositing rime fog 🌫️",
            51: "Light drizzle 🌦️",
            61: "Rain showers 🌧️",
            71: "Snow showers ❄️",
            80: "Heavy rain 🌧️",
            85: "Snow ❄️",
        }
        return mapping.get(code, "Unknown")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def paintEvent(self, e):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 20, 20)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillPath(path, Qt.white)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("lala the first dosent work")
    win = WeatherApp()
    print("two")
    win.show()
    print("third")
    sys.exit(app.exec_())
