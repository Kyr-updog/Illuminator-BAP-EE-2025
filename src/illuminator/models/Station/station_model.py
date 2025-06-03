from illuminator.builder import ModelConstructor

# construct the model
class Station(ModelConstructor):
    # Define the model parameters, inputs, outputs, and states
    parameters={'Station_ID': 'Station1'
                }
    inputs={'cp_powers': {}, # from controller
            'tl_powers': {}, # from controller
            'received_speeds': {} # from other station (not used)
            }
    outputs={}
    states={'cp_powers': {}, # to controllable peripherals
            'transmitted_speeds': {} # to LEDs
            }
    
    # define other attributes
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the station model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
                Additional keyword arguments to initialize the...
        """
        super().__init__(**kwargs)
        self.line_reactances = self.parameters['line_reactances']
        self.line_capacities = self.parameters['line_capacities']



    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        Args:
            time (float): Current simulation time in seconds
            inputs (dict): Dictionary containing input values:
                -
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 1.
        Returns:
            float: Next simulation time in seconds
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time

        ncp_power = input_data['ncp_power']
        cp_power = input_data['cp_power']
        tl_powers = input_data['tl_powers']

        results = self.routing(ncp_power, cp_power, tl_powers)
        self.ncp_power = results.pop('ncp_power')

        self.set_states({'ncp_power': self.ncp_power})
        self.set_outputs(results)

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    
    

    def routing(self, ncp_power, cp_power, tl_powers) -> dict:
        # TODO: isolate relevant tl_powers !!!!
        re_params = {'cp_power': cp_power, 'sent_tl_powers': tl_powers, 'ncp_power': ncp_power}
        return re_params