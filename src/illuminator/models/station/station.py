from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api


class station(ModelConstructor):
    
    inputs = {
        "LED-configuration": []
    }
    outputs = {
        "ID": []
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def step(self, time: int, inputs: dict = None, max_advance: int = 1):
        """
        1. receive the led-configuration
        2. check if configuration is the same
        3. if not, try to set the leds that are available
        4. update the ID table if nescesarry
        5. send the IDs to the pandalyser
        5.1. send the load and modelconfiguration to the pandalyser        
        """
        
        return time + self._model.time_step_size