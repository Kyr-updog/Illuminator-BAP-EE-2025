import serial.tools.list_ports
from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
import serial
from socket import gethostbyname, gethostname
from illuminator.models.LED.LED_strip_controller import sendPixelData

class IDrequester(ModelConstructor):

    states = {"stripList": False}
    
    def __init__(self, *args, **kwargs):
        result = super().__init__(*args, **kwargs)
        return result
        
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:
        connectionList = serial.tools.list_ports.comports()
        self.connections = []
        ip = gethostbyname(gethostname())
        for connection in connectionList:
            #serialCon = serial.Serial(connection.name)
            #id, sender = sendPixelData(serialCon, 0, 0, 0, 0, 0)
            #serialCon.close()
            #self.connections[str(id)] = [serialCon, sender] #store as id:[serial port, sender/dummy]
            id = 1
            sender = 'sender'
            self.connections.append([id, ip, sender, connection.name])
            self.connections.append([id, ip, sender, connection.name])
            
        output = {'stripList': self.connections}
        self.set_states(output)
           
        return time + self._model.time_step_size
    
    
if __name__ == "__main__":
    mosaik_api.start_simulation(IDrequester(), "USB connections")
