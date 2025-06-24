from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
import serial
import time
from numpy import ceil
from illuminator.models.LED.LED_strip_controller import sendPixelData
import pandas as pd



class LED_connection(ModelConstructor):
    """
    Calculates total load demand based on number of houses and input load.

    Parameters
    ----------
    load : float
        Input load per house in kW or kWh depending on output_type
        
    Returns
    -------
    re_params : dict
        Dictionary containing calculated load demand values
    """

    parameters={'max_delay': 100,  # maximum speed for the connection
                'direction': 0,  # direction of the connection (towards the unit)
                'port': None,
                'file_path': 'examples/BAP-2025-Simulation/demo_line_specs.csv'
                }
    inputs={'power': 0}  # speed for the connection
    outputs={
             }
    states={
            }
    time_step_size=1
    time=None

    def __init__(self, *args, **kwargs):
        return super().__init__(**kwargs)

    def init(self, *args, **kwargs) -> None:
        """
        Initialize Load model with given parameters.

        Parameters
        ----------
        kwargs : dict
            Dictionary containing model parameters and initial states
            
        Returns
        -------
        None
        """
        result = super().init(*args, **kwargs)
        print(result)
        self.max_delay = self.parameters.get('max_delay')
        self.direction = self.parameters.get('direction')
        self.port = self.parameters.get('port')
        self.file_path = self.parameters.get('file_path')

        try:
            connection = serial.Serial(self.port, timeout=1)

            self.id, _ = sendPixelData(connection, 0, 0, 0, 0, 0)
        except:
            print("no Serial connection")
        
        try:
            df = pd.read_csv(self.file_path)
        except:
            print("oops, no file available")
        line = df[df['line_id'] == self.id]
        self.line_capacity = float(line['capacity']*line['prim_kv_rating'])

        self.ps_ratio = self.line_capacity/self.max_delay # Power to speed ratio
        
        
        return result

    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Performs a single simulation time step by calculating load demand.

        Parameters
        ----------
        time : float
            Current simulation time in seconds
        inputs : dict
            Dictionary containing input values including 'load'
        max_advance : int, optional
            Maximum time step advancement, defaults to 1
            
        Returns
        -------
        float
            Next simulation time step
        """
        input_data = self.unpack_inputs(inputs)
        self.time = time

        power = float(input_data['power'][f'line_{self.id}']) # Selects the power corresponding to its own line_ID
        speed = self.ps_ratio*power
        direction = self.direction
        print("got speed: ", speed)

        if speed < 0:
            direction = not direction
            speed *=-1


        self.send_led_animation(speed, direction)
        return time + self._model.time_step_size
    

    def send_led_animation(self, speed, direction) -> None:
        device = self.port
        ser = serial.Serial(device, timeout=1)
        line = ''

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(line)
        
        if speed > 100:
            colour = [255,0,0]
            delay = 0
        else:
            delay = max(0, min(255, ceil(255 * speed/100)))  # Maps 0-100% to 0-255, with bounds checking
            delay = round(delay)

            colour = [255-delay, delay, 0]

        print(f"speed: {speed}%, Sending {delay}{colour}")
        sendPixelData(ser, int(delay), True, colour[0], colour[1], colour[2])
        time.sleep(3)

        return


if __name__ == '__main__':
    #send_led_animation()
    mosaik_api.start_simulation(LED_connection(), 'LED connection Simulator')
    #led = LED_connection()
    #led.init("LED-connection", sim_params = {'name': 'Station4', 'type': 'Station', 'parameters': {'station_ID': 'Station4', 'kv': 380}, 'inputs': {'cp_powers': {}, 'tl_powers': {}}, 'states': {'cp_powers': {}, 'transmit': {}}, 'outputs': {'USBchange': False}, 'connect': {'ip': '192.168.0.8', 'port': 5102}})

