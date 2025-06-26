from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
import numpy as np
from scipy.stats import laplace
import time as timer
import rpi_ws281x as ws

# LED strip configuration
LED_COUNT = 20
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


class Load(ModelConstructor):
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

    parameters={'houses': 1,  # number of houses that determine the total load demand
                'output_type': 'power',  # type of output for consumption calculation ('energy' or 'power')
                'input_type': 'total',
                'name': 'Load1',
                'total': 5.00
                }
    inputs={'load': 0}  # incoming energy or power demand per house kW
    outputs={ # total energy or power consumption for all houses (kWh) over the time step
             'consumption': 0,  # Current energy or power consumption based on the number of houses and input load (kWh)
             }
    states={'time': None,
            'forecast': None,
            'load_dem_out': 0,
            'load_dem': {}
            }
    time_step_size=1
    time=None

    par1 = 1.003 
    par2 = 0.189
    laplaceMax = laplace.pdf(0, scale=par2)


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
        self.consumption = 0
        self.input_type = self.parameters['input_type']
        self.name = self.parameters['name']
        self.total = self.parameters['total']
        self.previous_dem = 0
        print(f"initialisation houses: {self._model.parameters.get('houses')}")
        
        # Initialize LED strip
        self.strip = ws.PixelStrip(
            LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
            LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
        )
        self.strip.begin()

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

        load_in = input_data.get('load', 0)
        load_out = load_in * self.total

        if self.input_type == 'per_house':
            results = self.demand(load=load_in)
        else:
            results = {'consumption': load_out}

        self.set_outputs(results)
        self.set_states({'load_dem': {self.name: results['consumption']}, 'load_dem_out': -load_out})

        #Green is for base unit W or Wh, yellow is for kW or kWh and red is for MW or MWhh and above. 
        #LEDs blinking indicated load demand is increased, while constant illumination indicates constant or decreased load demand.    
        
        # Update LEDs
        self.update_leds(results['consumption'])

        self.previous_dem = results['consumption']

        return time + self._model.time_step_size

    def update_leds(self, consumption):
        if consumption > 10:
            color = ws.Color(139, 0, 0)
        elif consumption > 7:
            color = ws.Color(255, 200, 0)
        elif consumption > 0:
            color = ws.Color(0, 255, 0)
        else:
            color = ws.Color(0, 0, 0)

        if consumption > self.previous_dem and consumption > 0:
            # blinking if demand increased
            for _ in range(2):
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, color)
                self.strip.show()
                timer.sleep(0.3)

                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, ws.Color(0, 0, 0))
                self.strip.show()
                timer.sleep(0.3)

            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, color)
            self.strip.show()
            timer.sleep(0.4)
        else:
            # constant color
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, color)
            self.strip.show()

    def demand(self, load:float) -> dict:
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
        # incoming load is in kWh at every 15 min interval
        # incoming value of load is in kWh
        houses = self._model.parameters.get('houses')
        output_type = self._model.parameters.get('output_type')
        deltaTime = self.time_resolution * self.time_step_size / 60 / 60

        if output_type == 'energy':
            self.consumption = houses * load # kW
        elif output_type == 'power':
            self.consumption = houses * load * deltaTime # kWh

        re_params = {'load_dem': self.consumption}
        return re_params


if __name__ == '__main__':
    #load_model = Load(load)
    #print("")
    mosaik_api.start_simulation(Load(), 'load Simulator')
