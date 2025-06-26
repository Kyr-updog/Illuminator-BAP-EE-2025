from illuminator.builder import ModelConstructor

class businessController(ModelConstructor):
    inputs={
        "pv_genState":0,
        "wind_genState":0,
        "load_demandState":0,
        "battery_percentage":0
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
        battery = input_data["battery_percentage"]

        bat_flow = pv_gen+wind_gen-load_dem
        grid_flow = 0
        if battery >= 100 and bat_flow > 0: #in case the battery is full, export power
            grid_flow = bat_flow
            bat_flow = 0
        elif battery <= 0 and bat_flow < 0: #in case the battery is empty, import power
            grid_flow = bat_flow
            bat_flow = 0

        self.set_outputs({"battery_flow":bat_flow, "grid_flow":grid_flow})

        return time + self._model.time_step_size