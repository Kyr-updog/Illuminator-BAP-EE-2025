import serial.tools
import serial.tools.list_ports
from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
import serial
import time as t

class USBdetector(ModelConstructor):

    parameters = {"start": True}
    outputs = {"USBchange": False}
    
    def __init__(self, *args, **kwargs):
        result = super().__init__(*args, **kwargs)
        self.connections = serial.tools.list_ports.comports()
        print("starting")
        return result
        
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:
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
         
        t.sleep(1)
        print(self.outputs)
           
        return time + 1
    
    
if __name__ == "__main__":
    mosaik_api.start_simulation(USBdetector(), "USB connections")