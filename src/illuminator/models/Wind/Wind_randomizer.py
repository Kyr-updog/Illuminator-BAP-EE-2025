from illuminator.builder import ModelConstructor

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta as beta_dist
import matplotlib.dates as mdates
import datetime

# construct the model
class WindRandomizer(ModelConstructor):
    # Define the model parameters, inputs, outputs, and states
    parameters={'type': 'offshore'
                }
    inputs={}
    outputs={'fraction': 0
             }
    states={'s': 0,
            'ds': 0,
            'dds': 0
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
        self.type = self.parameters['type']

        self.s = self._model.states.get('s')
        self.ds = self._model.states.get('ds')
        self.dds = self._model.states.get('dds')

        self.infinitesimal = 1e-6
        self.dt = self.time_resolution/3600

        self.s_init = -1
        self.ds_init = 0.3

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

        self.set_states({'s': self.s, 'ds': self.ds, 'dds': self.dds})
        self.set_outputs({'fraction': fraction})

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    


    def sigmoid(g):
        return 1 / (1 + np.exp(-g))
    

    def dUds(self, g):
        s = self.sigmoid(g)
        s = np.clip(s, self.infinitesimal, 1 - self.infinitesimal)
        return (self.distrAlpha/s - self.distrBeta/(1-s)) * s * (1-s)

