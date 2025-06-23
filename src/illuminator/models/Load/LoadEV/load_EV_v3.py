from illuminator.builder import ModelConstructor
import time as timer
import rpi_ws281x as ws

# LED strip configuration
LED_COUNT = 7
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 204  # 0.8 * 255 ≈ 204
LED_INVERT = False
LED_CHANNEL = 0

class LoadEV(ModelConstructor):
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

    parameters={'houses_case': None,  # number of EVs you want to model
                'houses_data': None,  # number of EVs for which the profile is for
                'name': 'EV1'
                }
    inputs={'power': {},
             'n': 0,  # # n is number of EVs charging at a certain point in time (its in the database but unused for now)
            }
    outputs={'load_EV': 0,  #
             }
    states={}
    time_step_size=1
    time=None


    def __init__(self, **kwargs) -> None:
        """
        Initialize Load model with given parameters.

        Parameters
        ----------
        kwargs : dict
            
        Returns
        -------
        None
        """
        super().__init__(**kwargs)
        self.houses_case = self.parameters['houses_case']
        self.houses_data = self.parameters['houses_data']
        self.name = self.parameters['name']
        
        # Initialize LED strip
        self.strip = ws.PixelStrip(
            LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
            LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
        )
        self.strip.begin()

    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Performs a single simulation time step by calculating EV load demand.

        Parameters
        ----------
        time : float
            Current simulation time in seconds
        inputs : dict
            Dictionary containing input values including 'power' and 'n'
        max_advance : int, optional
            Maximum time step advancement, defaults to 900
            
        Returns
        -------
        float
            Next simulation time step
        """

        input_data = self.unpack_inputs(inputs)
        self.time = time

        load_in = input_data['power'][self.name]
        n = input_data.get('n', 0)
        results = self.demand(power=load_in, n=n)
        self.set_outputs({'load_EV': results['load_EV']})

        #Green is for base unit W or Wh, yellow is for kW or kWh and red is for MW or MWhh and above. 
        #LEDs blinking indicated load demand is increased, while constant illumination indicates constant or decreased load demand.         
        
        # Update LEDs
        self.update_leds(results['load_EV'])

        self.previous_dem = results['load_EV']  

        return time + self._model.time_step_size

    def update_leds(self, load_EV):
        if load_EV > 1_000_000:
            color = ws.Color(139, 0, 0)
        elif load_EV > 1_000:
            color = ws.Color(255, 200, 0)
        elif load_EV > 0:
            color = ws.Color(0, 255, 0)
        else:
            color = ws.Color(0, 0, 0)

        if load_EV > self.previous_dem and load_EV > 0:
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

    def demand(self, power:float, n:int) -> dict:
        """
        Calculates total EV load demand based on power per EV and number of EVs.

        Parameters
        ----------
        power : float
            Power consumption per EV in kWh per 15-min interval
        n : int
            Number of EVs charging at current time step
            
        Returns
        -------
        re_params : dict
            Dictionary containing EV load demand and number of EVs
        """
        # incoming load is in kWh at every 15 min interval
        # incoming value of load is in kWh
        if self.houses_case == self.houses_data:
            consumption = power
        else:
            consumption = power * self.houses_case/self.houses_data # scaling if necessary
        re_params = {'load_EV': consumption, 'n': n}
        return re_params
        
if __name__ == '__main__':
    mosaik_api.start_simulation(LoadEV(), 'Battery Simulator')
