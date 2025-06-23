from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
#from .Dynamic_yaml_scenario_module import *
import yaml

class TopologyMaker(ModelConstructor):

    parameters = {'filename': 'default.yaml'}
    inputs = {'config':{}}
    
    def __init__(self, *args, **kwargs):
        result = super().__init__(*args, **kwargs)
        print("hi there")
        return result
        
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:
        input = self.unpack_inputs(inputs)
        filename = self.parameters.get("filename")
        network = []
        
        #station aan ip koppelen
       
        stationlist = self.get_stations(filename)
            
        for device in input['config']:#make the input one giant list for the mapping function
            for led_strip in device:
                station = ""
                for ip_name in stationlist:
                    if ip_name[0] in led_strip:
                        station = ip_name[1]
                network.append([led_strip[0], station, led_strip[3]])
                
        led_connections = []
        ip_port = []
        for device in input['config']:
            for led_strip in device:
                if led_strip[3] == 'sender':
                    station = ""
                    for ip_name in stationlist:
                        if ip_name[0] in led_strip:
                            station = ip_name[1]
                    led_connections.append([led_strip[1], led_strip[2], led_strip[4], station])
                    ip_port.append([led_strip[1], led_strip[2]])

        
        self.create_shell_file(filename, ip_port)
        connected_pairs = determine_connected_pairs(network)
        topology = write_topology(connected_pairs, 'connections', filename, 'simulation.yaml')
        LED_portmap, LED_Station_map = write_LED_portmaps(led_connections)
        filename = self._model.parameters.get('filename')
        write_scenario_LEDs_and_connections('simulation.yaml',LED_portmap, LED_Station_map, topology)

            
        return time + self._model.time_step_size
    
    def get_stations(self, filename):
        with open(filename, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
            models = data["models"]
            ip_name = []
            for model in models:
                if model["type"] == "Station":
                    name = model["name"]
                    ip = model["connect"]["ip"]
                    ip_name.append([ip, name])
        return ip_name
            
    def create_shell_file(self, filename, led_connections):
        yaml_file = open(filename, 'r')
        shell_file = open("simulation.sh", 'w')
        yaml_data = yaml.safe_load(yaml_file)
        yaml_file.close()
        models = yaml_data["models"]
        for model in models:
            try:
                name = model["name"]
                modelType = model["type"]
                ip = model["connect"]["ip"]
                port = model["connect"]["port"]   
            except KeyError:
                continue     
            shell_file.write(f"lxterminal -e ssh Raspinator@{ip} './Illuminator/configuration/runshfile/run{modelType}.sh {ip} {port} /home/Raspinator/Illuminator/src/illuminator/models/'&\n")

        for connection in led_connections:
            shell_file.write(f"lxterminal -e ssh Raspinator@{connection[0]} './Illuminator/configuration/runshfile/runLED_connection.sh {connection[0]} {connection[1]} /home/Raspinator/Illuminator/src/illuminator/models/'&\n")



        
    
if __name__ == "__main__":
    #mosaik_api.start_simulation(TopologyMaker(), "USB connections")
    maker = TopologyMaker()
    maker.create_shell_file("examples/BAP-2025-Simulation/Demonstration.yaml", [['127.0.0.1', 5100], ['192.168.0.1', 5101], ['192.168.0.6', 5102]])

