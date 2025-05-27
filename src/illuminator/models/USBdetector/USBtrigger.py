import serial.tools
import serial.tools.list_ports
from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
from ...cli.main import simulation
import asyncio

class USBtrigger(ModelConstructor):

    inputs = {"USBchange": False}
    
    def __init__(self, *args, **kwargs):
        result = super().__init__(*args, **kwargs)
        return result
        
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:
        input_data = self.unpack_inputs(inputs)
        print(input_data)
        if input_data["USBchange"] == 1:
            #raise RuntimeWarning
            loop = asyncio.get_event_loop()
            print(loop.is_running())
            loop.create_task(simulation.world._async_world.shutdown())

        return time + 1 
    
    
if __name__ == "__main__":
    mosaik_api.start_simulation(USBtrigger(), "USB trigger")