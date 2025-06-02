from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
from illuminator.models.LED.LED_strip_controller import sendPixelData
from serial import Serial
from serial.tools import list_ports


class station(ModelConstructor):
    
    inputs = {
        "LED-configuration": []
    }
    outputs = {
        "ID": []
    }
    
    def __init__(self, *args, **kwargs):
        self.led_data = []
        self.led_table = {} #ID:[port name, send/dummy]
        super().__init__(*args, **kwargs)
        
    def step(self, time: int, inputs: dict = None, max_advance: int = 1):
        """
        1. receive the led-configuration
        2. check if configuration is the same
        3. if not, try to set the leds that are available
        4. update the ID table if nescesarry
        5. send the IDs to the pandalyser
        5.1. send the load and modelconfiguration to the pandalyser        
        """
        self.led_table = {}
        return time + self._model.time_step_size
    
    def set_leds(self, led_configuration: list):
        for led_speed in led_configuration:
            id = led_speed[0]
            speed = led_speed[1]
            strip_id = self.led_table["con_"+str(id)]
            try:
                serialConnection = Serial(strip_id)
                if speed > 255:
                    speed = 255
                    direction = 0
                elif speed < 0:
                    speed = 0
                    direction = 1
                else: 
                    direction = 0
                color = [speed, 255-speed, 0]
                return_data = sendPixelData(serialConnection, speed, direction, color[0], color[1], color[2])
                self.led_data.append(return_data)
            except:
                print("Connection not found! Don't worry, we will go to the next led strip and fix it in the next step.")

    def detect_leds(self):
        comports = list_ports.comports()
        port_list = []
        for port in comports:
            port_list.append(port.name)
        print(port_list)
        #also use the led_data from the previous step
        id_values = list(self.led_table.values())
        current_comports = []
        for id in id_values:
            current_comports.append(id[0])
        print(current_comports)


if __name__ == "__main__":
    station.detect_leds("hi")