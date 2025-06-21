from illuminator.builder import ModelConstructor

import time as timer
import rpi_ws281x as ws

# LED strip configuration
LED_COUNT = 20      # Number of LED pixels.
LED_PIN = 18        # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10         # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255 # Set to 0 for darkest and 255 for brightest
LED_INVERT = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0

# Define the model class
class Battery(ModelConstructor):

    parameters = {
        'max_p': 150,
        'min_p': 250,
        'max_energy': 50,
        'charge_efficiency': 90,
        'discharge_efficiency': 90,
        'soc_min': 3,
        'soc_max': 80,
    }

    inputs = {'flow2b': 0}

    outputs = {
        'p_out': 20,
        'p_in': 20,
    }

    states = {
        'mod': 0,
        'soc': 0,
        'flag': -1
    }

    time_step_size = 1
    time = None

    def _init_(self, **kwargs):
        super()._init_(**kwargs)

        self.soc = self._model.states.get('soc')
        self.flag = self._model.states.get('flag')
        self.mod = self._model.states.get('mod')

        self.charge_efficiency = self._model.parameters.get('charge_efficiency') / 100
        self.discharge_efficiency = self._model.parameters.get('discharge_efficiency') / 100
        self.max_p = self._model.parameters.get('max_p')
        self.min_p = self._model.parameters.get('min_p')
        self.max_energy = self._model.parameters.get('max_energy')
        self.soc_min = self._model.parameters.get('soc_min')
        self.soc_max = self._model.parameters.get('soc_max')

        self.powerout = 0

        # Initialize LED strip
        self.strip = ws.PixelStrip(
            LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
            LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
        )
        self.strip.begin()

    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> int:
        input_data = self.unpack_inputs(inputs)

        results = self.output_power(input_data['flow2b'])

        self.soc = results.pop('soc')
        self.flag = results.pop('flag')
        self.mod = results.pop('mod')

        self.set_states({'soc': self.soc, 'flag': self.flag, 'mod': self.mod})
        self.set_outputs(results)

        # Update LEDs
        self.update_leds()

        timer.sleep(1)

        return time + self._model.time_step_size

    def update_leds(self):
        # Determine color based on SOC
        if self.soc < 21:
            color = ws.Color(139, 0, 0)
        elif self.soc < 41:
            color = ws.Color(255, 40, 0)
        elif self.soc < 61:
            color = ws.Color(255, 200, 0)
        elif self.soc < 81:
            color = ws.Color(142, 255, 0)
        else:
            color = ws.Color(0, 255, 0)

        # Set all LEDs to this color
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def discharge_battery(self, flow2b: int) -> dict:
        hours = self.time_resolution / 3600
        flow = max(self.min_p, flow2b)

        if flow < 0:
            energy2discharge = flow * hours / self.discharge_efficiency
            energy_capacity = ((self.soc_min - self.soc) / 100) * self.max_energy

            if self.soc <= self.soc_min:
                self.flag = -1
                self.powerout = 0
            else:
                if energy2discharge > energy_capacity:
                    self.soc += (energy2discharge / self.max_energy * 100)
                    self.powerout = flow
                    self.flag = 0
                else:
                    self.powerout = energy_capacity * self.discharge_efficiency / hours
                    self.soc = self.soc_min
                    self.flag = -1

        self.soc = round(self.soc, 3)
        return {
            'p_out': self.powerout,
            'p_in': flow,
            'soc': self.soc,
            'mod': -1,
            'flag': self.flag
        }

    def charge_battery(self, flow2b: int) -> dict:
        hours = self.time_resolution / 3600
        flow = min(self.max_p, flow2b)

        if flow > 0:
            energy2charge = flow * hours * self.charge_efficiency
            energy_capacity = ((self.soc_max - self.soc) / 100) * self.max_energy

            if self.soc >= self.soc_max:
                self.flag = 1
                self.powerout = 0
            else:
                if energy2charge <= energy_capacity:
                    self.soc += (energy2charge / self.max_energy * 100)
                    self.powerout = flow
                    self.flag = 0
                else:
                    self.powerout = energy_capacity / self.charge_efficiency / hours
                    self.soc = self.soc_max
                    self.flag = 1

        self.soc = round(self.soc, 3)
        return {
            'p_out': self.powerout,
            'p_in': flow,
            'soc': self.soc,
            'mod': 1,
            'flag': self.flag
        }

    def output_power(self, flow2b: int) -> dict:
        if flow2b == 0:
            if self.soc >= self.soc_max:
                self.flag = 1
            elif self.soc <= self.soc_min:
                self.flag = -1
            else:
                self.flag = 0

            return {
                'p_out': 0,
                'p_in': 0,
                'soc': self.soc,
                'mod': 0,
                'flag': self.flag
            }

        elif flow2b < 0:
            return self.discharge_battery(flow2b)
        else:
            return self.charge_battery(flow2b)