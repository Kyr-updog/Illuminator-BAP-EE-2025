from illuminator.builder import ModelConstructor

class businessController(ModelConstructor):
    inputs={
        "pv_genState":0,
        "wind_genState":0,
        "load_demandState":0,
        "bat_pin":0,
        "bat_pout":0
    }
    outputs={
        "battery_flow":0,
        "grid_flow":0
    }

    def init(self, sid, time_resolution=1, **sim_params):
        return super().init(sid, time_resolution, **sim_params)
    
    def step(self, time, inputs = None, max_advance = None):

        input_data = self.unpack_inputs(inputs)

        pv_gen = input_data["pv_genState"]
        wind_gen = input_data["wind_genState"]
        load_dem = input_data["load_demandState"]
        bat_pin = input_data["bat_pin"]
        bat_pout = input_data["bat_pout"]

        print(bat_pin, bat_pout)

        grid_flow = bat_pin-bat_pout



        self.set_outputs({"grid_flow":grid_flow})

        return time + self._model.time_step_size