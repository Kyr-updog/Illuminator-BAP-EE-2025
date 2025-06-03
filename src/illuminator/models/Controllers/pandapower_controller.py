from illuminator.builder import ModelConstructor
import pandapower as pp
import pandas as pd

# construct the model
class PandaController(ModelConstructor):
    # Define the model parameters, inputs, outputs, and states
    parameters={'peripherals': {},                          
                'stations': {},
                'ps_connections': {},
                'ss_connections': {},
                'lines_file_path': '' # File contains line ID's with their reactances and capacities
                }
    inputs={'ncp_powers': {}
            }
    outputs={} # No outputs
    states={'cp_powers': {},
            'tl_powers': {}
            }
    
    # define other attributes
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the analyzer/controller model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the...
        """
        super().__init__(**kwargs)
        self.stations = self.parameters['stations']
        self.connections = self.parameters['connections']
        self.lines_file_path = self.parameters['lines_file_path']

        # Build graph here !!!
        net = pp.create_empty_network()
        for station in self.stations:
            pp.create_bus(net, vn_kv=360., name='%s' % station)

        lines = pd.read_csv(self.lines_file_path)

         

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

        ncp_powers = input_data['ncp_powers']

        results = self.control_and_analysis(ncp_powers)

        self.set_states(results)

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    


    def control_and_analysis(self, ncp_powers) -> dict:
        pass