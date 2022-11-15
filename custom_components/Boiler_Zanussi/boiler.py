import json
import socket
from .const import MQTT_PORT, MQTT_HOST, DOMAIN, MQTT_USERNAME, MQTT_PASSWORD, TCP_HOST, TCP_PORT
from homeassistant.core import HomeAssistant
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


class Boiler:
    def __init__(self, hass: HomeAssistant, username: str, password: str) -> None:
        self.name = "Boiler_Zanussi"
        self.domain = DOMAIN
        self.icon = "mdi:oil"
        self.class_ = "Boiler"
        self.dev_class = "heating"
        self.unit = "°C"
        self.state = 0
        self.min_temp = 0
        self.max_temp = 75
        self.target_temp = 50
        self.temperature = 0
        self.temp_step = 1
        self.antibacterial = 0
        self.mode = "off"
        self.modes = ["off", "power1", "power2", "power3", "timer", "nofrost"]
        self.supported_features = 3
        self.device_id = 10001
        self.hass = hass
        self.attributes = {
            "min_temp": self.min_temp,
            "max_temp": self.max_temp,
            "target_temp": self.target_temp,
            "temp_step": self.temp_step,
            "antibacterial": self.antibacterial,
            "temperature": self.temperature,
            "mode": self.mode,
            "modes": self.modes,
            "supported_features": self.supported_features,
        }
        self.payload = {
            "name": self.name,
            "domain": self.domain,
            "icon": self.icon,
            "class": self.class_,
            "dev_class": self.dev_class,
            "unit": self.unit,
            "state": self.state,
            "attributes": self.attributes,
        }

        self.server_address = (TCP_HOST, TCP_PORT)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)
        self.current_state = 0

        self.payload_json = json.dumps(self.payload)
        self.topic = "homeassistant/sensor/" + self.name + "/config"
        self.host = MQTT_HOST
        self.port = MQTT_PORT
        self.username = MQTT_USERNAME
        self.password = MQTT_PASSWORD
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_log = self.on_log
        self.mqttc.username_pw_set(self.username, self.password)
        self.mqttc.connect(self.host, self.port, 60)
        self.mqttc.loop_start()

    def get_state(self):  # Get current state of boiler
        self.server_socket.listen(1)
        connection, address = self.server_socket.accept()
        while True:
            await self.hass.async_add_executor_job(
                self.send_data, bytes.fromhex("AA03081004C9"), connection  # Get current state
            )
            # self.send_data(bytes.fromhex("AA03081004C9")) # Request state. AA03081004C9 hex command to get state # OLD
            data = connection.recv(4096)
            if len(data) == 13:
                connection.close()
                self.current_state = data
                if data[3] == 0:
                    self.mode = self.modes[0]
                    self.state = 0
                elif data[3] == 1:
                    self.mode = self.modes[1]
                    self.state = 1
                elif data[3] == 2:
                    self.mode = self.modes[2]
                    self.state = 2
                elif data[3] == 3:
                    self.mode = self.modes[3]
                    self.state = 3
                elif data[3] == 4:
                    self.mode = self.modes[4]  # TODO timer mode: add to modes
                    self.state = 4
                elif data[3] == 5:
                    self.mode = self.modes[5]
                    self.state = 5
                else:
                    self.mode = self.modes[0]
                self.temperature = data[4]
                self.target_temp = data[5]
                # if self.state == BoilerState.POWER_TIMER: # TODO timer mode
                #     self.timer_days = data[8]
                #     self.timer_hours = data[9]
                self.antibacterial = data[11]
                return 0

    def set_state(self):
        if (self.mode in self.modes) and (self.target_temp in range(self.min_temp, self.max_temp)):
            hex_string = r"AA040A000" + hex(self.state)[2:] + hex(self.target_temp)[2:]
            sum = (184 + self.state + self.target_temp) % 256 # Calculate checksum. 184 is sum of constant string AA040A000
            if sum < 10:
                hex_string += "0" + hex(sum)[2:]
            else:
                hex_string += hex(sum)[2:]
            self.server_socket.listen(1)
            connection, address = self.server_socket.accept()
            await self.hass.async_add_executor_job(
                self.send_data, bytes.fromhex(hex_string), connection
            )
            if (self.antibacterial == 0):
                hex_string = r"AA030A0300BA"
            else:
                hex_string = r"AA030A0301BB"
            await self.hass.async_add_executor_job(
                self.send_data, bytes.fromhex(hex_string), connection
            )
            connection.close()
            return 0
        else:
            return 1

    def send_data(self, data, connection):  # Send data in hex format to boiler
        connection.sendto(data, (TCP_HOST, TCP_PORT))
        # from time import sleep # OLD
        from asyncio import sleep
        sleep(1)
        connection.sendto(data, (TCP_HOST, TCP_PORT))
        sleep(1)
        connection.sendto(data, (TCP_HOST, TCP_PORT))

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        self.payload_json = msg.payload
        self.payload = json.loads(self.payload_json)
        self.state = self.payload["state"]
        self.target_temp = self.payload["attributes"]["target_temp"]
        self.antibacterial = self.payload["attributes"]["antibacterial"]
        self.set_state()

    def on_publish(self, client, userdata, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)

    def update(self) -> None:
        self.get_state()
        self.payload = {
            "state": self.state,
            "attributes": self.attributes,
        }
        self.payload_json = json.dumps(self.payload)
        self.mqttc.publish(self.topic, self.payload_json, 0, False)

