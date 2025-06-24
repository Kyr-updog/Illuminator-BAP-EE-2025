import serial.tools
import serial.tools.list_ports
from illuminator.builder import ModelConstructor
import mosaik_api_v3 as mosaik_api

# construct the model
class Station(ModelConstructor):
    # Define the model parameters, inputs, outputs, and states
    parameters={'station_ID': 'Station1',
                'kv': 380
                }
    inputs={'cp_powers': {}, # from controller
            'tl_powers': {}, # from controller
            }
    outputs={"USBchange": False}#for detecting changes in the connections
    states={'cp_powers': {}, # to controllable peripherals
            'transmit': {} # to LEDs
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
        self.station_ID = self.parameters['station_ID']
        self.kv = self.parameters['kv']

        self.connections = serial.tools.list_ports.comports()


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

        cp_powers = input_data['cp_powers']
        tl_powers = input_data['tl_powers']

        results = self.routing(cp_powers, tl_powers)

        self.set_states(results)


        current_connections = serial.tools.list_ports.comports()
        
        old_connections = []
        for port in self.connections:
            old_connections.append(str(port))
        
        self.set_outputs({"USBchange": False})
        
        for port in current_connections:
            if str(port) not in str(old_connections): #detects if all comports are still present (port change or added)
                self.set_outputs({"USBchange": True})
                
        if len(old_connections) != len(current_connections): #detects if a comport is removed
            self.set_outputs({"USBchange": True})

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    
    

    def routing(self, cp_powers, tl_powers) -> dict:
        sent_cp_powers = cp_powers[self.station_ID]
        transmit = tl_powers[self.station_ID]
        re_params = {'cp_powers': sent_cp_powers, 'transmit': transmit}
        return re_params
        
if __name__ == "__main__":
    mosaik_api.start_simulation(Station(), "station sim")
