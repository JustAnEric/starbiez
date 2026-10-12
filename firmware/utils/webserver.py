from adafruit_httpserver import Server, Request, Response
import wifi
import socketpool
import json
from utils.tama import globals

class WS:
    def __init__(self, main_app):
        self.pool = socketpool.SocketPool(wifi.radio)
        self.server = Server(
            self.pool,
            root_path="/starbiez",
            debug=True,
        )
        self.main_app = main_app

        @self.server.route("/")
        def base(request: Request):
            return Response(request, "Welcome to the Starbiez web server! You can use this to see your stats about your Tamagotchi, or reprogram it in <code>utils/webserver.py</code>!<br/><br/><ul><li>/starbiez/stat</li><li>/starbiez/sensor</li></ul>", content_type="text/html")

        @self.server.route("/stat")
        def stat(request: Request):
            state = {
                "joy": self.main_app.petState.joy,
                "energy": self.main_app.petState.energy,
                "fullness": self.main_app.petState.fullness
            }
            return Response(request, json.dumps(state), content_type="application/json")

        @self.server.route("/sensor")
        def sensor(request: Request):
            state = {}
            if self.main_app.dhtFound and self.main_app.DHT:
                state['dht'] = {
                    'type': globals.DHT_TYPE,
                    'tempC': self.main_app.temperatureC,
                    'humidity': self.main_app.humidity
                }
            if self.main_app.mpuFound and self.main_app.MPU:
                state['mpu'] = {
                    'accel_range': self.main_app.MPU.accelerometer_range,
                    'gyro_range': self.main_app.MPU.gyro_range,
                    'filter_bandwidth': self.main_app.MPU.filter_bandwidth,
                    'address': globals.I2C.get("MPU6050_ADDRESS", 0x68)
                }

        self.server.serve_forever(str(wifi.radio.ipv4_address), 443, poll_interval=16/1000) # 16 requests per second as per the main code.py file