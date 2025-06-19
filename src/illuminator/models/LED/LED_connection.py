from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
import serial
import time as t
from numpy import ceil
from illuminator.models.LED.LED_strip_controller import sendPixelData



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

    parameters={'min_speed': 0,  # minimum speed for the connection
                'max_speed': 0.5,  # maximum speed for the connection
                'direction': 0,  # direction of the connection (towards the unit)
                'port': None,
                'file_path': 'line_specs.csv'
                }
    inputs={'power': 0}  # speed for the connection
    outputs={
             }
    states={
            }
    time_step_size=1
    time=None


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
        self.min_speed = self.parameters.get('min_speed')
        self.max_speed = self.parameters.get('max_speed')
        self.direction = self.parameters.get('direction')
        self.port = self.parameters.get('port')
        self.file_path = self.parameters.get('file_path')

        connection = serial.Serial(self.port, timeout=1)
        self.id = 0
        while self.id == 0:
            self.id = int.from_bytes(connection.read(1))

        df = pd.read_csv(self.file_path)
        line = df[df['line_id'] == self.id]
        self.line_capacity = float(line['capacity'])

        self.ps_ratio = self.max_speed/self.line_capacity # Power to speed ratio
        
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
            direction = 1 - direction
            speed *=-1

        if speed <= self.min_speed:
            speed = 0
        # elif speed >= self.max_speed:
        #     speed = 100
        else:
            speed = ((speed - self.min_speed) / (self.max_speed - self.min_speed)) * 100

        #self.send_led_animation(speed, direction)
        # self.set_outputs(results)
        t.sleep(1)

        return time + self._model.time_step_size
    

    def send_led_animation(self, speed, direction) -> None:
        device = self.port
        ser = serial.Serial(device, timeout=1)
        line = ''

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(line)
        
        if speed == 0:
            colour = [0,255,0]
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
