from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
from .Dynamic_yaml_scenario_module import *
import yaml

class TopologyMaker(ModelConstructor):

    parameters = {'filename': 'default.yaml'}
    inputs = {'config':{}}
    
    def __init__(self, *args, **kwargs):
        result = super().__init__(*args, **kwargs)
        print("hi there")
        return result
        
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:
        print("BOE!!")
        input = self.unpack_inputs(inputs)
        filename = self.parameters.get("filename")
        network = []
        
        #station aan ip koppelen
        with open(filename, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
            
        
        for device in input['config']:#make the input one giant list for the mapping function
            for led_strip in device:
                network.append([led_strip[0], led_strip[1], led_strip[3]])
                
        led_connections = []
        for device in input['config']:
            for led_strip in device:
                if led_strip[3] == 'Sender':
                    led_connections.append([led_strip[1], led_strip[2], led_strip[4]])
        
        print(network)
        print("network")
        print(led_connections)
        connected_pairs = determine_connected_pairs(network)
        topology = write_topology(connected_pairs, 'connections', filename, 'temp_no_con.yaml')
        led_map = write_LED_portmaps(led_connections)
        filename = self._model.parameters.get('filename')
        write_scenario_LEDs_and_connections('temp_no_con.yaml', 'simulation.yaml', led_map, topology)
        print(network)
            
        return time + self._model.time_step_size
    
    
if __name__ == "__main__":
    mosaik_api.start_simulation(TopologyMaker(), "USB connections")
