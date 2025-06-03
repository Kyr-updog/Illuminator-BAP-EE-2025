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
                
        led_connections = []
        for device in input['config']:
            for led_strip in device:
                if led_strip[3] == 'sender':
                    led_connections.append([led_strip[1], led_strip[2], led_strip[4]])
        
        connected_pairs = determine_connected_pairs(network)
        write_topology(connected_pairs, 'connections', filename, 'temp_no_con')
        led_map = write_LED_portmaps(led_connections)
        filename = self._model.parameters.get('filename')
        read_and_copy_yaml_data_plus_add_data_to_new_file('temp_no_con', 'simulation', led_map)
        print(network)
            
        return time + self._model.time_step_size
    
    
if __name__ == "__main__":
    mosaik_api.start_simulation(TopologyMaker(), "USB connections")
