from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
from .Dynamic_yaml_scenario_module import *

class TopologyMaker(ModelConstructor):

    parameters = {'filename': 'default.yaml'}
    inputs = {'config':{}}
    
    def __init__(self, *args, **kwargs):
        result = super().__init__(*args, **kwargs)
        return result
        
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:
        input = self.unpack_inputs(inputs)
        network = []
        for device in input['config']:#make the input one giant list for the mapping function
            for led_strip in device:
                network.append(led_strip[0:3])
        
        #connected_pairs = determine_connected_pairs(network)
        #topology = write_topology(connected_pairs)
        #filename = self._model.parameters.get('filename')
        #read_and_copy_yaml_data_plus_add_data_to_new_file(filename, 'simulation', topology)
        print(network)
            
        return time + self._model.time_step_size
    
    
if __name__ == "__main__":
    mosaik_api.start_simulation(TopologyMaker(), "USB connections")
