from illuminator.builder import ModelConstructor

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta as beta_dist
import matplotlib.dates as mdates
import datetime

# construct the model
class WindRandomizer(ModelConstructor):
    # Define the model parameters, inputs, outputs, and states
    parameters={'area_type': 'offshore'
                }
    inputs={}
    outputs={'fraction_out': 0
             }
    states={'s': -1,
            'ds': 0.3,
            'dds': 0,
            'fraction': 0
            }
    
    # define other attributes
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the nuclear generator model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
                Additional keyword arguments to initialize the...
        """
        super().__init__(**kwargs)
        self.type = self.parameters['area_type']

        self.fac = 0.5

        self.s = self._model.states.get('s')
        self.ds = self._model.states.get('ds')
        self.dds = self._model.states.get('dds')

        self.infinitesimal = 1e-6
        self.dt = 600.00/3600.00

        if self.type == 'offshore':
            self.a = 0.779
            self.b = 0.260
            self.distrAlpha = 0.480
            self.distrBeta = 0.229
        else:
            self.a = 0.420
            self.b = 0.090
            self.distrAlpha = 0.550
            self.distrBeta = 1.007
         

    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        Args:
            time (float): Current simulation time in seconds
            inputs (dict): Dictionary containing input values:
            - req_pow (float): Power required of the generator
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 1.
        Returns:
            float: Next simulation time in seconds
        """
        self.time = time

        self.dds = self.b ** 2 / (2 * self.a) * self.dUds(self.s) - self.a * self.ds + self.b * np.sqrt(self.dt) * np.random.randn() / self.dt
        self.ds = self.ds + self.dds * self.dt
        self.s = self.s + self.ds * self.dt

        fraction = self.sigmoid(self.s)

        self.set_states({'s': self.s, 'ds': self.ds, 'dds': self.dds, 'fraction': fraction})
        self.set_outputs({'fraction_out': fraction})

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    


    def sigmoid(self, g):
        return 1 / (1 + np.exp(-g/self.fac))
    

    def dUds(self, g):
        result = (self.distrAlpha - self.distrBeta * np.exp(g/self.fac)) / (self.fac * (np.exp(g/self.fac) + 1))
        return result

